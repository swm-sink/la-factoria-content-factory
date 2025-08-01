"""
Health Monitoring Middleware

Monitors dependency health and updates health check status based on
request patterns and response codes.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.cache import get_cache_backend
from app.core.metrics import metrics

logger = logging.getLogger(__name__)


class HealthMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor health of dependencies based on request outcomes.
    """

    def __init__(self, app):
        super().__init__(app)
        self.cache = get_cache_backend()

        # Dependency patterns to monitor
        self.dependency_patterns = {
            "redis": {
                "patterns": ["/api/", "/health/"],  # Most endpoints use cache
                "error_threshold": 5,
                "window_seconds": 60,
            },
            "firestore": {
                "patterns": ["/api/jobs", "/api/content", "/api/feedback"],
                "error_threshold": 5,
                "window_seconds": 60,
            },
            "vertex_ai": {
                "patterns": ["/api/content/generate"],
                "error_threshold": 3,
                "window_seconds": 300,  # More lenient for external API
            },
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Monitor request outcomes to infer dependency health.
        """
        # Skip health check endpoints to avoid circular dependencies
        if request.url.path.startswith("/health"):
            return await call_next(request)

        start_time = time.time()
        response = None
        exception_occurred = False

        try:
            response = await call_next(request)

            # Update dependency health based on response
            await self._update_dependency_health(
                request=request,
                status_code=response.status_code,
                latency_ms=(time.time() - start_time) * 1000,
                exception_occurred=False,
            )

        except Exception as e:
            exception_occurred = True
            logger.error(f"Request failed with exception: {e}")

            # Update dependency health for failed request
            await self._update_dependency_health(
                request=request, status_code=500, latency_ms=(time.time() - start_time) * 1000, exception_occurred=True
            )

            raise

        return response

    async def _update_dependency_health(
        self, request: Request, status_code: int, latency_ms: float, exception_occurred: bool
    ):
        """Update health metrics for dependencies based on request outcome."""
        path = request.url.path

        # Check each dependency pattern
        for dep_name, config in self.dependency_patterns.items():
            if any(path.startswith(pattern) for pattern in config["patterns"]):
                await self._update_dependency_metrics(
                    dependency=dep_name,
                    success=status_code < 500 and not exception_occurred,
                    latency_ms=latency_ms,
                    config=config,
                )

    async def _update_dependency_metrics(self, dependency: str, success: bool, latency_ms: float, config: dict):
        """Update metrics for a specific dependency."""
        try:
            # Update success rate
            success_key = f"dep_health_{dependency}_success_count"
            total_key = f"dep_health_{dependency}_total_count"
            latency_key = f"dep_health_{dependency}_latency_ms"
            error_key = f"dep_health_{dependency}_recent_errors"

            # Get current counts
            success_count = await self.cache.get(success_key) or 0
            total_count = await self.cache.get(total_key) or 0
            recent_errors = await self.cache.get(error_key) or []

            # Update counts
            total_count += 1
            if success:
                success_count += 1
            else:
                # Track recent errors with timestamp
                recent_errors.append({"timestamp": datetime.now(timezone.utc).isoformat(), "latency_ms": latency_ms})

                # Keep only recent errors within window
                cutoff_time = time.time() - config["window_seconds"]
                recent_errors = [
                    e for e in recent_errors if datetime.fromisoformat(e["timestamp"]).timestamp() > cutoff_time
                ]

            # Calculate success rate
            success_rate = (success_count / total_count * 100) if total_count > 0 else 100.0

            # Store metrics
            await self.cache.set(success_key, success_count, expire=3600)
            await self.cache.set(total_key, total_count, expire=3600)
            await self.cache.set(latency_key, latency_ms, expire=300)
            await self.cache.set(error_key, recent_errors, expire=300)

            # Update Prometheus metrics
            metrics.gauge(f"dependency_{dependency}_success_rate", success_rate)
            metrics.gauge(f"dependency_{dependency}_latency_ms", latency_ms)

            # Check if dependency should be marked as unhealthy
            if len(recent_errors) >= config["error_threshold"]:
                await self._mark_dependency_unhealthy(dependency, recent_errors)
            else:
                await self._mark_dependency_healthy(dependency)

        except Exception as e:
            logger.error(f"Error updating dependency metrics for {dependency}: {e}")

    async def _mark_dependency_unhealthy(self, dependency: str, errors: list):
        """Mark a dependency as unhealthy."""
        await self.cache.set(
            f"dep_health_{dependency}_status",
            {
                "status": "unhealthy",
                "since": datetime.now(timezone.utc).isoformat(),
                "error_count": len(errors),
                "recent_errors": errors[-5:],  # Keep last 5 errors
            },
            expire=300,
        )

        # Log alert
        logger.error(f"Dependency {dependency} marked as unhealthy: {len(errors)} errors in window")

        # Update metric
        metrics.gauge(f"dependency_{dependency}_healthy", 0)

    async def _mark_dependency_healthy(self, dependency: str):
        """Mark a dependency as healthy."""
        current_status = await self.cache.get(f"dep_health_{dependency}_status")

        # Only update if status changed
        if current_status and current_status.get("status") != "healthy":
            logger.info(f"Dependency {dependency} recovered and marked as healthy")

        await self.cache.set(
            f"dep_health_{dependency}_status",
            {"status": "healthy", "since": datetime.now(timezone.utc).isoformat()},
            expire=300,
        )

        # Update metric
        metrics.gauge(f"dependency_{dependency}_healthy", 1)
