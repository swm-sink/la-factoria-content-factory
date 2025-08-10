"""
Comprehensive test suite for the validation module.
Tests all security validation functions to ensure proper input sanitization.
"""

import pytest
from fastapi import HTTPException
from unittest.mock import patch
import html

from src.core.validation import (
    SecurityValidator,
    SecureContentRequest,
    validate_api_key,
    validate_query_params,
    validate_request_size,
    MAX_STRING_LENGTH,
    MAX_TOPIC_LENGTH,
    MAX_REQUIREMENTS_LENGTH,
    MAX_LIST_LENGTH,
    MAX_JSON_DEPTH
)


class TestSecurityValidator:
    """Test the SecurityValidator class methods"""
    
    def test_sanitize_string_valid_input(self):
        """Test sanitize_string with valid input"""
        result = SecurityValidator.sanitize_string("Valid input string")
        assert result == "Valid input string"
    
    def test_sanitize_string_html_escape(self):
        """Test that HTML special characters are escaped"""
        result = SecurityValidator.sanitize_string("Test <div> with \"quotes\"")
        assert result == "Test &lt;div&gt; with \"quotes\""
    
    def test_sanitize_string_whitespace_normalization(self):
        """Test whitespace normalization"""
        result = SecurityValidator.sanitize_string("  Multiple   spaces   ")
        assert result == "Multiple spaces"
    
    def test_sanitize_string_max_length(self):
        """Test maximum length validation"""
        with pytest.raises(HTTPException) as exc_info:
            SecurityValidator.sanitize_string("x" * 5001)
        assert exc_info.value.status_code == 422
        assert "exceeds maximum length" in exc_info.value.detail
    
    def test_sanitize_string_xss_patterns(self):
        """Test XSS pattern detection"""
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "onclick='alert()'",
            "<iframe src='evil.com'>",
        ]
        
        for dangerous_input in dangerous_inputs:
            with pytest.raises(HTTPException) as exc_info:
                SecurityValidator.sanitize_string(dangerous_input)
            assert exc_info.value.status_code == 422
            assert "Invalid characters or patterns" in exc_info.value.detail
    
    def test_sanitize_string_sql_injection_patterns(self):
        """Test SQL injection pattern detection"""
        # Note: The pattern requires semicolon before SQL commands
        dangerous_inputs = [
            "foo; DROP TABLE users",  # SQL command with semicolon
            "bar; DELETE FROM data",  # SQL command with semicolon
        ]
        
        for dangerous_input in dangerous_inputs:
            with pytest.raises(HTTPException) as exc_info:
                SecurityValidator.sanitize_string(dangerous_input)
            assert exc_info.value.status_code == 422
    
    def test_sanitize_string_path_traversal(self):
        """Test path traversal pattern detection"""
        with pytest.raises(HTTPException):
            SecurityValidator.sanitize_string("../../etc/passwd")
    
    def test_sanitize_string_null_bytes(self):
        """Test null byte detection and blocking"""
        # Null bytes are dangerous and should be rejected
        with pytest.raises(HTTPException) as exc_info:
            SecurityValidator.sanitize_string("test\x00string")
        assert exc_info.value.status_code == 422
    
    def test_sanitize_string_empty_after_sanitization(self):
        """Test error when string is empty after sanitization"""
        with pytest.raises(HTTPException) as exc_info:
            SecurityValidator.sanitize_string("   ")
        assert "cannot be empty" in exc_info.value.detail
    
    def test_sanitize_string_not_string(self):
        """Test error for non-string input"""
        with pytest.raises(HTTPException) as exc_info:
            SecurityValidator.sanitize_string(123)
        assert "must be a string" in exc_info.value.detail
    
    def test_validate_enum_value_valid(self):
        """Test enum validation with valid value"""
        result = SecurityValidator.validate_enum_value(
            "high_school", 
            ["elementary", "middle_school", "high_school"],
            "level"
        )
        assert result == "high_school"
    
    def test_validate_enum_value_invalid(self):
        """Test enum validation with invalid value"""
        with pytest.raises(HTTPException) as exc_info:
            SecurityValidator.validate_enum_value(
                "invalid",
                ["valid1", "valid2"],
                "field"
            )
        assert "Must be one of" in exc_info.value.detail
    
    def test_validate_list_length_valid(self):
        """Test list length validation with valid list"""
        result = SecurityValidator.validate_list_length([1, 2, 3], 5)
        assert result == [1, 2, 3]
    
    def test_validate_list_length_too_long(self):
        """Test list length validation with list too long"""
        with pytest.raises(HTTPException) as exc_info:
            SecurityValidator.validate_list_length([1] * 51)
        assert "exceeds maximum length" in exc_info.value.detail
    
    def test_validate_json_depth_valid(self):
        """Test JSON depth validation with valid nesting"""
        obj = {"level1": {"level2": {"level3": "value"}}}
        result = SecurityValidator.validate_json_depth(obj, max_depth=5)
        assert result == obj
    
    def test_validate_json_depth_too_deep(self):
        """Test JSON depth validation with excessive nesting"""
        # Create deeply nested object
        obj = {}
        current = obj
        for i in range(12):
            current[f"level{i}"] = {}
            current = current[f"level{i}"]
        
        with pytest.raises(HTTPException) as exc_info:
            SecurityValidator.validate_json_depth(obj, max_depth=10)
        assert "JSON nesting too deep" in exc_info.value.detail
    
    def test_validate_json_depth_with_list(self):
        """Test JSON depth validation with nested lists"""
        obj = [[[[[["too", "deep"]]]]]]
        with pytest.raises(HTTPException):
            SecurityValidator.validate_json_depth(obj, max_depth=5)


class TestSecureContentRequest:
    """Test the SecureContentRequest model"""
    
    def test_valid_request(self):
        """Test creating valid request"""
        request = SecureContentRequest(
            topic="Introduction to Python",
            learning_level="high_school",
            additional_requirements="Focus on practical examples"
        )
        assert request.topic == "Introduction to Python"
        assert request.learning_level == "high_school"
    
    def test_topic_too_short(self):
        """Test topic minimum length validation"""
        with pytest.raises(Exception):  # Pydantic validation error
            SecureContentRequest(topic="AB")
    
    def test_topic_sanitization(self):
        """Test topic sanitization in validator"""
        # This should trigger the field validator
        with pytest.raises(HTTPException):
            request = SecureContentRequest(
                topic="<script>alert('xss')</script>Python"
            )
    
    def test_learning_level_default(self):
        """Test default learning level"""
        request = SecureContentRequest(topic="Valid Topic")
        assert request.learning_level == "general"
    
    def test_learning_level_invalid(self):
        """Test invalid learning level"""
        with pytest.raises(HTTPException):
            SecureContentRequest(
                topic="Valid Topic",
                learning_level="invalid_level"
            )
    
    def test_additional_requirements_optional(self):
        """Test that additional requirements are optional"""
        request = SecureContentRequest(topic="Valid Topic")
        assert request.additional_requirements is None
    
    def test_whitespace_stripping(self):
        """Test automatic whitespace stripping"""
        request = SecureContentRequest(
            topic="  Python Basics  ",
            learning_level="  high_school  "
        )
        # Topic will be processed by validator
        assert request.learning_level == "high_school"  # ConfigDict strips whitespace


class TestValidateAPIKey:
    """Test the validate_api_key function"""
    
    def test_valid_api_key(self):
        """Test valid API key formats"""
        valid_keys = [
            "abcdef123456789012345678901234567890",
            "test_key_123.456-789",
            "a" * 32,
            "UPPERCASE_KEY_12345"
        ]
        
        for key in valid_keys:
            assert validate_api_key(key) is True
    
    def test_empty_api_key(self):
        """Test empty API key"""
        assert validate_api_key("") is False
        assert validate_api_key(None) is False
    
    def test_api_key_too_short(self):
        """Test API key that's too short"""
        assert validate_api_key("short") is False
    
    def test_api_key_too_long(self):
        """Test API key that's too long"""
        assert validate_api_key("x" * 257) is False
    
    def test_api_key_with_dangerous_patterns(self):
        """Test API key with dangerous patterns"""
        dangerous_keys = [
            "key_with_<script>",
            "key;DROP TABLE users",
            "../../etc/passwd",
            "key_with_null\x00byte"
        ]
        
        for key in dangerous_keys:
            assert validate_api_key(key) is False
    
    def test_api_key_invalid_characters(self):
        """Test API key with invalid characters"""
        invalid_keys = [
            "key with spaces",
            "key@with#special$chars",
            "key|with|pipes",
            "key&with&ampersands"
        ]
        
        for key in invalid_keys:
            assert validate_api_key(key) is False


class TestValidateQueryParams:
    """Test the validate_query_params function"""
    
    def test_valid_params(self):
        """Test valid query parameters"""
        params = {
            "limit": "10",
            "offset": "0",
            "sort": "created_at",
            "filter": "active"
        }
        result = validate_query_params(params)
        assert result["limit"] == 10
        assert result["offset"] == 0
        assert result["sort"] == "created_at"
        assert result["filter"] == "active"
    
    def test_invalid_param_name(self):
        """Test invalid parameter name"""
        with pytest.raises(HTTPException) as exc_info:
            validate_query_params({"invalid-name!": "value"})
        assert "Invalid parameter name" in exc_info.value.detail
    
    def test_negative_numeric_params(self):
        """Test negative values for numeric parameters"""
        with pytest.raises(HTTPException) as exc_info:
            validate_query_params({"limit": "-1"})
        assert "must be a non-negative integer" in exc_info.value.detail
    
    def test_limit_capping(self):
        """Test that limit is capped at 1000"""
        result = validate_query_params({"limit": "5000"})
        assert result["limit"] == 1000
    
    def test_sort_sanitization(self):
        """Test sort parameter sanitization"""
        result = validate_query_params({"sort": "name; DROP TABLE"})
        assert "DROP" not in result["sort"]
        assert ";" not in result["sort"]
    
    def test_string_param_sanitization(self):
        """Test general string parameter sanitization"""
        result = validate_query_params({"custom": "test<script>alert()</script>"})
        # Should be HTML escaped
        assert "<script>" not in result["custom"]
    
    def test_non_string_sort(self):
        """Test non-string sort parameter"""
        with pytest.raises(HTTPException) as exc_info:
            validate_query_params({"sort": 123})
        assert "must be a string" in exc_info.value.detail


class TestValidateRequestSize:
    """Test the validate_request_size function"""
    
    @pytest.mark.asyncio
    async def test_valid_request_size(self):
        """Test request within size limit"""
        request_body = b"x" * 1024  # 1KB
        # Should not raise
        await validate_request_size(request_body, max_size=1024 * 1024)
    
    @pytest.mark.asyncio
    async def test_request_too_large(self):
        """Test request exceeding size limit"""
        request_body = b"x" * (1024 * 1024 + 1)  # Just over 1MB
        with pytest.raises(HTTPException) as exc_info:
            await validate_request_size(request_body, max_size=1024 * 1024)
        assert exc_info.value.status_code == 413
        assert "too large" in exc_info.value.detail.lower()


class TestIntegration:
    """Integration tests for validation module"""
    
    def test_full_content_request_validation(self):
        """Test complete content request validation flow"""
        # Valid request should work
        request = SecureContentRequest(
            topic="Introduction to Machine Learning",
            learning_level="college",
            additional_requirements="Include Python examples"
        )
        assert request.topic == "Introduction to Machine Learning"
        
        # Dangerous content should be blocked
        with pytest.raises(HTTPException):
            SecureContentRequest(
                topic="<iframe src='evil.com'>ML</iframe>",
                learning_level="college"
            )
    
    def test_query_params_full_flow(self):
        """Test full query parameter validation flow"""
        params = {
            "limit": "50",
            "offset": "10",
            "sort": "name,created_at",
            "filter": "status:active",
            "search": "python programming"
        }
        
        result = validate_query_params(params)
        
        assert isinstance(result["limit"], int)
        assert isinstance(result["offset"], int)
        assert "," in result["sort"]  # Comma preserved
        assert ":" in result["filter"]  # Colon preserved
        assert "python programming" in result["search"]
    
    @pytest.mark.asyncio
    async def test_request_size_with_different_sizes(self):
        """Test request size validation with various sizes"""
        sizes = [
            (100, True),      # 100 bytes - should pass
            (1024, True),     # 1KB - should pass
            (1024 * 512, True),  # 512KB - should pass
            (1024 * 1024, True),  # 1MB - should pass
            (1024 * 1024 + 1, False),  # Just over 1MB - should fail
            (1024 * 1024 * 2, False),  # 2MB - should fail
        ]
        
        for size, should_pass in sizes:
            request_body = b"x" * size
            
            if should_pass:
                # Should not raise
                await validate_request_size(request_body)
            else:
                with pytest.raises(HTTPException):
                    await validate_request_size(request_body)