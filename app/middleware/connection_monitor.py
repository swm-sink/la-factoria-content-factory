"""
Connection monitoring middleware.

Monitors connection pool health and performance metrics.
"""

import asyncio
import logging
import time
from typing import Callable, Dict, Any

from fastapi import Request, Response
from prometheus_client import Gauge, Summary
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.redis_pool import check_redis_health, get_redis_pool
from app.utils.firestore_pool import check_firestore_health, get_firestore_pool


# Metrics
CONNECTION_POOL_HEALTH = Gauge(
    "connection_pool_health", 
    "Connection pool health status (1=healthy, 0=unhealthy)",
    ["pool_name"]
)
CONNECTION_POOL_UTILIZATION = Gauge(
    "connection_pool_utilization",
    "Connection pool utilization percentage",
    ["pool_name"]
)
CONNECTION_POOL_ACTIVE = Gauge(
    "connection_pool_active_connections",
    "Number of active connections",
    ["pool_name"]
)
CONNECTION_POOL_IDLE = Gauge(
    "connection_pool_idle_connections",
    "Number of idle connections",
    ["pool_name"]
)
CONNECTION_MONITOR_CHECK_TIME = Summary(
    "connection_monitor_check_duration_seconds",
    "Time spent checking connection health"
)


class ConnectionMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor connection pool health and metrics.
    """
    
    def __init__(self, app, check_interval: int = 30):
        """
        Initialize connection monitoring.
        
        Args:
            app: FastAPI application
            check_interval: Health check interval in seconds
        """
        super().__init__(app)
        self.check_interval = check_interval
        self.logger = logging.getLogger(__name__)
        self._monitoring_task = None
        self._last_check = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and update connection metrics if needed."""
        # Start monitoring if not already running
        if self._monitoring_task is None:
            self._monitoring_task = asyncio.create_task(self._monitor_connections())
        
        # Process the request
        response = await call_next(request)
        
        # Add connection pool headers to response for debugging
        if request.url.path == "/metrics" or request.url.path.startswith("/api/v1/admin"):
            try:
                headers = await self._get_connection_headers()
                for key, value in headers.items():
                    response.headers[key] = value
            except Exception as e:
                self.logger.error(f"Error adding connection headers: {e}")
        
        return response
    
    async def _monitor_connections(self) -> None:
        """Periodic monitoring of connection pools."""
        while True:
            try:
                await asyncio.sleep(self.check_interval)
                await self._check_all_pools()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Connection monitoring error: {e}")
    
    @CONNECTION_MONITOR_CHECK_TIME.time()
    async def _check_all_pools(self) -> None:
        """Check health of all connection pools."""
        self._last_check = time.time()
        
        # Check Redis pool
        try:
            redis_health = await check_redis_health()
            await self._update_pool_metrics("redis", redis_health)
        except Exception as e:
            self.logger.error(f"Error checking Redis health: {e}")
            CONNECTION_POOL_HEALTH.labels(pool_name="redis").set(0)
        
        # Check Firestore pool
        try:
            firestore_health = await check_firestore_health()
            await self._update_pool_metrics("firestore", firestore_health)
        except Exception as e:
            self.logger.error(f"Error checking Firestore health: {e}")
            CONNECTION_POOL_HEALTH.labels(pool_name="firestore").set(0)
    
    async def _update_pool_metrics(self, pool_name: str, health_data: Dict[str, Any]) -> None:
        """Update metrics for a connection pool."""
        # Update health status
        is_healthy = health_data.get("status") == "healthy"
        CONNECTION_POOL_HEALTH.labels(pool_name=pool_name).set(1 if is_healthy else 0)
        
        # Update pool statistics if available
        pool_stats = health_data.get("pool_stats", {})
        if pool_stats:
            # Connection counts
            connections = pool_stats.get("connections", {})
            CONNECTION_POOL_ACTIVE.labels(pool_name=pool_name).set(
                connections.get("active", 0)
            )
            CONNECTION_POOL_IDLE.labels(pool_name=pool_name).set(
                connections.get("idle", 0)
            )
            
            # Utilization
            size_info = pool_stats.get("size", {})
            current = size_info.get("current", 0)
            max_size = size_info.get("max", 1)
            utilization = (current / max_size * 100) if max_size > 0 else 0
            CONNECTION_POOL_UTILIZATION.labels(pool_name=pool_name).set(utilization)
    
    async def _get_connection_headers(self) -> Dict[str, str]:
        """Get connection pool status headers."""
        headers = {}
        
        try:
            # Get Redis pool stats
            redis_pool = await get_redis_pool()
            redis_stats = redis_pool.get_stats()
            headers["X-Redis-Pool-Active"] = str(redis_stats["connections"]["active"])
            headers["X-Redis-Pool-Idle"] = str(redis_stats["connections"]["idle"])
            headers["X-Redis-Pool-Size"] = str(redis_stats["size"]["current"])
        except Exception:
            pass
        
        try:
            # Get Firestore pool stats
            firestore_pool = await get_firestore_pool()
            firestore_stats = firestore_pool.get_stats()
            headers["X-Firestore-Pool-Active"] = str(firestore_stats["connections"]["active"])
            headers["X-Firestore-Pool-Idle"] = str(firestore_stats["connections"]["idle"])
            headers["X-Firestore-Pool-Size"] = str(firestore_stats["size"]["current"])
        except Exception:
            pass
        
        headers["X-Connection-Monitor-Last-Check"] = str(int(self._last_check))
        
        return headers


async def get_connection_pool_status() -> Dict[str, Any]:
    """
    Get current status of all connection pools.
    
    Returns:
        Dictionary with pool statuses
    """
    status = {
        "pools": {},
        "overall_health": "healthy",
    }
    
    # Check Redis
    try:
        redis_pool = await get_redis_pool()
        redis_stats = redis_pool.get_stats()
        redis_health = await check_redis_health()
        
        status["pools"]["redis"] = {
            "health": redis_health["status"],
            "stats": redis_stats,
            "metrics": {
                "utilization": (redis_stats["size"]["current"] / redis_stats["size"]["max"] * 100)
                if redis_stats["size"]["max"] > 0 else 0,
                "error_rate": redis_stats["usage"]["error_rate"],
            }
        }
        
        if redis_health["status"] != "healthy":
            status["overall_health"] = "degraded"
    except Exception as e:
        status["pools"]["redis"] = {
            "health": "error",
            "error": str(e)
        }
        status["overall_health"] = "unhealthy"
    
    # Check Firestore
    try:
        firestore_pool = await get_firestore_pool()
        firestore_stats = firestore_pool.get_stats()
        firestore_health = await check_firestore_health()
        
        status["pools"]["firestore"] = {
            "health": firestore_health["status"],
            "stats": firestore_stats,
            "metrics": {
                "utilization": (firestore_stats["size"]["current"] / firestore_stats["size"]["max"] * 100)
                if firestore_stats["size"]["max"] > 0 else 0,
                "error_rate": firestore_stats["usage"]["error_rate"],
            }
        }
        
        if firestore_health["status"] != "healthy":
            status["overall_health"] = "degraded"
    except Exception as e:
        status["pools"]["firestore"] = {
            "health": "error",
            "error": str(e)
        }
        status["overall_health"] = "unhealthy"
    
    return status