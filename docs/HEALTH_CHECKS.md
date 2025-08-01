# Health Check Documentation

## Overview

La Factoria provides comprehensive health check endpoints to monitor the service status, dependencies, and system resources. These endpoints are designed to work with Kubernetes/Cloud Run health probes and monitoring systems.

## Health Check Endpoints

### 1. Root Health Endpoints

#### `/healthz` - Simple Liveness Check

- **Purpose**: Basic liveness probe for load balancers and orchestrators
- **Authentication**: None (public access)
- **Response**: 200 OK if service is alive

```json
{
  "status": "healthy",
  "uptime_seconds": 3600.5
}
```

#### `/health` - Basic Health Status

- **Purpose**: Quick health check for monitoring systems
- **Authentication**: None (public access)
- **Response**: 200 OK if ready, includes readiness status

```json
{
  "status": "healthy",
  "ready": true,
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### 2. Detailed Health Endpoints

#### `/health/live` - Liveness Probe

- **Purpose**: Kubernetes/Cloud Run liveness probe
- **Authentication**: None
- **Response**: Always 200 OK if service is running

```json
{
  "status": "alive",
  "timestamp": "2024-01-20T10:30:00Z",
  "uptime_seconds": 3600.5
}
```

#### `/health/ready` - Readiness Probe

- **Purpose**: Kubernetes/Cloud Run readiness probe
- **Authentication**: None
- **Response**:
  - 200 OK if ready to serve traffic
  - 503 Service Unavailable if critical dependencies are down

```json
{
  "ready": true,
  "timestamp": "2024-01-20T10:30:00Z",
  "components": {
    "redis": "ready",
    "firestore": "ready"
  }
}
```

#### `/health/` - Component Health Summary

- **Purpose**: Overview of all component health statuses
- **Authentication**: None
- **Response**: 200 OK (degraded) or 503 (unhealthy)

```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00Z",
  "uptime_seconds": 3600.5,
  "version": "1.0.0",
  "environment": "production",
  "components": [
    {
      "name": "Redis",
      "status": "healthy",
      "latency_ms": 5.2,
      "last_check": "2024-01-20T10:30:00Z"
    },
    {
      "name": "Firestore",
      "status": "healthy",
      "latency_ms": 12.5,
      "last_check": "2024-01-20T10:30:00Z"
    },
    {
      "name": "Vertex AI",
      "status": "healthy",
      "latency_ms": 150.3,
      "last_check": "2024-01-20T10:30:00Z"
    }
  ],
  "resources": {
    "cpu_percent": 45.5,
    "memory_percent": 62.3,
    "memory_available_mb": 1024.5,
    "disk_percent": 75.0,
    "disk_available_gb": 50.2,
    "open_connections": 125
  }
}
```

#### `/health/detailed` - Comprehensive Health Check

- **Purpose**: Detailed health information for debugging
- **Authentication**: None
- **Query Parameters**:
  - `include_metrics` (bool): Include performance metrics
  - `check_dependencies` (bool): Check external dependencies
- **Response**: Full health status with all details

### 3. Component-Specific Health Checks

#### `/health/components/{component_name}`

- **Purpose**: Check specific component health
- **Components**: `redis`, `firestore`, `vertex_ai`, `resources`
- **Response**: Component-specific health data

Example for Redis:

```json
{
  "component": "redis",
  "result": {
    "status": "healthy",
    "latency_ms": 5.2,
    "details": {
      "pool_stats": {
        "current_size": 5,
        "available": 3,
        "in_use": 2,
        "waiting": 0
      },
      "test_successful": true
    }
  }
}
```

## Health Status Levels

### 1. **Healthy** (HTTP 200)

- All critical components operational
- System resources within normal ranges
- Service fully functional

### 2. **Degraded** (HTTP 200)

- Non-critical components down (e.g., Vertex AI)
- High resource usage (>90% memory/disk)
- Service operational but with reduced capabilities

### 3. **Unhealthy** (HTTP 503)

- Critical components down (Redis, Firestore)
- Service cannot handle requests properly
- Immediate intervention required

## Component Health Checks

### Redis Health Check

- Tests connection pool availability
- Performs test SET/GET operation
- Monitors pool statistics
- Timeout: 5 seconds

### Firestore Health Check

- Tests connection pool availability
- Performs minimal query operation
- Monitors pool statistics
- Timeout: 10 seconds

### Vertex AI Health Check

- Tests API connectivity
- Sends minimal test prompt
- Validates response received
- Timeout: 30 seconds

### System Resources Check

- CPU usage percentage
- Memory usage and availability
- Disk usage and free space
- Open network connections

## Health Monitoring Middleware

The `HealthMonitoringMiddleware` automatically tracks dependency health based on request patterns:

- Monitors success/failure rates for each dependency
- Updates health status based on error thresholds
- Provides real-time dependency health metrics

### Dependency Patterns

- **Redis**: Monitored on all API endpoints
- **Firestore**: Monitored on job, content, and feedback endpoints
- **Vertex AI**: Monitored on content generation endpoints

### Error Thresholds

- Redis/Firestore: 5 errors in 60 seconds
- Vertex AI: 3 errors in 300 seconds

## Integration with Monitoring Systems

### Kubernetes/Cloud Run Configuration

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 5
```

### Prometheus Metrics

Health metrics are exposed via Prometheus:

- `dependency_redis_healthy` (gauge)
- `dependency_firestore_healthy` (gauge)
- `dependency_vertex_ai_healthy` (gauge)
- `dependency_*_success_rate` (gauge)
- `dependency_*_latency_ms` (gauge)

### Alert Configuration

Example alert for API health:

```yaml
- alert: APIDown
  expr: up{job="la-factoria"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "API is down"
    runbook: "runbooks/incident-response/api-down.md"
```

## Best Practices

### 1. Health Check Frequency

- Liveness: Every 10 seconds
- Readiness: Every 5 seconds
- Detailed health: On-demand or every 60 seconds

### 2. Timeout Configuration

- Liveness probe: 5 seconds
- Readiness probe: 5 seconds
- Detailed health: 30 seconds

### 3. Dependency Checks

- Use connection pools for efficiency
- Implement circuit breakers for external services
- Cache health status briefly (5-60 seconds)

### 4. Resource Thresholds

- CPU: Alert at 80%, critical at 90%
- Memory: Alert at 85%, critical at 95%
- Disk: Alert at 85%, critical at 95%

## Troubleshooting

### Common Issues

1. **Readiness Failing**
   - Check Redis connectivity
   - Verify Firestore authentication
   - Review connection pool stats

2. **High Latency**
   - Check network connectivity
   - Review connection pool configuration
   - Monitor external API response times

3. **Resource Exhaustion**
   - Check for memory leaks
   - Review connection pool sizes
   - Monitor request patterns

### Debug Commands

```bash
# Check all health endpoints
curl http://localhost:8000/health/detailed?include_metrics=true

# Check specific component
curl http://localhost:8000/health/components/redis

# Validate all health checks
python scripts/validate_health_checks.py http://localhost:8000
```

## Validation Script

Use the validation script to test all health endpoints:

```bash
python scripts/validate_health_checks.py [BASE_URL]
```

The script will:

- Test all health endpoints
- Validate response formats
- Check response times
- Verify health monitoring behavior
- Report any failures

## Security Considerations

1. **No Authentication**: Health endpoints are public by design
2. **Limited Information**: No sensitive data in responses
3. **Rate Limiting**: Applied to prevent abuse
4. **Resource Protection**: Lightweight checks to avoid DoS
