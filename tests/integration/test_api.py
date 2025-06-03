import os
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.config.settings import Settings

# We need to import the FastAPI app instance from app.main
from app.main import app
from app.models.pydantic.content import (
    ContentOutline,
    ContentRequest,
    GeneratedContent,
    OutlineSection,
)
from app.models.pydantic.job import Job, JobStatus


# Create fixtures for mocking external services
@pytest.fixture(scope="module")
def mock_firestore():
    """Mock Firestore client to prevent real database connections"""
    with patch(
        "app.services.job.firestore_client.get_firestore_client"
    ) as mock_get_client:
        mock_client = MagicMock()

        # Mock the collection and document methods
        mock_collection = MagicMock()
        mock_document = MagicMock()
        mock_client.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document

        # Mock the async set method
        async def mock_set(data, merge=True):
            return True

        mock_document.set = AsyncMock(side_effect=mock_set)

        # Mock the async update method
        async def mock_update(data):
            return True

        mock_document.update = AsyncMock(side_effect=mock_update)

        # Mock the async get method
        async def mock_get():
            mock_snapshot = MagicMock()
            mock_snapshot.exists = True
            mock_snapshot.to_dict.return_value = {
                "id": str(uuid.uuid4()),
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            return mock_snapshot

        mock_document.get = AsyncMock(side_effect=mock_get)

        mock_get_client.return_value = mock_client
        yield mock_client


@pytest.fixture(scope="module")
def mock_redis():
    """Mock Redis client to prevent real Redis connections"""
    with patch("app.services.content_cache.redis.Redis") as mock_redis_class:
        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.return_value = None
        mock_redis_instance.set.return_value = True
        mock_redis_instance.expire.return_value = True
        mock_redis_class.return_value = mock_redis_instance
        yield mock_redis_instance


@pytest.fixture(scope="module")
def mock_cloud_tasks():
    """Mock Cloud Tasks client"""
    with patch("app.services.job.tasks_client.CloudTasksClient") as mock_tasks_class:
        mock_tasks_instance = MagicMock()
        # Make the enqueue method async
        mock_tasks_instance.enqueue_content_generation_job = AsyncMock(
            return_value=True
        )
        mock_tasks_class.return_value = mock_tasks_instance
        yield mock_tasks_instance


@pytest.fixture(scope="module", autouse=True)
def mock_app_settings():
    """Mock application settings"""
    with patch("app.main.get_settings") as mock_get_main_settings, patch(
        "app.services.job_manager.get_settings"
    ) as mock_get_job_manager_settings, patch(
        "app.api.deps.get_settings"
    ) as mock_get_deps_settings, patch(
        "app.api.routes.jobs.get_settings", create=True
    ) as mock_get_jobs_route_settings, patch(
        "app.api.routes.content.get_settings", create=True
    ) as mock_get_content_route_settings, patch(
        "app.core.config.settings.get_settings"
    ) as mock_get_core_settings, patch(
        "app.services.job.tasks_client.get_settings"
    ) as mock_get_tasks_client_settings:
        mock_settings_instance = MagicMock(spec=Settings)
        mock_settings_instance.api_key = "test-api-key"
        mock_settings_instance.gcp_project_id = "test-gcp-project"
        mock_settings_instance.gcp_location = "us-central1"
        mock_settings_instance.jwt_secret_key = "test-jwt-secret"
        mock_settings_instance.jwt_algorithm = "HS256"
        mock_settings_instance.redis_host = "localhost"
        mock_settings_instance.redis_port = 6379
        mock_settings_instance.redis_db = 0
        mock_settings_instance.redis_password = None
        mock_settings_instance.tasks_queue_name = "content-generation"
        mock_settings_instance.tasks_worker_service_url = os.getenv(
            "TEST_WORKER_SERVICE_URL", "https://test-worker.example.com"
        )

        # Apply settings to all locations
        for mock in [
            mock_get_main_settings,
            mock_get_job_manager_settings,
            mock_get_deps_settings,
            mock_get_jobs_route_settings,
            mock_get_content_route_settings,
            mock_get_core_settings,
            mock_get_tasks_client_settings,
        ]:
            if mock:
                mock.return_value = mock_settings_instance

        yield mock_settings_instance


@pytest.fixture(scope="module")
def client(mock_app_settings, mock_firestore, mock_redis, mock_cloud_tasks):
    """Create test client with all mocks applied"""
    return TestClient(app)


@pytest.fixture
def mock_job_manager(mock_firestore):
    """Mock JobManager for job-related tests"""
    with patch("app.api.routes.jobs.get_job_manager") as mock_get_manager:
        mock_manager_instance = MagicMock()

        async def mock_create_job(content_request: ContentRequest):
            job_id = uuid.uuid4()
            mock_job_data = {
                "id": job_id,
                "status": JobStatus.PENDING,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "completed_at": None,
                "error": None,
                "progress": {
                    "current_step": "Job created",
                    "total_steps": 7,
                    "completed_steps": 1,
                    "percentage": 10.0,
                },
                "result": None,
                "metadata": content_request.model_dump(),
            }
            return Job(**mock_job_data)

        mock_manager_instance.create_job = AsyncMock(side_effect=mock_create_job)
        mock_get_manager.return_value = mock_manager_instance
        yield mock_manager_instance


@pytest.fixture
def mock_content_service():
    """Mock content generation service"""
    with patch(
        "app.api.routes.content.get_enhanced_content_service"
    ) as mock_get_service:
        mock_service_instance = MagicMock()

        # Create a proper ContentOutline instance first
        mock_outline = ContentOutline(
            title="Generated Title",
            overview="This is a comprehensive overview of the content that provides detailed information about the topic and meets the minimum character requirement for validation",
            learning_objectives=[
                "Learn objective 1",
                "Learn objective 2",
                "Learn objective 3",
            ],
            sections=[
                OutlineSection(
                    section_number=1,
                    title="Introduction Section",
                    description="This section introduces the main concepts of the topic",
                    key_points=[
                        "Key point 1 for introduction",
                        "Key point 2 for introduction",
                    ],
                ),
                OutlineSection(
                    section_number=2,
                    title="Main Content Section",
                    description="This section covers the core material and main learning points",
                    key_points=["Main key point 1", "Main key point 2"],
                ),
                OutlineSection(
                    section_number=3,
                    title="Conclusion Section",
                    description="This section summarizes the key learnings and provides next steps",
                    key_points=["Summary point 1", "Summary point 2"],
                ),
            ],
        )

        # Create a proper GeneratedContent instance with the outline
        mock_generated_content = GeneratedContent(content_outline=mock_outline)

        async def mock_generate():
            return (
                mock_generated_content,
                {"tokens_used": 1000},  # metadata
                {"overall_score": 0.95},  # quality_metrics
                1000,  # tokens
                None,  # error
            )

        mock_service_instance.generate_long_form_content = AsyncMock(
            side_effect=mock_generate
        )
        mock_get_service.return_value = mock_service_instance
        yield mock_service_instance


@pytest.fixture
def mock_integration_settings():
    """Settings for integration tests with configurable external URLs"""
    return MagicMock(
        api_key="test-integration-api-key",
        jwt_secret_key="test-integration-jwt-secret-32-chars-min",
        gcp_project_id="test-integration-project",
        tasks_worker_service_url=os.getenv(
            "TEST_WORKER_SERVICE_URL", "https://test-worker.example.com"
        ),
        cors_origins=["http://localhost:3000", "http://localhost:5173"],
    )


# Test cases


def test_create_job_success(client, mock_job_manager):
    """Tests POST /api/v1/jobs for successful job creation."""
    payload = {
        "syllabus_text": "Integration test syllabus: The future of AI and its impact on education. This is a comprehensive overview of AI applications.",
        "target_format": "guide",
        "target_duration": 20.0,
        "target_pages": 5,
        "use_parallel": True,
        "use_cache": False,
    }
    headers = {"X-API-Key": "test-api-key"}

    response = client.post("/api/v1/jobs", json=payload, headers=headers)

    assert response.status_code == 201
    response_data = response.json()

    assert "id" in response_data
    assert response_data["status"] == "pending"
    assert response_data["metadata"]["syllabus_text"] == payload["syllabus_text"]
    assert response_data["metadata"]["target_format"] == payload["target_format"]

    # Ensure the job ID is a valid UUID
    try:
        uuid.UUID(str(response_data["id"]))
    except ValueError:
        pytest.fail(f"Invalid UUID format for job ID: {response_data['id']}")

    # Verify JobManager.create_job was called correctly
    assert mock_job_manager.create_job.call_count == 1
    called_with_payload = mock_job_manager.create_job.call_args[0][0]
    assert isinstance(called_with_payload, ContentRequest)
    assert called_with_payload.syllabus_text == payload["syllabus_text"]
    assert called_with_payload.target_format == payload["target_format"]


def test_create_job_invalid_api_key(client):
    """Tests POST /api/v1/jobs with an invalid API key."""
    payload = {
        "syllabus_text": "Test syllabus for authentication testing with sufficient length to pass validation requirements.",
        "target_format": "guide",
    }
    headers = {"X-API-Key": "wrong-api-key"}
    response = client.post("/api/v1/jobs", json=payload, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key."}


def test_create_job_missing_api_key(client):
    """Tests POST /api/v1/jobs with a missing API key."""
    payload = {
        "syllabus_text": "Test syllabus for missing API key validation test with sufficient length.",
        "target_format": "guide",
    }
    response = client.post("/api/v1/jobs", json=payload)  # No headers
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key."}


def test_create_job_validation_error(client):
    """Tests POST /api/v1/jobs with invalid payload (missing required field)."""
    payload = {
        # "syllabus_text": "Missing syllabus text.", # syllabus_text is required
        "target_format": "guide"
    }
    headers = {"X-API-Key": "test-api-key"}
    response = client.post("/api/v1/jobs", json=payload, headers=headers)
    assert (
        response.status_code == 422
    )  # FastAPI's default for Pydantic validation errors
    response_data = response.json()
    assert "details" in response_data or "detail" in response_data
    details = response_data.get("details", response_data.get("detail", []))
    if isinstance(details, list):
        assert any("syllabus_text" in str(err) for err in details)
    else:
        assert "syllabus_text" in str(details)


def test_generate_content_success(client, mock_content_service):
    """Tests the /api/v1/content/generate endpoint success case."""
    payload = {
        "syllabus_text": "Sample syllabus for testing the API with comprehensive content generation and validation.",
        "target_format": "guide",
        "quality_threshold": 0.8,
        "use_parallel": False,
        "use_cache": True,
    }

    headers = {"X-API-Key": "test-api-key"}
    response = client.post("/api/v1/content/generate", json=payload, headers=headers)

    assert response.status_code == 200
    response_data = response.json()
    assert "content_outline" in response_data
    assert response_data["content_outline"]["title"] == "Generated Title"
    assert "metadata" in response_data
    assert "quality_metrics" in response_data
    assert "version_id" in response_data

    # Verify the service method was called correctly
    mock_content_service.generate_long_form_content.assert_called_once()
    call_kwargs = mock_content_service.generate_long_form_content.call_args[1]
    assert call_kwargs["syllabus_text"] == payload["syllabus_text"]
    assert call_kwargs["target_format"] == payload["target_format"]
    assert call_kwargs["use_parallel"] == payload["use_parallel"]
    assert call_kwargs["use_cache"] == payload["use_cache"]
    assert "job_id" in call_kwargs
    assert call_kwargs["quality_threshold"] == payload["quality_threshold"]


def test_generate_content_invalid_api_key(client):
    """Tests the /api/v1/content/generate endpoint with an invalid API key."""
    payload = {"syllabus_text": "Sample syllabus.", "target_format": "guide"}
    headers = {"X-API-Key": "wrong-key"}
    response = client.post("/api/v1/content/generate", json=payload, headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key."}


def test_generate_content_missing_api_key(client):
    """Tests the /api/v1/content/generate endpoint with a missing API key."""
    payload = {"syllabus_text": "Sample syllabus.", "target_format": "guide"}
    # No headers - missing API key
    response = client.post("/api/v1/content/generate", json=payload, headers={})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key."}


# TODO: Add tests for GET /api/v1/jobs/{job_id} and GET /api/v1/jobs (list jobs)
