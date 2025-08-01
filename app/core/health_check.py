"""
Enhanced Health Check System

Provides comprehensive health checking for all system components including:
- Database connectivity (Firestore)
- Cache connectivity (Redis)
- External APIs (Vertex AI/Gemini)
- System resources (memory, disk)
- Service dependencies
"""

import asyncio
import logging
import os
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import psutil
from fastapi import status
from pydantic import BaseModel

from app.core.cache import get_cache_backend
from app.core.config.settings import get_settings
from app.services.llm_client import LLMClient
from app.utils.firestore_pool import check_firestore_health, get_firestore_pool
from app.utils.redis_pool import check_redis_health, get_redis_pool

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status levels"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """Health status for a single component"""

    name: str
    status: HealthStatus
    latency_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    last_check: datetime


class SystemResources(BaseModel):
    """System resource usage"""

    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_percent: float
    disk_available_gb: float
    open_connections: int


class HealthCheckResponse(BaseModel):
    """Complete health check response"""

    status: HealthStatus
    timestamp: datetime
    uptime_seconds: float
    version: str
    environment: str
    components: List[ComponentHealth]
    resources: SystemResources
    details: Optional[Dict[str, Any]] = None


class HealthChecker:
    """Comprehensive health checking system"""

    def __init__(self):
        self.settings = get_settings()
        self.start_time = time.time()
        self._llm_client = None

    @property
    def llm_client(self):
        """Lazy initialization of LLM client"""
        if self._llm_client is None:
            self._llm_client = LLMClient(self.settings)
        return self._llm_client

    async def check_all(self, detailed: bool = True) -> HealthCheckResponse:
        """
        Perform comprehensive health check.

        Args:
            detailed: Include detailed component information

        Returns:
            Complete health check response
        """
        # Check all components in parallel
        component_checks = await asyncio.gather(
            self._check_redis(),
            self._check_firestore(),
            self._check_vertex_ai(),
            self._check_system_resources(),
            return_exceptions=True,
        )

        # Process results
        components = []
        overall_status = HealthStatus.HEALTHY

        # Redis health
        redis_health = self._process_component_result("Redis", component_checks[0])
        components.append(redis_health)
        overall_status = self._update_overall_status(overall_status, redis_health.status)

        # Firestore health
        firestore_health = self._process_component_result("Firestore", component_checks[1])
        components.append(firestore_health)
        overall_status = self._update_overall_status(overall_status, firestore_health.status)

        # Vertex AI health
        vertex_health = self._process_component_result("Vertex AI", component_checks[2])
        components.append(vertex_health)
        # Vertex AI is optional, so only degrade if unhealthy
        if vertex_health.status == HealthStatus.UNHEALTHY:
            overall_status = HealthStatus.DEGRADED

        # System resources
        resources = (
            component_checks[3] if isinstance(component_checks[3], SystemResources) else self._get_default_resources()
        )

        # Check resource thresholds
        if resources.memory_percent > 90 or resources.disk_percent > 90:
            overall_status = HealthStatus.DEGRADED
        elif resources.memory_percent > 95 or resources.disk_percent > 95:
            overall_status = HealthStatus.UNHEALTHY

        # Build response
        response = HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.now(timezone.utc),
            uptime_seconds=time.time() - self.start_time,
            version="1.0.0",  # TODO: Get from app version
            environment=os.getenv("ENVIRONMENT", "development"),
            components=components,
            resources=resources,
        )

        if detailed:
            response.details = {
                "service_name": self.settings.project_name,
                "region": os.getenv("REGION", "unknown"),
                "instance_id": os.getenv("INSTANCE_ID", "unknown"),
                "deployment_id": os.getenv("DEPLOYMENT_ID", "unknown"),
            }

        return response

    async def check_liveness(self) -> Dict[str, Any]:
        """
        Simple liveness check - is the service running?

        Returns:
            Basic health status
        """
        return {
            "status": "alive",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": time.time() - self.start_time,
        }

    async def check_readiness(self) -> Dict[str, Any]:
        """
        Readiness check - is the service ready to handle requests?

        Returns:
            Readiness status with basic component health
        """
        # Quick checks for critical components
        redis_ready = await self._quick_redis_check()
        firestore_ready = await self._quick_firestore_check()

        is_ready = redis_ready and firestore_ready

        return {
            "ready": is_ready,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {
                "redis": "ready" if redis_ready else "not_ready",
                "firestore": "ready" if firestore_ready else "not_ready",
            },
        }

    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis health with timing"""
        start_time = time.time()
        try:
            result = await check_redis_health()
            latency_ms = (time.time() - start_time) * 1000

            return {"status": result.get("status", "unhealthy"), "latency_ms": latency_ms, "details": result}
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"status": "unhealthy", "error": str(e), "latency_ms": (time.time() - start_time) * 1000}

    async def _check_firestore(self) -> Dict[str, Any]:
        """Check Firestore health with timing"""
        start_time = time.time()
        try:
            result = await check_firestore_health()
            latency_ms = (time.time() - start_time) * 1000

            return {"status": result.get("status", "unhealthy"), "latency_ms": latency_ms, "details": result}
        except Exception as e:
            logger.error(f"Firestore health check failed: {e}")
            return {"status": "unhealthy", "error": str(e), "latency_ms": (time.time() - start_time) * 1000}

    async def _check_vertex_ai(self) -> Dict[str, Any]:
        """Check Vertex AI/Gemini API health"""
        start_time = time.time()
        try:
            # Simple test generation
            test_prompt = "Respond with 'OK' if you receive this."
            # Run synchronous call in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.llm_client.generate_content,
                test_prompt,
                "health_check",
                0.0,  # temperature
                10,  # max_output_tokens
                None,  # response_schema
            )

            latency_ms = (time.time() - start_time) * 1000
            is_healthy = response and len(response) > 0

            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "latency_ms": latency_ms,
                "details": {
                    "response_received": is_healthy,
                    "model": self.llm_client.model_name if hasattr(self.llm_client, "model_name") else "gemini-pro",
                },
            }
        except Exception as e:
            logger.error(f"Vertex AI health check failed: {e}")
            return {"status": "unhealthy", "error": str(e), "latency_ms": (time.time() - start_time) * 1000}

    async def _check_system_resources(self) -> SystemResources:
        """Check system resource usage"""
        try:
            # CPU usage (averaged over 1 second)
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_mb = memory.available / (1024 * 1024)

            # Disk usage (for root partition)
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            disk_available_gb = disk.free / (1024 * 1024 * 1024)

            # Network connections
            connections = len(psutil.net_connections())

            return SystemResources(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_mb=round(memory_available_mb, 2),
                disk_percent=disk_percent,
                disk_available_gb=round(disk_available_gb, 2),
                open_connections=connections,
            )
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return self._get_default_resources()

    async def _quick_redis_check(self) -> bool:
        """Quick Redis connectivity check for readiness"""
        try:
            pool = await get_redis_pool()
            # Just check if pool is initialized and has connections
            stats = pool.get_stats()
            return stats["current_size"] > 0 or stats["available"] > 0
        except Exception:
            return False

    async def _quick_firestore_check(self) -> bool:
        """Quick Firestore connectivity check for readiness"""
        try:
            pool = await get_firestore_pool()
            # Just check if pool is initialized and has connections
            stats = pool.get_stats()
            return stats["current_size"] > 0 or stats["available"] > 0
        except Exception:
            return False

    def _process_component_result(self, name: str, result: Any) -> ComponentHealth:
        """Process component check result into ComponentHealth"""
        if isinstance(result, Exception):
            return ComponentHealth(
                name=name, status=HealthStatus.UNHEALTHY, error=str(result), last_check=datetime.now(timezone.utc)
            )

        if isinstance(result, dict):
            status_str = result.get("status", "unhealthy")
            status = (
                HealthStatus(status_str) if status_str in [s.value for s in HealthStatus] else HealthStatus.UNHEALTHY
            )

            return ComponentHealth(
                name=name,
                status=status,
                latency_ms=result.get("latency_ms"),
                details=result.get("details"),
                error=result.get("error"),
                last_check=datetime.now(timezone.utc),
            )

        return ComponentHealth(
            name=name,
            status=HealthStatus.UNHEALTHY,
            error="Invalid result format",
            last_check=datetime.now(timezone.utc),
        )

    def _update_overall_status(self, current: HealthStatus, component: HealthStatus) -> HealthStatus:
        """Update overall status based on component status"""
        if component == HealthStatus.UNHEALTHY:
            return HealthStatus.UNHEALTHY
        elif component == HealthStatus.DEGRADED and current != HealthStatus.UNHEALTHY:
            return HealthStatus.DEGRADED
        return current

    def _get_default_resources(self) -> SystemResources:
        """Get default resource values when check fails"""
        return SystemResources(
            cpu_percent=0.0,
            memory_percent=0.0,
            memory_available_mb=0.0,
            disk_percent=0.0,
            disk_available_gb=0.0,
            open_connections=0,
        )


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get or create health checker instance"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


# HTTP status code mapping
def get_http_status_for_health(health_status: HealthStatus) -> int:
    """Map health status to HTTP status code"""
    mapping = {
        HealthStatus.HEALTHY: status.HTTP_200_OK,
        HealthStatus.DEGRADED: status.HTTP_200_OK,  # Still operational
        HealthStatus.UNHEALTHY: status.HTTP_503_SERVICE_UNAVAILABLE,
    }
    return mapping.get(health_status, status.HTTP_503_SERVICE_UNAVAILABLE)
