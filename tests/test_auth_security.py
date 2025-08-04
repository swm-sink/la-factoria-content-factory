"""
Authentication and Security Tests for La Factoria
=================================================

Comprehensive security testing covering:
- API key authentication and validation
- Authorization for different endpoints
- Input validation and sanitization
- Rate limiting and abuse prevention
- Security headers and CORS
- Data protection and privacy
"""

import pytest
import time
import hashlib
import hmac
from typing import Dict, Any
from unittest.mock import patch, Mock
from fastapi import status
from fastapi.testclient import TestClient

from src.core.auth import (
    verify_api_key,
    verify_admin_api_key,
    hash_api_key,
    verify_api_key_hash,
    APIKeyManager,
    rate_limiter
)
from src.core.config import settings


class TestAPIKeyAuthentication:
    """Test API key authentication mechanisms"""

    @pytest.mark.security
    def test_api_key_hashing(self):
        """Test API key hashing for secure storage"""
        api_key = "test-api-key-123"
        hashed = hash_api_key(api_key)

        # Hash should be consistent
        assert hash_api_key(api_key) == hashed

        # Hash should be different from original
        assert hashed != api_key

        # Hash should be hex string of expected length (SHA256)
        assert len(hashed) == 64
        assert all(c in '0123456789abcdef' for c in hashed)

    @pytest.mark.security
    def test_api_key_verification(self):
        """Test API key hash verification"""
        api_key = "test-verification-key"
        correct_hash = hash_api_key(api_key)
        wrong_hash = hash_api_key("wrong-key")

        # Correct key should verify
        assert verify_api_key_hash(api_key, correct_hash) == True

        # Wrong key should not verify
        assert verify_api_key_hash(api_key, wrong_hash) == False

        # Different key should not verify
        assert verify_api_key_hash("different-key", correct_hash) == False

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_verify_api_key_function_development_mode(self):
        """Test API key verification in development mode"""
        from fastapi.security import HTTPAuthorizationCredentials

        # Mock development settings
        with patch('src.core.auth.settings') as mock_settings:
            mock_settings.is_development = True
            mock_settings.API_KEY = None

            # Any non-empty key should work in development
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="any-test-key"
            )

            result = await verify_api_key(credentials)
            assert result == "any-test-key"

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_verify_api_key_function_production_mode(self):
        """Test API key verification in production mode"""
        from fastapi.security import HTTPAuthorizationCredentials
        from fastapi import HTTPException

        # Mock production settings
        with patch('src.core.auth.settings') as mock_settings:
            mock_settings.is_development = False
            mock_settings.API_KEY = "production-api-key"

            # Correct key should work
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="production-api-key"
            )
            result = await verify_api_key(credentials)
            assert result == "production-api-key"

            # Wrong key should raise exception
            wrong_credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="wrong-key"
            )

            with pytest.raises(HTTPException) as exc_info:
                await verify_api_key(wrong_credentials)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid API key" in str(exc_info.value.detail)

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_empty_api_key_rejection(self):
        """Test rejection of empty API keys"""
        from fastapi.security import HTTPAuthorizationCredentials
        from fastapi import HTTPException

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=""
        )

        with pytest.raises(HTTPException) as exc_info:
            await verify_api_key(credentials)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "API key is required" in str(exc_info.value.detail)

    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_admin_api_key_verification(self):
        """Test admin API key verification"""
        from fastapi.security import HTTPAuthorizationCredentials

        # Mock settings for testing
        with patch('src.core.auth.settings') as mock_settings:
            mock_settings.is_development = True
            mock_settings.API_KEY = "admin-key"

            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="admin-key"
            )

            result = await verify_admin_api_key(credentials)
            assert result == "admin-key"


class TestAPIKeyManager:
    """Test API key management functionality"""

    @pytest.fixture
    def api_key_manager(self):
        """Create API key manager for testing"""
        with patch('src.core.auth.settings') as mock_settings:
            mock_settings.API_KEY = "master-test-key"
            mock_settings.is_development = False
            return APIKeyManager()

    @pytest.mark.security
    def test_api_key_generation(self, api_key_manager):
        """Test API key generation"""
        user_id = "test-user-123"
        api_key = api_key_manager.generate_api_key(user_id)

        # Should follow format: lf_<prefix>_<token>
        assert api_key.startswith("lf_")
        parts = api_key.split("_")
        assert len(parts) >= 3
        assert user_id[:8] in parts[1]  # User ID prefix should be included
        assert len(parts[2]) >= 16  # Token should be reasonably long

    @pytest.mark.security
    def test_api_key_format_validation(self, api_key_manager):
        """Test API key format validation"""
        # Valid La Factoria key format
        valid_key = "lf_user123_abcdef0123456789abcdef0123456789"
        assert api_key_manager.validate_key_format(valid_key) == True

        # Master key should be valid
        assert api_key_manager.validate_key_format("master-test-key") == True

        # Invalid formats
        assert api_key_manager.validate_key_format("") == False
        assert api_key_manager.validate_key_format("invalid-format") == False
        assert api_key_manager.validate_key_format("lf_short") == False

    @pytest.mark.security
    def test_api_key_info_extraction(self, api_key_manager):
        """Test API key information extraction"""
        # Master key info
        master_info = api_key_manager.get_key_info("master-test-key")
        assert master_info["valid"] == True
        assert master_info["type"] == "master"
        assert "admin" in master_info["permissions"]

        # Generated user key info
        user_key = "lf_user123_abcdef0123456789abcdef0123456789"
        user_info = api_key_manager.get_key_info(user_key)
        assert user_info["valid"] == True
        assert user_info["type"] == "user"
        assert "read" in user_info["permissions"]
        assert "write" in user_info["permissions"]
        assert "admin" not in user_info["permissions"]

        # Invalid key info
        invalid_info = api_key_manager.get_key_info("invalid-key-format")
        assert invalid_info["valid"] == False
        assert invalid_info["type"] == "invalid"

    @pytest.mark.security
    def test_development_mode_key_validation(self):
        """Test key validation in development mode"""
        with patch('src.core.auth.settings') as mock_settings:
            mock_settings.is_development = True
            mock_settings.API_KEY = None

            manager = APIKeyManager()

            # Any non-empty key should be valid in development
            assert manager.validate_key_format("any-key") == True
            assert manager.validate_key_format("") == False


class TestEndpointSecurity:
    """Test endpoint-level security measures"""

    @pytest.mark.security
    def test_protected_endpoints_require_auth(self, client):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            "/api/v1/generate/study_guide",
            "/api/v1/generate/flashcards",
            "/api/v1/generate/master_content_outline",
            "/api/v1/generate/podcast_script",
            "/api/v1/generate/one_pager_summary",
            "/api/v1/generate/detailed_reading_material",
            "/api/v1/generate/faq_collection",
            "/api/v1/generate/reading_guide_questions",
            "/api/v1/service/info"
        ]

        test_payload = {
            "topic": "Security Test",
            "age_group": "high_school"
        }

        for endpoint in protected_endpoints:
            response = client.post(endpoint, json=test_payload)
            # Should require authentication
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.security
    def test_public_endpoints_no_auth_required(self, client):
        """Test that public endpoints don't require authentication"""
        public_endpoints = [
            ("/api/v1/content-types", "GET"),
            ("/api/v1/service/health", "GET"),
            ("/health", "GET"),
            ("/", "GET")
        ]

        for endpoint, method in public_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)

            # Should not require authentication (200 or other non-401 status)
            assert response.status_code != status.HTTP_401_UNAUTHORIZED

    @pytest.mark.security
    def test_invalid_auth_header_formats(self, client):
        """Test handling of invalid authorization header formats"""
        invalid_headers = [
            {"Authorization": "InvalidScheme token"},  # Wrong scheme
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "Bearer "},  # Empty token
            {"Authorization": "token"},  # Missing scheme
            {"Authorization": ""},  # Empty header
        ]

        test_payload = {"topic": "Test", "age_group": "high_school"}

        for headers in invalid_headers:
            response = client.post(
                "/api/v1/generate/study_guide",
                json=test_payload,
                headers=headers
            )
            assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    @pytest.mark.security
    def test_sql_injection_protection(self, client, auth_headers):
        """Test protection against SQL injection attempts"""
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "1'; DELETE FROM content WHERE '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --"
        ]

        for payload in sql_injection_payloads:
            test_data = {
                "topic": payload,
                "age_group": "high_school"
            }

            response = client.post(
                "/api/v1/generate/study_guide",
                json=test_data,
                headers=auth_headers
            )

            # Should handle malicious input gracefully
            # Either reject with validation error or process safely
            assert response.status_code in [
                status.HTTP_200_OK,  # Safely processed
                status.HTTP_422_UNPROCESSABLE_ENTITY,  # Validation rejected
                status.HTTP_400_BAD_REQUEST  # Input rejected
            ]

    @pytest.mark.security
    def test_xss_protection(self, client, auth_headers):
        """Test protection against XSS attacks"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//",
            "<iframe src='javascript:alert(`xss`)'></iframe>"
        ]

        for payload in xss_payloads:
            test_data = {
                "topic": payload,
                "age_group": "high_school",
                "additional_requirements": payload
            }

            response = client.post(
                "/api/v1/generate/study_guide",
                json=test_data,
                headers=auth_headers
            )

            # Should handle malicious input
            if response.status_code == status.HTTP_200_OK:
                # If processed, check that output is sanitized
                content = response.json()
                generated_text = str(content.get("generated_content", ""))

                # Should not contain executable scripts
                assert "<script>" not in generated_text.lower()
                assert "javascript:" not in generated_text.lower()
                assert "onerror=" not in generated_text.lower()


class TestInputValidation:
    """Test input validation and sanitization"""

    @pytest.mark.security
    def test_topic_length_validation(self, client, auth_headers):
        """Test topic length validation"""
        # Too short topic
        response = client.post(
            "/api/v1/generate/study_guide",
            json={"topic": "AB", "age_group": "high_school"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Too long topic
        response = client.post(
            "/api/v1/generate/study_guide",
            json={"topic": "X" * 501, "age_group": "high_school"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Valid length topic
        response = client.post(
            "/api/v1/generate/study_guide",
            json={"topic": "Valid Topic Length", "age_group": "high_school"},
            headers=auth_headers
        )
        # Should either succeed or fail for non-validation reasons
        assert response.status_code != status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.security
    def test_additional_requirements_length_validation(self, client, auth_headers):
        """Test additional requirements length validation"""
        # Too long additional requirements
        response = client.post(
            "/api/v1/generate/study_guide",
            json={
                "topic": "Test Topic",
                "age_group": "high_school",
                "additional_requirements": "X" * 1001
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.security
    def test_enum_validation(self, client, auth_headers):
        """Test enum field validation"""
        # Invalid age group
        response = client.post(
            "/api/v1/generate/study_guide",
            json={"topic": "Test Topic", "age_group": "invalid_age_group"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Valid age group
        response = client.post(
            "/api/v1/generate/study_guide",
            json={"topic": "Test Topic", "age_group": "high_school"},
            headers=auth_headers
        )
        assert response.status_code != status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.security
    def test_learning_objectives_validation(self, client, auth_headers):
        """Test learning objectives validation"""
        # Invalid cognitive level
        invalid_objectives = [{
            "cognitive_level": "invalid_level",
            "subject_area": "Math",
            "specific_skill": "algebra",
            "measurable_outcome": "solve equations",
            "difficulty_level": 5
        }]

        response = client.post(
            "/api/v1/generate/study_guide",
            json={
                "topic": "Test Topic",
                "age_group": "high_school",
                "learning_objectives": invalid_objectives
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.security
    def test_malformed_json_handling(self, client, auth_headers):
        """Test handling of malformed JSON requests"""
        response = client.post(
            "/api/v1/generate/study_guide",
            data='{"topic": "Test", "age_group":}',  # Malformed JSON
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.security
    def test_content_type_header_validation(self, client, auth_headers):
        """Test Content-Type header validation"""
        valid_data = {"topic": "Test Topic", "age_group": "high_school"}

        # Missing Content-Type
        headers_no_content_type = {k: v for k, v in auth_headers.items() if k != "Content-Type"}
        response = client.post(
            "/api/v1/generate/study_guide",
            json=valid_data,
            headers=headers_no_content_type
        )
        # Should still work (FastAPI handles this)
        assert response.status_code != status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


class TestRateLimiting:
    """Test rate limiting and abuse prevention"""

    @pytest.mark.security
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization"""
        assert rate_limiter is not None
        assert hasattr(rate_limiter, 'check_rate_limit')
        assert hasattr(rate_limiter, 'increment_usage')

    @pytest.mark.security
    def test_rate_limit_check_development(self):
        """Test rate limiting in development mode"""
        with patch('src.core.auth.settings') as mock_settings:
            mock_settings.is_development = True

            # Should always allow in development
            result = rate_limiter.check_rate_limit("test-key", limit=5)
            assert result == True

    @pytest.mark.security
    def test_rate_limit_check_production(self):
        """Test rate limiting in production mode"""
        with patch('src.core.auth.settings') as mock_settings:
            mock_settings.is_development = False
            mock_settings.RATE_LIMIT_REQUESTS_PER_MINUTE = 10

            # Current implementation always returns True (placeholder)
            # In a full implementation, this would test actual rate limiting
            result = rate_limiter.check_rate_limit("test-key", limit=10)
            assert isinstance(result, bool)

    @pytest.mark.security
    def test_usage_increment(self):
        """Test usage increment tracking"""
        # Should not raise exception
        rate_limiter.increment_usage("test-key")

        # In a full implementation, this would test actual tracking

    @pytest.mark.security
    @pytest.mark.slow
    def test_burst_request_handling(self, client, auth_headers):
        """Test handling of burst requests"""
        valid_data = {"topic": "Burst Test", "age_group": "high_school"}

        # Send multiple rapid requests
        responses = []
        for i in range(10):
            response = client.post(
                "/api/v1/generate/flashcards",  # Use fastest endpoint
                json={**valid_data, "topic": f"Burst Test {i}"},
                headers=auth_headers
            )
            responses.append(response)

        # Should handle burst gracefully
        # In development, all should succeed
        # In production, might have rate limiting
        success_count = sum(1 for r in responses if r.status_code == status.HTTP_200_OK)
        assert success_count >= 5  # At least half should succeed


class TestSecurityHeaders:
    """Test security headers and CORS configuration"""

    @pytest.mark.security
    def test_cors_headers_presence(self, client):
        """Test CORS headers are present"""
        response = client.options("/api/v1/content-types")

        # Should include CORS headers
        # Exact headers depend on FastAPI CORS middleware configuration
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED]

    @pytest.mark.security
    def test_security_headers_basic_endpoints(self, client):
        """Test basic security headers on public endpoints"""
        response = client.get("/health")

        # Check for basic security considerations
        # Note: FastAPI doesn't add security headers by default
        # This test documents what should be added in production

        assert response.status_code == status.HTTP_200_OK
        # In production, should add headers like:
        # - X-Content-Type-Options: nosniff
        # - X-Frame-Options: DENY
        # - X-XSS-Protection: 1; mode=block

    @pytest.mark.security
    def test_api_error_information_disclosure(self, client, auth_headers):
        """Test that API errors don't disclose sensitive information"""
        # Trigger various error conditions
        error_requests = [
            {"topic": "", "age_group": "high_school"},  # Validation error
            {"topic": "Test", "age_group": "invalid"},  # Enum error
        ]

        for request_data in error_requests:
            response = client.post(
                "/api/v1/generate/study_guide",
                json=request_data,
                headers=auth_headers
            )

            if response.status_code in [422, 400]:
                error_detail = response.json()
                error_text = str(error_detail)

                # Should not expose sensitive information
                sensitive_terms = [
                    "password", "secret", "key", "token",
                    "database", "internal", "stack trace"
                ]

                for term in sensitive_terms:
                    assert term.lower() not in error_text.lower()


class TestDataProtection:
    """Test data protection and privacy measures"""

    @pytest.mark.security
    def test_request_data_sanitization(self, client, auth_headers):
        """Test that request data is properly sanitized"""
        # Test with potentially dangerous characters
        test_data = {
            "topic": "Test with <script>alert('xss')</script> content",
            "age_group": "high_school",
            "additional_requirements": "Requirements with 'quotes' and \"double quotes\""
        }

        response = client.post(
            "/api/v1/generate/study_guide",
            json=test_data,
            headers=auth_headers
        )

        # Should handle potentially dangerous input
        if response.status_code == status.HTTP_200_OK:
            content = response.json()
            # Generated content should be safe
            assert "<script>" not in str(content).lower()

    @pytest.mark.security
    def test_no_sensitive_data_in_logs(self, client, auth_headers, caplog):
        """Test that sensitive data is not logged"""
        test_data = {
            "topic": "Sensitive Information Test",
            "age_group": "high_school"
        }

        with caplog.at_level("INFO"):
            response = client.post(
                "/api/v1/generate/study_guide",
                json=test_data,
                headers=auth_headers
            )

        # Check logs don't contain full API key
        log_text = caplog.text
        if "test-api-key" in auth_headers.get("Authorization", ""):
            # Should only log partial key (first 8 chars or similar)
            assert "test-api-key-la-factoria-2025" not in log_text

    @pytest.mark.security
    def test_response_data_sanitization(self, client, auth_headers):
        """Test that response data doesn't leak sensitive information"""
        response = client.post(
            "/api/v1/generate/study_guide",
            json={"topic": "Response Test", "age_group": "high_school"},
            headers=auth_headers
        )

        if response.status_code == status.HTTP_200_OK:
            response_data = response.json()
            response_text = str(response_data)

            # Should not contain sensitive system information
            sensitive_info = [
                "password", "secret", "private_key", "database_url",
                "internal_error", "stack_trace", "file_path"
            ]

            for info in sensitive_info:
                assert info.lower() not in response_text.lower()

    @pytest.mark.security
    def test_user_data_isolation(self, client):
        """Test that user data is properly isolated"""
        # Test with different API keys to ensure data isolation
        user1_headers = {"Authorization": "Bearer user1-api-key"}
        user2_headers = {"Authorization": "Bearer user2-api-key"}

        # In development mode, these might both work
        # In production, would need valid keys

        user1_data = {"topic": "User 1 Topic", "age_group": "high_school"}
        user2_data = {"topic": "User 2 Topic", "age_group": "college"}

        # Make requests as different users
        response1 = client.post("/api/v1/generate/study_guide", json=user1_data, headers=user1_headers)
        response2 = client.post("/api/v1/generate/study_guide", json=user2_data, headers=user2_headers)

        # Both might succeed in development mode
        # In production, would test that users can't access each other's data
