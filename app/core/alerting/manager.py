"""
Alert Manager

Central alert management system that coordinates routing, notifications,
and escalations.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from .models import Alert, AlertGroup, AlertStatus, Notification, NotificationStatus
from .notifications import NotificationChannel
from .routing import AlertRouter, Route
from .templates import AlertFormatter

logger = logging.getLogger(__name__)


class AlertManager:
    """Central alert management system"""

    def __init__(
        self,
        router: AlertRouter,
        formatter: AlertFormatter,
        group_interval: int = 300,  # 5 minutes
        group_wait: int = 10,  # 10 seconds
    ):
        self.router = router
        self.formatter = formatter
        self.group_interval = group_interval
        self.group_wait = group_wait

        # State tracking
        self.active_alerts: dict[str, Alert] = {}
        self.alert_groups: dict[str, AlertGroup] = {}
        self.notifications: dict[str, Notification] = {}
        self.acknowledgments: dict[str, datetime] = {}

        # Background tasks
        self._tasks: list[asyncio.Task] = []
        self._running = False

    async def start(self) -> None:
        """Start the alert manager"""
        self._running = True

        # Start background tasks
        self._tasks.append(asyncio.create_task(self._group_processor()))
        self._tasks.append(asyncio.create_task(self._escalation_processor()))
        self._tasks.append(asyncio.create_task(self._cleanup_processor()))

        logger.info("Alert manager started")

    async def stop(self) -> None:
        """Stop the alert manager"""
        self._running = False

        # Cancel background tasks
        for task in self._tasks:
            task.cancel()

        await asyncio.gather(*self._tasks, return_exceptions=True)
        logger.info("Alert manager stopped")

    async def fire_alert(self, alert_data: dict[str, Any]) -> Alert:
        """Fire a new alert or update existing"""
        # Create alert object
        alert = Alert(
            id=alert_data.get("id", str(uuid.uuid4())),
            name=alert_data["name"],
            severity=alert_data.get("severity", "warning"),
            status=AlertStatus.FIRING,
            summary=alert_data["summary"],
            description=alert_data.get("description", ""),
            service=alert_data.get("service", "unknown"),
            environment=alert_data.get("environment", "production"),
            labels=alert_data.get("labels", {}),
            annotations=alert_data.get("annotations", {}),
            value=alert_data.get("value"),
            threshold=alert_data.get("threshold"),
            runbook_url=alert_data.get("runbook_url"),
            dashboard_url=alert_data.get("dashboard_url"),
        )

        # Generate fingerprint for deduplication
        alert.fingerprint = self._generate_fingerprint(alert)

        # Check if alert already exists
        existing = self.active_alerts.get(alert.fingerprint)
        if existing:
            # Update existing alert
            existing.value = alert.value
            existing.annotations.update(alert.annotations)
            logger.info(f"Updated existing alert: {alert.fingerprint}")
            return existing

        # Add new alert
        self.active_alerts[alert.fingerprint] = alert

        # Add to group
        await self._add_to_group(alert)

        logger.info(f"Fired new alert: {alert.name} ({alert.fingerprint})")
        return alert

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        alert = None

        # Find alert by ID or fingerprint
        for fingerprint, a in self.active_alerts.items():
            if a.id == alert_id or fingerprint == alert_id:
                alert = a
                break

        if not alert:
            logger.warning(f"Alert not found: {alert_id}")
            return False

        # Update alert status
        alert.status = AlertStatus.RESOLVED
        alert.ends_at = datetime.utcnow()

        # Remove from active alerts
        del self.active_alerts[alert.fingerprint]

        # Send resolution notification
        await self._send_resolution_notification(alert)

        logger.info(f"Resolved alert: {alert.name} ({alert.fingerprint})")
        return True

    async def acknowledge_alert(self, alert_id: str, acknowledger: str) -> bool:
        """Acknowledge an alert"""
        alert = None

        # Find alert
        for fingerprint, a in self.active_alerts.items():
            if a.id == alert_id or fingerprint == alert_id:
                alert = a
                break

        if not alert:
            logger.warning(f"Alert not found: {alert_id}")
            return False

        # Update status
        alert.status = AlertStatus.ACKNOWLEDGED
        self.acknowledgments[alert.fingerprint] = datetime.utcnow()

        # Update notification status
        for notification in self.notifications.values():
            if notification.alert_id == alert.id:
                notification.status = NotificationStatus.ACKNOWLEDGED
                notification.acknowledged_at = datetime.utcnow()

        logger.info(f"Alert acknowledged by {acknowledger}: {alert.name}")
        return True

    async def silence_alert(self, alert_id: str, duration: int = 3600, comment: Optional[str] = None) -> bool:
        """Silence an alert for a specified duration"""
        alert = None

        # Find alert
        for fingerprint, a in self.active_alerts.items():
            if a.id == alert_id or fingerprint == alert_id:
                alert = a
                break

        if not alert:
            logger.warning(f"Alert not found: {alert_id}")
            return False

        # Update status
        alert.status = AlertStatus.SILENCED
        alert.annotations["silence_until"] = (datetime.utcnow() + timedelta(seconds=duration)).isoformat()

        if comment:
            alert.annotations["silence_comment"] = comment

        logger.info(f"Alert silenced for {duration}s: {alert.name}")
        return True

    async def _add_to_group(self, alert: Alert) -> None:
        """Add alert to appropriate group"""
        group_key = self._get_group_key(alert)
        alert.group_key = group_key

        if group_key not in self.alert_groups:
            self.alert_groups[group_key] = AlertGroup(
                key=group_key,
                alerts=[alert],
            )
        else:
            group = self.alert_groups[group_key]
            group.alerts.append(alert)
            group.updated_at = datetime.utcnow()

    def _get_group_key(self, alert: Alert) -> str:
        """Generate group key for alert"""
        # Group by service, alert name, and severity
        parts = [
            alert.service,
            alert.name,
            alert.severity,
        ]

        # Add custom grouping labels
        for label in ["group", "cluster", "region"]:
            if label in alert.labels:
                parts.append(alert.labels[label])

        return ":".join(parts)

    def _generate_fingerprint(self, alert: Alert) -> str:
        """Generate unique fingerprint for alert deduplication"""
        # Include key identifying fields
        parts = [
            alert.name,
            alert.service,
            alert.environment,
        ]

        # Add identifying labels
        for label in ["instance", "pod", "node"]:
            if label in alert.labels:
                parts.append(alert.labels[label])

        return ":".join(parts)

    async def _group_processor(self) -> None:
        """Process alert groups and send notifications"""
        while self._running:
            try:
                now = datetime.utcnow()

                for group_key, group in list(self.alert_groups.items()):
                    # Skip if group was recently processed
                    time_since_update = (now - group.updated_at).total_seconds()
                    if time_since_update < self.group_wait:
                        continue

                    # Skip if only resolved alerts
                    if not group.is_active:
                        del self.alert_groups[group_key]
                        continue

                    # Process active alerts in group
                    active_alerts = [a for a in group.alerts if a.status == AlertStatus.FIRING]

                    for alert in active_alerts:
                        await self._route_alert(alert)

                    # Update group timestamp
                    group.updated_at = now

                # Clean up old groups
                await self._cleanup_groups()

            except Exception as e:
                logger.error(f"Error in group processor: {e}")

            await asyncio.sleep(self.group_wait)

    async def _route_alert(self, alert: Alert) -> None:
        """Route alert to appropriate channels"""
        # Skip if silenced
        if alert.status == AlertStatus.SILENCED:
            silence_until = alert.annotations.get("silence_until")
            if silence_until:
                if datetime.fromisoformat(silence_until) > datetime.utcnow():
                    return
                else:
                    # Unsilence
                    alert.status = AlertStatus.FIRING

        # Get route for alert
        route = self.router.get_route_for_alert(alert)
        if not route:
            logger.warning(f"No route found for alert: {alert.name}")
            return

        # Get channels
        channels = route.get_channels_for_alert(alert)

        # Send notifications
        for channel_name, channel in channels:
            try:
                # Format message
                message = self.formatter.format_alert(alert, channel_name)

                # Send notification
                notification = await channel.send(alert, message)

                # Track notification
                self.notifications[notification.id] = notification

                logger.info(f"Sent {channel_name} notification for alert: {alert.name}")

            except Exception as e:
                logger.error(f"Failed to send {channel_name} notification: {e}")

    async def _send_resolution_notification(self, alert: Alert) -> None:
        """Send notification when alert is resolved"""
        # Find route
        route = self.router.get_route_for_alert(alert)
        if not route:
            return

        # Get channels that should receive resolution
        channels = route.get_channels_for_alert(alert)

        for channel_name, channel in channels:
            try:
                # Format resolution message
                context = {"resolution_time": datetime.utcnow().isoformat()}
                message = self.formatter.format_alert(alert, channel_name, context)

                # Send notification
                await channel.send(alert, f"RESOLVED: {message}")

            except Exception as e:
                logger.error(f"Failed to send resolution notification: {e}")

    async def _escalation_processor(self) -> None:
        """Process escalations for unacknowledged alerts"""
        while self._running:
            try:
                now = datetime.utcnow()

                for notification in list(self.notifications.values()):
                    # Skip if not sent or already acknowledged
                    if notification.status != NotificationStatus.SENT:
                        continue

                    # Check if escalation needed
                    alert = self.active_alerts.get(self._find_alert_fingerprint(notification.alert_id))

                    if not alert or alert.status != AlertStatus.FIRING:
                        continue

                    # Get route and escalation policy
                    route = self.router.get_route_for_alert(alert)
                    if not route or not route.escalation_policy:
                        continue

                    # Check time since notification
                    time_since_sent = (now - notification.sent_at).total_seconds()

                    # Get next escalation level
                    next_level = notification.escalation_level + 1
                    level_config = route.escalation_policy.get_level(next_level)

                    if level_config and time_since_sent >= level_config["delay"]:
                        await self._escalate_notification(alert, notification, route, next_level)

            except Exception as e:
                logger.error(f"Error in escalation processor: {e}")

            await asyncio.sleep(60)  # Check every minute

    async def _escalate_notification(self, alert: Alert, notification: Notification, route: Route, level: int) -> None:
        """Escalate a notification"""
        level_config = route.escalation_policy.get_level(level)
        if not level_config:
            return

        logger.info(f"Escalating alert {alert.name} to level {level}")

        # Update notification
        notification.escalation_level = level
        notification.status = NotificationStatus.ESCALATED

        # Send to escalation channels
        for channel_name in level_config["channels"]:
            if channel_name in route.channels:
                try:
                    channel = route.channels[channel_name]
                    message = self.formatter.format_alert(alert, channel_name, {"escalation_level": level})

                    escalation_notification = await channel.send(alert, f"ESCALATION L{level}: {message}")

                    self.notifications[escalation_notification.id] = escalation_notification

                except Exception as e:
                    logger.error(f"Failed to send escalation: {e}")

    def _find_alert_fingerprint(self, alert_id: str) -> Optional[str]:
        """Find alert fingerprint by ID"""
        for fingerprint, alert in self.active_alerts.items():
            if alert.id == alert_id:
                return fingerprint
        return None

    async def _cleanup_processor(self) -> None:
        """Clean up old data"""
        while self._running:
            try:
                # Clean up router suppression cache
                self.router.cleanup_suppression_cache()

                # Clean up old notifications
                await self._cleanup_notifications()

                # Clean up old acknowledgments
                await self._cleanup_acknowledgments()

            except Exception as e:
                logger.error(f"Error in cleanup processor: {e}")

            await asyncio.sleep(3600)  # Run hourly

    async def _cleanup_groups(self) -> None:
        """Clean up inactive alert groups"""
        now = datetime.utcnow()
        to_remove = []

        for group_key, group in self.alert_groups.items():
            # Remove groups with no active alerts that are older than group_interval
            if not group.is_active:
                age = (now - group.updated_at).total_seconds()
                if age > self.group_interval:
                    to_remove.append(group_key)

        for key in to_remove:
            del self.alert_groups[key]

    async def _cleanup_notifications(self) -> None:
        """Clean up old notifications"""
        cutoff = datetime.utcnow() - timedelta(days=7)
        to_remove = []

        for notif_id, notification in self.notifications.items():
            if notification.created_at < cutoff:
                to_remove.append(notif_id)

        for notif_id in to_remove:
            del self.notifications[notif_id]

    async def _cleanup_acknowledgments(self) -> None:
        """Clean up old acknowledgments"""
        cutoff = datetime.utcnow() - timedelta(days=1)
        to_remove = []

        for fingerprint, ack_time in self.acknowledgments.items():
            if ack_time < cutoff:
                to_remove.append(fingerprint)

        for fingerprint in to_remove:
            del self.acknowledgments[fingerprint]
