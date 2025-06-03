"""
Unit tests for the Unified Content Service
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.models.pydantic.content import (
    ContentOutline,
    OutlineSection,
    PodcastScript,
    StudyGuide,
)
from app.services.unified_content_service import ContentOptions, UnifiedContentService


@pytest.fixture
def mock_outline():
    """Create a mock content outline"""
    return ContentOutline(
        title="Test Content",
        overview="This is a comprehensive test overview that provides detailed information about the content and its objectives for testing purposes",
        learning_objectives=[
            "Learn the fundamental concepts of testing methodologies",
            "Understand best practices for quality assurance",
            "Apply testing strategies in real-world scenarios",
        ],
        sections=[
            OutlineSection(
                section_number=1,
                title="Introduction",
                description="Introduction to the topic with comprehensive overview",
                key_points=[
                    "This is the first key point about introduction",
                    "This is the second key point",
                ],
            ),
            OutlineSection(
                section_number=2,
                title="Main Content",
                description="Main content section with detailed information",
                key_points=[
                    "This is the third key point about main content",
                    "This is the fourth key point",
                ],
            ),
            OutlineSection(
                section_number=3,
                title="Conclusion",
                description="Conclusion section with summary and takeaways",
                key_points=[
                    "This is the fifth key point about conclusion",
                    "This is the sixth key point",
                ],
            ),
        ],
    )


@pytest.fixture
def mock_podcast_script():
    """Create a mock podcast script"""
    return PodcastScript(
        title="Test Content",
        introduction="Welcome to our podcast about test content! Today we're diving deep into the exciting world of software testing. We'll explore various methodologies, best practices, and real-world applications.",
        main_content="In this episode, we'll explore the fascinating world of testing. "
        * 100,
        conclusion="Thank you for listening to our test podcast. We hope you found this exploration of testing concepts valuable. Don't forget to subscribe for more content and check out our study materials!",
        speaker_notes=["Note 1", "Note 2"],
    )


@pytest.fixture
def mock_study_guide():
    """Create a mock study guide"""
    return StudyGuide(
        title="Test Content",
        overview="This comprehensive study guide covers test content in detail, providing you with all the essential knowledge and practical insights you need to master software testing methodologies.",
        key_concepts=["Concept 1", "Concept 2", "Concept 3", "Concept 4", "Concept 5"],
        detailed_content="This is detailed content about testing. " * 50,
        summary="In summary, testing is a critical component of software development that ensures quality, reliability, and user satisfaction. Through this guide, you've learned the fundamental principles and best practices.",
        recommended_reading=["Book 1", "Book 2"],
    )


class TestUnifiedContentService:
    """Test the unified content service"""

    @pytest.mark.asyncio
    async def test_generate_content_success(
        self, test_settings, mock_outline, mock_podcast_script, mock_study_guide
    ):
        """Test successful content generation"""
        service = UnifiedContentService(test_settings)

        # Mock the LLM client
        mock_llm = AsyncMock()
        service.llm = mock_llm

        # Mock successful outline generation
        mock_llm.generate_outline.return_value = (
            mock_outline,
            {"input_tokens": 100, "output_tokens": 200},
        )

        # Mock successful content type generation
        async def mock_generate_content_type(content_type, outline, debug=False):
            if content_type == "podcast_script":
                return (
                    mock_podcast_script,
                    {"input_tokens": 150, "output_tokens": 250},
                )
            elif content_type == "study_guide":
                return (mock_study_guide, {"input_tokens": 120, "output_tokens": 220})
            else:
                return (None, {"input_tokens": 0, "output_tokens": 0})

        mock_llm.generate_content_type = mock_generate_content_type

        # Test content generation
        result = await service.generate_content(
            syllabus_text="This is a test syllabus about testing concepts.",
            job_id="test-job-123",
        )

        # Verify success
        assert result.content is not None
        assert result.error is None
        assert result.content.content_outline == mock_outline
        assert result.content.podcast_script == mock_podcast_script
        assert result.content.study_guide == mock_study_guide

        # Verify metadata
        assert result.metadata is not None
        assert result.metadata.ai_model_used == test_settings.gemini_model_name
        # Token usage should be the sum of all operations
        # outline: 100 input, 200 output
        # podcast_script: 150 input, 250 output
        # study_guide: 120 input, 220 output
        # 5 other content types (None): 0 input, 0 output each
        assert result.token_usage["input_tokens"] == 370  # 100 + 150 + 120
        assert result.token_usage["output_tokens"] == 670  # 200 + 250 + 220

    @pytest.mark.asyncio
    async def test_generate_content_invalid_input(self, test_settings):
        """Test content generation with invalid input"""
        service = UnifiedContentService(test_settings)

        # Test with empty syllabus
        result = await service.generate_content(syllabus_text="", job_id="test-job-124")

        # Verify failure
        assert result.content is None
        assert result.error is not None
        assert "InvalidInputError" in result.error["code"]
        assert "Syllabus text is empty" in result.error["message"]

    @pytest.mark.asyncio
    async def test_generate_content_outline_failure(self, test_settings):
        """Test handling of outline generation failure"""
        service = UnifiedContentService(test_settings)

        # Mock the LLM client to fail
        mock_llm = AsyncMock()
        service.llm = mock_llm
        mock_llm.generate_outline.return_value = (
            None,
            {"input_tokens": 100, "output_tokens": 0},
        )

        # Test content generation
        result = await service.generate_content(
            syllabus_text="This is a test syllabus.", job_id="test-job-125"
        )

        # Verify failure
        assert result.content is None
        assert result.error is not None
        assert "ContentGenerationError" in result.error["code"]
        assert "Failed to generate outline" in result.error["message"]

    @pytest.mark.asyncio
    async def test_generate_content_partial_success(
        self, test_settings, mock_outline, mock_podcast_script
    ):
        """Test partial success when some content types fail"""
        service = UnifiedContentService(test_settings)

        # Mock the LLM client
        mock_llm = AsyncMock()
        service.llm = mock_llm

        # Mock successful outline generation
        mock_llm.generate_outline.return_value = (
            mock_outline,
            {"input_tokens": 100, "output_tokens": 200},
        )

        # Mock partial content type generation (study guide fails)
        async def mock_generate_content_type(content_type, outline, debug=False):
            if content_type == "podcast_script":
                return (
                    mock_podcast_script,
                    {"input_tokens": 150, "output_tokens": 250},
                )
            else:
                return (None, {"input_tokens": 50, "output_tokens": 0})

        mock_llm.generate_content_type = mock_generate_content_type

        # Test content generation
        result = await service.generate_content(
            syllabus_text="This is a test syllabus.", job_id="test-job-126"
        )

        # Verify partial success
        assert result.content is not None
        assert result.error is None
        assert result.content.content_outline == mock_outline
        assert result.content.podcast_script == mock_podcast_script
        assert result.content.study_guide is None  # Failed to generate

        # Verify metrics show partial generation
        assert result.metadata is not None
        assert result.metrics is not None
        assert result.metrics.overall_score < 1.0  # Not all content generated

    @pytest.mark.asyncio
    async def test_generate_content_with_cache(self, test_settings, mock_outline):
        """Test content generation with caching"""
        # Use options to enable cache
        service = UnifiedContentService(test_settings)

        # Mock cache
        mock_cache = AsyncMock()
        service.cache = mock_cache
        mock_cache.generate_key.return_value = "test-cache-key"
        mock_cache.get.return_value = None  # Cache miss

        # Mock LLM client
        mock_llm = AsyncMock()
        service.llm = mock_llm
        mock_llm.generate_outline.return_value = (
            mock_outline,
            {"input_tokens": 100, "output_tokens": 200},
        )

        # Test content generation with cache enabled
        options = ContentOptions(use_cache=True)
        result = await service.generate_content(
            syllabus_text="This is a cached test.",
            job_id="test-job-127",
            options=options,
        )

        # Verify cache was checked and set
        assert mock_cache.generate_key.called
        assert mock_cache.get.called
        assert mock_cache.set.called

    def test_llm_client_initialization(self, test_settings):
        """Test that LLM client is properly initialized"""
        service = UnifiedContentService(test_settings)

        assert service.llm is not None
        assert hasattr(service.llm, "generate_outline")
        assert hasattr(service.llm, "generate_content_type")

    def test_monitor_initialization(self, test_settings):
        """Test that monitor is properly initialized"""
        service = UnifiedContentService(test_settings)

        assert service.monitor is not None
        assert hasattr(service.monitor, "track_operation")
        assert hasattr(service.monitor, "record_quality")
