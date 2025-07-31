# Pre-commit Hooks Setup Guide

This guide explains how to set up and use pre-commit hooks in the La Factoria project.

## What are Pre-commit Hooks?

Pre-commit hooks are scripts that run automatically before each commit to ensure code quality, consistency, and security. They help catch issues early and maintain project standards.

## Quick Setup

```bash
# Install pre-commit and set up hooks
python scripts/setup_precommit.py

# Or manually:
pip install pre-commit
pre-commit install
```

## Configured Hooks

Our pre-commit configuration includes:

### Code Quality
- **Black**: Python code formatting (line length: 120)
- **isort**: Import sorting (Black-compatible profile)
- **Ruff**: Fast Python linting (replaces flake8)
- **MyPy**: Type checking for Python code

### Security
- **Bandit**: Security vulnerability scanning
- **Safety**: Check for known security vulnerabilities in dependencies
- **Detect Private Key**: Prevent committing private keys
- **Secrets Guard**: Custom hook to check for exposed secrets

### File Formatting
- **Trailing Whitespace**: Remove trailing whitespace
- **End of File Fixer**: Ensure files end with newline
- **Mixed Line Ending**: Normalize line endings
- **Check YAML/JSON/TOML**: Validate configuration files

### Additional Checks
- **Check AST**: Verify Python syntax
- **Check Merge Conflict**: Detect merge conflict markers
- **Check Added Large Files**: Prevent large files (>1MB)
- **Markdown Lint**: Check markdown formatting
- **ShellCheck**: Lint shell scripts
- **Hadolint**: Lint Dockerfiles

### Custom Hooks
- **Smart AI Context**: Generate context for AI assistance
- **Check API Tests**: Ensure API endpoints have tests

## Usage

### Running Hooks

```bash
# Run on staged files (automatic before commit)
pre-commit run

# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Skip hooks for one commit
git commit --no-verify -m "Emergency fix"
```

### Updating Hooks

```bash
# Update hook versions
pre-commit autoupdate

# Clean pre-commit cache
pre-commit clean

# Reinstall hooks
pre-commit install --install-hooks
```

## CI Integration

Pre-commit hooks are integrated with our CI pipeline. The CI will:
1. Run all hooks on the entire codebase
2. Fail the build if any hooks fail
3. Show detailed output for debugging

## Performance

All hooks are optimized to run in under 30 seconds total. Individual hook timings:
- Black: ~2s
- isort: ~1s
- Ruff: ~3s
- MyPy: ~10s
- Bandit: ~5s
- Other hooks: ~5s combined

## Troubleshooting

### Hook Installation Issues
```bash
# Check pre-commit version
pre-commit --version

# Reinstall pre-commit
pip install --upgrade pre-commit

# Clear cache and reinstall
pre-commit clean
pre-commit install --install-hooks
```

### Specific Hook Failures

**Black formatting issues:**
```bash
# Auto-fix formatting
black .
```

**Import sorting issues:**
```bash
# Auto-fix imports
isort .
```

**Type checking issues:**
```bash
# Run mypy with more details
mypy app/ --show-error-codes
```

### Bypassing Hooks

If you need to bypass hooks temporarily:
```bash
# Skip all hooks
git commit --no-verify

# Skip specific hook (in .pre-commit-config.yaml)
# Add: skip: [hook-id]
```

## Best Practices

1. **Run before pushing**: Always run `pre-commit run --all-files` before pushing
2. **Keep hooks updated**: Run `pre-commit autoupdate` monthly
3. **Fix issues immediately**: Don't accumulate technical debt
4. **Configure your editor**: Set up auto-formatting in your IDE
5. **Document exemptions**: If skipping hooks, document why in commit message

## IDE Integration

### VS Code
```json
// settings.json
{
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=120"],
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "editor.formatOnSave": true
}
```

### PyCharm
1. Settings → Tools → Black
2. Set line length to 120
3. Enable "On save"

## Adding New Hooks

To add a new hook:
1. Edit `.pre-commit-config.yaml`
2. Add the hook configuration
3. Run `pre-commit install --install-hooks`
4. Test with `pre-commit run <hook-id> --all-files`
5. Update this documentation

## Validation

Run the validation script to ensure hooks are properly configured:
```bash
python scripts/validate_precommit_hooks.py
```

This will check:
- Pre-commit installation
- Hook configuration
- Execution speed
- CI integration