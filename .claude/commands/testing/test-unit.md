---
name: /test-unit
description: "Run unit tests for . using pytest"
usage: /test-unit [file-pattern] [--coverage] [--watch]
category: testing
tools: Bash, Read, Write
security_level: HIGH
---

# Unit Testing for .

<!-- SECURITY: Include command security wrapper for injection prevention -->
<include>components/security/command-security-wrapper.md</include>

**SECURITY NOTICE**: This command executes test frameworks with potential file system access. ALL inputs are validated to prevent command injection and path traversal attacks.

I'll help you run and manage unit tests for **.** using **pytest** with patterns optimized for **Python**.

## Test Configuration

- **Framework**: pytest
- **Language**: Python
- **Coverage Target**: Based on standard requirements
- **Tech Stack**: Python

## Running Tests

### All Unit Tests
```bash
/test-unit
# SECURITY: Default execution with security wrapper validation
# SECURITY: Test commands validated against TEST_ALLOWED_COMMANDS allowlist
```

### Specific Test Files
For Python test patterns:
```bash
/test-unit src/**/*.test.[ext]
# SECURITY: File patterns validated using validateFilePath() with extension checking
# SECURITY: Path traversal prevention applied to all file patterns
/test-unit tests/unit/
# SECURITY: Directory paths validated against project boundaries
```

### Watch Mode
For agile development:
```bash
/test-unit --watch
# SECURITY: Watch mode validated, file monitoring secured
# SECURITY: Continuous monitoring with sanitized output
```

## Coverage Requirements

Based on standard requirements:
- **Basic**: 60% minimum coverage
- **Standard**: 80% minimum coverage
- **High**: 90% minimum coverage with branch coverage
- Coverage thresholds validated
- Coverage reports properly formatted

## Test Patterns for backend

Domain-specific testing patterns:
- Component isolation with test boundaries
- Mock strategies with input validation
- Test data factories with clean test data
- Assertion patterns with proper comparisons
- Test execution patterns
- File discovery patterns
- Clean test output and error handling

## Integration with GitHub Actions

Your CI pipeline configuration:
- Pre-commit hooks
- PR validation
- Coverage reporting
- Test result artifacts

## Performance Considerations

For balanced requirements:
- Test execution optimization
- Parallel test runners
- Test suite splitting
- Resource management

## Team Collaboration

For small teams:
- Test naming conventions
- Shared test utilities
- Test documentation
- Review processes

**TEST EXECUTION PROCESS:**

1. **Input Validation**: All test parameters validated
2. **File Pattern Validation**: Test file patterns validated
3. **Command Validation**: Test framework commands validated against allowlist
4. **Path Validation**: All test paths validated for boundary compliance
5. **Execution**: Tests executed using framework wrapper
6. **Output Processing**: All test results and coverage reports processed
7. **Error Handling**: Test failures handled with clean error messages
8. **Logging**: Complete audit trail maintained

**ALLOWED TEST FRAMEWORKS**: pytest, jest, mocha, jasmine, karma, go test, cargo test, mvn test, gradle test, phpunit, rspec, minitest
**VALIDATIONS**: 
- File patterns: Extension validation, path boundary checking
- Coverage values: Numeric validation, range checking
- Framework parameters: Parameter validation
- Test execution: Resource limits and timeout controls

What would you like to test? (All inputs will be validated)