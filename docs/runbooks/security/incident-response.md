# Security Incident Response

**Severity**: P1 (Critical)  
**Time Estimate**: 30-60 minutes  
**Last Updated**: 2025-07-31  
**Owner**: Security Team  
**Related SLO**: Security Incident Response < 15 minutes

## Summary

Procedures for responding to security incidents including breaches, vulnerabilities, and suspicious activities. This runbook provides immediate containment actions, investigation steps, and recovery procedures for various security threats. Expected outcome is rapid incident containment, evidence preservation, and restoration of secure operations.

## Symptoms

- [ ] Unauthorized access detected
- [ ] API key compromise
- [ ] SQL injection attempts
- [ ] Suspicious user activity
- [ ] Data breach suspected
- [ ] DDoS attack
- [ ] Unusual traffic patterns
- [ ] Failed authentication spikes

## Alert References

- **Alert Name**: `security-incident-detected`
- **Dashboard**: Security Dashboard
- **Runbook Trigger**: Security alerts from monitoring or manual report

## Prerequisites

- Security team access credentials
- Railway CLI with admin permissions
- Access to security monitoring tools
- Incident response toolkit ready
- Communication channels prepared
- Legal/compliance contacts available

## Resolution Steps

### IMMEDIATE ACTIONS (First 5 minutes)

### Step 1: Assess and Contain

```bash
# 1. Enable security mode - limits access
railway env set SECURITY_MODE=true
railway env set RATE_LIMIT_STRICT=true
railway restart

# 2. Block suspicious IPs
railway run python scripts/block_ips.py --suspicious

# 3. Rotate potentially compromised keys
railway run python scripts/rotate_api_keys.py --emergency
```

### Step 2: Preserve Evidence

```bash
# Capture current state
railway logs --tail 10000 > "security_incident_$(date +%Y%m%d_%H%M%S).log"

# Backup database state
railway run python scripts/emergency_backup.py --security-incident

# Export access logs
railway run python scripts/export_access_logs.py --last-24h
```

## Investigation Steps

### Step 1: Identify Attack Vector (10-15 minutes)

**For Unauthorized Access**:

```bash
# Check authentication logs
railway logs --tail 1000 | grep -E "auth|login|token" | grep -i "fail\|error\|unauthorized"

# Review API key usage
railway run python scripts/audit_api_keys.py --suspicious-activity

# Check for privilege escalation
railway run psql $DATABASE_URL -c "
SELECT user_id, role, updated_at
FROM user_roles
WHERE updated_at > NOW() - INTERVAL '24 hours'
ORDER BY updated_at DESC;"
```

**For SQL Injection**:

```bash
# Search for SQL patterns in logs
railway logs --tail 5000 | grep -iE "union.*select|sleep\(|benchmark\(|';|--"

# Check for unusual queries
railway run python scripts/analyze_query_logs.py --sql-injection-patterns
```

**For API Abuse**:

```bash
# Identify high-volume users
railway run python scripts/api_usage_analysis.py --threshold=1000

# Check for scraping patterns
railway logs --tail 1000 | awk '/api/ {print $1}' | sort | uniq -c | sort -rn | head -20
```

### Step 2: Determine Impact (10-15 minutes)

```bash
# Check data access
railway run psql $DATABASE_URL -c "
SELECT
  table_name,
  user_name,
  query,
  query_start
FROM pg_stat_activity
JOIN information_schema.tables ON true
WHERE query_start > NOW() - INTERVAL '2 hours'
ORDER BY query_start DESC;"

# Audit data modifications
railway run python scripts/audit_data_changes.py --last-24h

# Check for data exfiltration
railway run python scripts/check_data_export.py --suspicious
```

## Containment Procedures

### For API Key Compromise

```bash
# 1. Revoke compromised keys
railway run python scripts/revoke_api_keys.py --keys="key1,key2"

# 2. Generate new keys for affected users
railway run python scripts/generate_new_keys.py --affected-users

# 3. Notify affected users
railway run python scripts/send_security_notification.py --template=key-rotation
```

### For Active Attack

```bash
# 1. Enable DDoS protection
railway env set DDOS_PROTECTION=true
railway env set RATE_LIMIT_PER_IP=10

# 2. Block attacking IPs
railway run python scripts/block_ips.py --from-logs --threshold=100

# 3. Enable CAPTCHA
railway env set CAPTCHA_ENABLED=true
railway env set CAPTCHA_THRESHOLD=3

railway restart
```

### For Data Breach

```bash
# 1. Isolate affected systems
railway env set READ_ONLY_MODE=true

# 2. Snapshot current state
railway run python scripts/create_forensic_snapshot.py

# 3. Begin breach protocol
railway run python scripts/initiate_breach_protocol.py
```

## Recovery Steps

### Step 1: Patch Vulnerabilities (15-30 minutes)

```bash
# Apply security patches
npm audit fix --force
pip install --upgrade -r requirements.txt

# Update dependencies
railway run python scripts/security_patch.py

# Deploy patches
railway up
```

### Step 2: Restore Normal Operations

```bash
# Gradually restore access
railway env set SECURITY_MODE=false
railway env set RATE_LIMIT_STRICT=false

# Remove IP blocks (after review)
railway run python scripts/unblock_ips.py --reviewed

# Re-enable full functionality
railway env set READ_ONLY_MODE=false
railway restart
```

## Communication Templates

### Initial Alert

```
SECURITY INCIDENT: [Type of incident]
Status: Investigating
Impact: [Estimated impact]
Actions: Security team responding
Next Update: 15 minutes
```

### User Notification (if needed)

```
Security Notice: [Brief description]
Impact: [What users should know]
Action Required: [Any user action needed]
More Info: [Link to status page]
```

### All-Clear

```
RESOLVED: Security incident contained
Duration: [Time]
Impact: [Final assessment]
Actions Taken: [Summary]
Follow-up: [Next steps]
```

## Security Checklist

### During Incident

- [ ] Incident commander assigned
- [ ] Evidence preserved
- [ ] Attack vector identified
- [ ] Impact assessed
- [ ] Containment applied
- [ ] Communication sent

### Post-Incident

- [ ] Vulnerabilities patched
- [ ] Security scan completed
- [ ] Logs analyzed
- [ ] Report written
- [ ] Procedures updated
- [ ] Team debriefed

## Compliance Requirements

1. **Notification Timeline**:
   - Internal: Immediate
   - Users: Within 72 hours if data affected
   - Authorities: As required by law

2. **Documentation**:
   - Incident timeline
   - Systems affected
   - Data potentially accessed
   - Remediation steps
   - Preventive measures

3. **Audit Trail**:

   ```bash
   # Generate compliance report
   railway run python scripts/generate_security_report.py \
     --incident-id=$INCIDENT_ID \
     --format=compliance
   ```

## Prevention Measures

1. **Regular Security Scans**:

   ```bash
   # Weekly automated scans
   npm audit
   safety check
   bandit -r app/
   ```

2. **Access Reviews**:

   ```bash
   # Monthly access audit
   railway run python scripts/audit_user_access.py
   ```

3. **Security Training**:
   - Quarterly security reviews
   - Incident response drills
   - Security awareness updates

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

- Security Best Practices (see relevant docs section)
- API Security Guide (see relevant docs section)
- Data Protection Policy (see relevant docs section)
- Incident Post-Mortem Template (see relevant docs section)
