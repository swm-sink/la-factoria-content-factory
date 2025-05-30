"""Unit tests for the AI Content Factory FastAPI application."""

import pytest
import os
from unittest.mock import patch, MagicMock, Mock
# from flask import Flask # Removed
from fastapi.testclient import TestClient # Added
from app.main import app # Added: Import FastAPI app instance
from app.models.pydantic.job import JobStatus # For Pydantic models if needed by tests directly

# We don't need to patch vertexai at module level anymore since services are lazy-loaded

@pytest.fixture
def client():
    """Configures the FastAPI test client."""
    # Mock environment variables for testing
    # FastAPI apps typically load .env files automatically or use dependency injection for settings,
    # so direct os.environ patching might be less common or handled differently.
    # For now, we assume settings are loaded correctly by the app itself.
    # If specific test settings are needed, they should be managed via FastAPI's dependency overrides or test-specific settings.
    
    with TestClient(app) as test_client: # Added
        yield test_client # Added

def test_health_check(client):
    """Tests the health check endpoint."""
    response = client.get("/api/v1/health") # Corrected path
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "ok" # Corrected expected status

def test_generate_content_missing_syllabus(client):
    """Tests missing syllabus_text input for /api/v1/generate-content."""
    # This endpoint now uses ContentRequest Pydantic model which includes target_format etc.
    # syllabus_text is mandatory.
    response = client.post("/api/v1/generate-content", json={
        "target_format": "guide" # Provide other fields with defaults or valid values
    })
    assert response.status_code == 422 # FastAPI Pydantic validation error
    response_json = response.json()
    assert "detail" in response_json
    assert any(err["loc"] == ["body", "syllabus_text"] and "Field required" in err["msg"] for err in response_json["detail"])

def test_generate_content_empty_syllabus(client):
    """Tests empty syllabus_text input for /api/v1/generate-content."""
    response = client.post("/api/v1/generate-content", json={"syllabus_text": "", "target_format": "guide"})
    assert response.status_code == 422 # FastAPI Pydantic validation error
    # The actual error message from Pydantic might vary based on validators (e.g. min_length)
    # Assuming syllabus_text has a min_length validator in the Pydantic model, or this test needs adjustment.
    # For now, we'll check that there's an error associated with syllabus_text.
    response_json = response.json()
    assert "detail" in response_json
    assert any(err["loc"] == ["body", "syllabus_text"] for err in response_json["detail"])

def test_generate_content_too_short_syllabus(client):
    """Tests syllabus_text that is too short for /api/v1/generate-content."""
    response = client.post("/api/v1/generate-content", json={"syllabus_text": "Too short", "target_format": "guide"})
    assert response.status_code == 422 # FastAPI Pydantic validation error
    # Similar to above, exact message depends on Pydantic model constraints.
    response_json = response.json()
    assert "detail" in response_json
    assert any(err["loc"] == ["body", "syllabus_text"] for err in response_json["detail"])

def create_mock_service_response_content():
    """Creates a mock dictionary that the content_service.generate_long_form_content might return."""
    return {
        "title": "Mock Title from Service",
        "content": "Mock Content from Service (could be detailed_reading_material or other)",
        "metadata": {"source_syllabus_length": 100, "generated_format": "guide"},
        "quality_metrics": {"clarity_score": 0.95},
        "version_id": "v1.mock",
        # The following are not directly in ContentResponse but might be part of the service's internal full dict
        "content_outline": "Mock content outline",
        "podcast_script": "Mock podcast script",
        "study_guide": "Mock study guide (could be same as 'content' field)",
        "one_pager_summary": "Mock one-pager summary",
        "detailed_reading_material": "Mock detailed reading material (could be same as 'content' field)",
        "faqs": [
            {"question": "Mock question 1", "answer": "Mock answer 1"},
            {"question": "Mock question 2", "answer": "Mock answer 2"}
        ],
        "flashcards": [
            {"term": "Mock term 1", "definition": "Mock definition 1"},
            {"term": "Mock term 2", "definition": "Mock definition 2"}
        ],
        "reading_guide_questions": [
            "Mock question 1?",
            "Mock question 2?"
        ]
    }

@patch("app.api.routes.content.content_service") # Corrected mock target
def test_generate_content_success(mock_content_service_instance, client):
    """Tests successful content generation via /api/v1/generate-content."""
    mock_service_data = create_mock_service_response_content()
    # Mocking the return value of the service method called by the route
    # The route expects: content_dict, status_code, job_id (job_id might be None for sync path)
    mock_content_service_instance.generate_long_form_content.return_value = (mock_service_data, 200, "mock_job_id_123")
    
    response = client.post(
        "/api/v1/generate-content", # Corrected path
        json={ # Payload for ContentRequest
            "syllabus_text": "A sample syllabus text for testing purposes, long enough to pass validation. " * 3,
            "target_format": "guide", # Default, but explicit
            "use_parallel": False,
            "use_cache": True
        },
    )

    assert response.status_code == 200
    json_data = response.json() # This should match ContentResponse model
    
    # Verify fields from ContentResponse
    assert json_data["title"] == mock_service_data["title"]
    assert json_data["content"] == mock_service_data["content"]
    assert json_data["metadata"] == mock_service_data["metadata"]
    assert json_data["quality_metrics"] == mock_service_data["quality_metrics"]
    assert json_data["version_id"] == mock_service_data["version_id"]
    
    # Check if the mock service method was called correctly
    mock_content_service_instance.generate_long_form_content.assert_called_once_with(
        "A sample syllabus text for testing purposes, long enough to pass validation. " * 3,
        "guide",
        use_parallel=False,
        use_cache=True
        # target_duration and target_pages are not passed if not in JSON, service should use defaults
    )
    
@patch("app.api.routes.content.content_service") # Corrected mock target
def test_generate_content_service_error(mock_content_service_instance, client):
    """Tests error handling when service raises an exception for /api/v1/generate-content."""
    # Simulate the service method raising an exception
    mock_content_service_instance.generate_long_form_content.side_effect = Exception("Simulated internal service error")
    
    response = client.post(
        "/api/v1/generate-content", # Corrected path
        json={ # Payload for ContentRequest
            "syllabus_text": "A sample syllabus text for testing. " * 3,
            "target_format": "podcast"
        },
    )

    # The route's exception handler should catch this and return a 500
    assert response.status_code == 500
    json_data = response.json()
    assert "detail" in json_data
    assert "Simulated internal service error" in json_data["detail"] or "Internal Server Error" in json_data["detail"] # FastAPI might mask original error

# The following tests for /api/v1/content/generate are adapted from old /api/generate-long-form-content tests
# They primarily test Pydantic model validation for ContentRequest

def test_content_request_validation_missing_syllabus(client): # Renamed for clarity
    """Tests missing syllabus_text for ContentRequest validation at /api/v1/generate-content."""
    response = client.post("/api/v1/generate-content", json={"target_format": "guide"}) # syllabus_text is missing
    assert response.status_code == 422 # FastAPI Pydantic validation error
    response_json = response.json()
    assert "detail" in response_json
    assert any(err["loc"] == ["body", "syllabus_text"] and "Field required" in err["msg"] for err in response_json["detail"])

def test_content_request_validation_invalid_target_format(client): # Renamed for clarity
    """Tests invalid target_format for ContentRequest validation at /api/v1/generate-content."""
    response = client.post("/api/v1/generate-content", json={
        "syllabus_text": "A sample syllabus text for testing purposes, long enough. " * 3,
        "target_format": "invalid_format_value" # This should fail if target_format has an Enum or Literal constraint
    })
    assert response.status_code == 422 # FastAPI Pydantic validation error
    response_json = response.json()
    assert "detail" in response_json
    # Assuming target_format is constrained by an Enum in Pydantic model.
    # The error message for Enum validation looks like: "Input should be 'enum_value1' or 'enum_value2'"
    assert any(
        err["loc"] == ["body", "target_format"] and 
        ("Input should be" in err["msg"] or "unexpected value" in err["msg"]) # Pydantic v2 error messages vary
        for err in response_json["detail"]
    )

# TODO: Reinstate or adapt the following tests if/when these endpoints are implemented in FastAPI
# def test_supported_formats(client):
#     """Tests the supported formats endpoint."""
#     response = client.get("/api/v1/content/formats") # Corrected path
#     assert response.status_code == 200
#     json_data = response.json()
#     assert "supported_formats" in json_data
#     assert "podcast" in json_data["supported_formats"]
#     assert "guide" in json_data["supported_formats"]
#     assert "one_pager" in json_data["supported_formats"]

# @patch("app.api.routes.content.content_service") # Corrected mock target
# def test_cache_stats(mock_content_service_instance, client):
#     """Tests the cache statistics endpoint."""
#     mock_content_service_instance.get_cache_stats.return_value = { # Assuming service has this method
#         "total_entries": 0,
#         "cache_utilization": 0,
#         "hit_rate": 0.0,
#         "miss_rate": 1.0
#     }
#     response = client.get("/api/v1/content/cache/stats") # Corrected path
#     assert response.status_code == 200
#     json_data = response.json()
#     assert "total_entries" in json_data

# @patch("app.api.routes.content.content_service") # Corrected mock target
# def test_system_stats(mock_content_service_instance, client):
#     """Tests the system statistics endpoint."""
#     mock_content_service_instance.get_cache_stats.return_value = {"total_entries": 0}
#     # Assuming progress_tracker might be part of the service or another component
#     # For now, let's assume it's not directly on content_service for this test if not present
#     # mock_content_service_instance.progress_tracker.get_stats.return_value = {"total_jobs": 0} 
    
#     # This test would need more info on how system stats are gathered in FastAPI version
#     response = client.get("/api/v1/system/stats") # Corrected path
#     assert response.status_code == 200 # Or 404 if not implemented
#     # json_data = response.json()
#     # assert "cache" in json_data
#     # assert "progress_tracker" in json_data # If applicable
#     # assert "system_status" in json_data 
#     pytest.skip("System stats endpoint not confirmed in FastAPI version or its structure is unknown.")
 