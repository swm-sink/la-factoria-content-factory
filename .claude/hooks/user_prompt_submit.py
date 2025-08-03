#!/usr/bin/env python3
"""
User Prompt Submit Security Validation Hook
Validates user prompts for security concerns before Claude processes them
Based on 2024-2025 Claude Code hooks best practices
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class UserPromptValidator:
    def __init__(self):
        self.security_patterns = [
            (r'rm\s+-rf\s+/', 'Dangerous file deletion command'),
            (r'sudo\s+rm', 'Privileged file deletion'),
            (r'curl.*\|\s*bash', 'Piped execution security risk'),
            (r'wget.*\|\s*sh', 'Piped execution security risk'),
            (r'eval\s*\(\s*input', 'Code injection risk'),
            (r'exec\s*\(\s*input', 'Code execution risk'),
            (r'__import__\s*\(\s*input', 'Dynamic import risk'),
        ]

        self.sensitive_patterns = [
            (r'password\s*[=:]\s*["\']?[^"\'\s]+', 'Potential password exposure'),
            (r'api[_-]?key\s*[=:]\s*["\']?[^"\'\s]+', 'Potential API key exposure'),
            (r'secret\s*[=:]\s*["\']?[^"\'\s]+', 'Potential secret exposure'),
            (r'token\s*[=:]\s*["\']?[^"\'\s]+', 'Potential token exposure'),
            (r'[A-Za-z0-9+/]{40,}={0,2}', 'Potential base64 encoded secret'),
        ]

        self.prompt_injection_patterns = [
            (r'ignore\s+(previous|all)\s+instructions', 'Potential prompt injection'),
            (r'forget\s+(everything|all)', 'Potential prompt injection'),
            (r'you\s+are\s+now\s+a', 'Potential role manipulation'),
            (r'system\s*:\s*new\s+instructions', 'Potential system override'),
        ]

    def validate_security_concerns(self, prompt: str) -> Dict[str, Any]:
        """Check for security-related patterns in the prompt"""
        issues = []

        # Check for dangerous commands
        for pattern, description in self.security_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                issues.append(f"Security risk: {description}")

        return {
            'category': 'security',
            'issues': issues
        }

    def validate_sensitive_data(self, prompt: str) -> Dict[str, Any]:
        """Check for potentially sensitive data in the prompt"""
        issues = []

        for pattern, description in self.sensitive_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            if matches:
                # Don't log the actual sensitive data, just flag it
                issues.append(f"Sensitive data: {description}")

        return {
            'category': 'sensitive_data',
            'issues': issues
        }

    def validate_prompt_injection(self, prompt: str) -> Dict[str, Any]:
        """Check for potential prompt injection attempts"""
        issues = []

        for pattern, description in self.prompt_injection_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                issues.append(f"Prompt injection: {description}")

        return {
            'category': 'prompt_injection',
            'issues': issues
        }

    def validate_content_appropriateness(self, prompt: str) -> Dict[str, Any]:
        """Basic content appropriateness checks"""
        issues = []

        # Check for extremely long prompts (potential DoS)
        if len(prompt) > 50000:
            issues.append("Extremely long prompt (potential DoS)")

        # Check for excessive repetition (potential resource exhaustion)
        words = prompt.lower().split()
        if len(words) > 100:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1

            max_repetitions = max(word_counts.values())
            if max_repetitions > len(words) * 0.3:  # >30% repetition
                issues.append("Excessive word repetition detected")

        return {
            'category': 'content',
            'issues': issues
        }

    def validate_user_prompt(self, prompt: str) -> bool:
        """Main validation method for user prompts"""
        print(f"🔍 Prompt Security Validation (length: {len(prompt)} chars)")

        all_issues = []
        validation_passed = True

        # Run all validation checks
        checks = [
            self.validate_security_concerns(prompt),
            self.validate_sensitive_data(prompt),
            self.validate_prompt_injection(prompt),
            self.validate_content_appropriateness(prompt)
        ]

        for check in checks:
            if check['issues']:
                all_issues.extend(check['issues'])
                validation_passed = False

        # Log results
        if validation_passed:
            print("✅ Prompt validation passed")
        else:
            print("⚠️  Prompt validation issues detected:")
            for issue in all_issues:
                print(f"   - {issue}")

            # Note: We might want to allow prompts with warnings
            # but log them for security monitoring
            print("🛡️  Proceeding with security warnings logged")

        return validation_passed

    def log_validation(self, prompt: str, result: bool, issues: List[str]):
        """Log prompt validation results"""
        log_dir = Path('.claude/artifacts/logs/validation/')
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f'prompt_validation_{datetime.now().strftime("%Y-%m-%d")}.log'

        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().isoformat()
            status = "PASS" if result else "WARN"
            prompt_preview = prompt[:100].replace('\n', ' ') + ('...' if len(prompt) > 100 else '')

            f.write(f"{timestamp} | PROMPT | {status} | {len(prompt)} chars | {prompt_preview}\n")

            if issues:
                for issue in issues:
                    f.write(f"  ISSUE: {issue}\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: user_prompt_submit.py <prompt>")
        sys.exit(0)

    prompt = sys.argv[1] if len(sys.argv) > 1 else ""

    validator = UserPromptValidator()

    # Collect all issues for logging
    all_issues = []
    checks = [
        validator.validate_security_concerns(prompt),
        validator.validate_sensitive_data(prompt),
        validator.validate_prompt_injection(prompt),
        validator.validate_content_appropriateness(prompt)
    ]

    for check in checks:
        all_issues.extend(check['issues'])

    result = validator.validate_user_prompt(prompt)
    validator.log_validation(prompt, result, all_issues)

    # For user prompt validation, we typically don't want to block the prompt
    # but rather log security concerns for monitoring
    sys.exit(0)

if __name__ == "__main__":
    main()
