# La Factoria Incident Response Checklist

## Overview

This document provides step-by-step procedures for handling production incidents at La Factoria. Follow these steps in order during any production issue.

**Emergency Contact**: [On-call rotation schedule](https://oncall.lafactoria.ai)  
**Status Page**: [status.lafactoria.ai](https://status.lafactoria.ai)

## Incident Severity Levels

### SEV-1 (Critical)
- Complete service outage
- Data loss or corruption
- Security breach
- Cost overrun >$100/hour

### SEV-2 (High)
- Partial service degradation
- Key features unavailable
- Performance <50% normal
- Cost overrun >$20/hour

### SEV-3 (Medium)
- Minor feature issues
- Performance 50-80% normal
- Non-critical errors

## Immediate Response (0-5 minutes)

### 1. Assess the Situation

```bash
# Check service health
curl https://api.lafactoria.ai/health

# Check recent errors
gcloud logging read "severity>=ERROR" --limit 50 --format json

# Check current costs
python scripts/check_ai_costs.py --current
```

### 2. Activate Emergency Controls

#### If AI costs are spiking:
```bash
# Activate kill switch
curl -X POST https://api.lafactoria.ai/admin/cost-controls/kill-switch \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"activate": true}'

# Check usage
curl https://api.lafactoria.ai/monitoring/usage-stats
```

#### If under attack:
```bash
# Enable strict rate limiting
kubectl patch configmap api-config \
  -p '{"data":{"RATE_LIMIT_MULTIPLIER":"0.1"}}'

# Block suspicious IPs
./scripts/security/block_ips.sh suspicious_ips.txt
```

### 3. Notify Stakeholders

- [ ] Post in #incidents Slack channel
- [ ] Update status page
- [ ] Email major customers if SEV-1

Template:
```
INCIDENT: [Brief description]
SEVERITY: [SEV-1/2/3]
IMPACT: [Who/what affected]
STATUS: Investigating
NEXT UPDATE: In 15 minutes
```

## Investigation Phase (5-30 minutes)

### 4. Gather Data

```bash
# Recent deployments
gcloud run revisions list --service=la-factoria-api

# Error patterns
python scripts/analyze_logs.py --timeframe 1h

# Performance metrics
curl https://api.lafactoria.ai/metrics | grep -E "request_duration|error_rate"

# Database health
python scripts/db_health_check.py
```

### 5. Identify Root Cause

Common issues checklist:
- [ ] Recent deployment? → Check revision history
- [ ] Traffic spike? → Check rate limiting
- [ ] AI API issues? → Check provider status
- [ ] Database issues? → Check connection pool
- [ ] Memory leak? → Check container metrics

## Mitigation Phase

### 6. Implement Fix

#### Quick Rollback (if deployment issue):
```bash
# Rollback to previous revision
gcloud run services update-traffic la-factoria-api \
  --to-revisions=PREVIOUS_REVISION=100

# Verify rollback
curl https://api.lafactoria.ai/health
```

#### Scale Up (if load issue):
```bash
# Increase instances
gcloud run services update la-factoria-api \
  --min-instances=5 \
  --max-instances=50

# Increase memory if needed
gcloud run services update la-factoria-api \
  --memory=2Gi
```

#### Database Issues:
```bash
# Reset connection pool
kubectl rollout restart deployment/api

# Emergency read replica promotion (if primary down)
./scripts/db/promote_read_replica.sh
```

### 7. Verify Fix

- [ ] Service health check passing
- [ ] Error rate returning to normal
- [ ] Performance metrics acceptable
- [ ] No new errors in logs

## Recovery Phase

### 8. Monitor Stability

```bash
# Watch error rates for 30 minutes
watch -n 30 'curl -s https://api.lafactoria.ai/metrics | grep error_rate'

# Monitor costs
python scripts/monitor_costs.py --alert-threshold 50
```

### 9. Update Status

- [ ] Post resolution in #incidents
- [ ] Update status page to "Resolved"
- [ ] Email affected customers with RCA timeline

## Post-Incident

### 10. Document Incident

Create incident report with:
- Timeline of events
- Root cause analysis
- Impact assessment
- Action items to prevent recurrence

Template location: `docs/emergency/incident_report_template.md`

### 11. Schedule Post-Mortem

- Within 48 hours for SEV-1
- Within 1 week for SEV-2
- Optional for SEV-3

## Quick Reference Commands

### Cost Control
```bash
# Check current spend
curl https://api.lafactoria.ai/monitoring/usage-stats | jq '.total_cost_today'

# Set emergency limit
curl -X PUT https://api.lafactoria.ai/admin/cost-controls/limits \
  -d '{"daily_limit": 100}'

# Disable expensive features
kubectl set env deployment/api ENABLE_AUDIO_GENERATION=false
```

### Performance
```bash
# Clear cache
redis-cli FLUSHALL

# Restart workers
kubectl rollout restart deployment/content-workers

# Enable read-only mode
kubectl set env deployment/api READ_ONLY_MODE=true
```

### Security
```bash
# Rotate API keys
python scripts/security/rotate_api_keys.py --all

# Enable firewall rules
gcloud compute firewall-rules update default-allow-https \
  --source-ranges="<trusted_ips>"

# Check for suspicious activity
python scripts/security/audit_access_logs.py --last 1h
```

## Emergency Contacts

- **Engineering On-Call**: Check PagerDuty
- **AI API Vendors**:
  - Gemini Support: support@google.com
  - ElevenLabs: support@elevenlabs.io
- **Infrastructure**:
  - GCP Support: 1-877-355-5787
  - Railway Support: support@railway.app

## Validation Checklist

Before closing incident:
- [ ] All services healthy
- [ ] No elevated error rates
- [ ] Costs within normal range
- [ ] All customers notified
- [ ] Incident documented
- [ ] Post-mortem scheduled (if needed)
- [ ] Monitoring alerts reset

---

**Last Updated**: 2025-07-30  
**Next Review**: Monthly or after major incident