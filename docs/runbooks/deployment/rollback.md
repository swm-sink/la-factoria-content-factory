# Emergency Rollback Procedure

**Severity**: P1 (Critical)  
**Time Estimate**: 5-10 minutes  
**Last Updated**: 2025-07-31  
**Owner**: Platform Team  
**Related SLO**: Rollback Success Rate 100%

## Summary

Emergency procedure to quickly revert to a previous stable version when critical issues are detected after deployment. This runbook provides step-by-step instructions for various rollback scenarios including code, database, and configuration rollbacks. Expected outcome is rapid restoration of service stability with minimal user impact.

## Symptoms

Immediate rollback triggers:

- [ ] API availability < 95%
- [ ] Error rate > 10%
- [ ] Critical functionality broken
- [ ] Data corruption detected
- [ ] Security vulnerability exposed
- [ ] Performance degradation > 50%
- [ ] Critical user-facing features failing

## Prerequisites

- Railway CLI access
- Knowledge of last stable version
- Access to monitoring dashboards

## Rollback Decision Tree

```
Issue Detected
    ↓
Is it affecting > 10% of users?
    ├─ No → Monitor and fix forward
    └─ Yes ↓
       Is core functionality broken?
           ├─ No → Consider feature flag disable
           └─ Yes → IMMEDIATE ROLLBACK
```

## Resolution Steps

### Immediate Rollback Steps

### Step 1: Initiate Rollback (1-2 minutes)

**Goal**: Start reverting to last known good version

```bash
# 1. Get recent deployments
railway deployments list --limit 10

# 2. Identify last stable deployment
# Look for deployment before current issues

# 3. Execute rollback
railway deployments rollback <stable-deployment-id>

# 4. Monitor rollback progress
railway logs --tail -f
```

### Step 2: Verify Rollback (2-3 minutes)

**Goal**: Ensure service is restored

```bash
# Check deployment status
railway status

# Verify health
curl --fail https://api.lafactoria.com/health

# Check version rolled back
curl --fail https://api.lafactoria.com/api/version

# Monitor error rates dropping
railway logs --tail 100 | grep -c ERROR
```

### Step 3: Stabilization (2-5 minutes)

**Goal**: Ensure system is stable

```bash
# Clear any bad cache
railway run python scripts/clear_cache.py

# Reset connection pools
railway run python scripts/reset_connections.py

# Run smoke tests
npm run test:production:smoke
```

## Alternative Rollback Methods

### Git-Based Rollback

```bash
# If Railway rollback fails
git checkout deploy-<last-stable-tag>
railway up --detach

# Force deployment
railway deploy --force
```

### Database Rollback

```bash
# If database migrations need reverting
railway run python manage.py migrate <previous-migration>

# Or restore from backup
railway run python scripts/restore_database.py --timestamp=<backup-time>
```

### Feature Flag Rollback

```bash
# Disable problematic features without full rollback
railway env set FEATURE_NEW_ALGORITHM=false
railway env set FEATURE_EXPERIMENTAL=false
railway restart
```

## Communication During Rollback

### Initial Alert

```
ALERT: Initiating emergency rollback
Reason: [Specific issue]
Impact: Service may be unavailable for 5 minutes
Status: Rollback in progress
```

### Progress Updates

```
UPDATE: Rollback 50% complete
Current Status: Deploying stable version
ETA: 3 minutes
```

### Completion Notice

```
RESOLVED: Rollback completed successfully
Service Status: Fully operational
Version: Reverted to [version]
Next Steps: Post-mortem scheduled
```

## Post-Rollback Actions

### Immediate (First 30 minutes)

1. **Verify Stability**:

   ```bash
   # Continuous monitoring
   watch -n 10 'curl --fail -s https://api.lafactoria.com/health | jq .status'
   ```

2. **Document Timeline**:

   ```bash
   echo "Rollback completed at $(date)" >> incidents.log
   echo "From version: $FAILED_VERSION" >> incidents.log
   echo "To version: $STABLE_VERSION" >> incidents.log
   ```

3. **Preserve Evidence**:

   ```bash
   # Save logs from failed deployment
   railway logs --deployment $FAILED_DEPLOYMENT > "logs/failed-deploy-$(date +%Y%m%d-%H%M%S).log"

   # Capture metrics
   railway metrics export --deployment $FAILED_DEPLOYMENT
   ```

### Follow-up (Next 24 hours)

- [ ] Root cause analysis
- [ ] Fix issues in development
- [ ] Update deployment procedures
- [ ] Schedule post-mortem meeting
- [ ] Update runbooks with learnings

## Rollback Scenarios

### Scenario 1: Bad Code Deploy

**Symptoms**: Immediate 500 errors
**Action**: Standard rollback
**Prevention**: Better testing

### Scenario 2: Performance Regression

**Symptoms**: Slow response times
**Action**: Rollback or scale up
**Prevention**: Load testing

### Scenario 3: Database Migration Issue

**Symptoms**: Schema errors
**Action**: Rollback + migration revert
**Prevention**: Migration testing

### Scenario 4: Configuration Error

**Symptoms**: Service won't start
**Action**: Fix config or rollback
**Prevention**: Config validation

## Rollback Metrics

Track these for improvement:

- Time to detect issue
- Time to initiate rollback
- Time to restore service
- User impact duration
- Root cause category

## Best Practices

1. **Practice Rollbacks**:
   - Test quarterly in staging
   - Document lessons learned
   - Update procedures

2. **Automated Triggers**:

   ```python
   # Example auto-rollback logic
   if error_rate > 0.1 and duration > 300:
       trigger_automatic_rollback()
   ```

3. **Rollback Testing**:
   - Verify rollback works before deploying
   - Test data compatibility
   - Check for breaking changes

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

- [Deployment Procedures](production-deploy.md)
- Incident Response (see relevant docs section)
- Post-Mortem Template (see relevant docs section)
- Change Management (see relevant docs section)
