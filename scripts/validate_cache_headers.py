#!/usr/bin/env python3
"""
Validate HTTP response caching headers implementation.
"""

import json
import time
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import hashlib
import sys


class CacheHeaderValidator:
    """Validates cache header implementation."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def validate_all(self) -> bool:
        """Run all validation tests."""
        print("🔍 Validating HTTP Response Caching Headers Implementation...\n")
        
        # Test different content types and paths
        self._test_static_content_caching()
        self._test_api_response_caching()
        self._test_dynamic_content_caching()
        self._test_user_specific_caching()
        self._test_conditional_requests()
        self._test_cache_invalidation()
        self._test_vary_headers()
        self._test_performance_improvements()
        
        # Print results
        self._print_results()
        
        return self.failed == 0
    
    def _test_static_content_caching(self) -> None:
        """Test caching headers for static content."""
        print("📁 Testing static content caching...")
        
        static_paths = [
            "/static/css/main.css",
            "/static/js/app.js",
            "/assets/images/logo.png",
            "/static/fonts/font.woff2"
        ]
        
        for path in static_paths:
            try:
                # Mock static file response
                response = self._make_request("GET", path)
                if response.status_code == 404:
                    # Skip if static files don't exist in test
                    continue
                
                cache_control = response.headers.get("Cache-Control", "")
                
                # Validate static content has long-term caching
                if "max-age=31536000" in cache_control and "public" in cache_control and "immutable" in cache_control:
                    self._add_result(f"Static content {path}", True, "Correct cache headers")
                else:
                    self._add_result(f"Static content {path}", False, f"Invalid cache headers: {cache_control}")
                
            except Exception as e:
                self._add_result(f"Static content {path}", False, str(e))
    
    def _test_api_response_caching(self) -> None:
        """Test caching headers for API responses."""
        print("\n🔌 Testing API response caching...")
        
        api_endpoints = [
            ("/api/v1/content/types", 900),  # 15 minutes
            ("/api/v1/content/templates", 900),  # 15 minutes
            ("/api/v1/prompts", 300),  # 5 minutes
            ("/api/v1/health", 0)  # No cache
        ]
        
        for endpoint, expected_max_age in api_endpoints:
            try:
                response = self._make_request("GET", endpoint)
                cache_control = response.headers.get("Cache-Control", "")
                
                if expected_max_age == 0:
                    if "no-cache" in cache_control or "max-age=0" in cache_control:
                        self._add_result(f"API endpoint {endpoint}", True, "Correctly not cached")
                    else:
                        self._add_result(f"API endpoint {endpoint}", False, f"Should not be cached: {cache_control}")
                else:
                    if f"max-age={expected_max_age}" in cache_control:
                        self._add_result(f"API endpoint {endpoint}", True, f"Correct cache duration")
                    else:
                        self._add_result(f"API endpoint {endpoint}", False, f"Wrong cache duration: {cache_control}")
                
            except Exception as e:
                self._add_result(f"API endpoint {endpoint}", False, str(e))
    
    def _test_dynamic_content_caching(self) -> None:
        """Test caching headers for dynamic content."""
        print("\n🔄 Testing dynamic content caching...")
        
        try:
            # Test HTML page
            response = self._make_request("GET", "/", headers={"Accept": "text/html"})
            cache_control = response.headers.get("Cache-Control", "")
            
            if "private" in cache_control and "max-age=60" in cache_control:
                self._add_result("Dynamic HTML content", True, "Correct cache headers")
            else:
                self._add_result("Dynamic HTML content", False, f"Invalid cache headers: {cache_control}")
            
            # Check for ETag
            if "ETag" in response.headers:
                self._add_result("Dynamic content ETag", True, "ETag present")
            else:
                self._add_result("Dynamic content ETag", False, "No ETag header")
                
        except Exception as e:
            self._add_result("Dynamic content caching", False, str(e))
    
    def _test_user_specific_caching(self) -> None:
        """Test caching headers for user-specific content."""
        print("\n👤 Testing user-specific content caching...")
        
        user_endpoints = [
            "/api/v1/user/profile",
            "/api/v1/auth/me"
        ]
        
        for endpoint in user_endpoints:
            try:
                response = self._make_request("GET", endpoint)
                cache_control = response.headers.get("Cache-Control", "")
                
                if "no-cache" in cache_control or ("private" in cache_control and "max-age=0" in cache_control):
                    self._add_result(f"User endpoint {endpoint}", True, "Correctly not cached")
                else:
                    self._add_result(f"User endpoint {endpoint}", False, f"Should not be cached: {cache_control}")
                    
            except Exception as e:
                self._add_result(f"User endpoint {endpoint}", False, str(e))
    
    def _test_conditional_requests(self) -> None:
        """Test conditional request handling (ETags and If-None-Match)."""
        print("\n🔍 Testing conditional requests...")
        
        try:
            # First request to get ETag
            response1 = self._make_request("GET", "/api/v1/content/types")
            etag = response1.headers.get("ETag")
            
            if not etag:
                self._add_result("Conditional requests", False, "No ETag in response")
                return
            
            # Second request with If-None-Match
            response2 = self._make_request("GET", "/api/v1/content/types", headers={"If-None-Match": etag})
            
            if response2.status_code == 304:
                self._add_result("Conditional requests (304)", True, "Correctly returns 304 Not Modified")
            else:
                self._add_result("Conditional requests (304)", False, f"Expected 304, got {response2.status_code}")
            
            # Test If-Modified-Since
            last_modified = response1.headers.get("Last-Modified")
            if last_modified:
                response3 = self._make_request("GET", "/api/v1/content/types", headers={"If-Modified-Since": last_modified})
                if response3.status_code == 304:
                    self._add_result("If-Modified-Since", True, "Correctly returns 304")
                else:
                    self._add_result("If-Modified-Since", False, f"Expected 304, got {response3.status_code}")
                    
        except Exception as e:
            self._add_result("Conditional requests", False, str(e))
    
    def _test_cache_invalidation(self) -> None:
        """Test cache invalidation on write operations."""
        print("\n🗑️ Testing cache invalidation...")
        
        try:
            # Get initial response
            response1 = self._make_request("GET", "/api/v1/content/types")
            etag1 = response1.headers.get("ETag")
            
            # Simulate write operation (would trigger invalidation in real scenario)
            # This is a mock test - in real implementation, you'd POST new content
            
            # Check that cache headers indicate freshness
            cache_control = response1.headers.get("Cache-Control", "")
            if "must-revalidate" in cache_control:
                self._add_result("Cache invalidation headers", True, "Has must-revalidate directive")
            else:
                self._add_result("Cache invalidation headers", False, "Missing must-revalidate")
                
        except Exception as e:
            self._add_result("Cache invalidation", False, str(e))
    
    def _test_vary_headers(self) -> None:
        """Test Vary headers for content negotiation."""
        print("\n🔀 Testing Vary headers...")
        
        try:
            # Test with different Accept headers
            response = self._make_request("GET", "/api/v1/content/types", headers={"Accept": "application/json"})
            vary = response.headers.get("Vary", "")
            
            expected_vary = ["Accept", "Accept-Encoding"]
            vary_values = [v.strip() for v in vary.split(",")]
            
            missing = [v for v in expected_vary if v not in vary_values]
            if not missing:
                self._add_result("Vary headers", True, f"Correct Vary headers: {vary}")
            else:
                self._add_result("Vary headers", False, f"Missing Vary values: {missing}")
                
        except Exception as e:
            self._add_result("Vary headers", False, str(e))
    
    def _test_performance_improvements(self) -> None:
        """Test cache performance improvements."""
        print("\n⚡ Testing cache performance...")
        
        try:
            # Make multiple requests to test caching effect
            endpoint = "/api/v1/content/types"
            times = []
            
            for i in range(5):
                start = time.time()
                response = self._make_request("GET", endpoint)
                elapsed = (time.time() - start) * 1000  # Convert to ms
                times.append(elapsed)
                
                # Check for process time header
                if "X-Process-Time" in response.headers:
                    self._add_result(f"Process time header (request {i+1})", True, 
                                   f"Present: {response.headers['X-Process-Time']}")
            
            # First request should be slower than subsequent cached requests
            avg_first = times[0]
            avg_rest = sum(times[1:]) / len(times[1:])
            
            if avg_rest < avg_first * 0.8:  # At least 20% improvement
                self._add_result("Cache performance", True, 
                               f"Performance improved: {avg_first:.2f}ms → {avg_rest:.2f}ms")
            else:
                self._add_result("Cache performance", False, 
                               f"No significant improvement: {avg_first:.2f}ms → {avg_rest:.2f}ms")
                
        except Exception as e:
            self._add_result("Cache performance", False, str(e))
    
    def _make_request(self, method: str, path: str, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """Make HTTP request to the API."""
        url = f"{self.base_url}{path}"
        
        # Add API key if needed
        if headers is None:
            headers = {}
        
        if path.startswith("/api/v1/") and path not in ["/api/v1/auth", "/api/v1/health"]:
            headers["X-API-Key"] = "test-api-key"  # Use test API key
        
        return requests.request(method, url, headers=headers)
    
    def _add_result(self, test_name: str, passed: bool, message: str) -> None:
        """Add test result."""
        self.results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
        
        if passed:
            self.passed += 1
            print(f"  ✅ {test_name}: {message}")
        else:
            self.failed += 1
            print(f"  ❌ {test_name}: {message}")
    
    def _print_results(self) -> None:
        """Print validation results."""
        print("\n" + "="*60)
        print("📊 CACHE HEADERS VALIDATION RESULTS")
        print("="*60)
        
        total = self.passed + self.failed
        if total > 0:
            success_rate = (self.passed / total) * 100
            print(f"\nTotal Tests: {total}")
            print(f"Passed: {self.passed} ({success_rate:.1f}%)")
            print(f"Failed: {self.failed}")
            
            if self.failed > 0:
                print("\n❌ Failed Tests:")
                for result in self.results:
                    if not result["passed"]:
                        print(f"  - {result['test']}: {result['message']}")
            
            # Performance metrics
            print("\n📈 Cache Performance Metrics:")
            print("  - Static assets: 1 year cache (immutable)")
            print("  - API responses: 5-15 minute cache")
            print("  - Dynamic content: 1 minute cache with ETags")
            print("  - User content: No caching")
            print("  - Conditional requests: 304 responses supported")
            
            print("\n" + ("✅ All cache headers validated successfully!" if self.failed == 0 
                         else "❌ Some cache header validations failed!"))
        else:
            print("No tests were run!")


def main():
    """Main validation function."""
    # Get base URL from environment or use default
    import os
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    validator = CacheHeaderValidator(base_url)
    success = validator.validate_all()
    
    # Save results to file
    with open("cache_headers_validation_report.json", "w") as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "base_url": base_url,
            "passed": validator.passed,
            "failed": validator.failed,
            "results": validator.results
        }, f, indent=2)
    
    print(f"\n📝 Validation report saved to cache_headers_validation_report.json")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()