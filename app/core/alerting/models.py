"""
Alert Data Models

Defines the data structures used throughout the alerting system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class AlertStatus(Enum):
    """Alert status"""

    FIRING = "firing"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"
    SILENCED = "silenced"


class NotificationStatus(Enum):
    """Notification delivery status"""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    ACKNOWLEDGED = "acknowledged"
    ESCALATED = "escalated"


@dataclass
class Alert:
    """Alert data structure"""

    # Core fields
    id: str
    name: str
    severity: str
    status: AlertStatus

    # Alert details
    summary: str
    description: str
    service: str
    environment: str = "production"

    # Metadata
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)

    # Timing
    starts_at: datetime = field(default_factory=datetime.utcnow)
    ends_at: Optional[datetime] = None

    # Additional context
    value: Optional[float] = None
    threshold: Optional[float] = None
    runbook_url: Optional[str] = None
    dashboard_url: Optional[str] = None

    # Grouping and suppression
    group_key: Optional[str] = None
    fingerprint: Optional[str] = None

    @property
    def duration(self) -> Optional[float]:
        """Get alert duration in seconds"""
        if self.ends_at:
            return (self.ends_at - self.starts_at).total_seconds()
        return (datetime.utcnow() - self.starts_at).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "severity": self.severity,
            "status": self.status.value,
            "summary": self.summary,
            "description": self.description,
            "service": self.service,
            "environment": self.environment,
            "labels": self.labels,
            "annotations": self.annotations,
            "starts_at": self.starts_at.isoformat(),
            "ends_at": self.ends_at.isoformat() if self.ends_at else None,
            "value": self.value,
            "threshold": self.threshold,
            "runbook_url": self.runbook_url,
            "dashboard_url": self.dashboard_url,
            "duration": self.duration,
        }


@dataclass
class Notification:
    """Notification record"""

    id: str
    alert_id: str
    channel: str
    recipient: str
    status: NotificationStatus

    # Content
    title: str
    message: str

    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None

    # Response tracking
    response: Optional[dict[str, Any]] = None
    error: Optional[str] = None

    # Escalation
    escalation_level: int = 0
    escalated_to: Optional[str] = None


@dataclass
class AlertGroup:
    """Group of related alerts"""

    key: str
    alerts: list[Alert]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def severity(self) -> str:
        """Get highest severity in group"""
        severity_order = ["critical", "high", "warning", "info"]
        severities = [a.severity for a in self.alerts]
        for sev in severity_order:
            if sev in severities:
                return sev
        return "info"

    @property
    def is_active(self) -> bool:
        """Check if any alerts are still firing"""
        return any(a.status == AlertStatus.FIRING for a in self.alerts)


@dataclass
class EscalationPolicy:
    """Escalation policy configuration"""

    name: str
    levels: list[dict[str, Any]]  # List of escalation levels
    repeat_interval: int = 3600  # Seconds before re-escalating

    def get_level(self, level: int) -> Optional[dict[str, Any]]:
        """Get escalation level configuration"""
        if 0 <= level < len(self.levels):
            return self.levels[level]
        return None
