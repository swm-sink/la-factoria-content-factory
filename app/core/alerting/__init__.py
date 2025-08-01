"""
Alert Management System

This module provides a comprehensive alert management system with:
- Multiple notification channels (Slack, PagerDuty, Email)
- Advanced routing and escalation
- Alert suppression and grouping
- Rich alert formatting and templates
"""

from .manager import AlertManager
from .notifications import EmailNotifier, NotificationChannel, PagerDutyNotifier, SlackNotifier
from .routing import AlertRouter, Route, RoutingRule
from .templates import AlertFormatter, AlertTemplate

__all__ = [
    "AlertManager",
    "SlackNotifier",
    "PagerDutyNotifier",
    "EmailNotifier",
    "NotificationChannel",
    "AlertRouter",
    "Route",
    "RoutingRule",
    "AlertTemplate",
    "AlertFormatter",
]
