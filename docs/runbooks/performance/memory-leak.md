# Memory Leak Detection and Resolution

**Severity**: P2 (High)  
**Time Estimate**: 20-45 minutes  
**Last Updated**: 2025-07-31  
**Owner**: Platform Team  
**Related SLO**: Memory Usage < 80%

## Summary

Procedures for detecting, diagnosing, and resolving memory leaks in the La Factoria application. Expected outcome is to resolve the issue and restore normal service operation.

## Symptoms

- [ ] Steadily increasing memory usage over time
- [ ] Application crashes with OOM (Out of Memory)
- [ ] Performance degradation as memory fills
- [ ] Frequent garbage collection pauses
- [ ] Container restarts due to memory limits

## Alert References

- **Alert Name**: `high-memory-usage`
- **Dashboard**: Memory Usage Dashboard
- **Runbook Trigger**: Memory usage > 85% for 10+ minutes

## Prerequisites

- Railway CLI access
- Python memory profiling tools
- Understanding of application architecture
- Access to application metrics

## Initial Assessment (5-10 minutes)

### Step 1: Confirm Memory Leak Pattern

```bash
# Check memory trend over time
railway metrics memory --last 24h

# Look for:
# - Continuous upward trend
# - Sawtooth pattern (GC not fully clearing)
# - Sudden spikes

# Get current memory stats
railway run python -c "
import psutil
import gc
proc = psutil.Process()
print(f'RSS Memory: {proc.memory_info().rss / 1024 / 1024:.2f} MB')
print(f'Python Objects: {len(gc.get_objects())}')
print(f'GC Stats: {gc.get_stats()}')
"
```

### Step 2: Identify Affected Components

```bash
# Check memory by process
railway run ps aux --sort=-%mem | head -10

# Python memory breakdown
railway run python scripts/memory_snapshot.py

# Check for large objects
railway run python -c "
import sys
import gc
for obj in gc.get_objects():
    size = sys.getsizeof(obj)
    if size > 1000000:  # Objects > 1MB
        print(f'{type(obj)}: {size / 1024 / 1024:.2f} MB')
"
```

## Resolution Steps

### Step 1: Force Garbage Collection (Quick Fix) (2-3 minutes)

**Goal**: Temporary relief while investigating

```bash
# Force full garbage collection
railway run python -c "
import gc
print('Before GC:', len(gc.get_objects()))
collected = gc.collect(2)  # Full collection
print(f'Collected {collected} objects')
print('After GC:', len(gc.get_objects()))
"

# Clear caches
railway run python scripts/clear_all_caches.py

# Monitor impact
railway metrics memory --last 10m
```

### Step 2: Identify Memory Leak Source (10-20 minutes)

**Goal**: Find what's holding memory

```bash
# 1. Enable memory profiling
railway env set MEMORY_PROFILING=true
railway env set TRACEMALLOC=true
railway restart

# 2. Take memory snapshots
railway run python scripts/memory_profile.py --snapshot start

# Wait 5-10 minutes for leak to manifest
sleep 600

# Take second snapshot
railway run python scripts/memory_profile.py --snapshot end

# 3. Compare snapshots
railway run python scripts/memory_profile.py --compare start end
```

Common leak sources to check:

```python
# Check for circular references
railway run python -c "
import gc
gc.set_debug(gc.DEBUG_LEAK)
gc.collect()
# Check gc.garbage for uncollectable objects
print(f'Uncollectable objects: {len(gc.garbage)}')
"

# Check cache sizes
railway run python -c "
from app.core.cache import cache
print(f'Cache entries: {len(cache._cache)}')
print(f'Cache memory: {cache.memory_usage()} MB')
"

# Check database connections
railway run python -c "
from app.db import engine
print(f'Pool size: {engine.pool.size()}')
print(f'Checked out: {engine.pool.checkedout()}')
"
```

### Step 3: Apply Targeted Fixes (10-20 minutes)

**Goal**: Fix identified memory leaks

#### Fix 1: Clear Large Collections

```python
# Add to problematic endpoints
def cleanup_large_data():
    global large_cache
    large_cache.clear()
    gc.collect()

# Or use weak references
import weakref
cache = weakref.WeakValueDictionary()
```

#### Fix 2: Fix Circular References

```python
# Break circular references
def cleanup_handler():
    self.parent = None
    self.callbacks = []
```

#### Fix 3: Limit Cache Sizes

```bash
# Set cache limits
railway env set CACHE_MAX_SIZE=1000
railway env set CACHE_TTL=300
railway env set LRU_CACHE_MAXSIZE=500

# Apply settings
railway restart
```

#### Fix 4: Fix Connection Leaks

```python
# Ensure connections are closed
from contextlib import closing

with closing(get_connection()) as conn:
    # Use connection
    pass  # Connection auto-closed
```

### Step 4: Deploy Fix and Monitor (5-10 minutes)

**Goal**: Ensure leak is resolved

```bash
# 1. Deploy fix
railway up

# 2. Monitor memory usage
watch -n 30 'railway metrics memory --last 30m'

# 3. Verify leak stopped
railway run python scripts/verify_memory_stable.py --duration=15m
```

## Memory Leak Patterns

### Pattern 1: Cache Growth

**Symptoms**: Steadily growing cache
**Fix**: Implement LRU eviction

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_operation(key):
    return compute_result(key)
```

### Pattern 2: Event Listeners

**Symptoms**: Accumulating callbacks
**Fix**: Remove listeners properly

```python
# Bad
emitter.on('event', callback)

# Good
emitter.on('event', callback)
# Later...
emitter.off('event', callback)
```

### Pattern 3: Global Lists/Dicts

**Symptoms**: Growing global collections
**Fix**: Use bounded collections

```python
from collections import deque

# Bad
results = []
results.append(new_result)

# Good
results = deque(maxlen=1000)
results.append(new_result)
```

### Pattern 4: File Handles

**Symptoms**: Too many open files
**Fix**: Use context managers

```python
# Bad
f = open('file.txt')
data = f.read()

# Good
with open('file.txt') as f:
    data = f.read()
```

## Monitoring and Prevention

### Memory Monitoring Setup

```bash
# Enable detailed memory tracking
railway env set MEMORY_TRACK_ALLOCATIONS=true
railway env set MEMORY_PROFILE_INTERVAL=300
railway env set MEMORY_ALERT_THRESHOLD=80

# Add memory health endpoint
railway run python scripts/add_memory_endpoint.py
```

### Prevention Checklist

- [ ] Use context managers for resources
- [ ] Implement cache size limits
- [ ] Clear large objects after use
- [ ] Avoid global mutable state
- [ ] Profile memory in CI/CD

## Emergency Actions

If memory critically high:

### Option 1: Restart Workers

```bash
# Rolling restart to avoid downtime
railway scale --replicas 3
sleep 30
railway restart --rolling
sleep 60
railway scale --replicas 2
```

### Option 2: Reduce Memory Usage

```bash
# Reduce worker concurrency
railway env set WEB_CONCURRENCY=2

# Reduce cache sizes
railway env set CACHE_EMERGENCY_MODE=true

# Disable memory-intensive features
railway env set FEATURE_HEAVY_PROCESSING=false

railway restart
```

### Option 3: Increase Memory Limit

```bash
# Temporary increase while fixing
railway env set MEMORY_LIMIT=2048
railway restart
```

## Post-Incident Actions

- [ ] Document leak source and fix
- [ ] Add memory leak tests
- [ ] Update monitoring thresholds
- [ ] Review similar code patterns
- [ ] Schedule memory profiling

## Memory Profiling Tools

### Built-in Python Tools

```python
# tracemalloc
import tracemalloc
tracemalloc.start()
# ... code ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

# memory_profiler
from memory_profiler import profile

@profile
def memory_intensive_function():
    pass
```

### Custom Memory Report

```bash
# Execute command in production environment
railway run python scripts/generate_memory_report.py \
  --output=memory_report.html \
  --include-graphs
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

- Performance Optimization (see relevant docs section)
- Monitoring Setup (see relevant docs section)
- Python Best Practices (see relevant docs section)
- Container Resource Limits (see relevant docs section)
