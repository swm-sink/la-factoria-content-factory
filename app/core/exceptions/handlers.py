"""
Global exception handlers for FastAPI application.
Provides consistent error responses and proper logging.
"""

import logging
import traceback
from typing import Any, Dict

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.core.exceptions.custom_exceptions import AppExceptionBase

logger = logging.getLogger(__name__)


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
        }
    )
    
    # Return user-friendly error response
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.user_message,
                "code": exc.error_code.value,
                "details": exc.details,
                "timestamp": request.state.timestamp if hasattr(request.state, 'timestamp') else None,
                "request_id": request.state.request_id if hasattr(request.state, 'request_id') else None,
            }
        }
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
        }
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
                "timestamp": request.state.timestamp if hasattr(request.state, 'timestamp') else None,
                "request_id": request.state.request_id if hasattr(request.state, 'request_id') else None,
            }
        }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )


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
        }
    )
    
    # Return generic error to avoid exposing internal details
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An unexpected error occurred. Please try again later.",
                "code": "INTERNAL_SERVER_ERROR",
                "details": {
                    "support_message": "If this error persists, please contact support with the request ID."
                },
                "timestamp": request.state.timestamp if hasattr(request.state, 'timestamp') else None,
                "request_id": request.state.request_id if hasattr(request.state, 'request_id') else None,
            }
        }
    )


def get_error_response_dict(
    message: str, 
    code: str, 
    details: Dict[str, Any] = None,
    request_id: str = None,
    timestamp: str = None
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