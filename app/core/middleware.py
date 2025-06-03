import logging
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Try to get correlation_id from headers first
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            # Fallback to other common trace headers
            correlation_id = request.headers.get("X-Request-ID")
        if not correlation_id:
            # GCP Trace context
            gcp_trace_context = request.headers.get("X-Cloud-Trace-Context")
            if gcp_trace_context:
                correlation_id = gcp_trace_context.split("/")[0]

        if not correlation_id:
            # Generate a new one if not found
            correlation_id = str(uuid.uuid4())
            logger.debug(
                f"No correlation ID in headers. Generated new: {correlation_id}"
            )

        # Store it in request.state to be accessible in route handlers and other middleware
        request.state.correlation_id = correlation_id

        # Add correlation_id to the logger's extra context for this request
        # This requires a custom log filter or formatter adapter in the main logging setup
        # For now, we ensure it's available in request.state

        response = await call_next(request)

        # Add correlation_id to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response
