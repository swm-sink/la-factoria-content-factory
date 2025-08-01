"""
Alert Templates and Formatting

Provides customizable templates for different notification channels.
"""

from string import Template
from typing import Any, Optional

from .models import Alert


class AlertTemplate:
    """Base alert template"""

    def __init__(self, name: str, template_str: str):
        self.name = name
        self.template = Template(template_str)

    def render(self, alert: Alert, context: Optional[dict[str, Any]] = None) -> str:
        """Render template with alert data"""
        # Build template context
        template_context = {
            "alert_name": alert.name,
            "severity": alert.severity.upper(),
            "status": alert.status.value.upper(),
            "summary": alert.summary,
            "description": alert.description,
            "service": alert.service,
            "environment": alert.environment,
            "starts_at": alert.starts_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "duration": self._format_duration(alert.duration),
            "value": alert.value,
            "threshold": alert.threshold,
            "runbook_url": alert.runbook_url or "N/A",
            "dashboard_url": alert.dashboard_url or "N/A",
        }

        # Add labels with prefix
        for key, value in alert.labels.items():
            template_context[f"label_{key}"] = value

        # Add annotations with prefix
        for key, value in alert.annotations.items():
            template_context[f"annotation_{key}"] = value

        # Add custom context
        if context:
            template_context.update(context)

        return self.template.safe_substitute(template_context)

    def _format_duration(self, seconds: Optional[float]) -> str:
        """Format duration in human-readable format"""
        if seconds is None:
            return "N/A"

        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds / 60)}m"
        elif seconds < 86400:
            return f"{int(seconds / 3600)}h {int((seconds % 3600) / 60)}m"
        else:
            return f"{int(seconds / 86400)}d {int((seconds % 86400) / 3600)}h"


class AlertFormatter:
    """Alert formatter with channel-specific templates"""

    def __init__(self):
        self.templates: dict[str, dict[str, AlertTemplate]] = {
            "slack": {},
            "pagerduty": {},
            "email": {},
            "default": {},
        }
        self._load_default_templates()

    def add_template(self, channel: str, severity: str, template: AlertTemplate) -> None:
        """Add a template for a specific channel and severity"""
        if channel not in self.templates:
            self.templates[channel] = {}
        self.templates[channel][severity] = template

    def format_alert(self, alert: Alert, channel: str, context: Optional[dict[str, Any]] = None) -> str:
        """Format alert for a specific channel"""
        # Try channel-specific template
        if channel in self.templates and alert.severity in self.templates[channel]:
            template = self.templates[channel][alert.severity]
        # Fall back to default template
        elif alert.severity in self.templates["default"]:
            template = self.templates["default"][alert.severity]
        else:
            # Use generic template
            template = self._get_generic_template()

        return template.render(alert, context)

    def _load_default_templates(self) -> None:
        """Load default templates"""
        # Slack templates
        self.templates["slack"]["critical"] = AlertTemplate(
            "slack_critical",
            """*🚨 CRITICAL ALERT: $alert_name*

*Summary:* $summary
*Description:* $description

*Service:* $service | *Environment:* $environment
*Duration:* $duration | *Status:* $status

*Value:* $value | *Threshold:* $threshold

*Actions:*
• 📖 <$runbook_url|View Runbook>
• 📊 <$dashboard_url|View Dashboard>

*Response Required:* Immediate action needed!""",
        )

        self.templates["slack"]["high"] = AlertTemplate(
            "slack_high",
            """*⚠️ HIGH PRIORITY: $alert_name*

*Summary:* $summary

*Service:* $service | *Duration:* $duration

*Actions:* <$runbook_url|Runbook> | <$dashboard_url|Dashboard>""",
        )

        self.templates["slack"]["warning"] = AlertTemplate(
            "slack_warning",
            """*⚡ Warning: $alert_name*

$summary

Service: $service | Duration: $duration
<$runbook_url|View Runbook>""",
        )

        # Email templates
        self.templates["email"]["critical"] = AlertTemplate(
            "email_critical",
            """CRITICAL ALERT: $alert_name

Summary: $summary
Description: $description

Service: $service
Environment: $environment
Started: $starts_at
Duration: $duration
Status: $status

Current Value: $value
Threshold: $threshold

IMMEDIATE ACTION REQUIRED

Runbook: $runbook_url
Dashboard: $dashboard_url

This is an automated alert from La Factoria monitoring system.""",
        )

        self.templates["email"]["high"] = AlertTemplate(
            "email_high",
            """High Priority Alert: $alert_name

$summary

Service: $service
Environment: $environment
Duration: $duration

Please investigate within 15 minutes.

Runbook: $runbook_url
Dashboard: $dashboard_url""",
        )

        # PagerDuty templates (shorter for SMS)
        self.templates["pagerduty"]["critical"] = AlertTemplate(
            "pagerduty_critical",
            """$alert_name: $summary
Svc: $service | Val: $value | Threshold: $threshold
$runbook_url""",
        )

        # Default templates
        self.templates["default"]["critical"] = AlertTemplate(
            "default_critical",
            """[$severity] $alert_name

$summary

Service: $service
Environment: $environment
Duration: $duration
Value: $value (threshold: $threshold)

Runbook: $runbook_url
Dashboard: $dashboard_url""",
        )

        self.templates["default"]["high"] = self.templates["default"]["critical"]
        self.templates["default"]["warning"] = self.templates["default"]["critical"]
        self.templates["default"]["info"] = self.templates["default"]["critical"]

    def _get_generic_template(self) -> AlertTemplate:
        """Get generic template for any alert"""
        return AlertTemplate(
            "generic",
            """Alert: $alert_name
Severity: $severity
Summary: $summary
Service: $service
Duration: $duration""",
        )


def create_custom_templates() -> dict[str, AlertTemplate]:
    """Create custom templates for specific alert types"""
    return {
        "sla_violation": AlertTemplate(
            "sla_violation",
            """🚨 *SLA VIOLATION ALERT*

*Service:* $service
*SLA Target:* $annotation_sla_target
*Current Value:* $value
*Duration:* $duration

*Impact:* $annotation_impact
*Customer Impact:* $annotation_customer_impact

*Immediate Actions:*
1. Check service health: $dashboard_url
2. Review recent deployments
3. Check dependency status
4. Follow runbook: $runbook_url

*Escalation:* This alert will escalate to on-call engineer in 5 minutes if not acknowledged.""",
        ),
        "security_incident": AlertTemplate(
            "security_incident",
            """🔴 *SECURITY INCIDENT DETECTED*

*Type:* $annotation_incident_type
*Severity:* $severity
*Source:* $label_source_ip
*Target:* $service

*Description:* $description

*Immediate Actions:*
1. DO NOT ACKNOWLEDGE - Follow security protocol
2. Contact security team immediately
3. Preserve evidence - do not modify logs
4. Follow incident response: $runbook_url

*Security Hotline:* +1-XXX-XXX-XXXX""",
        ),
        "deployment_failure": AlertTemplate(
            "deployment_failure",
            """⚠️ *DEPLOYMENT FAILURE*

*Service:* $service
*Version:* $label_version
*Environment:* $environment

*Error:* $description

*Rollback Instructions:*
1. Check deployment status: $dashboard_url
2. Initiate rollback if needed
3. Verify service health after rollback
4. Follow runbook: $runbook_url

*Deployment ID:* $label_deployment_id""",
        ),
    }
