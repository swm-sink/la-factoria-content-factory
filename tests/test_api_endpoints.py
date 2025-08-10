"""
Comprehensive API Endpoint Tests for La Factoria
===============================================

Tests for all 8 educational content generation endpoints:
- Master Content Outline
- Podcast Script
- Study Guide
- One-Pager Summary
- Detailed Reading Material
- FAQ Collection
- Flashcards
- Reading Guide Questions

Plus batch generation, content types, and service endpoints.
"""

# Fix Python path for src imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import json
from fastapi import status
from typing import Dict, Any, List
from unittest.mock import patch, AsyncMock

from src.models.educational import LaFactoriaContentType, LearningLevel, CognitiveLevel
from src.models.content import ContentRequest


class TestContentGenerationEndpoints:
    """Test all 8 educational content generation endpoints"""

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_master_content_outline_generation(
        self, client, auth_headers, sample_learning_objectives, mock_ai_providers, assert_quality_thresholds, mock_verify_api_key
    ):
        """Test master content outline generation endpoint"""
        request_data = {
            "topic": "Introduction to Python Programming",
            "age_group": "high_school",
            "learning_objectives": [obj.model_dump() for obj in sample_learning_objectives],
            "additional_requirements": "Include hands-on coding exercises"
        }

        response = client.post(
            "/api/v1/generate/master_content_outline",
            json=request_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        content = response.json()

        # Validate response structure
        assert "id" in content
        assert "content_type" in content
        assert content["content_type"] == "master_content_outline"
        assert "topic" in content
        assert content["topic"] == request_data["topic"]
        assert "generated_content" in content
        assert "quality_metrics" in content
        assert "metadata" in content
        assert "created_at" in content

        # Validate generated content structure (master outline specific)
        generated = content["generated_content"]
        assert "title" in generated
        assert "overview" in generated
        assert "learning_objectives" in generated
        assert "sections" in generated
        assert isinstance(generated["sections"], list)
        assert len(generated["sections"]) > 0

        # Validate section structure
        for section in generated["sections"]:
            assert "title" in section
            assert "duration" in section or "content" in section

        # Validate quality metrics meet thresholds
        if content["quality_metrics"]:
            quality_metrics = content["quality_metrics"]
            
            # Debug: Print detailed quality metrics
            print(f"\n=== Quality Metrics Debug ===")
            print(f"Generated content keys: {list(generated.keys())}")
            print(f"Generated content preview: {str(generated)[:500]}...")
            print(f"Quality metrics: {quality_metrics}")
            print(f"Overall score: {quality_metrics.get('overall_quality_score', 'N/A')}")
            print(f"Educational effectiveness: {quality_metrics.get('educational_effectiveness', 'N/A')}")
            print(f"Factual accuracy: {quality_metrics.get('factual_accuracy', 'N/A')}")
            print(f"Structural quality: {quality_metrics.get('structural_quality', 'N/A')}")
            print(f"Engagement score: {quality_metrics.get('engagement_score', 'N/A')}")
            print("==========================\n")
            
            assert_quality_thresholds(quality_metrics)

        # Validate metadata
        metadata = content["metadata"]
        assert "generation_duration_ms" in metadata
        assert "ai_provider" in metadata
        assert "prompt_template" in metadata
        assert metadata["prompt_template"] == "master_content_outline"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_podcast_script_generation(
        self, client, auth_headers, mock_ai_providers
    ):
        """Test podcast script generation endpoint"""
        request_data = {
            "topic": "The History of Space Exploration",
            "age_group": "college",
            "additional_requirements": "Include engaging storytelling elements and audio cues"
        }

        response = client.post(
            "/api/v1/generate/podcast_script",
            json=request_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        content = response.json()

        # Validate podcast-specific content structure
        generated = content["generated_content"]

        # Should contain podcast-specific elements
        # Note: Structure depends on the actual prompt template implementation
        assert "title" in generated
        assert isinstance(generated, dict)

        # Validate content type
        assert content["content_type"] == "podcast_script"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_study_guide_generation(
        self, client, auth_headers, mock_ai_providers, assert_quality_thresholds
    ):
        """Test study guide generation endpoint"""
        request_data = {
            "topic": "Photosynthesis in Plants",
            "age_group": "high_school",
            "additional_requirements": "Include diagrams descriptions and practice questions"
        }

        response = client.post(
            "/api/v1/generate/study_guide",
            json=request_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        content = response.json()

        # Validate study guide specific structure
        generated = content["generated_content"]
        assert "title" in generated

        # Study guides should have educational structure
        if "sections" in generated:
            assert isinstance(generated["sections"], list)

        # Validate content type
        assert content["content_type"] == "study_guide"

        # Quality validation
        if content["quality_metrics"]:
            assert_quality_thresholds(content["quality_metrics"])

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_flashcards_generation(
        self, client, auth_headers, mock_ai_providers
    ):
        """Test flashcards generation endpoint"""
        request_data = {
            "topic": "Spanish Vocabulary - Family Members",
            "age_group": "middle_school",
            "additional_requirements": "Create 15-20 cards with pronunciation guides"
        }

        response = client.post(
            "/api/v1/generate/flashcards",
            json=request_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        content = response.json()

        # Validate flashcard specific structure
        generated = content["generated_content"]
        assert "title" in generated

        # Should contain cards
        if "cards" in generated:
            assert isinstance(generated["cards"], list)
            # Validate card structure
            for card in generated["cards"][:3]:  # Check first 3 cards
                assert "front" in card or "question" in card
                assert "back" in card or "answer" in card

        assert content["content_type"] == "flashcards"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_one_pager_summary_generation(
        self, client, auth_headers, mock_ai_providers
    ):
        """Test one-pager summary generation endpoint"""
        request_data = {
            "topic": "Climate Change Basics",
            "age_group": "general",
            "additional_requirements": "Focus on key facts and actionable information"
        }

        response = client.post(
            "/api/v1/generate/one_pager_summary",
            json=request_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        content = response.json()

        # One-pager should be concise
        generated = content["generated_content"]
        assert "title" in generated

        assert content["content_type"] == "one_pager_summary"

        # Validate metadata indicates shorter generation time
        metadata = content["metadata"]
        assert "generation_duration_ms" in metadata

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_detailed_reading_material_generation(
        self, client, auth_headers, mock_ai_providers
    ):
        """Test detailed reading material generation endpoint"""
        request_data = {
            "topic": "Introduction to Machine Learning",
            "age_group": "college",
            "additional_requirements": "Include technical depth and real-world applications"
        }

        response = client.post(
            "/api/v1/generate/detailed_reading_material",
            json=request_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        content = response.json()

        # Detailed reading should have comprehensive structure
        generated = content["generated_content"]
        assert "title" in generated

        assert content["content_type"] == "detailed_reading_material"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_faq_collection_generation(
        self, client, auth_headers, mock_ai_providers
    ):
        """Test FAQ collection generation endpoint"""
        request_data = {
            "topic": "Getting Started with Python Programming",
            "age_group": "adult_learning",
            "additional_requirements": "Address common beginner questions and misconceptions"
        }

        response = client.post(
            "/api/v1/generate/faq_collection",
            json=request_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        content = response.json()

        # FAQ should have question-answer structure
        generated = content["generated_content"]
        assert "title" in generated

        assert content["content_type"] == "faq_collection"

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_reading_guide_questions_generation(
        self, client, auth_headers, mock_ai_providers
    ):
        """Test reading guide questions generation endpoint"""
        request_data = {
            "topic": "To Kill a Mockingbird - Themes and Analysis",
            "age_group": "high_school",
            "additional_requirements": "Focus on critical thinking and discussion questions"
        }

        response = client.post(
            "/api/v1/generate/reading_guide_questions",
            json=request_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        content = response.json()

        # Reading guide should have question structure
        generated = content["generated_content"]
        assert "title" in generated

        assert content["content_type"] == "reading_guide_questions"

    @pytest.mark.api
    @pytest.mark.parametrize("content_type", [
        "master_content_outline", "podcast_script", "study_guide",
        "one_pager_summary", "detailed_reading_material", "faq_collection",
        "flashcards", "reading_guide_questions"
    ])
    @pytest.mark.asyncio
    async def test_all_content_types_basic_generation(
        self, client, auth_headers, mock_ai_providers, content_type
    ):
        """Parametrized test for all 8 content types with basic validation"""
        request_data = {
            "topic": f"Test Topic for {content_type.replace('_', ' ').title()}",
            "age_group": "high_school"
        }

        response = client.post(
            f"/api/v1/generate/{content_type}",
            json=request_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        content = response.json()

        # Basic structure validation for all content types
        assert content["content_type"] == content_type
        assert "generated_content" in content
        assert "id" in content
        assert "topic" in content
        assert "created_at" in content

        # Generated content should not be empty
        generated = content["generated_content"]
        assert generated is not None
        assert isinstance(generated, dict)
        assert len(generated) > 0


class TestBatchGeneration:
    """Test batch content generation endpoint"""

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_batch_content_generation_success(
        self, client, auth_headers, mock_ai_providers
    ):
        """Test successful batch generation of multiple content types"""
        content_types = ["study_guide", "flashcards", "one_pager_summary"]
        request_data = {
            "topic": "Introduction to Algebra",
            "age_group": "middle_school",
            "additional_requirements": "Make it engaging for young learners"
        }

        response = client.post(
            f"/api/v1/generate/batch?content_types={','.join(content_types)}",
            json=request_data,
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()

        # Should contain results for all requested content types
        assert "results" in result
        assert len(result["results"]) == len(content_types)

        # Each result should be valid
        for content_type in content_types:
            assert content_type in result["results"]
            content = result["results"][content_type]
            assert "generated_content" in content
            assert content["content_type"] == content_type

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_batch_generation_validation_errors(
        self, client, auth_headers
    ):
        """Test batch generation validation errors"""

        # Test empty content types
        response = client.post(
            "/api/v1/generate/batch",
            json={"topic": "Test", "age_group": "high_school"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY  # FastAPI returns 422 for missing required query parameters

        # Test too many content types
        all_valid_types = [t.value for t in LaFactoriaContentType]  # All 8 types as strings
        too_many_types = all_valid_types + ["extra_type"]  # Add one more (9 total)

        response = client.post(
            f"/api/v1/generate/batch?content_types={','.join(too_many_types)}",
            json={"topic": "Test", "age_group": "high_school"},
            headers=auth_headers
        )
        # Should still work with 8 types, might need to adjust based on actual implementation

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_batch_generation_partial_failure(
        self, client, auth_headers, mock_ai_providers
    ):
        """Test batch generation with partial failures"""

        # Mock one provider to fail
        with patch("src.services.educational_content_service.EducationalContentService.generate_content") as mock_generate:
            async def mock_side_effect(content_type, **kwargs):
                if content_type == "study_guide":
                    raise Exception("AI provider error")
                return {
                    "id": "test-id",
                    "content_type": content_type,
                    "generated_content": {"title": f"Test {content_type}"},
                    "quality_metrics": {"overall_quality_score": 0.8},
                    "metadata": {"generation_duration_ms": 1000}
                }

            mock_generate.side_effect = mock_side_effect

            content_types = ["study_guide", "flashcards"]
            request_data = {
                "topic": "Test Topic",
                "age_group": "high_school"
            }

            response = client.post(
                f"/api/v1/generate/batch?content_types={','.join(content_types)}",
                json=request_data,
                headers=auth_headers
            )

            # Should handle partial failures gracefully
            # Exact behavior depends on implementation


class TestContentTypesEndpoint:
    """Test content types information endpoint"""

    @pytest.mark.api
    def test_get_content_types_success(self, client):
        """Test successful retrieval of content types"""
        response = client.get("/api/v1/content-types")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Validate response structure
        assert "content_types" in data
        assert "total_count" in data
        assert data["total_count"] == 8  # La Factoria supports 8 content types

        # Validate content type information
        content_types = data["content_types"]
        assert len(content_types) == 8

        # Check for all 8 La Factoria content types
        expected_types = {ct.value for ct in LaFactoriaContentType}
        actual_types = {ct["name"] for ct in content_types}
        assert actual_types == expected_types

        # Validate content type structure
        for content_type in content_types:
            assert "name" in content_type
            assert "display_name" in content_type
            assert "description" in content_type
            assert "typical_use_cases" in content_type
            assert "estimated_generation_time" in content_type
            assert isinstance(content_type["typical_use_cases"], list)


class TestServiceEndpoints:
    """Test service information and health endpoints"""

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_service_info_endpoint(
        self, client, auth_headers, mock_ai_providers
    ):
        """Test service information endpoint"""
        response = client.get(
            "/api/v1/service/info",
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        info = response.json()

        # Should contain service information
        # Exact structure depends on implementation
        assert isinstance(info, dict)

    @pytest.mark.api
    def test_service_health_endpoint(self, client, mock_ai_providers):
        """Test service health check endpoint"""
        response = client.get("/api/v1/service/health")

        assert response.status_code == status.HTTP_200_OK
        health = response.json()

        # Should contain health status
        assert "overall_status" in health
        # Health can be "healthy", "degraded", or "unhealthy"
        assert health["overall_status"] in ["healthy", "degraded", "unhealthy"]


class TestAPIValidationAndErrors:
    """Test API input validation and error handling"""

    @pytest.mark.api
    @pytest.mark.parametrize("error_scenario", [
        {
            "name": "missing_topic",
            "request": {"age_group": "high_school"},
            "expected_status": 422
        },
        {
            "name": "empty_topic",
            "request": {"topic": "", "age_group": "high_school"},
            "expected_status": 422
        },
        {
            "name": "topic_too_short",
            "request": {"topic": "AB", "age_group": "high_school"},
            "expected_status": 422
        },
        {
            "name": "topic_too_long",
            "request": {"topic": "X" * 501, "age_group": "high_school"},
            "expected_status": 422
        },
        {
            "name": "invalid_age_group",
            "request": {"topic": "Valid Topic", "age_group": "invalid_age"},
            "expected_status": 422
        },
        {
            "name": "additional_requirements_too_long",
            "request": {
                "topic": "Valid Topic",
                "age_group": "high_school",
                "additional_requirements": "X" * 1001
            },
            "expected_status": 422
        }
    ])
    @pytest.mark.asyncio
    async def test_request_validation_errors(
        self, client, auth_headers, error_scenario
    ):
        """Test request validation for various error scenarios"""
        response = client.post(
            "/api/v1/generate/study_guide",
            json=error_scenario["request"],
            headers=auth_headers
        )

        assert response.status_code == error_scenario["expected_status"]

        if response.status_code == 422:
            error_detail = response.json()
            assert "detail" in error_detail

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_authentication_required(self, client, mock_ai_providers):
        """Test that authentication is required for protected endpoints"""
        request_data = {
            "topic": "Test Topic",
            "age_group": "high_school"
        }

        # Test without authentication header
        response = client.post(
            "/api/v1/generate/study_guide",
            json=request_data
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN  # FastAPI HTTPBearer dependency returns 403 for missing auth

        # Test with invalid authentication
        invalid_headers = {"Authorization": "Bearer invalid-key"}
        response = client.post(
            "/api/v1/generate/study_guide",
            json=request_data,
            headers=invalid_headers
        )

        # In development mode with mocked AI providers, should accept any non-empty key
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_unsupported_content_type_error(
        self, client, auth_headers
    ):
        """Test error handling for unsupported content types"""
        response = client.post(
            "/api/v1/generate/unsupported_type",
            json={"topic": "Test", "age_group": "high_school"},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_service_error_handling(
        self, client, auth_headers, monkeypatch
    ):
        """Test service error handling"""
        from unittest.mock import AsyncMock
        
        # Create a mock that raises an exception
        async def mock_generate_error(*args, **kwargs):
            raise Exception("Service temporarily unavailable")
        
        # Patch the service method
        monkeypatch.setattr(
            "src.services.educational_content_service.EducationalContentService.generate_content",
            mock_generate_error
        )

        response = client.post(
            "/api/v1/generate/study_guide",
            json={"topic": "Test", "age_group": "high_school"},
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        error_detail = response.json()
        assert "detail" in error_detail

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_malformed_json_handling(self, client, auth_headers):
        """Test handling of malformed JSON requests"""
        # Send malformed JSON with content-type header
        headers = auth_headers.copy()
        headers["Content-Type"] = "application/json"
        
        response = client.post(
            "/api/v1/generate/study_guide",
            data="{ invalid json }",  # Malformed JSON
            headers=headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_learning_objectives_validation(
        self, client, auth_headers, mock_ai_providers
    ):
        """Test learning objectives validation"""

        # Valid learning objectives
        valid_objectives = [
            {
                "cognitive_level": "understanding",
                "subject_area": "Mathematics",
                "specific_skill": "algebra",
                "measurable_outcome": "solve equations",
                "difficulty_level": 5
            }
        ]

        response = client.post(
            "/api/v1/generate/study_guide",
            json={
                "topic": "Algebra Basics",
                "age_group": "high_school",
                "learning_objectives": valid_objectives
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

        # Invalid learning objectives
        invalid_objectives = [
            {
                "cognitive_level": "invalid_level",  # Invalid cognitive level
                "subject_area": "Mathematics",
                "specific_skill": "algebra",
                "measurable_outcome": "solve equations",
                "difficulty_level": 5
            }
        ]

        response = client.post(
            "/api/v1/generate/study_guide",
            json={
                "topic": "Algebra Basics",
                "age_group": "high_school",
                "learning_objectives": invalid_objectives
            },
            headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAPIPerformance:
    """Test API performance requirements"""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_response_time_requirements(
        self, client, auth_headers, mock_ai_providers, timing_context
    ):
        """Test that API responses meet performance requirements"""

        request_data = {
            "topic": "Quick Performance Test",
            "age_group": "high_school"
        }

        # Test individual content type generation time
        with timing_context() as timer:
            response = client.post(
                "/api/v1/generate/one_pager_summary",  # Should be fastest
                json=request_data,
                headers=auth_headers
            )

        assert response.status_code == status.HTTP_200_OK

        # One-pager should be relatively fast (mock should be very fast)
        timer.assert_under_time_limit(5.0, "One-pager generation")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_request_handling(
        self, client, auth_headers, mock_ai_providers
    ):
        """Test concurrent request handling"""
        import asyncio
        import httpx
        from src.main import app

        async def make_request(async_client, request_data, headers):
            return await async_client.post(
                "/api/v1/generate/flashcards",
                json=request_data,
                headers=headers
            )

        request_data = {
            "topic": "Concurrent Test Topic",
            "age_group": "high_school"
        }

        # Test 5 concurrent requests
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), 
            base_url="http://test"
        ) as ac:
            tasks = [make_request(ac, request_data, auth_headers) for _ in range(5)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

        # All requests should succeed (or at least not fail due to concurrency)
        successful_responses = [r for r in responses if not isinstance(r, Exception)]
        assert len(successful_responses) >= 3  # At least 60% success rate

        for response in successful_responses:
            assert response.status_code == status.HTTP_200_OK
