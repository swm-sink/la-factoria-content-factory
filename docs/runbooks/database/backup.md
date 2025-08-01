# Database Backup Procedures

**Severity**: P3 (Scheduled) / P1 (Emergency)  
**Time Estimate**: 15-30 minutes  
**Last Updated**: 2025-07-31  
**Owner**: Database Team  
**Related SLO**: Backup Success Rate 99.9%

## Summary

Procedures for creating, verifying, and managing database backups for disaster recovery and data protection. This runbook covers scheduled, on-demand, and emergency backup procedures. Expected outcome is successful backup creation with verified integrity and proper storage.

## Symptoms

- Scheduled backup needed before maintenance
- Emergency backup required during incident
- Regular backup verification needed
- Backup restoration required

## Backup Types

- **Scheduled**: Automated daily backups
- **On-Demand**: Before major deployments
- **Emergency**: During incidents
- **Point-in-Time**: For specific recovery needs

## Prerequisites

- Database admin access
- Sufficient storage space
- Backup credentials
- Railway CLI access

## Resolution Steps

### Scheduled Backup Procedure

### Daily Automated Backup (Runs at 2 AM UTC)

```bash
# Verify scheduled backup completed
railway run python scripts/check_backup_status.py --date=today

# Check backup integrity
railway run python scripts/verify_backup.py --latest

# Confirm backup uploaded to storage
railway run python scripts/list_backups.py --last=7
```

### On-Demand Backup Procedure

### Step 1: Pre-Backup Checks (2-3 minutes)

```bash
# Check database size
railway run psql $DATABASE_URL -c "
SELECT pg_database_size('la_factoria')/1024/1024 as size_mb;"

# Check available storage
railway run python scripts/check_storage_space.py

# Verify no long-running transactions
railway run psql $DATABASE_URL -c "
SELECT pid, state, query_start, query
FROM pg_stat_activity
WHERE state != 'idle'
  AND query_start < NOW() - INTERVAL '10 minutes';"
```

### Step 2: Create Backup (10-20 minutes)

```bash
# Generate backup filename
BACKUP_NAME="la_factoria_backup_$(date +%Y%m%d_%H%M%S)"

# Method 1: Using pg_dump (Recommended)
railway run pg_dump $DATABASE_URL \
  --format=custom \
  --verbose \
  --no-owner \
  --no-acl \
  --clean \
  --if-exists \
  > backups/${BACKUP_NAME}.dump

# Method 2: Using backup script
railway run python scripts/create_backup.py \
  --name=$BACKUP_NAME \
  --compress=true \
  --encrypt=true
```

### Step 3: Verify Backup (5-10 minutes)

```bash
# Check backup file integrity
railway run pg_restore --list backups/${BACKUP_NAME}.dump | head -20

# Verify backup size is reasonable
ls -lh backups/${BACKUP_NAME}.dump

# Test restore to temporary database
railway run python scripts/test_restore.py \
  --backup=backups/${BACKUP_NAME}.dump \
  --test-db=test_restore_db
```

### Step 4: Upload to Storage (5-10 minutes)

```bash
# Upload to S3/R2
railway run python scripts/upload_backup.py \
  --file=backups/${BACKUP_NAME}.dump \
  --bucket=la-factoria-backups \
  --encrypt=true

# Verify upload
railway run python scripts/verify_s3_backup.py \
  --name=${BACKUP_NAME}.dump
```

### Emergency Backup Procedure

For critical situations requiring immediate backup:

```bash
# 1. Enable read-only mode to ensure consistency
railway env set READ_ONLY_MODE=true
railway restart

# 2. Create emergency backup
EMERGENCY_BACKUP="emergency_$(date +%Y%m%d_%H%M%S)"
railway run pg_dump $DATABASE_URL --format=custom --jobs=4 \
  > backups/${EMERGENCY_BACKUP}.dump &

# 3. Monitor progress
watch -n 10 'ls -lh backups/${EMERGENCY_BACKUP}.dump'

# 4. Once complete, disable read-only mode
railway env set READ_ONLY_MODE=false
railway restart
```

### Point-in-Time Recovery Setup

### Enable WAL Archiving

```bash
# Configure continuous archiving
railway env set POSTGRES_WAL_ARCHIVE=true
railway env set POSTGRES_ARCHIVE_COMMAND='cp %p /archives/%f'

# Verify WAL archiving
railway run psql $DATABASE_URL -c "
SELECT name, setting
FROM pg_settings
WHERE name IN ('wal_level', 'archive_mode', 'archive_command');"
```

### Create PITR Backup

```bash
# Start backup
railway run psql $DATABASE_URL -c "SELECT pg_start_backup('pitr_backup');"

# Copy data directory
railway run python scripts/copy_data_directory.py

# Stop backup
railway run psql $DATABASE_URL -c "SELECT pg_stop_backup();"
```

## Backup Rotation Policy

### Retention Schedule

- **Daily backups**: Keep for 7 days
- **Weekly backups**: Keep for 4 weeks  
- **Monthly backups**: Keep for 12 months
- **Yearly backups**: Keep for 5 years

### Cleanup Old Backups

```bash
# Run cleanup script
railway run python scripts/cleanup_old_backups.py \
  --dry-run  # Remove flag to actually delete

# Manual cleanup
railway run python scripts/list_backups.py --older-than=30d
# Review list, then:
railway run python scripts/delete_backups.py --older-than=30d --confirm
```

## Backup Monitoring

### Health Checks

```bash
# Check backup job status
railway run python scripts/backup_health_check.py

# Alert on failures
railway env set BACKUP_ALERT_EMAIL=ops@lafactoria.com
railway env set BACKUP_ALERT_SLACK=true
```

### Metrics to Monitor

- Backup duration trend
- Backup size growth
- Success/failure rate
- Storage usage

## Restore Testing

### Monthly Restore Test

```bash
# 1. Select random backup from last month
BACKUP_TO_TEST=$(railway run python scripts/select_random_backup.py --month=last)

# 2. Restore to test environment
railway run python scripts/restore_to_test.py \
  --backup=$BACKUP_TO_TEST \
  --target=test-db

# 3. Verify data integrity
railway run python scripts/verify_restored_data.py \
  --source=production \
  --target=test-db

# 4. Document results
echo "Restore test completed: $(date)" >> restore_tests.log
```

## Troubleshooting

### Issue: Backup Taking Too Long

```bash
# Use parallel backup
railway run pg_dump $DATABASE_URL \
  --format=directory \
  --jobs=4 \
  --verbose \
  -f backups/parallel_backup/

# Or exclude large tables
railway run pg_dump $DATABASE_URL \
  --exclude-table=audit_logs \
  --exclude-table=temp_data
```

### Issue: Storage Space Issues

```bash
# Compress existing backups
railway run python scripts/compress_backups.py --older-than=7d

# Move to cold storage
railway run python scripts/archive_to_glacier.py --older-than=30d
```

### Issue: Backup Corruption

```bash
# Verify backup integrity
railway run pg_restore --list $BACKUP_FILE > /dev/null
if [ $? -ne 0 ]; then
  echo "Backup corrupted!"
  # Create new backup immediately
fi
```

## Security Considerations

### Encryption

```bash
# Encrypt backup files
railway run openssl enc -aes-256-cbc \
  -in backup.dump \
  -out backup.dump.enc \
  -k $BACKUP_ENCRYPTION_KEY

# Decrypt when needed
railway run openssl enc -d -aes-256-cbc \
  -in backup.dump.enc \
  -out backup.dump \
  -k $BACKUP_ENCRYPTION_KEY
```

### Access Control

- Limit backup access to authorized personnel
- Use separate credentials for backup operations
- Audit backup access logs regularly

## Documentation

### Backup Log Entry Template

```
Date: YYYY-MM-DD HH:MM:SS
Type: [Scheduled/On-Demand/Emergency]
Size: X GB
Duration: X minutes
Location: s3://bucket/path
Verified: [Yes/No]
Notes: [Any issues or special circumstances]
```

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

- [Database Recovery Procedures](recovery.md)
- Disaster Recovery Plan (see relevant docs section)
- Database Maintenance (see relevant docs section)
- Storage Management (see relevant docs section)
