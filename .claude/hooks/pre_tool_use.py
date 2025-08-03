#!/usr/bin/env python3
"""
Pre-Tool-Use Validation Hook
Validates operations before Claude Code executes file modifications
Based on 2024-2025 Claude Code hooks best practices
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime

class PreToolUseValidator:
    def __init__(self):
        self.dangerous_patterns = [
            r'rm\s+-rf',
            r'sudo\s+rm',
            r'\.env',
            r'\.secret',
            r'password\s*=',
            r'api[_-]?key\s*=',
            r'token\s*=',
        ]
        self.protected_files = [
            '.env',
            '.env.local',
            '.env.production',
            'secrets.json',
            'private.key',
            '.ssh/id_rsa'
        ]

    def validate_tool_operation(self, tool_name: str, file_paths: str) -> bool:
        """Validate tool operation before execution"""
        print(f"🔍 Pre-Tool Validation: {tool_name} on {file_paths}")

        # Split file paths if multiple
        paths = [p.strip().strip('"') for p in file_paths.split(',') if p.strip()]

        validation_passed = True
        issues = []

        # Check for protected files
        for path in paths:
            if any(protected in path for protected in self.protected_files):
                issues.append(f"Attempting to modify protected file: {path}")
                validation_passed = False

        # Check for dangerous operations in file content if it's an Edit operation
        if tool_name in ['Edit', 'MultiEdit']:
            for path in paths:
                if os.path.exists(path):
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        for pattern in self.dangerous_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                issues.append(f"Dangerous pattern '{pattern}' found in {path}")
                                validation_passed = False
                    except Exception as e:
                        print(f"⚠️  Could not read file {path}: {e}")

        # Log validation results
        if validation_passed:
            print("✅ Pre-tool validation passed")
        else:
            print("❌ Pre-tool validation failed:")
            for issue in issues:
                print(f"   - {issue}")

        return validation_passed

    def log_operation(self, tool_name: str, file_paths: str, result: bool):
        """Log validation operation to audit trail"""
        log_dir = Path('.claude/artifacts/logs/validation/')
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f'pre_tool_validation_{datetime.now().strftime("%Y-%m-%d")}.log'

        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().isoformat()
            status = "PASS" if result else "FAIL"
            f.write(f"{timestamp} | PRE-TOOL | {status} | {tool_name} | {file_paths}\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: pre_tool_use.py <tool_name> <file_paths>")
        sys.exit(0)

    tool_name = sys.argv[1]
    file_paths = sys.argv[2]

    validator = PreToolUseValidator()
    result = validator.validate_tool_operation(tool_name, file_paths)
    validator.log_operation(tool_name, file_paths, result)

    # Exit with appropriate code (0 = success, 1 = failure)
    sys.exit(0 if result else 1)

if __name__ == "__main__":
    main()
