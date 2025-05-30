import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import uuid

# We need to import the FastAPI app instance from app.main
from app.main import app
from app.services.multi_step_content_generation import EnhancedMultiStepContentGenerationService
from app.core.config.settings import Settings
from app.core.schemas.job import Job, JobStatus
from app.models.pydantic.content import ContentRequest
# from app.services.job_manager import JobManager # We will mock this

# Create a TestClient for the FastAPI app
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def mock_app_settings(): # Renamed to avoid conflict if settings are imported elsewhere
    with patch('app.main.get_settings') as mock_get_main_settings, \
         patch('app.services.job_manager.get_settings') as mock_get_job_manager_settings, \
         patch('app.api.routes.jobs.get_settings', create=True) as mock_get_jobs_route_settings: # If jobs route uses its own get_settings
        
        mock_settings_instance = MagicMock(spec=Settings)
        mock_settings_instance.api_key = "test-api-key"
        # Add other relevant settings if needed by dependencies of the /jobs endpoint
        mock_settings_instance.gcp_project_id = "test-gcp-project"
        mock_settings_instance.some_other_setting = "test_value"

        if mock_get_main_settings:
            mock_get_main_settings.return_value = mock_settings_instance
        if mock_get_job_manager_settings:
            mock_get_job_manager_settings.return_value = mock_settings_instance
        if mock_get_jobs_route_settings:
            mock_get_jobs_route_settings.return_value = mock_settings_instance
        yield mock_settings_instance

@pytest.fixture
def mock_job_manager():
    with patch('app.api.routes.jobs.get_job_manager') as mock_get_manager:
        mock_manager_instance = MagicMock() # spec=JobManager if JobManager is importable
        
        async def mock_create_job(content_request: ContentRequest):
            # Simulate JobManager.create_job behavior
            job_id = uuid.uuid4()
            # Return a mock Job object that matches the Pydantic model structure
            mock_job_data = {
                "id": job_id,
                "status": JobStatus.PENDING,
                "created_at": "2024-07-30T10:00:00Z", # Use a fixed ISO string or datetime object
                "updated_at": "2024-07-30T10:00:00Z",
                "completed_at": None,
                "error": None,
                "progress": None,
                "result": None,
                "metadata": content_request.model_dump() # Store the input request as metadata
            }
            return Job(**mock_job_data) # Use the actual Pydantic model for construction

        mock_manager_instance.create_job = MagicMock(side_effect=mock_create_job)
        mock_get_manager.return_value = mock_manager_instance
        yield mock_manager_instance

def test_create_job_success(mock_job_manager, mock_app_settings):
    """Tests POST /api/v1/jobs for successful job creation."""
    payload = {
        "syllabus_text": "Integration test syllabus: The future of AI.",
        "target_format": "study_guide", # Example, ensure it's a valid format
        "target_duration": 20.0,
        "target_pages": 5,
        "use_parallel": True,
        "use_cache": False
    }
    headers = {"X-API-Key": "test-api-key"}

    response = client.post("/api/v1/jobs", json=payload, headers=headers)

    assert response.status_code == 201
    response_data = response.json()
    
    assert "id" in response_data
    assert response_data["status"] == "pending"
    assert response_data["metadata"]["syllabus_text"] == payload["syllabus_text"]
    assert response_data["metadata"]["target_format"] == payload["target_format"]

    # Verify JobManager.create_job was called correctly
    # The mock_job_manager.create_job is already a MagicMock due to the fixture setup
    assert mock_job_manager.create_job.call_count == 1
    called_with_payload = mock_job_manager.create_job.call_args[0][0]
    assert isinstance(called_with_payload, ContentRequest)
    assert called_with_payload.syllabus_text == payload["syllabus_text"]
    assert called_with_payload.target_format == payload["target_format"]

def test_create_job_invalid_api_key(mock_app_settings): # mock_job_manager not strictly needed if auth fails before
    """Tests POST /api/v1/jobs with an invalid API key."""
    payload = {
        "syllabus_text": "Test syllabus.",
        "target_format": "guide"
    }
    headers = {"X-API-Key": "wrong-api-key"}
    response = client.post("/api/v1/jobs", json=payload, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key."}

def test_create_job_missing_api_key(mock_app_settings):
    """Tests POST /api/v1/jobs with a missing API key."""
    payload = {
        "syllabus_text": "Test syllabus.",
        "target_format": "guide"
    }
    response = client.post("/api/v1/jobs", json=payload) # No headers
    assert response.status_code == 401 
    assert response.json() == {"detail": "Invalid or missing API key."}

def test_create_job_validation_error(mock_app_settings):
    """Tests POST /api/v1/jobs with invalid payload (missing required field)."""
    payload = {
        # "syllabus_text": "Missing syllabus text.", # syllabus_text is required
        "target_format": "guide"
    }
    headers = {"X-API-Key": "test-api-key"}
    response = client.post("/api/v1/jobs", json=payload, headers=headers)
    assert response.status_code == 422 # FastAPI's default for Pydantic validation errors
    response_data = response.json()
    assert "detail" in response_data
    assert any(err["type"] == "missing" and "syllabus_text" in err["loc"] for err in response_data["detail"])

# TODO: Add tests for GET /api/v1/jobs/{job_id} and GET /api/v1/jobs (list jobs)
# These would also mock JobManager methods (get_job, list_jobs).

# Mock the content generation service
@pytest.fixture(autouse=True)
def mock_content_service():
    with patch('app.main.EnhancedMultiStepContentGenerationService') as MockService:
        mock_instance = MockService.return_value
        # Configure default successful response
        mock_instance.generate_long_form_content.return_value = (
            {
                "title": "Generated Title",
                "content": "Generated content goes here.",
                "metadata": {"format": "guide", "source": "test"},
                "quality_metrics": {"overall_score": 0.95},
                "version_id": "abc-123"
            },
            200,
            "test-job-id"
        )
        yield mock_instance

def test_generate_content_success(mock_content_service):
    """Tests the /api/generate-content endpoint success case."""
    # Define request payload
    payload = {
        "syllabus_text": "Sample syllabus for testing the API.",
        "target_format": "guide",
        "target_duration": 30.5,
        "target_pages": 10,
        "use_parallel": False,
        "use_cache": True
    }

    # Make a POST request to the endpoint with API key header
    headers = {
        "X-API-Key": "test-api-key"
    }
    response = client.post("/api/generate-content", json=payload, headers=headers)

    # Assertions
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['title'] == "Generated Title"
    assert response_data['content'] == "Generated content goes here."
    assert "metadata" in response_data
    assert "quality_metrics" in response_data
    assert "version_id" in response_data

    # Verify the service method was called correctly
    mock_content_service.generate_long_form_content.assert_called_once_with(
        payload['syllabus_text'],
        payload['target_format'],
        target_duration=payload['target_duration'],
        target_pages=payload['target_pages'],
        use_parallel=payload['use_parallel'],
        use_cache=payload['use_cache']
    )

def test_generate_content_invalid_api_key():
    """Tests the /api/generate-content endpoint with an invalid API key."""
    payload = {
        "syllabus_text": "Sample syllabus.",
        "target_format": "guide"
    }
    headers = {
        "X-API-Key": "wrong-key"
    }
    response = client.post("/api/generate-content", json=payload, headers=headers)

    # Assertions
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key."}

def test_generate_content_missing_api_key():
    """Tests the /api/generate-content endpoint with a missing API key."""
    payload = {
        "syllabus_text": "Sample syllabus.",
        "target_format": "guide"
    }
    headers = {
        "X-API-Key": "wrong-key"
    }
    response = client.post("/api/generate-content", json=payload, headers=headers)

    # Assertions
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key."} 