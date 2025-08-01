"""
Tests for the Alert Management System
"""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.core.alerting.manager import AlertManager
from app.core.alerting.models import Alert, AlertGroup, AlertStatus, EscalationPolicy, Notification, NotificationStatus
from app.core.alerting.notifications import EmailNotifier, PagerDutyNotifier, SlackNotifier
from app.core.alerting.routing import AlertRouter, Route, RoutingRule
from app.core.alerting.templates import AlertFormatter, AlertTemplate


class TestAlertModels:
    """Test alert data models"""

    def test_alert_creation(self):
        """Test creating an alert"""
        alert = Alert(
            id="test-123",
            name="TestAlert",
            severity="critical",
            status=AlertStatus.FIRING,
            summary="Test summary",
            description="Test description",
            service="test-service",
        )

        assert alert.id == "test-123"
        assert alert.severity == "critical"
        assert alert.status == AlertStatus.FIRING
        assert alert.duration is not None

    def test_alert_to_dict(self):
        """Test converting alert to dictionary"""
        alert = Alert(
            id="test-123",
            name="TestAlert",
            severity="critical",
            status=AlertStatus.FIRING,
            summary="Test summary",
            description="Test description",
            service="test-service",
            value=95.5,
            threshold=90.0,
        )

        data = alert.to_dict()
        assert data["id"] == "test-123"
        assert data["severity"] == "critical"
        assert data["status"] == "firing"
        assert data["value"] == 95.5
        assert data["threshold"] == 90.0

    def test_alert_group(self):
        """Test alert grouping"""
        alerts = [
            Alert(
                id=f"test-{i}",
                name="TestAlert",
                severity=severity,
                status=AlertStatus.FIRING,
                summary=f"Alert {i}",
                description="",
                service="test",
            )
            for i, severity in enumerate(["warning", "critical", "info"])
        ]

        group = AlertGroup(key="test-group", alerts=alerts)

        assert group.severity == "critical"  # Highest severity
        assert group.is_active is True

        # Resolve all alerts
        for alert in alerts:
            alert.status = AlertStatus.RESOLVED

        assert group.is_active is False


class TestAlertRouting:
    """Test alert routing"""

    def test_routing_rule_matching(self):
        """Test routing rule matching"""
        rule = RoutingRule(
            name="test-rule",
            match_conditions={
                "severity": "critical",
                "service": "api",
                "label:team": "backend",
            },
            channels=["slack", "pagerduty"],
        )

        # Matching alert
        alert = Alert(
            id="test-1",
            name="TestAlert",
            severity="critical",
            status=AlertStatus.FIRING,
            summary="Test",
            description="Test",
            service="api",
            labels={"team": "backend"},
        )

        assert rule.matches(alert) is True

        # Non-matching alert (wrong severity)
        alert.severity = "warning"
        assert rule.matches(alert) is False

        # Non-matching alert (missing label)
        alert.severity = "critical"
        alert.labels = {}
        assert rule.matches(alert) is False

    def test_routing_rule_regex(self):
        """Test routing rule with regex matching"""
        rule = RoutingRule(
            name="test-rule",
            match_conditions={
                "service": "api.*",  # Regex pattern
                "annotation:description": ".*database.*",
            },
            channels=["database-team"],
        )

        alert = Alert(
            id="test-1",
            name="TestAlert",
            severity="warning",
            status=AlertStatus.FIRING,
            summary="Test",
            description="Test",
            service="api-v2",
            annotations={"description": "Database connection failed"},
        )

        assert rule.matches(alert) is True

    def test_alert_router(self):
        """Test alert router"""
        router = AlertRouter()

        # Create mock channels
        channels = {
            "slack": Mock(),
            "pagerduty": Mock(),
        }

        # Create route
        route = Route(
            name="critical",
            rules=[
                RoutingRule(
                    name="critical-all",
                    match_conditions={"severity": "critical"},
                    channels=["slack", "pagerduty"],
                ),
            ],
            channels=channels,
        )

        router.add_route(route)

        # Test routing
        alert = Alert(
            id="test-1",
            name="TestAlert",
            severity="critical",
            status=AlertStatus.FIRING,
            summary="Test",
            description="Test",
            service="api",
        )

        found_route = router.get_route_for_alert(alert)
        assert found_route == route

        # Test non-matching alert
        alert.severity = "info"
        found_route = router.get_route_for_alert(alert)
        assert found_route is None

    def test_suppression(self):
        """Test alert suppression"""
        router = AlertRouter()

        rule = RoutingRule(
            name="suppress-rule",
            match_conditions={"service": "api"},
            channels=["slack"],
            suppress_duration=60,  # 1 minute
        )

        route = Route(
            name="test",
            rules=[rule],
            channels={"slack": Mock()},
        )

        router.add_route(route)

        alert = Alert(
            id="test-1",
            name="TestAlert",
            severity="warning",
            status=AlertStatus.FIRING,
            summary="Test",
            description="Test",
            service="api",
        )

        # First alert should route
        found_route = router.get_route_for_alert(alert)
        assert found_route is not None

        # Same alert should be suppressed
        found_route = router.get_route_for_alert(alert)
        assert found_route is None


class TestAlertTemplates:
    """Test alert templates"""

    def test_alert_template_rendering(self):
        """Test rendering alert templates"""
        template = AlertTemplate("test", "Alert: $alert_name\nSeverity: $severity\nService: $service")

        alert = Alert(
            id="test-1",
            name="TestAlert",
            severity="critical",
            status=AlertStatus.FIRING,
            summary="Test",
            description="Test",
            service="api",
        )

        result = template.render(alert)
        assert "Alert: TestAlert" in result
        assert "Severity: CRITICAL" in result
        assert "Service: api" in result

    def test_alert_formatter(self):
        """Test alert formatter with channel-specific templates"""
        formatter = AlertFormatter()

        # Add custom template
        custom_template = AlertTemplate("custom", "CUSTOM: $alert_name ($severity)")
        formatter.add_template("slack", "critical", custom_template)

        alert = Alert(
            id="test-1",
            name="TestAlert",
            severity="critical",
            status=AlertStatus.FIRING,
            summary="Test",
            description="Test",
            service="api",
        )

        # Should use custom template
        result = formatter.format_alert(alert, "slack")
        assert result.startswith("CUSTOM:")

        # Should use default template for other channels
        result = formatter.format_alert(alert, "email")
        assert not result.startswith("CUSTOM:")


class TestNotificationChannels:
    """Test notification channels"""

    @pytest.mark.asyncio
    async def test_slack_notifier(self):
        """Test Slack notification channel"""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            notifier = SlackNotifier(webhook_url="https://hooks.slack.com/test", channel="#alerts")

            alert = Alert(
                id="test-1",
                name="TestAlert",
                severity="critical",
                status=AlertStatus.FIRING,
                summary="Test alert",
                description="Test description",
                service="api",
            )

            notification = await notifier.send(alert, "Test message")

            assert notification.status == NotificationStatus.SENT
            assert notification.channel == "slack"
            assert notification.recipient == "#alerts"

            # Verify Slack API was called
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://hooks.slack.com/test"

    @pytest.mark.asyncio
    async def test_pagerduty_notifier(self):
        """Test PagerDuty notification channel"""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 202
            mock_response.json.return_value = {"status": "success"}
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            notifier = PagerDutyNotifier(integration_key="test-key-1234567890abcdef12345678")

            alert = Alert(
                id="test-1",
                name="TestAlert",
                severity="critical",
                status=AlertStatus.FIRING,
                summary="Test alert",
                description="Test description",
                service="api",
                fingerprint="test-fingerprint",
            )

            notification = await notifier.send(alert, "Test message")

            assert notification.status == NotificationStatus.SENT
            assert notification.channel == "pagerduty"

            # Verify PagerDuty API was called
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert "events.pagerduty.com" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_email_notifier(self):
        """Test email notification channel"""
        with patch("smtplib.SMTP") as mock_smtp_class:
            mock_smtp = Mock()
            mock_smtp_class.return_value.__enter__.return_value = mock_smtp

            notifier = EmailNotifier(
                smtp_host="smtp.test.com",
                smtp_port=587,
                smtp_user="test@test.com",
                smtp_password="password",
                from_addr="alerts@test.com",
                to_addrs=["team@test.com"],
            )

            alert = Alert(
                id="test-1",
                name="TestAlert",
                severity="critical",
                status=AlertStatus.FIRING,
                summary="Test alert",
                description="Test description",
                service="api",
            )

            notification = await notifier.send(alert, "Test message")

            assert notification.status == NotificationStatus.SENT
            assert notification.channel == "email"
            assert notification.recipient == "team@test.com"

            # Verify SMTP was used
            mock_smtp.send_message.assert_called_once()


class TestAlertManager:
    """Test alert manager"""

    @pytest.mark.asyncio
    async def test_fire_alert(self):
        """Test firing an alert"""
        router = AlertRouter()
        formatter = AlertFormatter()
        manager = AlertManager(router, formatter)

        alert_data = {
            "name": "TestAlert",
            "severity": "critical",
            "summary": "Test alert",
            "description": "Test description",
            "service": "api",
        }

        alert = await manager.fire_alert(alert_data)

        assert alert.id is not None
        assert alert.name == "TestAlert"
        assert alert.status == AlertStatus.FIRING
        assert alert.fingerprint is not None
        assert alert.id in manager.active_alerts.values()

    @pytest.mark.asyncio
    async def test_alert_deduplication(self):
        """Test alert deduplication"""
        router = AlertRouter()
        formatter = AlertFormatter()
        manager = AlertManager(router, formatter)

        alert_data = {
            "name": "TestAlert",
            "severity": "critical",
            "summary": "Test alert",
            "description": "Test description",
            "service": "api",
        }

        # Fire same alert twice
        alert1 = await manager.fire_alert(alert_data)
        alert2 = await manager.fire_alert(alert_data)

        # Should be the same alert
        assert alert1.fingerprint == alert2.fingerprint
        assert len(manager.active_alerts) == 1

    @pytest.mark.asyncio
    async def test_resolve_alert(self):
        """Test resolving an alert"""
        router = AlertRouter()
        formatter = AlertFormatter()
        manager = AlertManager(router, formatter)

        # Fire alert
        alert_data = {
            "name": "TestAlert",
            "severity": "critical",
            "summary": "Test alert",
            "description": "Test description",
            "service": "api",
        }

        alert = await manager.fire_alert(alert_data)
        alert_id = alert.id

        # Resolve alert
        success = await manager.resolve_alert(alert_id)

        assert success is True
        assert alert.status == AlertStatus.RESOLVED
        assert alert.ends_at is not None
        assert len(manager.active_alerts) == 0

    @pytest.mark.asyncio
    async def test_acknowledge_alert(self):
        """Test acknowledging an alert"""
        router = AlertRouter()
        formatter = AlertFormatter()
        manager = AlertManager(router, formatter)

        # Fire alert
        alert_data = {
            "name": "TestAlert",
            "severity": "critical",
            "summary": "Test alert",
            "description": "Test description",
            "service": "api",
        }

        alert = await manager.fire_alert(alert_data)

        # Acknowledge alert
        success = await manager.acknowledge_alert(alert.id, "test-user")

        assert success is True
        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.fingerprint in manager.acknowledgments

    @pytest.mark.asyncio
    async def test_silence_alert(self):
        """Test silencing an alert"""
        router = AlertRouter()
        formatter = AlertFormatter()
        manager = AlertManager(router, formatter)

        # Fire alert
        alert_data = {
            "name": "TestAlert",
            "severity": "critical",
            "summary": "Test alert",
            "description": "Test description",
            "service": "api",
        }

        alert = await manager.fire_alert(alert_data)

        # Silence alert
        success = await manager.silence_alert(alert.id, duration=3600, comment="Testing")

        assert success is True
        assert alert.status == AlertStatus.SILENCED
        assert "silence_until" in alert.annotations
        assert alert.annotations.get("silence_comment") == "Testing"

    @pytest.mark.asyncio
    async def test_alert_grouping(self):
        """Test alert grouping"""
        router = AlertRouter()
        formatter = AlertFormatter()
        manager = AlertManager(router, formatter, group_wait=0)

        # Fire multiple alerts for same service
        alerts = []
        for i in range(3):
            alert_data = {
                "name": "TestAlert",
                "severity": "warning",
                "summary": f"Test alert {i}",
                "description": "Test description",
                "service": "api",
            }
            alert = await manager.fire_alert(alert_data)
            alerts.append(alert)

        # All alerts should be in same group
        group_keys = {alert.group_key for alert in alerts}
        assert len(group_keys) == 1

        # Check group exists
        group_key = alerts[0].group_key
        assert group_key in manager.alert_groups
        assert len(manager.alert_groups[group_key].alerts) == 3
