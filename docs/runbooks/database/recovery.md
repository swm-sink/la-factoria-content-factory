# Database Recovery Procedures

**Severity**: P1 (Critical)  
**Time Estimate**: 30-120 minutes  
**Last Updated**: 2025-07-31  
**Owner**: Database Team  
**Related SLO**: Data Durability 99.999%

## Summary

Procedures for recovering the database from various failure scenarios including corruption, data loss, or complete failure. This runbook covers point-in-time recovery, full restore from backup, selective table recovery, and emergency failover procedures. Expected outcome is complete data recovery with minimal downtime and data loss.

## Symptoms

- [ ] Database not responding
- [ ] Data corruption detected
- [ ] Accidental data deletion
- [ ] Hardware/infrastructure failure
- [ ] Ransomware or security incident

## Alert References

- **Alert Name**: `database-failure`
- **Dashboard**: Database Health
- **Runbook Trigger**: Database unavailable or data integrity issues

## Prerequisites

- Database admin credentials
- Access to backup storage
- Railway CLI access
- Recovery environment ready
- Communication channels ready

## Recovery Scenarios

### Scenario 1: Connection Issues Only

If database is running but connections failing, see [Connection Issues Runbook](connection-issues.md)

### Scenario 2: Data Corruption

Partial data corruption, database still accessible

### Scenario 3: Complete Database Failure

Database completely inaccessible or corrupted

### Scenario 4: Accidental Data Deletion

Specific data deleted, need point-in-time recovery

## Initial Assessment (5-10 minutes)

### Step 1: Determine Failure Type

```bash
# Try to connect
railway run psql $DATABASE_URL -c "SELECT version();"

# If connection succeeds, check data integrity
railway run python scripts/check_data_integrity.py

# Check database logs
railway logs --service postgres --tail 100 | grep -E "ERROR|FATAL|PANIC"

# Check for corruption
railway run psql $DATABASE_URL -c "
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

### Step 2: Stop Write Traffic

```bash
# Enable read-only mode immediately
railway env set READ_ONLY_MODE=true
railway env set MAINTENANCE_MODE=true
railway restart

# Verify no writes happening
railway run psql $DATABASE_URL -c "
SELECT count(*) FROM pg_stat_activity
WHERE state = 'active'
  AND query NOT LIKE '%SELECT%';"
```

## Resolution Steps

### Recovery Procedures

### Procedure A: Point-in-Time Recovery (30-60 minutes)

**Use when**: Need to recover to specific time before issue

```bash
# 1. Identify recovery point
railway run python scripts/list_recovery_points.py --last=24h

# 2. Select target time (before incident)
RECOVERY_TIME="2024-01-31 10:00:00"

# 3. Create new database for recovery
railway run createdb temp_recovery_db

# 4. Restore to point in time
railway run pg_restore \
  --dbname=temp_recovery_db \
  --clean \
  --if-exists \
  --no-owner \
  --no-acl \
  backups/base_backup.dump

# 5. Apply WAL logs up to recovery time
railway run python scripts/apply_wal_to_time.py \
  --database=temp_recovery_db \
  --target-time="$RECOVERY_TIME"

# 6. Verify recovered data
railway run psql temp_recovery_db -c "
SELECT count(*) FROM critical_table;
-- Run data verification queries
"
```

### Procedure B: Full Restore from Backup (45-90 minutes)

**Use when**: Complete database failure or corruption

```bash
# 1. List available backups
railway run python scripts/list_backups.py --last=7

# 2. Select most recent valid backup
BACKUP_FILE="la_factoria_backup_20240131_020000.dump"

# 3. Verify backup integrity
railway run pg_restore --list backups/$BACKUP_FILE > /dev/null
if [ $? -eq 0 ]; then
    echo "Backup valid"
else
    echo "Backup corrupted! Try next backup"
fi

# 4. Create fresh database
railway run dropdb $DATABASE_NAME --if-exists
railway run createdb $DATABASE_NAME

# 5. Restore from backup
railway run pg_restore \
  --dbname=$DATABASE_NAME \
  --verbose \
  --no-owner \
  --no-acl \
  --jobs=4 \
  backups/$BACKUP_FILE

# 6. Verify restoration
railway run psql $DATABASE_NAME -c "
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';"
```

### Procedure C: Selective Table Recovery (20-40 minutes)

**Use when**: Only specific tables corrupted/deleted

```bash
# 1. Identify affected tables
AFFECTED_TABLES="users,content,flashcards"

# 2. Create temporary database
railway run createdb temp_restore_db

# 3. Restore only affected tables
for table in ${AFFECTED_TABLES//,/ }; do
    railway run pg_restore \
      --dbname=temp_restore_db \
      --table=$table \
      --data-only \
      backups/latest_backup.dump
done

# 4. Copy recovered data back
for table in ${AFFECTED_TABLES//,/ }; do
    railway run psql $DATABASE_URL -c "
    BEGIN;
    TRUNCATE TABLE $table CASCADE;
    INSERT INTO $table
    SELECT * FROM dblink('dbname=temp_restore_db',
                        'SELECT * FROM $table')
    AS t(LIKE $table);
    COMMIT;"
done

# 5. Drop temporary database
railway run dropdb temp_restore_db
```

### Procedure D: Emergency Failover (15-30 minutes)

**Use when**: Primary database completely failed

```bash
# 1. Promote read replica (if available)
railway run python scripts/promote_replica.py --confirm

# 2. Update connection strings
railway env set DATABASE_URL=$REPLICA_DATABASE_URL
railway restart

# 3. Verify new primary
railway run psql $DATABASE_URL -c "SELECT pg_is_in_recovery();"
# Should return 'false' for primary

# 4. Configure new replica (later)
railway run python scripts/setup_new_replica.py
```

## Data Validation

### Post-Recovery Validation Steps

```bash
# 1. Check row counts
railway run python scripts/validate_row_counts.py \
  --compare-with=pre_incident_counts.json

# 2. Run integrity checks
railway run python scripts/data_integrity_check.py --full

# 3. Verify foreign key constraints
railway run psql $DATABASE_URL -c "
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE contype = 'f'
  AND NOT convalidated;"

# 4. Check sequences
railway run python scripts/fix_sequences.py --check

# 5. Application-level validation
railway run python scripts/validate_business_logic.py
```

## Gradual Traffic Restoration

### Step 1: Test with Synthetic Traffic

```bash
# Run test transactions
railway run python scripts/test_database_operations.py

# Monitor for errors
railway logs --tail -f | grep -E "ERROR|database"
```

### Step 2: Enable Read Traffic

```bash
# Allow reads but not writes
railway env set READ_ONLY_MODE=true
railway env set MAINTENANCE_MODE=false
railway restart

# Monitor performance
railway metrics database --last 10m
```

### Step 3: Enable Full Traffic

```bash
# Restore full access
railway env set READ_ONLY_MODE=false
railway restart

# Watch closely
watch -n 5 'railway run python scripts/monitor_database.py'
```

## Communication During Recovery

### Initial Alert

```
🚨 DATABASE RECOVERY IN PROGRESS
Status: Assessing damage
Impact: All services affected
ETA: Determining based on recovery type
Updates: Every 15 minutes
```

### Progress Updates

```
UPDATE [Time elapsed]:
✓ Backup identified and validated
✓ Recovery in progress (X% complete)
⏳ Estimated completion: [time]
```

### Completion Notice

```
✅ DATABASE RECOVERY COMPLETE
Duration: X hours
Data Status: [Full recovery/Partial loss]
Services: Resuming normal operation
Follow-up: Post-mortem scheduled
```

## Disaster Recovery Testing

### Monthly DR Drill

```bash
# 1. Create test environment
railway run python scripts/create_dr_test_env.py

# 2. Simulate failure
railway run python scripts/simulate_db_failure.py --scenario=corruption

# 3. Execute recovery
# Follow this runbook

# 4. Validate results
railway run python scripts/validate_dr_test.py

# 5. Document results
railway run python scripts/generate_dr_report.py
```

## Prevention Measures

### Backup Verification

```bash
# Daily backup test restore
railway run python scripts/test_restore_daily.py

# Weekly full validation
railway run python scripts/validate_all_backups.py
```

### Monitoring Setup

```bash
# Corruption detection
railway env set DB_CORRUPTION_CHECK=true
railway env set DB_CHECKSUM=on

# Replication monitoring
railway env set REPLICATION_LAG_ALERT=60
```

## Recovery Metrics

Track these metrics:

- Time to detect failure
- Time to begin recovery
- Total recovery time
- Data loss (if any)
- Service downtime

## Post-Recovery Actions

- [ ] Verify all data recovered
- [ ] Run full application test suite
- [ ] Update backup strategy
- [ ] Schedule post-mortem
- [ ] Document lessons learned
- [ ] Test monitoring alerts
- [ ] Review and update runbook

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

- [Backup Procedures](backup.md)
- Database Monitoring (see relevant docs section)
- Disaster Recovery Plan (see relevant docs section)
- Data Integrity Testing (see relevant docs section)
