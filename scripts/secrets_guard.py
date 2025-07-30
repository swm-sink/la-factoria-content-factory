#!/usr/bin/env python3
"""Git pre-commit hook to prevent secrets from being committed."""

import os
import re
import sys
from pathlib import Path
from typing import List, Set


class SecretsGuard:
    """Lightweight secrets detection for pre-commit hooks."""
    
    def __init__(self):
        """Initialize with focused patterns for real secrets."""
        self.patterns = {
            # Real API keys with specific formats
            'google_api_key': re.compile(r'AIza[0-9A-Za-z\-_]{35}'),
            'openai_api_key': re.compile(r'sk-[a-zA-Z0-9]{48}'),
            'anthropic_api_key': re.compile(r'sk-ant-[a-zA-Z0-9\-]{95,}'),
            
            # Real AWS keys (not just long strings)
            'aws_access_key': re.compile(r'AKIA[0-9A-Z]{16}'),
            
            # Database connection strings with credentials
            'db_url_with_creds': re.compile(r'(postgres|mysql|mongodb)://[^:\s]+:[^@\s]+@[^/\s]+'),
            
            # Private keys
            'private_key': re.compile(r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----'),
            
            # JWT secrets (actual long random strings)
            'jwt_secret_long': re.compile(r'jwt[_-]?secret["\'\s]*[:=]["\'\s]*[a-zA-Z0-9_\-+/]{32,}', re.IGNORECASE),
            
            # Actual secrets in .env format
            'env_secret': re.compile(r'^[A-Z_]+(SECRET|KEY|TOKEN|PASSWORD)[A-Z_]*\s*=\s*[a-zA-Z0-9_\-+/]{20,}$', re.MULTILINE),
        }
        
        # Known safe patterns to ignore
        self.safe_patterns = [
            'your-api-key-here',
            'your-secret-here',
            'your-gemini-api-key-here',
            'your-elevenlabs-api-key-here',
            'example-key',
            'test-key',
            'dummy-key',
            'placeholder',
            'REPLACE_WITH_ACTUAL',
            'sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            'AIzaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            'AKIAXXXXXXXXXXXXXXXX',
        ]

    def is_safe_content(self, content: str) -> bool:
        """Check if content is safe (contains known placeholders)."""
        content_lower = content.lower()
        return any(safe in content_lower for safe in self.safe_patterns)

    def scan_content(self, content: str, filepath: str) -> List[dict]:
        """Scan content for secrets."""
        findings = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern_name, pattern in self.patterns.items():
                matches = pattern.finditer(line)
                for match in matches:
                    secret_value = match.group(0)
                    
                    # Skip if it's a safe placeholder
                    if self.is_safe_content(secret_value):
                        continue
                    
                    findings.append({
                        'file': filepath,
                        'line': line_num,
                        'pattern': pattern_name,
                        'match': secret_value[:20] + '...' if len(secret_value) > 20 else secret_value,
                        'context': line.strip()[:100]
                    })
        
        return findings

    def check_staged_files(self) -> List[dict]:
        """Check staged files for secrets."""
        import subprocess
        
        try:
            # Get staged files
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True, text=True, check=True
            )
            
            staged_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
            all_findings = []
            
            for filepath in staged_files:
                # Skip binary files and irrelevant extensions
                if not self._should_scan_file(filepath):
                    continue
                
                try:
                    # Get staged content
                    result = subprocess.run(
                        ['git', 'show', f':{filepath}'],
                        capture_output=True, text=True, check=True
                    )
                    
                    findings = self.scan_content(result.stdout, filepath)
                    all_findings.extend(findings)
                    
                except subprocess.CalledProcessError:
                    # File might be deleted or binary
                    continue
                except UnicodeDecodeError:
                    # Binary file
                    continue
            
            return all_findings
            
        except subprocess.CalledProcessError:
            print("Error: Not in a git repository or git not available")
            return []

    def _should_scan_file(self, filepath: str) -> bool:
        """Check if file should be scanned."""
        # Skip certain file types
        skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar', '.gz'}
        skip_files = {'package-lock.json', 'yarn.lock', 'poetry.lock'}
        
        if any(filepath.endswith(ext) for ext in skip_extensions):
            return False
        
        if any(skip_file in filepath for skip_file in skip_files):
            return False
        
        return True


def main():
    """Run secrets guard as pre-commit hook."""
    guard = SecretsGuard()
    
    # Check staged files
    findings = guard.check_staged_files()
    
    if not findings:
        print("✅ No secrets detected in staged files")
        return 0
    
    # Report findings
    print("🚨 SECRETS DETECTED IN STAGED FILES!")
    print("=" * 50)
    
    for finding in findings:
        print(f"File: {finding['file']}")
        print(f"Line: {finding['line']}")
        print(f"Pattern: {finding['pattern']}")
        print(f"Match: {finding['match']}")
        print(f"Context: {finding['context']}")
        print("-" * 30)
    
    print("\nCOMMIT BLOCKED - Please remove secrets before committing:")
    print("1. Remove the secrets from your files")
    print("2. Use environment variables instead")
    print("3. Add secrets to .env (already in .gitignore)")
    print("4. Stage your changes and commit again")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())