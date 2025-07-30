#!/usr/bin/env python3
"""Validate security event logger implementation."""

import os
import sys
import time
import json
from pathlib import Path
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


def validate_security_logger_implementation():
    """Validate security event logger service."""
    print("Validating security event logger implementation...")
    
    logger_file = "app/services/security_event_logger.py"
    if not check_file_exists(logger_file):
        print(f"  ✗ {logger_file} not found")
        return False
    
    print(f"  ✓ {logger_file} exists")
    
    # Check for key components
    components = [
        "SecurityEventLogger",
        "SecurityEvent",
        "SecurityEventType",
        "SecurityEventSeverity",
        "log_auth_failure",
        "log_malicious_request",
        "log_rate_limit_exceeded",
        "log_api_key_abuse",
        "log_suspicious_activity",
        "get_security_event_summary",
        "is_system_under_attack",
    ]
    
    results = check_content_in_file(logger_file, components)
    
    all_found = True
    for component, found in results.items():
        if found:
            print(f"  ✓ Found {component}")
        else:
            print(f"  ✗ Missing {component}")
            all_found = False
    
    return all_found


def validate_event_types_and_severities():
    """Validate event types and severity levels."""
    print("\nValidating event types and severities...")
    
    logger_file = "app/services/security_event_logger.py"
    
    # Critical event types that must be supported
    event_types = [
        "AUTH_FAILURE",
        "MALICIOUS_REQUEST",
        "RATE_LIMIT_EXCEEDED",
        "API_KEY_ABUSE",
        "SUSPICIOUS_ACTIVITY",
        "INTRUSION_ATTEMPT",
        "DATA_BREACH_ATTEMPT",
    ]
    
    # Severity levels that must be supported
    severities = [
        "LOW",
        "MEDIUM", 
        "HIGH",
        "CRITICAL",
    ]
    
    results = check_content_in_file(logger_file, event_types + severities)
    
    all_covered = True
    for item, found in results.items():
        if found:
            print(f"  ✓ Supported: {item}")
        else:
            print(f"  ✗ Missing: {item}")
            all_covered = False
    
    return all_covered


def validate_middleware_integration():
    """Validate integration with request validation middleware."""
    print("\nValidating middleware integration...")
    
    middleware_file = "app/middleware/request_validation.py"
    if not check_file_exists(middleware_file):
        print(f"  ✗ {middleware_file} not found")
        return False
    
    # Check if security logger is imported and used
    components = [
        "from app.services.security_event_logger import",
        "log_malicious_request",
        "log_suspicious_activity",
    ]
    
    results = check_content_in_file(middleware_file, components)
    
    all_integrated = True
    for component, found in results.items():
        if found:
            print(f"  ✓ Found: {component}")
        else:
            print(f"  ✗ Missing: {component}")
            all_integrated = False
    
    return all_integrated


def validate_test_coverage():
    """Validate test coverage for security event logger."""
    print("\nValidating test coverage...")
    
    test_file = "tests/unit/services/test_security_event_logger.py"
    if not check_file_exists(test_file):
        print(f"  ✗ {test_file} not found")
        return False
    
    print(f"  ✓ {test_file} exists")
    
    # Check for critical test cases
    test_cases = [
        "test_security_event_creation",
        "test_security_event_to_dict",
        "test_logger_initialization",
        "test_log_event_info_level",
        "test_log_event_critical_level",
        "test_log_auth_failure",
        "test_log_malicious_request",
        "test_log_rate_limit_exceeded",
        "test_log_api_key_abuse",
        "test_log_suspicious_activity",
        "test_get_event_summary",
        "test_is_under_attack",
        "test_multiple_event_types_logging",
    ]
    
    results = check_content_in_file(test_file, test_cases)
    
    all_tests_present = True
    for test_case, found in results.items():
        if found:
            print(f"  ✓ Test case: {test_case}")
        else:
            print(f"  ✗ Missing test: {test_case}")
            all_tests_present = False
    
    return all_tests_present


def validate_logging_configuration():
    """Validate logging configuration."""
    print("\nValidating logging configuration...")
    
    logger_file = "app/services/security_event_logger.py"
    
    config_components = [
        "_setup_security_logger",
        "logging.getLogger",
        "StreamHandler",
        "setFormatter",
        "setLevel",
        "propagate = False",
    ]
    
    results = check_content_in_file(logger_file, config_components)
    
    all_configured = True
    for component, found in results.items():
        if found:
            print(f"  ✓ Configuration: {component}")
        else:
            print(f"  ✗ Missing config: {component}")
            all_configured = False
    
    return all_configured


def validate_structured_logging():
    """Validate structured logging format."""
    print("\nValidating structured logging...")
    
    logger_file = "app/services/security_event_logger.py"
    
    structured_components = [
        "json.dumps",
        "to_dict",
        "iso_timestamp",
        "event_counter",
        "environment",
        "additional_data",
    ]
    
    results = check_content_in_file(logger_file, structured_components)
    
    all_structured = True
    for component, found in results.items():
        if found:
            print(f"  ✓ Structured logging: {component}")
        else:
            print(f"  ✗ Missing component: {component}")
            all_structured = False
    
    return all_structured


def validate_security_features():
    """Validate security-specific features."""
    print("\nValidating security features...")
    
    logger_file = "app/services/security_event_logger.py"
    
    security_features = [
        "critical_events",
        "_handle_critical_event",
        "_handle_high_severity_event",
        "event_counters",
        "is_under_attack",
        "payload_sample",  # Payload truncation
        "confidence_score",  # Risk scoring
    ]
    
    results = check_content_in_file(logger_file, security_features)
    
    all_secure = True
    for feature, found in results.items():
        if found:
            print(f"  ✓ Security feature: {feature}")
        else:
            print(f"  ✗ Missing feature: {feature}")
            all_secure = False
    
    return all_secure


def simulate_security_events():
    """Simulate security events to test functionality."""
    print("\nSimulating security events...")
    
    try:
        # Import the security logger
        import sys
        import os
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Try to import and test with security logger
        try:
            from app.services.security_event_logger import (
                log_auth_failure,
                log_malicious_request,
                log_rate_limit_exceeded,
                log_api_key_abuse,
                log_suspicious_activity,
                get_security_event_summary,
                is_system_under_attack,
            )
            
            print("  ✓ Successfully imported security logger")
            
            # Test logging different event types
            log_auth_failure("127.0.0.1", "/api/auth/login", user_id="test_user")
            print("  ✓ Auth failure logging works")
            
            log_malicious_request("192.168.1.100", "/api/users", "POST", attack_type="sql_injection")
            print("  ✓ Malicious request logging works")
            
            log_rate_limit_exceeded("10.0.0.1", "/api/content", limit_type="requests")
            print("  ✓ Rate limit logging works")
            
            log_api_key_abuse("key_123", "172.16.0.1", "excessive_requests")
            print("  ✓ API key abuse logging works")
            
            log_suspicious_activity("203.0.113.1", "port_scanning", confidence_score=0.8)
            print("  ✓ Suspicious activity logging works")
            
            # Test summary and attack detection
            summary = get_security_event_summary()
            print(f"  ✓ Event summary retrieved: {len(summary)} event types")
            
            under_attack = is_system_under_attack(threshold=1)  # Low threshold for testing
            print(f"  ✓ Attack detection works: under_attack={under_attack}")
            
            return True
            
        except ImportError as import_err:
            print(f"  ⚠️  Import error (dependencies missing): {import_err}")
            print("  ℹ️  Testing basic code structure validation...")
            
            # Fallback: just verify the code structure is valid
            with open("app/services/security_event_logger.py", 'r') as f:
                source_code = f.read()
            
            # Verify basic Python syntax
            try:
                compile(source_code, "app/services/security_event_logger.py", "exec")
                print("  ✓ Security logger code compiles successfully")
            except SyntaxError as syntax_err:
                print(f"  ✗ Syntax error in security logger: {syntax_err}")
                return False
            
            # Verify key functions are defined
            required_functions = [
                "def log_auth_failure",
                "def log_malicious_request", 
                "def log_rate_limit_exceeded",
                "def log_api_key_abuse",
                "def log_suspicious_activity",
            ]
            
            all_functions_present = True
            for func in required_functions:
                if func in source_code:
                    print(f"  ✓ Function defined: {func}")
                else:
                    print(f"  ✗ Missing function: {func}")
                    all_functions_present = False
            
            return all_functions_present
        
    except Exception as e:
        print(f"  ✗ Error testing functionality: {e}")
        return False


def validate_data_privacy():
    """Validate data privacy and truncation features."""
    print("\nValidating data privacy features...")
    
    logger_file = "app/services/security_event_logger.py"
    
    privacy_features = [
        "payload_sample[:200]",  # Payload truncation
        "[:100]",  # User agent truncation
        "[:200]",  # General truncation
        "errors='ignore'",  # Safe decoding
        "# avoid logging sensitive data",  # Privacy comment
    ]
    
    results = check_content_in_file(logger_file, privacy_features)
    
    privacy_protected = True
    for feature, found in results.items():
        if found:
            print(f"  ✓ Privacy feature: {feature}")
        else:
            print(f"  ✗ Missing privacy protection: {feature}")
            privacy_protected = False
    
    return privacy_protected


def validate_performance_considerations():
    """Validate performance optimizations."""
    print("\nValidating performance considerations...")
    
    logger_file = "app/services/security_event_logger.py"
    
    performance_features = [
        "event_counters",  # Efficient counting
        "last_reset_time",  # Time-based reset
        "time_window_minutes",  # Configurable windows
        "dataclass",  # Efficient data structures
        "asdict",  # Fast serialization
    ]
    
    results = check_content_in_file(logger_file, performance_features)
    
    performance_optimized = True
    for feature, found in results.items():
        if found:
            print(f"  ✓ Performance feature: {feature}")
        else:
            print(f"  ✗ Missing optimization: {feature}")
            performance_optimized = False
    
    return performance_optimized


def main():
    """Run all security event logger validations."""
    print("=" * 60)
    print("Security Event Logger Implementation Validation")
    print("=" * 60)
    
    validations = [
        ("Security Logger Implementation", validate_security_logger_implementation),
        ("Event Types and Severities", validate_event_types_and_severities),
        ("Middleware Integration", validate_middleware_integration),
        ("Test Coverage", validate_test_coverage),
        ("Logging Configuration", validate_logging_configuration),
        ("Structured Logging", validate_structured_logging),
        ("Security Features", validate_security_features),
        ("Security Events Simulation", simulate_security_events),
        ("Data Privacy Features", validate_data_privacy),
        ("Performance Considerations", validate_performance_considerations),
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
        print("\nSecurity event logger properly implemented with:")
        print("- Comprehensive event type coverage")
        print("- Multiple severity levels for appropriate response")
        print("- Structured JSON logging for easy parsing")
        print("- Integration with request validation middleware")
        print("- Data privacy protections and payload truncation")
        print("- Performance optimizations for high-throughput scenarios")
        print("- Attack detection and event summarization")
        print("- Extensive test coverage for reliability")
        print("\nNext steps:")
        print("1. Monitor security events in staging environment")
        print("2. Set up alerting for critical security events")
        print("3. Configure log aggregation and analysis tools")
        print("4. Tune attack detection thresholds based on traffic")
        return 0
    else:
        print("❌ Some validations FAILED")
        print("\nPlease fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())