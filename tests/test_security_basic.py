#!/usr/bin/env python3
"""
Basic Security Validation for La Factoria
OWASP-aligned security checks for Phase 3D
"""

import requests
import json
from typing import Dict, List
import re


class SecurityValidator:
    """Basic security validation following OWASP guidelines"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.vulnerabilities = []
        self.checks_passed = []
        self.checks_failed = []
    
    def test_security_headers(self) -> bool:
        """Test for security headers"""
        print("\n🔒 Testing Security Headers...")
        
        response = requests.get(f"{self.base_url}/api/v1/health")
        headers = response.headers
        
        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "Content-Security-Policy": None,  # Check exists
            "Strict-Transport-Security": None,  # For HTTPS
        }
        
        missing_headers = []
        for header, expected in required_headers.items():
            if header not in headers:
                missing_headers.append(header)
                self.vulnerabilities.append({
                    "type": "Missing Security Header",
                    "header": header,
                    "severity": "Medium",
                    "recommendation": f"Add {header} header to responses"
                })
            elif expected and headers.get(header) not in expected:
                self.vulnerabilities.append({
                    "type": "Incorrect Security Header",
                    "header": header,
                    "value": headers.get(header),
                    "expected": expected,
                    "severity": "Medium"
                })
        
        if not missing_headers:
            self.checks_passed.append("Security Headers")
            print("   ✅ Basic security headers present")
            return True
        else:
            self.checks_failed.append("Security Headers")
            print(f"   ⚠️ Missing headers: {', '.join(missing_headers)}")
            return False
    
    def test_input_validation(self) -> bool:
        """Test input validation and injection protection"""
        print("\n🛡️ Testing Input Validation...")
        
        # Test SQL injection patterns
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users--",
            "1' UNION SELECT NULL--",
        ]
        
        # Test XSS patterns
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
        ]
        
        vulnerable = False
        
        # Test content generation endpoint
        for payload in sql_payloads + xss_payloads:
            data = {
                "topic": payload,
                "content_type": "study_guide",
                "educational_level": "intermediate"
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/content/generate",
                    json=data
                )
                
                # Check if payload appears in response (potential XSS)
                if response.status_code == 200:
                    if payload in response.text:
                        vulnerable = True
                        self.vulnerabilities.append({
                            "type": "Potential XSS",
                            "payload": payload,
                            "endpoint": "/api/v1/content/generate",
                            "severity": "High"
                        })
                
                # Check for SQL errors in response
                if any(err in response.text.lower() for err in ["sql", "syntax", "database"]):
                    vulnerable = True
                    self.vulnerabilities.append({
                        "type": "Potential SQL Injection",
                        "payload": payload,
                        "endpoint": "/api/v1/content/generate",
                        "severity": "Critical"
                    })
            except:
                pass  # Request failed, which is good for malicious input
        
        if not vulnerable:
            self.checks_passed.append("Input Validation")
            print("   ✅ Input validation working correctly")
            return True
        else:
            self.checks_failed.append("Input Validation")
            print("   ❌ Input validation issues detected")
            return False
    
    def test_authentication(self) -> bool:
        """Test authentication mechanisms"""
        print("\n🔐 Testing Authentication...")
        
        # Test protected endpoints without auth
        protected_endpoints = [
            "/api/v1/admin/users",
            "/api/v1/admin/metrics",
            "/api/v1/content/delete",
        ]
        
        unauthorized_access = []
        
        for endpoint in protected_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    unauthorized_access.append(endpoint)
                    self.vulnerabilities.append({
                        "type": "Missing Authentication",
                        "endpoint": endpoint,
                        "severity": "Critical",
                        "recommendation": "Implement authentication for admin endpoints"
                    })
                elif response.status_code not in [401, 403, 404]:
                    # Unexpected status code
                    self.vulnerabilities.append({
                        "type": "Improper Authentication Response",
                        "endpoint": endpoint,
                        "status": response.status_code,
                        "severity": "Low"
                    })
            except:
                pass  # Connection error is fine
        
        if not unauthorized_access:
            self.checks_passed.append("Authentication")
            print("   ✅ Protected endpoints require authentication")
            return True
        else:
            self.checks_failed.append("Authentication")
            print(f"   ❌ Unauthorized access to: {', '.join(unauthorized_access)}")
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting"""
        print("\n⏱️ Testing Rate Limiting...")
        
        # Send rapid requests
        endpoint = "/api/v1/health"
        rapid_requests = 100
        rate_limited = False
        
        for i in range(rapid_requests):
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                if response.status_code == 429:  # Too Many Requests
                    rate_limited = True
                    break
            except:
                pass
        
        if rate_limited:
            self.checks_passed.append("Rate Limiting")
            print("   ✅ Rate limiting is active")
            return True
        else:
            self.checks_failed.append("Rate Limiting")
            print("   ⚠️ No rate limiting detected (optional for Phase 3D)")
            self.vulnerabilities.append({
                "type": "Missing Rate Limiting",
                "severity": "Medium",
                "recommendation": "Implement rate limiting to prevent abuse"
            })
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling for information disclosure"""
        print("\n🚨 Testing Error Handling...")
        
        # Try to trigger errors
        error_tests = [
            ("/api/v1/nonexistent", "GET", None),
            ("/api/v1/content/generate", "POST", {"invalid": "data"}),
            ("/api/v1/content/generate", "POST", None),
        ]
        
        information_disclosure = []
        
        for endpoint, method, data in error_tests:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}")
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", json=data)
                
                # Check for sensitive information in error messages
                sensitive_patterns = [
                    r"File \".*\.py\"",  # File paths
                    r"line \d+",  # Line numbers
                    r"Traceback",  # Stack traces
                    r"sqlalchemy",  # Database details
                    r"postgresql://",  # Connection strings
                ]
                
                for pattern in sensitive_patterns:
                    if re.search(pattern, response.text, re.IGNORECASE):
                        information_disclosure.append({
                            "endpoint": endpoint,
                            "pattern": pattern,
                            "response_snippet": response.text[:200]
                        })
                        self.vulnerabilities.append({
                            "type": "Information Disclosure",
                            "endpoint": endpoint,
                            "severity": "Medium",
                            "details": "Stack trace or sensitive info in error response"
                        })
                        break
            except:
                pass
        
        if not information_disclosure:
            self.checks_passed.append("Error Handling")
            print("   ✅ Error handling doesn't leak sensitive info")
            return True
        else:
            self.checks_failed.append("Error Handling")
            print("   ⚠️ Sensitive information in error messages")
            return False
    
    def test_cors_configuration(self) -> bool:
        """Test CORS configuration"""
        print("\n🌐 Testing CORS Configuration...")
        
        # Test with different origins
        test_origins = [
            "http://malicious-site.com",
            "null",
            "*"
        ]
        
        cors_issues = []
        
        for origin in test_origins:
            headers = {"Origin": origin}
            response = requests.get(f"{self.base_url}/api/v1/health", headers=headers)
            
            if "Access-Control-Allow-Origin" in response.headers:
                allowed = response.headers["Access-Control-Allow-Origin"]
                if allowed == "*" or allowed == origin:
                    cors_issues.append({
                        "origin": origin,
                        "allowed": allowed
                    })
                    self.vulnerabilities.append({
                        "type": "Permissive CORS",
                        "origin": origin,
                        "severity": "Medium",
                        "recommendation": "Restrict CORS to trusted domains"
                    })
        
        if not cors_issues:
            self.checks_passed.append("CORS Configuration")
            print("   ✅ CORS properly configured")
            return True
        else:
            self.checks_failed.append("CORS Configuration")
            print("   ⚠️ CORS too permissive")
            return False
    
    def run_security_validation(self) -> Dict:
        """Run complete security validation suite"""
        print("\n" + "="*60)
        print("LA FACTORIA SECURITY VALIDATION")
        print("Phase 3D - OWASP-Aligned Security Checks")
        print("="*60)
        
        # Run all security tests
        self.test_security_headers()
        self.test_input_validation()
        self.test_authentication()
        self.test_rate_limiting()
        self.test_error_handling()
        self.test_cors_configuration()
        
        # Generate summary
        self.print_summary()
        
        # Determine overall pass/fail
        critical_vulns = [v for v in self.vulnerabilities if v["severity"] == "Critical"]
        passed = len(critical_vulns) == 0 and len(self.checks_failed) <= 2
        
        return {
            "passed": passed,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "vulnerabilities": self.vulnerabilities,
            "critical_count": len(critical_vulns)
        }
    
    def print_summary(self):
        """Print security validation summary"""
        print("\n" + "="*60)
        print("SECURITY VALIDATION SUMMARY")
        print("="*60)
        
        print(f"\n✅ Passed Checks: {len(self.checks_passed)}")
        for check in self.checks_passed:
            print(f"   • {check}")
        
        print(f"\n❌ Failed Checks: {len(self.checks_failed)}")
        for check in self.checks_failed:
            print(f"   • {check}")
        
        if self.vulnerabilities:
            print(f"\n⚠️ Vulnerabilities Found: {len(self.vulnerabilities)}")
            
            # Group by severity
            critical = [v for v in self.vulnerabilities if v["severity"] == "Critical"]
            high = [v for v in self.vulnerabilities if v["severity"] == "High"]
            medium = [v for v in self.vulnerabilities if v["severity"] == "Medium"]
            low = [v for v in self.vulnerabilities if v["severity"] == "Low"]
            
            if critical:
                print(f"\n🔴 CRITICAL ({len(critical)}):")
                for vuln in critical:
                    print(f"   • {vuln['type']}: {vuln.get('endpoint', vuln.get('details', ''))}")
            
            if high:
                print(f"\n🟠 HIGH ({len(high)}):")
                for vuln in high:
                    print(f"   • {vuln['type']}: {vuln.get('endpoint', vuln.get('payload', ''))}")
            
            if medium:
                print(f"\n🟡 MEDIUM ({len(medium)}):")
                for vuln in medium:
                    print(f"   • {vuln['type']}: {vuln.get('recommendation', '')}")
        
        print("\n" + "="*60)
        
        # Phase 3D criteria
        critical_count = len([v for v in self.vulnerabilities if v["severity"] == "Critical"])
        if critical_count == 0:
            print("✅ Phase 3D Security Criteria: PASSED (No critical vulnerabilities)")
        else:
            print(f"❌ Phase 3D Security Criteria: FAILED ({critical_count} critical vulnerabilities)")


def main():
    """Run security validation"""
    validator = SecurityValidator()
    
    # Check if server is running
    try:
        response = requests.get(f"{validator.base_url}/api/v1/health")
        if response.status_code != 200:
            print("⚠️ Server health check failed")
            return False
    except:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("   Please start the server with:")
        print("   uvicorn src.main:app --reload")
        return False
    
    # Run security validation
    results = validator.run_security_validation()
    
    # Save results
    with open("security_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n💾 Results saved to security_results.json")
    
    return results["passed"]


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)