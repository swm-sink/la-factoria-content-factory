# Performance Tests

This directory contains load tests for the La Factoria API using Locust.

## Quick Start

```bash
# Install Locust
pip install locust

# Run basic load test
locust -f locustfile.py --host=http://localhost:8000

# Run headless with 50 users for 5 minutes
locust -f locustfile.py --host=http://localhost:8000 --users=50 --spawn-rate=5 --headless --run-time=5m
```

## Test Files

- `locustfile.py` - Main test suite with typical user scenarios
- `scenarios/authentication_scenario.py` - Authentication-focused tests
- `scenarios/content_generation_scenario.py` - Content generation tests
- `scenarios/stress_test_scenario.py` - Stress and spike tests
- `baseline.json` - Performance baseline metrics

## Running Specific Scenarios

```bash
# Authentication tests
locust -f scenarios/authentication_scenario.py --host=http://localhost:8000

# Content generation tests
locust -f scenarios/content_generation_scenario.py --host=http://localhost:8000

# Stress tests
locust -f scenarios/stress_test_scenario.py --host=http://localhost:8000
```

## Environment Variables

- `LA_FACTORIA_API_KEY` - API key for authentication (default: test-api-key-12345)
- `ADMIN_EMAIL` - Admin email for admin tests
- `ADMIN_PASSWORD` - Admin password

## Web UI

When running without `--headless`, open http://localhost:8089 to access the Locust web UI.

## CI/CD Integration

Load tests can be triggered manually in GitHub Actions:
1. Go to Actions tab
2. Select "Load Testing" workflow
3. Click "Run workflow"
4. Configure test parameters
5. Run and wait for results

## Performance Baselines

See `baseline.json` for expected performance metrics. Update these baselines when:
- Infrastructure changes
- Major performance improvements are made
- New endpoints are added