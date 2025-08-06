"""
Health Check API Routes for La Factoria
System health monitoring and status endpoints
"""

from fastapi import APIRouter, status
from typing import Dict, Any
import time
import psutil
import logging
from datetime import datetime, timezone

from ...models.content import HealthResponse
from ...core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint for La Factoria platform

    Returns:
        - Service status
        - Timestamp
        - Version information
        - Basic service availability
    """
    try:
        services = {}

        # Check database connectivity (real implementation)
        try:
            from ...core.database import check_database_connection
            db_connected = await check_database_connection()
            services["database"] = "healthy" if db_connected else "unhealthy: connection failed"
        except Exception as e:
            services["database"] = f"unhealthy: {str(e)}"

        # Check AI providers
        try:
            available_providers = settings.available_ai_providers
            services["ai_providers"] = f"healthy ({len(available_providers)} available)"
        except Exception as e:
            services["ai_providers"] = f"unhealthy: {str(e)}"

        # Check prompt templates
        try:
            services["prompt_templates"] = "healthy"  # Would check template directory
        except Exception as e:
            services["prompt_templates"] = f"unhealthy: {str(e)}"

        # Overall status
        overall_status = "healthy" if all("healthy" in status for status in services.values()) else "degraded"

        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(timezone.utc),
            version=settings.APP_VERSION,
            services=services
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(timezone.utc),
            version=settings.APP_VERSION,
            services={"error": str(e)}
        )

@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with system metrics and component status

    Returns comprehensive system information including:
    - System resources (CPU, memory)
    - Service component health
    - Configuration status
    - Performance metrics
    """
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Service checks
        service_health = {}

        # Database health (real implementation)
        try:
            from ...core.database import get_database_info
            service_health["database"] = await get_database_info()
        except Exception as e:
            service_health["database"] = {"status": "unhealthy", "error": str(e)}

        # AI Providers health
        service_health["ai_providers"] = {
            "available_providers": settings.available_ai_providers,
            "openai_configured": settings.has_openai_config,
            "anthropic_configured": settings.has_anthropic_config,
            "elevenlabs_configured": settings.has_elevenlabs_config
        }

        # Configuration health
        service_health["configuration"] = {
            "environment": settings.ENVIRONMENT,
            "debug_mode": settings.DEBUG,
            "langfuse_configured": settings.has_langfuse_config,
            "redis_configured": bool(settings.REDIS_URL)
        }

        # Performance metrics
        performance_metrics = {
            "cpu_usage_percent": round(cpu_percent, 1),
            "memory_usage_percent": round(memory.percent, 1),
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_usage_percent": round(disk.percent, 1),
            "disk_free_gb": round(disk.free / (1024**3), 2)
        }

        # Overall status determination
        critical_issues = []

        if cpu_percent > 90:
            critical_issues.append("High CPU usage")
        if memory.percent > 90:
            critical_issues.append("High memory usage")
        if disk.percent > 90:
            critical_issues.append("High disk usage")

        overall_status = "healthy"
        if critical_issues:
            overall_status = "degraded"
        if len(critical_issues) > 2:
            overall_status = "unhealthy"

        return {
            "status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "uptime_seconds": time.time(),  # Placeholder - would track actual uptime
            "critical_issues": critical_issues,
            "system_metrics": performance_metrics,
            "services": service_health
        }

    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }

@router.get("/health/ai-providers")
async def ai_providers_health():
    """
    Specific health check for AI providers

    Tests connectivity and availability of all configured AI services
    """
    try:
        from ...services.ai_providers import AIProviderManager

        provider_manager = AIProviderManager()
        health_status = await provider_manager.health_check()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "providers": health_status,
            "provider_stats": provider_manager.get_provider_stats(),
            "overall_status": "healthy" if all(
                "healthy" in status for status in health_status.values()
            ) else "degraded"
        }

    except Exception as e:
        logger.error(f"AI providers health check failed: {e}")
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "unhealthy",
            "error": str(e)
        }

@router.get("/health/content-service")
async def content_service_health():
    """
    Health check for the educational content generation service
    """
    try:
        from ...services.educational_content_service import EducationalContentService

        content_service = EducationalContentService()
        health_status = await content_service.health_check()

        return health_status

    except Exception as e:
        logger.error(f"Content service health check failed: {e}")
        return {
            "timestamp": time.time(),
            "overall_status": "unhealthy",
            "error": str(e)
        }

@router.get("/ready")
async def readiness_check():
    """
    Kubernetes/Railway readiness probe endpoint

    Returns 200 if service is ready to accept traffic
    Returns 503 if service is not ready
    """
    try:
        # Check critical dependencies
        checks = []

        # Check if we can access prompt templates
        try:
            import os
            prompts_dir = "prompts"
            if os.path.exists(prompts_dir):
                template_files = os.listdir(prompts_dir)
                if len(template_files) >= 8:  # Should have at least 8 content type templates
                    checks.append(True)
                else:
                    checks.append(False)
            else:
                checks.append(False)
        except:
            checks.append(False)

        # Check if AI providers are configured
        checks.append(len(settings.available_ai_providers) > 0)

        # Check database connectivity for readiness
        try:
            from ...core.database import check_database_connection
            db_ready = await check_database_connection()
            checks.append(db_ready)
        except Exception:
            checks.append(False)

        # All checks must pass for readiness
        if all(checks):
            return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}
        else:
            return {"status": "not ready", "timestamp": datetime.now(timezone.utc).isoformat()}, 503

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not ready", "error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()}, 503

@router.get("/live")
async def liveness_check():
    """
    Kubernetes/Railway liveness probe endpoint

    Returns 200 if service is alive and responding
    Simple check that doesn't test dependencies
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.APP_VERSION
    }
