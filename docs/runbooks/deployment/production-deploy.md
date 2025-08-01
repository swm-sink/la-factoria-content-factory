# Production Deployment Runbook

**Severity**: P3 (Medium)  
**Time Estimate**: 15-30 minutes  
**Last Updated**: 2025-07-31  
**Owner**: Platform Team  
**Related SLO**: Deployment Success Rate > 95%

## Summary

Standard procedure for deploying code changes to production environment on Railway. This runbook covers pre-deployment validation, zero-downtime deployment, health verification, and rollback procedures. Expected outcome is successful deployment with all services operational and no user impact.

## Prerequisites

- [ ] Code reviewed and approved
- [ ] All tests passing in CI
- [ ] No active incidents
- [ ] Deployment window confirmed
- [ ] Rollback plan prepared

## Pre-Deployment Checklist

1. **Code Validation**:

   ```bash
   # Ensure on correct branch and up to date with remote
   git checkout main
   git pull origin main

   # Run unit and integration tests to verify code quality
   npm test
   npm run test:integration

   # Scan for known security vulnerabilities in dependencies
   npm audit

   # Run security analysis on Python code for common issues
   bandit -r app/
   ```

2. **Environment Check**:

   ```bash
   # Verify production health before deployment
   curl --fail https://api.lafactoria.com/health
   # Expected: {"status": "healthy"}

   # Check current deployment version and status
   railway status

   # Count recent errors to establish baseline
   railway logs --tail 100 | grep ERROR | wc -l
   # Note this count for comparison after deployment
   ```

3. **Backup Critical Data**:

   ```bash
   # Trigger database backup before deployment
   railway run python scripts/backup_database.py

   # Verify backup completed successfully and is restorable
   railway run python scripts/verify_backup.py --latest
   # Expected: "Backup verified: <timestamp>"
   ```

## Deployment Steps

### Step 1: Prepare Deployment (5 minutes)

**Goal**: Stage changes for deployment

```bash
# Create deployment tag with timestamp for tracking
VERSION=$(date +%Y%m%d-%H%M%S)
git tag -a "deploy-$VERSION" -m "Production deployment $VERSION"
git push origin "deploy-$VERSION"

# Log deployment start for audit trail
echo "Deployment $VERSION started at $(date)" >> deployments.log
```

### Step 2: Deploy to Production (10-15 minutes)

**Goal**: Deploy new version with zero downtime

```bash
# Deploy to production using Railway's zero-downtime deployment
railway up

# Monitor deployment progress in real-time
# Watch for build and health check status
railway logs --tail -f

# Expected output:
# - "Build started"
# - "Build completed"
# - "Deployment started"
# - "Health check passed"
```

### Step 3: Health Verification (5 minutes)

**Goal**: Ensure deployment successful

```bash
# 1. Check overall service health with formatted output
curl --fail https://api.lafactoria.com/health | jq .
# Expected: All components show "healthy" status

# 2. Test critical endpoints for functionality
# Verify authentication service is responding
curl --fail -X POST https://api.lafactoria.com/api/auth/health
# Expected: 200 OK

# Verify content generation service is operational
curl --fail https://api.lafactoria.com/api/content/health
# Expected: 200 OK

# 3. Compare error rates to pre-deployment baseline
railway logs --tail 100 | grep -c ERROR
# Should be same or lower than pre-deployment count
```

### Step 4: Smoke Tests (5 minutes)

**Goal**: Verify core functionality

```bash
# Run automated smoke tests against production
# Tests core user journeys and critical features
npm run test:production:smoke
# Expected: All tests pass

# Manual verification checklist:
# [ ] Can create new content
# [ ] Authentication works
# [ ] Audio generation functional
# [ ] Database queries responsive
```

## Monitoring During Deployment

Keep these dashboards open:

1. API Health Dashboard
2. Error Rate Monitor
3. Performance Metrics Dashboard

Watch for:

- Spike in error rates
- Increased response times
- Memory usage anomalies
- Database connection issues

## Rollback Procedure

If issues detected within 30 minutes:

### Quick Rollback (5 minutes)

```bash
# 1. List recent deployments to identify last stable version
railway deployments list --limit 5
# Note the deployment ID of the last known good version

# 2. Rollback to previous stable version
railway deployments rollback <deployment-id>

# 3. Verify rollback completed successfully
railway status
# Confirm service is healthy after rollback
curl --fail https://api.lafactoria.com/health
# Expected: {"status": "healthy"}
```

### Emergency Rollback

```bash
# If Railway rollback fails, deploy previous version manually
git checkout deploy-<previous-version>
railway up --detach

# Enable maintenance mode to prevent user access during recovery
railway env set MAINTENANCE_MODE=true
# Remember to disable after recovery:
# railway env set MAINTENANCE_MODE=false
```

## Post-Deployment Tasks

### Immediate (First 30 minutes)

- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Review user feedback channels
- [ ] Verify all features working

### Follow-up (Next 24 hours)

- [ ] Analyze deployment metrics
- [ ] Update deployment log
- [ ] Clean up old deployments
- [ ] Document any issues

## Communication Templates

### Pre-Deployment Notice

```
SCHEDULED: Production deployment
Time: [Time]
Duration: ~15 minutes
Impact: No expected downtime
Features: [List key changes]
```

### Post-Deployment Success

```
COMPLETED: Production deployment successful
Version: [Version]
Duration: [X] minutes
Status: All systems operational
Changes: [Link to changelog]
```

### Rollback Notice

```
ROLLBACK: Reverting deployment
Reason: [Brief reason]
Impact: Service may be briefly unavailable
ETA: 5 minutes
```

## Deployment Best Practices

1. **Timing**:
   - Deploy during low-traffic periods
   - Avoid Fridays and before holidays
   - Consider timezone differences

2. **Communication**:
   - Notify team before deployment
   - Update status page if needed
   - Document in deployment log

3. **Gradual Rollout**:

   ```bash
   # Start with 10% of traffic for high-risk features
   railway env set FEATURE_FLAG_NEW_FEATURE=0.1
   # Monitor metrics for 30 minutes, then increase if stable
   railway env set FEATURE_FLAG_NEW_FEATURE=0.5
   # After successful 50% rollout, enable for all users
   railway env set FEATURE_FLAG_NEW_FEATURE=1.0
   ```

## Common Issues and Solutions

### Build Failures

- Check Railway build logs
- Verify dependencies installed
- Review Dockerfile changes

### Health Check Failures

- Increase startup timeout
- Check database migrations
- Verify environment variables

### Performance Degradation

- Check for N+1 queries
- Review new dependencies
- Profile memory usage

## Symptoms

- Deployment needed for bug fixes or new features
- Scheduled release window
- Hotfix required for production issue

## Resolution Steps

See deployment steps above (Steps 1-4).

## Verification

1. All health checks pass
2. No increase in error rates
3. Performance metrics stable
4. Smoke tests successful
5. User functionality verified

## Related Documentation

- CI/CD Pipeline Guide (see docs/deployment/)
- Environment Configuration (see docs/)
- Rollback Procedures (see rollback.md)
- Monitoring Setup Guide (see docs/monitoring/)
