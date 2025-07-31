# Connection Pooling Strategy

## Overview

This document describes the connection pooling implementation for Redis and Firestore in La Factoria, designed to improve performance through connection reuse and efficient resource management.

## Architecture

### Core Components

1. **Base Connection Pool (`app/core/connection_pool.py`)**
   - Abstract base class for all connection pools
   - Provides health monitoring, automatic recovery, and metrics
   - Implements connection lifecycle management
   - Supports configurable pool sizes and idle timeouts

2. **Redis Pool (`app/utils/redis_pool.py`)**
   - Implements Redis-specific connection pooling
   - Configured for high throughput (20 max connections)
   - Optimized for caching operations
   - Provides convenience functions for common operations

3. **Firestore Pool (`app/utils/firestore_pool.py`)**
   - Implements Firestore-specific connection pooling
   - Configured for moderate throughput (10 max connections)
   - Optimized for document operations
   - Maintains backward compatibility with existing code

4. **Connection Monitor (`app/middleware/connection_monitor.py`)**
   - Monitors pool health and performance
   - Exports Prometheus metrics
   - Provides real-time connection statistics

## Configuration

### Pool Sizes

Configured in `app/core/config/connection_config.py`:

```python
# Redis Pool Configuration
redis_pool = PoolConfig(
    min_size=5,          # Minimum connections to maintain
    max_size=20,         # Maximum connections allowed
    max_idle_time=600,   # 10 minutes idle before closing
    health_check_interval=30,  # Health check every 30 seconds
)

# Firestore Pool Configuration
firestore_pool = PoolConfig(
    min_size=2,          # Minimum connections to maintain
    max_size=10,         # Maximum connections allowed
    max_idle_time=300,   # 5 minutes idle before closing
    health_check_interval=60,  # Health check every 60 seconds
)
```

### Environment-Specific Settings

- **Production**: Higher pool sizes (Redis: 50, Firestore: 20)
- **Staging**: Moderate pool sizes (Redis: 20, Firestore: 10)
- **Development**: Lower pool sizes (Redis: 20, Firestore: 10)

## Features

### 1. Connection Reuse
- Connections are returned to the pool after use
- Subsequent requests reuse existing connections
- Reduces connection overhead significantly

### 2. Health Monitoring
- Periodic health checks on all idle connections
- Automatic removal of unhealthy connections
- Replacement with new healthy connections

### 3. Automatic Recovery
- Failed connections are automatically replaced
- Pool maintains minimum size through auto-recovery
- Graceful handling of connection errors

### 4. Performance Monitoring
- Real-time metrics via Prometheus
- Connection usage statistics
- Pool utilization tracking

### 5. Resource Management
- Enforces maximum connection limits
- Removes stale connections automatically
- Prevents connection leaks

## Usage Examples

### Redis Operations

```python
from app.utils.redis_pool import redis_get, redis_set, get_redis_pool

# Simple operations using pooled connections
await redis_set("key", "value", ex=3600)
value = await redis_get("key")

# Direct pool access for advanced operations
pool = await get_redis_pool()
async with PooledConnectionContext(pool) as conn:
    # Use connection for multiple operations
    pipe = conn.pipeline()
    pipe.set("key1", "value1")
    pipe.set("key2", "value2")
    await pipe.execute()
```

### Firestore Operations

```python
from app.utils.firestore_pool import get_firestore_pool

# Using backward-compatible functions
doc = await get_document_from_firestore("doc_id", "collection")

# Direct pool access
pool = await get_firestore_pool()
docs = await pool.query_documents(
    collection="jobs",
    filters=[("status", "==", "PENDING")],
    limit=10
)
```

## Metrics

### Prometheus Metrics

- `connection_pool_size`: Current pool size by state (idle/active/total)
- `connection_pool_wait_seconds`: Time waiting for connections
- `connection_pool_errors_total`: Connection errors by type
- `connection_pool_health_checks_total`: Health check results
- `connection_usage_seconds`: Connection usage duration
- `connection_pool_utilization`: Pool utilization percentage

### Health Endpoints

Access pool statistics via:
- GET `/api/v1/admin/connection-pools` - Detailed pool statistics
- Prometheus metrics at `/metrics`

## Performance Benefits

Based on validation tests:

1. **Redis Performance**
   - ~40-60% improvement in operation throughput
   - Reduced latency for cache operations
   - Better handling of concurrent requests

2. **Firestore Performance**
   - Consistent operation times
   - Reduced connection setup overhead
   - Better batch operation performance

3. **Resource Efficiency**
   - Lower memory usage through connection reuse
   - Reduced CPU overhead from connection setup
   - Better scalability under load

## Best Practices

1. **Use Pooled Functions**
   - Always use the provided pooled functions
   - Avoid creating direct connections

2. **Handle Errors Gracefully**
   - Pool operations may fail during recovery
   - Implement appropriate retry logic

3. **Monitor Pool Health**
   - Watch pool utilization metrics
   - Adjust pool sizes based on usage patterns

4. **Clean Shutdown**
   - Pools are automatically closed on app shutdown
   - Ensures clean resource cleanup

## Troubleshooting

### High Pool Utilization
- Increase max_size in configuration
- Check for connection leaks
- Review operation efficiency

### Connection Errors
- Check network connectivity
- Verify service credentials
- Review health check logs

### Performance Issues
- Monitor pool wait times
- Check for pool exhaustion
- Review concurrent operation patterns

## Migration Notes

The implementation maintains backward compatibility:
- Existing code continues to work unchanged
- New code benefits from pooling automatically
- Gradual migration possible

## Future Improvements

1. **Dynamic Pool Sizing**
   - Auto-adjust pool size based on load
   - Predictive scaling

2. **Advanced Monitoring**
   - Connection lifetime tracking
   - Detailed performance analytics

3. **Circuit Breaker Integration**
   - Automatic service degradation
   - Fallback mechanisms