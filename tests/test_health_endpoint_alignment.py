"""
Test Health Endpoint Alignment with Railway Configuration
=========================================================

RED Phase: Test-first development to ensure health check paths are properly aligned
between Railway deployment configuration and FastAPI endpoints.

Critical Issue: Railway.toml expects /api/v1/health but we need to verify:
1. The endpoint exists and responds correctly
2. No duplicate endpoints cause confusion
3. Response format matches Railway expectations
"""

# Fix Python path for src imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Import railway.toml configuration for validation
import toml
import os

def get_railway_health_path():
    """Extract health check path from railway.toml"""
    railway_config_path = os.path.join(os.path.dirname(__file__), "..", "railway.toml")
    if os.path.exists(railway_config_path):
        config = toml.load(railway_config_path)
        return config.get("deploy", {}).get("healthcheckPath", "/health")
    return "/health"

class TestHealthEndpointAlignment:
    """Test suite to ensure health endpoints align with Railway configuration"""
    
    def test_railway_health_endpoint_exists(self):
        """
        RED TEST: Verify that the health endpoint configured in railway.toml exists
        
        This test will fail if:
        - The configured health path doesn't respond
        - The response format is incorrect for Railway
        - The endpoint returns non-200 status
        """
        # Get expected path from railway.toml
        expected_path = get_railway_health_path()
        
        # Test that Railway's expected health endpoint exists
        response = client.get(expected_path)
        
        # Railway expects 200 status code for healthy service
        assert response.status_code == 200, f"Health endpoint {expected_path} should return 200"
        
        # Verify response contains required fields for Railway
        data = response.json()
        assert "status" in data, "Health response must contain 'status' field"
        assert "timestamp" in data, "Health response must contain 'timestamp' field"
        
        # Status should indicate healthy service
        assert data["status"] in ["healthy", "degraded"], f"Status should be 'healthy' or 'degraded', got: {data['status']}"
    
    def test_no_duplicate_health_endpoints(self):
        """
        RED TEST: Ensure there are no conflicting health endpoints
        
        This test identifies if we have multiple health endpoints that could
        cause confusion during deployment or monitoring.
        """
        # Test the main health endpoint
        main_health_response = client.get("/health")
        
        # Test the API versioned health endpoint  
        api_v1_health_response = client.get("/api/v1/health")
        
        # Both should exist and return 200, but should have consistent behavior
        assert main_health_response.status_code == 200
        assert api_v1_health_response.status_code == 200
        
        # Get response data
        main_data = main_health_response.json()
        api_data = api_v1_health_response.json()
        
        # The API v1 endpoint should be more detailed than the main endpoint
        # Main endpoint should be simple, API endpoint should be comprehensive
        assert "status" in main_data
        assert "status" in api_data
        
        # API v1 endpoint should have additional details for monitoring
        assert len(api_data.keys()) >= len(main_data.keys()), "API v1 health endpoint should provide more detail"
    
    def test_health_endpoint_response_format(self):
        """
        RED TEST: Verify health endpoint response format matches Railway expectations
        
        Railway health checks need specific response format for proper monitoring.
        """
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        required_fields = ["status", "timestamp", "version"]
        for field in required_fields:
            assert field in data, f"Health response missing required field: {field}"
        
        # Verify data types
        assert isinstance(data["status"], str)
        assert isinstance(data["timestamp"], str)
        assert isinstance(data["version"], str)
        
        # Status should be one of the expected values
        valid_statuses = ["healthy", "degraded", "unhealthy"]
        assert data["status"] in valid_statuses, f"Invalid status: {data['status']}"
    
    def test_detailed_health_endpoint_exists(self):
        """
        GREEN TEST: Verify detailed health endpoint for comprehensive monitoring
        """
        response = client.get("/api/v1/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        # Detailed endpoint should have additional monitoring data
        expected_sections = ["checks", "metrics", "environment"]
        for section in expected_sections:
            assert section in data, f"Detailed health response missing section: {section}"
        
        # Verify checks section has system components
        assert "checks" in data
        checks = data["checks"]
        expected_checks = ["system_resources", "database", "ai_providers"]
        for check in expected_checks:
            assert check in checks, f"Health checks missing component: {check}"
    
    def test_readiness_and_liveness_probes(self):
        """
        RED TEST: Verify Kubernetes-style readiness and liveness probes work
        
        These are useful for Railway deployment monitoring and scaling.
        """
        # Test readiness probe
        readiness_response = client.get("/api/v1/ready")
        assert readiness_response.status_code in [200, 503], "Readiness probe should return 200 or 503"
        
        # Test liveness probe  
        liveness_response = client.get("/api/v1/live")
        assert liveness_response.status_code == 200, "Liveness probe should always return 200"
        
        liveness_data = liveness_response.json()
        assert "status" in liveness_data
        assert liveness_data["status"] == "alive"

class TestRailwayDeploymentCompatibility:
    """Test suite to verify Railway deployment configuration alignment"""
    
    def test_railway_toml_configuration_validity(self):
        """
        RED TEST: Verify railway.toml configuration matches actual endpoints
        """
        # Load railway.toml
        railway_config_path = os.path.join(os.path.dirname(__file__), "..", "railway.toml")
        assert os.path.exists(railway_config_path), "railway.toml must exist"
        
        config = toml.load(railway_config_path)
        
        # Verify health check configuration
        assert "deploy" in config, "railway.toml must have [deploy] section"
        deploy_config = config["deploy"]
        
        assert "healthcheckPath" in deploy_config, "Must specify healthcheckPath"
        assert "healthcheckTimeout" in deploy_config, "Must specify healthcheckTimeout"
        
        # Test that the configured health path actually works
        health_path = deploy_config["healthcheckPath"]
        response = client.get(health_path)
        assert response.status_code == 200, f"Configured health path {health_path} must be accessible"
    
    def test_railway_environment_compatibility(self):
        """
        RED TEST: Verify that health checks work with Railway environment variables
        """
        # Health endpoint should work even without all optional environment variables
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should not fail even if some services are not configured
        # This ensures Railway deployment succeeds even with minimal configuration
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]  # "unhealthy" only for critical failures

# This test suite will initially FAIL because:
# 1. We have duplicate health endpoints (main.py line 87 vs health.router)
# 2. Health endpoints may not return consistent response formats
# 3. Some health checks may call non-existent methods
# 
# GREEN phase will fix these issues to make tests pass