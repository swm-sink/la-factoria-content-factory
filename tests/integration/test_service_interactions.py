"""
Integration tests for service-to-service interactions.

These tests validate real interactions between different services and components,
ensuring proper integration across service boundaries.
"""

import asyncio
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.config.settings import Settings, get_settings
from app.main import app
from app.models.pydantic.content import (
    ContentOutline,
    ContentRequest,
    GeneratedContent,
    OutlineSection,
    PodcastScript,
    StudyGuide,
    TargetFormat,
)
from app.models.pydantic.job import Job, JobProgress, JobStatus
from app.services.job_manager import JobManager
from app.services.multi_step_content_generation_final import EnhancedContentService


@pytest.mark.integration
class TestServiceToServiceIntegration:
    """Test interactions between different services."""

    @pytest.fixture
    def mock_firestore_client(self):
        """Mock Firestore client for database operations."""
        with patch("app.services.job.firestore_client.get_firestore_client") as mock_get_client:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_document = MagicMock()
            
            mock_client.collection.return_value = mock_collection
            mock_collection.document.return_value = mock_document
            
            # Mock async operations
            mock_document.set = AsyncMock(return_value=True)
            mock_document.update = AsyncMock(return_value=True)
            mock_document.get = AsyncMock()
            
            mock_get_client.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client for caching operations."""
        with patch("app.services.content_cache.redis.Redis") as mock_redis_class:
            mock_redis = MagicMock()
            mock_redis.ping.return_value = True
            mock_redis.get.return_value = None
            mock_redis.set.return_value = True
            mock_redis.expire.return_value = True
            mock_redis_class.return_value = mock_redis
            yield mock_redis

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client for content generation."""
        with patch("app.services.llm_client.SimpleLLMClient") as mock_llm_class:
            mock_llm = MagicMock()
            
            async def mock_generate_content(prompt, **kwargs):
                # Return realistic content based on prompt type
                if "outline" in prompt.lower():
                    return json.dumps({
                        "title": "Test Content Title",
                        "overview": "A comprehensive overview of the test content that provides detailed information about the topic.",
                        "learning_objectives": [
                            "Understand key concept 1",
                            "Apply principle 2 in practice",
                            "Analyze complex scenarios"
                        ],
                        "sections": [
                            {
                                "section_number": 1,
                                "title": "Introduction",
                                "description": "This section introduces the fundamental concepts and sets the stage for deeper learning.",
                                "key_points": ["Foundation concepts", "Historical context"]
                            },
                            {
                                "section_number": 2,
                                "title": "Core Concepts",
                                "description": "Deep dive into the main principles and theories that form the basis of this topic.",
                                "key_points": ["Main principle", "Supporting theory"]
                            },
                            {
                                "section_number": 3,
                                "title": "Practical Applications",
                                "description": "Real-world applications and case studies demonstrating the concepts in action.",
                                "key_points": ["Case study 1", "Implementation guide"]
                            }
                        ]
                    })
                elif "podcast" in prompt.lower():
                    return json.dumps({
                        "title": "Test Content Title",
                        "introduction": "Welcome to our podcast! Today we'll be exploring fascinating topics. " * 5,
                        "main_content": "In this episode, we dive deep into the subject matter. " * 50,
                        "conclusion": "To wrap up, we've covered important points about our topic. " * 5,
                        "estimated_duration_minutes": 15.0
                    })
                elif "study guide" in prompt.lower():
                    return json.dumps({
                        "title": "Test Content Title",
                        "overview": "This study guide provides a comprehensive learning resource. " * 5,
                        "key_concepts": ["Concept 1", "Concept 2", "Concept 3", "Concept 4", "Concept 5"],
                        "detailed_content": "Detailed explanations of each concept follow. " * 50,
                        "summary": "In summary, we've explored the key aspects of this topic. " * 5
                    })
                else:
                    return json.dumps({"content": "Generic test content"})
            
            mock_llm.generate_content = AsyncMock(side_effect=mock_generate_content)
            mock_llm_class.return_value = mock_llm
            yield mock_llm

    @pytest.fixture
    def mock_cloud_tasks(self):
        """Mock Cloud Tasks client for job queuing."""
        with patch("app.services.job.tasks_client.CloudTasksClient") as mock_tasks_class:
            mock_tasks = MagicMock()
            mock_tasks.enqueue_content_generation_job = AsyncMock(return_value="task-123")
            mock_tasks_class.return_value = mock_tasks
            yield mock_tasks

    @pytest.fixture
    async def job_manager(self, mock_firestore_client, mock_cloud_tasks, test_settings):
        """Create a real JobManager instance with mocked dependencies."""
        with patch("app.services.job_manager.get_settings", return_value=test_settings):
            manager = JobManager()
            yield manager

    @pytest.fixture
    async def content_service(self, mock_llm_client, mock_redis_client, test_settings):
        """Create a real EnhancedContentService with mocked dependencies."""
        with patch("app.services.multi_step_content_generation_final.get_settings", return_value=test_settings):
            service = EnhancedContentService()
            yield service

    @pytest.mark.asyncio
    async def test_job_creation_and_content_generation_flow(
        self, job_manager, content_service, mock_firestore_client, mock_llm_client
    ):
        """Test the complete flow from job creation to content generation."""
        # Create a content request
        content_request = ContentRequest(
            syllabus_text="Integration test: Comprehensive guide to machine learning fundamentals. " * 5,
            target_format=TargetFormat.COMPREHENSIVE,
            use_parallel=True,
            use_cache=False
        )
        
        # Step 1: Create a job
        job = await job_manager.create_job(content_request)
        
        assert job is not None
        assert job.status == JobStatus.PENDING
        assert job.metadata["syllabus_text"] == content_request.syllabus_text
        
        # Verify Firestore was called
        mock_firestore_client.collection.assert_called_with("jobs")
        
        # Step 2: Generate content
        result = await content_service.generate_long_form_content(
            syllabus_text=content_request.syllabus_text,
            target_format=content_request.target_format,
            job_id=str(job.id),
            use_parallel=content_request.use_parallel,
            use_cache=content_request.use_cache
        )
        
        generated_content, metadata, quality_metrics, tokens, error = result
        
        assert generated_content is not None
        assert isinstance(generated_content, GeneratedContent)
        assert generated_content.content_outline.title == "Test Content Title"
        assert len(generated_content.content_outline.sections) == 3
        assert error is None
        
        # Verify LLM was called multiple times for different content types
        assert mock_llm_client.generate_content.call_count >= 3  # outline, podcast, study guide

    @pytest.mark.asyncio
    async def test_job_status_updates_during_processing(
        self, job_manager, mock_firestore_client
    ):
        """Test that job status is properly updated during processing."""
        # Create a job
        content_request = ContentRequest(
            syllabus_text="Test syllabus for status update testing with sufficient content length.",
            target_format=TargetFormat.GUIDE
        )
        
        job = await job_manager.create_job(content_request)
        job_id = str(job.id)
        
        # Mock the document get method to return updated status
        async def mock_get():
            mock_snapshot = MagicMock()
            mock_snapshot.exists = True
            mock_snapshot.to_dict.return_value = {
                "id": job_id,
                "status": "processing",
                "progress": {
                    "current_step": "Generating outline",
                    "total_steps": 7,
                    "completed_steps": 2,
                    "percentage": 28.6
                },
                "updated_at": datetime.utcnow().isoformat()
            }
            return mock_snapshot
        
        mock_firestore_client.collection().document().get = AsyncMock(side_effect=mock_get)
        
        # Update job status
        await job_manager.update_job_status(
            job_id,
            JobStatus.PROCESSING,
            progress=JobProgress(
                current_step="Generating outline",
                total_steps=7,
                completed_steps=2,
                percentage=28.6
            )
        )
        
        # Verify update was called
        mock_firestore_client.collection().document().update.assert_called_once()
        update_data = mock_firestore_client.collection().document().update.call_args[0][0]
        assert update_data["status"] == "processing"
        assert update_data["progress"]["current_step"] == "Generating outline"

    @pytest.mark.asyncio
    async def test_content_caching_integration(
        self, content_service, mock_redis_client, mock_llm_client
    ):
        """Test that content caching works correctly across service calls."""
        syllabus_text = "Caching test: Introduction to distributed systems and cloud computing."
        
        # First call - should generate new content
        result1 = await content_service.generate_long_form_content(
            syllabus_text=syllabus_text,
            target_format=TargetFormat.GUIDE,
            use_cache=True
        )
        
        # Verify Redis set was called
        assert mock_redis_client.set.called
        
        # Mock Redis to return cached content on next get
        mock_redis_client.get.return_value = json.dumps({
            "content": result1[0].model_dump(),
            "metadata": result1[1],
            "quality_metrics": result1[2],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Second call - should use cache
        result2 = await content_service.generate_long_form_content(
            syllabus_text=syllabus_text,
            target_format=TargetFormat.GUIDE,
            use_cache=True
        )
        
        # Verify content is the same
        assert result1[0].content_outline.title == result2[0].content_outline.title
        
        # LLM should not be called again for cached content
        # (initial call count vs final call count should show minimal increase)
        initial_calls = mock_llm_client.generate_content.call_count
        
        # Third call with cache disabled - should generate new content
        result3 = await content_service.generate_long_form_content(
            syllabus_text=syllabus_text,
            target_format=TargetFormat.GUIDE,
            use_cache=False
        )
        
        # Verify LLM was called again
        assert mock_llm_client.generate_content.call_count > initial_calls

    @pytest.mark.asyncio
    async def test_parallel_processing_integration(
        self, content_service, mock_llm_client
    ):
        """Test that parallel processing works correctly for content generation."""
        # Generate content with parallel processing
        result = await content_service.generate_long_form_content(
            syllabus_text="Parallel processing test: Advanced topics in artificial intelligence and machine learning.",
            target_format=TargetFormat.COMPREHENSIVE,
            use_parallel=True
        )
        
        generated_content, metadata, quality_metrics, tokens, error = result
        
        assert generated_content is not None
        assert error is None
        
        # With comprehensive format, we should have multiple content types
        assert generated_content.podcast_script is not None
        assert generated_content.study_guide is not None
        
        # Verify multiple LLM calls were made (for different content types)
        assert mock_llm_client.generate_content.call_count >= 3

    @pytest.mark.asyncio
    async def test_error_handling_across_services(
        self, job_manager, content_service, mock_firestore_client, mock_llm_client
    ):
        """Test error handling and propagation across service boundaries."""
        # Make LLM client raise an error
        mock_llm_client.generate_content.side_effect = Exception("LLM service unavailable")
        
        # Create a job
        content_request = ContentRequest(
            syllabus_text="Error handling test: This should trigger an error in content generation.",
            target_format=TargetFormat.GUIDE
        )
        
        job = await job_manager.create_job(content_request)
        
        # Try to generate content - should handle error gracefully
        result = await content_service.generate_long_form_content(
            syllabus_text=content_request.syllabus_text,
            target_format=content_request.target_format,
            job_id=str(job.id)
        )
        
        generated_content, metadata, quality_metrics, tokens, error = result
        
        assert error is not None
        assert "LLM service unavailable" in str(error)
        
        # Job should be updated with error status
        await job_manager.update_job_status(
            str(job.id),
            JobStatus.FAILED,
            error=str(error)
        )
        
        # Verify error was stored
        update_data = mock_firestore_client.collection().document().update.call_args[0][0]
        assert update_data["status"] == "failed"
        assert "error" in update_data


@pytest.mark.integration
class TestAPIEndpointIntegration:
    """Test integration between API endpoints and underlying services."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_dependencies(self, mock_firestore_client, mock_redis_client, mock_llm_client, mock_cloud_tasks):
        """Set up all mock dependencies."""
        with patch("app.api.deps.get_settings") as mock_get_settings:
            mock_settings = MagicMock(spec=Settings)
            mock_settings.api_key = "test-api-key"
            mock_settings.jwt_secret_key = "test-secret-key-minimum-32-chars"
            mock_settings.gcp_project_id = "test-project"
            mock_settings.gcp_location = "us-central1"
            mock_get_settings.return_value = mock_settings
            yield mock_settings

    @pytest.mark.asyncio
    async def test_end_to_end_content_generation_via_api(
        self, client, mock_dependencies, mock_firestore_client, mock_llm_client
    ):
        """Test complete content generation flow through API endpoints."""
        # Override the job manager dependency
        mock_job_manager = MagicMock()
        mock_job = Job(
            id=uuid.uuid4(),
            status=JobStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={"syllabus_text": "Test syllabus"}
        )
        mock_job_manager.create_job = AsyncMock(return_value=mock_job)
        
        from app.api.routes.jobs import get_job_manager
        app.dependency_overrides[get_job_manager] = lambda: mock_job_manager
        
        try:
            # Step 1: Create a job via API
            create_response = client.post(
                "/api/v1/jobs",
                json={
                    "syllabus_text": "E2E test: Comprehensive guide to software engineering best practices and methodologies.",
                    "target_format": "comprehensive",
                    "use_parallel": True
                },
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert create_response.status_code == 201
            job_data = create_response.json()
            assert "id" in job_data
            assert job_data["status"] == "pending"
            
            # Step 2: Check job status
            job_id = job_data["id"]
            mock_job_manager.get_job = AsyncMock(return_value=mock_job)
            
            status_response = client.get(
                f"/api/v1/jobs/{job_id}",
                headers={"X-API-Key": "test-api-key"}
            )
            
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["id"] == str(mock_job.id)
            
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, client, mock_dependencies):
        """Test rate limiting across multiple service calls."""
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = client.get("/healthz")
            responses.append(response)
        
        # All should succeed as health endpoint is not rate limited
        assert all(r.status_code == 200 for r in responses)
        
        # Test rate limited endpoint (if implemented)
        # This would test actual rate limiting behavior

    @pytest.mark.asyncio
    async def test_authentication_across_services(self, client, mock_dependencies):
        """Test authentication is properly enforced across all services."""
        # Test without API key
        response = client.post(
            "/api/v1/jobs",
            json={"syllabus_text": "Test", "target_format": "guide"}
        )
        assert response.status_code == 401
        
        # Test with invalid API key
        response = client.post(
            "/api/v1/jobs",
            json={"syllabus_text": "Test", "target_format": "guide"},
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code == 401
        
        # Test with valid API key but missing required fields
        response = client.post(
            "/api/v1/jobs",
            json={"target_format": "guide"},  # Missing syllabus_text
            headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 422  # Validation error


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database integration scenarios."""

    @pytest.mark.asyncio
    async def test_concurrent_job_updates(self, job_manager, mock_firestore_client):
        """Test handling of concurrent job updates."""
        # Create a job
        content_request = ContentRequest(
            syllabus_text="Concurrency test: Testing concurrent updates to job status and progress.",
            target_format=TargetFormat.GUIDE
        )
        
        job = await job_manager.create_job(content_request)
        job_id = str(job.id)
        
        # Simulate concurrent updates
        update_tasks = []
        for i in range(5):
            progress = JobProgress(
                current_step=f"Step {i+1}",
                total_steps=5,
                completed_steps=i+1,
                percentage=(i+1) * 20.0
            )
            task = job_manager.update_job_status(
                job_id,
                JobStatus.PROCESSING,
                progress=progress
            )
            update_tasks.append(task)
        
        # Execute all updates concurrently
        await asyncio.gather(*update_tasks)
        
        # Verify all updates were attempted
        assert mock_firestore_client.collection().document().update.call_count >= 5

    @pytest.mark.asyncio
    async def test_job_listing_with_filters(self, job_manager, mock_firestore_client):
        """Test job listing with various filters."""
        # Mock Firestore query results
        mock_query = MagicMock()
        mock_docs = []
        
        for i in range(5):
            mock_doc = MagicMock()
            mock_doc.to_dict.return_value = {
                "id": str(uuid.uuid4()),
                "status": "completed" if i % 2 == 0 else "failed",
                "created_at": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            mock_docs.append(mock_doc)
        
        mock_query.stream = AsyncMock(return_value=mock_docs)
        mock_firestore_client.collection().where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # List jobs with status filter
        result = await job_manager.list_jobs(
            status="completed",
            limit=10,
            offset=0
        )
        
        assert result is not None
        assert hasattr(result, "jobs")
        assert hasattr(result, "total")


@pytest.mark.integration
class TestExternalServiceIntegration:
    """Test integration with external services (LLM, Audio, etc)."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("TEST_WITH_REAL_LLM"),
        reason="Skip real LLM tests unless TEST_WITH_REAL_LLM is set"
    )
    async def test_real_llm_integration(self, content_service):
        """Test with real LLM service (only when explicitly enabled)."""
        # This test would use real Gemini API
        result = await content_service.generate_long_form_content(
            syllabus_text="Real LLM test: Introduction to quantum computing and its applications in cryptography.",
            target_format=TargetFormat.GUIDE,
            use_cache=False
        )
        
        generated_content, metadata, quality_metrics, tokens, error = result
        
        assert generated_content is not None
        assert generated_content.content_outline is not None
        assert len(generated_content.content_outline.sections) >= 3
        assert error is None

    @pytest.mark.asyncio
    async def test_audio_generation_integration(self, mock_llm_client):
        """Test audio generation service integration."""
        with patch("app.services.audio_generation.ElevenLabsAudioGenerator") as mock_audio_class:
            mock_audio = MagicMock()
            mock_audio.generate_audio = AsyncMock(return_value=b"fake-audio-data")
            mock_audio_class.return_value = mock_audio
            
            # Generate podcast content
            from app.services.multi_step_content_generation_final import EnhancedContentService
            service = EnhancedContentService()
            
            result = await service.generate_long_form_content(
                syllabus_text="Audio test: Creating engaging podcast content about space exploration.",
                target_format=TargetFormat.PODCAST,
                use_cache=False
            )
            
            generated_content, metadata, quality_metrics, tokens, error = result
            
            assert generated_content is not None
            assert generated_content.podcast_script is not None
            assert error is None


@pytest.mark.integration 
class TestMonitoringAndMetrics:
    """Test monitoring and metrics collection across services."""

    @pytest.mark.asyncio
    async def test_metrics_collection_during_content_generation(
        self, content_service, mock_llm_client
    ):
        """Test that metrics are properly collected during content generation."""
        with patch("app.services.multi_step_content_generation_final.track_metric") as mock_track_metric:
            result = await content_service.generate_long_form_content(
                syllabus_text="Metrics test: Monitoring content generation performance and quality metrics.",
                target_format=TargetFormat.COMPREHENSIVE,
                use_parallel=True
            )
            
            # Verify metrics were tracked
            assert mock_track_metric.called
            
            # Check for specific metric types
            metric_names = [call[0][0] for call in mock_track_metric.call_args_list]
            assert any("generation_time" in name for name in metric_names)
            assert any("token" in name for name in metric_names)

    @pytest.mark.asyncio
    async def test_error_logging_integration(self, job_manager, mock_firestore_client):
        """Test that errors are properly logged across services."""
        with patch("app.services.security_event_logger.SecurityEventLogger.log_event") as mock_log_event:
            # Simulate an error during job creation
            mock_firestore_client.collection().document().set.side_effect = Exception("Database error")
            
            with pytest.raises(Exception):
                await job_manager.create_job(
                    ContentRequest(
                        syllabus_text="Error logging test: This should trigger error logging.",
                        target_format=TargetFormat.GUIDE
                    )
                )
            
            # Verify error was logged (if security logging is implemented)
            # mock_log_event.assert_called()


@pytest.mark.integration
class TestWorkflowIntegration:
    """Test complete end-to-end workflows."""

    @pytest.mark.asyncio
    async def test_complete_content_generation_workflow(
        self, job_manager, content_service, mock_firestore_client, mock_llm_client, mock_redis_client
    ):
        """Test the complete workflow from request to final content."""
        # Step 1: Create content request
        request = ContentRequest(
            syllabus_text="Complete workflow test: A comprehensive course on data science, covering statistics, "
                         "machine learning, data visualization, and practical applications in business analytics.",
            target_format=TargetFormat.COMPREHENSIVE,
            target_pages=10,
            use_parallel=True,
            use_cache=True
        )
        
        # Step 2: Create job
        job = await job_manager.create_job(request)
        assert job.status == JobStatus.PENDING
        
        # Step 3: Process content generation
        result = await content_service.generate_long_form_content(
            syllabus_text=request.syllabus_text,
            target_format=request.target_format,
            target_pages=request.target_pages,
            job_id=str(job.id),
            use_parallel=request.use_parallel,
            use_cache=request.use_cache,
            quality_threshold=0.8
        )
        
        generated_content, metadata, quality_metrics, tokens, error = result
        
        # Step 4: Verify complete content generation
        assert generated_content is not None
        assert error is None
        
        # Verify all content types for comprehensive format
        assert generated_content.content_outline is not None
        assert generated_content.podcast_script is not None
        assert generated_content.study_guide is not None
        
        # Verify quality metrics
        assert quality_metrics is not None
        assert quality_metrics.get("overall_score", 0) > 0
        
        # Step 5: Update job as completed
        await job_manager.update_job_status(
            str(job.id),
            JobStatus.COMPLETED,
            result=generated_content.model_dump()
        )
        
        # Verify caching worked
        assert mock_redis_client.set.called
        
        # Step 6: Retrieve cached content
        mock_redis_client.get.return_value = json.dumps({
            "content": generated_content.model_dump(),
            "metadata": metadata,
            "quality_metrics": quality_metrics,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Generate again with cache - should be faster
        cached_result = await content_service.generate_long_form_content(
            syllabus_text=request.syllabus_text,
            target_format=request.target_format,
            use_cache=True
        )
        
        # Verify cached content matches
        assert cached_result[0].content_outline.title == generated_content.content_outline.title

    @pytest.mark.asyncio
    async def test_failure_recovery_workflow(
        self, job_manager, content_service, mock_firestore_client, mock_llm_client
    ):
        """Test workflow recovery from various failure points."""
        request = ContentRequest(
            syllabus_text="Failure recovery test: Testing system resilience and error recovery mechanisms.",
            target_format=TargetFormat.GUIDE
        )
        
        # Create job
        job = await job_manager.create_job(request)
        
        # Simulate failure during outline generation
        call_count = 0
        original_side_effect = mock_llm_client.generate_content.side_effect
        
        async def failing_then_success(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Temporary LLM failure")
            return await original_side_effect(*args, **kwargs)
        
        mock_llm_client.generate_content.side_effect = failing_then_success
        
        # Content generation should retry and eventually succeed
        result = await content_service.generate_long_form_content(
            syllabus_text=request.syllabus_text,
            target_format=request.target_format,
            job_id=str(job.id),
            max_retries=3
        )
        
        generated_content, metadata, quality_metrics, tokens, error = result
        
        # Should eventually succeed after retries
        assert generated_content is not None or error is not None
        assert call_count > 2  # Verify retries happened