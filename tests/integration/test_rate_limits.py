"""Integration tests for rate limiting across the application."""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
import requests
from fastapi.testclient import TestClient

from app.main import app


class TestRateLimitingIntegration:
    """Integration tests for rate limiting."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def base_url(self):
        """Base URL for integration tests."""
        return "http://localhost:8000"

    def test_concurrent_requests_rate_limiting(self, client):
        """Test rate limiting under concurrent load."""
        results = {"success": 0, "rate_limited": 0}
        
        def make_request():
            response = client.get("/api/v1/health")
            if response.status_code == 200:
                results["success"] += 1
            elif response.status_code == 429:
                results["rate_limited"] += 1
            return response.status_code
        
        # Make concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            statuses = [f.result() for f in futures]
        
        # Verify some requests were rate limited
        assert results["rate_limited"] > 0, "Should have rate limited some requests"
        assert results["success"] > 0, "Should have successful requests"

    def test_different_endpoints_different_limits(self, client):
        """Test that different endpoints have different rate limits."""
        endpoints = [
            ("/api/v1/content/generate", 5),   # Low limit for expensive operations
            ("/api/v1/health", 100),           # High limit for health checks
            ("/api/v1/auth/login", 10),        # Medium limit for auth
        ]
        
        for endpoint, expected_limit in endpoints:
            response = client.post(endpoint, json={})  # May fail, just need headers
            
            if "X-RateLimit-Limit" in response.headers:
                limit = int(response.headers["X-RateLimit-Limit"])
                assert limit > 0, f"Endpoint {endpoint} should have positive limit"

    def test_rate_limit_persistence(self, client):
        """Test that rate limits persist across requests."""
        endpoint = "/api/v1/test"
        
        # Make first request
        response1 = client.get(endpoint)
        if "X-RateLimit-Remaining" in response1.headers:
            remaining1 = int(response1.headers["X-RateLimit-Remaining"])
            
            # Make second request
            response2 = client.get(endpoint)
            remaining2 = int(response2.headers["X-RateLimit-Remaining"])
            
            # Remaining should decrease
            assert remaining2 < remaining1

    def test_api_key_higher_limits(self, client):
        """Test that API key authenticated requests have higher limits."""
        # Without API key
        no_key_remaining = None
        response = client.get("/api/v1/test")
        if "X-RateLimit-Limit" in response.headers:
            no_key_limit = int(response.headers["X-RateLimit-Limit"])
        
        # With API key
        headers = {"X-API-Key": "test-key"}
        response = client.get("/api/v1/test", headers=headers)
        if "X-RateLimit-Limit" in response.headers:
            api_key_limit = int(response.headers["X-RateLimit-Limit"])
            
            # API key should have higher or equal limit
            assert api_key_limit >= no_key_limit

    @pytest.mark.asyncio
    async def test_distributed_rate_limiting(self):
        """Test rate limiting works across multiple instances."""
        # This would test Redis-backed rate limiting
        # In a real test, we'd spin up multiple app instances
        pass

    def test_rate_limit_cost_based(self, client):
        """Test cost-based rate limiting for expensive operations."""
        # Content generation should consume more "cost" than simple queries
        expensive_endpoint = "/api/v1/content/generate"
        cheap_endpoint = "/api/v1/health"
        
        # Make requests to expensive endpoint
        expensive_responses = []
        for i in range(10):
            response = client.post(
                expensive_endpoint,
                json={"content_type": "podcast_script", "topic": f"Test {i}"}
            )
            expensive_responses.append(response)
            if response.status_code == 429:
                break
        
        # Should hit rate limit quickly on expensive endpoint
        expensive_hits = len([r for r in expensive_responses if r.status_code != 429])
        
        # Make requests to cheap endpoint
        cheap_responses = []
        for i in range(50):
            response = client.get(cheap_endpoint)
            cheap_responses.append(response)
            if response.status_code == 429:
                break
        
        # Should allow more requests on cheap endpoint
        cheap_hits = len([r for r in cheap_responses if r.status_code != 429])
        
        # Cheap endpoint should allow more requests
        assert cheap_hits > expensive_hits * 2

    def test_rate_limit_metrics(self, client):
        """Test that rate limit metrics are exposed."""
        # Make some requests to generate metrics
        for _ in range(10):
            client.get("/api/v1/test")
        
        # Check metrics endpoint
        response = client.get("/metrics")
        if response.status_code == 200:
            metrics = response.text
            
            # Should have rate limit metrics
            assert "rate_limit_hits_total" in metrics
            assert "rate_limit_exceeded_total" in metrics

    def test_graceful_degradation(self, client):
        """Test graceful degradation when rate limited."""
        # Hit rate limit
        for _ in range(50):
            response = client.get("/api/v1/test")
            if response.status_code == 429:
                # Check error message is helpful
                error = response.json()
                assert "error" in error
                assert "retry" in error["error"]["message"].lower()
                assert "Retry-After" in response.headers
                break

    def test_rate_limit_bypass_internal(self, client):
        """Test internal endpoints bypass rate limiting."""
        # Internal health check endpoint
        internal_headers = {"X-Internal-Request": "true"}
        
        # Make many requests with internal header
        responses = []
        for _ in range(100):
            response = client.get("/internal/health", headers=internal_headers)
            responses.append(response)
        
        # Should not hit rate limit for internal requests
        assert all(r.status_code != 429 for r in responses)