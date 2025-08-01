# Alert Management Runbook

## Overview

This runbook covers the configuration, testing, and management of La Factoria's alert system.

## Quick Reference

- **Alert Dashboard**: <http://localhost:9093> (Alertmanager UI)
- **Active Alerts API**: <http://localhost:8000/alerts/active>
- **Test Script**: `python scripts/test_alerts.py`
- **Validation Script**: `python scripts/validate_alerting.py`

## Initial Setup

### 1. Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your notification channel credentials:
# - SLACK_WEBHOOK_URL
# - PAGERDUTY_INTEGRATION_KEY
# - SMTP settings for email
```

### 2. Validate Configuration

```bash
# Show required environment variables
python scripts/validate_alerting.py --show-env

# Validate current configuration
python scripts/validate_alerting.py --validate-yaml

# Test channels (dry run by default)
DRY_RUN=true python scripts/validate_alerting.py --test-channels
```

### 3. Deploy Alertmanager

```bash
# Copy enhanced configuration
cp monitoring/alertmanager-enhanced.yml monitoring/alertmanager.yml

# Start monitoring stack
cd monitoring
docker-compose up -d
```

## Testing Alerts

### Fire Test Alerts

```bash
# Test specific scenarios
python scripts/test_alerts.py fire critical_api_down
python scripts/test_alerts.py fire high_error_rate
python scripts/test_alerts.py fire security_incident

# Test escalation flow
python scripts/test_alerts.py escalation-test

# Test alert storm handling
python scripts/test_alerts.py storm-test
```

### Manage Active Alerts

```bash
# List active alerts
python scripts/test_alerts.py list-active

# Acknowledge an alert
python scripts/test_alerts.py acknowledge <alert-id>

# Resolve an alert
python scripts/test_alerts.py resolve <alert-id>
```

## Common Tasks

### Adding a New Notification Channel

1. Create channel configuration in `.env`:

```bash
CUSTOM_WEBHOOK_URL=https://custom.webhook.url
CUSTOM_CHANNEL=#custom-alerts
```

2. Add channel in `app/core/alerting/config.py`:

```python
channels["custom"] = CustomNotifier(
    webhook_url=config["custom"]["webhook_url"],
    channel=config["custom"]["channel"]
)
```

3. Update routing rules to use the channel.

### Creating Custom Alert Templates

1. Add template in `app/core/alerting/templates.py`:

```python
custom_template = AlertTemplate(
    "custom_alert",
    """🚨 $alert_name
Service: $service
Impact: $annotation_impact
Action: $runbook_url"""
)
```

2. Register template:

```python
formatter.add_template("slack", "custom_alert", custom_template)
```

### Modifying Routing Rules

1. Edit `app/core/alerting/config.py`
2. Add new routing rule:

```python
RoutingRule(
    name="payment_critical",
    match_conditions={
        "service": "payment-gateway",
        "severity": "critical"
    },
    channels=["pagerduty", "slack-critical"],
    suppress_duration=300
)
```

### Setting Up Escalation

1. Define escalation policy:

```python
payment_escalation = EscalationPolicy(
    name="payment",
    levels=[
        {"delay": 0, "channels": ["slack-payments"]},
        {"delay": 300, "channels": ["pagerduty-payments"]},
        {"delay": 900, "channels": ["phone-oncall"]}
    ]
)
```

2. Attach to route:

```python
route.escalation_policy = payment_escalation
```

## Troubleshooting

### Alerts Not Firing

1. Check Prometheus rules:

```bash
curl http://localhost:9090/api/v1/rules | jq
```

2. Verify webhook endpoint:

```bash
curl -X POST http://localhost:8000/alerts/webhook \
  -H "Content-Type: application/json" \
  -d '{"alerts": []}'
```

3. Check alert thresholds in metrics:

```bash
curl http://localhost:8000/metrics | grep -E "(error_rate|latency)"
```

### Notifications Not Received

1. Validate channel configuration:

```bash
python scripts/validate_alerting.py
```

2. Check Alertmanager logs:

```bash
docker logs monitoring_alertmanager_1
```

3. Test channel directly:

```bash
DRY_RUN=false python scripts/validate_alerting.py --test-channels
```

### Too Many Alerts

1. Review suppression settings:
   - Check `suppress_duration` in routing rules
   - Verify grouping intervals

2. Implement inhibition rules in `alertmanager.yml`:

```yaml
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['service']
```

3. Adjust alert thresholds in `monitoring/rules/alerts.yml`

### Alert Storm

1. Check grouping:

```bash
# Alerts should be grouped by service/severity
curl http://localhost:8000/alerts/active | jq '.alerts | group_by(.group_key)'
```

2. Enable rate limiting:
   - Adjust `group_interval` in alertmanager.yml
   - Increase `suppress_duration` for noisy alerts

## Maintenance

### Weekly Tasks

- [ ] Review active alerts and clear stale ones
- [ ] Test critical notification channels
- [ ] Check escalation policies are working
- [ ] Review and tune alert thresholds

### Monthly Tasks

- [ ] Analyze alert metrics (frequency, resolution time)
- [ ] Update runbooks based on incidents
- [ ] Review and optimize routing rules
- [ ] Test disaster recovery scenarios

### Metrics to Monitor

1. **Alert Volume**
   - alerts.received
   - alerts.processed
   - alerts.suppressed

2. **Notification Success**
   - notifications.sent{channel="slack"}
   - notifications.failed{channel="pagerduty"}

3. **Response Times**
   - alert.acknowledgment.time
   - alert.resolution.time

## Integration Points

### With Prometheus

Alerts flow: Prometheus → Alertmanager → La Factoria API → Notification Channels

### With SLA Monitoring

SLA violations automatically trigger alerts with appropriate severity.

### With Health Checks

Failed health checks can trigger immediate alerts bypassing normal grouping.

## Security

### Webhook Authentication

1. Implement webhook tokens:

```python
ALERT_WEBHOOK_TOKEN = os.getenv("ALERT_WEBHOOK_TOKEN")
```

2. Validate in endpoint:

```python
if request.headers.get("X-Webhook-Token") != ALERT_WEBHOOK_TOKEN:
    raise HTTPException(status_code=401)
```

### Channel Security

- Rotate webhook URLs quarterly
- Use encrypted connections (HTTPS/TLS)
- Implement IP allowlisting where possible
- Audit access to alert management endpoints

## Emergency Procedures

### All Channels Down

1. Check network connectivity
2. Verify DNS resolution
3. Use backup notification method (direct API calls)
4. Check for service-wide outages

### Alert System Failure

1. Access Prometheus directly: <http://localhost:9090/alerts>
2. Check raw metrics: <http://localhost:8000/metrics>
3. Use manual notification scripts as backup
4. Monitor logs directly

### Rollback Procedure

1. Stop alert manager:

```bash
docker-compose stop alertmanager
```

2. Restore previous configuration:

```bash
cp monitoring/alertmanager.yml.backup monitoring/alertmanager.yml
```

3. Restart:

```bash
docker-compose up -d alertmanager
```

## Contact Information

- **On-Call Engineer**: Check PagerDuty schedule
- **Slack Channel**: #alerts-help
- **Escalation**: <security@lafactoria.ai> for security incidents
