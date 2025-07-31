# Integration Testing Guide

## Overview

This guide documents the integration testing approach for La Factoria, focusing on testing service boundaries, API endpoints, and end-to-end workflows.

## Test Structure

### Directory Organization
```
tests/integration/
├── __init__.py
├── test_service_interactions.py    # Service-to-service tests
├── test_api.py                      # API endpoint tests
├── test_api_routes.py               # Route handler tests
├── test_endpoints.py                # Critical endpoint tests
├── test_firestore_client_integration.py  # Database integration
└── test_rate_limits.py              # Rate limiting tests
```

## Key Integration Test Categories

### 1. Service-to-Service Integration
Tests interactions between different services:
- Job creation and management
- Content generation pipeline
- Caching integration
- External service communication

### 2. API Endpoint Integration
Tests complete API request/response cycles:
- Authentication and authorization
- Request validation
- Error handling
- Response formatting

### 3. Database Integration
Tests database operations:
- CRUD operations
- Concurrent updates
- Transaction handling
- Query operations

### 4. External Service Integration
Tests integration with external services:
- LLM (Gemini) integration
- Audio generation (ElevenLabs)
- Cloud Tasks queuing
- Redis caching

## Running Integration Tests

### Run All Integration Tests
```bash
pytest -m integration -v
```

### Run Specific Test Category
```bash
# Service tests only
pytest tests/integration/test_service_interactions.py -v

# API tests only
pytest tests/integration/test_api*.py -v
```

### Run with Coverage
```bash
pytest -m integration --cov=app --cov-report=html
```

## Validation Script

Use the validation script to check integration test quality:
```bash
python scripts/validate_integration_tests.py
```

This script:
- Counts real vs placeholder tests
- Checks for proper test markers
- Validates test coverage
- Identifies missing service tests
- Generates a quality score

## Writing Integration Tests

### Best Practices

1. **Use Proper Markers**
```python
@pytest.mark.integration
class TestServiceIntegration:
    pass
```

2. **Mock External Dependencies**
```python
@pytest.fixture
def mock_firestore():
    with patch("app.services.job.firestore_client.get_firestore_client") as mock:
        # Setup mock behavior
        yield mock
```

3. **Test Real Workflows**
```python
async def test_complete_workflow(self, job_manager, content_service):
    # Create job
    job = await job_manager.create_job(request)
    
    # Generate content
    result = await content_service.generate_content(job.id)
    
    # Verify end-to-end behavior
    assert result.status == "completed"
```

4. **Test Error Scenarios**
```python
async def test_service_failure_handling(self):
    # Simulate service failure
    mock_llm.side_effect = Exception("Service unavailable")
    
    # Verify graceful handling
    result = await content_service.generate_content()
    assert result.error is not None
```

## Common Test Patterns

### Testing Concurrent Operations
```python
async def test_concurrent_updates(self):
    tasks = [update_job(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    # Verify all updates succeeded
```

### Testing with Real Services
```python
@pytest.mark.skipif(
    not os.getenv("TEST_WITH_REAL_LLM"),
    reason="Skip unless TEST_WITH_REAL_LLM is set"
)
async def test_real_llm_integration(self):
    # Test with actual external service
```

### Testing Rate Limiting
```python
def test_rate_limiting(self):
    responses = []
    for _ in range(100):
        response = client.get("/api/endpoint")
        responses.append(response)
    
    # Should have some 429 responses
    rate_limited = [r for r in responses if r.status_code == 429]
    assert len(rate_limited) > 0
```

## CI/CD Integration

Integration tests are run in CI with:
- Mocked external services by default
- Optional real service tests with env flags
- Parallel test execution
- Result reporting

## Troubleshooting

### Common Issues

1. **Timeout Errors**
   - Increase async timeout: `@pytest.mark.asyncio(timeout=30)`
   - Check for deadlocks in concurrent tests

2. **Mock Setup Issues**
   - Ensure mocks are properly configured before test
   - Use `AsyncMock` for async methods

3. **Flaky Tests**
   - Add proper waits for async operations
   - Use deterministic test data
   - Mock time-dependent operations

## Metrics and Monitoring

Integration tests track:
- Test execution time
- Service interaction patterns
- Error rates and types
- Performance characteristics

Use the validation report to monitor test quality over time.