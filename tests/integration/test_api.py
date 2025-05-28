import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# We need to import the FastAPI app instance from app.main
from app.main import app
from app.services.multi_step_content_generation import EnhancedMultiStepContentGenerationService
from app.core.config.settings import Settings

# Create a TestClient for the FastAPI app
client = TestClient(app)

# Mock settings to provide a predictable API key
@pytest.fixture(scope="module", autouse=True)
def mock_settings():
    with patch('app.main.get_settings') as mock_get_settings:
        mock_settings_instance = MagicMock(spec=Settings)
        mock_settings_instance.api_key = "test-api-key"
        # Also mock other settings needed by the service if any are accessed during API call setup
        # For now, assuming only api_key is directly accessed in the endpoint dependencies

        # Ensure other settings used by the service are also mocked if necessary
        # This might require a more comprehensive mock depending on service initialization
        mock_settings_instance.gcp_project_id = "test-project"
        mock_settings_instance.gcp_location = "test-location"
        mock_settings_instance.gemini_model_name = "test-model"
        mock_settings_instance.elevenlabs_api_key = "test-key"
        mock_settings_instance.max_tokens_per_content_type = {}
        mock_settings_instance.max_total_tokens = 10000
        mock_settings_instance.max_generation_time = 90
        mock_settings_instance.max_retries = 3
        mock_settings_instance.retry_delay = 2

        mock_get_settings.return_value = mock_settings_instance
        yield mock_settings_instance

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