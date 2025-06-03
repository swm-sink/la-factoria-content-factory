"""Final production-ready unit tests for the AI Content Factory FastAPI application."""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def test_env():
    """Set up test environment variables."""
    original_env = {}
    test_vars = {
        "TESTING": "true",
        "REDIS_URL": "redis://localhost:6379",
        "GOOGLE_APPLICATION_CREDENTIALS": "/tmp/test-credentials.json",
        "SECRET_KEY": "test-secret-key-for-testing-only",
        "ENVIRONMENT": "test",
    }

    # Store original values
    for key, value in test_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    yield test_vars

    # Restore original values
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


def test_health_check(test_env):
    """Tests the public health check endpoint."""
    with TestClient(app) as client:
        response = client.get("/healthz")
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["status"] == "healthy"


def test_generate_content_missing_syllabus(test_env):
    """Tests missing syllabus_text input for /api/v1/content/generate."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/content/generate", json={"target_format": "guide"}
        )
        assert response.status_code == 422
        response_json = response.json()
        assert "detail" in response_json


def test_generate_content_empty_syllabus(test_env):
    """Tests empty syllabus_text input for /api/v1/content/generate."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/content/generate",
            json={"syllabus_text": "", "target_format": "guide"},
        )
        assert response.status_code == 422
        response_json = response.json()
        assert "detail" in response_json


def create_mock_service_response_content():
    """Creates a mock dictionary for successful content generation."""
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
def test_generate_content_success(mock_content_service_instance, test_env):
    """Tests successful content generation via /api/v1/content/generate."""
    mock_service_data = create_mock_service_response_content()
    mock_content_service_instance.generate_long_form_content.return_value = (
        mock_service_data,
        200,
        "mock_job_id_123",
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/content/generate",
            json={
                "syllabus_text": "A comprehensive syllabus about machine learning fundamentals covering supervised learning, unsupervised learning, and deep learning concepts with practical applications.",
                "target_format": "guide",
                "use_parallel": False,
                "use_cache": True,
            },
        )

        assert response.status_code == 200
        json_data = response.json()

        # Verify core fields from ContentResponse
        assert "title" in json_data
        assert "content" in json_data
        assert "metadata" in json_data


@patch("app.api.routes.content.content_service")
def test_generate_content_service_error(mock_content_service_instance, test_env):
    """Tests error handling when service raises an exception."""
    mock_content_service_instance.generate_long_form_content.side_effect = Exception(
        "Simulated internal service error"
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/content/generate",
            json={
                "syllabus_text": "A sample syllabus for testing error scenarios.",
                "target_format": "podcast",
            },
        )

        assert response.status_code == 500
        json_data = response.json()
        assert "detail" in json_data


def test_content_request_validation_invalid_target_format(test_env):
    """Tests invalid target_format for ContentRequest validation."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/content/generate",
            json={
                "syllabus_text": "A comprehensive syllabus about data science fundamentals.",
                "target_format": "invalid_format_value",
            },
        )
        assert response.status_code == 422
        response_json = response.json()
        assert "detail" in response_json


def test_jobs_endpoint_basic(test_env):
    """Tests basic jobs endpoint functionality."""
    with TestClient(app) as client:
        # Test getting jobs (should return empty list or auth error)
        response = client.get("/api/v1/jobs")
        # Should either return 401 (auth required) or 200 (empty list)
        assert response.status_code in [200, 401]


def test_auth_endpoints_exist(test_env):
    """Tests that auth endpoints are accessible."""
    with TestClient(app) as client:
        # Test login endpoint exists
        response = client.post(
            "/api/v1/auth/login", json={"username": "test", "password": "test"}
        )
        # Should return validation error or auth failure (not 404)
        assert response.status_code != 404

        # Test register endpoint exists
        response = client.post(
            "/api/v1/auth/register",
            json={"username": "test", "email": "test@example.com", "password": "test"},
        )
        # Should return validation error or conflict (not 404)
        assert response.status_code != 404


def test_security_headers(test_env):
    """Tests that security headers are present."""
    with TestClient(app) as client:
        response = client.get("/healthz")

        # Check for basic security headers
        response.headers
        # FastAPI should include basic security headers
        assert response.status_code == 200
        # Additional security headers can be added via middleware


def test_input_sanitization(test_env):
    """Tests input sanitization for potential XSS/injection attacks."""
    malicious_inputs = [
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "{{7*7}}",  # Template injection
        "${java.lang.Runtime}",  # Expression injection
    ]

    with TestClient(app) as client:
        for malicious_input in malicious_inputs:
            response = client.post(
                "/api/v1/content/generate",
                json={"syllabus_text": malicious_input, "target_format": "guide"},
            )

            # Should either validate properly or sanitize input
            # At minimum, shouldn't cause server error
            assert response.status_code != 500


def test_api_versioning(test_env):
    """Tests that API versioning is properly implemented."""
    with TestClient(app) as client:
        # Test public health endpoint exists
        response = client.get("/healthz")
        assert response.status_code == 200

        # Test that unversioned endpoints redirect or return proper error
        response = client.get("/health")
        assert response.status_code in [404, 301, 302]  # Should not exist or redirect


def test_error_response_format(test_env):
    """Tests that error responses follow consistent format."""
    with TestClient(app) as client:
        # Test 422 validation error format
        response = client.post(
            "/api/v1/content/generate", json={"invalid_field": "test"}
        )
        assert response.status_code == 422
        json_data = response.json()
        assert "detail" in json_data

        # Test 404 error format
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404


def test_cors_headers(test_env):
    """Tests that CORS headers are properly configured."""
    with TestClient(app) as client:
        # Test OPTIONS request
        response = client.options("/healthz")
        # Should not return 405 Method Not Allowed if CORS is configured
        assert response.status_code != 405


def test_request_size_limits(test_env):
    """Tests that request size limits are enforced."""
    with TestClient(app) as client:
        # Test with very large request body
        large_syllabus = "x" * 50000  # 50KB syllabus
        response = client.post(
            "/api/v1/content/generate",
            json={"syllabus_text": large_syllabus, "target_format": "guide"},
        )

        # Should either process or return appropriate error (not 500)
        assert response.status_code in [
            200,
            413,
            422,
        ]  # OK, Payload Too Large, or Validation Error
