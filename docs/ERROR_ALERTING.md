# Error Alerting Integration

This document describes the comprehensive error alerting system implemented in Step 20 of the La Factoria improvement plan.

## Overview

The error alerting system automatically detects errors in the application and generates alerts through multiple notification channels (PagerDuty, Slack, Email). It integrates with the existing monitoring infrastructure to provide immediate visibility into application issues.

## Architecture

### Components

1. **Error Alerting Middleware** (`app/middleware/error_alerting.py`)
   - Detects HTTP errors and unhandled exceptions
   - Tracks error rates and patterns
   - Generates alerts based on configurable thresholds
   - Enriches alerts with contextual information

2. **Enhanced Exception Handlers** (`app/core/exceptions/handlers.py`)
   - Integrates with alert manager for automatic alert generation
   - Fires alerts for critical application exceptions
   - Categorizes errors by type (database, external service, timeout)
   - Provides detailed error context in alerts

3. **Critical Error Detector** (`app/middleware/error_alerting.py`)
   - Specialized detection for infrastructure failures
   - Database connection issues
   - External service failures
   - Real-time alert generation

4. **Alert Manager Integration** (`app/main.py`)
   - Configures alert manager during application startup
   - Sets up notification channels and routing rules
   - Manages alert lifecycle (firing, acknowledgment, resolution)

## Features

### Automatic Error Detection

- **HTTP Error Codes**: 500, 502, 503, 504 automatically trigger alerts
- **Unhandled Exceptions**: All uncaught exceptions generate critical alerts
- **Error Rate Monitoring**: Alerts when error rate exceeds configurable threshold (default: 5%)
- **Pattern Recognition**: Detects database, network, and timeout errors

### Alert Enrichment

Each alert includes:

- Request context (endpoint, method, user agent, IP)
- Error details (type, message, stack trace)
- Performance metrics (error rate, response time)
- User context (user ID, API key if available)
- Runbook links for resolution guidance

### Severity Classification

- **Critical**: Unhandled exceptions, infrastructure failures (500-503 errors)
- **High**: Service degradation, database errors
- **Medium**: Timeouts, external service issues
- **Low**: Client errors, validation failures

## Configuration

### Middleware Configuration

```python
error_alerting_config = {
    "error_rate_threshold": 0.05,  # 5% error rate threshold
    "error_rate_window": 300,      # 5-minute window
    "critical_error_codes": [500, 502, 503, 504],
    "alert_on_first_error": True   # Alert immediately on critical errors
}
```

### Alert Routing

Alerts are routed based on:

- **Severity Level**: Critical → PagerDuty, High → Slack, Medium → Email
- **Service Type**: Database errors → Database team, API errors → Engineering team
- **Error Pattern**: Infrastructure → Ops team, Application → Dev team

## Usage

### Automatic Operation

The error alerting system operates automatically once deployed:

1. **Application Startup**: Alert manager and middleware are initialized
2. **Request Processing**: Middleware monitors all requests for errors
3. **Error Detection**: Errors are automatically detected and classified
4. **Alert Generation**: Alerts are fired based on severity and configuration
5. **Notification**: Alerts are sent to appropriate channels

### Manual Testing

Test the error alerting system:

```bash
# Run validation script
python scripts/validate_error_alerting_simple.py

# Fire test alerts
curl -X POST http://localhost:8000/alerts/fire \
  -H "Content-Type: application/json" \
  -d '{"name": "TestAlert", "severity": "critical"}'

# Check active alerts
curl http://localhost:8000/alerts/active
```

### Monitoring

Monitor error alerting effectiveness:

- **Alert Volume**: Track alerts generated per hour/day
- **Response Times**: Monitor alert acknowledgment and resolution times
- **False Positives**: Tune thresholds to reduce noise
- **Coverage**: Ensure all critical errors generate alerts

## Integration Points

### With Existing Systems

1. **Prometheus/Grafana**: Error metrics are exposed for visualization
2. **SLA Monitoring**: Error rates feed into SLO calculations
3. **Health Checks**: Failed health checks trigger immediate alerts
4. **Logging System**: All alerts are logged with full context

### With Notification Channels

1. **PagerDuty**: Critical alerts for immediate response
2. **Slack**: Warning alerts for team awareness
3. **Email**: Database team notifications
4. **Webhook**: Custom integrations

## Alert Examples

### Database Connection Failure

```json
{
  "name": "ExceptionHandler_UnhandledException",
  "severity": "critical",
  "message": "Unhandled ConnectionError: Connection refused",
  "context": {
    "exception_type": "ConnectionError",
    "is_database_error": true,
    "endpoint": "POST /api/v1/content",
    "error_rate": 0.15
  },
  "runbook_url": "https://github.com/lafactoria/runbooks/blob/main/database/connection-issues.md"
}
```

### High Error Rate

```json
{
  "name": "HighErrorRate_API",
  "severity": "high",
  "message": "Error rate 8.5% exceeds threshold of 5%",
  "context": {
    "error_rate": 0.085,
    "request_count": 1000,
    "error_count": 85,
    "time_window": "5 minutes"
  },
  "runbook_url": "https://github.com/lafactoria/runbooks/blob/main/incident-response/high-error-rate.md"
}
```

## Best Practices

### Tuning Alert Thresholds

1. **Start Conservative**: Begin with low thresholds, tune upward to reduce noise
2. **Monitor Patterns**: Analyze historical data to set appropriate baselines
3. **Context Matters**: Different endpoints may require different thresholds
4. **Feedback Loop**: Use alert metrics to continuously improve configuration

### Alert Management

1. **Acknowledge Promptly**: Acknowledge alerts to prevent escalation
2. **Document Resolution**: Update runbooks based on incident learnings
3. **Review Regularly**: Weekly review of alert patterns and effectiveness
4. **Team Training**: Ensure team knows how to respond to different alert types

### Error Prevention

1. **Circuit Breakers**: Implement circuit breakers for external services
2. **Retry Logic**: Add retry mechanisms with exponential backoff
3. **Graceful Degradation**: Handle errors gracefully when possible
4. **Input Validation**: Prevent errors through robust validation

## Troubleshooting

### Common Issues

1. **Alert Storm**: Too many alerts generated
   - **Solution**: Increase thresholds, implement alert grouping
   - **Check**: Error rate calculation, notification channels

2. **Missing Alerts**: Critical errors not generating alerts
   - **Solution**: Verify middleware configuration, check alert manager status
   - **Check**: Exception handler integration, notification channels

3. **False Positives**: Alerts for non-critical issues
   - **Solution**: Refine error detection patterns, adjust severity levels
   - **Check**: Error classification logic, alert routing rules

### Validation Commands

```bash
# Check error alerting integration
python scripts/validate_error_alerting_simple.py

# Test alert firing
python scripts/test_alerts.py fire test_error_alert

# Check alert manager status
curl http://localhost:8000/alerts/active

# View prometheus metrics
curl http://localhost:8000/metrics | grep error
```

## Metrics and KPIs

### Alert Metrics

- `alerts_fired_total{severity="critical"}`: Total critical alerts fired
- `alerts_fired_total{source="error_middleware"}`: Alerts from error middleware
- `alert_response_time_seconds`: Time from alert to acknowledgment
- `alert_resolution_time_seconds`: Time from alert to resolution

### Error Metrics

- `http_requests_total{status="5xx"}`: Server error requests
- `error_rate`: Current application error rate
- `unhandled_exceptions_total`: Total unhandled exceptions
- `database_errors_total`: Database-related errors

### SLA Impact

- **Error Budget**: Error alerts consume error budget allocation
- **Availability SLO**: High error rates impact availability SLO
- **Response Time SLO**: Error handling affects response time metrics

## Security Considerations

### Alert Content

- **No Sensitive Data**: Alerts should not contain passwords, tokens, or PII
- **Sanitized Messages**: Error messages are sanitized for external channels
- **Access Control**: Alert endpoints require proper authentication

### Notification Security

- **Encrypted Channels**: All notification channels use TLS/HTTPS
- **Webhook Tokens**: Webhook endpoints require authentication tokens
- **IP Allowlisting**: Restrict access to alert management endpoints

## Future Enhancements

### Planned Improvements

1. **Machine Learning**: Anomaly detection for unusual error patterns
2. **Auto-Resolution**: Automatic resolution of known issues
3. **Intelligent Routing**: Dynamic routing based on on-call schedules
4. **Context Enhancement**: Additional context from user sessions, feature flags

### Integration Opportunities

1. **APM Tools**: Integration with application performance monitoring
2. **Log Aggregation**: Enhanced correlation with centralized logging
3. **Chaos Engineering**: Integration with chaos testing frameworks
4. **CI/CD**: Alert on deployment-related errors
