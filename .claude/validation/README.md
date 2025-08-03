# La Factoria Validation System

## Overview

This validation system provides comprehensive testing and quality assurance for the La Factoria Claude Code ecosystem. It's designed to be portable and flexible across different environments and user setups.

## Quick Start

### Running Tests

```bash
# From the project root
python -m pytest .claude/validation/scripts/test_validation_system.py -v

# From the validation directory
cd .claude/validation
python -m pytest scripts/test_validation_system.py -v

# Run specific test categories
pytest -m "unit" -v                    # Unit tests only
pytest -m "integration" -v             # Integration tests only
pytest -m "not requires_files" -v      # Skip tests that need specific files
```

### Running Full System Validation

```bash
# Run the complete validation system
python .claude/validation/scripts/validate_system.py

# Run individual validators
python .claude/validation/scripts/validate_agents.py
python .claude/validation/scripts/validate_context.py
python .claude/validation/scripts/validate_commands.py
```

## Environment Flexibility

### Portable Design

This validation system is designed to work in various environments:

- **Any directory structure**: Tests adapt to find files in multiple possible locations
- **Missing dependencies**: Tests gracefully skip when validation modules aren't available
- **Permission issues**: Robust error handling for file system operations
- **Cross-platform**: Works on Windows, macOS, and Linux

### Configuration Options

#### pytest.ini Configuration

The `pytest.ini` file includes flexible test paths:

```ini
testpaths = 
    scripts
    .
    validation/scripts
    .claude/validation/scripts
```

#### Environment Variables

Set these variables for customized behavior:

```bash
export PYTHONPATH=.:validation:scripts:.claude/validation/scripts
export VALIDATION_TEST_MODE=true
```

### Test Markers

Use pytest markers to control test execution:

- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.unit` - Unit tests  
- `@pytest.mark.validation` - Validation-specific tests
- `@pytest.mark.hooks` - Claude Code hooks tests
- `@pytest.mark.requires_files` - Tests needing specific files
- `@pytest.mark.slow` - Long-running tests

### Skipping Tests

```bash
# Skip slow tests
pytest -m "not slow"

# Skip tests requiring specific files
pytest -m "not requires_files"

# Skip integration tests
pytest -m "not integration"

# Run only unit tests
pytest -m "unit"
```

## Directory Structure

```
.claude/validation/
├── README.md                           # This file
├── conftest.py                         # Shared test fixtures (portable)
├── pytest.ini                         # Pytest configuration (flexible paths)
├── scripts/
│   ├── validate_system.py              # System orchestrator
│   ├── validate_agents.py              # Agent validation
│   ├── validate_context.py             # Context validation
│   ├── validate_commands.py            # Commands validation
│   └── test_validation_system.py       # Pytest test suite
├── config/
│   └── validation.yaml                 # Validation configuration
└── test_data/                          # Sample test files (auto-created)
    ├── valid_agent.md
    ├── valid_command.md
    └── valid_context.md
```

## Troubleshooting

### Common Issues

#### Import Errors

If you see import errors:

```bash
# Add the validation scripts to your Python path
export PYTHONPATH="${PYTHONPATH}:.claude/validation/scripts"

# Or run from the validation directory
cd .claude/validation
python -m pytest scripts/test_validation_system.py
```

#### Missing Test Data

Test data files are automatically created. If creation fails:

```bash
# Manual creation (from validation directory)
mkdir -p test_data
# Test files will be created automatically on next run
```

#### Permission Issues

On systems with strict permissions:

```bash
# Run tests with relaxed requirements
pytest -m "not requires_files" -v

# Or adjust permissions
chmod -R 755 .claude/validation/
```

### Environment-Specific Solutions

#### Windows

```cmd
# Set Python path (Windows Command Prompt)
set PYTHONPATH=%PYTHONPATH%;.claude\validation\scripts

# Run tests
python -m pytest .claude\validation\scripts\test_validation_system.py -v
```

#### macOS/Linux

```bash
# Set Python path
export PYTHONPATH="${PYTHONPATH}:.claude/validation/scripts"

# Run tests with proper permissions
chmod +x .claude/validation/scripts/*.py
python -m pytest .claude/validation/scripts/test_validation_system.py -v
```

#### Docker/Container Environments

```bash
# Install test dependencies
pip install pytest pyyaml

# Run tests from container
docker run -v $(pwd):/app -w /app python:3.11 \
  python -m pytest .claude/validation/scripts/test_validation_system.py -v
```

## Advanced Usage

### Custom Configuration

Create your own validation configuration:

```yaml
# custom_validation.yaml
validation:
  global:
    zero_tolerance_failures: false
    minimum_coverage_threshold: 0.80
  quality_thresholds:
    cross_reference_coverage: 0.70
    content_quality: 0.85
```

### Extending Tests

Add your own tests to the system:

```python
# my_custom_test.py
import pytest
from pathlib import Path

class TestCustomValidation:
    def test_my_custom_validation(self, validation_config):
        # Your custom validation logic
        assert True
```

### CI/CD Integration

Example GitHub Actions workflow:

```yaml
- name: Run Validation Tests
  run: |
    pip install pytest pyyaml
    python -m pytest .claude/validation/scripts/test_validation_system.py \
      --tb=short -v
```

## Support

This validation system follows the MEP-CE (Multi-step Exhaustive Planning - Critical Execution) methodology and 2024-2025 testing best practices.

For issues or questions:
1. Check the troubleshooting section above
2. Review test output for specific error messages
3. Ensure all dependencies are installed: `pip install pytest pyyaml`
4. Verify file permissions and directory structure

The system is designed to be robust and provide clear feedback when issues occur.