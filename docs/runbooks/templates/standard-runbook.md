# [Issue/Operation Name]

**Severity**: P[1-4]  
**Time Estimate**: X minutes  
**Last Updated**: YYYY-MM-DD  
**Owner**: [Team/Person]  
**Related SLO**: [Link to relevant SLO]

## Summary

Brief description of what this runbook addresses.

## Symptoms

- [ ] Symptom 1 (e.g., API returns 500 errors)
- [ ] Symptom 2 (e.g., Response time > 5s)
- [ ] Symptom 3 (e.g., Database connection timeouts)

## Alert References

- **Alert Name**: [Name in monitoring system]
- **Dashboard**: [Link to relevant dashboard]
- **Runbook Trigger**: [What triggers this runbook]

## Prerequisites

- Access to production environment
- SSH keys for servers
- Database credentials (if needed)
- Required tools: `kubectl`, `psql`, etc.

## Initial Assessment (2-5 minutes)

1. Check service health:

   ```bash
   curl https://api.lafactoria.com/health
   ```

2. Review recent deployments:

   ```bash
   git log --oneline -10
   ```

3. Check system resources:

   ```bash
   kubectl top pods -n production
   ```

## Resolution Steps

### Step 1: [Action Name] (X minutes)

**Goal**: What this step accomplishes

```bash
# Command to execute
command --with-options
```

**Expected Output**:

```
Expected result here
```

### Step 2: [Action Name] (X minutes)

**Goal**: What this step accomplishes

```bash
# Command to execute
command --with-options
```

**Checkpoint**: Verify progress before continuing

### Step 3: [Action Name] (X minutes)

**Goal**: What this step accomplishes

```bash
# Command to execute
command --with-options
```

## Verification

1. Confirm service is healthy:

   ```bash
   curl https://api.lafactoria.com/health
   ```

2. Check metrics have returned to normal:
   - [ ] Error rate < 1%
   - [ ] Response time < 500ms
   - [ ] No active alerts

3. Run smoke tests:

   ```bash
   npm run test:smoke
   ```

## Rollback Procedure

If the issue persists or worsens:

1. Revert recent changes:

   ```bash
   kubectl rollback deployment/api -n production
   ```

2. Restore from backup (if data-related):

   ```bash
   ./scripts/restore_backup.sh --timestamp=XXXXX
   ```

3. Escalate to senior engineer

## Post-Incident Actions

- [ ] Update monitoring alerts
- [ ] Create post-mortem document
- [ ] Update this runbook with learnings
- [ ] Schedule review meeting

## Related Documentation

- [Architecture Documentation](/docs/ARCHITECTURE.md)
- [SLA Documentation](/docs/sla.md)
- [Monitoring Setup](/docs/monitoring/observability.md)
- Previous incidents: [Link to post-mortems]

## Notes

Additional context, gotchas, or special considerations.
