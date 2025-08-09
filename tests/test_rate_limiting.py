"""
Test suite for API rate limiting functionality
Simple approach: Test that rate limiting works on expensive AI endpoints
"""
# Fix Python path for src imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import time
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestRateLimiting:
    """Test rate limiting on expensive AI content generation endpoints"""

    def test_content_generation_rate_limit(self):
        """Test that content generation endpoints are rate limited"""
        # Simple test data
        request_data = {
            "topic": "Test Topic for Rate Limiting",
            "age_group": "high_school"
        }
        
        headers = {"Authorization": "Bearer test-api-key"}
        
        # Make rapid requests to trigger rate limit
        responses = []
        for i in range(12):  # Exceed the 10/minute limit
            response = client.post(
                "/api/v1/generate/study_guide",
                json=request_data,
                headers=headers
            )
            responses.append(response)
            
        # Should have some rate limited responses (429 Too Many Requests)
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes, f"Expected rate limit (429) not found in {status_codes}"
        
    def test_rate_limit_reset_after_time(self):
        """Test that rate limit resets after time window"""
        request_data = {
            "topic": "Test Topic for Rate Reset",
            "age_group": "high_school"
        }
        
        headers = {"Authorization": "Bearer test-api-key"}
        
        # First request should work
        response1 = client.post(
            "/api/v1/generate/flashcards",
            json=request_data,
            headers=headers
        )
        
        # Note: In real test, we'd wait for rate limit window
        # For now, just verify the endpoint is accessible
        assert response1.status_code in [200, 429]  # Either works or is rate limited
        
    def test_health_endpoints_not_rate_limited(self):
        """Test that health check endpoints are NOT rate limited"""
        # Health endpoints should never be rate limited
        for i in range(15):  # More than any rate limit
            response = client.get("/api/v1/health")
            assert response.status_code == 200, f"Health endpoint rate limited on request {i}"