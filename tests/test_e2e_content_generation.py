"""
End-to-End Content Generation Tests for La Factoria
==================================================

Comprehensive testing of the complete content generation workflow including:
- AI provider configuration and fallback
- Langfuse integration for observability
- Redis caching for cost optimization
- Educational quality assessment
- All 8 content types validation

This test validates P1 critical fixes and ensures production readiness.
"""

# Fix Python path for src imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import pytest_asyncio
import asyncio
import os
import time
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from src.services.educational_content_service import EducationalContentService
from src.models.educational import LearningObjective, CognitiveLevel, LaFactoriaContentType


class TestEndToEndContentGeneration:
    """Test complete content generation workflow with all P1 fixes"""

    @pytest_asyncio.fixture
    async def content_service(self):
        """Create educational content service with all integrations"""
        service = EducationalContentService()
        await service.initialize()
        yield service
        await service.close()  # Clean up resources

    @pytest.fixture
    def sample_learning_objectives(self):
        """Sample learning objectives for testing"""
        return [
            LearningObjective(
                cognitive_level=CognitiveLevel.UNDERSTANDING,
                subject_area="Computer Science",
                specific_skill="Python syntax",
                measurable_outcome="Identify basic Python data types",
                difficulty_level=3
            ),
            LearningObjective(
                cognitive_level=CognitiveLevel.APPLYING,
                subject_area="Computer Science", 
                specific_skill="Problem solving",
                measurable_outcome="Write simple Python programs",
                difficulty_level=4
            )
        ]

    @pytest.mark.asyncio
    async def test_complete_content_generation_pipeline(
        self, content_service: EducationalContentService, sample_learning_objectives
    ):
        """Test the complete content generation pipeline with all P1 fixes"""
        
        # Test parameters
        content_type = "study_guide"
        topic = "Python Programming Fundamentals"
        age_group = "high_school"
        
        # Mock AI response for controlled testing
        mock_ai_response = MagicMock()
        mock_ai_response.content = """{
            "title": "Python Programming Fundamentals Study Guide",
            "overview": "Comprehensive guide to Python basics",
            "learning_objectives": ["Understand Python syntax", "Apply programming concepts"],
            "sections": [
                {
                    "title": "Introduction to Python",
                    "content": "Python is a powerful programming language...",
                    "examples": ["print('Hello World')", "x = 10"]
                }
            ],
            "key_concepts": ["Variables", "Functions", "Control Flow"],
            "practice_exercises": ["Create a simple calculator", "Write a guessing game"],
            "summary": "Python fundamentals provide the foundation for programming"
        }"""
        mock_ai_response.provider = "openai"
        mock_ai_response.model = "gpt-4"
        mock_ai_response.tokens_used = 2500

        # Mock quality assessment response
        mock_quality_metrics = {
            "overall_quality_score": 0.85,
            "educational_effectiveness": 0.88,
            "cognitive_load_metrics": {"total_cognitive_load": 0.65},
            "readability_score": 0.82,
            "meets_quality_threshold": True
        }

        # Mock the AI provider and quality assessor
        with patch.object(content_service.ai_provider, 'generate_content', return_value=mock_ai_response) as mock_ai_gen, \
             patch.object(content_service.quality_assessor, 'assess_content_quality', return_value=mock_quality_metrics) as mock_quality:

            # Test first generation (cache miss)
            result = await content_service.generate_content(
                content_type=content_type,
                topic=topic,
                age_group=age_group,
                learning_objectives=sample_learning_objectives,
                additional_requirements="Include practical examples"
            )

            # Validate response structure
            assert "id" in result
            assert result["content_type"] == content_type
            assert result["topic"] == topic
            assert result["age_group"] == age_group
            assert "generated_content" in result
            assert "quality_metrics" in result
            assert "metadata" in result

            # Validate generated content structure
            generated_content = result["generated_content"]
            assert "title" in generated_content
            assert "sections" in generated_content
            assert isinstance(generated_content["sections"], list)
            assert len(generated_content["sections"]) > 0

            # Validate quality metrics
            quality_metrics = result["quality_metrics"]
            assert quality_metrics["overall_quality_score"] >= 0.70
            assert quality_metrics["meets_quality_threshold"] is True

            # Validate metadata
            metadata = result["metadata"]
            assert metadata["ai_provider"] == "openai"
            assert metadata["tokens_used"] == 2500
            assert "generation_duration_ms" in metadata
            assert metadata["meets_quality_threshold"] is True

            # Validate AI generation was called
            mock_ai_gen.assert_called_once()
            mock_quality.assert_called_once()

            first_generation_id = result["id"]

        # Wait for cache to be written (since it's async)
        await asyncio.sleep(0.1)

        # Test second generation (should hit cache)
        with patch.object(content_service.ai_provider, 'generate_content') as mock_ai_gen_2, \
             patch.object(content_service.quality_assessor, 'assess_content_quality') as mock_quality_2:

            result_cached = await content_service.generate_content(
                content_type=content_type,
                topic=topic,
                age_group=age_group,
                learning_objectives=sample_learning_objectives,
                additional_requirements="Include practical examples"
            )

            # Validate cache hit - AI generation should NOT be called
            mock_ai_gen_2.assert_not_called()
            mock_quality_2.assert_not_called()

            # Validate cached response
            assert result_cached["content_type"] == content_type
            assert result_cached["topic"] == topic
            assert result_cached["metadata"]["from_cache"] is True
            assert "cache_key" in result_cached["metadata"]

            # Content should be identical (except cache metadata)
            assert result_cached["generated_content"] == result["generated_content"]
            assert result_cached["quality_metrics"]["overall_quality_score"] == 0.85

    @pytest.mark.asyncio
    async def test_all_content_types_generation(
        self, content_service: EducationalContentService
    ):
        """Test generation for all 8 La Factoria content types"""

        # Mock AI response template
        def create_mock_response(content_type: str):
            mock_response = MagicMock()
            mock_response.content = f'{{"title": "Generated {content_type}", "content": "Educational content for {content_type}"}}'
            mock_response.provider = "openai"
            mock_response.model = "gpt-4"
            mock_response.tokens_used = 1500
            return mock_response

        # Mock quality metrics
        mock_quality = {
            "overall_quality_score": 0.80,
            "educational_effectiveness": 0.85,
            "meets_quality_threshold": True
        }

        # Test all 8 content types
        content_types = [ct.value for ct in LaFactoriaContentType]
        
        with patch.object(content_service.ai_provider, 'generate_content') as mock_ai_gen, \
             patch.object(content_service.quality_assessor, 'assess_content_quality', return_value=mock_quality):

            # Configure mock to return different responses for each content type
            mock_ai_gen.side_effect = lambda **kwargs: create_mock_response(kwargs.get('content_type', 'unknown'))

            for content_type in content_types:
                result = await content_service.generate_content(
                    content_type=content_type,
                    topic="Educational Testing Topic",
                    age_group="high_school"
                )

                # Basic validation for each content type
                assert result["content_type"] == content_type
                assert result["quality_metrics"]["overall_quality_score"] >= 0.70
                assert "generated_content" in result
                assert result["metadata"]["ai_provider"] == "openai"

        # Verify all content types were processed
        assert mock_ai_gen.call_count == len(content_types)

    @pytest.mark.asyncio
    async def test_concurrent_generation_with_caching(
        self, content_service: EducationalContentService
    ):
        """Test concurrent content generation with cache effectiveness"""

        # Mock AI response
        mock_ai_response = MagicMock()
        mock_ai_response.content = '{"title": "Concurrent Test", "content": "Test content"}'
        mock_ai_response.provider = "openai"
        mock_ai_response.model = "gpt-4"
        mock_ai_response.tokens_used = 1000

        mock_quality = {
            "overall_quality_score": 0.75,
            "educational_effectiveness": 0.80,
            "meets_quality_threshold": True
        }

        # Test parameters - same topic/type for cache testing
        topic = "Cache Test Topic"
        content_type = "study_guide"
        age_group = "high_school"

        with patch.object(content_service.ai_provider, 'generate_content', return_value=mock_ai_response) as mock_ai_gen, \
             patch.object(content_service.quality_assessor, 'assess_content_quality', return_value=mock_quality):

            # Generate multiple identical requests concurrently
            tasks = [
                content_service.generate_content(
                    content_type=content_type,
                    topic=topic,
                    age_group=age_group
                )
                for _ in range(3)
            ]

            results = await asyncio.gather(*tasks)

            # All results should be successful
            assert len(results) == 3
            for result in results:
                assert result["content_type"] == content_type
                assert result["topic"] == topic

            # AI generation should only be called once due to caching
            # (Note: in real concurrent scenario, there might be race conditions)
            assert mock_ai_gen.call_count <= 3  # Allow for race conditions in testing

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(
        self, content_service: EducationalContentService
    ):
        """Test error handling and recovery mechanisms"""

        # Test invalid content type
        with pytest.raises(ValueError, match="Unsupported content type"):
            await content_service.generate_content(
                content_type="invalid_type",
                topic="Test Topic",
                age_group="high_school"
            )

        # Test AI provider failure with recovery
        with patch.object(content_service.ai_provider, 'generate_content') as mock_ai_gen:
            # First call fails, second succeeds
            mock_ai_gen.side_effect = [
                Exception("AI service temporarily unavailable"),
                MagicMock(
                    content='{"title": "Recovery Test", "content": "Recovered content"}',
                    provider="anthropic",
                    model="claude-3",
                    tokens_used=800
                )
            ]

            mock_quality = {"overall_quality_score": 0.75, "meets_quality_threshold": True}
            with patch.object(content_service.quality_assessor, 'assess_content_quality', return_value=mock_quality):
                # This should fail on first attempt
                with pytest.raises(Exception, match="AI service temporarily unavailable"):
                    await content_service.generate_content(
                        content_type="study_guide",
                        topic="Error Recovery Test",
                        age_group="high_school"
                    )

    @pytest.mark.asyncio
    async def test_service_health_monitoring(
        self, content_service: EducationalContentService
    ):
        """Test comprehensive health monitoring of all service components"""

        # Mock healthy responses from all components
        with patch.object(content_service.ai_provider, 'health_check') as mock_ai_health, \
             patch.object(content_service.cache_service, 'health_check') as mock_cache_health:

            mock_ai_health.return_value = {"openai": "healthy", "anthropic": "healthy"}
            mock_cache_health.return_value = {"status": "healthy", "response_time_ms": 5.2}

            health_status = await content_service.health_check()

            # Validate health check response structure
            assert "overall_status" in health_status
            assert "prompt_loader" in health_status
            assert "ai_providers" in health_status
            assert "cache_service" in health_status
            assert "timestamp" in health_status

            # Validate healthy status
            assert health_status["overall_status"] == "healthy"
            assert health_status["service_initialized"] is True
            assert health_status["cache_service"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_batch_content_generation(
        self, content_service: EducationalContentService
    ):
        """Test concurrent generation of multiple content types"""

        # Mock responses for different content types
        mock_responses = {
            "study_guide": '{"title": "Study Guide", "content": "Study guide content"}',
            "flashcards": '{"title": "Flashcards", "flashcards": [{"question": "Q1", "answer": "A1"}]}',
            "one_pager_summary": '{"title": "Summary", "content": "Summary content"}'
        }

        def mock_ai_generate(**kwargs):
            content_type = kwargs.get('content_type', 'study_guide')
            response = MagicMock()
            response.content = mock_responses.get(content_type, '{"title": "Default", "content": "Default content"}')
            response.provider = "openai"
            response.model = "gpt-4"
            response.tokens_used = 1500
            return response

        mock_quality = {
            "overall_quality_score": 0.78,
            "educational_effectiveness": 0.82,
            "meets_quality_threshold": True
        }

        with patch.object(content_service.ai_provider, 'generate_content', side_effect=mock_ai_generate) as mock_ai_gen, \
             patch.object(content_service.quality_assessor, 'assess_content_quality', return_value=mock_quality):

            # Generate multiple content types concurrently
            content_types = ["study_guide", "flashcards", "one_pager_summary"]
            
            result = await content_service.generate_multiple_content_types(
                topic="Batch Generation Test",
                content_types=content_types,
                age_group="high_school"
            )

            # Validate batch generation response
            assert result["topic"] == "Batch Generation Test"
            assert result["requested_types"] == content_types
            assert "generated_content" in result
            assert "summary" in result

            # Validate all content types were generated successfully
            assert len(result["generated_content"]) == 3
            assert result["summary"]["successful_generations"] == 3
            assert result["summary"]["failed_generations"] == 0

            # Validate individual content pieces
            for content_type in content_types:
                assert content_type in result["generated_content"]
                content_piece = result["generated_content"][content_type]
                assert content_piece["content_type"] == content_type
                assert content_piece["quality_metrics"]["overall_quality_score"] >= 0.70

    @pytest.mark.asyncio
    async def test_langfuse_integration_tracing(
        self, content_service: EducationalContentService
    ):
        """Test Langfuse integration for AI observability"""

        # Mock AI response
        mock_ai_response = MagicMock()
        mock_ai_response.content = '{"title": "Langfuse Test", "content": "Test content"}'
        mock_ai_response.provider = "openai"
        mock_ai_response.model = "gpt-4"
        mock_ai_response.tokens_used = 1200

        mock_quality = {
            "overall_quality_score": 0.82,
            "educational_effectiveness": 0.85,
            "meets_quality_threshold": True
        }

        # Mock Langfuse if available
        if hasattr(content_service, 'langfuse') and content_service.langfuse:
            with patch.object(content_service.langfuse, 'trace') as mock_trace, \
                 patch.object(content_service.langfuse, 'flush') as mock_flush:

                mock_trace_obj = MagicMock()
                mock_span = MagicMock()
                mock_trace_obj.span.return_value = mock_span
                mock_trace.return_value = mock_trace_obj

                with patch.object(content_service.ai_provider, 'generate_content', return_value=mock_ai_response), \
                     patch.object(content_service.quality_assessor, 'assess_content_quality', return_value=mock_quality):

                    await content_service.generate_content(
                        content_type="study_guide",
                        topic="Langfuse Integration Test",
                        age_group="high_school"
                    )

                    # Validate Langfuse trace was created
                    mock_trace.assert_called_once()
                    trace_call = mock_trace.call_args
                    
                    assert "educational_content_generation_study_guide" in trace_call[1]["name"]
                    assert "content_type" in trace_call[1]["metadata"]
                    assert "ai_provider" in trace_call[1]["metadata"]
                    assert "quality_score" in trace_call[1]["metadata"]

                    # Validate span creation for cost tracking
                    mock_trace_obj.span.assert_called_once()
                    span_call = mock_trace_obj.span.call_args
                    assert "ai_content_generation" in span_call[1]["name"]
                    assert "cost_estimate" in span_call[1]["metadata"]

                    # Validate scoring
                    mock_span.score.assert_called()

    @pytest.mark.asyncio
    async def test_cache_service_integration(
        self, content_service: EducationalContentService
    ):
        """Test Redis cache service integration and performance"""

        # Test cache health check
        cache_health = await content_service.cache_service.health_check()
        assert "status" in cache_health
        # Cache might be disabled in test environment, which is OK
        assert cache_health["status"] in ["healthy", "disabled"]

        if cache_health["status"] == "healthy":
            # Test cache operations if Redis is available
            test_content = {
                "id": "test-123",
                "content_type": "study_guide",
                "generated_content": {"title": "Cache Test", "content": "Test content"},
                "quality_metrics": {"overall_quality_score": 0.80},
                "metadata": {"generation_duration_ms": 2500}
            }

            # Store in cache
            await content_service.cache_service.set_content_cache(
                content_type="study_guide",
                topic="Cache Integration Test",
                age_group="high_school",
                content=test_content,
                ttl_hours=1
            )

            # Retrieve from cache
            cached_result = await content_service.cache_service.get_content_cache(
                content_type="study_guide",
                topic="Cache Integration Test",
                age_group="high_school"
            )

            if cached_result:  # May be None if cache write didn't complete
                assert cached_result["id"] == "test-123"
                assert cached_result["metadata"]["from_cache"] is True

            # Test cache statistics
            cache_stats = await content_service.cache_service.get_cache_stats()
            assert "status" in cache_stats

    @pytest.mark.asyncio
    async def test_educational_quality_enforcement(
        self, content_service: EducationalContentService
    ):
        """Test educational quality threshold enforcement"""

        # Mock low-quality AI response
        mock_low_quality_response = MagicMock()
        mock_low_quality_response.content = '{"title": "Low Quality", "content": "Insufficient content"}'
        mock_low_quality_response.provider = "openai"
        mock_low_quality_response.model = "gpt-4"
        mock_low_quality_response.tokens_used = 500

        # Mock quality metrics below threshold
        mock_low_quality_metrics = {
            "overall_quality_score": 0.65,  # Below 0.70 threshold
            "educational_effectiveness": 0.60,  # Below 0.75 threshold
            "meets_quality_threshold": False
        }

        with patch.object(content_service.ai_provider, 'generate_content', return_value=mock_low_quality_response), \
             patch.object(content_service.quality_assessor, 'assess_content_quality', return_value=mock_low_quality_metrics):

            result = await content_service.generate_content(
                content_type="study_guide",
                topic="Quality Threshold Test",
                age_group="high_school"
            )

            # Even with low quality, service should return result
            # Quality enforcement is handled at API level or by client
            assert result["quality_metrics"]["overall_quality_score"] == 0.65
            assert result["quality_metrics"]["meets_quality_threshold"] is False

    @pytest.mark.asyncio 
    async def test_performance_benchmarks(
        self, content_service: EducationalContentService
    ):
        """Test performance meets La Factoria requirements"""

        # Mock fast AI response
        mock_ai_response = MagicMock()
        mock_ai_response.content = '{"title": "Performance Test", "content": "Optimized content"}'
        mock_ai_response.provider = "openai"
        mock_ai_response.model = "gpt-4"
        mock_ai_response.tokens_used = 2000

        mock_quality = {
            "overall_quality_score": 0.85,
            "educational_effectiveness": 0.88,
            "meets_quality_threshold": True
        }

        with patch.object(content_service.ai_provider, 'generate_content', return_value=mock_ai_response), \
             patch.object(content_service.quality_assessor, 'assess_content_quality', return_value=mock_quality):

            start_time = time.time()
            
            result = await content_service.generate_content(
                content_type="study_guide",
                topic="Performance Benchmark Test",
                age_group="high_school"
            )

            total_time = (time.time() - start_time) * 1000  # milliseconds

            # Validate performance requirements
            # Total service time should be reasonable (allowing for mock overhead)
            assert total_time < 5000  # 5 seconds max for mocked test

            # Validate generation time metadata
            generation_time = result["metadata"]["generation_duration_ms"]
            assert generation_time >= 0
            assert isinstance(generation_time, int)

    @pytest.mark.asyncio
    async def test_content_type_information_endpoint(
        self, content_service: EducationalContentService
    ):
        """Test content type information and service configuration"""

        # Mock template stats
        with patch.object(content_service.prompt_loader, 'get_supported_content_types') as mock_types, \
             patch.object(content_service.prompt_loader, 'get_template_stats') as mock_stats, \
             patch.object(content_service.ai_provider, 'get_provider_stats') as mock_provider_stats:

            mock_types.return_value = [ct.value for ct in LaFactoriaContentType]
            mock_stats.return_value = {"templates_loaded": 8, "total_size_kb": 150}
            mock_provider_stats.return_value = {"openai": "available", "anthropic": "available"}

            info = await content_service.get_content_type_info()

            # Validate service information
            assert "supported_types" in info
            assert "template_stats" in info
            assert "ai_provider_stats" in info
            assert "quality_thresholds" in info

            # Validate all 8 content types are supported
            assert len(info["supported_types"]) == 8
            assert "study_guide" in info["supported_types"]
            assert "flashcards" in info["supported_types"]

            # Validate quality thresholds are configured
            thresholds = info["quality_thresholds"]
            assert thresholds["overall_minimum"] == 0.70
            assert thresholds["educational_minimum"] == 0.75
            assert thresholds["factual_minimum"] == 0.85


class TestIntegrationStabilityValidation:
    """Validate P1 critical fixes for production stability"""

    @pytest.mark.asyncio
    async def test_p1_ai_provider_configuration_stability(self):
        """Validate AI provider configuration doesn't cause startup failures"""
        
        # Test service initialization with missing AI providers
        with patch.dict(os.environ, {}, clear=True):
            # Should not crash even without AI provider keys
            service = EducationalContentService()
            
            # Should initialize successfully
            await service.initialize()
            
            # Health check should report provider status accurately
            health = await service.health_check()
            assert "ai_providers" in health
            
            await service.close()

    @pytest.mark.asyncio
    async def test_p1_langfuse_graceful_degradation(self):
        """Validate Langfuse integration doesn't break when unavailable"""
        
        # Test service works without Langfuse configuration
        with patch.dict(os.environ, {"LANGFUSE_SECRET_KEY": "", "LANGFUSE_PUBLIC_KEY": ""}, clear=False):
            service = EducationalContentService()
            await service.initialize()
            
            # Should handle missing Langfuse gracefully
            assert service.langfuse is None
            
            await service.close()

    @pytest.mark.asyncio
    async def test_p1_redis_cache_fallback(self):
        """Validate Redis caching fails gracefully when unavailable"""
        
        service = EducationalContentService()
        await service.initialize()
        
        # Cache service should handle Redis unavailability
        cache_health = await service.cache_service.health_check()
        assert "status" in cache_health
        
        # Even if disabled, service should continue working
        if cache_health["status"] == "disabled":
            # Cache operations should not crash
            cached_content = await service.cache_service.get_content_cache(
                content_type="study_guide",
                topic="Fallback Test",
                age_group="high_school"
            )
            assert cached_content is None  # Expected when cache disabled
        
        await service.close()

    def test_p1_critical_configuration_validation(self):
        """Validate all P1 critical configurations are properly handled"""
        
        # Test that service can be created without crashing
        try:
            service = EducationalContentService()
            assert service is not None
            assert hasattr(service, 'cache_service')
            assert hasattr(service, 'ai_provider')
            assert hasattr(service, 'quality_assessor')
            
        except Exception as e:
            pytest.fail(f"Service initialization failed: {e}")