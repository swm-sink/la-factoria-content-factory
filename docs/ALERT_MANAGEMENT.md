# Alert Management System

## Overview

La Factoria's alert management system provides comprehensive monitoring and notification capabilities with support for multiple channels, intelligent routing, escalation policies, and rich formatting.

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Prometheus    │────▶│ Alert Manager │────▶│ Routing Engine  │
└─────────────────┘     └──────────────┘     └─────────────────┘
                                                      │
                        ┌─────────────────────────────┼─────────────────────────────┐
                        │                             │                             │
                  ┌─────▼─────┐              ┌───────▼──────┐             ┌────────▼────────┐
                  │   Slack    │              │  PagerDuty   │             │     Email       │
                  └───────────┘              └──────────────┘             └─────────────────┘
```

## Components

### 1. Alert Manager (`app.core.alerting.manager`)

The central component that:

- Receives and processes alerts
- Manages alert lifecycle (firing, acknowledged, resolved, silenced)
- Groups related alerts
- Handles escalations
- Tracks notification delivery

### 2. Routing Engine (`app.core.alerting.routing`)

Sophisticated routing based on:

- Alert severity
- Service/component
- Environment
- Custom labels and annotations
- Time-based rules

### 3. Notification Channels (`app.core.alerting.notifications`)

Supported channels:

- **Slack**: Rich formatted messages with actions
- **PagerDuty**: Incident creation and management
- **Email**: HTML formatted alerts with links

### 4. Templates (`app.core.alerting.templates`)

Customizable templates for:

- Channel-specific formatting
- Severity-based layouts
- Special alert types (SLA, security, deployment)

## Configuration

### Environment Variables

```bash
# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL_CRITICAL=#alerts-critical
SLACK_CHANNEL_WARNINGS=#alerts
SLACK_CHANNEL_DATABASE=#database-alerts
SLACK_CHANNEL_SECURITY=#security-alerts
SLACK_CHANNEL_DEV=#dev-alerts

# PagerDuty Configuration
PAGERDUTY_INTEGRATION_KEY=your-32-character-integration-key
PAGERDUTY_API_KEY=your-api-key-for-acknowledgments

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@yourdomain.com
SMTP_PASSWORD=your-smtp-password
ALERT_EMAIL_FROM=alerts@yourdomain.com

# Alert Manager Settings
ALERT_GROUP_INTERVAL=300  # Group alerts for 5 minutes
ALERT_GROUP_WAIT=10       # Wait 10s before initial notification
```

### Alertmanager Configuration

Use the enhanced configuration file:

```bash
cp monitoring/alertmanager-enhanced.yml monitoring/alertmanager.yml
```

## Alert Routing

### Default Routing Rules

1. **Critical Alerts**
   - Channels: PagerDuty + Slack (#alerts-critical) + Email
   - No grouping delay
   - Repeat interval: 2 hours

2. **Security Incidents**
   - Channels: PagerDuty (security) + Slack (#security-alerts) + Email
   - No acknowledgment allowed
   - Immediate escalation

3. **High Priority**
   - Channels: Slack (#alerts) + Email
   - 1 minute grouping
   - Repeat interval: 4 hours

4. **Service-Specific**
   - Database: #database-alerts + database team email
   - External APIs: #alerts with extended intervals
   - Development: #dev-alerts only

### Custom Routing

Add custom routes in `app/core/alerting/config.py`:

```python
custom_route = Route(
    name="custom",
    rules=[
        RoutingRule(
            name="custom_rule",
            match_conditions={
                "service": "payment-gateway",
                "severity": "critical",
            },
            channels=["pagerduty-payments", "slack-payments"],
            suppress_duration=300,  # 5 minute suppression
        ),
    ],
    channels=channels,
    escalation_policy=custom_escalation_policy,
)
```

## Escalation Policies

Default escalation levels:

1. **Level 0** (Immediate)
   - Slack warnings channel

2. **Level 1** (5 minutes)
   - Email + Slack critical channel

3. **Level 2** (15 minutes)
   - PagerDuty + Manager email

4. **Level 3** (1 hour)
   - Executive PagerDuty + Phone calls

## Alert Templates

### Built-in Templates

- **Critical**: Full details with actions
- **High**: Summary with key metrics
- **Warning**: Concise notification
- **Info**: Minimal notification

### Custom Templates

Create custom templates for specific alert types:

```python
sla_template = AlertTemplate(
    "sla_violation",
    """🚨 *SLA VIOLATION*

Service: $service
Target: $annotation_sla_target
Current: $value
Customer Impact: $annotation_customer_impact

Actions: $runbook_url | $dashboard_url"""
)
```

## Testing Alerts

### 1. Validate Configuration

```bash
python scripts/validate_alerting.py --validate-yaml

# Show required environment variables
python scripts/validate_alerting.py --show-env

# Test channels (dry run)
python scripts/validate_alerting.py --test-channels
```

### 2. Fire Test Alerts

```bash
# Fire specific scenario
python scripts/test_alerts.py fire critical_api_down

# Test escalation
python scripts/test_alerts.py escalation-test

# Simulate alert storm
python scripts/test_alerts.py storm-test

# Test Prometheus webhook
python scripts/test_alerts.py prometheus-test
```

### 3. Manage Alerts

```bash
# List active alerts
python scripts/test_alerts.py list-active

# Acknowledge alert
python scripts/test_alerts.py acknowledge <alert-id>

# Resolve alert
python scripts/test_alerts.py resolve <alert-id>
```

## Integration with Monitoring

### Prometheus Integration

The system automatically receives alerts from Prometheus via webhook:

```yaml
# In alertmanager.yml
receivers:
  - name: 'la-factoria-webhook'
    webhook_configs:
      - url: 'http://la-factoria-api:8000/alerts/webhook'
        send_resolved: true
```

### Metric-Based Alerts

The system also generates alerts from application metrics:

- High error rate (>5%)
- Slow response time (P95 > 1s)
- High memory usage (>85%)
- Database connection issues

## Alert Suppression

Prevent alert storms with:

1. **Time-based suppression**: Suppress similar alerts for X seconds
2. **Inhibition rules**: Critical alerts suppress warnings
3. **Grouping**: Combine related alerts into single notification

## Best Practices

### 1. Alert Design

- **Actionable**: Every alert should have clear remediation steps
- **Contextual**: Include relevant metrics and thresholds
- **Prioritized**: Use appropriate severity levels
- **Documented**: Link to runbooks and dashboards

### 2. Channel Usage

- **Critical**: PagerDuty for immediate response
- **High**: Slack for team awareness
- **Warning**: Email for non-urgent issues
- **Development**: Separate channels to avoid noise

### 3. Escalation

- Start with least disruptive channel
- Escalate based on acknowledgment
- Include clear ownership at each level
- Test escalation paths regularly

### 4. Maintenance

- Review alert effectiveness monthly
- Tune thresholds based on false positive rate
- Update runbooks with incident learnings
- Test notification channels weekly

## Troubleshooting

### Common Issues

1. **Alerts not firing**
   - Check Prometheus rules are loaded
   - Verify webhook endpoint is accessible
   - Check alert thresholds

2. **Notifications not sent**
   - Validate channel configuration
   - Check environment variables
   - Review alertmanager logs

3. **Too many alerts**
   - Review suppression rules
   - Adjust grouping intervals
   - Implement inhibition rules

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger("app.core.alerting").setLevel(logging.DEBUG)
```

### Health Checks

Monitor the alert system:

```bash
# Check alertmanager status
curl http://localhost:9093/-/healthy

# Check API webhook endpoint
curl http://localhost:8000/alerts/active
```

## Security Considerations

1. **Webhook Security**
   - Use authentication tokens
   - Validate webhook signatures
   - Rate limit webhook endpoints

2. **Channel Security**
   - Rotate webhook URLs regularly
   - Use encrypted connections
   - Limit channel permissions

3. **Data Privacy**
   - Sanitize sensitive data in alerts
   - Use secure credential storage
   - Audit alert access

## Future Enhancements

1. **Additional Channels**
   - SMS notifications
   - Microsoft Teams
   - Custom webhooks

2. **Advanced Features**
   - Alert correlation
   - Predictive alerting
   - Auto-remediation triggers

3. **Integrations**
   - Jira ticket creation
   - Status page updates
   - Incident management systems
