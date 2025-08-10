"""
Reusable test fixtures for La Factoria test suite
"""

import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
import asyncio
from datetime import datetime
import uuid

from src.core.database import SessionLocal, engine, Base
from src.models.educational import EducationalContentDB, UserModel
from src.services.educational_content_service import EducationalContentService
from src.services.quality_assessor import EducationalQualityAssessor
from src.services.prompt_loader import PromptTemplateLoader


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest_asyncio.fixture
async def async_db_session():
    """Async database session for async tests"""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker
    
    # Create async engine
    async_engine = create_async_engine(
        "sqlite+aiosqlite:///./test.db",
        echo=False
    )
    
    # Create async session
    async_session_maker = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def sample_content_request():
    """Sample content generation request"""
    return {
        "topic": "Python Programming",
        "content_type": "study_guide",
        "difficulty_level": "intermediate",
        "learning_objectives": [
            "Understand Python data structures",
            "Master control flow",
            "Learn object-oriented programming"
        ],
        "target_audience": "College students",
        "additional_requirements": "Include practical examples"
    }


@pytest.fixture
def sample_user():
    """Sample user for testing"""
    return UserModel(
        id=uuid.uuid4(),
        username=f"test_user_{uuid.uuid4().hex[:8]}",
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        api_key_hash=f"hashed_test_key_{uuid.uuid4().hex}",
        created_at=datetime.utcnow(),
        is_active=True
    )


@pytest.fixture
def sample_educational_content():
    """Sample educational content for testing"""
    return EducationalContentDB(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        content_type="study_guide",
        topic="Python Programming",
        difficulty_level="intermediate",
        content={
            "title": "Python Programming Study Guide",
            "sections": ["Introduction", "Data Types", "Control Flow"],
            "summary": "Comprehensive guide to Python programming"
        },
        metadata={
            "word_count": 1500,
            "reading_time": "10 minutes",
            "difficulty_score": 0.6
        },
        quality_score=0.85,
        created_at=datetime.utcnow()
    )


@pytest.fixture
def mock_ai_provider():
    """Mock AI provider for testing"""
    provider = AsyncMock()
    provider.generate_content = AsyncMock(return_value={
        "title": "Test Content",
        "content": "This is test content",
        "sections": ["Section 1", "Section 2"]
    })
    provider.name = "mock_provider"
    provider.model = "mock_model"
    return provider


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing"""
    client = Mock()
    client.get = Mock(return_value=None)
    client.set = Mock(return_value=True)
    client.delete = Mock(return_value=1)
    client.exists = Mock(return_value=False)
    client.expire = Mock(return_value=True)
    client.ping = Mock(return_value=True)
    return client


@pytest.fixture
def mock_rate_limiter():
    """Mock rate limiter for testing"""
    limiter = Mock()
    limiter.check_rate_limit = AsyncMock(return_value=True)
    limiter.get_remaining = AsyncMock(return_value=10)
    limiter.reset_time = AsyncMock(return_value=60)
    return limiter


@pytest_asyncio.fixture
async def test_content_service(mock_ai_provider):
    """Test content service with mocked dependencies"""
    service = EducationalContentService()
    # Replace AI provider with mock
    service._ai_provider = mock_ai_provider
    return service


@pytest_asyncio.fixture
async def test_quality_assessor():
    """Test quality assessor"""
    return EducationalQualityAssessor()


@pytest.fixture
def clean_test_database():
    """Clean database before and after test"""
    # Clean before
    with SessionLocal() as session:
        session.query(EducationalContentDB).delete()
        session.query(UserModel).delete()
        session.commit()
    
    yield
    
    # Clean after
    with SessionLocal() as session:
        session.query(EducationalContentDB).delete()
        session.query(UserModel).delete()
        session.commit()


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    # Reset any singleton instances to prevent test pollution
    import src.services.ai_providers as ai_providers
    import src.services.cache_service as cache_service
    
    # Clear module-level caches
    if hasattr(ai_providers, '_provider_cache'):
        ai_providers._provider_cache.clear()
    if hasattr(cache_service, '_instance'):
        cache_service._instance = None
    
    yield
    
    # Cleanup after test
    if hasattr(ai_providers, '_provider_cache'):
        ai_providers._provider_cache.clear()
    if hasattr(cache_service, '_instance'):
        cache_service._instance = None