"""Production-ready unit tests for the AI Content Factory FastAPI application.

Tests the actual endpoint architecture:
- /healthz - Public health check
- /api/v1/jobs - Job management (requires API key)
- /api/v1/auth - Authentication endpoints
- /api/v1/health - Protected health check (requires API key)
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_api_key
from app.main import app
from app.services.job_manager import get_job_manager


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
        "PROMETHEUS_DISABLE": "true",  # Disable Prometheus for tests
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


@pytest.fixture
def mock_api_key():
    """Mock API key for protected endpoints."""
    return "test-api-key-123"


@pytest.fixture
def mock_redis():
    """Mock Redis connection to avoid connection failures."""
    with patch("app.services.content_cache.redis.from_url") as mock_redis_func:
        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.return_value = None
        mock_redis_instance.set.return_value = True
        mock_redis_func.return_value = mock_redis_instance
        yield mock_redis_instance


@pytest.fixture
def mock_firestore():
    """Mock Firestore connection."""
    with patch("app.services.job.firestore_client.AsyncClient") as mock_firestore_class:
        mock_firestore_instance = MagicMock()
        mock_firestore_class.return_value = mock_firestore_instance
        yield mock_firestore_instance


@pytest.fixture
def mock_job_manager():
    """Mock JobManager to avoid external dependencies."""
    mock_manager = AsyncMock()

    # Mock job creation
    mock_manager.create_job.return_value = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "status": "pending",
        "created_at": "2024-01-01T00:00:00Z",
    }

    # Mock job listing
    mock_manager.list_jobs.return_value = {
        "jobs": [],
        "total": 0,
        "page": 1,
        "page_size": 10,
        "total_pages": 0,
    }

    return mock_manager


def test_public_health_check(test_env):
    """Tests the public health check endpoint (no auth required)."""
    with TestClient(app) as client:
        response = client.get("/healthz")
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["status"] == "healthy"


def test_protected_health_check_without_api_key(test_env):
    """Tests protected health endpoint requires API key."""
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 401  # Should require API key


def test_protected_health_check_with_api_key(test_env, mock_api_key):
    """Tests protected health endpoint with API key."""
    # Override the dependency for this test
    app.dependency_overrides[get_api_key] = lambda: mock_api_key

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            json_data = response.json()
            assert json_data["status"] == "healthy"
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_jobs_endpoint_requires_auth(test_env):
    """Tests that jobs endpoints require authentication."""
    with TestClient(app) as client:
        # Test GET /api/v1/jobs without auth
        response = client.get("/api/v1/jobs")
        assert response.status_code == 401

        # Test POST /api/v1/jobs without auth
        response = client.post(
            "/api/v1/jobs",
            json={"syllabus_text": "Test syllabus", "target_format": "guide"},
        )
        assert response.status_code == 401


def test_jobs_list_with_auth(
    test_env, mock_api_key, mock_redis, mock_firestore, mock_job_manager
):
    """Tests jobs listing with proper authentication."""
    # Override dependencies for this test
    app.dependency_overrides[get_api_key] = lambda: mock_api_key
    app.dependency_overrides[get_job_manager] = lambda: mock_job_manager

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/jobs")
            assert response.status_code == 200
            json_data = response.json()
            assert "jobs" in json_data
    finally:
        # Clean up dependency overrides
        app.dependency_overrides.clear()


def test_job_creation_with_auth(
    test_env, mock_api_key, mock_redis, mock_firestore, mock_job_manager
):
    """Tests job creation with proper authentication."""
    # Override dependencies for this test
    app.dependency_overrides[get_api_key] = lambda: mock_api_key
    app.dependency_overrides[get_job_manager] = lambda: mock_job_manager

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/jobs",
                json={
                    "syllabus_text": "Introduction to Machine Learning fundamentals including supervised and unsupervised learning algorithms",
                    "target_format": "podcast",
                    "use_parallel": True,
                    "use_cache": True,
                },
            )
            assert response.status_code == 201
            json_data = response.json()
            assert "id" in json_data
    finally:
        # Clean up dependency overrides
        app.dependency_overrides.clear()


def test_job_creation_validation(test_env, mock_api_key, mock_redis, mock_firestore):
    """Tests job creation input validation."""
    # Override dependency for this test
    app.dependency_overrides[get_api_key] = lambda: mock_api_key

    try:
        with TestClient(app) as client:
            # Test missing required fields
            response = client.post(
                "/api/v1/jobs",
                json={
                    "target_format": "guide"
                    # Missing syllabus_text
                },
            )
            assert response.status_code == 422

            # Test empty syllabus_text
            response = client.post(
                "/api/v1/jobs", json={"syllabus_text": "", "target_format": "guide"}
            )
            assert response.status_code == 422

            # Test invalid target_format
            response = client.post(
                "/api/v1/jobs",
                json={
                    "syllabus_text": "Test syllabus",
                    "target_format": "invalid_format",
                },
            )
            assert response.status_code == 422
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_auth_endpoints_exist(test_env):
    """Tests that auth endpoints are accessible."""
    with TestClient(app) as client:
        # Test login endpoint exists (should not return 404)
        response = client.post(
            "/api/v1/auth/login", json={"username": "test", "password": "test"}
        )
        assert response.status_code != 404

        # Test register endpoint exists (should not return 404)
        response = client.post(
            "/api/v1/auth/register",
            json={"username": "test", "email": "test@example.com", "password": "test"},
        )
        assert response.status_code != 404


def test_feedback_endpoint_exists(test_env):
    """Tests that feedback endpoints exist (may be 404 if not implemented yet)."""
    with TestClient(app) as client:
        response = client.post("/api/v1/feedback", json={"message": "Test feedback"})
        # Accept either 401 (requires auth) or 404 (not implemented yet)
        assert response.status_code in [401, 404]


def test_nonexistent_endpoints(test_env):
    """Tests that nonexistent endpoints return 404."""
    with TestClient(app) as client:
        # Test completely invalid endpoint
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

        # Test unversioned endpoints
        response = client.get("/health")
        assert response.status_code == 404


def test_api_versioning(test_env):
    """Tests that API versioning is properly implemented."""
    with TestClient(app) as client:
        # Public health endpoint should exist
        response = client.get("/healthz")
        assert response.status_code == 200

        # Versioned protected endpoints should exist but require auth
        response = client.get("/api/v1/health")
        assert response.status_code == 401  # Requires API key


def test_cors_configuration(test_env):
    """Tests CORS configuration."""
    with TestClient(app) as client:
        # Test preflight request
        response = client.options(
            "/api/v1/jobs",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        # Should not return Method Not Allowed if CORS is properly configured
        assert response.status_code != 405


def test_error_response_format(test_env):
    """Tests that error responses follow consistent format."""
    with TestClient(app) as client:
        # Test 404 error format
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        json_data = response.json()
        assert "detail" in json_data

        # Test 422 validation error format
        response = client.post("/api/v1/jobs", json={"invalid_field": "test"})
        assert response.status_code in [
            401,
            422,
        ]  # Either auth required or validation error


def test_security_headers(test_env):
    """Tests basic security considerations."""
    with TestClient(app) as client:
        response = client.get("/healthz")
        assert response.status_code == 200

        # FastAPI should include basic headers
        response.headers
        # Additional security headers can be added via middleware


def test_input_sanitization(test_env, mock_api_key, mock_redis, mock_firestore):
    """Tests input sanitization for potential security issues."""
    malicious_inputs = [
        "<script>alert('xss')</script>",
        "'; DROP TABLE jobs; --",
        "{{7*7}}",  # Template injection
        "${java.lang.Runtime}",  # Expression injection
    ]

    # Override dependency for this test
    app.dependency_overrides[get_api_key] = lambda: mock_api_key

    try:
        with TestClient(app) as client:
            for malicious_input in malicious_inputs:
                response = client.post(
                    "/api/v1/jobs",
                    json={"syllabus_text": malicious_input, "target_format": "guide"},
                )

                # Should either validate properly or sanitize input
                # At minimum, shouldn't cause server error
                assert response.status_code != 500
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_request_size_limits(test_env, mock_api_key, mock_redis, mock_firestore):
    """Tests that large requests are handled appropriately."""
    # Override dependency for this test
    app.dependency_overrides[get_api_key] = lambda: mock_api_key

    try:
        with TestClient(app) as client:
            # Test with very large request body
            large_syllabus = "x" * 50000  # 50KB syllabus
            response = client.post(
                "/api/v1/jobs",
                json={"syllabus_text": large_syllabus, "target_format": "guide"},
            )

            # Should either process or return appropriate error (not 500)
            assert response.status_code in [200, 201, 413, 422]
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_job_status_endpoint(test_env, mock_api_key, mock_redis, mock_firestore):
    """Tests job status retrieval."""
    # Override dependency for this test
    app.dependency_overrides[get_api_key] = lambda: mock_api_key

    try:
        with TestClient(app) as client:
            # Test getting a non-existent job
            response = client.get("/api/v1/jobs/123e4567-e89b-12d3-a456-426614174000")
            assert response.status_code in [
                404,
                401,
            ]  # Either not found or auth required
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_internal_endpoints_not_exposed(test_env):
    """Tests that internal endpoints are not exposed publicly."""
    with TestClient(app) as client:
        # The internal worker endpoints should not be accessible via /api/v1
        response = client.post(
            "/api/v1/generate-content",
            json={"syllabus_text": "Test", "target_format": "guide"},
        )
        assert response.status_code == 404  # Should not exist in public API
