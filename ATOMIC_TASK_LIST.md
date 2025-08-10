# Atomic Task List - Test Coverage Expansion
## Execution Order with TDD and Atomic Commits

### PHASE 0: Foundation & Stabilization
**Goal**: Fix all broken tests and establish infrastructure

#### Task 0.1: Fix HTTP_413_PAYLOAD_TOO_LARGE Error
```python
# File: tests/test_validation.py
# Issue: AttributeError: module 'starlette.status' has no attribute 'HTTP_413_PAYLOAD_TOO_LARGE'
# Fix: Use status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
```
- [ ] Read src/core/validation.py line 337
- [ ] Check correct Starlette status code 
- [ ] Update validation.py to use HTTP_413_REQUEST_ENTITY_TOO_LARGE
- [ ] Run test to verify fix
- [ ] Commit: "fix: correct HTTP 413 status code constant"

#### Task 0.2: Fix Query Parameter Colon Preservation
```python
# File: tests/test_validation.py 
# Issue: Colon being stripped from query params
# Fix: Adjust sanitization to preserve colons in filters
```
- [ ] Read SecurityValidator.sanitize_string implementation
- [ ] Identify colon stripping logic
- [ ] Modify to preserve colons in specific contexts
- [ ] Update test assertions
- [ ] Commit: "fix: preserve colons in query filter parameters"

#### Task 0.3: Fix API Key Validation Test
```python
# File: tests/test_validation.py
# Issue: Test expects exception but gets None in dev mode
# Fix: Mock settings properly for test context
```
- [ ] Read validate_api_key function
- [ ] Add proper settings mock in test
- [ ] Ensure test covers both dev and prod modes
- [ ] Verify test passes
- [ ] Commit: "test: fix API key validation with proper mocking"

#### Task 0.4: Fix String Sanitization Tests
```python
# File: tests/test_validation.py
# Issue: Sort parameter and string sanitization failing
# Fix: Align test expectations with implementation
```
- [ ] Review sanitize_string behavior for sort params
- [ ] Update test to match actual sanitization
- [ ] Verify HTML escaping vs blocking logic
- [ ] Run all validation tests
- [ ] Commit: "test: align validation tests with sanitization behavior"

#### Task 0.5: Create Test Utilities Module
```python
# File: tests/utils/__init__.py, fixtures.py, factories.py, mocks.py
# Purpose: Centralized test helpers
```
- [ ] Create tests/utils/ directory
- [ ] Create fixtures.py with database fixtures
- [ ] Create factories.py with data generators
- [ ] Create mocks.py with service mocks
- [ ] Create assertions.py with custom matchers
- [ ] Commit: "test: add centralized test utilities module"

#### Task 0.6: Set Up GitHub Actions CI
```yaml
# File: .github/workflows/test.yml
# Purpose: Automated testing on every push
```
- [ ] Create .github/workflows/ directory
- [ ] Write test.yml with pytest configuration
- [ ] Add coverage reporting
- [ ] Set 80% coverage requirement
- [ ] Test workflow locally with act
- [ ] Commit: "ci: add GitHub Actions test workflow"

### PHASE 1: Security-Critical Coverage

#### Task 1.1: Admin Authentication Tests
```python
# File: tests/test_admin_routes.py
# Tests: Authentication and authorization
```
- [ ] Create test_admin_routes.py
- [ ] Test missing API key (401)
- [ ] Test invalid API key (403)
- [ ] Test valid admin key (200)
- [ ] Test rate limiting on admin endpoints
- [ ] Commit: "test: add admin authentication test coverage"

#### Task 1.2: Admin Data Deletion Tests
```python
# Tests: User data deletion endpoint
```
- [ ] Test successful user deletion
- [ ] Test deletion of non-existent user
- [ ] Test SQL injection in user_id
- [ ] Test audit logging of deletion
- [ ] Commit: "test: add admin data deletion test coverage"

#### Task 1.3: Admin Config Update Tests
```python
# Tests: System configuration updates
```
- [ ] Test valid config updates
- [ ] Test invalid config values
- [ ] Test config validation rules
- [ ] Test rollback on error
- [ ] Commit: "test: add admin config update test coverage"

#### Task 1.4: Health Check Database Failure Tests
```python
# File: tests/test_health_endpoints.py
# Tests: Database connection failures
```
- [ ] Create test_health_endpoints.py
- [ ] Mock database connection error
- [ ] Test health check response
- [ ] Verify degraded status
- [ ] Test error message clarity
- [ ] Commit: "test: add health check database failure tests"

#### Task 1.5: Health Check Redis Failure Tests
```python
# Tests: Redis unavailability scenarios
```
- [ ] Mock Redis connection timeout
- [ ] Test fallback to memory
- [ ] Verify warning in health response
- [ ] Test rate limiting still works
- [ ] Commit: "test: add health check Redis failure tests"

#### Task 1.6: Health Check AI Provider Tests
```python
# Tests: AI provider connectivity
```
- [ ] Mock OpenAI timeout
- [ ] Mock Anthropic rate limit
- [ ] Mock Vertex AI auth failure
- [ ] Test provider health aggregation
- [ ] Commit: "test: add AI provider health check tests"

### PHASE 2: Core Functionality Coverage

#### Task 2.1: Monitoring SQL Injection Tests
```python
# File: tests/test_monitoring_routes.py
# Tests: SQL injection protection
```
- [ ] Create test_monitoring_routes.py
- [ ] Test malicious input in filters
- [ ] Test SQL keywords in parameters
- [ ] Test Unicode injection attempts
- [ ] Verify query parameterization
- [ ] Commit: "test: add monitoring SQL injection protection"

#### Task 2.2: Monitoring Metrics Accuracy Tests
```python
# Tests: Metric calculation correctness
```
- [ ] Test content count aggregation
- [ ] Test quality score averaging
- [ ] Test time-based filtering
- [ ] Test empty result handling
- [ ] Commit: "test: add monitoring metrics accuracy tests"

#### Task 2.3: Monitoring Performance Tests
```python
# Tests: Query performance under load
```
- [ ] Test with 1000 content items
- [ ] Test complex aggregations
- [ ] Test query timeout handling
- [ ] Test result pagination
- [ ] Commit: "test: add monitoring performance tests"

#### Task 2.4: Rate Limiting Redis Failover Tests
```python
# File: tests/test_rate_limiting_advanced.py
# Tests: Redis failure handling
```
- [ ] Create test_rate_limiting_advanced.py
- [ ] Simulate Redis connection loss
- [ ] Test automatic fallback
- [ ] Verify memory limiter activation
- [ ] Test seamless recovery
- [ ] Commit: "test: add rate limiting Redis failover tests"

#### Task 2.5: Rate Limiting Burst Tests
```python
# Tests: Concurrent request bursts
```
- [ ] Test 100 concurrent requests
- [ ] Test rate limit accuracy
- [ ] Test fair queuing
- [ ] Test header generation
- [ ] Commit: "test: add rate limiting burst handling tests"

### PHASE 3: Integration & Performance

#### Task 3.1: End-to-End Content Generation Flow
```python
# File: tests/test_integration_flows.py
# Tests: Complete user journey
```
- [ ] Create test_integration_flows.py
- [ ] Test API key → request → generation → response
- [ ] Test error recovery
- [ ] Test quality thresholds
- [ ] Test response formatting
- [ ] Commit: "test: add E2E content generation flow tests"

#### Task 3.2: Admin Workflow Integration
```python
# Tests: Admin operations flow
```
- [ ] Test login → monitor → configure → logout
- [ ] Test permission escalation attempts
- [ ] Test audit trail generation
- [ ] Test config persistence
- [ ] Commit: "test: add admin workflow integration tests"

#### Task 3.3: Performance Baseline Tests
```python
# File: tests/test_performance_baselines.py
# Tests: Response time benchmarks
```
- [ ] Create test_performance_baselines.py
- [ ] Measure content generation time
- [ ] Measure database query time
- [ ] Measure AI provider latency
- [ ] Set performance thresholds
- [ ] Commit: "test: add performance baseline measurements"

#### Task 3.4: Memory Usage Tests
```python
# Tests: Memory leak detection
```
- [ ] Test repeated content generation
- [ ] Monitor memory growth
- [ ] Test garbage collection
- [ ] Verify resource cleanup
- [ ] Commit: "test: add memory usage monitoring tests"

### PHASE 4: Advanced Features

#### Task 4.1: A/B Testing Framework Setup
```python
# File: tests/test_prompt_ab_framework.py
# Tests: Prompt variant testing
```
- [ ] Create test_prompt_ab_framework.py
- [ ] Test variant selection logic
- [ ] Test metric collection
- [ ] Test statistical significance
- [ ] Test result aggregation
- [ ] Commit: "test: add prompt A/B testing framework"

### EXECUTION CHECKLIST

#### Pre-Implementation
- [ ] Ensure clean working directory
- [ ] Pull latest changes from main
- [ ] Create feature branch: test-coverage-expansion

#### During Implementation
- [ ] Write test first (TDD)
- [ ] Run test (should fail)
- [ ] Implement minimal code to pass
- [ ] Run test (should pass)
- [ ] Refactor if needed
- [ ] Run all tests
- [ ] Make atomic commit

#### Post-Implementation
- [ ] Run full test suite
- [ ] Check coverage report
- [ ] Update documentation
- [ ] Create pull request
- [ ] Review quality gates

### SUCCESS CRITERIA

#### Phase 0 Complete When:
- All 6 validation tests pass ✓
- Test utilities created ✓
- CI/CD configured ✓

#### Phase 1 Complete When:
- Admin routes: 90% coverage ✓
- Health endpoints: 80% coverage ✓
- All security tests pass ✓

#### Phase 2 Complete When:
- Monitoring: 80% coverage ✓
- Rate limiting: 85% coverage ✓
- No SQL injection vulnerabilities ✓

#### Phase 3 Complete When:
- Integration tests pass ✓
- Performance baselines set ✓
- Memory leaks detected: 0 ✓

#### Phase 4 Complete When:
- A/B framework operational ✓
- Overall coverage: >80% ✓

### TIME ESTIMATES

#### Phase 0: 5 hours
- Validation fixes: 2 hours
- Test utilities: 2 hours  
- CI/CD setup: 1 hour

#### Phase 1: 10 hours
- Admin tests: 6 hours
- Health tests: 4 hours

#### Phase 2: 7 hours
- Monitoring tests: 4 hours
- Rate limiting: 3 hours

#### Phase 3: 8 hours
- Integration: 4 hours
- Performance: 4 hours

#### Phase 4: 3 hours
- A/B framework: 3 hours

**Total: 33 hours** (4-5 days at 7 hours/day)

### ATOMIC COMMIT MESSAGES

Format: `type: description`

Types:
- `fix`: Bug fixes
- `test`: New tests
- `ci`: CI/CD changes
- `refactor`: Code improvements
- `docs`: Documentation

Examples:
- `fix: correct HTTP 413 status code constant`
- `test: add admin authentication coverage`
- `ci: add GitHub Actions test workflow`
- `refactor: extract test fixtures to utilities`
- `docs: update test coverage report`