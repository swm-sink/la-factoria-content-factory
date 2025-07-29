"""
Request tracking middleware for enhanced error handling and monitoring.
Adds request IDs and timestamps to all requests.
"""

import time
import uuid
from datetime import datetime
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track requests with UUID and timestamps for better debugging and monitoring.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with tracking information.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
        
        Returns:
            Response with added tracking headers
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Add timestamp
        start_time = time.time()
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Store in request state for access in exception handlers
        request.state.request_id = request_id
        request.state.timestamp = timestamp
        request.state.start_time = start_time
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add tracking headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["X-Timestamp"] = timestamp
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request and response details for monitoring.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response details.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
        
        Returns:
            Response with logged details
        """
        import logging
        
        logger = logging.getLogger("app.requests")
        
        # Log request details
        logger.info(
            "Request started",
            extra={
                "request_id": getattr(request.state, 'request_id', 'unknown'),
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response details
        process_time = getattr(request.state, 'start_time', 0)
        if process_time:
            process_time = time.time() - process_time
        
        logger.info(
            "Request completed",
            extra={
                "request_id": getattr(request.state, 'request_id', 'unknown'),
                "status_code": response.status_code,
                "process_time": f"{process_time:.4f}s" if process_time else "unknown",
            }
        )
        
        return response