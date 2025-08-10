"""
Step 5: API Design Validation
==============================

Testing RESTful principles, endpoint design, and API consistency.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set
import pytest
from fastapi.testclient import TestClient


class TestAPIDesign:
    """Validate API design follows REST best practices"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from src.main import app
        return TestClient(app)
    
    def test_restful_url_patterns(self):
        """Verify URLs follow RESTful conventions"""
        violations = []
        
        # Check route definitions
        for py_file in Path('src/api/routes').rglob('*.py'):
            content = py_file.read_text()
            
            # Find route decorators
            route_pattern = r'@(?:app|router)\.(get|post|put|patch|delete)\(["\']([^"\']+)'
            routes = re.findall(route_pattern, content)
            
            for method, path in routes:
                # Check for RESTful patterns
                issues = []
                
                # No verbs in URLs (except standard endpoints)
                if re.search(r'/(?:get|create|update|delete|fetch|process)(?:_|/)', path.lower()):
                    issues.append("Verb in URL")
                
                # Use plural for collections
                if re.match(r'^/api/v\d+/[a-z]+$', path) and not path.endswith('s'):
                    if path.split('/')[-1] not in ['health', 'info', 'auth', 'login', 'logout']:
                        issues.append("Singular resource name for collection")
                
                # Proper HTTP methods
                if method == 'get' and 'create' in path:
                    issues.append("GET used for creation")
                if method == 'post' and any(word in path for word in ['get', 'fetch', 'list']):
                    issues.append("POST used for retrieval")
                
                if issues:
                    violations.append(f"{py_file.name}: {method.upper()} {path} - {', '.join(issues)}")
        
        assert len(violations) < 5, f"RESTful violations:\n" + "\n".join(violations[:10])
    
    def test_api_versioning(self):
        """Ensure API versioning is implemented"""
        api_files = list(Path('src/api').rglob('*.py'))
        
        has_versioning = False
        version_pattern = r'/api/v\d+'
        
        for py_file in api_files:
            content = py_file.read_text()
            if re.search(version_pattern, content):
                has_versioning = True
                break
        
        assert has_versioning, "No API versioning found (should use /api/v1/...)"
    
    def test_consistent_response_format(self):
        """Verify consistent response structure across endpoints"""
        response_patterns = []
        
        for py_file in Path('src/api/routes').rglob('*.py'):
            content = py_file.read_text()
            
            # Find return statements in route handlers
            return_pattern = r'return\s+(?:JSONResponse\()?(\{[^}]+\})'
            returns = re.findall(return_pattern, content)
            
            for ret in returns:
                # Check for consistent structure
                if 'data' in ret or 'error' in ret or 'status' in ret:
                    response_patterns.append('structured')
                else:
                    response_patterns.append('unstructured')
        
        # Most responses should follow same pattern
        if response_patterns:
            structured_ratio = response_patterns.count('structured') / len(response_patterns)
            assert structured_ratio > 0.7, f"Inconsistent response format (only {structured_ratio:.0%} structured)"
    
    def test_http_status_codes(self):
        """Verify appropriate HTTP status codes are used"""
        status_code_usage = {
            '200': [],  # OK
            '201': [],  # Created
            '204': [],  # No Content
            '400': [],  # Bad Request
            '401': [],  # Unauthorized
            '403': [],  # Forbidden
            '404': [],  # Not Found
            '422': [],  # Unprocessable Entity
            '500': [],  # Internal Server Error
        }
        
        for py_file in Path('src/api').rglob('*.py'):
            content = py_file.read_text()
            
            # Find status code usage
            for code in status_code_usage.keys():
                if f'status_code={code}' in content or f'status.HTTP_{code}' in content:
                    status_code_usage[code].append(py_file.name)
        
        # Should use variety of status codes appropriately
        codes_used = sum(1 for uses in status_code_usage.values() if uses)
        assert codes_used >= 4, f"Limited status code usage (only {codes_used} different codes)"
        
        # 201 should be used for creation
        assert len(status_code_usage['201']) > 0 or len(status_code_usage['204']) > 0, \
            "No 201/204 status codes for creation/deletion"
    
    def test_pagination_implementation(self):
        """Check if pagination is implemented for list endpoints"""
        pagination_params = ['limit', 'offset', 'page', 'per_page', 'cursor']
        
        has_pagination = False
        for py_file in Path('src/api/routes').rglob('*.py'):
            content = py_file.read_text()
            
            # Check for pagination parameters
            for param in pagination_params:
                if param in content:
                    has_pagination = True
                    break
        
        # Should have some form of pagination
        assert has_pagination, "No pagination implementation found"
    
    def test_filtering_and_sorting(self):
        """Verify filtering and sorting capabilities"""
        filter_patterns = ['filter', 'search', 'query', 'sort', 'order_by']
        
        has_filtering = False
        for py_file in Path('src/api/routes').rglob('*.py'):
            content = py_file.read_text()
            
            for pattern in filter_patterns:
                if pattern in content.lower():
                    has_filtering = True
                    break
        
        # Should support some filtering/sorting
        assert has_filtering, "No filtering or sorting capabilities found"
    
    def test_request_validation(self):
        """Ensure request validation is in place"""
        validation_patterns = [
            'BaseModel',
            'Field(',
            'validator',
            'Query(',
            'Body(',
            'Path(',
        ]
        
        validation_count = 0
        route_count = 0
        
        for py_file in Path('src/api/routes').rglob('*.py'):
            content = py_file.read_text()
            
            # Count routes
            route_count += len(re.findall(r'@(?:app|router)\.(?:get|post|put|patch|delete)', content))
            
            # Count validation usage
            for pattern in validation_patterns:
                validation_count += content.count(pattern)
        
        # Should have validation for most routes
        if route_count > 0:
            validation_ratio = validation_count / route_count
            assert validation_ratio > 0.5, f"Insufficient validation (ratio: {validation_ratio:.2f})"
    
    def test_api_documentation(self, client):
        """Verify API documentation is available"""
        # Check for OpenAPI/Swagger documentation
        response = client.get("/docs")
        
        # In production, docs might be disabled
        if response.status_code == 200:
            assert "swagger" in response.text.lower() or "openapi" in response.text.lower(), \
                "API documentation not properly configured"
        
        # Check for OpenAPI schema
        response = client.get("/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            assert "openapi" in schema, "OpenAPI schema missing"
            assert "paths" in schema, "No paths in OpenAPI schema"
            assert len(schema["paths"]) > 0, "No endpoints documented"
    
    def test_cors_configuration(self):
        """Verify CORS is properly configured"""
        main_file = Path('src/main.py')
        content = main_file.read_text()
        
        # Check for CORS middleware
        assert 'CORSMiddleware' in content, "CORS middleware not configured"
        
        # Check for proper configuration
        cors_config_found = any([
            'allow_origins' in content,
            'allow_credentials' in content,
            'allow_methods' in content,
            'allow_headers' in content,
        ])
        
        assert cors_config_found, "CORS not properly configured"
    
    def test_rate_limiting(self):
        """Verify rate limiting is implemented"""
        main_file = Path('src/main.py')
        content = main_file.read_text()
        
        # Check for rate limiting
        rate_limit_found = any([
            'RateLimiter' in content,
            'slowapi' in content,
            'rate_limit' in content,
            'throttle' in content,
        ])
        
        assert rate_limit_found, "No rate limiting implementation found"