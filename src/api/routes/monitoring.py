"""
La Factoria Monitoring and Health Check Endpoints
Production-ready monitoring with comprehensive system health validation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
import asyncio
import time
import psutil
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ...core.config import settings
from ...core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", tags=["Monitoring"])
async def health_check():
    """
    Basic health check endpoint for Railway deployment
    Used by Railway for automated health monitoring
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

@router.get("/health/detailed", tags=["Monitoring"])
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check with system metrics
    Validates all critical services and dependencies
    """
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "checks": {},
        "metrics": {},
        "response_time_ms": 0
    }

    try:
        # Database connectivity check
        health_status["checks"]["database"] = await _check_database_health(db)

        # AI providers availability check
        health_status["checks"]["ai_providers"] = await _check_ai_providers_health()

        # System resources check
        health_status["checks"]["system_resources"] = _check_system_resources()

        # Application metrics
        health_status["metrics"] = await _get_application_metrics(db)

        # Overall health determination
        failed_checks = [name for name, check in health_status["checks"].items()
                        if check.get("status") != "healthy"]

        if failed_checks:
            health_status["status"] = "degraded"
            health_status["failed_checks"] = failed_checks

        # Calculate response time
        health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)

        # Return appropriate HTTP status
        http_status = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "response_time_ms": round((time.time() - start_time) * 1000, 2)
        }

@router.get("/metrics", tags=["Monitoring"])
async def get_system_metrics(db: AsyncSession = Depends(get_db)):
    """
    System and application metrics for monitoring
    Used for performance tracking and alerting
    """
    try:
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": _get_system_metrics(),
            "application": await _get_application_metrics(db),
            "educational": await _get_educational_metrics(db),
            "performance": await _get_performance_metrics(db)
        }

        return metrics

    except Exception as e:
        logger.error(f"Metrics collection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metrics collection failed: {str(e)}"
        )

@router.get("/metrics/educational", tags=["Monitoring"])
async def get_educational_metrics(db: AsyncSession = Depends(get_db)):
    """
    Educational-specific metrics for La Factoria platform
    Quality scores, content generation rates, user engagement
    """
    try:
        # Get educational content statistics
        content_stats_query = """
        SELECT
            content_type,
            COUNT(*) as total_generated,
            AVG(quality_score) as avg_quality,
            AVG(educational_effectiveness) as avg_educational_value,
            AVG(factual_accuracy) as avg_factual_accuracy,
            AVG(generation_duration_ms) as avg_generation_time_ms
        FROM educational_content
        WHERE created_at >= NOW() - INTERVAL '24 hours'
        GROUP BY content_type
        """

        result = await db.execute(text(content_stats_query))
        content_stats = [dict(row._mapping) for row in result]

        # Get quality distribution
        quality_dist_query = """
        SELECT
            CASE
                WHEN quality_score >= 0.9 THEN 'excellent'
                WHEN quality_score >= 0.8 THEN 'good'
                WHEN quality_score >= 0.7 THEN 'acceptable'
                ELSE 'below_threshold'
            END as quality_category,
            COUNT(*) as count
        FROM educational_content
        WHERE created_at >= NOW() - INTERVAL '24 hours'
        GROUP BY quality_category
        """

        result = await db.execute(text(quality_dist_query))
        quality_distribution = [dict(row._mapping) for row in result]

        # Get recent generation trends
        trends_query = """
        SELECT
            DATE_TRUNC('hour', created_at) as hour,
            COUNT(*) as generations,
            AVG(quality_score) as avg_quality
        FROM educational_content
        WHERE created_at >= NOW() - INTERVAL '24 hours'
        GROUP BY hour
        ORDER BY hour
        """

        result = await db.execute(text(trends_query))
        generation_trends = [dict(row._mapping) for row in result]

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content_type_stats": content_stats,
            "quality_distribution": quality_distribution,
            "generation_trends": generation_trends,
            "quality_thresholds": {
                "overall": settings.QUALITY_THRESHOLD_OVERALL,
                "educational": settings.QUALITY_THRESHOLD_EDUCATIONAL,
                "factual": settings.QUALITY_THRESHOLD_FACTUAL
            }
        }

    except Exception as e:
        logger.error(f"Educational metrics collection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Educational metrics collection failed: {str(e)}"
        )

@router.get("/status", tags=["Monitoring"])
async def get_service_status():
    """
    Service status overview for operational monitoring
    Quick status check for all major components
    """
    try:
        status_info = {
            "platform": "La Factoria Educational Content Platform",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime": _get_uptime(),
            "services": {
                "api": "operational",
                "database": "operational" if settings.DATABASE_URL else "not_configured",
                "ai_providers": settings.available_ai_providers,
                "frontend": "operational",
                "monitoring": "operational"
            },
            "features": {
                "content_generation": True,
                "quality_assessment": True,
                "educational_standards": True,
                "multi_provider_ai": len(settings.available_ai_providers) > 0,
                "prompt_management": settings.has_langfuse_config,
                "caching": bool(settings.REDIS_URL)
            },
            "configuration": {
                "max_tokens": settings.DEFAULT_MAX_TOKENS,
                "timeout": settings.CONTENT_GENERATION_TIMEOUT,
                "rate_limits": {
                    "requests_per_minute": settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
                    "generations_per_hour": settings.RATE_LIMIT_GENERATIONS_PER_HOUR
                }
            }
        }

        return status_info

    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check failed: {str(e)}"
        )

# Helper functions for health checks and metrics

async def _check_database_health(db: AsyncSession) -> Dict[str, Any]:
    """Check database connectivity and basic operations"""
    try:
        # Simple connectivity test
        await db.execute(text("SELECT 1"))

        # Check if main tables exist
        table_check = await db.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('users', 'educational_content', 'quality_assessments')
        """))

        tables = [row[0] for row in table_check]

        return {
            "status": "healthy",
            "connection": "ok",
            "tables_available": len(tables),
            "required_tables": tables
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

async def _check_ai_providers_health() -> Dict[str, Any]:
    """Check AI provider configurations"""
    providers = {
        "openai": settings.has_openai_config,
        "anthropic": settings.has_anthropic_config,
        "vertex_ai": bool(settings.GOOGLE_CLOUD_PROJECT),
        "elevenlabs": settings.has_elevenlabs_config
    }

    available_count = sum(providers.values())

    return {
        "status": "healthy" if available_count > 0 else "unhealthy",
        "available_providers": [name for name, available in providers.items() if available],
        "total_configured": available_count,
        "providers": providers
    }

def _check_system_resources() -> Dict[str, Any]:
    """Check system resource usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Determine status based on resource usage
        status = "healthy"
        if cpu_percent > 80 or memory.percent > 80 or disk.percent > 90:
            status = "warning"
        if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
            status = "critical"

        return {
            "status": status,
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2)
        }

    except Exception as e:
        return {
            "status": "unknown",
            "error": str(e)
        }

def _get_system_metrics() -> Dict[str, Any]:
    """Get detailed system metrics"""
    try:
        return {
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "load_avg": list(psutil.getloadavg())
            },
            "memory": {
                "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                "percent_used": psutil.virtual_memory().percent
            },
            "disk": {
                "total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
                "free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
                "percent_used": psutil.disk_usage('/').percent
            },
            "network": dict(psutil.net_io_counters()._asdict()) if hasattr(psutil.net_io_counters(), '_asdict') else {}
        }
    except Exception as e:
        return {"error": str(e)}

async def _get_application_metrics(db: AsyncSession) -> Dict[str, Any]:
    """Get application-specific metrics"""
    try:
        # Total content generated
        total_content = await db.execute(text("SELECT COUNT(*) FROM educational_content"))
        total_count = total_content.scalar()

        # Content generated in last 24 hours
        recent_content = await db.execute(text("""
            SELECT COUNT(*) FROM educational_content
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """))
        recent_count = recent_content.scalar()

        # Average quality scores
        quality_avg = await db.execute(text("""
            SELECT AVG(quality_score) FROM educational_content
            WHERE created_at >= NOW() - INTERVAL '24 hours'
        """))
        avg_quality = quality_avg.scalar() or 0

        return {
            "total_content_generated": total_count or 0,
            "content_last_24h": recent_count or 0,
            "average_quality_24h": round(float(avg_quality), 3),
            "uptime": _get_uptime()
        }

    except Exception as e:
        return {
            "error": str(e),
            "uptime": _get_uptime()
        }

async def _get_educational_metrics(db: AsyncSession) -> Dict[str, Any]:
    """Get educational-specific metrics"""
    try:
        # Content type distribution
        type_dist = await db.execute(text("""
            SELECT content_type, COUNT(*) as count
            FROM educational_content
            WHERE created_at >= NOW() - INTERVAL '7 days'
            GROUP BY content_type
        """))

        content_distribution = {row[0]: row[1] for row in type_dist}

        # Quality metrics by threshold
        quality_metrics = await db.execute(text("""
            SELECT
                COUNT(CASE WHEN quality_score >= 0.7 THEN 1 END) as meets_overall_threshold,
                COUNT(CASE WHEN educational_effectiveness >= 0.75 THEN 1 END) as meets_educational_threshold,
                COUNT(CASE WHEN factual_accuracy >= 0.85 THEN 1 END) as meets_factual_threshold,
                COUNT(*) as total
            FROM educational_content
            WHERE created_at >= NOW() - INTERVAL '7 days'
        """))

        metrics = quality_metrics.fetchone()

        return {
            "content_type_distribution": content_distribution,
            "quality_compliance": {
                "overall_threshold_rate": round((metrics[0] / max(metrics[3], 1)) * 100, 2),
                "educational_threshold_rate": round((metrics[1] / max(metrics[3], 1)) * 100, 2),
                "factual_threshold_rate": round((metrics[2] / max(metrics[3], 1)) * 100, 2),
                "total_assessed": metrics[3]
            }
        }

    except Exception as e:
        return {"error": str(e)}

async def _get_performance_metrics(db: AsyncSession) -> Dict[str, Any]:
    """Get performance metrics"""
    try:
        # Average generation times by content type
        perf_metrics = await db.execute(text("""
            SELECT
                content_type,
                AVG(generation_duration_ms) as avg_duration_ms,
                COUNT(*) as count
            FROM educational_content
            WHERE created_at >= NOW() - INTERVAL '24 hours'
            AND generation_duration_ms IS NOT NULL
            GROUP BY content_type
        """))

        performance_by_type = {
            row[0]: {
                "avg_duration_ms": round(row[1], 2),
                "count": row[2]
            } for row in perf_metrics
        }

        return {
            "generation_performance_by_type": performance_by_type,
            "targets": {
                "max_generation_time_ms": 30000,  # 30 seconds
                "max_quality_assessment_ms": 5000  # 5 seconds
            }
        }

    except Exception as e:
        return {"error": str(e)}

def _get_uptime() -> Dict[str, Any]:
    """Get application uptime information"""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = (datetime.now() - boot_time).total_seconds()

        return {
            "boot_time": boot_time.isoformat(),
            "uptime_seconds": int(uptime_seconds),
            "uptime_human": str(timedelta(seconds=int(uptime_seconds)))
        }
    except Exception:
        return {"uptime_human": "unknown"}
