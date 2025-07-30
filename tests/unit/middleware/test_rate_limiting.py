"""Tests for rate limiting middleware."""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.middleware.rate_limiting import RateLimitingMiddleware, get_rate_limit_key


class TestRateLimiting:
    """Test rate limiting functionality."""

    @pytest.fixture
    def app(self):
        """Create test FastAPI app."""
        app = FastAPI()
        
        # Add rate limiting middleware
        app.add_middleware(RateLimitingMiddleware)
        
        # Add test endpoints
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        @app.get("/health")
        async def health_endpoint():
            return {"status": "ok"}
        
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_rate_limit_key_generation(self):
        """Test rate limit key generation from request."""
        # Test with IP address
        request = MagicMock()
        request.client.host = "192.168.1.100"
        request.headers = {}
        
        key = get_rate_limit_key(request)
        assert key == "192.168.1.100"
        
        # Test with API key
        request.headers = {"X-API-Key": "test-key-123"}
        key = get_rate_limit_key(request)
        assert key == "api_key:test-key-123"
        
        # Test with missing client
        request.client = None
        request.headers = {}
        key = get_rate_limit_key(request)
        assert key == "unknown"

    def test_rate_limit_headers(self, client):
        """Test that rate limit headers are included in response."""
        response = client.get("/test")
        
        # Check for rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
        
        # Verify header values
        limit = int(response.headers["X-RateLimit-Limit"])
        remaining = int(response.headers["X-RateLimit-Remaining"])
        reset = int(response.headers["X-RateLimit-Reset"])
        
        assert limit > 0
        assert remaining >= 0
        assert remaining < limit
        assert reset > time.time()

    def test_rate_limit_enforcement(self, client):
        """Test that rate limits are enforced."""
        # Make requests up to the limit
        responses = []
        for _ in range(15):  # Assuming default limit is lower
            response = client.get("/test")
            responses.append(response)
            if response.status_code == 429:
                break
        
        # Verify we hit rate limit
        assert any(r.status_code == 429 for r in responses), "Should hit rate limit"
        
        # Check 429 response
        rate_limited = next(r for r in responses if r.status_code == 429)
        assert rate_limited.json()["detail"] == "Rate limit exceeded"
        assert "Retry-After" in rate_limited.headers

    def test_per_endpoint_limits(self, client):
        """Test different rate limits per endpoint."""
        # Health endpoint should have higher or no limit
        health_responses = []
        for _ in range(50):
            response = client.get("/health")
            health_responses.append(response)
        
        # Health should not be rate limited (or have very high limit)
        assert all(r.status_code == 200 for r in health_responses[:20])
        
        # Regular endpoints should have lower limits
        test_responses = []
        for _ in range(20):
            response = client.get("/test")
            test_responses.append(response)
            if response.status_code == 429:
                break
        
        # Should hit rate limit on test endpoint
        assert any(r.status_code == 429 for r in test_responses)

    def test_rate_limit_with_api_key(self, client):
        """Test rate limiting with API key has separate limits."""
        # Requests without API key
        no_key_responses = []
        for _ in range(10):
            response = client.get("/test")
            no_key_responses.append(response)
            if response.status_code == 429:
                break
        
        # Requests with API key should have separate limit
        api_key_responses = []
        headers = {"X-API-Key": "test-api-key"}
        for _ in range(10):
            response = client.get("/test", headers=headers)
            api_key_responses.append(response)
        
        # API key requests should not be affected by no-key limit
        if any(r.status_code == 429 for r in no_key_responses):
            assert all(r.status_code == 200 for r in api_key_responses[:5])

    def test_rate_limit_reset(self, client):
        """Test rate limit reset after time window."""
        # Hit rate limit
        for _ in range(20):
            response = client.get("/test")
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                break
        
        # Wait for reset (in test, should be short)
        time.sleep(retry_after + 0.5)
        
        # Should be able to make requests again
        response = client.get("/test")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_redis_backend(self):
        """Test rate limiting with Redis backend."""
        with patch("app.middleware.rate_limiting.redis_client") as mock_redis:
            # Mock Redis operations
            mock_redis.get.return_value = None
            mock_redis.incr.return_value = 1
            mock_redis.expire.return_value = True
            
            # Create middleware
            middleware = RateLimitingMiddleware(None)
            
            # Mock request
            request = MagicMock()
            request.url.path = "/test"
            request.client.host = "192.168.1.100"
            request.headers = {}
            
            # Mock call_next
            async def mock_call_next(req):
                return Response(content="test")
            
            # Process request
            response = await middleware.dispatch(request, mock_call_next)
            
            # Verify Redis was used
            assert mock_redis.get.called
            assert mock_redis.incr.called

    def test_custom_error_response(self, client):
        """Test custom rate limit error response."""
        # Hit rate limit
        for _ in range(20):
            response = client.get("/test")
            if response.status_code == 429:
                break
        
        # Check custom error format
        assert response.status_code == 429
        error_data = response.json()
        assert "error" in error_data
        assert error_data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert "limit" in error_data["error"]["details"]
        assert "retry_after" in error_data["error"]["details"]

    def test_rate_limit_exemptions(self, client):
        """Test that certain paths are exempt from rate limiting."""
        exempt_paths = ["/metrics", "/health", "/docs", "/openapi.json"]
        
        for path in exempt_paths:
            # Make many requests to exempt endpoints
            responses = []
            for _ in range(100):
                response = client.get(path, follow_redirects=False)
                if response.status_code not in [404, 307]:  # Path might not exist
                    responses.append(response)
            
            # Should not hit rate limit on exempt paths
            assert not any(r.status_code == 429 for r in responses)