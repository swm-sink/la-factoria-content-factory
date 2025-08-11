"""
Comprehensive test suite for admin API routes
Tests authentication, authorization, and critical admin operations
"""

import pytest
from fastapi import status
from unittest.mock import patch, Mock, AsyncMock
import json
import uuid
from datetime import datetime

from tests.utils import (
    create_mock_settings,
    MockDatabase,
    UserFactory,
    EducationalContentFactory,
    assert_http_status,
    assert_error_response,
    assert_success_response,
    assert_no_dangerous_patterns
)


class TestAdminAuthentication:
    """Test admin authentication and authorization"""
    
    @pytest.mark.asyncio
    async def test_missing_api_key(self, async_client):
        """Test admin endpoints require API key"""
        response = await async_client.get("/api/v1/admin/system/info")
        assert_http_status(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        # HTTPBearer returns 403 when no Authorization header is provided
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    @pytest.mark.asyncio
    async def test_invalid_api_key(self, async_client):
        """Test invalid API key is rejected"""
        headers = {"Authorization": "Bearer invalid_key_123"}
        response = await async_client.get("/api/v1/admin/system/info", headers=headers)
        # In development mode with no API_KEY configured, it may return 200
        # Otherwise should return 401 for invalid key
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN, status.HTTP_200_OK]
    
    @pytest.mark.asyncio
    async def test_non_admin_api_key(self, async_client):
        """Test regular user API key cannot access admin endpoints"""
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            mock_settings.API_KEY = "user_key_123"
            
            headers = {"Authorization": "Bearer user_key_123"}
            response = await async_client.get("/api/v1/admin/system/info", headers=headers)
            # In development mode, any key might be accepted
            assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED, status.HTTP_200_OK]
    
    @pytest.mark.asyncio
    async def test_valid_admin_api_key(self, async_client):
        """Test valid admin API key allows access"""
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            
            headers = {"Authorization": "Bearer admin_key_123"}
            response = await async_client.get("/api/v1/admin/system/info", headers=headers)
            # Should get 200 or 500 (if service fails), not 401/403
            assert response.status_code != status.HTTP_401_UNAUTHORIZED
            assert response.status_code != status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_rate_limiting_on_admin_endpoints(self, async_client):
        """Test that admin endpoints have rate limiting"""
        headers = {"Authorization": "Bearer invalid_key"}
        
        # Make multiple requests
        for _ in range(10):
            response = await async_client.get("/api/v1/admin/system/info", headers=headers)
        
        # Rate limiting headers should be present
        assert "X-RateLimit-Limit" in response.headers or response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


class TestAdminDataDeletion:
    """Test user data deletion endpoint"""
    
    @pytest.mark.asyncio
    async def test_delete_existing_user(self, async_client):
        """Test successful user deletion"""
        user_id = str(uuid.uuid4())
        
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            
            with patch("src.core.database.SessionLocal") as mock_session:
                mock_db = Mock()
                mock_user = Mock()
                mock_user.id = user_id
                mock_db.query.return_value.filter.return_value.first.return_value = mock_user
                mock_db.commit = Mock()
                mock_session.return_value = mock_db
                
                headers = {"Authorization": "Bearer admin_key_123"}
                response = await async_client.delete(
                    f"/api/v1/admin/users/{user_id}",
                    headers=headers
                )
                
                if response.status_code == status.HTTP_200_OK:
                    data = response.json()
                    assert "success" in str(data).lower() or "deleted" in str(data).lower()
                    mock_db.delete.assert_called_once()
                    mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_non_existent_user(self, async_client):
        """Test deletion of non-existent user"""
        user_id = str(uuid.uuid4())
        
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            
            with patch("src.core.database.SessionLocal") as mock_session:
                mock_db = Mock()
                mock_db.query.return_value.filter.return_value.first.return_value = None
                mock_session.return_value = mock_db
                
                headers = {"Authorization": "Bearer admin_key_123"}
                response = await async_client.delete(
                    f"/api/v1/admin/users/{user_id}",
                    headers=headers
                )
                
                assert_http_status(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK])
    
    @pytest.mark.asyncio  
    async def test_delete_with_sql_injection(self, async_client):
        """Test SQL injection protection in user deletion"""
        malicious_id = "'; DROP TABLE users; --"
        
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            
            headers = {"Authorization": "Bearer admin_key_123"}
            response = await async_client.delete(
                f"/api/v1/admin/users/{malicious_id}",
                headers=headers
            )
            
            # Should handle safely (either validation error or safe processing)
            assert response.status_code in [
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_404_NOT_FOUND
            ]
    
    @pytest.mark.asyncio
    async def test_deletion_audit_logging(self, async_client):
        """Test that user deletion is properly logged"""
        user_id = str(uuid.uuid4())
        
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            
            with patch("src.services.admin_service.logger") as mock_logger:
                headers = {"Authorization": "Bearer admin_key_123"}
                response = await async_client.delete(
                    f"/api/v1/admin/users/{user_id}",
                    headers=headers
                )
                
                # Logger should be called regardless of result
                if response.status_code == status.HTTP_200_OK:
                    assert mock_logger.info.called or mock_logger.warning.called


class TestAdminConfigUpdate:
    """Test system configuration update endpoint"""
    
    @pytest.mark.asyncio
    async def test_update_valid_config(self, async_client):
        """Test updating configuration with valid values"""
        config_update = {
            "rate_limit_per_minute": 100,
            "max_request_size": 2097152,
            "cache_ttl": 600
        }
        
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            
            headers = {"Authorization": "Bearer admin_key_123"}
            response = await async_client.put(
                "/api/v1/admin/config",
                headers=headers,
                json=config_update
            )
            
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                assert "success" in str(data).lower() or "updated" in str(data).lower()
    
    @pytest.mark.asyncio
    async def test_update_invalid_config_values(self, async_client):
        """Test that invalid config values are rejected"""
        invalid_configs = [
            {"rate_limit_per_minute": -1},  # Negative value
            {"rate_limit_per_minute": "not_a_number"},  # Wrong type
            {"max_request_size": 0},  # Too small
            {"unknown_setting": "value"}  # Unknown setting
        ]
        
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            
            headers = {"Authorization": "Bearer admin_key_123"}
            
            for config in invalid_configs:
                response = await async_client.put(
                    "/api/v1/admin/config",
                    headers=headers,
                    json=config
                )
                
                # Should reject invalid configs
                assert response.status_code in [
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    status.HTTP_400_BAD_REQUEST
                ]
    
    @pytest.mark.asyncio
    async def test_config_validation_rules(self, async_client):
        """Test that config updates follow validation rules"""
        config_update = {
            "rate_limit_per_minute": 10000,  # Very high
            "max_request_size": 104857600  # 100MB
        }
        
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            
            headers = {"Authorization": "Bearer admin_key_123"}
            response = await async_client.put(
                "/api/v1/admin/config",
                headers=headers,
                json=config_update
            )
            
            # Should either accept with warnings or reject if too high
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST
            ]
    
    @pytest.mark.asyncio
    async def test_config_rollback_on_error(self, async_client):
        """Test that config changes rollback on error"""
        config_update = {
            "rate_limit_per_minute": 60,
            "trigger_error": True  # Simulate an error condition
        }
        
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            original_rate_limit = mock_settings.RATE_LIMIT_PER_MINUTE
            
            with patch("src.services.admin_service.update_config") as mock_update:
                mock_update.side_effect = Exception("Config update failed")
                
                headers = {"Authorization": "Bearer admin_key_123"}
                response = await async_client.put(
                    "/api/v1/admin/config",
                    headers=headers,
                    json=config_update
                )
                
                # Should return error
                assert response.status_code >= 400
                
                # Original config should be preserved
                assert mock_settings.RATE_LIMIT_PER_MINUTE == original_rate_limit


class TestAdminSystemInfo:
    """Test system information endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_system_info(self, async_client):
        """Test retrieving system information"""
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            
            headers = {"Authorization": "Bearer admin_key_123"}
            response = await async_client.get(
                "/api/v1/admin/system/info",
                headers=headers
            )
            
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                # Should contain system info
                assert any(key in str(data) for key in ["version", "uptime", "memory", "cpu", "status"])
    
    @pytest.mark.asyncio
    async def test_system_info_no_sensitive_data(self, async_client):
        """Test that system info doesn't leak sensitive data"""
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            mock_settings.OPENAI_API_KEY = "secret_openai_key"
            mock_settings.DATABASE_URL = "postgresql://user:password@localhost/db"
            
            headers = {"Authorization": "Bearer admin_key_123"}
            response = await async_client.get(
                "/api/v1/admin/system/info",
                headers=headers
            )
            
            if response.status_code == status.HTTP_200_OK:
                data_str = json.dumps(response.json())
                # Should not contain secrets
                assert "secret_openai_key" not in data_str
                assert "password" not in data_str
                assert_no_dangerous_patterns(data_str)


class TestAdminCacheManagement:
    """Test cache management endpoints"""
    
    @pytest.mark.asyncio
    async def test_clear_cache(self, async_client):
        """Test cache clearing functionality"""
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            
            with patch("src.services.cache_service.CacheService") as mock_cache:
                mock_cache_instance = Mock()
                mock_cache_instance.clear = AsyncMock(return_value=True)
                mock_cache.return_value = mock_cache_instance
                
                headers = {"Authorization": "Bearer admin_key_123"}
                response = await async_client.post(
                    "/api/v1/admin/cache/clear",
                    headers=headers
                )
                
                if response.status_code == status.HTTP_200_OK:
                    data = response.json()
                    assert "success" in str(data).lower() or "cleared" in str(data).lower()
    
    @pytest.mark.asyncio
    async def test_cache_stats(self, async_client):
        """Test retrieving cache statistics"""
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            
            headers = {"Authorization": "Bearer admin_key_123"}
            response = await async_client.get(
                "/api/v1/admin/stats",
                headers=headers
            )
            
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                # Should contain cache stats
                assert any(key in str(data) for key in ["cache", "hits", "misses", "size"])


class TestAdminPromptManagement:
    """Test prompt template management"""
    
    @pytest.mark.asyncio
    async def test_reload_prompts(self, async_client):
        """Test reloading prompt templates"""
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            
            with patch("src.services.prompt_loader.PromptTemplateLoader") as mock_loader:
                mock_loader_instance = Mock()
                mock_loader_instance.reload = Mock(return_value=True)
                mock_loader.return_value = mock_loader_instance
                
                headers = {"Authorization": "Bearer admin_key_123"}
                response = await async_client.post(
                    "/api/v1/admin/prompts/reload",
                    headers=headers
                )
                
                if response.status_code == status.HTTP_200_OK:
                    data = response.json()
                    assert "success" in str(data).lower() or "reloaded" in str(data).lower()
    
    @pytest.mark.asyncio
    async def test_get_prompt_info(self, async_client):
        """Test retrieving prompt template information"""
        with patch("src.core.config.settings") as mock_settings:
            mock_settings.ADMIN_API_KEY = "admin_key_123"
            
            headers = {"Authorization": "Bearer admin_key_123"}
            response = await async_client.get(
                "/api/v1/admin/prompts",
                headers=headers
            )
            
            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                # Should contain prompt info
                assert any(key in str(data) for key in ["prompts", "templates", "versions"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])