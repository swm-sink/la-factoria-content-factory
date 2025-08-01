"""
Metrics Collection Middleware

This middleware collects Prometheus metrics for all HTTP requests,
including request counts, latencies, and active request tracking.
"""

import logging
import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.metrics import metrics

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for collecting Prometheus metrics.
    """

    def __init__(self, app: ASGIApp):
        """Initialize the metrics middleware."""
        super().__init__(app)
        self.app = app

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and collect metrics.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response with metrics collected
        """
        # Skip metrics endpoint to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        # Extract route pattern for better metric labeling
        route = self._get_route_pattern(request)
        method = request.method

        # Track active requests
        metrics.gauge("active_requests", 1, tags={"method": method, "endpoint": route})

        # Start timing
        start_time = time.time()

        # Default values
        status_code = 500
        response = None
        exception_occurred = False

        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code

        except Exception as e:
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            exception_occurred = True

            # Track error
            metrics.increment("errors_total", tags={"error_type": type(e).__name__, "severity": "high"})
            raise

        finally:
            # Calculate duration
            duration = time.time() - start_time

            # Update metrics
            metrics.increment(
                "http_requests_total", tags={"method": method, "endpoint": route, "status": str(status_code)}
            )

            metrics.histogram("http_request_duration_seconds", duration, tags={"method": method, "endpoint": route})

            # Update active requests
            metrics.gauge("active_requests", -1, tags={"method": method, "endpoint": route})

            # Track content generation metrics
            if route.startswith("/api/content/generate"):
                await self._track_content_generation(status_code, duration)

            # Track audio generation metrics
            elif route.startswith("/api/audio/generate"):
                await self._track_audio_generation(status_code, duration)

            # Log slow requests
            if duration > 5.0:
                logger.warning(f"Slow request detected: {method} {route} took {duration:.2f}s")

        return response

    def _get_route_pattern(self, request: Request) -> str:
        """
        Extract the route pattern from the request.

        This helps group metrics by route pattern rather than specific URLs.
        For example, /api/content/123 becomes /api/content/{id}
        """
        path = request.url.path

        # Common patterns to normalize
        patterns = [
            (r"/api/content/[a-zA-Z0-9-]+", "/api/content/{id}"),
            (r"/api/jobs/[a-zA-Z0-9-]+", "/api/jobs/{id}"),
            (r"/api/users/[a-zA-Z0-9-]+", "/api/users/{id}"),
            (r"/api/feedback/[a-zA-Z0-9-]+", "/api/feedback/{id}"),
        ]

        import re

        for pattern, replacement in patterns:
            if re.match(pattern, path):
                return re.sub(pattern, replacement, path)

        return path

    async def _track_content_generation(self, status_code: int, duration: float):
        """Track content generation specific metrics."""
        status = "success" if status_code < 400 else "error"

        metrics.increment(
            "content_generation_total",
            tags={"content_type": "mixed", "status": status},  # Could be extracted from request
        )

        metrics.histogram("content_generation_duration_seconds", duration, tags={"content_type": "mixed"})

    async def _track_audio_generation(self, status_code: int, duration: float):
        """Track audio generation specific metrics."""
        status = "success" if status_code < 400 else "error"

        metrics.increment("audio_generation_total", tags={"status": status})

        metrics.histogram("audio_generation_duration_seconds", duration)


class DatabaseMetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track database connection pool metrics.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Track database pool metrics during request processing.
        """
        # This would typically integrate with your database connection pool
        # For now, we'll set some example values
        try:
            # Example: Track Redis pool
            from app.utils.redis_pool import get_redis_pool

            pool = get_redis_pool()
            if hasattr(pool, "connection_pool"):
                metrics.gauge(
                    "database_connections_active", pool.connection_pool.created_connections, tags={"database": "redis"}
                )
                metrics.gauge(
                    "database_connections_max", pool.connection_pool.max_connections, tags={"database": "redis"}
                )
        except Exception as e:
            logger.debug(f"Could not collect Redis metrics: {e}")

        try:
            # Example: Track Firestore pool
            from app.utils.firestore_pool import get_firestore_pool

            pool = get_firestore_pool()
            if hasattr(pool, "_pool"):
                metrics.gauge(
                    "database_connections_active", len(pool._pool._connections), tags={"database": "firestore"}
                )
                metrics.gauge("database_connections_max", pool._pool._max_size, tags={"database": "firestore"})
        except Exception as e:
            logger.debug(f"Could not collect Firestore metrics: {e}")

        return await call_next(request)


class CacheMetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track cache metrics.
    """

    def __init__(self, app: ASGIApp):
        """Initialize the cache metrics middleware."""
        super().__init__(app)
        self._cache_hits = 0
        self._cache_misses = 0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Track cache metrics during request processing.
        """
        # Get cache statistics from the request processing
        # This would typically be updated by your cache layer
        response = await call_next(request)

        # Example: Check if response was served from cache
        if hasattr(response, "headers") and response.headers.get("X-Cache-Status"):
            cache_status = response.headers.get("X-Cache-Status")

            if cache_status == "HIT":
                self._cache_hits += 1
                metrics.increment("cache_operations_total", tags={"operation": "get", "status": "hit"})
            elif cache_status == "MISS":
                self._cache_misses += 1
                metrics.increment("cache_operations_total", tags={"operation": "get", "status": "miss"})

            # Update hit ratio
            total = self._cache_hits + self._cache_misses
            if total > 0:
                hit_ratio = self._cache_hits / total
                metrics.gauge("cache_hit_ratio", hit_ratio)

        return response
