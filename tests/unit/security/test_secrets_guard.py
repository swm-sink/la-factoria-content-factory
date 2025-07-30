"""Tests for secrets guard functionality."""

import pytest
from unittest.mock import patch, MagicMock

from scripts.secrets_guard import SecretsGuard


class TestSecretsGuard:
    """Test secrets detection and prevention."""

    @pytest.fixture
    def guard(self):
        """Create SecretsGuard instance."""
        return SecretsGuard()

    def test_safe_content_detection(self, guard):
        """Test detection of safe placeholder content."""
        safe_contents = [
            "your-api-key-here",
            "GEMINI_API_KEY=your-gemini-api-key-here",
            "sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "AIzaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "AKIAXXXXXXXXXXXXXXXX",
        ]
        
        for content in safe_contents:
            assert guard.is_safe_content(content), f"Should be safe: {content}"

    def test_real_secrets_detection(self, guard):
        """Test detection of real secrets."""
        test_cases = [
            ("google_api_key", "AIzaSyDxKXxxxxxxxxxxxxxxxxxxxxxxxxxxx"),
            ("openai_api_key", "sk-abcdefghijklmnopqrstuvwxyz1234567890123456789012"),
            ("aws_access_key", "AKIA1234567890123456"),
            ("db_url_with_creds", "postgres://user:password@host:5432/db"),
            ("private_key", "-----BEGIN RSA PRIVATE KEY-----"),
        ]
        
        for pattern_name, secret in test_cases:
            findings = guard.scan_content(secret, "test.py")
            assert len(findings) > 0, f"Should detect {pattern_name}: {secret}"
            assert findings[0]['pattern'] == pattern_name

    def test_env_secret_detection(self, guard):
        """Test detection of environment variable secrets."""
        env_content = """
# Safe examples
GEMINI_API_KEY=your-gemini-api-key-here
DATABASE_URL=postgresql://localhost/testdb

# Actual secrets (should be caught)
JWT_SECRET=abcdef1234567890abcdef1234567890
API_KEY=sk-real1234567890abcdef1234567890abcdef123456
        """
        
        findings = guard.scan_content(env_content, ".env")
        
        # Should find real secrets but not placeholders
        secret_findings = [f for f in findings if not guard.is_safe_content(f['match'])]
        assert len(secret_findings) > 0, "Should detect actual secrets"

    def test_should_scan_file(self, guard):
        """Test file scanning filter."""
        # Should scan
        assert guard._should_scan_file("app/main.py")
        assert guard._should_scan_file("config.yaml")
        assert guard._should_scan_file(".env")
        
        # Should skip
        assert not guard._should_scan_file("image.png")
        assert not guard._should_scan_file("package-lock.json")
        assert not guard._should_scan_file("binary.zip")

    @patch('subprocess.run')
    def test_check_staged_files_no_secrets(self, mock_run, guard):
        """Test checking staged files with no secrets."""
        # Mock git diff output
        mock_run.side_effect = [
            MagicMock(stdout="app/main.py\nREADME.md", returncode=0),  # git diff --cached --name-only
            MagicMock(stdout="print('Hello World')", returncode=0),   # git show :app/main.py
            MagicMock(stdout="# README\nThis is safe content", returncode=0),  # git show :README.md
        ]
        
        findings = guard.check_staged_files()
        assert len(findings) == 0, "Should find no secrets in safe content"

    @patch('subprocess.run')
    def test_check_staged_files_with_secrets(self, mock_run, guard):
        """Test checking staged files with secrets."""
        # Mock git diff output
        mock_run.side_effect = [
            MagicMock(stdout="config.py", returncode=0),  # git diff --cached --name-only
            MagicMock(stdout="API_KEY = 'AIzaSyDxKXxxxxxxxxxxxxxxxxxxxxxxxxxxx'", returncode=0),  # git show :config.py
        ]
        
        findings = guard.check_staged_files()
        assert len(findings) > 0, "Should find secrets in staged content"
        assert findings[0]['pattern'] == 'google_api_key'

    @patch('subprocess.run')
    def test_check_staged_files_git_error(self, mock_run, guard):
        """Test handling of git errors."""
        # Mock git command failure
        mock_run.side_effect = [
            MagicMock(returncode=1),  # git diff --cached --name-only fails
        ]
        
        findings = guard.check_staged_files()
        assert len(findings) == 0, "Should handle git errors gracefully"

    def test_pattern_specificity(self, guard):
        """Test that patterns are specific enough to avoid false positives."""
        # Common false positives that should NOT be detected
        false_positives = [
            "EnhancedMultiStepContentGenerationService",  # Long class name
            "function_name_with_40_characters_exactly_123",  # Function name
            "this_is_just_a_long_variable_name_in_code_12345",  # Variable name
            "# This is a comment with some random text 1234567890",  # Comment
        ]
        
        for content in false_positives:
            findings = guard.scan_content(content, "test.py")
            # Filter out any findings that match our safe patterns
            real_findings = [f for f in findings if not guard.is_safe_content(f['match'])]
            assert len(real_findings) == 0, f"Should not detect false positive: {content}"

    def test_secret_truncation(self, guard):
        """Test that long secrets are truncated in output."""
        long_secret = "sk-" + "a" * 100  # Very long secret
        findings = guard.scan_content(f"API_KEY={long_secret}", "test.py")
        
        if findings:
            # Secret should be truncated to 20 chars + "..."
            assert len(findings[0]['match']) <= 23, "Secret should be truncated"
            assert "..." in findings[0]['match'] or len(findings[0]['match']) <= 20