# Slow API Response - Performance Troubleshooting

**Severity**: P2 (High)  
**Time Estimate**: 15-30 minutes  
**Last Updated**: 2025-07-31  
**Owner**: Platform Team  
**Related SLO**: 95th percentile response time < 500ms

## Summary

API response times exceeding acceptable thresholds, causing poor user experience. This runbook helps diagnose and resolve performance issues including slow database queries, resource constraints, and inefficient code patterns. Expected outcome is to restore response times below 500ms p95 threshold and improve overall system performance.

## Symptoms

- [ ] Response times > 1s for simple endpoints
- [ ] Response times > 5s for content generation
- [ ] User reports of slow loading
- [ ] Timeout errors increasing

## Alert References

- **Alert Name**: `api-response-time-high`
- **Dashboard**: Performance Dashboard
- **Runbook Trigger**: p95 response time > 1s for 5 minutes

## Prerequisites

- Railway CLI access with production permissions
- Database query access (psql)
- Python scripts directory access
- Performance monitoring dashboard access
- Understanding of application architecture

## Initial Assessment (3-5 minutes)

1. **Identify slow endpoints**:

   ```bash
   # Extract and sort response times by endpoint to find slowest operations
   # Fields: $NF = response time, $(NF-2) = endpoint path
   railway logs --tail 1000 | grep "response_time" | \
     awk '{print $NF, $(NF-2)}' | sort -rn | head -20
   ```

2. **Check system resources**:

   ```bash
   # Check CPU usage trends for resource constraints
   railway metrics cpu --last 1h

   # Check memory usage for potential memory pressure
   railway metrics memory --last 1h

   # Analyze database performance metrics and connection stats
   railway run python scripts/check_db_performance.py
   ```

3. **Identify bottlenecks**:

   ```bash
   # Identify slow database queries causing performance issues
   # Shows queries with mean execution time > 100ms
   railway run psql $DATABASE_URL -c "
   SELECT query, mean_exec_time, calls
   FROM pg_stat_statements
   WHERE mean_exec_time > 100
   ORDER BY mean_exec_time DESC
   LIMIT 10;"
   ```

## Resolution Steps

### Step 1: Quick Wins (5-10 minutes)

**Goal**: Implement immediate optimizations

```bash
# 1. Enable response caching to reduce backend load
railway env set CACHE_ENABLED=true
railway env set CACHE_TTL=300  # 5 minutes cache

# 2. Increase connection pool
railway env set DATABASE_POOL_SIZE=50

# 3. Enable query result caching
railway env set QUERY_CACHE_ENABLED=true

# Apply changes
railway restart
```

### Step 2: Database Optimization (10-15 minutes)

**Goal**: Fix database performance issues

```bash
# 1. Update PostgreSQL table statistics for better query planning
railway run psql $DATABASE_URL -c "ANALYZE;"

# 2. Check for missing indexes
railway run python scripts/analyze_missing_indexes.py

# 3. Add critical indexes
railway run psql $DATABASE_URL -c "
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_user_created
ON content(user_id, created_at);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_flashcards_content
ON flashcards(content_id);"

# 4. Check for table bloat
railway run psql $DATABASE_URL -c "
SELECT schemaname, tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

### Step 3: Application Optimization (10-20 minutes)

**Goal**: Optimize application code

```bash
# 1. Enable production optimizations for better performance
railway env set NODE_ENV=production
railway env set PYTHONOPTIMIZE=2  # Enable Python optimizations

# 2. Adjust worker settings
railway env set WEB_CONCURRENCY=4
railway env set WORKER_CONNECTIONS=1000

# 3. Enable response compression
railway env set COMPRESSION_ENABLED=true
railway env set COMPRESSION_LEVEL=6

# 4. Optimize JSON serialization
railway env set ORJSON_ENABLED=true

railway restart
```

### Step 4: External Service Optimization

**Goal**: Reduce external API latency

```bash
# 1. Enable HTTP connection pooling to reduce latency
railway env set HTTP_CONNECTION_POOL_SIZE=100
railway env set HTTP_KEEPALIVE=true  # Reuse connections

# 2. Optimize Gemini API calls
railway env set GEMINI_BATCH_SIZE=10
railway env set GEMINI_PARALLEL_REQUESTS=5
railway env set GEMINI_CACHE_RESPONSES=true

# 3. Optimize ElevenLabs calls
railway env set ELEVENLABS_QUEUE_ENABLED=true
railway env set ELEVENLABS_BATCH_PROCESSING=true

railway restart
```

## Performance Analysis Tools

### APM Profiling

```python
# Profile specific slow endpoint to identify bottlenecks
railway run python scripts/profile_endpoint.py /api/content/generate

# Analyze results
railway run python scripts/analyze_profile.py
```

### Database Query Analysis

```sql
-- Find slow queries
SELECT
  query,
  calls,
  mean_exec_time as avg_ms,
  max_exec_time as max_ms,
  total_exec_time/calls as total_ms
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### Memory Profiling

```bash
# Run memory profiler to detect potential memory leaks
railway run python scripts/memory_profile.py

# Garbage collection stats
railway run python -c "
import gc
print(f'Collections: {gc.get_count()}')
print(f'Objects: {len(gc.get_objects())}')
"
```

## Optimization Patterns

### 1. N+1 Query Issues

```python
# Bad: N+1 queries
for content in contents:
    user = User.query.get(content.user_id)  # N queries

# Good: Eager loading
contents = Content.query.options(joinedload(Content.user)).all()
```

### 2. Missing Pagination

```python
# Bad: Loading all records
all_content = Content.query.all()

# Good: Paginated queries
page = Content.query.paginate(page=1, per_page=20)
```

### 3. Inefficient Serialization

```python
# Bad: Manual serialization
data = {
    'id': content.id,
    'title': content.title,
    # ... many fields
}

# Good: Optimized serialization
from app.serializers import ContentSerializer
data = ContentSerializer(content).data
```

## Verification

1. **Response time improvement**:

   ```bash
   # Test response times after optimizations - should see improvement
   for i in {1..10}; do
     time curl -s --fail https://api.lafactoria.com/api/content/list > /dev/null
     sleep 1
   done
   # Target: < 500ms for list endpoint
   ```

2. **Load test**:

   ```bash
   # Run quick load test to verify performance under load
   npm run test:load:quick
   # Expected: All requests complete within SLO
   ```

3. **Check metrics**:
   - p95 response time < 500ms
   - p99 response time < 1000ms
   - No timeout errors

## Long-term Optimizations

1. **Implement CDN**:

   ```bash
   railway env set CDN_ENABLED=true
   railway env set CDN_URL=https://cdn.lafactoria.com
   ```

2. **Database Read Replicas**:

   ```bash
   railway env set READ_REPLICA_URL=$READ_DB_URL
   railway env set USE_READ_REPLICA=true
   ```

3. **Redis Caching**:

   ```bash
   railway env set REDIS_URL=$REDIS_URL
   railway env set CACHE_BACKEND=redis
   ```

## Post-Incident Actions

- [ ] Profile slow endpoints
- [ ] Review database queries
- [ ] Implement missing indexes
- [ ] Add performance tests
- [ ] Update monitoring thresholds

## Related Documentation

- Performance Best Practices (see docs/performance/)
- Database Optimization Guide (see docs/database/)
- Caching Strategy Guide (see docs/)
- Load Testing Guide (see docs/testing/)
