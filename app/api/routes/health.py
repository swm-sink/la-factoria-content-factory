"""
Health Check API Routes

Provides comprehensive health check endpoints for monitoring:
- /health/live - Liveness probe (is service running?)
- /health/ready - Readiness probe (can service handle requests?)
- /health/detailed - Detailed health check with all components
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Query, Response, status

from app.core.health_check import HealthCheckResponse, HealthStatus, get_health_checker, get_http_status_for_health

logger = logging.getLogger(__name__)

# Create router without auth - health checks should be accessible
router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live", summary="Liveness Probe")
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes/Cloud Run liveness probe endpoint.

    Returns 200 if the service is alive and running.
    This endpoint performs minimal checks to avoid cascading failures.

    Returns:
        Basic liveness status
    """
    health_checker = get_health_checker()
    return await health_checker.check_liveness()


@router.get("/ready", summary="Readiness Probe")
async def readiness_check(response: Response) -> Dict[str, Any]:
    """
    Kubernetes/Cloud Run readiness probe endpoint.

    Returns 200 if the service is ready to handle requests.
    Returns 503 if critical dependencies are not available.

    Returns:
        Readiness status with basic component health
    """
    health_checker = get_health_checker()
    result = await health_checker.check_readiness()

    # Set appropriate status code
    if not result.get("ready", False):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return result


@router.get("/", response_model=HealthCheckResponse, summary="Basic Health Check")
async def health_check(response: Response) -> HealthCheckResponse:
    """
    Basic health check endpoint with component status.

    Returns overall health status and basic component information.
    Suitable for monitoring dashboards and alerts.

    Returns:
        Health check response with component status
    """
    health_checker = get_health_checker()
    result = await health_checker.check_all(detailed=False)

    # Set appropriate status code
    response.status_code = get_http_status_for_health(result.status)

    return result


@router.get("/detailed", response_model=HealthCheckResponse, summary="Detailed Health Check")
async def detailed_health_check(
    response: Response,
    include_metrics: bool = Query(False, description="Include performance metrics"),
    check_dependencies: bool = Query(True, description="Check external dependencies"),
) -> HealthCheckResponse:
    """
    Detailed health check with comprehensive component information.

    Provides detailed health status including:
    - All component health with latency measurements
    - System resource usage (CPU, memory, disk)
    - Connection pool statistics
    - External dependency status

    Args:
        include_metrics: Include detailed performance metrics
        check_dependencies: Check external dependencies (may increase latency)

    Returns:
        Comprehensive health check response
    """
    health_checker = get_health_checker()
    result = await health_checker.check_all(detailed=True)

    # Add metrics if requested
    if include_metrics:
        from app.core.metrics import metrics

        result.details = result.details or {}
        result.details["metrics"] = {
            "http_requests_total": metrics.get_counter_value("http_requests_total"),
            "http_request_duration_p95": metrics.get_histogram_value("http_request_duration_seconds", 0.95),
            "active_requests": metrics.get_gauge_value("active_requests"),
            "cache_hits": metrics.get_counter_value("cache_hits"),
            "cache_misses": metrics.get_counter_value("cache_misses"),
        }

    # Set appropriate status code
    response.status_code = get_http_status_for_health(result.status)

    return result


@router.get("/components/{component_name}", summary="Component Health Check")
async def component_health_check(component_name: str, response: Response) -> Dict[str, Any]:
    """
    Check health of a specific component.

    Args:
        component_name: Name of component to check (redis, firestore, vertex_ai)

    Returns:
        Component health status
    """
    health_checker = get_health_checker()

    # Map component names to check methods
    component_checks = {
        "redis": health_checker._check_redis,
        "firestore": health_checker._check_firestore,
        "vertex_ai": health_checker._check_vertex_ai,
        "resources": health_checker._check_system_resources,
    }

    if component_name not in component_checks:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f"Unknown component: {component_name}"}

    try:
        result = await component_checks[component_name]()

        # Set status code based on result
        if isinstance(result, dict):
            component_status = result.get("status", "unhealthy")
            if component_status == "unhealthy":
                response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return {"component": component_name, "result": result}
    except Exception as e:
        logger.error(f"Component health check failed for {component_name}: {e}")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"component": component_name, "status": "unhealthy", "error": str(e)}
