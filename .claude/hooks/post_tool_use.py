#!/usr/bin/env python3
"""
Post-Tool-Use Quality Validation Hook
Validates code quality after Claude Code executes file modifications
Based on 2024-2025 Claude Code hooks best practices
"""

import sys
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class PostToolUseValidator:
    def __init__(self):
        self.python_extensions = ['.py']
        self.javascript_extensions = ['.js', '.jsx', '.ts', '.tsx']
        self.markdown_extensions = ['.md']
        self.validation_results = []

    def validate_python_file(self, file_path: str) -> Dict[str, Any]:
        """Validate Python file syntax and basic quality"""
        results = {
            'file': file_path,
            'syntax_valid': False,
            'issues': []
        }

        # Check Python syntax
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Compile to check syntax
            compile(content, file_path, 'exec')
            results['syntax_valid'] = True

            # Basic quality checks
            lines = content.split('\n')

            # Check for extremely long lines (>200 chars)
            long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 200]
            if long_lines:
                results['issues'].append(f"Long lines (>200 chars): {long_lines[:5]}")

            # Check for potential security issues
            dangerous_patterns = [
                (r'eval\s*\(', 'Use of eval() function'),
                (r'exec\s*\(', 'Use of exec() function'),
                (r'__import__\s*\(', 'Dynamic imports'),
                (r'subprocess\.call.*shell\s*=\s*True', 'Shell injection risk')
            ]

            for pattern, description in dangerous_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    results['issues'].append(f"Security concern: {description}")

        except SyntaxError as e:
            results['issues'].append(f"Syntax error: {e}")
        except Exception as e:
            results['issues'].append(f"Validation error: {e}")

        return results

    def validate_markdown_file(self, file_path: str) -> Dict[str, Any]:
        """Validate Markdown file structure and quality"""
        results = {
            'file': file_path,
            'syntax_valid': True,
            'issues': []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for basic markdown issues
            lines = content.split('\n')

            # Check for unmatched code blocks
            code_block_count = content.count('```')
            if code_block_count % 2 != 0:
                results['issues'].append("Unmatched code blocks (```)")

            # Check for proper heading hierarchy
            headings = []
            for i, line in enumerate(lines):
                if line.strip().startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    headings.append((i+1, level))

            # Validate heading hierarchy
            if headings:
                if headings[0][1] != 1:
                    results['issues'].append("Document should start with H1 (#)")

                for i in range(1, len(headings)):
                    prev_level = headings[i-1][1]
                    curr_level = headings[i][1]
                    if curr_level > prev_level + 1:
                        results['issues'].append(f"Heading hierarchy skip at line {headings[i][0]}")

        except Exception as e:
            results['issues'].append(f"Validation error: {e}")
            results['syntax_valid'] = False

        return results

    def validate_file_quality(self, file_path: str) -> Dict[str, Any]:
        """Validate file based on its extension"""
        if not os.path.exists(file_path):
            return {
                'file': file_path,
                'syntax_valid': False,
                'issues': ['File does not exist']
            }

        file_ext = Path(file_path).suffix.lower()

        if file_ext in self.python_extensions:
            return self.validate_python_file(file_path)
        elif file_ext in self.markdown_extensions:
            return self.validate_markdown_file(file_path)
        else:
            # Basic file validation for other types
            return {
                'file': file_path,
                'syntax_valid': True,
                'issues': []
            }

    def run_validation_scripts(self, file_paths: List[str]) -> bool:
        """Run our validation scripts if they exist and files are in .claude/"""
        claude_files = [f for f in file_paths if f.startswith('.claude/')]

        if not claude_files:
            return True

        # Check if validation scripts exist
        validation_script = Path('.claude/validation/scripts/validate_system.py')
        if not validation_script.exists():
            return True

        try:
            print("🧪 Running system validation after .claude/ modifications...")
            result = subprocess.run(
                ['python3', str(validation_script)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("✅ System validation passed")
                return True
            else:
                print("❌ System validation failed:")
                print(result.stdout)
                print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            print("⏰ Validation script timed out")
            return False
        except Exception as e:
            print(f"⚠️  Could not run validation script: {e}")
            return True  # Don't block on validation script errors

    def validate_post_tool_operation(self, tool_name: str, file_paths: str) -> bool:
        """Main validation method called after tool execution"""
        print(f"🔍 Post-Tool Validation: {tool_name} on {file_paths}")

        # Split file paths if multiple
        paths = [p.strip().strip('"') for p in file_paths.split(',') if p.strip()]

        overall_passed = True

        # Validate each file
        for path in paths:
            result = self.validate_file_quality(path)
            self.validation_results.append(result)

            if not result['syntax_valid'] or result['issues']:
                overall_passed = False
                print(f"❌ Issues in {path}:")
                for issue in result['issues']:
                    print(f"   - {issue}")

        # Run system validation for .claude/ files
        if not self.run_validation_scripts(paths):
            overall_passed = False

        if overall_passed:
            print("✅ Post-tool validation passed")
        else:
            print("❌ Post-tool validation completed with issues")

        return overall_passed

    def log_operation(self, tool_name: str, file_paths: str, result: bool):
        """Log validation operation to audit trail"""
        log_dir = Path('.claude/artifacts/logs/validation/')
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f'post_tool_validation_{datetime.now().strftime("%Y-%m-%d")}.log'

        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().isoformat()
            status = "PASS" if result else "FAIL"
            f.write(f"{timestamp} | POST-TOOL | {status} | {tool_name} | {file_paths}\n")

            # Log detailed results
            for validation_result in self.validation_results:
                if validation_result['issues']:
                    f.write(f"  ISSUES in {validation_result['file']}: {'; '.join(validation_result['issues'])}\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: post_tool_use.py <tool_name> <file_paths>")
        sys.exit(0)

    tool_name = sys.argv[1]
    file_paths = sys.argv[2]

    validator = PostToolUseValidator()
    result = validator.validate_post_tool_operation(tool_name, file_paths)
    validator.log_operation(tool_name, file_paths, result)

    # Note: We don't exit with error code for post-tool validation
    # as it shouldn't block the operation, just warn about issues
    sys.exit(0)

if __name__ == "__main__":
    main()
