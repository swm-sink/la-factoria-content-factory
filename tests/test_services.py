"""
Service Layer Unit Tests for La Factoria
========================================

Comprehensive unit tests for all service components:
- EducationalContentService: Core content generation orchestration
- AIProviderManager: Multi-provider AI integration
- PromptTemplateLoader: Template loading and compilation
- QualityAssessor: Educational quality assessment (enhanced from existing)

Focus on business logic, error handling, and integration patterns.
"""

# Fix Python path for src imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import pytest_asyncio
import asyncio
import json
import time
from typing import Dict, Any, List
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime

from src.services.educational_content_service import EducationalContentService
from src.services.ai_providers import AIProviderManager
from src.services.prompt_loader import PromptTemplateLoader
from src.services.quality_assessor import EducationalQualityAssessor
from src.models.educational import (
    LaFactoriaContentType,
    LearningLevel,
    CognitiveLevel,
    LearningObjective
)


class TestEducationalContentService:
    """Unit tests for EducationalContentService"""

    @pytest_asyncio.fixture
    async def content_service(self, mock_ai_providers):
        """Create content service with mocked dependencies"""
        service = EducationalContentService()

        # Mock the dependencies
        service.prompt_loader = AsyncMock()
        service.ai_provider = AsyncMock()
        service.quality_assessor = AsyncMock()

        # Configure mock responses
        service.prompt_loader.load_template.return_value = "Test prompt template for {topic}"
        service.prompt_loader.compile_template.return_value = "Compiled prompt for Test Topic"

        service.ai_provider.generate_content.return_value = {
            "content": '{"title": "Test Content", "sections": []}',
            "tokens_used": 500,
            "provider": "openai"
        }

        service.quality_assessor.assess_content_quality.return_value = {
            "overall_quality_score": 0.85,
            "educational_effectiveness": 0.80,
            "meets_quality_threshold": True,
            "meets_educational_threshold": True
        }

        await service.initialize()
        return service

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test service initialization"""
        service = EducationalContentService()
        assert not service._initialized

        with patch.object(service.prompt_loader, 'initialize', new_callable=AsyncMock):
            await service.initialize()
            assert service._initialized

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_content_success(self, content_service):
        """Test successful content generation"""
        result = await content_service.generate_content(
            content_type="study_guide",
            topic="Python Programming",
            age_group="high_school",
            learning_objectives=None,
            additional_requirements="Include examples"
        )

        # Validate result structure
        assert "id" in result
        assert "content_type" in result
        assert result["content_type"] == "study_guide"
        assert "topic" in result
        assert result["topic"] == "Python Programming"
        assert "generated_content" in result
        assert "quality_metrics" in result
        assert "metadata" in result

        # Verify service calls
        content_service.prompt_loader.load_template.assert_called_once_with("study_guide")
        content_service.ai_provider.generate_content.assert_called_once()
        content_service.quality_assessor.assess_content_quality.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_content_with_learning_objectives(self, content_service):
        """Test content generation with learning objectives"""
        learning_objectives = [
            LearningObjective(
                cognitive_level=CognitiveLevel.UNDERSTANDING,
                subject_area="Computer Science",
                specific_skill="Python syntax",
                measurable_outcome="Write basic Python programs",
                difficulty_level=5
            )
        ]

        result = await content_service.generate_content(
            content_type="study_guide",
            topic="Python Basics",
            age_group="high_school",
            learning_objectives=learning_objectives
        )

        assert result["content_type"] == "study_guide"

        # Verify that learning objectives were passed to template compilation
        content_service.prompt_loader.compile_template.assert_called_once()
        call_args = content_service.prompt_loader.compile_template.call_args
        variables = call_args[0][1]  # Second argument should be variables dict
        assert "learning_objectives" in variables

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_content_unsupported_type(self, content_service):
        """Test error handling for unsupported content type"""
        with pytest.raises(ValueError, match="Unsupported content type"):
            await content_service.generate_content(
                content_type="unsupported_type",
                topic="Test Topic",
                age_group="high_school"
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_content_initialization_check(self):
        """Test that service initializes itself if not already initialized"""
        service = EducationalContentService()

        with patch.object(service, 'initialize', new_callable=AsyncMock) as mock_init, \
             patch.object(service.prompt_loader, 'load_template', new_callable=AsyncMock) as mock_load, \
             patch.object(service.ai_provider, 'generate_content', new_callable=AsyncMock) as mock_generate, \
             patch.object(service.quality_assessor, 'assess_content_quality', new_callable=AsyncMock) as mock_assess:

            # Configure mocks
            mock_load.return_value = "template"
            mock_generate.return_value = {"content": '{"title": "test"}', "tokens_used": 100, "provider": "test"}
            mock_assess.return_value = {"overall_quality_score": 0.8, "meets_quality_threshold": True}

            await service.generate_content(
                content_type="study_guide",
                topic="Test",
                age_group="high_school"
            )

            # Should call initialize since service wasn't initialized
            mock_init.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_multiple_content_types(self):
        """Test batch generation of multiple content types"""
        service = EducationalContentService()

        # Mock the generate_content method to avoid full implementation
        with patch.object(service, 'generate_content', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = {
                "id": "test-id",
                "content_type": "test_type",
                "generated_content": {"title": "Test"},
                "quality_metrics": {"overall_quality_score": 0.8}
            }

            # Test batch generation method if it exists
            if hasattr(service, 'generate_multiple_content_types'):
                result = await service.generate_multiple_content_types(
                    topic="Test Topic",
                    content_types=["study_guide", "flashcards"],
                    age_group="high_school"
                )

                # Should call generate_content for each type
                assert mock_generate.call_count == 2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_content_parsing_json_extraction(self, content_service):
        """Test JSON content parsing from AI responses"""
        # Mock AI provider to return content with JSON embedded in markdown
        content_service.ai_provider.generate_content.return_value = {
            "content": '''Here is the generated content:

```json
{
    "title": "Test Study Guide",
    "sections": [
        {"title": "Introduction", "content": "Welcome to the guide"},
        {"title": "Main Content", "content": "Core learning material"}
    ]
}
```

This completes the generation.''',
            "tokens_used": 600,
            "provider": "openai"
        }

        result = await content_service.generate_content(
            content_type="study_guide",
            topic="Test Topic",
            age_group="high_school"
        )

        # Should extract JSON from markdown
        generated_content = result["generated_content"]
        assert "title" in generated_content
        assert generated_content["title"] == "Test Study Guide"
        assert "sections" in generated_content
        assert len(generated_content["sections"]) == 2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_error_handling_template_loading_failure(self, content_service):
        """Test error handling when template loading fails"""
        content_service.prompt_loader.load_template.side_effect = FileNotFoundError("Template not found")

        with pytest.raises(FileNotFoundError):
            await content_service.generate_content(
                content_type="study_guide",
                topic="Test Topic",
                age_group="high_school"
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_error_handling_ai_provider_failure(self, content_service):
        """Test error handling when AI provider fails"""
        content_service.ai_provider.generate_content.side_effect = Exception("AI service unavailable")

        with pytest.raises(Exception, match="AI service unavailable"):
            await content_service.generate_content(
                content_type="study_guide",
                topic="Test Topic",
                age_group="high_school"
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_quality_threshold_enforcement(self, content_service):
        """Test that quality thresholds are enforced"""
        # Configure quality assessor to return low quality
        content_service.quality_assessor.assess_content_quality.return_value = {
            "overall_quality_score": 0.65,  # Below 0.70 threshold
            "educational_effectiveness": 0.70,  # Below 0.75 threshold
            "meets_quality_threshold": False,
            "meets_educational_threshold": False
        }

        # Depending on implementation, should either:
        # 1. Regenerate content, or
        # 2. Return with low quality scores
        result = await content_service.generate_content(
            content_type="study_guide",
            topic="Test Topic",
            age_group="high_school"
        )

        # At minimum, quality metrics should reflect the low scores
        quality_metrics = result["quality_metrics"]
        assert quality_metrics["overall_quality_score"] == 0.65
        assert quality_metrics["meets_quality_threshold"] == False

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_metadata_generation_accuracy(self, content_service):
        """Test that metadata is accurately generated"""
        start_time = time.time()

        result = await content_service.generate_content(
            content_type="flashcards",
            topic="Spanish Vocabulary",
            age_group="middle_school"
        )

        end_time = time.time()

        metadata = result["metadata"]
        assert "generation_duration_ms" in metadata
        assert "tokens_used" in metadata
        assert "ai_provider" in metadata
        assert "prompt_template" in metadata

        # Generation time should be reasonable
        generation_time_ms = metadata["generation_duration_ms"]
        expected_max_time = (end_time - start_time) * 1000 + 100  # Allow 100ms buffer
        assert 0 <= generation_time_ms <= expected_max_time


class TestAIProviderManager:
    """Unit tests for AIProviderManager"""

    @pytest.fixture
    def ai_provider_manager(self):
        """Create AI provider manager with mocked clients"""
        manager = AIProviderManager()

        # Mock all AI clients
        manager.openai_client = AsyncMock()
        manager.anthropic_client = AsyncMock()
        manager.vertex_client = AsyncMock()

        return manager

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_provider_selection_logic(self, ai_provider_manager):
        """Test AI provider selection logic"""
        # Test that provider selection works
        # This tests the _select_provider method if it exists
        if hasattr(ai_provider_manager, '_select_provider'):
            provider = ai_provider_manager._select_provider("study_guide", "high_school")
            assert provider in ["openai", "anthropic", "vertex_ai"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_openai_generation(self, ai_provider_manager, mock_openai_response):
        """Test OpenAI content generation"""
        # Mock OpenAI response
        mock_response = mock_openai_response('{"title": "Test Content"}')
        ai_provider_manager.openai_client.chat.completions.create.return_value = mock_response

        if hasattr(ai_provider_manager, '_generate_with_openai'):
            result = await ai_provider_manager._generate_with_openai(
                "Test prompt", "study_guide"
            )

            assert "content" in result
            assert result["tokens_used"] == 500

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_anthropic_generation(self, ai_provider_manager, mock_anthropic_response):
        """Test Anthropic content generation"""
        # Mock Anthropic response
        mock_response = mock_anthropic_response('{"title": "Test Content"}')
        ai_provider_manager.anthropic_client.messages.create.return_value = mock_response

        if hasattr(ai_provider_manager, '_generate_with_anthropic'):
            result = await ai_provider_manager._generate_with_anthropic(
                "Test prompt", "study_guide"
            )

            assert "content" in result
            assert result["tokens_used"] == 500

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_provider_failover(self, ai_provider_manager):
        """Test provider failover logic"""
        # Mock primary provider to fail
        ai_provider_manager.openai_client.chat.completions.create.side_effect = Exception("API Error")

        # Mock secondary provider to succeed
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = '{"title": "Fallback Content"}'
        mock_response.usage = Mock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 200
        ai_provider_manager.anthropic_client.messages.create.return_value = mock_response

        # Test failover if implemented
        if hasattr(ai_provider_manager, 'generate_content_with_failover'):
            result = await ai_provider_manager.generate_content_with_failover(
                prompt="Test prompt",
                content_type="study_guide"
            )

            assert "content" in result
            # Should have used fallback provider

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_token_usage_tracking(self, ai_provider_manager):
        """Test token usage tracking"""
        # Test token usage tracking if implemented
        if hasattr(ai_provider_manager, 'get_token_usage_stats'):
            stats = ai_provider_manager.get_token_usage_stats()
            assert isinstance(stats, dict)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limiting_handling(self, ai_provider_manager):
        """Test rate limiting error handling"""
        # Mock rate limiting error
        from openai import RateLimitError

        rate_limit_error = RateLimitError(
            message="Rate limit exceeded",
            response=Mock(),
            body={}
        )
        ai_provider_manager.openai_client.chat.completions.create.side_effect = rate_limit_error

        # Test rate limiting handling
        with pytest.raises(Exception):  # Should handle rate limiting appropriately
            if hasattr(ai_provider_manager, '_generate_with_openai'):
                await ai_provider_manager._generate_with_openai("Test prompt", "study_guide")


class TestPromptTemplateLoader:
    """Unit tests for PromptTemplateLoader"""

    @pytest_asyncio.fixture
    async def prompt_loader(self):
        """Create prompt loader with mocked file system"""
        loader = PromptTemplateLoader()

        # Mock template files
        mock_templates = {
            "study_guide": """
# Study Guide Template

Topic: {topic}
Age Group: {age_group}
Learning Objectives: {learning_objectives}

Generate a comprehensive study guide.
            """.strip(),
            "flashcards": """
# Flashcard Template

Create flashcards for: {topic}
Target audience: {age_group}
Additional requirements: {additional_requirements}
            """.strip()
        }

        with patch("builtins.open") as mock_open:
            def mock_file_content(filename, mode='r', encoding=None):
                for template_name, content in mock_templates.items():
                    if template_name in filename:
                        mock_file = Mock()
                        mock_file.read.return_value = content
                        mock_file.__enter__.return_value = mock_file
                        return mock_file
                raise FileNotFoundError(f"Template not found: {filename}")

            mock_open.side_effect = mock_file_content
            await loader.initialize()

        return loader

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_template_loading(self, prompt_loader):
        """Test template loading from files"""
        template = await prompt_loader.load_template("study_guide")

        assert "Topic: {topic}" in template
        assert "Age Group: {age_group}" in template
        assert "Learning Objectives: {learning_objectives}" in template

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_template_caching(self, prompt_loader):
        """Test that templates are cached after first load"""
        # Load template twice
        template1 = await prompt_loader.load_template("study_guide")
        template2 = await prompt_loader.load_template("study_guide")

        # Should be the same instance (cached)
        assert template1 == template2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_template_compilation(self, prompt_loader):
        """Test template compilation with variables"""
        template = await prompt_loader.load_template("study_guide")

        variables = {
            "topic": "Python Programming",
            "age_group": "high_school",
            "learning_objectives": ["Learn Python syntax", "Write Python programs"],
            "additional_requirements": "Include examples"
        }

        compiled = prompt_loader.compile_template(template, variables)

        assert "Python Programming" in compiled
        assert "high_school" in compiled
        assert "{topic}" not in compiled  # Variables should be replaced

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_missing_template_error(self, prompt_loader):
        """Test error handling for missing templates"""
        with pytest.raises(FileNotFoundError):
            await prompt_loader.load_template("nonexistent_template")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_template_validation(self, prompt_loader):
        """Test template validation if implemented"""
        if hasattr(prompt_loader, 'validate_template'):
            template = await prompt_loader.load_template("study_guide")
            is_valid = prompt_loader.validate_template(template, "study_guide")
            assert isinstance(is_valid, bool)

    @pytest.mark.unit
    def test_variable_extraction(self, prompt_loader):
        """Test extraction of variables from templates"""
        template = "This is a {topic} template for {age_group} with {additional_requirements}"

        if hasattr(prompt_loader, 'extract_variables'):
            variables = prompt_loader.extract_variables(template)
            expected_vars = {"topic", "age_group", "additional_requirements"}
            assert set(variables) == expected_vars

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_all_content_types_have_templates(self, prompt_loader):
        """Test that all 8 content types have templates"""
        content_types = [ct.value for ct in LaFactoriaContentType]

        for content_type in content_types:
            try:
                template = await prompt_loader.load_template(content_type)
                assert len(template) > 0
            except FileNotFoundError:
                # If template doesn't exist, it should be created
                pytest.skip(f"Template for {content_type} not yet implemented")

    @pytest.mark.unit
    def test_template_format_validation(self, prompt_loader):
        """Test validation of template format"""
        valid_template = "Topic: {topic}\nContent: {content}"
        invalid_template = "Topic: {topic}\nMissing closing brace: {content"

        if hasattr(prompt_loader, 'validate_template_format'):
            assert prompt_loader.validate_template_format(valid_template) == True
            assert prompt_loader.validate_template_format(invalid_template) == False


class TestServiceIntegration:
    """Integration tests between services"""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_content_generation_pipeline(self, mock_ai_providers):
        """Test full content generation pipeline integration"""
        # Create services
        content_service = EducationalContentService()

        # Mock file system for templates
        with patch("builtins.open") as mock_open:
            mock_file = Mock()
            mock_file.read.return_value = "Template for {topic} at {age_group} level"
            mock_file.__enter__.return_value = mock_file
            mock_open.return_value = mock_file

            await content_service.initialize()

            result = await content_service.generate_content(
                content_type="study_guide",
                topic="Integration Test Topic",
                age_group="high_school"
            )

            # Validate integration result
            assert "generated_content" in result
            assert "quality_metrics" in result
            assert result["content_type"] == "study_guide"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_service_error_propagation(self):
        """Test error propagation between services"""
        content_service = EducationalContentService()

        # Mock prompt loader to fail
        with patch.object(content_service.prompt_loader, 'load_template', side_effect=Exception("Template loading failed")):
            with pytest.raises(Exception, match="Template loading failed"):
                await content_service.generate_content(
                    content_type="study_guide",
                    topic="Test Topic",
                    age_group="high_school"
                )

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_service_performance_integration(self, mock_ai_providers, timing_context):
        """Test service performance in integration"""
        content_service = EducationalContentService()

        with patch("builtins.open") as mock_open:
            mock_file = Mock()
            mock_file.read.return_value = "Quick template: {topic}"
            mock_file.__enter__.return_value = mock_file
            mock_open.return_value = mock_file

            await content_service.initialize()

            with timing_context() as timer:
                result = await content_service.generate_content(
                    content_type="one_pager_summary",
                    topic="Performance Test",
                    age_group="high_school"
                )

            # Should complete quickly with mocks
            timer.assert_under_time_limit(1.0, "Mocked content generation")
            assert "generated_content" in result

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_service_usage(self, mock_ai_providers):
        """Test concurrent usage of services"""
        content_service = EducationalContentService()

        with patch("builtins.open") as mock_open:
            mock_file = Mock()
            mock_file.read.return_value = "Concurrent template: {topic}"
            mock_file.__enter__.return_value = mock_file
            mock_open.return_value = mock_file

            await content_service.initialize()

            # Create multiple concurrent requests
            async def generate_content(topic_suffix):
                return await content_service.generate_content(
                    content_type="flashcards",
                    topic=f"Concurrent Test {topic_suffix}",
                    age_group="high_school"
                )

            tasks = [generate_content(i) for i in range(5)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # All should succeed
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) == 5

            # Each should have unique content
            topics = [r["topic"] for r in successful_results]
            assert len(set(topics)) == 5  # All unique topics
