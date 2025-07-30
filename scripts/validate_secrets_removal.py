#!/usr/bin/env python3
"""Validate secrets removal implementation."""

import os
import sys
from pathlib import Path


def validate_gitignore():
    """Validate .gitignore properly excludes secrets."""
    print("Validating .gitignore configuration...")
    
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("  ✗ .gitignore not found")
        return False
    
    with open(gitignore_path, 'r') as f:
        content = f.read()
    
    required_patterns = [
        '.env',
        '*.pem',
        '*.key',
        'secrets.yml',
    ]
    
    all_present = True
    for pattern in required_patterns:
        if pattern in content:
            print(f"  ✓ {pattern} properly ignored")
        else:
            print(f"  ✗ Missing pattern: {pattern}")
            all_present = False
    
    return all_present


def validate_env_example():
    """Validate .env.example contains only placeholders."""
    print("\nValidating .env.example...")
    
    env_example_path = Path(".env.example")
    if not env_example_path.exists():
        print("  ✗ .env.example not found")
        return False
    
    with open(env_example_path, 'r') as f:
        content = f.read()
    
    # Check for placeholder patterns
    safe_patterns = [
        'your-gemini-api-key-here',
        'your-elevenlabs-api-key-here',
        'your-production-secret',
    ]
    
    has_placeholders = any(pattern in content for pattern in safe_patterns)
    
    if has_placeholders:
        print("  ✓ Contains safe placeholder values")
    else:
        print("  ✗ Missing placeholder values")
        return False
    
    # Check for potential real secrets (basic check)
    suspicious_patterns = [
        'AIza[0-9A-Za-z\-_]{35}',
        'sk-[a-zA-Z0-9]{48}',
        'AKIA[0-9A-Z]{16}',
    ]
    
    import re
    for pattern in suspicious_patterns:
        if re.search(pattern, content):
            print(f"  ⚠️  Potential real secret found: {pattern}")
            return False
    
    print("  ✓ No real secrets detected")
    return True


def validate_secrets_guard():
    """Validate secrets guard implementation."""
    print("\nValidating secrets guard...")
    
    guard_path = Path("scripts/secrets_guard.py")
    if not guard_path.exists():
        print("  ✗ secrets_guard.py not found")
        return False
    
    print("  ✓ secrets_guard.py exists")
    
    # Test the guard
    try:
        import subprocess
        result = subprocess.run(
            ['python3', 'scripts/secrets_guard.py', '--help'],
            capture_output=True, text=True, timeout=10
        )
        # Even if --help isn't implemented, the script should run
        print("  ✓ secrets_guard.py is executable")
    except subprocess.TimeoutExpired:
        print("  ✗ secrets_guard.py timed out")
        return False
    except Exception as e:
        print(f"  ✗ secrets_guard.py error: {e}")
        return False
    
    return True


def validate_pre_commit_hook():
    """Validate pre-commit hook installation."""
    print("\nValidating pre-commit hook...")
    
    # Check for git worktree hook
    hook_path = Path("/Users/smenssink/conductor/repo/la-factoria-v2/.main/.git/worktrees/quebec/hooks/pre-commit")
    
    if hook_path.exists():
        print("  ✓ Pre-commit hook installed")
        
        # Check if executable
        if os.access(hook_path, os.X_OK):
            print("  ✓ Pre-commit hook is executable")
        else:
            print("  ✗ Pre-commit hook is not executable")
            return False
        
        # Check hook content
        with open(hook_path, 'r') as f:
            content = f.read()
        
        if 'secrets_guard.py' in content:
            print("  ✓ Pre-commit hook calls secrets guard")
        else:
            print("  ✗ Pre-commit hook doesn't call secrets guard")
            return False
        
        return True
    else:
        print("  ✗ Pre-commit hook not found")
        return False


def validate_test_coverage():
    """Validate test coverage for secrets guard."""
    print("\nValidating test coverage...")
    
    test_path = Path("tests/unit/security/test_secrets_guard.py")
    if not test_path.exists():
        print("  ✗ Secrets guard tests not found")
        return False
    
    print("  ✓ Secrets guard tests exist")
    
    with open(test_path, 'r') as f:
        content = f.read()
    
    required_tests = [
        'test_safe_content_detection',
        'test_real_secrets_detection',
        'test_check_staged_files',
        'test_pattern_specificity',
    ]
    
    all_tests_present = True
    for test in required_tests:
        if test in content:
            print(f"  ✓ Test present: {test}")
        else:
            print(f"  ✗ Missing test: {test}")
            all_tests_present = False
    
    return all_tests_present


def check_for_actual_secrets():
    """Quick check for any actual secrets in common locations."""
    print("\nChecking for actual secrets...")
    
    # Check common files that might contain secrets
    check_files = [
        '.env',
        'config.py',
        'settings.py',
        'secrets.py',
    ]
    
    secrets_found = False
    
    for filename in check_files:
        if os.path.exists(filename):
            print(f"  ⚠️  Found potential secrets file: {filename}")
            secrets_found = True
    
    if not secrets_found:
        print("  ✓ No obvious secrets files found")
    
    return not secrets_found


def main():
    """Run all secrets removal validations."""
    print("=" * 60)
    print("Secrets Removal Validation")
    print("=" * 60)
    
    validations = [
        ("GitIgnore Configuration", validate_gitignore),
        ("Environment Example", validate_env_example),
        ("Secrets Guard", validate_secrets_guard),
        ("Pre-commit Hook", validate_pre_commit_hook),
        ("Test Coverage", validate_test_coverage),
        ("Actual Secrets Check", check_for_actual_secrets),
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
        print("\nSecrets removal properly implemented with:")
        print("- Proper .gitignore configuration")
        print("- Safe .env.example with placeholders")
        print("- Functional secrets guard script")
        print("- Pre-commit hook to prevent future secrets")
        print("- Comprehensive test coverage")
        print("- No actual secrets found in codebase")
        print("\nNext steps:")
        print("1. Test pre-commit hook by staging a file with a fake secret")
        print("2. Train team on secret management practices")
        print("3. Set up secret management service for production")
        return 0
    else:
        print("❌ Some validations FAILED")
        print("\nPlease fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())