# API Down - Critical Incident Response

**Severity**: P1 (Critical)  
**Time Estimate**: 5-15 minutes  
**Last Updated**: 2025-07-31  
**Owner**: Platform Team  
**Related SLO**: API Availability 99.9%

## Summary

Complete API outage affecting all users. This runbook provides steps to quickly diagnose and restore service.

## Symptoms

- [ ] Health check endpoint returns errors or timeouts
- [ ] All API endpoints unresponsive
- [ ] Monitoring shows 100% error rate
- [ ] User reports of complete service unavailability

## Alert References

- **Alert Name**: `api-availability-critical`
- **Dashboard**: API Health Dashboard
- **Runbook Trigger**: Health check failures > 3 consecutive

## Prerequisites

- Railway CLI access
- Production environment credentials
- PagerDuty access for escalation

## Initial Assessment (1-2 minutes)

1. Verify API is truly down (not monitoring false positive):

   ```bash
   # From multiple locations
   curl -f https://api.lafactoria.com/health --max-time 5
   curl -f https://api.lafactoria.com/api/health --max-time 5
   ```

2. Check Railway dashboard:

   ```bash
   railway status
   railway logs --tail 100
   ```

3. Check for ongoing deployments:

   ```bash
   railway deployments list --limit 5
   ```

## Resolution Steps

### Step 1: Quick Service Restart (2-3 minutes)

**Goal**: Attempt immediate recovery

```bash
# Restart the service
railway restart

# Monitor startup logs
railway logs --tail -f
```

**Expected Output**:

```
Starting application...
Database connected successfully
Server listening on port 8000
Health check passed
```

### Step 2: Check Infrastructure (3-5 minutes)

**Goal**: Identify infrastructure issues

```bash
# Check service metrics
railway metrics cpu --last 1h
railway metrics memory --last 1h

# Check database connectivity
railway run python -c "from app.db import engine; engine.connect()"
```

**If database connection fails**, go to [Database Connection Issues](../database/connection-issues.md)

### Step 3: Emergency Rollback (5-10 minutes)

**Goal**: Restore last known good version

```bash
# List recent deployments
railway deployments list --limit 10

# Rollback to previous version
railway deployments rollback <deployment-id>

# Monitor rollback
railway logs --tail -f
```

### Step 4: Scale Up Resources (if needed)

**Goal**: Address resource constraints

```bash
# Scale up if under heavy load
railway scale --replicas 3

# Or increase resources
railway env set WEB_CONCURRENCY=4
railway restart
```

## Verification

1. Health check passes:

   ```bash
   curl --fail https://api.lafactoria.com/health
   # Expected: {"status": "healthy", "timestamp": "..."}
   ```

2. Test critical endpoints:

   ```bash
   # Authentication
   curl --fail -X POST https://api.lafactoria.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"test": "true"}'

   # Content generation
   curl --fail https://api.lafactoria.com/api/content/test
   ```

3. Monitor recovery:

   ```bash
   # Watch error rate drop
   railway logs --tail -f | grep -E "(ERROR|SUCCESS)"
   ```

## Rollback Procedure

If service remains down after 10 minutes:

1. **Immediate Actions**:

   ```bash
   # Enable maintenance mode
   railway env set MAINTENANCE_MODE=true

   # Deploy static maintenance page
   railway deploy --service maintenance-page
   ```

2. **Escalate to Senior Engineer**:
   - Page on-call senior engineer
   - Provide all logs and actions taken
   - Prepare for extended downtime procedures

## Communication Template

**Initial Alert** (0-5 min):

```
INVESTIGATING: API service experiencing issues
Impact: All API functionality affected
Status: Engineering team investigating
Next Update: In 10 minutes
```

**Progress Update** (5-15 min):

```
UPDATE: API service [recovering/still down]
Actions Taken: [List actions]
Current Status: [Status]
ETA: [Estimate]
```

**Resolution Notice**:

```
RESOLVED: API service restored
Duration: X minutes
Root Cause: Under investigation
Post-Mortem: To follow within 24h
```

## Post-Incident Actions

- [ ] Ensure all alerts have cleared
- [ ] Document timeline in incident ticket
- [ ] Schedule post-mortem (if > 5 min downtime)
- [ ] Update runbook with new findings
- [ ] Review monitoring coverage

## Related Documentation

- Emergency Contacts (see relevant docs section)
- Architecture Overview (see relevant docs section)
- Deployment Procedures (see relevant docs section)
- Post-Mortem Template (see relevant docs section)

## Common Causes

1. **Memory exhaustion** - Check for memory leaks
2. **Database connection pool** - Exhausted connections
3. **Failed deployment** - Bad code or config
4. **Rate limiting** - DDoS or abuse
5. **Certificate expiration** - SSL/TLS issues
