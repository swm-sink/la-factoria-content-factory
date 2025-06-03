"""Fixed unit tests for the AI Content Factory FastAPI application."""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Configures the FastAPI test client."""
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["REDIS_URL"] = "redis://localhost:6379"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/test-credentials.json"

    # Create TestClient correctly (no context manager needed)
    test_client = TestClient(app)
    yield test_client

    # Cleanup
    os.environ.pop("TESTING", None)
    os.environ.pop("REDIS_URL", None)
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)


def test_health_check(client):
    """Tests the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "ok"


def test_generate_content_missing_syllabus(client):
    """Tests missing syllabus_text input for /api/v1/content/generate."""
    response = client.post("/api/v1/content/generate", json={"target_format": "guide"})
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert any(
        err["loc"] == ["body", "syllabus_text"] and "Field required" in err["msg"]
        for err in response_json["detail"]
    )


def test_generate_content_empty_syllabus(client):
    """Tests empty syllabus_text input for /api/v1/content/generate."""
    response = client.post(
        "/api/v1/content/generate", json={"syllabus_text": "", "target_format": "guide"}
    )
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert any(
        err["loc"] == ["body", "syllabus_text"] for err in response_json["detail"]
    )


def test_generate_content_too_short_syllabus(client):
    """Tests syllabus_text that is too short for /api/v1/content/generate."""
    response = client.post(
        "/api/v1/content/generate",
        json={"syllabus_text": "Too short", "target_format": "guide"},
    )
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert any(
        err["loc"] == ["body", "syllabus_text"] for err in response_json["detail"]
    )


def create_mock_service_response_content():
    """Creates a mock dictionary that the content_service.generate_long_form_content might return."""
    return {
        "title": "Mock Title from Service",
        "content": "Mock Content from Service",
        "metadata": {"source_syllabus_length": 100, "generated_format": "guide"},
        "quality_metrics": {"clarity_score": 0.95},
        "version_id": "v1.mock",
        "content_outline": "Mock content outline",
        "podcast_script": "Mock podcast script",
        "study_guide": "Mock study guide",
        "one_pager_summary": "Mock one-pager summary",
        "detailed_reading_material": "Mock detailed reading material",
        "faqs": [
            {"question": "Mock question 1", "answer": "Mock answer 1"},
            {"question": "Mock question 2", "answer": "Mock answer 2"},
        ],
        "flashcards": [
            {"term": "Mock term 1", "definition": "Mock definition 1"},
            {"term": "Mock term 2", "definition": "Mock definition 2"},
        ],
        "reading_guide_questions": ["Mock question 1?", "Mock question 2?"],
    }


@patch("app.api.routes.content.content_service")
def test_generate_content_success(mock_content_service_instance, client):
    """Tests successful content generation via /api/v1/content/generate."""
    mock_service_data = create_mock_service_response_content()
    mock_content_service_instance.generate_long_form_content.return_value = (
        mock_service_data,
        200,
        "mock_job_id_123",
    )

    response = client.post(
        "/api/v1/content/generate",
        json={
            "syllabus_text": "A sample syllabus text for testing purposes, long enough to pass validation. "
            * 3,
            "target_format": "guide",
            "use_parallel": False,
            "use_cache": True,
        },
    )

    assert response.status_code == 200
    json_data = response.json()

    # Verify fields from ContentResponse
    assert json_data["title"] == mock_service_data["title"]
    assert json_data["content"] == mock_service_data["content"]
    assert json_data["metadata"] == mock_service_data["metadata"]
    assert json_data["quality_metrics"] == mock_service_data["quality_metrics"]
    assert json_data["version_id"] == mock_service_data["version_id"]

    # Check if the mock service method was called correctly
    mock_content_service_instance.generate_long_form_content.assert_called_once_with(
        "A sample syllabus text for testing purposes, long enough to pass validation. "
        * 3,
        "guide",
        use_parallel=False,
        use_cache=True,
    )


@patch("app.api.routes.content.content_service")
def test_generate_content_service_error(mock_content_service_instance, client):
    """Tests error handling when service raises an exception for /api/v1/content/generate."""
    mock_content_service_instance.generate_long_form_content.side_effect = Exception(
        "Simulated internal service error"
    )

    response = client.post(
        "/api/v1/content/generate",
        json={
            "syllabus_text": "A sample syllabus text for testing. " * 3,
            "target_format": "podcast",
        },
    )

    assert response.status_code == 500
    json_data = response.json()
    assert "detail" in json_data


def test_content_request_validation_missing_syllabus(client):
    """Tests missing syllabus_text for ContentRequest validation at /api/v1/content/generate."""
    response = client.post("/api/v1/content/generate", json={"target_format": "guide"})
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert any(
        err["loc"] == ["body", "syllabus_text"] and "Field required" in err["msg"]
        for err in response_json["detail"]
    )


def test_content_request_validation_invalid_target_format(client):
    """Tests invalid target_format for ContentRequest validation at /api/v1/content/generate."""
    response = client.post(
        "/api/v1/content/generate",
        json={
            "syllabus_text": "A sample syllabus text for testing purposes, long enough. "
            * 3,
            "target_format": "invalid_format_value",
        },
    )
    assert response.status_code == 422
    response_json = response.json()
    assert "detail" in response_json
    assert any(
        err["loc"] == ["body", "target_format"]
        and ("Input should be" in err["msg"] or "unexpected value" in err["msg"])
        for err in response_json["detail"]
    )
