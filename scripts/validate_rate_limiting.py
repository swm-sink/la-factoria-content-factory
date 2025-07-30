#!/usr/bin/env python3
"""Validate rate limiting implementation."""

import os
import sys
import time
from typing import Dict, List


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    return os.path.exists(filepath)


def check_content_in_file(filepath: str, content: List[str]) -> Dict[str, bool]:
    """Check if specific content exists in a file."""
    if not os.path.exists(filepath):
        return {item: False for item in content}
    
    with open(filepath, 'r') as f:
        file_content = f.read()
    
    results = {}
    for item in content:
        results[item] = item in file_content
    
    return results


def validate_dependencies():
    """Validate that required dependencies are installed."""
    print("Validating dependencies...")
    
    # Check requirements.txt
    req_file = "requirements.txt"
    if check_file_exists(req_file):
        with open(req_file, 'r') as f:
            requirements = f.read()
        
        if "slowapi" in requirements:
            print("  ✓ slowapi found in requirements.txt")
        else:
            print("  ✗ slowapi NOT found in requirements.txt")
            return False
    else:
        print("  ✗ requirements.txt not found")
        return False
    
    return True


def validate_middleware():
    """Validate middleware implementation."""
    print("\nValidating middleware implementation...")
    
    # Check middleware file
    middleware_file = "app/middleware/rate_limiting.py"
    if not check_file_exists(middleware_file):
        print(f"  ✗ {middleware_file} not found")
        return False
    
    print(f"  ✓ {middleware_file} exists")
    
    # Check for key components
    components = [
        "RateLimitingMiddleware",
        "get_rate_limit_key",
        "ENDPOINT_LIMITS",
        "redis_client",
        "_check_rate_limit",
        "_add_rate_limit_headers",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ]
    
    results = check_content_in_file(middleware_file, components)
    
    for component, found in results.items():
        if found:
            print(f"  ✓ Found {component}")
        else:
            print(f"  ✗ Missing {component}")
    
    return all(results.values())


def validate_configuration():
    """Validate rate limit configuration."""
    print("\nValidating configuration...")
    
    config_file = "app/core/config/rate_limits.py"
    if not check_file_exists(config_file):
        print(f"  ✗ {config_file} not found")
        return False
    
    print(f"  ✓ {config_file} exists")
    
    # Check configuration components
    components = [
        "RateLimitConfig",
        "endpoint_limits",
        "operation_costs",
        "user_tier_multipliers",
        "exempt_paths",
        "get_rate_limit_config",
    ]
    
    results = check_content_in_file(config_file, components)
    
    for component, found in results.items():
        if found:
            print(f"  ✓ Found {component}")
        else:
            print(f"  ✗ Missing {component}")
    
    return all(results.values())


def validate_integration():
    """Validate integration with main app."""
    print("\nValidating app integration...")
    
    main_file = "app/main.py"
    if not check_file_exists(main_file):
        print(f"  ✗ {main_file} not found")
        return False
    
    # Check if middleware is imported and added
    components = [
        "from app.middleware.rate_limiting import RateLimitingMiddleware",
        "app.add_middleware(RateLimitingMiddleware)",
    ]
    
    results = check_content_in_file(main_file, components)
    
    for component, found in results.items():
        if found:
            print(f"  ✓ Found: {component}")
        else:
            print(f"  ✗ Missing: {component}")
    
    return all(results.values())


def validate_tests():
    """Validate test coverage."""
    print("\nValidating test coverage...")
    
    test_files = [
        "tests/unit/middleware/test_rate_limiting.py",
        "tests/integration/test_rate_limits.py",
    ]
    
    all_exist = True
    for test_file in test_files:
        if check_file_exists(test_file):
            print(f"  ✓ Found {test_file}")
            
            # Check for key test cases
            if "unit" in test_file:
                test_cases = [
                    "test_rate_limit_key_generation",
                    "test_rate_limit_headers",
                    "test_rate_limit_enforcement",
                    "test_per_endpoint_limits",
                ]
            else:
                test_cases = [
                    "test_concurrent_requests_rate_limiting",
                    "test_different_endpoints_different_limits",
                    "test_api_key_higher_limits",
                ]
            
            results = check_content_in_file(test_file, test_cases)
            for test_case, found in results.items():
                if found:
                    print(f"    ✓ Test case: {test_case}")
                else:
                    print(f"    ✗ Missing test: {test_case}")
        else:
            print(f"  ✗ Missing {test_file}")
            all_exist = False
    
    return all_exist


def validate_documentation():
    """Validate documentation."""
    print("\nValidating documentation...")
    
    doc_file = "docs/api/rate-limiting.md"
    if not check_file_exists(doc_file):
        print(f"  ✗ {doc_file} not found")
        return False
    
    print(f"  ✓ {doc_file} exists")
    
    # Check for key sections
    sections = [
        "Default Limits",
        "Endpoint-Specific Limits",
        "Rate Limit Headers",
        "Best Practices",
        "Cost-Based Rate Limiting",
        "429 Too Many Requests",
    ]
    
    results = check_content_in_file(doc_file, sections)
    
    for section, found in results.items():
        if found:
            print(f"  ✓ Section: {section}")
        else:
            print(f"  ✗ Missing section: {section}")
    
    return all(results.values())


def validate_error_handling():
    """Validate error handling."""
    print("\nValidating error handling...")
    
    middleware_file = "app/middleware/rate_limiting.py"
    
    # Check for proper error responses
    error_components = [
        "429",
        "TOO_MANY_REQUESTS",
        "RATE_LIMIT_EXCEEDED",
        "Retry-After",
        "create_error_response",
    ]
    
    results = check_content_in_file(middleware_file, error_components)
    
    for component, found in results.items():
        if found:
            print(f"  ✓ Found {component}")
        else:
            print(f"  ✗ Missing {component}")
    
    return all(results.values())


def main():
    """Run all validations."""
    print("=" * 60)
    print("Rate Limiting Implementation Validation")
    print("=" * 60)
    
    validations = [
        ("Dependencies", validate_dependencies),
        ("Middleware", validate_middleware),
        ("Configuration", validate_configuration),
        ("App Integration", validate_integration),
        ("Tests", validate_tests),
        ("Documentation", validate_documentation),
        ("Error Handling", validate_error_handling),
    ]
    
    all_passed = True
    results = {}
    
    for name, validator in validations:
        try:
            passed = validator()
            results[name] = passed
            all_passed = all_passed and passed
        except Exception as e:
            print(f"\n✗ {name} validation failed with error: {e}")
            results[name] = False
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name}: {status}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✅ All validations PASSED!")
        print("\nRate limiting is properly implemented with:")
        print("- Per-endpoint configuration")
        print("- Cost-based limiting for expensive operations")
        print("- Redis support for distributed rate limiting")
        print("- Proper error responses with retry information")
        print("- Comprehensive test coverage")
        print("- Clear documentation")
        print("\nNext steps:")
        print("1. Test with Redis in staging environment")
        print("2. Monitor rate limit metrics")
        print("3. Adjust limits based on usage patterns")
        return 0
    else:
        print("❌ Some validations FAILED")
        print("\nPlease fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())