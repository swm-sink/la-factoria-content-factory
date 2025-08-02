"""
Error alerting middleware for automatic error detection and alert generation.
"""

import asyncio
import logging
import time
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.alerting.manager import AlertManager
from app.core.alerting.models import Alert, AlertSeverity

logger = logging.getLogger(__name__)


class ErrorAlertingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that detects errors and automatically generates alerts.
    """

    def __init__(self, app, alert_manager: AlertManager, config: Optional[Dict[str, Any]] = None):
        super().__init__(app)
        self.alert_manager = alert_manager
        self.config = config or {}

        # Configuration
        self.error_rate_threshold = self.config.get("error_rate_threshold", 0.05)  # 5%
        self.error_rate_window = self.config.get("error_rate_window", 300)  # 5 minutes
        self.critical_error_codes = self.config.get("critical_error_codes", [500, 502, 503, 504])
        self.alert_on_first_error = self.config.get("alert_on_first_error", True)

        # Error tracking
        self.error_counts: Dict[str, int] = {}
        self.request_counts: Dict[str, int] = {}
        self.last_reset_time = time.time()

    async def dispatch(self, request: Request, call_next):
        """Process request and detect errors."""
        start_time = time.time()
        response = None
        error_info = None

        try:
            # Process the request
            response = await call_next(request)

            # Track request
            await self._track_request(request, response.status_code)

            # Check for error status codes
            if response.status_code in self.critical_error_codes:
                error_info = {
                    "type": "http_error",
                    "status_code": response.status_code,
                    "path": request.url.path,
                    "method": request.method,
                    "user_agent": request.headers.get("user-agent"),
                    "ip": request.client.host if request.client else "unknown",
                }

        except Exception as exc:
            # Handle unhandled exceptions
            duration = time.time() - start_time

            error_info = {
                "type": "unhandled_exception",
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "traceback": traceback.format_exc(),
                "path": request.url.path,
                "method": request.method,
                "duration": duration,
                "user_agent": request.headers.get("user-agent"),
                "ip": request.client.host if request.client else "unknown",
            }

            # Track error
            await self._track_request(request, 500, error=True)

            # Return error response
            response = JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        # Generate alert if error detected
        if error_info:
            await self._handle_error_alert(request, error_info)

        return response

    async def _track_request(self, request: Request, status_code: int, error: bool = False):
        """Track request for error rate calculation."""
        current_time = time.time()
        window_key = f"{int(current_time // 60)}"  # 1-minute windows

        # Reset counters if window expired
        if current_time - self.last_reset_time > self.error_rate_window:
            self.error_counts.clear()
            self.request_counts.clear()
            self.last_reset_time = current_time

        # Track request
        self.request_counts[window_key] = self.request_counts.get(window_key, 0) + 1

        # Track error
        if error or status_code in self.critical_error_codes:
            self.error_counts[window_key] = self.error_counts.get(window_key, 0) + 1

    async def _handle_error_alert(self, request: Request, error_info: Dict[str, Any]):
        """Generate and fire error alert."""
        try:
            # Determine alert severity
            severity = self._determine_severity(error_info)

            # Check if we should alert on this error
            if not await self._should_alert(error_info, severity):
                return

            # Create alert
            alert = Alert(
                name=self._generate_alert_name(error_info),
                severity=severity,
                service="api",
                source="error_middleware",
                message=self._generate_alert_message(error_info),
                context={
                    "error_info": error_info,
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "error_rate": await self._calculate_error_rate(),
                    "endpoint": f"{request.method} {request.url.path}",
                    "user_context": await self._extract_user_context(request),
                },
                runbook_url=self._get_runbook_url(error_info),
                annotations={
                    "impact": self._assess_impact(error_info),
                    "urgency": self._assess_urgency(error_info),
                    "category": error_info.get("type", "unknown"),
                    "auto_generated": "true",
                },
            )

            # Fire alert asynchronously
            asyncio.create_task(self.alert_manager.fire_alert(alert))

            logger.warning(
                f"Error alert fired: {alert.name}",
                extra={
                    "alert_id": alert.id,
                    "severity": severity.value,
                    "error_type": error_info.get("type"),
                    "endpoint": f"{request.method} {request.url.path}",
                },
            )

        except Exception as exc:
            logger.error(f"Failed to generate error alert: {exc}", exc_info=True)

    def _determine_severity(self, error_info: Dict[str, Any]) -> AlertSeverity:
        """Determine alert severity based on error type."""
        error_type = error_info.get("type")
        status_code = error_info.get("status_code")

        # Critical: System failures, 5xx errors
        if error_type == "unhandled_exception":
            return AlertSeverity.CRITICAL

        if status_code in [500, 502, 503]:
            return AlertSeverity.CRITICAL

        # High: Client errors that might indicate issues
        if status_code in [504]:
            return AlertSeverity.HIGH

        # Medium: Other errors
        return AlertSeverity.MEDIUM

    async def _should_alert(self, error_info: Dict[str, Any], severity: AlertSeverity) -> bool:
        """Determine if we should fire an alert for this error."""
        # Always alert on critical errors
        if severity == AlertSeverity.CRITICAL and self.alert_on_first_error:
            return True

        # Check error rate threshold
        error_rate = await self._calculate_error_rate()
        if error_rate > self.error_rate_threshold:
            return True

        # Alert on specific error patterns
        if error_info.get("type") == "unhandled_exception":
            exception_type = error_info.get("exception_type", "")
            # Always alert on database/external service errors
            if any(
                keyword in exception_type.lower()
                for keyword in ["connection", "timeout", "database", "redis", "firestore"]
            ):
                return True

        return False

    async def _calculate_error_rate(self) -> float:
        """Calculate current error rate."""
        total_errors = sum(self.error_counts.values())
        total_requests = sum(self.request_counts.values())

        if total_requests == 0:
            return 0.0

        return total_errors / total_requests

    def _generate_alert_name(self, error_info: Dict[str, Any]) -> str:
        """Generate alert name based on error type."""
        error_type = error_info.get("type", "unknown")

        if error_type == "unhandled_exception":
            exception_type = error_info.get("exception_type", "Unknown")
            return f"UnhandledException_{exception_type}"

        if error_type == "http_error":
            status_code = error_info.get("status_code", "XXX")
            path = error_info.get("path", "/unknown").replace("/", "_")
            return f"HTTPError_{status_code}_{path}"

        return f"ApplicationError_{error_type}"

    def _generate_alert_message(self, error_info: Dict[str, Any]) -> str:
        """Generate human-readable alert message."""
        error_type = error_info.get("type", "unknown")

        if error_type == "unhandled_exception":
            exception_type = error_info.get("exception_type", "Unknown")
            exception_message = error_info.get("exception_message", "No message")
            path = error_info.get("path", "/unknown")
            return f"Unhandled {exception_type} on {path}: {exception_message}"

        if error_type == "http_error":
            status_code = error_info.get("status_code", "XXX")
            path = error_info.get("path", "/unknown")
            method = error_info.get("method", "UNKNOWN")
            return f"HTTP {status_code} error on {method} {path}"

        return f"Application error detected: {error_type}"

    def _get_runbook_url(self, error_info: Dict[str, Any]) -> str:
        """Get relevant runbook URL for error type."""
        error_type = error_info.get("type", "unknown")
        status_code = error_info.get("status_code")

        base_url = "https://github.com/lafactoria/runbooks/blob/main"

        if error_type == "unhandled_exception":
            return f"{base_url}/incident-response/api-down.md"

        if status_code in [500, 502, 503]:
            return f"{base_url}/incident-response/high-error-rate.md"

        if status_code == 504:
            return f"{base_url}/performance/slow-response.md"

        return f"{base_url}/incident-response/api-down.md"

    def _assess_impact(self, error_info: Dict[str, Any]) -> str:
        """Assess the impact of the error."""
        error_type = error_info.get("type", "unknown")
        status_code = error_info.get("status_code")

        if error_type == "unhandled_exception":
            return "High - Service may be degraded or unavailable"

        if status_code in [500, 502, 503]:
            return "High - User requests are failing"

        if status_code == 504:
            return "Medium - Requests are timing out"

        return "Low - Isolated error"

    def _assess_urgency(self, error_info: Dict[str, Any]) -> str:
        """Assess the urgency of addressing the error."""
        error_type = error_info.get("type", "unknown")
        status_code = error_info.get("status_code")

        if error_type == "unhandled_exception":
            exception_type = error_info.get("exception_type", "")
            if any(keyword in exception_type.lower() for keyword in ["connection", "database", "redis", "firestore"]):
                return "Immediate - Infrastructure component failure"
            return "High - Application logic failure"

        if status_code in [500, 502, 503]:
            return "High - Service availability impacted"

        return "Medium - Monitor for patterns"

    async def _extract_user_context(self, request: Request) -> Dict[str, Any]:
        """Extract user context for alert enrichment."""
        context = {
            "ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "path": request.url.path,
            "method": request.method,
            "query_params": str(request.query_params) if request.query_params else None,
        }

        # Extract user ID if available in request state
        if hasattr(request.state, "user_id"):
            context["user_id"] = request.state.user_id

        # Extract API key info if available
        if hasattr(request.state, "api_key"):
            context["api_key"] = request.state.api_key

        return context


class CriticalErrorDetector:
    """
    Detects critical error patterns and generates immediate alerts.
    """

    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager

    async def detect_database_failure(self, exception: Exception, context: Dict[str, Any]):
        """Detect database connection failures."""
        exception_str = str(exception).lower()
        if any(
            keyword in exception_str for keyword in ["connection refused", "connection timeout", "database is locked"]
        ):

            alert = Alert(
                name="DatabaseConnectionFailure",
                severity=AlertSeverity.CRITICAL,
                service="database",
                source="error_detector",
                message=f"Database connection failure: {str(exception)}",
                context=context,
                runbook_url="https://github.com/lafactoria/runbooks/blob/main/database/connection-issues.md",
                annotations={
                    "impact": "Critical - Database unavailable",
                    "urgency": "Immediate - Service down",
                    "category": "infrastructure",
                    "auto_generated": "true",
                },
            )

            await self.alert_manager.fire_alert(alert)

    async def detect_external_service_failure(self, service: str, exception: Exception, context: Dict[str, Any]):
        """Detect external service failures."""
        alert = Alert(
            name=f"ExternalServiceFailure_{service}",
            severity=AlertSeverity.HIGH,
            service="external-api",
            source="error_detector",
            message=f"External service {service} failure: {str(exception)}",
            context={**context, "failed_service": service},
            runbook_url="https://github.com/lafactoria/runbooks/blob/main/api/external-service-issues.md",
            annotations={
                "impact": "High - Feature degradation",
                "urgency": "High - Monitor and escalate",
                "category": "dependency",
                "auto_generated": "true",
            },
        )

        await self.alert_manager.fire_alert(alert)
