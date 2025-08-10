"""
Test to validate that test utilities work correctly
"""

import pytest
from tests.utils import (
    # Fixtures
    sample_content_request,
    mock_ai_provider,
    
    # Factories
    ContentRequestFactory,
    UserFactory,
    EducationalContentFactory,
    QualityMetricsFactory,
    
    # Mocks
    MockAIProvider,
    MockRedisClient,
    MockRateLimiter,
    create_mock_settings,
    
    # Assertions
    assert_valid_uuid,
    assert_valid_email,
    assert_valid_api_key,
    assert_quality_score_valid,
    assert_no_dangerous_patterns
)


def test_fixtures_work(sample_content_request):
    """Test that fixtures are properly imported and work"""
    assert sample_content_request["topic"] == "Python Programming"
    assert sample_content_request["content_type"] == "study_guide"
    assert len(sample_content_request["learning_objectives"]) == 3


def test_factories_work():
    """Test that factories generate valid data"""
    # Content request factory
    request = ContentRequestFactory.create()
    assert "topic" in request
    assert "content_type" in request
    assert request["content_type"] in ContentRequestFactory.CONTENT_TYPES
    
    # User factory
    user = UserFactory.create()
    assert "email" in user
    assert "api_key" in user
    assert_valid_email(user["email"])
    
    # Educational content factory
    content = EducationalContentFactory.create()
    assert "content_type" in content
    assert "quality_score" in content
    assert_quality_score_valid(content["quality_score"])
    
    # Quality metrics factory
    metrics = QualityMetricsFactory.create()
    assert "overall_score" in metrics
    assert_quality_score_valid(metrics["overall_score"])


@pytest.mark.asyncio
async def test_mocks_work():
    """Test that mock services work correctly"""
    # AI Provider mock
    ai_mock = MockAIProvider()
    result = await ai_mock.generate_content("Test prompt")
    assert "content" in result
    assert ai_mock.call_count == 1
    
    # Redis mock
    redis_mock = MockRedisClient()
    await redis_mock.set("key", "value")
    value = await redis_mock.get("key")
    assert value == "value"
    
    # Rate limiter mock
    limiter = MockRateLimiter(limit=2)
    assert await limiter.check_rate_limit("test") is True
    assert await limiter.check_rate_limit("test") is True
    assert await limiter.check_rate_limit("test") is False  # Exceeds limit
    
    # Settings mock
    settings = create_mock_settings(API_KEY="custom_key")
    assert settings.API_KEY == "custom_key"
    assert settings.DATABASE_URL == "sqlite:///test.db"


def test_assertions_work():
    """Test that custom assertions work correctly"""
    # Valid cases
    assert_valid_uuid("550e8400-e29b-41d4-a716-446655440000")
    assert_valid_email("test@example.com")
    assert_valid_api_key("test_key_123456789012345")
    assert_quality_score_valid(0.85)
    assert_no_dangerous_patterns("Safe text content")
    
    # Invalid cases should raise
    with pytest.raises(AssertionError):
        assert_valid_uuid("not-a-uuid")
    
    with pytest.raises(AssertionError):
        assert_valid_email("not-an-email")
    
    with pytest.raises(AssertionError):
        assert_valid_api_key("short")
    
    with pytest.raises(AssertionError):
        assert_quality_score_valid(1.5)
    
    with pytest.raises(AssertionError):
        assert_no_dangerous_patterns("DROP TABLE users")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])