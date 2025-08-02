"""
Global exception handlers for FastAPI application.
Provides consistent error responses and proper logging.
"""

import asyncio
import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.core.alerting.models import Alert, AlertSeverity
from app.core.exceptions.custom_exceptions import AppExceptionBase

logger = logging.getLogger(__name__)

# Global reference to alert manager (will be set during app startup)
_alert_manager: Optional[Any] = None


def set_alert_manager(alert_manager: Any):
    """Set the global alert manager instance."""
    global _alert_manager
    _alert_manager = alert_manager


async def _fire_error_alert(
    request: Request, error_type: str, severity: AlertSeverity, message: str, context: Dict[str, Any]
):
    """Fire an error alert if alert manager is available."""
    if _alert_manager is None:
        return

    try:
        alert = Alert(
            name=f"ExceptionHandler_{error_type}",
            severity=severity,
            service="api",
            source="exception_handler",
            message=message,
            context={
                **context,
                "request_id": getattr(request.state, "request_id", "unknown"),
                "timestamp": datetime.utcnow().isoformat(),
                "endpoint": f"{request.method} {request.url.path}",
                "user_agent": request.headers.get("user-agent", "unknown"),
                "ip": request.client.host if request.client else "unknown",
            },
            runbook_url="https://github.com/lafactoria/runbooks/blob/main/incident-response/api-down.md",
            annotations={
                "impact": "High - Request failed",
                "urgency": (
                    "High - Investigate immediately" if severity == AlertSeverity.CRITICAL else "Medium - Monitor"
                ),
                "category": "application_error",
                "auto_generated": "true",
                "exception_handler": error_type,
            },
        )

        # Fire alert asynchronously
        asyncio.create_task(_alert_manager.fire_alert(alert))

    except Exception as exc:
        logger.error(f"Failed to fire error alert: {exc}", exc_info=True)


async def app_exception_handler(request: Request, exc: AppExceptionBase) -> JSONResponse:
    """
    Handle custom application exceptions with structured error responses.

    Args:
        request: The FastAPI request object
        exc: The custom application exception

    Returns:
        JSONResponse with structured error details
    """
    # Log the internal message for debugging
    logger.error(
        "Application exception occurred",
        extra={
            "error_code": exc.error_code.value,
            "status_code": exc.status_code,
            "internal_message": exc.internal_log_message,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        },
    )

    # Fire alert for high-severity application exceptions
    if exc.status_code >= 500:
        await _fire_error_alert(
            request=request,
            error_type="AppException",
            severity=AlertSeverity.HIGH,
            message=f"Application exception: {exc.error_code.value} - {exc.internal_log_message}",
            context={
                "error_code": exc.error_code.value,
                "status_code": exc.status_code,
                "internal_message": exc.internal_log_message,
                "details": exc.details,
                "exception_type": type(exc).__name__,
            },
        )

    # Return user-friendly error response
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.user_message,
                "code": exc.error_code.value,
                "details": exc.details,
                "timestamp": request.state.timestamp if hasattr(request.state, "timestamp") else None,
                "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
            }
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions with enhanced error details.

    Args:
        request: The FastAPI request object
        exc: The HTTP exception

    Returns:
        JSONResponse with enhanced error details
    """
    logger.warning(
        "HTTP exception occurred",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method,
        },
    )

    # Fire alert for server error HTTP exceptions
    if exc.status_code >= 500:
        await _fire_error_alert(
            request=request,
            error_type="HTTPException",
            severity=AlertSeverity.HIGH if exc.status_code in [500, 502, 503] else AlertSeverity.MEDIUM,
            message=f"HTTP {exc.status_code} error: {exc.detail}",
            context={"status_code": exc.status_code, "detail": str(exc.detail), "exception_type": "HTTPException"},
        )

    # Enhanced error response format
    error_detail = exc.detail
    if isinstance(error_detail, dict):
        # If detail is already structured, use it as-is
        content = {"error": error_detail}
    else:
        # Convert simple string details to structured format
        content = {
            "error": {
                "message": str(error_detail),
                "code": f"HTTP_{exc.status_code}",
                "details": {},
                "timestamp": request.state.timestamp if hasattr(request.state, "timestamp") else None,
                "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
            }
        }

    return JSONResponse(status_code=exc.status_code, content=content)


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions with proper logging and user-safe responses.

    Args:
        request: The FastAPI request object
        exc: The unexpected exception

    Returns:
        JSONResponse with generic error message (no sensitive details exposed)
    """
    # Log the full exception details for debugging
    logger.error(
        "Unexpected exception occurred",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
            "path": request.url.path,
            "method": request.method,
        },
    )

    # Fire critical alert for unhandled exceptions
    await _fire_error_alert(
        request=request,
        error_type="UnhandledException",
        severity=AlertSeverity.CRITICAL,
        message=f"Unhandled {type(exc).__name__}: {str(exc)}",
        context={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
            "is_database_error": _is_database_error(exc),
            "is_external_service_error": _is_external_service_error(exc),
            "is_timeout_error": _is_timeout_error(exc),
        },
    )

    # Return generic error to avoid exposing internal details
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An unexpected error occurred. Please try again later.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": {"support_message": "If this error persists, please contact support with the request ID."},
                "timestamp": request.state.timestamp if hasattr(request.state, "timestamp") else None,
                "request_id": request.state.request_id if hasattr(request.state, "request_id") else None,
            }
        },
    )


def get_error_response_dict(
    message: str, code: str, details: Dict[str, Any] = None, request_id: str = None, timestamp: str = None
) -> Dict[str, Any]:
    """
    Utility function to create consistent error response dictionaries.

    Args:
        message: User-friendly error message
        code: Error code for programmatic handling
        details: Additional error details
        request_id: Request identifier for tracing
        timestamp: Error timestamp

    Returns:
        Structured error response dictionary
    """
    return {
        "error": {
            "message": message,
            "code": code,
            "details": details or {},
            "request_id": request_id,
            "timestamp": timestamp,
        }
    }


def _is_database_error(exc: Exception) -> bool:
    """Check if exception is related to database connectivity."""
    exc_str = str(exc).lower()
    exc_type = type(exc).__name__.lower()

    database_keywords = [
        "connection refused",
        "connection timeout",
        "database is locked",
        "connection error",
        "database error",
        "firestore",
        "redis",
        "connection pool",
        "database unavailable",
    ]

    return any(keyword in exc_str or keyword in exc_type for keyword in database_keywords)


def _is_external_service_error(exc: Exception) -> bool:
    """Check if exception is related to external service failures."""
    exc_str = str(exc).lower()
    exc_type = type(exc).__name__.lower()

    external_keywords = [
        "httpx",
        "requests",
        "aiohttp",
        "connection error",
        "timeout",
        "network",
        "api error",
        "service unavailable",
    ]

    return any(keyword in exc_str or keyword in exc_type for keyword in external_keywords)


def _is_timeout_error(exc: Exception) -> bool:
    """Check if exception is related to timeouts."""
    exc_str = str(exc).lower()
    exc_type = type(exc).__name__.lower()

    timeout_keywords = ["timeout", "timed out", "deadline exceeded"]

    return any(keyword in exc_str or keyword in exc_type for keyword in timeout_keywords)
