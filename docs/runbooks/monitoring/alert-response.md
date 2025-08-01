# Monitoring Alert Response

**Severity**: P2 (High)  
**Time Estimate**: 5-15 minutes  
**Last Updated**: 2025-07-31  
**Owner**: Platform Team  
**Related SLO**: Alert Response Time < 15 minutes

## Summary

Standard procedure for responding to monitoring alerts from the La Factoria platform monitoring system.

## Symptoms

- [ ] PagerDuty alert received
- [ ] Slack monitoring channel alert
- [ ] Email alert notification
- [ ] Dashboard showing red/critical status

## Alert References

- **Alert Types**: All monitoring alerts
- **Dashboard**: Alert Dashboard
- **Runbook Trigger**: Any monitoring system alert

## Prerequisites

- Access to monitoring dashboards
- Railway CLI access
- Runbook library access
- Communication channels access

## Resolution Steps

### Step 1: Alert Triage (1-2 minutes)

**Goal**: Understand the alert and its severity

```bash
# 1. Identify alert details
# Check alert message for:
# - Service affected
# - Metric triggering alert
# - Current value vs threshold
# - Duration of issue

# 2. Access relevant dashboard
# Each alert should link to its dashboard

# 3. Check for multiple related alerts
railway logs --tail 50 | grep ALERT
```

### Step 2: Initial Assessment (2-3 minutes)

**Goal**: Determine impact and urgency

```bash
# Check service health
curl --fail https://api.lafactoria.com/health

# Check current error rate
railway logs --tail 100 | grep -c ERROR

# Check active users/requests
railway metrics requests --last 5m
```

**Decision Matrix**:
| User Impact | Service Degraded | Action |
|------------|------------------|---------|
| > 50% | Yes | P1 - Immediate response |
| 10-50% | Yes | P2 - Rapid response |
| < 10% | Yes | P3 - Standard response |
| None | No | P4 - Monitor only |

### Step 3: Route to Correct Runbook (1-2 minutes)

**Goal**: Use specific runbook for the issue

Common alert mappings:

- `api-down` → [API Down Runbook](../incident-response/api-down.md)
- `high-error-rate` → [High Error Rate Runbook](../incident-response/high-error-rate.md)
- `database-connection` → [Database Connection Runbook](../database/connection-issues.md)
- `slow-response` → [Slow Response Runbook](../performance/slow-response.md)
- `rate-limit-exceeded` → [Rate Limiting Runbook](../api/rate-limiting-issues.md)

### Step 4: Communication (2-3 minutes)

**Goal**: Keep stakeholders informed

```bash
# 1. Acknowledge alert in PagerDuty
# This stops escalation

# 2. Post initial update
```

**Slack Template**:

```
🚨 Alert: [Alert Name]
Status: Investigating
Impact: [Estimated impact]
Engineer: @[your-name]
ETA: [Initial estimate]
Thread for updates 👇
```

**Status Page Update** (if customer-facing):

```bash
# Use status page CLI or web interface
railway run python scripts/update_status_page.py \
  --component=api \
  --status=degraded \
  --message="Investigating reported issues"
```

### Step 5: Execute Resolution (5-30 minutes)

**Goal**: Follow specific runbook to resolve

```bash
# Follow the specific runbook identified in Step 3
# Document actions taken for post-mortem
echo "[$(date)] Alert: $ALERT_NAME, Action: $ACTION" >> incident.log
```

### Step 6: Verify Resolution (2-3 minutes)

**Goal**: Confirm issue is resolved

```bash
# 1. Check metric has returned to normal
# View the metric that triggered the alert

# 2. Verify service health
curl --fail https://api.lafactoria.com/health

# 3. Check alert has cleared
# Alert should auto-resolve when metric recovers

# 4. Run smoke tests
npm run test:smoke:production
```

## Alert Types and Responses

### Infrastructure Alerts

| Alert | Severity | First Action |
|-------|----------|--------------|
| High CPU | P2 | Check for runaway processes |
| High Memory | P2 | Check for memory leaks |
| Disk Space | P3 | Clean up logs/temp files |
| Network Issues | P1 | Check connectivity |

### Application Alerts

| Alert | Severity | First Action |
|-------|----------|--------------|
| High Error Rate | P2 | Check recent deployments |
| Slow Response | P2 | Check database performance |
| Failed Health Checks | P1 | Check service status |
| Queue Backup | P3 | Check worker processes |

### Business Alerts

| Alert | Severity | First Action |
|-------|----------|--------------|
| Low Conversion | P3 | Check user flow |
| High Bounce Rate | P3 | Check page performance |
| Payment Failures | P1 | Check payment provider |
| Content Quality | P4 | Review generation logs |

## Communication Best Practices

### During Incident

- Post updates every 15 minutes
- Be specific about actions taken
- Set realistic ETAs
- Escalate if needed

### Update Template

```
UPDATE [Time since start]:
✅ Completed: [What was done]
🔄 Current: [What's being done]
⏭️ Next: [What's planned]
ETA: [Updated estimate]
```

### Resolution Template

```
✅ RESOLVED
Duration: [Total time]
Root Cause: [Brief description]
Fix: [What fixed it]
Impact: [Final assessment]
Follow-up: [Post-mortem scheduled/actions needed]
```

## Escalation Path

### When to Escalate

- Unable to resolve within 30 minutes
- Issue is worsening
- Multiple services affected
- Data integrity concerns
- Security implications

### Escalation Levels

1. **L1** - On-call engineer (0-30 min)
2. **L2** - Senior engineer (30-60 min)
3. **L3** - Team lead/Architect (60+ min)
4. **L4** - CTO/Executive (major incident)

## Post-Incident Actions

### Immediate (within 1 hour)

- [ ] Ensure all alerts cleared
- [ ] Update status page
- [ ] Close incident ticket
- [ ] Brief message to team

### Next Day

- [ ] Create post-mortem document
- [ ] Schedule post-mortem meeting
- [ ] Update runbooks if needed
- [ ] File improvement tickets

### Post-Mortem Template Location

`/docs/templates/post-mortem.md`

## Alert Fatigue Prevention

### Review Alerts Monthly

```bash
# Generate alert statistics
railway run python scripts/analyze_alerts.py --last-month

# Review for:
# - Frequently firing alerts
# - False positives
# - Alerts that auto-resolve
# - Missing alerts (incidents without alerts)
```

### Tuning Guidelines

- Adjust thresholds based on actual incidents
- Add appropriate delays/durations
- Group related alerts
- Remove noisy alerts

## Verification

1. **Confirm issue is resolved**:
   - Check relevant metrics have returned to normal
   - Verify service health endpoints respond correctly
   - Monitor for any recurring issues

2. **Test functionality**:
   - Run relevant smoke tests if available
   - Manually verify critical user paths
   - Check error logs are clear

3. **Document resolution**:
   - Note what fixed the issue
   - Update runbook if new solutions found
   - Create follow-up tickets if needed

## Related Documentation

- Monitoring Setup (see relevant docs section)
- Alert Configuration (see relevant docs section)
- Incident Response Process (see relevant docs section)
- Post-Mortem Process (see relevant docs section)
