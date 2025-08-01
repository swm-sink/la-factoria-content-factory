"""
Alert Configuration

Provides configuration loading and validation for the alerting system.
"""

import os
from typing import Any, Optional

from app.core.config.settings import get_settings

from .manager import AlertManager
from .notifications import EmailNotifier, PagerDutyNotifier, SlackNotifier
from .routing import AlertRouter, Route, RoutingRule, create_default_escalation_policy, create_default_routing_rules
from .templates import AlertFormatter, create_custom_templates


def load_alert_config() -> dict[str, Any]:
    """Load alert configuration from environment"""
    settings = get_settings()

    return {
        # Slack configuration
        "slack": {
            "enabled": bool(os.getenv("SLACK_WEBHOOK_URL")),
            "webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
            "channels": {
                "critical": os.getenv("SLACK_CHANNEL_CRITICAL", "#alerts-critical"),
                "warnings": os.getenv("SLACK_CHANNEL_WARNINGS", "#alerts"),
                "database": os.getenv("SLACK_CHANNEL_DATABASE", "#database-alerts"),
                "security": os.getenv("SLACK_CHANNEL_SECURITY", "#security-alerts"),
                "dev": os.getenv("SLACK_CHANNEL_DEV", "#dev-alerts"),
            },
        },
        # PagerDuty configuration
        "pagerduty": {
            "enabled": bool(os.getenv("PAGERDUTY_INTEGRATION_KEY")),
            "integration_key": os.getenv("PAGERDUTY_INTEGRATION_KEY", ""),
            "api_key": os.getenv("PAGERDUTY_API_KEY", ""),
            "services": {
                "default": os.getenv("PAGERDUTY_SERVICE_DEFAULT", ""),
                "critical": os.getenv("PAGERDUTY_SERVICE_CRITICAL", ""),
                "executive": os.getenv("PAGERDUTY_SERVICE_EXECUTIVE", ""),
            },
        },
        # Email configuration
        "email": {
            "enabled": bool(os.getenv("SMTP_HOST")),
            "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "smtp_user": os.getenv("SMTP_USER", ""),
            "smtp_password": os.getenv("SMTP_PASSWORD", ""),
            "from_addr": os.getenv("ALERT_EMAIL_FROM", "alerts@lafactoria.ai"),
            "recipients": {
                "default": os.getenv("ALERT_EMAIL_DEFAULT", "team@lafactoria.ai").split(","),
                "database": os.getenv("ALERT_EMAIL_DATABASE", "database@lafactoria.ai").split(","),
                "security": os.getenv("ALERT_EMAIL_SECURITY", "security@lafactoria.ai").split(","),
                "manager": os.getenv("ALERT_EMAIL_MANAGER", "manager@lafactoria.ai").split(","),
            },
        },
        # Alert manager configuration
        "manager": {
            "group_interval": int(os.getenv("ALERT_GROUP_INTERVAL", "300")),
            "group_wait": int(os.getenv("ALERT_GROUP_WAIT", "10")),
        },
        # Feature flags
        "features": {
            "enable_escalation": os.getenv("ALERT_ENABLE_ESCALATION", "true").lower() == "true",
            "enable_suppression": os.getenv("ALERT_ENABLE_SUPPRESSION", "true").lower() == "true",
            "enable_grouping": os.getenv("ALERT_ENABLE_GROUPING", "true").lower() == "true",
        },
    }


def create_notification_channels(config: dict[str, Any]) -> dict[str, Any]:
    """Create notification channel instances"""
    channels = {}

    # Slack channels
    if config["slack"]["enabled"]:
        base_url = config["slack"]["webhook_url"]

        for name, channel in config["slack"]["channels"].items():
            channels[f"slack-{name}"] = SlackNotifier(base_url, channel)

    # PagerDuty channels
    if config["pagerduty"]["enabled"]:
        for name, service_key in config["pagerduty"]["services"].items():
            if service_key:
                channels[f"pagerduty-{name}"] = PagerDutyNotifier(
                    service_key,
                    config["pagerduty"]["api_key"],
                )

    # Email channels
    if config["email"]["enabled"]:
        email_config = config["email"]

        for name, recipients in email_config["recipients"].items():
            if recipients and recipients[0]:  # Check if not empty
                channels[f"email-{name}"] = EmailNotifier(
                    smtp_host=email_config["smtp_host"],
                    smtp_port=email_config["smtp_port"],
                    smtp_user=email_config["smtp_user"],
                    smtp_password=email_config["smtp_password"],
                    from_addr=email_config["from_addr"],
                    to_addrs=recipients,
                )

    return channels


def create_routes(channels: dict[str, Any]) -> list[Route]:
    """Create routing configurations"""
    routes = []

    # Critical alerts route
    critical_route = Route(
        name="critical",
        rules=[
            RoutingRule(
                name="critical_all",
                match_conditions={"severity": "critical"},
                channels=["pagerduty-default", "slack-critical", "email-default"],
                continue_routing=True,
            ),
            RoutingRule(
                name="critical_security",
                match_conditions={"severity": "critical", "label:security": "true"},
                channels=["pagerduty-critical", "slack-security", "email-security"],
                continue_routing=False,
            ),
        ],
        channels=channels,
        escalation_policy=create_default_escalation_policy(),
    )
    routes.append(critical_route)

    # High priority route
    high_route = Route(
        name="high",
        rules=[
            RoutingRule(
                name="high_all",
                match_conditions={"severity": "high"},
                channels=["slack-warnings", "email-default"],
                continue_routing=True,
                suppress_duration=300,
            ),
        ],
        channels=channels,
    )
    routes.append(high_route)

    # Service-specific routes
    database_route = Route(
        name="database",
        rules=[
            RoutingRule(
                name="database_all",
                match_conditions={"service": "database"},
                channels=["slack-database", "email-database"],
                suppress_duration=600,
            ),
        ],
        channels=channels,
    )
    routes.append(database_route)

    # Development environment route
    dev_route = Route(
        name="development",
        rules=[
            RoutingRule(
                name="dev_all",
                match_conditions={"environment": "development"},
                channels=["slack-dev"],
                suppress_duration=1800,
            ),
        ],
        channels=channels,
    )
    routes.append(dev_route)

    # Default route for unmatched alerts
    default_route = Route(
        name="default",
        rules=[
            RoutingRule(
                name="default_all",
                match_conditions={},  # Matches everything
                channels=["slack-warnings"],
            ),
        ],
        channels=channels,
    )

    return routes, default_route


def create_alert_manager() -> AlertManager:
    """Create and configure alert manager"""
    # Load configuration
    config = load_alert_config()

    # Create notification channels
    channels = create_notification_channels(config)

    # Create router
    router = AlertRouter()

    # Create routes
    routes, default_route = create_routes(channels)

    # Add routes to router
    for route in routes:
        router.add_route(route)

    router.set_default_route(default_route)

    # Create formatter
    formatter = AlertFormatter()

    # Add custom templates
    custom_templates = create_custom_templates()
    for name, template in custom_templates.items():
        # Add to all channels
        for channel in ["slack", "email", "pagerduty"]:
            formatter.add_template(channel, name, template)

    # Create alert manager
    manager = AlertManager(
        router=router,
        formatter=formatter,
        group_interval=config["manager"]["group_interval"],
        group_wait=config["manager"]["group_wait"],
    )

    return manager


# Singleton instance
_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """Get or create alert manager instance"""
    global _alert_manager

    if _alert_manager is None:
        _alert_manager = create_alert_manager()

    return _alert_manager
