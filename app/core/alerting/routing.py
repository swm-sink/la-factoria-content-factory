"""
Alert Routing and Escalation

Provides sophisticated routing rules and escalation policies for alerts.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

from .models import Alert, EscalationPolicy
from .notifications import NotificationChannel


@dataclass
class RoutingRule:
    """Alert routing rule"""

    name: str
    match_conditions: dict[str, Any]  # Conditions to match
    channels: list[str]  # Notification channels to use
    continue_routing: bool = False  # Continue evaluating other rules
    suppress_duration: Optional[int] = None  # Seconds to suppress similar alerts

    def matches(self, alert: Alert) -> bool:
        """Check if alert matches this rule"""
        for field, pattern in self.match_conditions.items():
            value = None

            # Get field value from alert
            if field in ["severity", "status", "service", "environment", "name"]:
                value = getattr(alert, field, None)
            elif field.startswith("label:"):
                label_name = field[6:]
                value = alert.labels.get(label_name)
            elif field.startswith("annotation:"):
                annotation_name = field[11:]
                value = alert.annotations.get(annotation_name)

            # Check if value matches pattern
            if value is None:
                return False

            if isinstance(pattern, str):
                # Regex match
                if not re.match(pattern, str(value)):
                    return False
            elif isinstance(pattern, list):
                # Value in list
                if value not in pattern:
                    return False
            else:
                # Exact match
                if value != pattern:
                    return False

        return True


@dataclass
class Route:
    """Alert route with associated channels and policies"""

    name: str
    rules: list[RoutingRule]
    channels: dict[str, NotificationChannel]
    escalation_policy: Optional[EscalationPolicy] = None

    def get_channels_for_alert(self, alert: Alert) -> list[tuple[str, NotificationChannel]]:
        """Get notification channels for an alert"""
        channels = []

        for rule in self.rules:
            if rule.matches(alert):
                for channel_name in rule.channels:
                    if channel_name in self.channels:
                        channels.append((channel_name, self.channels[channel_name]))

                if not rule.continue_routing:
                    break

        return channels


class AlertRouter:
    """Main alert routing engine"""

    def __init__(self):
        self.routes: dict[str, Route] = {}
        self.default_route: Optional[Route] = None
        self.suppression_cache: dict[str, datetime] = {}

    def add_route(self, route: Route) -> None:
        """Add a routing configuration"""
        self.routes[route.name] = route

    def set_default_route(self, route: Route) -> None:
        """Set default route for unmatched alerts"""
        self.default_route = route

    def get_route_for_alert(self, alert: Alert) -> Optional[Route]:
        """Find the appropriate route for an alert"""
        # Check each route
        for route in self.routes.values():
            for rule in route.rules:
                if rule.matches(alert):
                    # Check suppression
                    if self._is_suppressed(alert, rule):
                        return None

                    # Update suppression cache
                    if rule.suppress_duration:
                        cache_key = self._get_suppression_key(alert, rule)
                        self.suppression_cache[cache_key] = datetime.utcnow()

                    return route

        # Use default route if no match
        return self.default_route

    def _is_suppressed(self, alert: Alert, rule: RoutingRule) -> bool:
        """Check if alert is suppressed"""
        if not rule.suppress_duration:
            return False

        cache_key = self._get_suppression_key(alert, rule)
        last_seen = self.suppression_cache.get(cache_key)

        if last_seen:
            suppress_until = last_seen + timedelta(seconds=rule.suppress_duration)
            if datetime.utcnow() < suppress_until:
                return True

        return False

    def _get_suppression_key(self, alert: Alert, rule: RoutingRule) -> str:
        """Generate suppression cache key"""
        parts = [rule.name, alert.name, alert.service]

        # Include matched fields in key
        for field in rule.match_conditions:
            if field.startswith("label:"):
                label_name = field[6:]
                parts.append(alert.labels.get(label_name, ""))

        return ":".join(parts)

    def cleanup_suppression_cache(self) -> None:
        """Remove expired suppression entries"""
        now = datetime.utcnow()
        expired_keys = []

        for key, timestamp in self.suppression_cache.items():
            # Assume maximum suppression of 24 hours
            if now - timestamp > timedelta(hours=24):
                expired_keys.append(key)

        for key in expired_keys:
            del self.suppression_cache[key]


def create_default_routing_rules() -> list[RoutingRule]:
    """Create default routing rules"""
    return [
        # Critical alerts go to PagerDuty and Slack
        RoutingRule(
            name="critical_alerts",
            match_conditions={"severity": "critical"},
            channels=["pagerduty", "slack-critical"],
            continue_routing=True,
        ),
        # High severity alerts go to Slack and email
        RoutingRule(
            name="high_alerts",
            match_conditions={"severity": "high"},
            channels=["slack-warnings", "email"],
            continue_routing=True,
        ),
        # Database alerts go to database team
        RoutingRule(
            name="database_alerts",
            match_conditions={"service": "database"},
            channels=["email-database-team", "slack-database"],
            suppress_duration=300,  # Suppress for 5 minutes
        ),
        # External API issues
        RoutingRule(
            name="external_api_alerts",
            match_conditions={"service": "external-api"},
            channels=["slack-warnings"],
            suppress_duration=600,  # Suppress for 10 minutes
        ),
        # Security incidents always alert
        RoutingRule(
            name="security_alerts",
            match_conditions={"label:security": "true"},
            channels=["pagerduty", "slack-security", "email-security"],
            continue_routing=False,
        ),
        # Development environment alerts
        RoutingRule(
            name="dev_alerts",
            match_conditions={"environment": "development"},
            channels=["slack-dev"],
            suppress_duration=1800,  # Suppress for 30 minutes
        ),
    ]


def create_default_escalation_policy() -> EscalationPolicy:
    """Create default escalation policy"""
    return EscalationPolicy(
        name="default",
        levels=[
            {
                "delay": 0,  # Immediate
                "channels": ["slack-warnings"],
            },
            {
                "delay": 300,  # 5 minutes
                "channels": ["email", "slack-critical"],
            },
            {
                "delay": 900,  # 15 minutes
                "channels": ["pagerduty", "email-manager"],
            },
            {
                "delay": 3600,  # 1 hour
                "channels": ["pagerduty-executive", "phone"],
            },
        ],
        repeat_interval=3600,  # Repeat escalation every hour
    )
