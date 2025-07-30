"""Tests for security headers middleware."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.security_headers import SecurityHeadersMiddleware


class TestSecurityHeaders:
    """Test security headers functionality."""

    @pytest.fixture
    def app(self):
        """Create test FastAPI app."""
        app = FastAPI()
        
        # Add security headers middleware
        app.add_middleware(SecurityHeadersMiddleware)
        
        # Add test endpoints
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        @app.get("/api/test")
        async def api_endpoint():
            return {"data": "test"}
        
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_all_security_headers_present(self, client):
        """Test that all required security headers are present."""
        response = client.get("/test")
        
        # Check OWASP recommended headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        
        assert "Referrer-Policy" in response.headers
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        
        assert "Permissions-Policy" in response.headers

    def test_hsts_header(self, client):
        """Test HSTS header configuration."""
        response = client.get("/test")
        
        assert "Strict-Transport-Security" in response.headers
        hsts = response.headers["Strict-Transport-Security"]
        
        # Check HSTS directives
        assert "max-age=" in hsts
        assert "includeSubDomains" in hsts
        
        # Check max-age is at least 1 year (31536000 seconds)
        import re
        max_age_match = re.search(r'max-age=(\d+)', hsts)
        if max_age_match:
            max_age = int(max_age_match.group(1))
            assert max_age >= 31536000

    def test_csp_policy(self, client):
        """Test Content Security Policy."""
        response = client.get("/test")
        
        assert "Content-Security-Policy" in response.headers
        csp = response.headers["Content-Security-Policy"]
        
        # Check essential CSP directives
        assert "default-src" in csp
        assert "script-src" in csp
        assert "style-src" in csp
        assert "img-src" in csp
        assert "connect-src" in csp
        assert "frame-ancestors" in csp
        
        # Ensure frame-ancestors prevents clickjacking
        assert "frame-ancestors 'none'" in csp or "frame-ancestors 'self'" in csp

    def test_csp_report_only_mode(self, client):
        """Test CSP report-only mode for development."""
        # In development, might use Content-Security-Policy-Report-Only
        response = client.get("/test")
        
        # Should have either enforcing or report-only CSP
        has_csp = "Content-Security-Policy" in response.headers
        has_csp_report = "Content-Security-Policy-Report-Only" in response.headers
        
        assert has_csp or has_csp_report

    def test_cache_control_headers(self, client):
        """Test cache control for sensitive endpoints."""
        # API endpoints should have no-store
        response = client.get("/api/test")
        
        if "Cache-Control" in response.headers:
            cache_control = response.headers["Cache-Control"]
            assert "no-store" in cache_control or "no-cache" in cache_control

    def test_permissions_policy(self, client):
        """Test Permissions Policy (formerly Feature Policy)."""
        response = client.get("/test")
        
        assert "Permissions-Policy" in response.headers
        permissions = response.headers["Permissions-Policy"]
        
        # Check that sensitive features are disabled
        assert "geolocation=()" in permissions
        assert "camera=()" in permissions
        assert "microphone=()" in permissions

    def test_remove_server_header(self, client):
        """Test that server information is not exposed."""
        response = client.get("/test")
        
        # Server header should be removed or generic
        if "Server" in response.headers:
            assert response.headers["Server"] != "uvicorn"
            assert "python" not in response.headers["Server"].lower()

    def test_environment_specific_headers(self, client, monkeypatch):
        """Test environment-specific header configuration."""
        # Test production headers
        monkeypatch.setenv("ENV", "production")
        response = client.get("/test")
        
        # Production should have strict CSP
        if "Content-Security-Policy" in response.headers:
            csp = response.headers["Content-Security-Policy"]
            assert "'unsafe-inline'" not in csp or "nonce-" in csp
        
        # Production should have HSTS with preload
        if "Strict-Transport-Security" in response.headers:
            hsts = response.headers["Strict-Transport-Security"]
            assert "preload" in hsts

    def test_headers_on_error_responses(self, client):
        """Test that security headers are present on error responses."""
        # Test 404 response
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        # Security headers should still be present
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        
        # Test 500 response (if we can trigger one)
        @client.app.get("/error")
        async def error_endpoint():
            raise Exception("Test error")
        
        response = client.get("/error")
        assert response.status_code == 500
        assert "X-Content-Type-Options" in response.headers

    def test_cors_preflight_headers(self, client):
        """Test security headers on CORS preflight requests."""
        response = client.options(
            "/test",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
            }
        )
        
        # Security headers should be present even on OPTIONS
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers

    def test_api_specific_headers(self, client):
        """Test API-specific security headers."""
        response = client.get("/api/test")
        
        # API responses should have additional restrictions
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        # API should not be embeddable
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_static_file_headers(self, client):
        """Test headers for static file serving."""
        # Create a static file endpoint for testing
        @client.app.get("/static/test.js")
        async def static_file():
            return {"content": "console.log('test');"}
        
        response = client.get("/static/test.js")
        
        # Static files might have different CSP
        if "Content-Security-Policy" in response.headers:
            csp = response.headers["Content-Security-Policy"]
            # Static files might allow different sources
            assert "script-src" in csp

    def test_security_headers_performance(self, client):
        """Test that security headers don't significantly impact performance."""
        import time
        
        # Measure response time with middleware
        start = time.time()
        for _ in range(100):
            response = client.get("/test")
            assert response.status_code == 200
        
        elapsed = time.time() - start
        
        # Should complete 100 requests in reasonable time (< 1 second)
        assert elapsed < 1.0

    def test_csp_nonce_generation(self, client):
        """Test CSP nonce generation for inline scripts."""
        response = client.get("/test")
        
        if "Content-Security-Policy" in response.headers:
            csp = response.headers["Content-Security-Policy"]
            
            # Check if nonce is used for inline scripts
            if "'nonce-" in csp:
                import re
                nonce_match = re.search(r"'nonce-([^']+)'", csp)
                assert nonce_match
                
                # Nonce should be different on each request
                response2 = client.get("/test")
                csp2 = response2.headers.get("Content-Security-Policy", "")
                nonce_match2 = re.search(r"'nonce-([^']+)'", csp2)
                
                if nonce_match2:
                    assert nonce_match.group(1) != nonce_match2.group(1)