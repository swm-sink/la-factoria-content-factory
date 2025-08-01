"""
Alert Configuration with Runbook Mappings

Maps monitoring alerts to their corresponding runbooks.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class AlertSeverity(Enum):
    """Alert severity levels"""

    CRITICAL = "P1"
    HIGH = "P2"
    MEDIUM = "P3"
    LOW = "P4"


@dataclass
class AlertConfig:
    """Alert configuration with runbook mapping"""

    name: str
    description: str
    severity: AlertSeverity
    runbook_path: str
    threshold: dict[str, Any]
    duration: int  # seconds before alert fires
    cooldown: int  # seconds before alert can fire again

    @property
    def runbook_url(self) -> str:
        """Get full runbook URL"""
        return f"https://docs.lafactoria.com/{self.runbook_path}"


# Alert definitions with runbook mappings
ALERT_CONFIGS = {
    "api_down": AlertConfig(
        name="API Down",
        description="API health check failing",
        severity=AlertSeverity.CRITICAL,
        runbook_path="runbooks/incident-response/api-down.md",
        threshold={"health_check_failures": 3},
        duration=60,
        cooldown=300,
    ),
    "high_error_rate": AlertConfig(
        name="High Error Rate",
        description="5XX error rate exceeds threshold",
        severity=AlertSeverity.HIGH,
        runbook_path="runbooks/incident-response/high-error-rate.md",
        threshold={"error_rate_percent": 5},
        duration=300,
        cooldown=600,
    ),
    "slow_response": AlertConfig(
        name="Slow API Response",
        description="API response time exceeds SLO",
        severity=AlertSeverity.HIGH,
        runbook_path="runbooks/performance/slow-response.md",
        threshold={"p95_latency_ms": 1000},
        duration=300,
        cooldown=900,
    ),
    "database_connection": AlertConfig(
        name="Database Connection Issues",
        description="Database connection pool exhausted or connections failing",
        severity=AlertSeverity.CRITICAL,
        runbook_path="runbooks/database/connection-issues.md",
        threshold={"connection_failures": 10, "pool_usage_percent": 90},
        duration=120,
        cooldown=300,
    ),
    "high_memory": AlertConfig(
        name="High Memory Usage",
        description="Application memory usage exceeds threshold",
        severity=AlertSeverity.HIGH,
        runbook_path="runbooks/performance/memory-leak.md",
        threshold={"memory_usage_percent": 85},
        duration=600,
        cooldown=1800,
    ),
    "rate_limit_exceeded": AlertConfig(
        name="Rate Limit Exceeded",
        description="High rate of rate limit violations",
        severity=AlertSeverity.MEDIUM,
        runbook_path="runbooks/api/rate-limiting-issues.md",
        threshold={"rate_limit_violations_per_min": 100},
        duration=300,
        cooldown=600,
    ),
    "security_incident": AlertConfig(
        name="Security Incident Detected",
        description="Suspicious activity or security violation detected",
        severity=AlertSeverity.CRITICAL,
        runbook_path="runbooks/security/incident-response.md",
        threshold={"suspicious_requests": 50},
        duration=60,
        cooldown=0,  # No cooldown for security
    ),
    "backup_failure": AlertConfig(
        name="Database Backup Failed",
        description="Scheduled database backup failed",
        severity=AlertSeverity.HIGH,
        runbook_path="runbooks/database/backup.md#troubleshooting",
        threshold={"consecutive_failures": 1},
        duration=0,
        cooldown=3600,
    ),
    "deployment_failed": AlertConfig(
        name="Deployment Failed",
        description="Production deployment failed or health check not passing",
        severity=AlertSeverity.HIGH,
        runbook_path="runbooks/deployment/rollback.md",
        threshold={"health_check_failures_after_deploy": 3},
        duration=180,
        cooldown=0,
    ),
    "error_budget_burn": AlertConfig(
        name="Error Budget Burn Rate High",
        description="SLO error budget consuming too quickly",
        severity=AlertSeverity.HIGH,
        runbook_path="runbooks/monitoring/alert-response.md",
        threshold={"burn_rate": 5},
        duration=300,
        cooldown=1800,
    ),
}


def get_alert_config(alert_name: str) -> AlertConfig | None:
    """Get alert configuration by name"""
    return ALERT_CONFIGS.get(alert_name)


def get_runbook_for_alert(alert_name: str) -> str | None:
    """Get runbook path for a specific alert"""
    config = get_alert_config(alert_name)
    return config.runbook_path if config else None


def get_alerts_by_severity(severity: AlertSeverity) -> list[AlertConfig]:
    """Get all alerts of a specific severity"""
    return [config for config in ALERT_CONFIGS.values() if config.severity == severity]


def format_alert_message(alert_name: str, details: dict[str, Any]) -> str:
    """Format alert message with runbook link"""
    config = get_alert_config(alert_name)
    if not config:
        return f"Unknown alert: {alert_name}"

    message = f"""
🚨 **{config.name}** ({config.severity.value})

**Description**: {config.description}

**Details**: {details}

**Runbook**: {config.runbook_url}

**Response Time**: Respond within {_get_response_time(config.severity)}
"""
    return message.strip()


def _get_response_time(severity: AlertSeverity) -> str:
    """Get expected response time for severity"""
    response_times = {
        AlertSeverity.CRITICAL: "5 minutes",
        AlertSeverity.HIGH: "15 minutes",
        AlertSeverity.MEDIUM: "1 hour",
        AlertSeverity.LOW: "next business day",
    }
    return response_times.get(severity, "1 hour")
