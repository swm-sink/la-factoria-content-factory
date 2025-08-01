# High Error Rate - Incident Response

**Severity**: P2 (High)  
**Time Estimate**: 10-20 minutes  
**Last Updated**: 2025-07-31  
**Owner**: Platform Team  
**Related SLO**: Error Rate < 1%

## Summary

API experiencing elevated error rates affecting user experience. Service is partially available but degraded. This runbook helps identify root causes of high error rates and provides step-by-step resolution for common issues including database problems, memory exhaustion, and external service failures. Expected outcome is to reduce error rate below 1% SLO threshold and restore normal operations.

## Symptoms

- [ ] Error rate > 5% for 5+ minutes
- [ ] Mix of 500, 502, 503 errors
- [ ] Some requests succeed, others fail
- [ ] User reports of intermittent failures

## Alert References

- **Alert Name**: `api-error-rate-high`
- **Dashboard**: Error Rate Dashboard
- **Runbook Trigger**: 5XX error rate > 5% for 5 minutes

## Prerequisites

- Access to logs and monitoring
- Database query access
- Ability to modify rate limits

## Initial Assessment (2-3 minutes)

1. Identify error patterns:

   ```bash
   # Get error distribution by type to identify most common errors
   # Field $4 should contain error type/code
   railway logs --tail 1000 | grep -E "ERROR|CRITICAL" | \
     awk '{print $4}' | sort | uniq -c | sort -rn | head -10
   ```

2. Check specific error types:

   ```bash
   # Search for database-related errors (connection pool, query failures)
   railway logs --tail 500 | grep -i "database\|connection\|pool"

   # Look for timeout errors indicating slow operations
   railway logs --tail 500 | grep -i "timeout\|deadline"

   # Check for memory errors or out-of-memory kills
   railway logs --tail 500 | grep -i "memory\|oom"
   ```

3. Identify affected endpoints:

   ```bash
   # Extract and count API endpoints with errors to find problem areas
   railway logs --tail 1000 | grep "ERROR" | \
     grep -oE "/(api/[^\"? ]+)" | sort | uniq -c | sort -rn
   ```

## Resolution Steps

### Step 1: Mitigate Load (2-5 minutes)

**Goal**: Reduce pressure on failing components

```bash
# Enable rate limiting to reduce load on failing components
railway env set RATE_LIMIT_ENABLED=true
railway env set RATE_LIMIT_REQUESTS=100  # requests per hour

# Increase cache TTL to reduce backend calls
railway env set CACHE_TTL=300  # 5 minutes

# Apply configuration changes with rolling restart
railway restart
```

### Step 2: Address Database Issues (5-10 minutes)

**Goal**: Fix common database problems

```bash
# Check current database connection pool usage and limits
railway run python scripts/check_db_connections.py

# If connections exhausted:
railway env set DATABASE_POOL_SIZE=50
railway env set DATABASE_MAX_OVERFLOW=10
railway restart

# Clear stale connections
railway run python scripts/reset_db_pool.py
```

### Step 3: Fix Memory Issues (5-10 minutes)

**Goal**: Address memory-related errors

```bash
# Review memory usage trends over last hour
railway metrics memory --last 1h

# If memory pressure:
# 1. Force garbage collection
railway run python scripts/force_gc.py

# 2. Restart workers
railway restart --no-downtime

# 3. Scale horizontally if needed
railway scale --replicas 2
```

### Step 4: Handle External Service Failures

**Goal**: Mitigate third-party issues

```bash
# Check external service health status
curl --fail https://status.google.com/api  # Gemini API status
curl --fail https://api.elevenlabs.io/health  # ElevenLabs status

# If external service down:
railway env set GEMINI_TIMEOUT=30
railway env set ELEVENLABS_TIMEOUT=30
railway env set ENABLE_FALLBACK_MODE=true
railway restart
```

## Targeted Fixes

### For Gemini API Errors

```bash
# Reduce Gemini load
railway env set GEMINI_RATE_LIMIT=10
railway env set GEMINI_RETRY_COUNT=1
railway env set GEMINI_CACHE_ENABLED=true
```

### For Database Timeouts

```bash
# Optimize slow queries
railway run python scripts/analyze_slow_queries.py

# Increase timeouts temporarily
railway env set DATABASE_TIMEOUT=30
```

### For Memory Exhaustion

```bash
# Reduce worker memory usage
railway env set WEB_CONCURRENCY=2
railway env set MAX_CONTENT_SIZE=100000
```

## Verification

1. Monitor error rate decline:

   ```bash
   # Monitor error count in real-time, should decrease after fixes
   watch -n 5 'railway logs --tail 100 | grep -c ERROR'
   # Target: Count should drop below 1 per 100 logs
   ```

2. Test affected endpoints:

   ```bash
   # Run smoke tests to verify critical functionality restored
   npm run test:api:smoke
   # Expected: All tests pass
   ```

3. Verify metrics improving:
   - Error rate returning to < 1%
   - Response times normalizing
   - No new error patterns

## Escalation Triggers

Escalate if:

- Error rate > 10% for 10+ minutes
- Data corruption detected
- Security-related errors
- Cannot identify root cause

## Communication Template

**Initial Alert**:

```
ISSUE: Elevated API error rate detected
Current Rate: X%
Impact: Intermittent failures for some users
Status: Engineering team investigating
```

**Updates**:

```
UPDATE: Error rate [improving/stable/worsening]
Current Rate: X%
Identified Cause: [cause]
Actions Taken: [list]
ETA for resolution: [time]
```

## Common Error Patterns

### 1. Database Connection Exhaustion

- **Pattern**: "connection pool exhausted"
- **Fix**: Increase pool size, check for leaks

### 2. Memory Pressure

- **Pattern**: Worker crashes, OOM kills
- **Fix**: Scale horizontally, reduce memory usage

### 3. External API Failures

- **Pattern**: Timeout errors from Gemini/ElevenLabs
- **Fix**: Enable caching, increase timeouts

### 4. Rate Limit Hit

- **Pattern**: 429 errors from external services
- **Fix**: Implement backoff, reduce request rate

## Post-Incident Actions

- [ ] Analyze error patterns
- [ ] Update monitoring thresholds
- [ ] Review error handling code
- [ ] Update dependencies if needed
- [ ] Document new error patterns

## Related Documentation

- Performance Tuning Guide (see docs/performance/)
- Database Optimization Guide (see docs/database/)
- External Service Integration (see docs/api/)
- Error Handling Best Practices (see docs/developer/)
