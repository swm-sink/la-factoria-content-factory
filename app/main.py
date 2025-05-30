"""
Main application entry point for the AI Content Factory.
"""

import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
import logging
from pythonjsonlogger import jsonlogger # Added for structured logging
import os
from prometheus_client import start_http_server
from app.core.config.settings import get_settings
from app.api.routes import api_router  # Main router for versioned API

# from app.api.routes.content import router as content_router # Legacy, handled by api_router or deprecated
# from app.api.routes.jobs import router as jobs_router # Handled by api_router
# from app.api.routes.health import router as health_router # Handled by api_router
# from app.api.routes.auth import router as auth_router # Handled by api_router
from app.api.routes.worker import (
    router as worker_router,
)  # Internal worker endpoints, not versioned under /api/v1

# Get settings
settings = get_settings()

# Configure logging
# logging.basicConfig(level=settings.log_level.upper(), format=settings.log_format)
logger = logging.getLogger() # Get root logger, or a specific one like logging.getLogger(__name__)
log_handler = logging.StreamHandler()

# Attempt to get correlation_id format key from settings.log_format to include in JsonFormatter
# This is a basic attempt; a more robust solution might parse the format string
# or have a separate list of fields for the JsonFormatter.
reserved_attrs = [
    attr for attr in ['asctime', 'levelname', 'name', 'message'] 
    if f'%({attr})' in settings.log_format
]
# Add correlation_id if it's in the format string
custom_attrs_in_format = []
if "%(correlation_id)s" in settings.log_format:
    custom_attrs_in_format.append("correlation_id")

formatter_string_parts = []
if "%(asctime)s" in settings.log_format:
    formatter_string_parts.append("%(asctime)s")
if "%(levelname)s" in settings.log_format:
    formatter_string_parts.append("%(levelname)s")
if "%(name)s" in settings.log_format:
    formatter_string_parts.append("%(name)s")
if "%(correlation_id)s" in settings.log_format: # Check again for specific placement
    formatter_string_parts.append("[%(correlation_id)s]")
formatter_string_parts.append("%(message)s")

# Construct a simple format string for JsonFormatter based on what was in settings.log_format
# This ensures JsonFormatter outputs fields that were intended by settings.log_format
# JsonFormatter will output these as top-level keys in the JSON log.
# The `format` kwarg to JsonFormatter defines which LogRecord attributes are pulled into the JSON.
json_formatter_format_str = " ".join(f'%({attr})' for attr in reserved_attrs + custom_attrs_in_format + ['message'])
# More simply, tell JsonFormatter which fields to expect using its own syntax or rely on default plus rename

formatter = jsonlogger.JsonFormatter(
    fmt=settings.log_format, # Let JsonFormatter try to parse this, or use its own field list
    # Alternatively, define the fields explicitly for JsonFormatter:
    # format="%(asctime)s %(levelname)s %(name)s %(correlation_id)s %(message)s",
    # rename_fields={"asctime": "timestamp", "levelname": "level"} # Example rename
    reserved_attrs=reserved_attrs + custom_attrs_in_format # Ensure these are not dropped if not in default set
)

log_handler.setFormatter(formatter)
logger.handlers = [log_handler] # Replace existing handlers
logger.setLevel(settings.log_level.upper())

# Re-get the specific logger for app.main after root logger setup
main_logger = logging.getLogger(__name__)

# API Key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    """
    Dependency function to validate the API key.

    Args:
        api_key: The API key passed in the X-API-Key header.

    Raises:
        HTTPException: If the API key is invalid or missing.

    Returns:
        The validated API key.
    """
    if not api_key or api_key != settings.api_key:
        provided_key_display = f"'{api_key[:10]}...'" if api_key else "None"
        main_logger.warning(
            f"Invalid or missing API key attempt. Provided key: {provided_key_display}."
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
    return api_key


# FastAPI app
app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    description="AI Content Factory API to generate various educational materials.",
    # Add dependencies=[Depends(get_api_key)] here if ALL routes need API key auth by default
    # Otherwise, apply it selectively to routers or individual endpoints.
    # For now, assuming api_router or specific routes within it will handle auth.
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True, # Allow cookies if your auth uses them
    allow_methods=["*"],    # Allows all methods
    allow_headers=["*"],    # Allows all headers
)

# Include the main API router with the /api/v1 prefix
# This router (from app/api/routes.py) should aggregate all user-facing, versioned endpoints.
app.include_router(api_router, prefix=settings.api_v1_prefix)

# Include internal worker router (NOT exposed via API Gateway and NOT under /api/v1)
# These routes are typically for internal services like Cloud Tasks.
app.include_router(worker_router, prefix="/internal", tags=["Internal Worker"])


# Start Prometheus metrics server if not in testing mode
if os.getenv("PROMETHEUS_DISABLE") != "true":
    try:
        start_http_server(settings.prometheus_port)  # Use port from settings
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


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Generic exception handler to catch unhandled errors and return a 500 response.
    """
    main_logger.error(
        f"Unhandled error during request to {request.url.path}: {exc}", exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )


@app.on_event("startup")
async def startup_event() -> None:
    """
    Actions to perform on application startup.
    """
    main_logger.info(f"Application startup: {settings.project_name} v{app.version}")
    main_logger.info(f"Log level set to: {settings.log_level}")
    # Example: Initialize database connections, load ML models, etc.
    pass


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Actions to perform on application shutdown.
    """
    main_logger.info(f"Application shutdown: {settings.project_name}")
    # Example: Close database connections, cleanup resources, etc.
    pass


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.app_port, reload=True)
