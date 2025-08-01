# Runbook Standards and Guidelines

## Overview

This document defines the standards and best practices for creating and maintaining runbooks in the La Factoria platform. All runbooks must follow these guidelines to ensure consistency and effectiveness during operational incidents.

## Runbook Philosophy

1. **Actionable**: Every step must be executable
2. **Tested**: All procedures must be validated
3. **Clear**: No ambiguity in instructions
4. **Complete**: Cover all common scenarios
5. **Current**: Regular updates required

## Structure Requirements

### 1. Header Section

Every runbook MUST include:

```markdown
# [Clear, Descriptive Title]

**Severity**: P[1-4] (Critical/High/Medium/Low)
**Time Estimate**: X-Y minutes
**Last Updated**: YYYY-MM-DD
**Owner**: [Team Name]
**Related SLO**: [Link to relevant SLO/SLA]
```

### 2. Summary Section

- Brief description of the issue/procedure
- When to use this runbook
- Expected outcome

### 3. Symptoms/Triggers

- Checkbox list of observable symptoms
- Alert names that trigger this runbook
- User reports that indicate this issue

### 4. Prerequisites

- Required access levels
- Tools needed
- Environmental requirements
- Knowledge prerequisites

### 5. Resolution Steps

- Numbered, sequential steps
- Each step includes:
  - Goal statement
  - Exact commands to run
  - Expected output
  - What to do if step fails

### 6. Verification

- How to confirm the issue is resolved
- Metrics to check
- Tests to run

### 7. Related Documentation

- Links to architecture docs
- Related runbooks
- Post-mortem reports

## Writing Style Guide

### Do's

- ✅ Use exact commands with full paths
- ✅ Include expected output examples
- ✅ Provide copy-paste ready commands
- ✅ Add time estimates for each major step
- ✅ Include rollback procedures
- ✅ Use consistent formatting

### Don'ts

- ❌ Use vague instructions like "check the logs"
- ❌ Assume knowledge without stating prerequisites
- ❌ Skip error handling scenarios
- ❌ Use relative paths or aliases
- ❌ Forget to test procedures

## Command Examples

### Good Example

```bash
# Check API health endpoint
curl -f https://api.lafactoria.com/health --max-time 5

# Expected output:
# {"status": "healthy", "version": "1.2.3", "timestamp": "2024-01-31T10:00:00Z"}
```

### Bad Example

```bash
# Check if API is working
curl api/health
```

## Severity Levels

### P1 - Critical (Response: Immediate)

- Complete service outage
- Data loss risk
- Security breach
- Revenue impact

### P2 - High (Response: < 30 minutes)

- Partial service degradation
- Performance issues affecting users
- Failed deployments
- High error rates

### P3 - Medium (Response: < 2 hours)

- Non-critical feature issues
- Scheduled maintenance
- Minor performance degradation
- Configuration changes

### P4 - Low (Response: Next business day)

- Documentation updates
- Non-urgent optimizations
- Cleanup tasks
- Research tasks

## Testing Requirements

### Before Publishing

1. Execute every command in staging
2. Verify all links work
3. Time the entire procedure
4. Have someone else follow the runbook
5. Update based on feedback

### Testing Checklist

```bash
# Run validation script
python scripts/validate_runbooks.py --file=<runbook-path>

# Checks performed:
# - All commands are executable
# - Expected outputs match reality
# - Time estimates are accurate
# - Links are valid
# - Format compliance
```

## Maintenance Schedule

### Weekly

- Review runbooks used in past week
- Update any outdated commands
- Fix broken links

### Monthly

- Test critical (P1) runbooks
- Review metrics and improve
- Update time estimates

### Quarterly

- Full runbook audit
- Archive obsolete runbooks
- Training on new runbooks

## Metrics and Quality

### Track for Each Runbook

- Usage frequency
- Success rate
- Time to resolution
- User feedback
- Last tested date

### Quality Metrics

```python
# Runbook effectiveness score
score = (successful_uses / total_uses) * 100

# Target metrics:
# - Success rate > 90%
# - Average resolution time < estimated time
# - User satisfaction > 4/5
```

## Integration with Monitoring

### Alert Integration

```yaml
# monitoring/alerts.yaml
alert: HighErrorRate
annotations:
  runbook_url: https://docs.lafactoria.com/runbooks/incident-response/high-error-rate.md
  severity: P2
  estimated_time: 15m
```

### Dashboard Links

- Every dashboard should link to relevant runbooks
- Runbooks should link back to dashboards
- Use consistent URL structure

## Review Process

### New Runbook

1. Author creates PR with runbook
2. Technical review by senior engineer
3. Test execution by different team member
4. Operations team approval
5. Merge and announce

### Updates

1. Any team member can propose updates
2. Changes require one approval
3. Major changes need re-testing
4. Update version and date

## Templates

### Standard Runbook Template

Located at: `/docs/runbooks/templates/standard-runbook.md`

### Quick Decision Tree

Located at: `/docs/runbooks/templates/decision-tree.md`

### Post-Mortem Template

Located at: `/docs/templates/post-mortem.md`

## Common Patterns

### 1. Service Restart Pattern

```bash
# 1. Check current state
railway status

# 2. Graceful restart
railway restart --no-downtime

# 3. Verify service healthy
curl https://api.lafactoria.com/health

# 4. Check logs for errors
railway logs --tail 100 | grep ERROR
```

### 2. Debug Information Collection

```bash
# Collect comprehensive debug info
railway run python scripts/collect_debug_info.py > debug_$(date +%Y%m%d_%H%M%S).log

# Always includes:
# - Service status
# - Recent logs
# - Resource usage
# - Configuration
# - Recent changes
```

### 3. Progressive Remediation

1. Try least invasive fix first
2. Escalate to more aggressive fixes
3. Always have rollback ready
4. Document what worked

## Anti-Patterns to Avoid

### 1. Vague Instructions

❌ "Check if the database is working properly"
✅ "Execute: `psql $DATABASE_URL -c 'SELECT 1'` - Expected: `1` returned"

### 2. Missing Error Handling

❌ "Run the migration script"
✅ "Run migration: `./migrate.sh`. If fails with 'locked', wait 30s and retry"

### 3. Assumed Context

❌ "In the API directory..."
✅ "Navigate to `/app/api` directory..."

### 4. No Verification

❌ "Restart the service"
✅ "Restart service and verify with health check showing 'healthy'"

## Contributing

To contribute a new runbook:

1. Use the standard template
2. Follow all guidelines in this document
3. Test thoroughly in staging
4. Submit PR with reviewers
5. Update index after merge

Questions? Contact the Platform Team.
