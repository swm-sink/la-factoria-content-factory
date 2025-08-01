# Database Connection Issues

**Severity**: P1 (Critical)  
**Time Estimate**: 5-15 minutes  
**Last Updated**: 2025-07-31  
**Owner**: Platform Team  
**Related SLO**: Database Availability 99.9%

## Summary

Database connection failures preventing API from serving requests. Critical issue affecting all database-dependent operations. This runbook helps diagnose and resolve PostgreSQL connection issues including pool exhaustion, timeouts, and connection leaks. Expected outcome is to restore database connectivity and normal API operations.

## Symptoms

- [ ] "connection refused" or "connection timeout" errors
- [ ] "connection pool exhausted" messages
- [ ] API health check fails with database errors
- [ ] Slow queries leading to timeouts

## Alert References

- **Alert Name**: `database-connection-failure`
- **Dashboard**: Database Health Dashboard
- **Runbook Trigger**: Connection failures > 10% for 2 minutes

## Prerequisites

- PostgreSQL client access
- Database credentials
- Railway CLI access
- Direct database server access (for emergencies)

## Initial Assessment (1-2 minutes)

1. Test direct database connectivity:

   ```bash
   # Test direct database connectivity from API container
   # Expected: returns "1" if connection successful
   railway run psql $DATABASE_URL -c "SELECT 1"

   # Check current active connection count against max_connections limit
   railway run psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity"
   ```

2. Check connection pool status:

   ```bash
   # Search recent logs for connection pool related errors
   railway logs --tail 100 | grep -i "pool\|connection"

   # Get current connection pool metrics to identify exhaustion
   # Pool size: configured pool size
   # Checked out: connections currently in use
   # Overflow: extra connections beyond pool size
   railway run python -c "
   from app.db import engine
   print(f'Pool size: {engine.pool.size()}')
   print(f'Checked out: {engine.pool.checkedout()}')
   print(f'Overflow: {engine.pool.overflow()}')
   "
   ```

3. Verify database server status:

   ```bash
   # Verify database server is up and accepting connections
   # Expected: "accepting connections" message
   railway run pg_isready -h $DB_HOST -p $DB_PORT
   ```

## Resolution Steps

### Step 1: Reset Connection Pool (2-3 minutes)

**Goal**: Clear stale connections

```bash
# Force disconnect all database connections to clear stale/stuck connections
railway run python scripts/reset_db_connections.py

# Or manually:
railway run psql $DATABASE_URL -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'la_factoria'
  AND pid <> pg_backend_pid()
  AND state = 'idle'
  AND state_change < NOW() - INTERVAL '5 minutes';
"

# Restart API to reset pool
railway restart
```

### Step 2: Increase Connection Limits (3-5 minutes)

**Goal**: Handle connection exhaustion

```bash
# Check current PostgreSQL max_connections setting
# Compare with active connections from step 1
railway run psql $DATABASE_URL -c "SHOW max_connections"

# Increase pool size temporarily
railway env set DATABASE_POOL_SIZE=100
railway env set DATABASE_MAX_OVERFLOW=20
railway env set DATABASE_POOL_TIMEOUT=30

# Apply changes
railway restart
```

### Step 3: Identify Connection Leaks (5-10 minutes)

**Goal**: Find and fix connection leaks

```bash
# List all active connections with details to identify problematic queries
# Shows: process ID, username, application, client IP, state, duration, current query
railway run psql $DATABASE_URL -c "
SELECT
  pid,
  usename,
  application_name,
  client_addr,
  state,
  state_change,
  query
FROM pg_stat_activity
WHERE datname = 'la_factoria'
ORDER BY state_change;
"

# Kill long-running idle connections
railway run psql $DATABASE_URL -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'la_factoria'
  AND state = 'idle'
  AND state_change < NOW() - INTERVAL '10 minutes';
"
```

### Step 4: Emergency Database Restart (10-15 minutes)

**Goal**: Last resort recovery

```bash
# WARNING: This will disconnect all users - use only as last resort
# Only proceed if all other steps have failed

# 1. Enable maintenance mode to prevent new connections
railway env set MAINTENANCE_MODE=true

# 2. Gracefully stop connections
railway run psql $DATABASE_URL -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'la_factoria';
"

# 3. Restart database (Railway managed)
# Contact Railway support if needed

# 4. Restart application
railway restart

# 5. Disable maintenance mode
railway env set MAINTENANCE_MODE=false
```

## Connection Pool Optimization

### Quick Fixes

```bash
# For high traffic
railway env set DATABASE_POOL_SIZE=50
railway env set DATABASE_POOL_RECYCLE=300  # 5 minutes

# For connection timeouts
railway env set DATABASE_CONNECT_TIMEOUT=30
railway env set DATABASE_COMMAND_TIMEOUT=30

# For better resilience
railway env set DATABASE_POOL_PRE_PING=true
railway env set DATABASE_ECHO_POOL=true  # Enable logging
```

### Connection Monitoring

```sql
-- Current connection usage
SELECT
  count(*) as total,
  state,
  count(*) * 100.0 / (SELECT setting::int FROM pg_settings WHERE name='max_connections') as percentage
FROM pg_stat_activity
GROUP BY state;

-- Connections per user
SELECT
  usename,
  count(*) as connections,
  array_agg(DISTINCT application_name) as applications
FROM pg_stat_activity
GROUP BY usename
ORDER BY connections DESC;
```

## Verification

1. Test database connectivity:

   ```bash
   railway run python -c "
   from app.db import engine
   with engine.connect() as conn:
       result = conn.execute('SELECT 1')
       print('Database connected successfully')
   "
   ```

2. Monitor connection pool:

   ```bash
   # Monitor connection pool metrics in real-time
   # Watch for pool size, overflow, and timeout messages
   watch -n 5 'railway logs --tail 20 | grep -i pool'
   ```

3. Run health checks:

   ```bash
   # Check API health endpoint - should return healthy status
   curl --fail https://api.lafactoria.com/health
   # Expected: {"status": "healthy", "database": "connected"}
   ```

## Prevention Measures

1. **Connection Pool Tuning**:

   ```python
   # Optimal settings for Railway
   DATABASE_POOL_SIZE = 20  # Per worker
   DATABASE_MAX_OVERFLOW = 10
   DATABASE_POOL_TIMEOUT = 30
   DATABASE_POOL_RECYCLE = 300
   ```

2. **Query Optimization**:

   ```bash
   # Find slow queries that may be holding connections
   # Shows query text, average execution time, and call count
   railway run psql $DATABASE_URL -c "
   SELECT
     query,
     mean_time/1000 as mean_ms,
     calls
   FROM pg_stat_statements
   ORDER BY mean_time DESC
   LIMIT 10;
   "
   ```

3. **Connection Monitoring**:

   ```bash
   # Configure monitoring alerts for connection count thresholds
   # Sets alerts at 80% and 90% of max_connections
   railway run python scripts/setup_db_monitoring.py
   ```

## Post-Incident Actions

- [ ] Review connection pool settings
- [ ] Audit code for connection leaks
- [ ] Implement connection pooling best practices
- [ ] Add connection metrics to dashboard
- [ ] Update database capacity planning

## Related Documentation

- Database Optimization Guide (see docs/database/)
- Connection Pooling Best Practices (see docs/database/)
- PostgreSQL Tuning Guide (see docs/database/)
- Performance Monitoring Setup (see docs/monitoring/)
