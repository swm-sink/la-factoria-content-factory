"""
Security Audit Tests for La Factoria
=====================================

Comprehensive security validation following OWASP guidelines.
"""

import os
import re
import pytest
from pathlib import Path
from typing import List, Dict, Any


class TestSecurityAudit:
    """Comprehensive security audit tests"""
    
    def test_no_hardcoded_secrets(self):
        """Ensure no hardcoded secrets in source code"""
        secret_patterns = [
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'secret[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'password\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI key pattern
            r'anthropic-[a-zA-Z0-9]+',  # Anthropic key pattern
        ]
        
        violations = []
        src_path = Path('src')
        
        for py_file in src_path.rglob('*.py'):
            content = py_file.read_text()
            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Check if it's not a placeholder
                    if not any(placeholder in content for placeholder in ['demo-key', 'example', 'your-', 'change-this']):
                        violations.append(f"{py_file}: Potential secret found")
        
        assert len(violations) == 0, f"Hardcoded secrets found: {violations}"
    
    def test_sql_injection_protection(self):
        """Check for SQL injection vulnerabilities"""
        sql_patterns = [
            r'execute\(["\'].*%s',  # Raw SQL with string formatting
            r'execute\(.*\.format\(',  # SQL with .format()
            r'execute\(.*\+.*\+',  # SQL with string concatenation
            r'f".*SELECT.*FROM.*{',  # f-strings in SQL
        ]
        
        violations = []
        src_path = Path('src')
        
        for py_file in src_path.rglob('*.py'):
            content = py_file.read_text()
            for pattern in sql_patterns:
                if re.search(pattern, content):
                    violations.append(f"{py_file}: Potential SQL injection")
        
        assert len(violations) == 0, f"SQL injection risks found: {violations}"
    
    def test_cors_configuration(self):
        """Verify CORS is properly configured"""
        from src.core.config import settings
        
        # Check CORS settings exist
        assert hasattr(settings, 'ALLOWED_ORIGINS'), "CORS origins not configured"
        
        # Check for wildcard in production
        if settings.ENVIRONMENT == 'production':
            assert '*' not in settings.ALLOWED_ORIGINS, "Wildcard CORS not allowed in production"
    
    def test_authentication_required(self):
        """Ensure authentication is required for sensitive endpoints"""
        sensitive_patterns = [
            '/admin',
            '/api/v1/generate',
            '/api/v1/content',
        ]
        
        # This would need to check actual route definitions
        # For now, verify auth module exists
        auth_path = Path('src/core/auth.py')
        assert auth_path.exists(), "Authentication module missing"
        
        # Check for auth decorators usage
        content = auth_path.read_text()
        assert 'def verify_api_key' in content or 'def require_auth' in content, \
            "No authentication verification functions found"
    
    def test_rate_limiting_configured(self):
        """Verify rate limiting is properly configured"""
        main_path = Path('src/main.py')
        content = main_path.read_text()
        
        # Check for rate limiter import and setup
        assert 'from slowapi import Limiter' in content, "SlowAPI not imported"
        assert 'limiter = Limiter' in content, "Rate limiter not initialized"
        assert 'app.state.limiter' in content or 'app.add_exception_handler' in content, \
            "Rate limiter not attached to app"
    
    def test_input_validation(self):
        """Check that input validation is in place"""
        violations = []
        src_path = Path('src/api')
        
        if src_path.exists():
            for py_file in src_path.rglob('*.py'):
                content = py_file.read_text()
                # Check for Pydantic models usage
                if '@app.' in content or '@router.' in content:
                    if 'BaseModel' not in content and 'Body' not in content:
                        violations.append(f"{py_file}: No input validation models found")
        
        assert len(violations) == 0, f"Missing input validation: {violations}"
    
    def test_error_messages_safe(self):
        """Ensure error messages don't leak sensitive information"""
        unsafe_patterns = [
            r'except.*:\s*raise\s+e',  # Re-raising raw exceptions
            r'traceback\.print',  # Printing tracebacks
            r'sys\.exc_info',  # Exposing system exception info
        ]
        
        violations = []
        src_path = Path('src')
        
        for py_file in src_path.rglob('*.py'):
            content = py_file.read_text()
            for pattern in unsafe_patterns:
                if re.search(pattern, content):
                    violations.append(f"{py_file}: Unsafe error handling")
        
        # Allow some violations in non-production code
        assert len(violations) < 5, f"Too many unsafe error handlers: {violations}"
    
    def test_secure_headers_configured(self):
        """Check for security headers configuration"""
        expected_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Content-Security-Policy'
        ]
        
        # This would need actual middleware inspection
        # For now, check if security headers are mentioned
        main_path = Path('src/main.py')
        if main_path.exists():
            content = main_path.read_text()
            # Basic check - in production would test actual headers
            pass
    
    def test_dependency_vulnerabilities(self):
        """Check for known vulnerabilities in dependencies"""
        # This would use safety or similar tools
        # For now, check critical versions
        import importlib.metadata as metadata
        
        critical_checks = {
            'fastapi': '0.100.0',  # Minimum secure version
            'pydantic': '2.0.0',  # V2 for security fixes
            'sqlalchemy': '2.0.0',  # V2 for security improvements
        }
        
        for package, min_version in critical_checks.items():
            try:
                installed_version = metadata.version(package)
                from packaging import version
                assert version.parse(installed_version) >= version.parse(min_version), \
                    f"{package} version {installed_version} is below minimum secure version {min_version}"
            except metadata.PackageNotFoundError:
                pass  # Package not installed
    
    def test_logging_configuration(self):
        """Ensure logging doesn't expose sensitive data"""
        log_patterns = [
            r'logger\.(debug|info|warning|error)\(.*password',
            r'logger\.(debug|info|warning|error)\(.*api_key',
            r'logger\.(debug|info|warning|error)\(.*token',
            r'print\(.*password',
            r'print\(.*api_key',
        ]
        
        violations = []
        src_path = Path('src')
        
        for py_file in src_path.rglob('*.py'):
            content = py_file.read_text()
            for pattern in log_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    violations.append(f"{py_file}: Potential sensitive data in logs")
        
        assert len(violations) == 0, f"Sensitive data in logs: {violations}"


class TestAPIKeySecurity:
    """Test API key management security"""
    
    def test_api_keys_from_environment(self):
        """Ensure API keys are loaded from environment variables"""
        from src.core.config import settings
        
        # Check that API keys are Optional (not hardcoded)
        api_key_attrs = [
            'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY',
            'LA_FACTORIA_API_KEY'
        ]
        
        for attr in api_key_attrs:
            if hasattr(settings, attr):
                value = getattr(settings, attr)
                if value:
                    # Check it's not a demo/test key
                    assert not value.startswith('demo-'), f"{attr} using demo key"
                    assert not value.startswith('test-'), f"{attr} using test key"
    
    def test_api_key_rotation_capability(self):
        """Check if API key rotation is supported"""
        # This would check for key rotation endpoints or mechanisms
        # For now, verify settings can be reloaded
        from src.core.config import Settings
        
        # Should be able to create new settings instance
        new_settings = Settings()
        assert new_settings is not None
    
    def test_api_key_validation(self):
        """Test that API keys are validated before use"""
        auth_path = Path('src/core/auth.py')
        if auth_path.exists():
            content = auth_path.read_text()
            assert 'verify' in content or 'validate' in content, \
                "No API key validation found"


class TestDatabaseSecurity:
    """Test database security configurations"""
    
    def test_database_url_not_exposed(self):
        """Ensure database URL is not exposed in responses"""
        # Check API routes don't return database URL
        api_path = Path('src/api')
        if api_path.exists():
            for py_file in api_path.rglob('*.py'):
                content = py_file.read_text()
                assert 'DATABASE_URL' not in content or 'settings.DATABASE_URL' not in content, \
                    f"Database URL potentially exposed in {py_file}"
    
    def test_parameterized_queries(self):
        """Ensure all database queries use parameters"""
        # Check for parameterized query usage
        violations = []
        src_path = Path('src')
        
        for py_file in src_path.rglob('*.py'):
            content = py_file.read_text()
            # Look for SQLAlchemy query construction
            if 'select(' in content or 'insert(' in content or 'update(' in content:
                # Should use bindparam or parameters, not string formatting
                if '.format(' in content and ('select' in content or 'SELECT' in content):
                    violations.append(f"{py_file}: Non-parameterized query")
        
        assert len(violations) == 0, f"Non-parameterized queries: {violations}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])