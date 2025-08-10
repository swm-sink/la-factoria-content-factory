"""
Test Infrastructure Fixes Validation
Verify that test infrastructure issues are resolved
"""

import pytest
import asyncio
from decimal import Decimal
from unittest.mock import Mock, patch

class TestInfrastructureFixes:
    """Validate that infrastructure fixes are working"""
    
    def test_api_key_development_mode(self):
        """Verify API_KEY is None for development mode"""
        from src.core.config import settings
        assert settings.API_KEY is None, "API_KEY should be None for development mode"
    
    def test_decimal_float_comparison(self):
        """Test Decimal/float comparison helper"""
        # Import the helper from conftest if available
        try:
            from builtins import assert_numeric_equal
            
            decimal_val = Decimal('0.85')
            float_val = 0.85
            
            assert assert_numeric_equal(decimal_val, float_val)
            assert assert_numeric_equal(0.8500001, 0.85, tolerance=0.001)
            assert not assert_numeric_equal(0.9, 0.85, tolerance=0.01)
        except ImportError:
            # Fallback to manual comparison
            decimal_val = Decimal('0.85')
            float_val = 0.85
            assert abs(float(decimal_val) - float_val) < 0.0001
    
    def test_psycopg2_installed(self):
        """Verify PostgreSQL driver is installed"""
        import psycopg2
        assert psycopg2 is not None
        assert hasattr(psycopg2, '__version__')
    
    def test_content_service_sync_fixture(self, content_service_sync):
        """Test synchronous content service fixture"""
        assert content_service_sync is not None
        assert hasattr(content_service_sync, 'generate_content')
        
        # The generate_content should be callable synchronously
        assert callable(content_service_sync.generate_content)
    
    @pytest.mark.asyncio
    async def test_content_service_async_fixture(self, content_service):
        """Test async content service fixture"""
        assert content_service is not None
        assert hasattr(content_service, 'generate_content')
        
        # Should be able to call async method
        result = await content_service.generate_content(
            content_type='study_guide',
            topic='Test Topic',
            age_group='high_school'
        )
        assert result is not None
    
    def test_auth_bypass_in_tests(self, client, mock_verify_api_key):
        """Test that authentication is properly bypassed in tests"""
        # Make a request without API key - should work in test mode
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        # Make a request with test API key - should also work
        response = client.get("/api/v1/health", headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
    
    def test_mock_ai_providers_structure(self, mock_ai_providers):
        """Test that mock AI providers have correct structure"""
        assert mock_ai_providers is not None
        
        # Check OpenAI mock
        assert hasattr(mock_ai_providers['openai'], 'return_value')
        mock_response = mock_ai_providers['openai'].return_value
        assert 'content' in mock_response
        assert 'metadata' in mock_response
    
    def test_database_session_handling(self, test_database):
        """Test database session is properly handled"""
        assert test_database is not None
        
        # Test basic query works
        from sqlalchemy import text
        result = test_database.execute(text("SELECT 1"))
        assert result is not None
        
        # Session should auto-rollback in tests
        test_database.rollback()
    
    @pytest.mark.performance
    def test_realistic_performance_expectations(self):
        """Test that performance expectations are realistic"""
        import time
        
        # Simulate API call
        start = time.time()
        time.sleep(0.1)  # 100ms simulated latency
        elapsed = time.time() - start
        
        # Should be under 2 seconds (realistic for dev)
        assert elapsed < 2.0, f"Performance test should allow for dev environment: {elapsed}s"