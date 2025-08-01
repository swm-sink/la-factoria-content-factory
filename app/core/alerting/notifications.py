"""
Notification Channel Implementations

Provides integrations with various notification channels including
Slack, PagerDuty, and Email.
"""

import json
import logging
import smtplib
from abc import ABC, abstractmethod
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Optional

import httpx

from .models import Alert, Notification, NotificationStatus

logger = logging.getLogger(__name__)


class NotificationChannel(ABC):
    """Base notification channel interface"""

    @abstractmethod
    async def send(self, alert: Alert, template: str) -> Notification:
        """Send notification for an alert"""
        pass

    @abstractmethod
    async def acknowledge(self, notification_id: str) -> bool:
        """Acknowledge a notification"""
        pass


class SlackNotifier(NotificationChannel):
    """Slack notification channel"""

    def __init__(self, webhook_url: str, channel: Optional[str] = None):
        self.webhook_url = webhook_url
        self.channel = channel
        self.client = httpx.AsyncClient(timeout=30.0)

    async def send(self, alert: Alert, template: str) -> Notification:
        """Send Slack notification"""
        notification = Notification(
            id=f"slack-{alert.id}-{datetime.utcnow().timestamp()}",
            alert_id=alert.id,
            channel="slack",
            recipient=self.channel or "default",
            status=NotificationStatus.PENDING,
            title=alert.summary,
            message=template,
        )

        try:
            # Format Slack message with blocks
            blocks = self._format_blocks(alert, template)

            payload = {
                "blocks": blocks,
                "text": alert.summary,  # Fallback text
            }

            if self.channel:
                payload["channel"] = self.channel

            response = await self.client.post(
                self.webhook_url,
                json=payload,
            )

            if response.status_code == 200:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
                notification.response = {"status_code": response.status_code}
                logger.info(f"Slack notification sent for alert {alert.id}")
            else:
                notification.status = NotificationStatus.FAILED
                notification.error = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Failed to send Slack notification: {notification.error}")

        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.error = str(e)
            logger.error(f"Error sending Slack notification: {e}")

        return notification

    async def acknowledge(self, notification_id: str) -> bool:
        """Slack doesn't support acknowledgment via webhook"""
        return False

    def _format_blocks(self, alert: Alert, template: str) -> list[dict[str, Any]]:
        """Format Slack blocks for rich formatting"""
        severity_emoji = {
            "critical": "🚨",
            "high": "⚠️",
            "warning": "⚡",
            "info": "ℹ️",
        }

        severity_color = {
            "critical": "#D00000",
            "high": "#F77F00",
            "warning": "#FCBF49",
            "info": "#06FFD2",
        }

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{severity_emoji.get(alert.severity, '📢')} {alert.name}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": template,
                },
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"*Service:* {alert.service} | *Environment:* {alert.environment}"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Started:* <!date^{int(alert.starts_at.timestamp())}^{date_time}|{alert.starts_at.isoformat()}>",
                    },
                ],
            },
        ]

        # Add actions if URLs are available
        actions = []
        if alert.runbook_url:
            actions.append(
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📖 Runbook"},
                    "url": alert.runbook_url,
                }
            )

        if alert.dashboard_url:
            actions.append(
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📊 Dashboard"},
                    "url": alert.dashboard_url,
                }
            )

        if actions:
            blocks.append({"type": "actions", "elements": actions})

        # Add color attachment
        return [{"color": severity_color.get(alert.severity, "#808080"), "blocks": blocks}]


class PagerDutyNotifier(NotificationChannel):
    """PagerDuty notification channel"""

    def __init__(self, integration_key: str, api_key: Optional[str] = None):
        self.integration_key = integration_key
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self.events_url = "https://events.pagerduty.com/v2/enqueue"
        self.api_url = "https://api.pagerduty.com"

    async def send(self, alert: Alert, template: str) -> Notification:
        """Send PagerDuty notification"""
        notification = Notification(
            id=f"pagerduty-{alert.id}-{datetime.utcnow().timestamp()}",
            alert_id=alert.id,
            channel="pagerduty",
            recipient=self.integration_key,
            status=NotificationStatus.PENDING,
            title=alert.summary,
            message=template,
        )

        try:
            # Map severity to PagerDuty severity
            pd_severity = {
                "critical": "critical",
                "high": "error",
                "warning": "warning",
                "info": "info",
            }.get(alert.severity, "error")

            # Create PagerDuty event
            event = {
                "routing_key": self.integration_key,
                "event_action": "trigger" if alert.status.value == "firing" else "resolve",
                "dedup_key": alert.fingerprint or alert.id,
                "payload": {
                    "summary": alert.summary,
                    "severity": pd_severity,
                    "source": alert.service,
                    "component": alert.service,
                    "group": alert.group_key,
                    "class": alert.name,
                    "custom_details": {
                        "description": alert.description,
                        "environment": alert.environment,
                        "value": alert.value,
                        "threshold": alert.threshold,
                        "labels": alert.labels,
                        "annotations": alert.annotations,
                    },
                },
            }

            # Add links
            if alert.runbook_url or alert.dashboard_url:
                event["links"] = []
                if alert.runbook_url:
                    event["links"].append({"href": alert.runbook_url, "text": "Runbook"})
                if alert.dashboard_url:
                    event["links"].append({"href": alert.dashboard_url, "text": "Dashboard"})

            response = await self.client.post(
                self.events_url,
                json=event,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code in [200, 201, 202]:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
                notification.response = response.json()
                logger.info(f"PagerDuty notification sent for alert {alert.id}")
            else:
                notification.status = NotificationStatus.FAILED
                notification.error = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Failed to send PagerDuty notification: {notification.error}")

        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.error = str(e)
            logger.error(f"Error sending PagerDuty notification: {e}")

        return notification

    async def acknowledge(self, notification_id: str) -> bool:
        """Acknowledge PagerDuty incident"""
        if not self.api_key:
            logger.warning("PagerDuty API key not configured for acknowledgment")
            return False

        # This would require looking up the incident ID from the notification
        # and making an API call to acknowledge it
        # Implementation depends on your incident tracking system
        return False


class EmailNotifier(NotificationChannel):
    """Email notification channel"""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_addr: str,
        to_addrs: list[str],
        use_tls: bool = True,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_addr = from_addr
        self.to_addrs = to_addrs
        self.use_tls = use_tls

    async def send(self, alert: Alert, template: str) -> Notification:
        """Send email notification"""
        notification = Notification(
            id=f"email-{alert.id}-{datetime.utcnow().timestamp()}",
            alert_id=alert.id,
            channel="email",
            recipient=",".join(self.to_addrs),
            status=NotificationStatus.PENDING,
            title=alert.summary,
            message=template,
        )

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{alert.severity.upper()}] {alert.name}: {alert.summary}"
            msg["From"] = self.from_addr
            msg["To"] = ", ".join(self.to_addrs)

            # Create HTML content
            html_body = self._format_html(alert, template)

            # Add plain text and HTML parts
            msg.attach(MIMEText(template, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            logger.info(f"Email notification sent for alert {alert.id}")

        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.error = str(e)
            logger.error(f"Error sending email notification: {e}")

        return notification

    async def acknowledge(self, notification_id: str) -> bool:
        """Email doesn't support acknowledgment"""
        return False

    def _format_html(self, alert: Alert, template: str) -> str:
        """Format HTML email body"""
        severity_color = {
            "critical": "#D00000",
            "high": "#F77F00",
            "warning": "#FCBF49",
            "info": "#06FFD2",
        }

        color = severity_color.get(alert.severity, "#808080")

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert-box {{
                    border-left: 4px solid {color};
                    padding: 20px;
                    margin: 20px 0;
                    background-color: #f8f9fa;
                }}
                .alert-header {{
                    color: {color};
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .alert-details {{
                    margin: 10px 0;
                }}
                .alert-actions {{
                    margin-top: 20px;
                }}
                .btn {{
                    display: inline-block;
                    padding: 10px 20px;
                    margin-right: 10px;
                    text-decoration: none;
                    color: white;
                    background-color: #007bff;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="alert-box">
                <div class="alert-header">{alert.name}</div>
                <div class="alert-details">
                    <p><strong>Summary:</strong> {alert.summary}</p>
                    <p><strong>Description:</strong> {alert.description}</p>
                    <p><strong>Service:</strong> {alert.service}</p>
                    <p><strong>Environment:</strong> {alert.environment}</p>
                    <p><strong>Started:</strong> {alert.starts_at.isoformat()}</p>
                    """

        if alert.value is not None:
            html += f"<p><strong>Value:</strong> {alert.value}</p>"

        if alert.threshold is not None:
            html += f"<p><strong>Threshold:</strong> {alert.threshold}</p>"

        html += """
                </div>
                <div class="alert-actions">
        """

        if alert.runbook_url:
            html += f'<a href="{alert.runbook_url}" class="btn">View Runbook</a>'

        if alert.dashboard_url:
            html += f'<a href="{alert.dashboard_url}" class="btn">View Dashboard</a>'

        html += """
                </div>
            </div>
        </body>
        </html>
        """

        return html
