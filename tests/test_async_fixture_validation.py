"""
Async Fixture Validation Tests for La Factoria
==============================================

Test suite specifically designed to validate that async fixtures work correctly.
This test file will expose any issues with async fixture configuration and help
verify that all async fixtures are properly decorated and functional.

Following TDD principles:
1. Write tests that validate async fixture behavior
2. Run tests to confirm they fail due to fixture issues (RED)
3. Fix fixtures in conftest.py
4. Run tests to confirm they pass (GREEN)
"""

# Fix Python path for src imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import asyncio
from typing import AsyncGenerator, Dict, Any
from unittest.mock import AsyncMock

# La Factoria imports
from src.services.educational_content_service import EducationalContentService
from src.services.quality_assessor import EducationalQualityAssessor
from src.services.prompt_loader import PromptTemplateLoader
from src.models.educational import LaFactoriaContentType, LearningLevel


class TestAsyncFixtureValidation:
    """Test class specifically for validating async fixture functionality"""

    @pytest.mark.asyncio
    async def test_async_client_fixture_works(self, async_client):
        """Test that async_client fixture is properly configured and functional"""
        # Verify the fixture returns an AsyncClient instance
        assert async_client is not None
        assert hasattr(async_client, 'get')
        assert hasattr(async_client, 'post')
        
        # Verify it can make async calls
        try:
            response = await async_client.get("/api/v1/health")
            # We expect this to work if fixture is properly configured
            assert response is not None
        except Exception as e:
            pytest.fail(f"Async client fixture failed to make request: {e}")

    @pytest.mark.asyncio
    async def test_content_service_fixture_works(self, content_service):
        """Test that content_service async fixture is properly configured"""
        # Verify the fixture returns a service instance
        assert content_service is not None
        assert isinstance(content_service, EducationalContentService)
        
        # Verify service has required async methods
        assert hasattr(content_service, 'generate_content')
        assert asyncio.iscoroutinefunction(content_service.generate_content)
        
        # Test that the service can be used asynchronously
        try:
            # This should work if fixture is properly configured
            result = await content_service.generate_content(
                content_type=LaFactoriaContentType.STUDY_GUIDE,
                topic="Test Topic",
                age_group=LearningLevel.HIGH_SCHOOL
            )
            assert result is not None
        except Exception as e:
            pytest.fail(f"Content service async fixture failed: {e}")

    @pytest.mark.asyncio
    async def test_quality_assessor_fixture_works(self, quality_assessor):
        """Test that quality_assessor async fixture is properly configured"""
        # Verify the fixture returns a quality assessor instance
        assert quality_assessor is not None
        assert isinstance(quality_assessor, EducationalQualityAssessor)
        
        # Verify assessor has required methods
        assert hasattr(quality_assessor, 'assess_content_quality')
        
        # Test with sample content
        sample_content = {
            "title": "Test Content",
            "content": "Educational content for testing quality assessment functionality",
            "learning_objectives": ["Test objective 1", "Test objective 2"]
        }
        
        try:
            # This should work if fixture is properly configured
            result = await quality_assessor.assess_content_quality(
                content=sample_content,
                content_type="study_guide",
                age_group="high_school"
            )
            assert result is not None
            assert isinstance(result, dict)
        except Exception as e:
            pytest.fail(f"Quality assessor async fixture failed: {e}")

    @pytest.mark.asyncio
    async def test_prompt_loader_fixture_works(self, prompt_loader):
        """Test that prompt_loader async fixture is properly configured"""
        # Verify the fixture returns a prompt loader instance
        assert prompt_loader is not None
        assert isinstance(prompt_loader, PromptTemplateLoader)
        
        # Verify loader has required async methods
        assert hasattr(prompt_loader, 'load_template')
        
        try:
            # Test loading a template - should work if fixture is properly configured
            template = await prompt_loader.load_template("study_guide")
            assert template is not None
        except Exception as e:
            pytest.fail(f"Prompt loader async fixture failed: {e}")

    @pytest.mark.asyncio
    async def test_test_database_fixture_works(self, test_database):
        """Test that test_database async fixture is properly configured"""
        # Verify the fixture returns database config
        assert test_database is not None
        assert isinstance(test_database, dict)
        assert "url" in test_database
        
        # This tests that async database fixture works correctly
        assert test_database["url"].startswith(("sqlite://", "postgresql://"))

    def test_sync_fixtures_still_work(self, auth_headers, sample_generated_content):
        """Test that regular sync fixtures continue to work after async fixes"""
        # Verify sync fixtures are not affected by async changes
        assert auth_headers is not None
        assert isinstance(auth_headers, dict)
        assert "Authorization" in auth_headers
        
        assert sample_generated_content is not None
        assert isinstance(sample_generated_content, dict)
        assert "master_content_outline" in sample_generated_content

    @pytest.mark.asyncio
    async def test_multiple_async_fixtures_together(
        self, 
        content_service, 
        quality_assessor, 
        prompt_loader,
        async_client
    ):
        """Test that multiple async fixtures can be used together in one test"""
        # This test validates that async fixture scoping works correctly
        # and multiple async fixtures don't interfere with each other
        
        assert content_service is not None
        assert quality_assessor is not None
        assert prompt_loader is not None
        assert async_client is not None
        
        # Verify they're all different instances
        assert content_service is not quality_assessor
        assert quality_assessor is not prompt_loader
        assert prompt_loader is not async_client

    @pytest.mark.asyncio
    async def test_async_fixture_cleanup_works(self, content_service):
        """Test that async fixture cleanup (teardown) works properly"""
        # Use the fixture and verify it can be used normally
        assert content_service is not None
        
        # Test that fixture state is clean for each test
        # (this test should get a fresh instance each time)
        assert hasattr(content_service, 'generate_content')
        
        # Mark that this fixture was used (for cleanup validation)
        content_service._test_marker = "test_async_fixture_cleanup_works"
        assert content_service._test_marker == "test_async_fixture_cleanup_works"


class TestAsyncFixtureErrorScenarios:
    """Test class for validating async fixture error handling"""

    @pytest.mark.asyncio
    async def test_async_fixture_with_none_values(self, quality_assessor):
        """Test async fixtures handle None/empty values properly"""
        assert quality_assessor is not None
        
        # Test that fixture can handle edge cases
        try:
            # This might fail if fixture isn't properly configured
            result = await quality_assessor.assess_content_quality(
                content={},
                content_type="study_guide",
                age_group="high_school"
            )
            # Should handle empty content gracefully
            assert result is not None
        except Exception as e:
            # Acceptable if it fails gracefully with proper error
            assert "content" in str(e).lower() or "empty" in str(e).lower()

    @pytest.mark.asyncio
    async def test_async_fixture_concurrent_access(self, content_service):
        """Test that async fixtures work correctly with concurrent access"""
        assert content_service is not None
        
        # Create multiple concurrent tasks using the same fixture
        async def generate_test_content(i):
            return await content_service.generate_content(
                content_type=LaFactoriaContentType.STUDY_GUIDE,
                topic=f"Concurrent Test Topic {i}",
                age_group=LearningLevel.HIGH_SCHOOL
            )
        
        try:
            # Run multiple concurrent operations
            tasks = [generate_test_content(i) for i in range(3)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should succeed if fixture is properly configured
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    pytest.fail(f"Concurrent task {i} failed: {result}")
                assert result is not None
                
        except Exception as e:
            pytest.fail(f"Concurrent async fixture test failed: {e}")


# Utility functions for fixture validation
def validate_async_fixture_decorator(fixture_func):
    """Utility to validate that a fixture function has proper async decorator"""
    # This would be used in implementation to validate fixture configuration
    if asyncio.iscoroutinefunction(fixture_func):
        return hasattr(fixture_func, '_pytestfixturefunction')
    return False


# Test execution markers for async tests only
# (sync tests will not inherit the asyncio mark)