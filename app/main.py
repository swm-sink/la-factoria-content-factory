"""
Main application entry point for the AI Content Factory.
"""

import logging
import os

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import start_http_server
from pythonjsonlogger import jsonlogger

from app.api.routes import (
    api_router as v1_router,  # Ensures importing from the __init__.py
)
from app.api.routes.worker import router as worker_router
from app.core.config.settings import get_settings

# Get settings
settings = get_settings()

# Configure structured logging
logger = logging.getLogger()
log_handler = logging.StreamHandler()

# Import the filter
from app.core.logging_filters import CorrelationIdFilter

# Add the filter to the handler
correlation_id_filter = CorrelationIdFilter()
log_handler.addFilter(correlation_id_filter)

# Update formatter to include correlation_id
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s [%(correlation_id)s] %(message)s"
formatter = jsonlogger.JsonFormatter(
    LOG_FORMAT,
    rename_fields={
        "asctime": "timestamp",
        "levelname": "level",
        "correlation_id": "correlation_id",
    },
    # Ensure correlation_id is processed even if None
    defaults={"correlation_id": None},
)

log_handler.setFormatter(formatter)
logger.handlers = [log_handler]
logger.setLevel(settings.log_level.upper())

main_logger = logging.getLogger(__name__)


# FastAPI app
app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    description="AI Content Factory API to generate various educational materials.",
    # Authentication is handled at the router/endpoint level
)

# Import and add enhanced middleware
from app.core.middleware import CorrelationIdMiddleware
from app.core.middleware.request_tracking import RequestTrackingMiddleware, RequestLoggingMiddleware
from app.middleware.usage_tracking import UsageTrackingMiddleware
from app.middleware.cost_control import CostControlMiddleware
from app.middleware.rate_limiting import RateLimitingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

# Add enhanced request tracking and logging middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestTrackingMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(UsageTrackingMiddleware)
app.add_middleware(CostControlMiddleware)
app.add_middleware(RateLimitingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Add CORS middleware (should be one of the last, or after CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main API router with the /api/v1 prefix (all user-facing endpoints)
app.include_router(
    v1_router, prefix="/api/v1"
)  # Only register the canonical api_router from app.api.routes.__init__.py

# Internal worker router - NOT exposed via API Gateway.
# Relies on network-level access controls (e.g., VPC SC, Cloud Run ingress settings)
# and/or Cloud Tasks OIDC token authentication if invoked by Cloud Tasks.
# These routes are intended for internal service-to-service communication only.
app.include_router(worker_router, prefix="/internal", tags=["Internal Worker"])


# Start Prometheus metrics server if not in testing mode
if os.getenv("PROMETHEUS_DISABLE") != "true":
    try:
        start_http_server(settings.prometheus_port)
        main_logger.info(
            f"Prometheus metrics server started on port {settings.prometheus_port}"
        )
    except OSError as e:
        main_logger.warning(
            f"Could not start Prometheus metrics server on port {settings.prometheus_port}: {e}"
        )


@app.get("/healthz", tags=["Root Health"])
async def root_health_check():
    """Provides a simple health check for liveness/readiness probes.
    This endpoint is NOT protected by API Key and is suitable for GCP health checks.
    """
    return {"status": "healthy"}


# Helper to generate trace_id (can be more sophisticated, e.g., using a request ID middleware)
import uuid

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationErrorCore

# Import custom exceptions and enhanced handlers
from app.core.exceptions import AppExceptionBase, JobErrorCode
from app.core.exceptions.handlers import (
    app_exception_handler as enhanced_app_exception_handler,
    http_exception_handler as enhanced_http_exception_handler,
    general_exception_handler as enhanced_general_exception_handler
)
from app.core.logging.structured_logger import get_logger, set_correlation_context

# Initialize structured logger
structured_logger = get_logger(__name__)


def _get_trace_id(request: Request) -> str:
    # Attempt to get from headers (if set by a load balancer or previous middleware)
    trace_id = request.headers.get("X-Cloud-Trace-Context")
    if trace_id:
        # Format might be "TRACE_ID/SPAN_ID;o=TRACE_TRUE"
        return trace_id.split("/")[0]
    trace_id = request.headers.get("X-Request-ID")
    if trace_id:
        return trace_id
    # Generate a new one if not found
    return str(uuid.uuid4())


@app.exception_handler(AppExceptionBase)
async def app_exception_handler(
    request: Request, exc: AppExceptionBase
) -> JSONResponse:
    """Handles custom application exceptions with enhanced logging."""
    return await enhanced_app_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handles FastAPI request validation errors (e.g., for path/query/body params)."""
    trace_id = _get_trace_id(request)
    error_details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_details.append({"field": field, "message": message})

    main_logger.warning(
        f"RequestValidationError: Invalid request to {request.url.path} "
        f"(Trace: {trace_id}, Details: {error_details})",
        extra={
            "error_code": "REQUEST_VALIDATION_ERROR",
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "details": error_details,
            "trace_id": trace_id,
            "path": request.url.path,
        },
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Request validation failed.",
            "code": "REQUEST_VALIDATION_ERROR",
            "details": error_details,
            "trace_id": trace_id,
        },
    )


@app.exception_handler(
    PydanticValidationErrorCore
)  # Handles Pydantic validation errors not caught by FastAPI's RequestValidationError
async def pydantic_core_validation_exception_handler(
    request: Request, exc: PydanticValidationErrorCore
) -> JSONResponse:
    trace_id = _get_trace_id(request)
    error_details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_details.append({"field": field, "message": message})

    main_logger.warning(
        f"PydanticValidationErrorCore: Data validation error for {request.url.path} "
        f"(Trace: {trace_id}, Details: {error_details})",
        extra={
            "error_code": "DATA_VALIDATION_ERROR",
            "status_code": status.HTTP_400_BAD_REQUEST,  # Or 422 if preferred for all validation
            "details": error_details,
            "trace_id": trace_id,
            "path": request.url.path,
        },
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Data validation failed.",
            "code": "DATA_VALIDATION_ERROR",
            "details": error_details,
            "trace_id": trace_id,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Generic exception handler with enhanced error handling and logging.
    This should be the last handler.
    """
    return await enhanced_general_exception_handler(request, exc)


@app.on_event("startup")
async def startup_event() -> None:
    """
    Actions to perform on application startup with enhanced logging.
    """
    structured_logger.log_event(
        structured_logger.LogLevel.INFO,
        structured_logger.EventType.PERFORMANCE,
        f"Application startup: {settings.project_name} v{app.version}",
        app_name=settings.project_name,
        app_version=app.version,
        log_level=settings.log_level,
        prometheus_port=settings.prometheus_port,
        environment=os.getenv("ENVIRONMENT", "development")
    )


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Actions to perform on application shutdown with enhanced logging.
    """
    structured_logger.log_event(
        structured_logger.LogLevel.INFO,
        structured_logger.EventType.PERFORMANCE,
        f"Application shutdown: {settings.project_name}",
        app_name=settings.project_name,
        app_version=app.version
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.app_port, reload=True)
