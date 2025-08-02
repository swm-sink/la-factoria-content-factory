"""
TDD Tests for Simplified Tikal - Write Tests First!
Total: ~50 lines (vs 1000+ in original)
"""
import pytest
from fastapi.testclient import TestClient

# Test the app before it exists (TDD)
def test_health_endpoint_exists():
    """Test 1: Health check endpoint should exist"""
    from backend.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_content_generation_requires_auth():
    """Test 2: Content generation should require API key"""
    from backend.main import app
    client = TestClient(app)
    response = client.post("/api/generate", json={"topic": "Python"})
    assert response.status_code == 401

def test_content_generation_success():
    """Test 3: Content generation should work with valid API key"""
    from backend.main import app
    client = TestClient(app)
    response = client.post(
        "/api/generate",
        json={"topic": "Python basics", "content_type": "study_guide"},
        headers={"X-API-Key": "test-key-123"}
    )
    assert response.status_code == 200
    assert "content" in response.json()
    assert len(response.json()["content"]) > 100

def test_user_deletion_gdpr():
    """Test 4: GDPR compliance - user deletion should work"""
    from backend.main import app
    client = TestClient(app)
    response = client.delete(
        "/api/user/user123",
        headers={"X-API-Key": "admin-key-123"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "deleted", "user_id": "user123"}

def test_basic_stats():
    """Test 5: Basic monitoring stats should work"""
    from backend.main import app
    client = TestClient(app)
    response = client.get(
        "/api/stats",
        headers={"X-API-Key": "test-key-123"}
    )
    assert response.status_code == 200
    stats = response.json()
    assert "total_generations" in stats
    assert "active_users" in stats
    assert isinstance(stats["total_generations"], int)