import os

import pytest

from app.core.config.settings import Settings


@pytest.fixture
def test_settings():
    """Shared test settings fixture with environment-aware defaults"""
    # Allow environment variables to override test defaults
    return Settings(
        gcp_project_id=os.getenv("TEST_GCP_PROJECT_ID", "test-project"),
        gcp_location=os.getenv("TEST_GCP_LOCATION", "us-central1"),
        gemini_model_name=os.getenv(
            "TEST_GEMINI_MODEL_NAME", "models/gemini-2.5-flash-preview-05-20"
        ),
        api_key=os.getenv("TEST_API_KEY", "test_key"),
        elevenlabs_api_key=os.getenv("TEST_ELEVENLABS_API_KEY", "test_eleven_key"),
        jwt_secret_key=os.getenv(
            "TEST_JWT_SECRET_KEY", "test_jwt_secret_key_minimum_length_32"
        ),
        cors_origins=_get_test_cors_origins(),
        cache_max_size=100,
        cache_ttl_seconds=3600,
        max_refinement_iterations=1,
        cache_min_quality_retrieval=0.6,
        enable_cache=True,
        enable_cost_tracking=False,  # Disable for tests unless explicitly needed
        enable_performance_tracking=False,  # Disable for tests
        tasks_worker_service_url=os.getenv(
            "TEST_WORKER_URL", "https://test-worker.example.com"
        ),
    )


def _get_test_cors_origins():
    """Get CORS origins for testing"""
    test_origins = os.getenv("TEST_CORS_ORIGINS")
    if test_origins:
        return [origin.strip() for origin in test_origins.split(",")]
    return ["http://localhost:3000", "http://localhost:5173"]
