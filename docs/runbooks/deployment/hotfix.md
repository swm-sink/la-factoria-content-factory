# Hotfix Deployment Procedure

**Severity**: P2 (High)  
**Time Estimate**: 10-20 minutes  
**Last Updated**: 2025-07-31  
**Owner**: Platform Team  
**Related SLO**: Hotfix Deployment Time < 30 minutes

## Summary

Emergency procedure for deploying critical fixes to production outside of normal deployment windows.

## Symptoms

- [ ] Critical bug in production
- [ ] Security vulnerability discovered
- [ ] Data corruption risk
- [ ] Major functionality broken

## Alert References

- **Alert Name**: Manual trigger
- **Dashboard**: Production Health
- **Runbook Trigger**: Critical issue requiring immediate fix

## Prerequisites

- Identified root cause and fix
- Fix tested locally
- Railway CLI access
- Approval from team lead (if possible)

## Hotfix Decision Criteria

Use hotfix deployment when:

- **Severity**: Customer-impacting issue
- **Scope**: Fix is small and isolated
- **Risk**: Lower risk than leaving issue
- **Testing**: Can be quickly validated

DO NOT use hotfix for:

- Feature additions
- Large refactoring
- Untested changes
- Non-critical issues

## Resolution Steps

### Step 1: Prepare Hotfix Branch (3-5 minutes)

**Goal**: Create isolated fix

```bash
# 1. Create hotfix branch from production
git checkout main
git pull origin main
git checkout -b hotfix/issue-description

# 2. Apply minimal fix
# Make ONLY necessary changes

# 3. Commit with clear message
git add .
git commit -m "hotfix: Brief description of critical fix

Issue: [Issue description]
Impact: [User impact]
Fix: [What was changed]
"

# 4. Push hotfix branch
git push origin hotfix/issue-description
```

### Step 2: Fast-Track Testing (5-10 minutes)

**Goal**: Validate fix works

```bash
# 1. Run targeted tests
npm test -- --testPathPattern=affected-module
pytest tests/test_affected_module.py

# 2. Run smoke tests
npm run test:smoke

# 3. Manual validation
# Test the specific issue locally
# Document test results

# 4. Get peer review if possible
# Even 5-minute review helps
```

### Step 3: Deploy Hotfix (5-10 minutes)

**Goal**: Deploy with minimal disruption

```bash
# 1. Announce deployment
echo "🚨 HOTFIX DEPLOYMENT starting at $(date)" | \
  railway run python scripts/notify_team.py

# 2. Snapshot current state
railway deployments list --limit 1 > rollback_point.txt
railway run python scripts/create_backup.py --emergency

# 3. Deploy hotfix
git checkout hotfix/issue-description
railway up --detach

# 4. Monitor deployment
railway logs --tail -f
```

### Step 4: Validate in Production (2-5 minutes)

**Goal**: Ensure fix is working

```bash
# 1. Test specific fix
# Run exact steps that reproduced issue

# 2. Check health
curl --fail https://api.lafactoria.com/health

# 3. Monitor metrics
railway logs --tail 100 | grep -E "ERROR|SUCCESS"

# 4. Check error rates
railway run python scripts/check_error_rate.py --last=5m
```

### Step 5: Merge and Cleanup (3-5 minutes)

**Goal**: Integrate fix properly

```bash
# 1. If successful, merge to main
git checkout main
git merge hotfix/issue-description
git push origin main

# 2. Tag the hotfix
git tag -a "hotfix-$(date +%Y%m%d-%H%M)" -m "Emergency fix for [issue]"
git push origin --tags

# 3. Delete hotfix branch
git branch -d hotfix/issue-description
git push origin --delete hotfix/issue-description

# 4. Update tracking
echo "Hotfix deployed: $(date)" >> hotfix_log.txt
```

## Verification

1. **Specific Issue Fixed**:
   - Original issue no longer reproduces
   - No regression in related features

2. **System Stable**:

   ```bash
   # All health checks pass
   npm run test:health:production

   # Error rate normal
   railway run python scripts/monitor_health.py --duration=10m
   ```

3. **Performance Normal**:
   - Response times unchanged
   - No memory leaks introduced
   - Database queries efficient

## Rollback Procedure

If hotfix causes issues:

```bash
# 1. Immediate rollback
PREVIOUS_DEPLOYMENT=$(cat rollback_point.txt | grep ID | awk '{print $2}')
railway deployments rollback $PREVIOUS_DEPLOYMENT

# 2. Verify rollback
railway status
curl --fail https://api.lafactoria.com/health

# 3. Communicate
echo "⚠️ Hotfix rolled back at $(date)" | \
  railway run python scripts/notify_team.py
```

## Communication Templates

### Pre-Deployment

```
🚨 HOTFIX ALERT
Issue: [Brief description]
Impact: [User impact]
Fix: Ready to deploy
ETA: 15 minutes
Contact: @[your-name]
```

### During Deployment

```
🔄 HOTFIX IN PROGRESS
Started: [Time]
Status: [Current step]
ETA: [Minutes remaining]
```

### Success

```
✅ HOTFIX COMPLETE
Issue: Resolved
Duration: [X] minutes
Verification: All systems normal
Follow-up: Post-mortem scheduled
```

### Rollback

```
⚠️ HOTFIX ROLLED BACK
Reason: [Why rollback needed]
Status: Previous version restored
Impact: [Current state]
Next: Investigating alternative fix
```

## Post-Hotfix Actions

### Immediate

- [ ] Verify fix holding stable (30 min)
- [ ] Document in incident log
- [ ] Notify affected users (if any)
- [ ] Update status page

### Within 24 Hours

- [ ] Create proper PR with full tests
- [ ] Schedule post-mortem
- [ ] Update monitoring for issue
- [ ] Document lessons learned

### Post-Mortem Questions

1. Why wasn't this caught before production?
2. Can we add tests to prevent recurrence?
3. Is our monitoring adequate?
4. Was the hotfix process efficient?

## Hotfix Guidelines

### Do's

- ✅ Keep changes minimal
- ✅ Test specific issue thoroughly
- ✅ Communicate constantly
- ✅ Document everything
- ✅ Have rollback ready

### Don'ts

- ❌ Bundle multiple fixes
- ❌ Skip any testing
- ❌ Deploy without monitoring
- ❌ Forget to merge back
- ❌ Rush without thinking

## Common Hotfix Scenarios

### Scenario 1: API 500 Errors

```python
# Common fix: Missing error handling
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    return error_response(500, "Service temporarily unavailable")
```

### Scenario 2: Database Deadlock

```sql
-- Add timeout to prevent deadlocks
SET lock_timeout = '5s';
-- Or adjust query order
```

### Scenario 3: Memory Leak

```python
# Common fix: Clear large objects
large_data = None  # Clear reference
gc.collect()  # Force garbage collection
```

## Related Documentation

- [Production Deployment](production-deploy.md)
- [Emergency Rollback](rollback.md)
- Incident Response (see relevant docs section)
- Post-Mortem Process (see relevant docs section)
