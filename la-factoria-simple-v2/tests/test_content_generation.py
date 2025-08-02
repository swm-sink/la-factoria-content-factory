"""
Test Content Generation Endpoint - TDD First!
Task: API-002
"""

import uuid
from datetime import datetime

import pytest
from fastapi.testclient import TestClient


def test_content_generation_endpoint_exists():
    """Test that /api/generate endpoint exists and accepts POST."""
    from src.main import app

    client = TestClient(app)

    # Should not return 404
    response = client.post("/api/generate", json={})
    assert response.status_code != 404


def test_content_generation_requires_authentication():
    """Test that endpoint requires API key authentication."""
    from src.main import app

    client = TestClient(app)

    # No API key should return 401
    response = client.post("/api/generate", json={"topic": "Python basics"})
    assert response.status_code == 401
    assert "detail" in response.json()


def test_content_generation_validates_required_topic():
    """Test that topic field is required."""
    from src.main import app

    client = TestClient(app)

    # Missing topic should return 422
    response = client.post("/api/generate", json={}, headers={"X-API-Key": "test-key-123"})
    assert response.status_code == 422
    error = response.json()
    assert "topic" in str(error["detail"])


def test_content_generation_validates_topic_length():
    """Test topic length validation (min 10, max 500 chars)."""
    from src.main import app

    client = TestClient(app)

    # Too short topic
    response = client.post("/api/generate", json={"topic": "AI"}, headers={"X-API-Key": "test-key-123"})
    assert response.status_code == 422
    assert "at least 10 characters" in str(response.json()["detail"])

    # Too long topic
    long_topic = "x" * 501
    response = client.post("/api/generate", json={"topic": long_topic}, headers={"X-API-Key": "test-key-123"})
    assert response.status_code == 422
    assert "at most 500 characters" in str(response.json()["detail"])


def test_content_generation_validates_content_type():
    """Test that content_type must be from allowed list."""
    from src.main import app

    client = TestClient(app)

    # Invalid content type
    response = client.post(
        "/api/generate",
        json={"topic": "Python basics", "content_type": "invalid_type"},
        headers={"X-API-Key": "test-key-123"},
    )
    assert response.status_code == 422
    assert "content_type" in str(response.json()["detail"])


def test_content_generation_uses_default_content_type():
    """Test that default content_type is study_guide."""
    from src.main import app

    client = TestClient(app)

    # No content_type specified
    response = client.post("/api/generate", json={"topic": "Python basics"}, headers={"X-API-Key": "test-key-123"})
    assert response.status_code == 200
    data = response.json()
    assert data["content_type"] == "study_guide"


def test_successful_content_generation():
    """Test successful content generation returns correct schema."""
    from src.main import app

    client = TestClient(app)

    response = client.post(
        "/api/generate",
        json={"topic": "Introduction to Machine Learning", "content_type": "flashcards"},
        headers={"X-API-Key": "test-key-123"},
    )

    assert response.status_code == 200
    data = response.json()

    # Check response schema
    assert "content" in data
    assert isinstance(data["content"], str)
    assert len(data["content"]) > 100  # Should have substantial content

    assert data["content_type"] == "flashcards"
    assert data["topic"] == "Introduction to Machine Learning"

    assert "generated_at" in data
    # Verify it's a valid ISO timestamp
    datetime.fromisoformat(data["generated_at"].replace("Z", "+00:00"))

    assert "request_id" in data
    # Verify it's a valid UUID
    uuid.UUID(data["request_id"])


def test_request_ids_are_unique():
    """Test that each request gets a unique request_id."""
    from src.main import app

    client = TestClient(app)

    # Make two requests
    response1 = client.post("/api/generate", json={"topic": "Python basics"}, headers={"X-API-Key": "test-key-123"})

    response2 = client.post("/api/generate", json={"topic": "Python basics"}, headers={"X-API-Key": "test-key-123"})

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Request IDs should be different
    assert response1.json()["request_id"] != response2.json()["request_id"]


def test_all_content_types_supported():
    """Test that all extracted content types are supported."""
    from src.main import app

    client = TestClient(app)

    content_types = [
        "study_guide",
        "study_guide_enhanced",
        "flashcards",
        "podcast_script",
        "one_pager_summary",
        "detailed_reading_material",
        "faq_collection",
        "reading_guide_questions",
        "master_content_outline",
    ]

    for content_type in content_types:
        response = client.post(
            "/api/generate",
            json={"topic": f"Test topic for {content_type}", "content_type": content_type},
            headers={"X-API-Key": "test-key-123"},
        )
        assert response.status_code == 200, f"Failed for {content_type}"
        assert response.json()["content_type"] == content_type


def test_invalid_api_key_rejected():
    """Test that invalid API keys are rejected."""
    from src.main import app

    client = TestClient(app)

    response = client.post("/api/generate", json={"topic": "Python basics"}, headers={"X-API-Key": "invalid-key-999"})
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]
