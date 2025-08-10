"""
Conftest fixes to be integrated - solving async and auth issues
This module contains the fixes needed for test infrastructure
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from typing import Any, Dict
from decimal import Decimal

# Helper for decimal/float comparisons
def assert_numeric_equal(val1: Any, val2: Any, tolerance: float = 0.0001) -> bool:
    """Compare numeric values (Decimal, float, int) with tolerance"""
    try:
        return abs(float(val1) - float(val2)) < tolerance
    except (TypeError, ValueError):
        return val1 == val2

# Fixed async fixture decorator
def async_fixture(scope="function"):
    """Decorator to properly handle async fixtures"""
    def decorator(func):
        @pytest.fixture(scope=scope)
        def wrapper(*args, **kwargs):
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(func(*args, **kwargs))
            finally:
                loop.close()
        return wrapper
    return decorator

# Mock AI response structure that matches service expectations
def create_mock_ai_response(content_type: str = "study_guide") -> Dict[str, Any]:
    """Create a properly structured mock AI response"""
    from dataclasses import dataclass
    
    @dataclass
    class MockResponse:
        content: str
        metadata: Dict[str, Any]
        
        def dict(self):
            return {
                'content': self.content,
                'metadata': self.metadata
            }
    
    mock_content = {
        "study_guide": """
        # Study Guide: Test Topic
        
        ## Introduction
        This is a test study guide for testing purposes.
        
        ## Key Concepts
        1. Concept One
        2. Concept Two
        
        ## Summary
        Test content successfully generated.
        """,
        "master_content_outline": """
        # Master Content Outline: Test Topic
        
        ## Learning Objectives
        - Objective 1
        - Objective 2
        
        ## Content Structure
        1. Introduction
        2. Main Content
        3. Conclusion
        """
    }
    
    return MockResponse(
        content=mock_content.get(content_type, "Test content"),
        metadata={
            'tokens_used': 100,
            'model': 'test-model',
            'content_type': content_type
        }
    )

# Fixed content service fixture
@async_fixture()
async def content_service_fixed(mock_ai_providers):
    """Fixed content service with proper async handling"""
    from src.services.educational_content_service import EducationalContentService
    
    # Patch the AI provider to return proper structure
    with patch('src.services.educational_content_service.AIProviderManager') as MockAI:
        mock_manager = AsyncMock()
        
        # Make generate_content return proper structure
        async def mock_generate(*args, **kwargs):
            return create_mock_ai_response().dict()
        
        mock_manager.generate_content = mock_generate
        MockAI.return_value = mock_manager
        
        # Create and initialize service
        service = EducationalContentService()
        await service.initialize()
        
        return service

# Fixed authentication for tests
def setup_test_auth():
    """Setup authentication for test environment"""
    from src.core.config import settings
    
    # Clear API key to enable development mode
    settings.API_KEY = None
    
    # Mock verify_api_key to always pass in tests
    async def mock_verify(credentials):
        return credentials.credentials if hasattr(credentials, 'credentials') else "test-key"
    
    return mock_verify

# Database type compatibility helpers
class DatabaseTypeHelper:
    """Helper for handling database type differences"""
    
    @staticmethod
    def to_float(value: Any) -> float:
        """Convert any numeric type to float"""
        if isinstance(value, Decimal):
            return float(value)
        return float(value)
    
    @staticmethod
    def assert_equal(val1: Any, val2: Any, tolerance: float = 0.0001) -> bool:
        """Assert equality with type conversion"""
        try:
            return abs(DatabaseTypeHelper.to_float(val1) - 
                      DatabaseTypeHelper.to_float(val2)) < tolerance
        except:
            return val1 == val2

# Performance test helpers
class PerformanceTestConfig:
    """Configuration for performance tests in development"""
    
    # Realistic timeouts for development environment
    TIMEOUTS = {
        'api_response': 2.0,  # 2 seconds for API responses
        'content_generation': 5.0,  # 5 seconds for content generation
        'database_query': 0.5,  # 500ms for database queries
        'cache_lookup': 0.1,  # 100ms for cache lookups
    }
    
    @classmethod
    def get_timeout(cls, operation: str) -> float:
        """Get appropriate timeout for operation"""
        return cls.TIMEOUTS.get(operation, 1.0)