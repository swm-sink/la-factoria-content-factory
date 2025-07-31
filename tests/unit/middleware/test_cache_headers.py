"""
Unit tests for cache headers middleware.
"""

import pytest
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from app.middleware.cache_headers import CacheHeadersMiddleware, CacheInvalidationHandler
from app.core.config.cache_config import CacheConfig, CacheStrategy
from app.utils.cache_utils import CacheUtils


@pytest.fixture
def test_app():
    """Create test FastAPI app with cache middleware."""
    app = FastAPI()
    app.add_middleware(CacheHeadersMiddleware)
    
    @app.get("/api/v1/content/types")
    async def get_content_types():
        return {"types": ["flashcards", "quiz", "summary"]}
    
    @app.get("/api/v1/user/profile")
    async def get_user_profile():
        return {"user": "test", "email": "test@example.com"}
    
    @app.get("/static/css/main.css")
    async def get_static_css():
        return JSONResponse(
            content="body { margin: 0; }",
            media_type="text/css"
        )
    
    @app.post("/api/v1/content/generate")
    async def generate_content():
        # Simulate cache invalidation
        handler = CacheInvalidationHandler()
        handler.invalidate("/api/v1/content*")
        return {"id": "123", "status": "processing"}
    
    @app.get("/healthz")
    async def health_check():
        return {"status": "healthy"}
    
    return app


@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)


class TestCacheHeaders:
    """Test cache header middleware functionality."""
    
    def test_static_content_caching(self, client):
        """Test static content gets long-term cache headers."""
        response = client.get("/static/css/main.css")
        
        assert response.status_code == 200
        assert "Cache-Control" in response.headers
        
        cache_control = response.headers["Cache-Control"]
        assert "max-age=31536000" in cache_control
        assert "public" in cache_control
        assert "immutable" in cache_control
    
    def test_api_response_caching(self, client):
        """Test API responses get appropriate cache headers."""
        response = client.get("/api/v1/content/types")
        
        assert response.status_code == 200
        assert "Cache-Control" in response.headers
        
        cache_control = response.headers["Cache-Control"]
        assert "max-age=900" in cache_control  # 15 minutes for content types
        assert "public" in cache_control
    
    def test_user_specific_no_cache(self, client):
        """Test user-specific content is not cached."""
        response = client.get("/api/v1/user/profile")
        
        assert response.status_code == 200
        assert "Cache-Control" in response.headers
        
        cache_control = response.headers["Cache-Control"]
        assert "no-cache" in cache_control or "max-age=0" in cache_control
    
    def test_health_check_no_cache(self, client):
        """Test health check endpoints are not cached."""
        response = client.get("/healthz")
        
        assert response.status_code == 200
        assert "Cache-Control" in response.headers
        
        cache_control = response.headers["Cache-Control"]
        assert "no-cache" in cache_control
    
    def test_etag_generation(self, client):
        """Test ETag headers are generated for dynamic content."""
        response = client.get("/api/v1/content/types")
        
        assert response.status_code == 200
        assert "ETag" in response.headers
        assert response.headers["ETag"].startswith('W/"')  # Weak ETag
    
    def test_conditional_request_304(self, client):
        """Test conditional requests return 304 when content unchanged."""
        # First request to get ETag
        response1 = client.get("/api/v1/content/types")
        etag = response1.headers.get("ETag")
        
        assert etag is not None
        
        # Second request with If-None-Match
        response2 = client.get(
            "/api/v1/content/types",
            headers={"If-None-Match": etag}
        )
        
        assert response2.status_code == 304
        assert len(response2.content) == 0  # No body for 304
    
    def test_last_modified_header(self, client):
        """Test Last-Modified headers are present."""
        response = client.get("/api/v1/content/types")
        
        assert response.status_code == 200
        assert "Last-Modified" in response.headers
        
        # Verify it's a valid HTTP date
        last_modified = response.headers["Last-Modified"]
        assert "GMT" in last_modified
    
    def test_vary_headers(self, client):
        """Test Vary headers for content negotiation."""
        response = client.get(
            "/api/v1/content/types",
            headers={"Accept": "application/json", "Accept-Encoding": "gzip"}
        )
        
        assert response.status_code == 200
        assert "Vary" in response.headers
        
        vary = response.headers["Vary"]
        assert "Accept" in vary
        assert "Accept-Encoding" in vary
    
    def test_process_time_header(self, client):
        """Test X-Process-Time header is added."""
        response = client.get("/api/v1/content/types")
        
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers
        assert "ms" in response.headers["X-Process-Time"]


class TestCacheUtils:
    """Test cache utility functions."""
    
    def test_etag_generation(self):
        """Test ETag generation from content."""
        utils = CacheUtils()
        
        # Test string content
        etag1 = utils.generate_etag("Hello World")
        assert etag1.startswith('W/"')
        assert etag1.endswith('"')
        
        # Test bytes content
        etag2 = utils.generate_etag(b"Hello World")
        assert etag1 == etag2  # Same content should produce same ETag
        
        # Test different content produces different ETags
        etag3 = utils.generate_etag("Different content")
        assert etag1 != etag3
    
    def test_etag_from_dict(self):
        """Test ETag generation from dictionary."""
        utils = CacheUtils()
        
        data = {"key": "value", "number": 42}
        etag = utils.generate_etag_from_dict(data)
        
        assert etag.startswith('W/"')
        
        # Same data in different order should produce same ETag
        data2 = {"number": 42, "key": "value"}
        etag2 = utils.generate_etag_from_dict(data2)
        assert etag == etag2
    
    def test_parse_if_none_match(self):
        """Test parsing If-None-Match header."""
        utils = CacheUtils()
        
        # Single ETag
        etags = utils.parse_if_none_match('W/"abc123"')
        assert 'W/"abc123"' in etags
        
        # Multiple ETags
        etags = utils.parse_if_none_match('W/"abc123", W/"def456"')
        assert 'W/"abc123"' in etags
        assert 'W/"def456"' in etags
        
        # Wildcard
        etags = utils.parse_if_none_match("*")
        assert "*" in etags
    
    def test_http_date_formatting(self):
        """Test HTTP date formatting."""
        utils = CacheUtils()
        
        # Test with specific date
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        formatted = utils.format_http_date(dt)
        assert formatted == "Mon, 01 Jan 2024 12:00:00 GMT"
        
        # Test current date
        now_formatted = utils.format_http_date()
        assert "GMT" in now_formatted
    
    def test_cache_control_builder(self):
        """Test Cache-Control header building."""
        utils = CacheUtils()
        
        # Test public caching
        cc = utils.build_cache_control_header(
            max_age=3600,
            public=True,
            immutable=True
        )
        assert "public" in cc
        assert "max-age=3600" in cc
        assert "immutable" in cc
        
        # Test private caching
        cc = utils.build_cache_control_header(
            max_age=300,
            private=True,
            must_revalidate=True
        )
        assert "private" in cc
        assert "max-age=300" in cc
        assert "must-revalidate" in cc
        
        # Test no-cache
        cc = utils.build_cache_control_header(no_cache=True)
        assert cc == "no-cache"
    
    def test_should_return_304(self):
        """Test 304 decision logic."""
        utils = CacheUtils()
        
        # Test ETag match
        should_304 = utils.should_return_304(
            etag='W/"abc123"',
            if_none_match='W/"abc123"',
            last_modified=None,
            if_modified_since=None
        )
        assert should_304 is True
        
        # Test ETag mismatch
        should_304 = utils.should_return_304(
            etag='W/"abc123"',
            if_none_match='W/"def456"',
            last_modified=None,
            if_modified_since=None
        )
        assert should_304 is False
        
        # Test Last-Modified
        last_modified = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        if_modified_since = "Mon, 01 Jan 2024 13:00:00 GMT"  # After last modified
        
        should_304 = utils.should_return_304(
            etag=None,
            if_none_match=None,
            last_modified=last_modified,
            if_modified_since=if_modified_since
        )
        assert should_304 is True


class TestCacheConfig:
    """Test cache configuration."""
    
    def test_content_type_config(self):
        """Test content type based cache configuration."""
        config = CacheConfig()
        
        # Test CSS
        css_config = config.get_cache_config("/test", "text/css")
        assert css_config["max_age"] == 31536000
        assert css_config["strategy"] == CacheStrategy.PUBLIC
        assert css_config["immutable"] is True
        
        # Test JSON
        json_config = config.get_cache_config("/test", "application/json")
        assert json_config["max_age"] == 300
        assert json_config["strategy"] == CacheStrategy.PRIVATE
        
        # Test HTML
        html_config = config.get_cache_config("/test", "text/html")
        assert html_config["max_age"] == 60
        assert html_config["strategy"] == CacheStrategy.PRIVATE
    
    def test_path_based_config(self):
        """Test path-based cache configuration."""
        config = CacheConfig()
        
        # Test static path
        static_config = config.get_cache_config("/static/file.js")
        assert static_config["max_age"] == 31536000
        assert static_config["strategy"] == CacheStrategy.PUBLIC
        
        # Test user path
        user_config = config.get_cache_config("/api/v1/user/profile")
        assert user_config["max_age"] == 0
        assert user_config["strategy"] == CacheStrategy.NO_CACHE
        
        # Test health check
        health_config = config.get_cache_config("/healthz")
        assert health_config["max_age"] == 0
        assert health_config["strategy"] == CacheStrategy.NO_CACHE
    
    def test_should_use_etag(self):
        """Test ETag usage decision."""
        config = CacheConfig()
        
        # Should use ETag for API endpoints
        assert config.should_use_etag("/api/v1/content") is True
        
        # Should not use ETag for static files
        assert config.should_use_etag("/static/file.js") is False
        assert config.should_use_etag("/assets/image.png") is False
        assert config.should_use_etag("/healthz") is False


class TestCacheInvalidation:
    """Test cache invalidation functionality."""
    
    def test_invalidation_handler_singleton(self):
        """Test invalidation handler is a singleton."""
        handler1 = CacheInvalidationHandler()
        handler2 = CacheInvalidationHandler()
        
        assert handler1 is handler2
    
    def test_invalidation_marking(self):
        """Test marking patterns for invalidation."""
        handler = CacheInvalidationHandler()
        
        # Clear any existing invalidations
        handler._invalidated_patterns.clear()
        
        # Mark pattern
        handler.invalidate("/api/v1/content*")
        
        assert "/api/v1/content*" in handler._invalidated_patterns
    
    def test_pattern_matching(self):
        """Test pattern matching for invalidation."""
        handler = CacheInvalidationHandler()
        
        # Test wildcard matching
        assert handler._matches_pattern("/api/v1/content/123", "/api/v1/content*") is True
        assert handler._matches_pattern("/api/v1/users/123", "/api/v1/content*") is False
        
        # Test exact matching
        assert handler._matches_pattern("/api/v1/exact", "/api/v1/exact") is True
        assert handler._matches_pattern("/api/v1/exact/more", "/api/v1/exact") is False
    
    def test_invalidation_cleanup(self):
        """Test cleanup of old invalidation records."""
        handler = CacheInvalidationHandler()
        handler._invalidated_patterns.clear()
        
        # Add current invalidation
        handler.invalidate("/api/v1/current*")
        
        # Add old invalidation (simulate old timestamp)
        from datetime import timedelta
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        handler._invalidated_patterns["/api/v1/old*"] = old_time
        
        # Cleanup
        handler.cleanup_old_invalidations(max_age_hours=24)
        
        assert "/api/v1/current*" in handler._invalidated_patterns
        assert "/api/v1/old*" not in handler._invalidated_patterns