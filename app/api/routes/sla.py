"""
SLA Dashboard API endpoints

Provides SLA metrics, compliance status, and reporting endpoints.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Depends

from app.services.sla_monitor import sla_monitor
from app.core.security import require_api_key
from app.core.cache import get_cache_backend
from app.core.metrics import metrics

# Get cache instance
cache = get_cache_backend()

router = APIRouter(prefix="/sla", tags=["SLA"])


@router.get("/status")
async def get_sla_status(
    _: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    Get current SLA status including compliance rates and error budgets.
    
    Returns:
        Current SLA status with SLOs, error budgets, and active alerts
    """
    try:
        status = await sla_monitor.get_sla_status()
        
        # Record access metric
        metrics.increment("api.sla.status.requests")
        
        return status
    except Exception as e:
        metrics.increment("api.sla.status.errors")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/slos/{slo_name}")
async def get_slo_details(
    slo_name: str,
    hours: int = Query(24, description="Hours of history to retrieve"),
    _: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific SLO.
    
    Args:
        slo_name: Name of the SLO
        hours: Number of hours of history to include
        
    Returns:
        SLO details with historical SLI data
    """
    try:
        if slo_name not in sla_monitor.slos:
            raise HTTPException(status_code=404, detail=f"SLO '{slo_name}' not found")
        
        slo = sla_monitor.slos[slo_name]
        history = await sla_monitor.get_sli_history(slo_name, hours)
        
        return {
            "name": slo.name,
            "description": slo.description,
            "target": slo.target,
            "window": slo.window,
            "compliance_rate": slo.compliance_rate,
            "is_met": slo.is_met,
            "history": history,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        metrics.increment("api.sla.slo_details.errors")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/error-budgets")
async def get_error_budgets(
    _: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    Get error budget status for all SLOs.
    
    Returns:
        Error budget consumption and burn rates
    """
    try:
        budgets = {}
        
        for name, budget in sla_monitor.error_budgets.items():
            budgets[name] = {
                "total_minutes": budget.total_minutes,
                "consumed_minutes": budget.consumed_minutes,
                "remaining_minutes": budget.remaining_minutes,
                "consumption_rate": budget.consumption_rate,
                "burn_rate": budget.burn_rate,
                "status": "critical" if budget.burn_rate >= 10 else
                         "error" if budget.burn_rate >= 5 else
                         "warning" if budget.burn_rate >= 2 else
                         "normal"
            }
        
        return {
            "error_budgets": budgets,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        metrics.increment("api.sla.error_budgets.errors")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report")
async def generate_sla_report(
    period: str = Query("weekly", description="Report period: daily, weekly, monthly"),
    _: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    Generate SLA compliance report.
    
    Args:
        period: Report period (daily, weekly, monthly)
        
    Returns:
        Comprehensive SLA report with compliance metrics and recommendations
    """
    try:
        if period not in ["daily", "weekly", "monthly"]:
            raise HTTPException(status_code=400, detail="Invalid period. Use: daily, weekly, monthly")
        
        report = await sla_monitor.generate_sla_report(period)
        
        # Cache report for quick access
        cache_key = f"sla_report:{period}:{datetime.utcnow().date()}"
        await cache.set(cache_key, report, expire=3600)
        
        metrics.increment(f"api.sla.report.{period}")
        
        return report
    except HTTPException:
        raise
    except Exception as e:
        metrics.increment("api.sla.report.errors")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_active_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity: warning, error, critical"),
    _: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    Get active SLA alerts.
    
    Args:
        severity: Optional severity filter
        
    Returns:
        List of active alerts
    """
    try:
        # Get all alerts from cache
        alert_keys = await cache.keys("sla_alert:*")
        alerts = []
        
        for key in alert_keys:
            alert_data = await cache.get(key)
            if alert_data:
                alert = eval(alert_data) if isinstance(alert_data, str) else alert_data
                if not severity or alert.get("severity") == severity:
                    alerts.append(alert)
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "alerts": alerts,
            "count": len(alerts),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        metrics.increment("api.sla.alerts.errors")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/realtime")
async def get_realtime_metrics(
    _: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    Get real-time SLA metrics for dashboard display.
    
    Returns:
        Real-time metrics for dashboard widgets
    """
    try:
        # Get latest metrics from cache
        realtime = {
            "api_availability": await cache.get("health_check_success_rate") or 99.9,
            "api_latency_p95": await cache.get("api_latency_p95") or 250,
            "api_latency_p99": await cache.get("api_latency_p99") or 500,
            "error_rate": await cache.get("api_error_rate") or 0.5,
            "content_success_rate": await cache.get("content_generation_success_rate") or 98.5,
            "active_alerts": len(await cache.keys("sla_alert:*")),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Calculate overall health score
        health_score = (
            (realtime["api_availability"] / 100) * 0.4 +
            (1 - min(realtime["api_latency_p95"] / 500, 1)) * 0.3 +
            (1 - realtime["error_rate"] / 100) * 0.2 +
            (realtime["content_success_rate"] / 100) * 0.1
        ) * 100
        
        realtime["health_score"] = round(health_score, 2)
        
        return realtime
    except Exception as e:
        metrics.increment("api.sla.realtime.errors")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{slo_name}/acknowledge")
async def acknowledge_alert(
    slo_name: str,
    severity: str = Query(..., description="Alert severity to acknowledge"),
    _: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    Acknowledge an SLA alert.
    
    Args:
        slo_name: Name of the SLO
        severity: Alert severity
        
    Returns:
        Acknowledgement confirmation
    """
    try:
        alert_key = f"sla_alert:{slo_name}:{severity}"
        alert_data = await cache.get(alert_key)
        
        if not alert_data:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Mark as acknowledged
        alert = eval(alert_data) if isinstance(alert_data, str) else alert_data
        alert["acknowledged"] = True
        alert["acknowledged_at"] = datetime.utcnow().isoformat()
        
        # Update cache with shorter TTL
        await cache.set(alert_key, alert, expire=300)  # 5 minutes
        
        metrics.increment("api.sla.alerts.acknowledged")
        
        return {
            "status": "acknowledged",
            "slo": slo_name,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        metrics.increment("api.sla.alerts.acknowledge_errors")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dependencies")
async def get_service_dependencies(
    _: str = Depends(require_api_key)
) -> Dict[str, Any]:
    """
    Get service dependency status.
    
    Returns:
        Health status of all service dependencies
    """
    try:
        dependencies = {
            "postgresql": {
                "status": await cache.get("dependency_postgresql_status") or "healthy",
                "latency": await cache.get("dependency_postgresql_latency") or 5,
                "last_check": await cache.get("dependency_postgresql_last_check") or datetime.utcnow().isoformat()
            },
            "redis": {
                "status": await cache.get("dependency_redis_status") or "healthy",
                "latency": await cache.get("dependency_redis_latency") or 1,
                "last_check": await cache.get("dependency_redis_last_check") or datetime.utcnow().isoformat()
            },
            "gemini_api": {
                "status": await cache.get("dependency_gemini_status") or "healthy",
                "latency": await cache.get("dependency_gemini_latency") or 200,
                "last_check": await cache.get("dependency_gemini_last_check") or datetime.utcnow().isoformat()
            },
            "elevenlabs_api": {
                "status": await cache.get("dependency_elevenlabs_status") or "healthy",
                "latency": await cache.get("dependency_elevenlabs_latency") or 300,
                "last_check": await cache.get("dependency_elevenlabs_last_check") or datetime.utcnow().isoformat()
            },
            "cdn": {
                "status": await cache.get("dependency_cdn_status") or "healthy",
                "latency": await cache.get("dependency_cdn_latency") or 50,
                "last_check": await cache.get("dependency_cdn_last_check") or datetime.utcnow().isoformat()
            }
        }
        
        # Calculate overall dependency health
        healthy_count = sum(1 for dep in dependencies.values() if dep["status"] == "healthy")
        total_count = len(dependencies)
        
        return {
            "dependencies": dependencies,
            "overall_health": (healthy_count / total_count) * 100,
            "healthy_count": healthy_count,
            "total_count": total_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        metrics.increment("api.sla.dependencies.errors")
        raise HTTPException(status_code=500, detail=str(e))