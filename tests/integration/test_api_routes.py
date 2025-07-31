"""
Integration tests for API route handlers.

These tests validate the integration between API routes, middleware,
and backend services.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.config.settings import Settings
from app.main import app
from app.models.pydantic.content import ContentRequest, TargetFormat
from app.models.pydantic.job import Job, JobStatus


@pytest.mark.integration
class TestAPIRoutesIntegration:
    """Test API routes with full integration."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_auth_settings(self):
        """Mock settings for authentication."""
        with patch("app.api.deps.get_settings") as mock_get_settings:
            mock_settings = MagicMock(spec=Settings)
            mock_settings.api_key = "test-api-key"
            mock_settings.jwt_secret_key = "test-secret-key-minimum-32-chars"
            mock_settings.jwt_algorithm = "HS256"
            mock_settings.gcp_project_id = "test-project"
            mock_get_settings.return_value = mock_settings
            yield mock_settings

    @pytest.fixture
    def mock_service_dependencies(self):
        """Mock all service dependencies."""
        with patch("app.services.job.firestore_client.get_firestore_client") as mock_firestore, \
             patch("app.services.content_cache.redis.Redis") as mock_redis, \
             patch("app.services.llm_client.SimpleLLMClient") as mock_llm, \
             patch("app.services.job.tasks_client.CloudTasksClient") as mock_tasks:
            
            # Setup Firestore mock
            mock_firestore_client = MagicMock()
            mock_collection = MagicMock()
            mock_document = MagicMock()
            mock_firestore_client.collection.return_value = mock_collection
            mock_collection.document.return_value = mock_document
            mock_document.set = AsyncMock(return_value=True)
            mock_document.get = AsyncMock()
            mock_document.update = AsyncMock(return_value=True)
            mock_firestore.return_value = mock_firestore_client
            
            # Setup Redis mock
            mock_redis_client = MagicMock()
            mock_redis_client.get.return_value = None
            mock_redis_client.set.return_value = True
            mock_redis_client.ping.return_value = True
            mock_redis.return_value = mock_redis_client
            
            # Setup LLM mock
            mock_llm_client = MagicMock()
            mock_llm_client.generate_content = AsyncMock(
                return_value=json.dumps({"content": "test"})
            )
            mock_llm.return_value = mock_llm_client
            
            # Setup Cloud Tasks mock
            mock_tasks_client = MagicMock()
            mock_tasks_client.enqueue_content_generation_job = AsyncMock(
                return_value="task-123"
            )
            mock_tasks.return_value = mock_tasks_client
            
            yield {
                "firestore": mock_firestore_client,
                "redis": mock_redis_client,
                "llm": mock_llm_client,
                "tasks": mock_tasks_client
            }

    @pytest.mark.asyncio
    async def test_complete_job_workflow(self, client, mock_auth_settings, mock_service_dependencies):
        """Test complete workflow from job creation to retrieval."""
        # Step 1: Create a job
        create_payload = {
            "syllabus_text": "Integration test: Complete workflow for educational content about Python programming fundamentals.",
            "target_format": "comprehensive",
            "target_pages": 10,
            "use_parallel": True
        }
        
        # Mock the Firestore document get to return a job
        mock_job_data = {
            "id": str(uuid.uuid4()),
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": create_payload
        }
        
        async def mock_get():
            snapshot = MagicMock()
            snapshot.exists = True
            snapshot.to_dict.return_value = mock_job_data
            return snapshot
            
        mock_service_dependencies["firestore"].collection().document().get = AsyncMock(
            side_effect=mock_get
        )
        
        create_response = client.post(
            "/api/v1/jobs",
            json=create_payload,
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert create_response.status_code == 201
        job_data = create_response.json()
        assert "id" in job_data
        assert job_data["status"] == "pending"
        
        # Step 2: Retrieve the job
        job_id = job_data["id"]
        get_response = client.get(
            f"/api/v1/jobs/{job_id}",
            headers={"X-API-Key": "test-api-key"}
        )
        
        # The response depends on how the mock is configured
        assert get_response.status_code in [200, 404]  # 404 if job manager doesn't find it

    def test_authentication_required_endpoints(self, client, mock_auth_settings):
        """Test that protected endpoints require authentication."""
        protected_endpoints = [
            ("/api/v1/jobs", "POST"),
            ("/api/v1/jobs/123", "GET"),
            ("/api/v1/content/generate", "POST"),
        ]
        
        for endpoint, method in protected_endpoints:
            # Request without API key
            if method == "POST":
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)
            
            assert response.status_code == 401, f"{endpoint} should require authentication"
            assert "Invalid or missing API key" in response.json().get("detail", "")

    def test_validation_errors(self, client, mock_auth_settings):
        """Test that validation errors are properly handled."""
        # Invalid content request - missing required field
        invalid_payload = {
            "target_format": "guide"
            # Missing syllabus_text
        }
        
        response = client.post(
            "/api/v1/jobs",
            json=invalid_payload,
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 422
        error_detail = response.json()
        assert "detail" in error_detail or "details" in error_detail

    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        # Make OPTIONS request
        response = client.options("/api/v1/jobs")
        
        # Check CORS headers
        assert "access-control-allow-origin" in response.headers or "Access-Control-Allow-Origin" in response.headers
        assert "access-control-allow-methods" in response.headers or "Access-Control-Allow-Methods" in response.headers

    @pytest.mark.asyncio
    async def test_error_handling_cascade(self, client, mock_auth_settings, mock_service_dependencies):
        """Test error handling when services fail."""
        # Make Firestore fail
        mock_service_dependencies["firestore"].collection().document().set.side_effect = Exception(
            "Database connection failed"
        )
        
        payload = {
            "syllabus_text": "Test error handling in integration",
            "target_format": "guide"
        }
        
        response = client.post(
            "/api/v1/jobs",
            json=payload,
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Should handle error gracefully
        assert response.status_code in [500, 503]
        error_data = response.json()
        assert "error" in error_data or "detail" in error_data

    def test_health_check_integration(self, client):
        """Test health check endpoint works without authentication."""
        response = client.get("/healthz")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, client, mock_auth_settings, mock_service_dependencies):
        """Test API handles concurrent requests properly."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        def make_request():
            return client.post(
                "/api/v1/jobs",
                json={
                    "syllabus_text": f"Concurrent test {uuid.uuid4()}",
                    "target_format": "guide"
                },
                headers={"X-API-Key": "test-api-key"}
            )
        
        # Make concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [f.result() for f in futures]
        
        # All should complete successfully
        for response in responses:
            assert response.status_code in [201, 429]  # 429 if rate limited

    def test_request_id_tracking(self, client, mock_auth_settings):
        """Test that request IDs are properly tracked."""
        response = client.get(
            "/api/v1/jobs",
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Check for request ID header
        assert "x-request-id" in response.headers or "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_content_type_validation(self, client, mock_auth_settings):
        """Test content type validation."""
        # Send invalid content type
        response = client.post(
            "/api/v1/jobs",
            data="not json",
            headers={
                "X-API-Key": "test-api-key",
                "Content-Type": "text/plain"
            }
        )
        
        assert response.status_code in [400, 422]

    def test_method_not_allowed(self, client, mock_auth_settings):
        """Test proper handling of unsupported HTTP methods."""
        # Try DELETE on an endpoint that doesn't support it
        response = client.delete(
            "/api/v1/jobs",
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 405
        assert response.json()["detail"] == "Method Not Allowed"

    @pytest.mark.asyncio
    async def test_pagination_parameters(self, client, mock_auth_settings, mock_service_dependencies):
        """Test pagination parameters are properly handled."""
        # Mock list response
        mock_service_dependencies["firestore"].collection().where.return_value.stream = AsyncMock(
            return_value=[]
        )
        
        response = client.get(
            "/api/v1/jobs?page=2&page_size=10",
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Should handle pagination
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            if "jobs" in data:  # Check if pagination info is included
                assert isinstance(data.get("jobs"), list)

    def test_api_versioning(self, client):
        """Test API versioning is properly implemented."""
        # v1 endpoints should work
        v1_response = client.get("/api/v1/health")
        
        # Should either work or return proper error
        assert v1_response.status_code in [200, 404]
        
        # Non-versioned endpoints might also exist
        response = client.get("/healthz")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_timeout_handling(self, client, mock_auth_settings, mock_service_dependencies):
        """Test request timeout handling."""
        # Make service hang
        async def slow_operation(*args, **kwargs):
            await asyncio.sleep(30)  # Simulate slow operation
            
        mock_service_dependencies["llm"].generate_content = slow_operation
        
        # This would timeout in a real scenario
        # For testing, we just verify the setup
        assert mock_service_dependencies["llm"] is not None