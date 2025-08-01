# Monitoring Setup Guide

This document describes the monitoring infrastructure for La Factoria, including Prometheus metrics collection, Grafana dashboards, and alerting configuration.

## Overview

The monitoring stack consists of:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert routing and notifications
- **Node Exporter**: System metrics collection
- **Redis Exporter**: Redis metrics collection
- **Blackbox Exporter**: Endpoint monitoring

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   La Factoria   │────▶│  Prometheus  │────▶│   Grafana   │
│      API        │     │              │     │             │
│  /metrics       │     └──────┬───────┘     └─────────────┘
└─────────────────┘            │
                               ▼
┌─────────────────┐     ┌──────────────┐
│ Node Exporter   │────▶│ Alertmanager │
└─────────────────┘     └──────────────┘
                               │
┌─────────────────┐            ▼
│ Redis Exporter  │     ┌──────────────┐
└─────────────────┘     │Notifications │
                        │ (Slack, PD)  │
                        └──────────────┘
```

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- La Factoria API running on port 8000
- Redis running on port 6379 (if using Redis)

### 2. Start the Monitoring Stack

```bash
cd monitoring
docker-compose up -d
```

This will start:

- Prometheus on <http://localhost:9090>
- Grafana on <http://localhost:3001> (login: admin/admin)
- Alertmanager on <http://localhost:9093>
- Node Exporter on <http://localhost:9100>
- Redis Exporter on <http://localhost:9121>

### 3. Verify Installation

Run the validation script:

```bash
./scripts/validate_monitoring.py
```

## Metrics Collection

### Application Metrics

The application exposes metrics at `/metrics` endpoint in Prometheus format:

#### HTTP Metrics

- `http_requests_total` - Total HTTP requests by method, endpoint, and status
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_active` - Currently active requests

#### Content Generation Metrics

- `content_generation_total` - Total content generation requests
- `content_generation_duration_seconds` - Generation time histogram
- `audio_generation_total` - Total audio generation requests
- `audio_generation_duration_seconds` - Audio generation time

#### Database Metrics

- `database_connections_active` - Active database connections
- `database_connections_max` - Maximum connection pool size
- `database_query_duration_seconds` - Query execution time
- `database_transactions_total` - Transaction counts by status

#### Cache Metrics

- `cache_operations_total` - Cache operations by type and status
- `cache_hit_ratio` - Cache hit/miss ratio

#### SLI Metrics

- `sli_health_check_success_rate` - Health check success percentage
- `sli_api_latency_p95` - 95th percentile API latency
- `sli_api_latency_p99` - 99th percentile API latency
- `sli_api_error_rate` - API error rate percentage

### Custom Metrics

To add custom metrics in your code:

```python
from app.core.metrics import metrics

# Increment a counter
metrics.increment("my_custom_counter", tags={"operation": "create"})

# Set a gauge value
metrics.gauge("queue_size", 42, tags={"queue": "jobs"})

# Time an operation
with metrics.timer("operation_duration", tags={"op": "process"}):
    # Your operation here
    pass

# Use decorators
@metrics.track_db_operation("select", "users")
async def get_user(user_id: str):
    # Database operation
    pass

@metrics.track_external_api("openai", "completions")
async def call_openai():
    # External API call
    pass
```

## Dashboards

### Pre-configured Dashboards

1. **API Overview** (`api-overview.json`)
   - Request rates and error rates
   - Response time percentiles
   - Active requests
   - Top errors by endpoint

2. **Database Monitoring** (`database-monitoring.json`)
   - Connection pool usage
   - Query latency by operation
   - Transaction rates
   - Cache performance

3. **System Metrics** (`system-metrics.json`)
   - CPU and memory usage
   - Disk I/O and space
   - Network traffic
   - System load

### Creating Custom Dashboards

1. Access Grafana at <http://localhost:3001>
2. Create a new dashboard
3. Add panels using Prometheus as the data source
4. Save the dashboard
5. Export as JSON and add to `monitoring/grafana/provisioning/dashboards/json/`

### Example Queries

#### Request Rate by Status

```promql
sum(rate(http_requests_total{job="la-factoria-api"}[5m])) by (status)
```

#### P95 Latency

```promql
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket{job="la-factoria-api"}[5m])) by (le)
) * 1000
```

#### Error Rate Percentage

```promql
(
  sum(rate(http_requests_total{job="la-factoria-api",status=~"5.."}[5m]))
  /
  sum(rate(http_requests_total{job="la-factoria-api"}[5m]))
) * 100
```

## Alerting

### Alert Configuration

Alerts are defined in `monitoring/rules/alerts.yml` and grouped by category:

1. **API Availability**
   - API down
   - High error rate
   - High latency

2. **Content Generation**
   - High failure rate
   - Slow generation times

3. **Database**
   - Connection pool exhaustion
   - Slow queries

4. **External APIs**
   - Service down
   - High latency

5. **System**
   - High CPU/memory usage
   - Low disk space

### Adding Custom Alerts

Edit `monitoring/rules/alerts.yml`:

```yaml
- alert: MyCustomAlert
  expr: my_metric > 100
  for: 5m
  labels:
    severity: warning
    service: my-service
  annotations:
    summary: "My metric is too high"
    description: "My metric value is {{ $value }}"
```

### Notification Channels

Configure in `monitoring/alertmanager.yml`:

1. **Slack**

```yaml
slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#alerts'
```

2. **PagerDuty**

```yaml
pagerduty_configs:
  - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
```

3. **Email**

```yaml
email_configs:
  - to: 'oncall@example.com'
    from: 'alerts@example.com'
    smarthost: 'smtp.gmail.com:587'
    auth_username: 'alerts@example.com'
    auth_password: 'YOUR_PASSWORD'
```

## Production Deployment

### Railway Deployment

1. **Environment Variables**

   ```bash
   PROMETHEUS_PORT=9090
   METRICS_ENABLED=true
   ```

2. **Prometheus Remote Write**
   Configure in `prometheus.yml`:

   ```yaml
   remote_write:
     - url: "https://prometheus-endpoint.grafana.net/api/prom/push"
       basic_auth:
         username: YOUR_USERNAME
         password: YOUR_API_KEY
   ```

3. **Grafana Cloud**
   - Use Grafana Cloud for hosted dashboards
   - Configure Prometheus to push metrics

### Security Considerations

1. **Authentication**
   - Secure Prometheus with basic auth or OAuth
   - Use strong Grafana passwords
   - Protect metrics endpoint if needed

2. **Network Security**
   - Use TLS for all connections
   - Restrict access to monitoring ports
   - Use VPN or private networks

3. **Data Retention**
   - Configure appropriate retention in Prometheus
   - Use remote storage for long-term data

## Troubleshooting

### Common Issues

1. **Metrics not appearing**
   - Check if the application is running
   - Verify Prometheus can reach the app
   - Check scrape configuration

2. **High memory usage**
   - Adjust Prometheus retention
   - Reduce scrape frequency
   - Use recording rules for expensive queries

3. **Alerts not firing**
   - Check alert rule syntax
   - Verify metric names and labels
   - Check Alertmanager logs

### Debugging Commands

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Test alert rules
promtool check rules monitoring/rules/alerts.yml

# Check Grafana datasources
curl -u admin:admin http://localhost:3001/api/datasources

# View application metrics
curl http://localhost:8000/metrics
```

## Maintenance

### Regular Tasks

1. **Weekly**
   - Review alert noise and tune thresholds
   - Check dashboard performance
   - Update alert routing rules

2. **Monthly**
   - Review metrics cardinality
   - Clean up unused dashboards
   - Update exporters

3. **Quarterly**
   - Review retention policies
   - Upgrade monitoring components
   - Audit security settings

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Best Practices for Metrics](https://prometheus.io/docs/practices/naming/)
