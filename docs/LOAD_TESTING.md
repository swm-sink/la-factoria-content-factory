# Load Testing Guide

This guide covers load testing for the La Factoria API using Locust.

## Overview

Load testing ensures the API can handle expected traffic patterns and identifies performance bottlenecks before they impact users.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run basic load test (10 users)
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --users=10 --spawn-rate=2 --headless --run-time=1m

# Run with web UI
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Generate HTML report
locust -f tests/performance/locustfile.py --host=http://localhost:8000 --users=50 --spawn-rate=5 --headless --run-time=5m --html=load_test_report.html
```

## Test Scenarios

### 1. Main Test Suite (`locustfile.py`)

The main test suite simulates typical API usage patterns:

- **LaFactoriaUser**: Regular API user performing content generation
- **AdminUser**: Administrative user checking monitoring endpoints
- **QuickCheckUser**: Monitoring systems performing health checks
- **HeavyContentUser**: Power users generating lots of content

### 2. Authentication Scenario

Tests authentication system under load:

```bash
locust -f tests/performance/scenarios/authentication_scenario.py --host=http://localhost:8000
```

Simulates:
- Registration storms
- Login attempts (successful and failed)
- Token validation
- Rate limiting behavior

### 3. Content Generation Scenario

Tests content generation performance:

```bash
locust -f tests/performance/scenarios/content_generation_scenario.py --host=http://localhost:8000
```

Includes:
- Various content types and sizes
- Cache hit/miss patterns
- Concurrent generation requests
- Long-running tasks

### 4. Stress Test Scenario

Tests system limits:

```bash
locust -f tests/performance/scenarios/stress_test_scenario.py --host=http://localhost:8000
```

Features:
- Sudden traffic spikes
- Sustained high load
- Database stress
- Large payloads

## Performance Baselines

Expected performance metrics are defined in `tests/performance/baseline.json`:

| Endpoint | P50 (ms) | P95 (ms) | P99 (ms) | RPS |
|----------|----------|----------|----------|-----|
| /healthz | 10 | 50 | 100 | 1000 |
| /api/v1/health | 20 | 100 | 200 | 500 |
| /api/v1/auth/login | 150 | 400 | 800 | 100 |
| /api/v1/jobs (POST) | 100 | 300 | 500 | 50 |
| /api/v1/content/generate | 2000 | 5000 | 10000 | 10 |

## Running Tests

### Local Development

1. Start the API server:
   ```bash
   npm run dev
   ```

2. Run load test:
   ```bash
   locust -f tests/performance/locustfile.py --host=http://localhost:8000
   ```

3. Open browser to http://localhost:8089

### CI/CD Pipeline

Load tests can be triggered manually in CI:

```yaml
# .github/workflows/load-test.yml
name: Load Test

on:
  workflow_dispatch:
    inputs:
      users:
        description: 'Number of users'
        required: true
        default: '50'
      duration:
        description: 'Test duration'
        required: true
        default: '5m'

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Load Test
        run: |
          locust -f tests/performance/locustfile.py \
            --host=${{ secrets.API_URL }} \
            --users=${{ github.event.inputs.users }} \
            --spawn-rate=5 \
            --run-time=${{ github.event.inputs.duration }} \
            --headless \
            --html=report.html \
            --csv=results
      - uses: actions/upload-artifact@v4
        with:
          name: load-test-results
          path: |
            report.html
            results_*.csv
```

### Production Testing

For production load testing:

1. Use a staging environment that mirrors production
2. Start with low load and gradually increase
3. Monitor system metrics during tests
4. Have rollback plan ready

## Interpreting Results

### Key Metrics

1. **Response Times**
   - P50: Median response time
   - P95/P99: Tail latencies (critical for user experience)
   - Min/Max: Range of response times

2. **Throughput**
   - Requests per second (RPS)
   - Total requests handled
   - Concurrent users supported

3. **Error Rates**
   - Failed requests percentage
   - Types of errors (timeouts, 5xx, 4xx)
   - Error patterns over time

4. **Resource Usage**
   - CPU utilization
   - Memory consumption
   - Database connections
   - External API rate limits

### Performance Thresholds

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| P95 Response Time | < 2s | 2-5s | > 5s |
| Error Rate | < 1% | 1-5% | > 5% |
| CPU Usage | < 70% | 70-85% | > 85% |
| Memory Usage | < 70% | 70-85% | > 85% |

## Common Issues

### 1. Connection Errors

```
ConnectionError: Failed to establish a new connection
```

**Solution**: Increase connection pool size or reduce spawn rate

### 2. Timeouts

```
ReadTimeout: HTTPSConnectionPool read timed out
```

**Solution**: Increase timeout values or optimize slow endpoints

### 3. Rate Limiting

```
429 Too Many Requests
```

**Solution**: Adjust test parameters or increase rate limits for testing

### 4. Memory Issues

```
MemoryError: Unable to allocate memory
```

**Solution**: Reduce number of concurrent users or optimize memory usage

## Best Practices

1. **Realistic Scenarios**
   - Model actual user behavior
   - Include think time between requests
   - Vary request patterns

2. **Gradual Load Increase**
   - Start with few users
   - Gradually increase to find breaking point
   - Monitor system behavior

3. **Test Data Management**
   - Use unique test data
   - Clean up after tests
   - Avoid polluting production data

4. **Monitoring During Tests**
   - Watch application logs
   - Monitor system resources
   - Track external dependencies

5. **Regular Testing**
   - Run after significant changes
   - Before major releases
   - Periodic baseline checks

## Advanced Usage

### Custom User Behavior

```python
class CustomUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def custom_workflow(self):
        # Your custom test logic
        pass
```

### Load Shapes

Define custom load patterns:

```python
class StepLoadShape(LoadTestShape):
    step_time = 60
    step_load = 10
    spawn_rate = 5
    time_limit = 600
    
    def tick(self):
        run_time = self.get_run_time()
        if run_time > self.time_limit:
            return None
        
        current_step = math.floor(run_time / self.step_time) + 1
        return (current_step * self.step_load, self.spawn_rate)
```

### Distributed Testing

For higher loads, use distributed mode:

```bash
# Master node
locust -f tests/performance/locustfile.py --master

# Worker nodes
locust -f tests/performance/locustfile.py --worker --master-host=<master-ip>
```

## Validation

Run the validation script to ensure setup is correct:

```bash
python scripts/validate_load_testing.py
```

This checks:
- Locust installation
- Test file syntax
- Performance baselines
- Environment configuration

## Continuous Improvement

1. **Update Baselines**
   - After performance improvements
   - When infrastructure changes
   - Based on real-world data

2. **Expand Scenarios**
   - Add new user patterns
   - Test new features
   - Cover edge cases

3. **Correlate with Monitoring**
   - Compare with production metrics
   - Validate test accuracy
   - Improve test realism