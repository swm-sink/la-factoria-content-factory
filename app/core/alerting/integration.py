"""
Alert Integration with Monitoring System

Provides integration between the alert manager and existing monitoring infrastructure.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.alerts import AlertSeverity, get_alert_config
from app.core.metrics import get_metrics_collector

from .config import get_alert_manager
from .models import AlertStatus

logger = logging.getLogger(__name__)


def setup_alert_endpoints(app: FastAPI) -> None:
    """Set up alert webhook endpoints"""

    @app.post("/alerts/webhook")
    async def receive_prometheus_alert(request: Request) -> JSONResponse:
        """Receive alerts from Prometheus Alertmanager"""
        try:
            data = await request.json()
            alert_manager = get_alert_manager()

            # Process each alert
            alerts_received = 0
            alerts_processed = 0

            for alert_data in data.get("alerts", []):
                alerts_received += 1

                # Convert Prometheus alert to our format
                alert = await _convert_prometheus_alert(alert_data)

                if alert:
                    # Fire or resolve alert
                    if alert_data.get("status") == "resolved":
                        await alert_manager.resolve_alert(alert["id"])
                    else:
                        await alert_manager.fire_alert(alert)

                    alerts_processed += 1

            # Track metrics
            metrics = get_metrics_collector()
            metrics.increment("alerts.received", alerts_received)
            metrics.increment("alerts.processed", alerts_processed)

            return JSONResponse(
                {
                    "status": "success",
                    "alerts_received": alerts_received,
                    "alerts_processed": alerts_processed,
                }
            )

        except Exception as e:
            logger.error(f"Error processing alert webhook: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/alerts/fire")
    async def fire_manual_alert(request: Request) -> JSONResponse:
        """Manually fire an alert (for testing)"""
        try:
            data = await request.json()
            alert_manager = get_alert_manager()

            # Validate required fields
            required = ["name", "summary", "severity"]
            for field in required:
                if field not in data:
                    raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

            # Fire alert
            alert = await alert_manager.fire_alert(data)

            return JSONResponse(
                {
                    "status": "success",
                    "alert_id": alert.id,
                    "fingerprint": alert.fingerprint,
                }
            )

        except Exception as e:
            logger.error(f"Error firing manual alert: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/alerts/{alert_id}/acknowledge")
    async def acknowledge_alert(alert_id: str, request: Request) -> JSONResponse:
        """Acknowledge an alert"""
        try:
            data = await request.json()
            acknowledger = data.get("acknowledger", "unknown")

            alert_manager = get_alert_manager()
            success = await alert_manager.acknowledge_alert(alert_id, acknowledger)

            if not success:
                raise HTTPException(status_code=404, detail="Alert not found")

            return JSONResponse(
                {
                    "status": "success",
                    "alert_id": alert_id,
                    "acknowledged_by": acknowledger,
                }
            )

        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/alerts/{alert_id}/resolve")
    async def resolve_alert(alert_id: str) -> JSONResponse:
        """Resolve an alert"""
        try:
            alert_manager = get_alert_manager()
            success = await alert_manager.resolve_alert(alert_id)

            if not success:
                raise HTTPException(status_code=404, detail="Alert not found")

            return JSONResponse(
                {
                    "status": "success",
                    "alert_id": alert_id,
                }
            )

        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/alerts/{alert_id}/silence")
    async def silence_alert(alert_id: str, request: Request) -> JSONResponse:
        """Silence an alert"""
        try:
            data = await request.json()
            duration = data.get("duration", 3600)
            comment = data.get("comment")

            alert_manager = get_alert_manager()
            success = await alert_manager.silence_alert(alert_id, duration, comment)

            if not success:
                raise HTTPException(status_code=404, detail="Alert not found")

            return JSONResponse(
                {
                    "status": "success",
                    "alert_id": alert_id,
                    "silenced_for": duration,
                }
            )

        except Exception as e:
            logger.error(f"Error silencing alert: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/alerts/active")
    async def get_active_alerts() -> JSONResponse:
        """Get all active alerts"""
        try:
            alert_manager = get_alert_manager()

            active_alerts = []
            for alert in alert_manager.active_alerts.values():
                active_alerts.append(alert.to_dict())

            return JSONResponse(
                {
                    "status": "success",
                    "count": len(active_alerts),
                    "alerts": active_alerts,
                }
            )

        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            raise HTTPException(status_code=500, detail=str(e))


async def _convert_prometheus_alert(alert_data: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Convert Prometheus alert format to our format"""
    try:
        # Extract labels and annotations
        labels = alert_data.get("labels", {})
        annotations = alert_data.get("annotations", {})

        # Map Prometheus severity to our severity
        severity_map = {
            "critical": "critical",
            "warning": "warning",
            "info": "info",
            "page": "high",
        }
        severity = severity_map.get(labels.get("severity", "warning"), "warning")

        # Get alert configuration if available
        alert_name = labels.get("alertname", "Unknown")
        alert_config = get_alert_config(alert_name.lower().replace(" ", "_"))

        # Build alert object
        alert = {
            "id": alert_data.get("fingerprint", alert_name),
            "name": alert_name,
            "severity": severity,
            "summary": annotations.get("summary", alert_name),
            "description": annotations.get("description", ""),
            "service": labels.get("service", labels.get("job", "unknown")),
            "environment": labels.get("environment", "production"),
            "labels": labels,
            "annotations": annotations,
            "starts_at": alert_data.get("startsAt"),
        }

        # Add value if present
        if "value" in alert_data:
            alert["value"] = float(alert_data["value"])

        # Add runbook URL from config or annotations
        if alert_config:
            alert["runbook_url"] = alert_config.runbook_url
            alert["threshold"] = alert_config.threshold
        elif "runbook_url" in annotations:
            alert["runbook_url"] = annotations["runbook_url"]

        # Add dashboard URL
        if "dashboard_url" in annotations:
            alert["dashboard_url"] = annotations["dashboard_url"]

        return alert

    except Exception as e:
        logger.error(f"Error converting Prometheus alert: {e}")
        return None


def create_metric_alerts() -> None:
    """Create alerts based on application metrics"""

    async def check_metrics():
        """Periodically check metrics and fire alerts"""
        alert_manager = get_alert_manager()
        metrics = get_metrics_collector()

        while True:
            try:
                # Check error rate
                error_rate = metrics.get_value("http_requests_total", {"status": "5xx"})
                total_requests = metrics.get_value("http_requests_total")

                if total_requests > 0:
                    error_percent = (error_rate / total_requests) * 100

                    if error_percent > 5:
                        await alert_manager.fire_alert(
                            {
                                "name": "HighErrorRate",
                                "severity": "high",
                                "summary": "High API error rate detected",
                                "description": f"Error rate is {error_percent:.2f}%",
                                "service": "api",
                                "value": error_percent,
                                "threshold": 5,
                                "labels": {"source": "metrics"},
                            }
                        )

                # Check response time
                p95_latency = metrics.get_percentile("http_request_duration_seconds", 0.95)

                if p95_latency > 1.0:  # 1 second
                    await alert_manager.fire_alert(
                        {
                            "name": "SlowAPIResponse",
                            "severity": "warning",
                            "summary": "API response time is high",
                            "description": f"95th percentile latency is {p95_latency:.2f}s",
                            "service": "api",
                            "value": p95_latency,
                            "threshold": 1.0,
                            "labels": {"source": "metrics"},
                        }
                    )

                # Check memory usage
                memory_usage = metrics.get_value("process_resident_memory_bytes")
                memory_limit = metrics.get_value("process_virtual_memory_bytes")

                if memory_limit > 0:
                    memory_percent = (memory_usage / memory_limit) * 100

                    if memory_percent > 85:
                        await alert_manager.fire_alert(
                            {
                                "name": "HighMemoryUsage",
                                "severity": "warning",
                                "summary": "High memory usage detected",
                                "description": f"Memory usage is {memory_percent:.2f}%",
                                "service": "api",
                                "value": memory_percent,
                                "threshold": 85,
                                "labels": {"source": "metrics"},
                            }
                        )

            except Exception as e:
                logger.error(f"Error checking metrics: {e}")

            await asyncio.sleep(60)  # Check every minute

    # Start metric checking task
    asyncio.create_task(check_metrics())


async def start_alert_manager(app: FastAPI) -> None:
    """Start the alert manager on application startup"""
    alert_manager = get_alert_manager()
    await alert_manager.start()

    # Set up metric-based alerts
    create_metric_alerts()

    logger.info("Alert manager started and integrated")


async def stop_alert_manager(app: FastAPI) -> None:
    """Stop the alert manager on application shutdown"""
    alert_manager = get_alert_manager()
    await alert_manager.stop()

    logger.info("Alert manager stopped")
