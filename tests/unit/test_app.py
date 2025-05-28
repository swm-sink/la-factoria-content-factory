"""Unit tests for the AI Content Factory Flask application."""

import pytest
import os
from unittest.mock import patch, MagicMock, Mock
from flask import Flask

# We don't need to patch vertexai at module level anymore since services are lazy-loaded

@pytest.fixture
def client():
    """Configures the Flask test client."""
    # Mock environment variables for testing
    with patch.dict(os.environ, {
        'GCP_PROJECT_ID': 'test-project',
        'ELEVENLABS_API_KEY': 'test-api-key'
    }):
        from app.main import create_app
        app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Tests the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"

def test_generate_content_missing_syllabus(client):
    """Tests missing syllabus_text input."""
    response = client.post("/api/generate-content", json={})
    assert response.status_code == 400
    assert "Missing syllabus_text in request" in response.get_json()["error"]

def test_generate_content_empty_syllabus(client):
    """Tests empty syllabus_text input."""
    response = client.post("/api/generate-content", json={"syllabus_text": ""})
    assert response.status_code == 400
    assert "syllabus_text must be a string between 50 and 5000 characters" in response.get_json()["error"]

def test_generate_content_too_short_syllabus(client):
    """Tests syllabus_text that is too short."""
    response = client.post("/api/generate-content", json={"syllabus_text": "Too short"})
    assert response.status_code == 400
    assert (
        "syllabus_text must be a string between 50 and 5000 characters"
        in response.get_json()["error"]
    )

def create_mock_content_response():
    """Creates a mock content response for testing."""
    return {
        "content_outline": "Mock content outline",
        "podcast_script": "Mock podcast script",
        "study_guide": "Mock study guide",
        "one_pager_summary": "Mock one-pager summary",
        "detailed_reading_material": "Mock detailed reading material",
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

@patch("app.api.routes.get_content_service")
def test_generate_content_success(mock_get_service, client):
    """Tests successful content generation."""
    # Create a mock service
    mock_service = MagicMock()
    mock_content = create_mock_content_response()
    mock_service.generate_content.return_value = (mock_content, 200)
    mock_get_service.return_value = mock_service

        response = client.post(
        "/api/generate-content",
            json={
            "syllabus_text": "A sample syllabus text for testing purposes. " * 10
            },
        )

    assert response.status_code == 200
    json_data = response.get_json()
    
    # Verify all content types are present and correct
    assert json_data["content_outline"] == "Mock content outline"
    assert json_data["podcast_script"] == "Mock podcast script"
    assert json_data["study_guide"] == "Mock study guide"
    assert json_data["one_pager_summary"] == "Mock one-pager summary"
    assert json_data["detailed_reading_material"] == "Mock detailed reading material"
    
    # Verify array content
    assert len(json_data["faqs"]) == 2
    assert json_data["faqs"][0]["question"] == "Mock question 1"
    assert json_data["faqs"][0]["answer"] == "Mock answer 1"
    
    assert len(json_data["flashcards"]) == 2
    assert json_data["flashcards"][0]["term"] == "Mock term 1"
    assert json_data["flashcards"][0]["definition"] == "Mock definition 1"
    
    assert len(json_data["reading_guide_questions"]) == 2
    assert json_data["reading_guide_questions"][0] == "Mock question 1?"
    
@patch("app.api.routes.get_content_service")
def test_generate_content_error(mock_get_service, client):
    """Tests content generation error handling."""
    # Create a mock service that returns an error
    mock_service = MagicMock()
    error_response = {
        "content_outline": "Error: API Error",
        "podcast_script": "Error: API Error",
        "study_guide": "Error: API Error",
        "one_pager_summary": "Error: API Error",
        "detailed_reading_material": "Error: API Error",
        "faqs": [],
        "flashcards": [],
        "reading_guide_questions": []
    }
    mock_service.generate_content.return_value = (error_response, 503)
    mock_get_service.return_value = mock_service

        response = client.post(
        "/api/generate-content",
            json={
                "syllabus_text": "A sample syllabus text for testing purposes. " * 10
            },
        )

    assert response.status_code == 503
    json_data = response.get_json()
    assert "API Error" in json_data.get("content_outline", "")

def test_generate_long_form_content_missing_fields(client):
    """Tests missing required fields for long-form content generation."""
    response = client.post("/api/generate-long-form-content", json={})
    assert response.status_code == 400
    assert "Missing syllabus_text in request" in response.get_json()["error"]

def test_generate_long_form_content_invalid_format(client):
    """Tests invalid target format for long-form content generation."""
    response = client.post("/api/generate-long-form-content", json={
        "syllabus_text": "A sample syllabus text for testing purposes. " * 10,
        "target_format": "invalid_format"
    })
    assert response.status_code == 400
    assert "target_format must be one of" in response.get_json()["error"]

def test_supported_formats(client):
    """Tests the supported formats endpoint."""
    response = client.get("/api/formats")
    assert response.status_code == 200
    json_data = response.get_json()
    assert "supported_formats" in json_data
    assert "podcast" in json_data["supported_formats"]
    assert "guide" in json_data["supported_formats"]
    assert "one_pager" in json_data["supported_formats"]

@patch("app.api.routes.get_enhanced_multi_step_service")
def test_cache_stats(mock_get_service, client):
    """Tests the cache statistics endpoint."""
    # Create a mock service with cache
    mock_service = MagicMock()
    mock_service.get_cache_stats.return_value = {
        "total_entries": 0,
        "cache_utilization": 0,
        "hit_rate": 0.0,
        "miss_rate": 1.0
    }
    mock_get_service.return_value = mock_service

    response = client.get("/api/cache/stats")
    assert response.status_code == 200
    json_data = response.get_json()
    assert "total_entries" in json_data

@patch("app.api.routes.get_enhanced_multi_step_service")
def test_system_stats(mock_get_service, client):
    """Tests the system statistics endpoint."""
    # Create a mock service
    mock_service = MagicMock()
    mock_service.get_cache_stats.return_value = {"total_entries": 0}
    mock_service.progress_tracker.get_stats.return_value = {"total_jobs": 0}
    mock_get_service.return_value = mock_service

    response = client.get("/api/system/stats")
    assert response.status_code == 200
    json_data = response.get_json()
    assert "cache" in json_data
    assert "progress_tracker" in json_data
    assert "system_status" in json_data
 