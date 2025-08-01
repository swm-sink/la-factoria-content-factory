# La Factoria Monitoring Stack

This directory contains the monitoring infrastructure for La Factoria using Prometheus and Grafana.

## Quick Start

1. **Start the monitoring stack:**

   ```bash
   docker-compose up -d
   ```

2. **Access the services:**
   - Prometheus: <http://localhost:9090>
   - Grafana: <http://localhost:3001> (login: admin/admin)
   - Alertmanager: <http://localhost:9093>

3. **Verify the setup:**

   ```bash
   ../scripts/validate_monitoring.py
   ```

## Components

- `prometheus.yml` - Prometheus configuration
- `alertmanager.yml` - Alert routing configuration
- `blackbox.yml` - Endpoint monitoring configuration
- `docker-compose.yml` - Container orchestration
- `rules/` - Prometheus alerting rules
- `grafana/` - Grafana dashboards and configuration

## Dashboards

Pre-configured dashboards are automatically provisioned:

- **API Overview** - Request rates, errors, latency
- **Database Monitoring** - Connection pools, query performance
- **System Metrics** - CPU, memory, disk, network

## Configuration

### Adding Alerts

Edit `rules/alerts.yml` and restart Prometheus:

```bash
docker-compose restart prometheus
```

### Notification Channels

Configure in `alertmanager.yml`:

- Slack webhooks
- PagerDuty integration
- Email notifications

## Troubleshooting

If metrics are not appearing:

1. Check if the app is running: `curl http://localhost:8000/health`
2. Verify Prometheus targets: <http://localhost:9090/targets>
3. Check container logs: `docker-compose logs prometheus`

For more details, see [MONITORING_SETUP.md](../docs/MONITORING_SETUP.md)
