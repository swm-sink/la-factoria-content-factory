"""
Test Health Check Endpoint - TDD First!
Task: API-001
"""
import pytest
from fastapi.testclient import TestClient


def test_health_check_exists():
    """Test that health check endpoint exists."""
    from src.main import app
    client = TestClient(app)
    
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_returns_correct_format():
    """Test that health check returns expected JSON format."""
    from src.main import app
    client = TestClient(app)
    
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


def test_health_check_is_fast():
    """Test that health check responds quickly."""
    from src.main import app
    client = TestClient(app)
    
    import time
    start = time.time()
    response = client.get("/health")
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 0.1  # Should respond in under 100ms


def test_health_check_no_auth_required():
    """Test that health check doesn't require authentication."""
    from src.main import app
    client = TestClient(app)
    
    # Should work without any auth headers
    response = client.get("/health")
    assert response.status_code == 200
    
    # Should also work with invalid auth
    response = client.get("/health", headers={"X-API-Key": "invalid"})
    assert response.status_code == 200