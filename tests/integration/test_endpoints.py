"""Integration tests for critical API endpoints."""

import datetime
import os
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.pydantic.job import Job, JobStatus


@pytest.fixture
def client():
    """Test client fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_settings():
    """Mock settings with test API key."""
    with patch("app.api.deps.get_settings") as mock_get_settings:
        mock_settings_instance = MagicMock()
        mock_settings_instance.api_key = "test-key"
        mock_get_settings.return_value = mock_settings_instance
        yield mock_settings_instance


@pytest.fixture
def mock_job_manager():
    """Mock job manager dependency."""
    # Create a mock job manager instance
    mock_manager = MagicMock()
    mock_manager.get_job = AsyncMock()
    mock_manager.create_job = AsyncMock()
    mock_manager.list_jobs = AsyncMock()

    # Override the dependency in the app
    from app.api.routes.jobs import get_job_manager

    app.dependency_overrides[get_job_manager] = lambda: mock_manager

    yield mock_manager

    # Clean up
    app.dependency_overrides.clear()


class TestJobsEndpoint:
    """Test /api/v1/jobs endpoints."""

    def test_create_job_success(self, client, mock_settings, mock_job_manager):
        """Test successful job creation."""
        # Setup mock
        mock_job = Job(
            id=UUID("12345678-1234-5678-1234-567812345678"),
            status=JobStatus.PENDING,
            created_at=datetime.datetime.now(datetime.UTC),
            updated_at=datetime.datetime.now(datetime.UTC),
        )
        mock_job_manager.create_job.return_value = mock_job

        # Make request
        response = client.post(
            "/api/v1/jobs",
            json={
                "syllabus_text": "A" * 200,  # Minimum length
                "target_format": "comprehensive",
            },
            headers={"X-API-Key": "test-key"},
        )

        # Verify
        assert response.status_code == 201  # Created status
        data = response.json()
        assert data["id"] == "12345678-1234-5678-1234-567812345678"
        assert data["status"] == "pending"

    def test_create_job_invalid_syllabus(self, client, mock_settings):
        """Test job creation with invalid syllabus."""
        response = client.post(
            "/api/v1/jobs",
            json={"syllabus_text": "Too short", "target_format": "comprehensive"},
            headers={"X-API-Key": "test-key"},
        )

        assert response.status_code == 422

    def test_get_job_status(self, client, mock_settings, mock_job_manager):
        """Test getting job status."""
        job_id = "12345678-1234-5678-1234-567812345678"

        # Setup mock
        from app.models.pydantic.job import JobProgress

        mock_job = Job(
            id=UUID(job_id),
            status=JobStatus.PROCESSING,
            created_at=datetime.datetime.now(datetime.UTC),
            updated_at=datetime.datetime.now(datetime.UTC),
            progress=JobProgress(
                current_step="Processing content",
                total_steps=5,
                completed_steps=2,
                percentage=50.0,
            ),
        )
        mock_job_manager.get_job.return_value = mock_job

        response = client.get(
            f"/api/v1/jobs/{job_id}", headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["status"] == "processing"


class TestContentEndpoint:
    """Test /api/v1/content endpoints."""

    def test_generate_content_success(self, client, mock_settings):
        """Test successful content generation."""
        # Create mock service instance
        mock_service_instance = MagicMock()

        # Mock response
        from tests.unit.test_app import create_mock_generated_content

        mock_content = create_mock_generated_content()
        mock_service_instance.generate_long_form_content.return_value = (
            mock_content,
            MagicMock(),  # metadata
            MagicMock(),  # quality_metrics
            {"total": 1000},  # tokens
            None,  # no error
        )

        # Override the dependency in the app
        from app.services.multi_step_content_generation_final import (
            get_enhanced_content_service,
        )

        app.dependency_overrides[
            get_enhanced_content_service
        ] = lambda: mock_service_instance

        try:
            # Make request
            response = client.post(
                "/api/v1/content/generate",
                json={"syllabus_text": "A" * 200, "target_format": "comprehensive"},
                headers={"X-API-Key": "test-key"},
            )

            # Verify
            assert response.status_code in [200, 201]  # Can be OK or Created
            data = response.json()
            assert "content_outline" in data
            assert "podcast_script" in data
            assert "study_guide" in data
        finally:
            # Clean up
            app.dependency_overrides.pop(get_enhanced_content_service, None)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns healthy status."""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAuthEndpoint:
    """Test authentication endpoints."""

    def test_missing_api_key(self, client):
        """Test request without API key."""
        # Temporarily set DISABLE_AUTH to ensure auth is enforced
        original_auth = os.environ.get("DISABLE_AUTH")
        os.environ["DISABLE_AUTH"] = "false"

        try:
            response = client.post(
                "/api/v1/content/generate",  # Use content endpoint which requires auth
                json={"syllabus_text": "A" * 200, "target_format": "comprehensive"},
            )
            assert response.status_code in [401, 403]  # Unauthorized or Forbidden
        finally:
            if original_auth is not None:
                os.environ["DISABLE_AUTH"] = original_auth
            else:
                os.environ.pop("DISABLE_AUTH", None)

    def test_invalid_api_key(self, client):
        """Test request with invalid API key."""
        # Temporarily set DISABLE_AUTH to ensure auth is enforced
        original_auth = os.environ.get("DISABLE_AUTH")
        os.environ["DISABLE_AUTH"] = "false"

        try:
            response = client.post(
                "/api/v1/content/generate",  # Use content endpoint which requires auth
                json={"syllabus_text": "A" * 200, "target_format": "comprehensive"},
                headers={"X-API-Key": "invalid-key"},
            )
            assert response.status_code in [401, 403]  # Unauthorized or Forbidden
        finally:
            if original_auth is not None:
                os.environ["DISABLE_AUTH"] = original_auth
            else:
                os.environ.pop("DISABLE_AUTH", None)


class TestErrorHandling:
    """Test error handling across endpoints."""

    def test_404_unknown_endpoint(self, client, mock_settings):
        """Test 404 for unknown endpoints."""
        response = client.get("/api/v1/nonexistent", headers={"X-API-Key": "test-key"})
        assert response.status_code == 404
        assert response.json()["detail"] == "Not Found"

    def test_method_not_allowed(self, client, mock_settings, mock_job_manager):
        """Test 405 for wrong HTTP method."""
        # Mock the list_jobs method
        from app.models.pydantic.job import JobList

        mock_job_manager.list_jobs.return_value = JobList(
            jobs=[], total=0, page=1, page_size=10, total_pages=0
        )

        # Try PUT on jobs endpoint (which doesn't exist)
        response = client.put(
            "/api/v1/jobs", json={"test": "data"}, headers={"X-API-Key": "test-key"}
        )
        assert response.status_code == 405
