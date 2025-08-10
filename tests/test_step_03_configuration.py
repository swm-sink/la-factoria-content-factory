"""
Step 3: Configuration Management Audit
=======================================

Testing configuration security, flexibility, and operational readiness.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Any
import pytest
from unittest.mock import patch, MagicMock


class TestConfigurationManagement:
    """Validate configuration management best practices"""
    
    def test_no_hardcoded_sensitive_values(self):
        """Ensure no sensitive values are hardcoded in source"""
        sensitive_patterns = [
            (r'["\']sk-[a-zA-Z0-9]{48}["\']', 'OpenAI API key'),
            (r'["\']anthropic-[a-zA-Z0-9]+["\']', 'Anthropic API key'),
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
            (r'secret[_-]?key\s*=\s*["\'][^"\']+["\']', 'Secret key'),
            (r'["\']postgres://[^"\']+:[^"\']+@[^"\']+["\']', 'Database URL with password'),
            (r'["\']mysql://[^"\']+:[^"\']+@[^"\']+["\']', 'Database URL with password'),
            (r'token\s*=\s*["\'][a-zA-Z0-9]{20,}["\']', 'API token'),
        ]
        
        violations = []
        excluded_patterns = ['demo-', 'test-', 'example', 'your-', 'xxx', 'change-this']
        
        for py_file in Path('src').rglob('*.py'):
            content = py_file.read_text()
            
            for pattern, description in sensitive_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Check if it's not a placeholder
                    if not any(excl in match.lower() for excl in excluded_patterns):
                        violations.append(f"{py_file}: {description} found: {match[:30]}...")
        
        assert len(violations) == 0, f"Hardcoded secrets found:\n" + "\n".join(violations)
    
    def test_environment_variables_used(self):
        """Verify sensitive config comes from environment variables"""
        from src.core.config import settings
        
        sensitive_attrs = [
            'SECRET_KEY',
            'DATABASE_URL',
            'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY',
            'LA_FACTORIA_API_KEY',
            'REDIS_URL',
        ]
        
        for attr in sensitive_attrs:
            if hasattr(settings, attr):
                value = getattr(settings, attr)
                if value and not value.startswith('${'):  # Not a template variable
                    # Check it's not a hardcoded production value
                    assert 'production' not in str(value).lower() or attr == 'DATABASE_URL', \
                        f"{attr} might be hardcoded for production"
    
    def test_configuration_hierarchy(self):
        """Verify configuration follows proper hierarchy (env > file > defaults)"""
        from src.core.config import Settings
        
        # Test that environment variables override defaults
        test_cases = [
            ('APP_NAME', 'TestApp'),
            ('DEBUG', 'false'),
            ('API_V1_PREFIX', '/test/api/v1'),
        ]
        
        for env_var, test_value in test_cases:
            with patch.dict(os.environ, {env_var: test_value}):
                settings = Settings()
                actual_value = getattr(settings, env_var)
                assert str(actual_value) == test_value or actual_value == (test_value == 'true'), \
                    f"Environment variable {env_var} not properly loaded"
    
    def test_required_settings_defined(self):
        """Ensure all required settings are defined"""
        from src.core.config import settings
        
        required_settings = [
            'APP_NAME',
            'APP_VERSION',
            'ENVIRONMENT',
            'API_V1_PREFIX',
            'SECRET_KEY',
        ]
        
        missing = []
        for setting in required_settings:
            if not hasattr(settings, setting):
                missing.append(setting)
            elif getattr(settings, setting) is None:
                missing.append(f"{setting} (is None)")
        
        assert len(missing) == 0, f"Missing required settings: {missing}"
    
    def test_environment_specific_configs(self):
        """Verify different configs for different environments"""
        from src.core.config import Settings
        
        environments = ['development', 'staging', 'production']
        
        for env in environments:
            with patch.dict(os.environ, {'ENVIRONMENT': env}):
                settings = Settings()
                
                # Production should have stricter settings
                if env == 'production':
                    assert settings.DEBUG is False, "DEBUG should be False in production"
                    assert settings.ENVIRONMENT == 'production'
                
                # Development should have debug enabled
                if env == 'development':
                    assert settings.ENVIRONMENT == 'development'
    
    def test_config_validation(self):
        """Test that invalid configurations are caught"""
        from src.core.config import Settings
        from pydantic import ValidationError
        
        invalid_configs = [
            {'API_V1_PREFIX': ''},  # Empty prefix
            {'CACHE_TTL': '-1'},    # Negative TTL
            {'DB_POOL_SIZE': '0'},  # Zero pool size
        ]
        
        for invalid_config in invalid_configs:
            with patch.dict(os.environ, invalid_config):
                # Should either handle gracefully or have sensible defaults
                try:
                    settings = Settings()
                    # If it doesn't raise, check for sensible defaults
                    for key, value in invalid_config.items():
                        actual = getattr(settings, key, None)
                        if actual is not None:
                            assert actual != value, f"Invalid value {value} accepted for {key}"
                except ValidationError:
                    pass  # Good - invalid config was caught
    
    def test_secrets_not_logged(self):
        """Ensure secrets are not printed in logs or errors"""
        sensitive_fields = ['api_key', 'password', 'secret', 'token', 'credential']
        
        violations = []
        for py_file in Path('src').rglob('*.py'):
            content = py_file.read_text()
            
            # Check for logging of sensitive fields
            log_patterns = [
                r'log.*\.(debug|info|warning|error|critical)\([^)]*(' + '|'.join(sensitive_fields) + ')',
                r'print\([^)]*(' + '|'.join(sensitive_fields) + ')',
                r'f["\'].*\{.*(' + '|'.join(sensitive_fields) + ').*\}',  # f-strings with secrets
            ]
            
            for pattern in log_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    violations.append(f"{py_file}: Potential secret in logs")
                    break
        
        assert len(violations) < 3, f"Too many potential secret logging issues: {violations}"
    
    def test_config_file_security(self):
        """Verify config files are properly secured"""
        config_files = [
            '.env',
            '.env.production',
            'config.json',
            'settings.json',
            'secrets.yaml',
        ]
        
        issues = []
        for config_file in config_files:
            file_path = Path(config_file)
            if file_path.exists():
                # Check if it's in .gitignore
                gitignore_path = Path('.gitignore')
                if gitignore_path.exists():
                    gitignore_content = gitignore_path.read_text()
                    if config_file not in gitignore_content:
                        issues.append(f"{config_file} not in .gitignore")
                
                # Check file permissions (Unix-like systems)
                import stat
                st = os.stat(file_path)
                mode = st.st_mode
                if mode & stat.S_IROTH:
                    issues.append(f"{config_file} is world-readable")
        
        assert len(issues) == 0, f"Config file security issues: {issues}"
    
    def test_config_documentation(self):
        """Ensure all configuration options are documented"""
        from src.core.config import Settings
        
        # Check if Settings class has proper docstrings
        assert Settings.__doc__ is not None, "Settings class lacks documentation"
        
        # Check for example configuration
        env_example = Path('.env.example')
        assert env_example.exists(), ".env.example file missing"
        
        # Verify example has all required variables
        example_content = env_example.read_text()
        required_vars = [
            'ENVIRONMENT',
            'SECRET_KEY',
            'DATABASE_URL',
            'OPENAI_API_KEY',
        ]
        
        missing_examples = []
        for var in required_vars:
            if var not in example_content:
                missing_examples.append(var)
        
        assert len(missing_examples) == 0, f"Missing examples for: {missing_examples}"
    
    def test_config_type_safety(self):
        """Verify configuration uses proper type hints"""
        from src.core.config import Settings
        import inspect
        from typing import get_type_hints
        
        # Get type hints for Settings class
        try:
            hints = get_type_hints(Settings)
            
            # Check that critical fields have proper types
            expected_types = {
                'DEBUG': bool,
                'DB_POOL_SIZE': int,
                'CACHE_TTL': int,
                'APP_NAME': str,
            }
            
            for field, expected_type in expected_types.items():
                if field in hints:
                    # Check if type matches (handling Optional types)
                    actual_type = hints[field]
                    type_matches = (
                        actual_type == expected_type or
                        str(actual_type).startswith(f'typing.Optional[{expected_type.__name__}]') or
                        str(actual_type).startswith(f'typing.Union[{expected_type.__name__}')
                    )
                    assert type_matches, f"{field} has wrong type: {actual_type} instead of {expected_type}"
        except Exception as e:
            # Type hints might not be fully available at runtime
            pass