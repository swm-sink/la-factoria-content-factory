#!/usr/bin/env python3
"""Audit codebase for exposed secrets and sensitive information."""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import json


class SecretScanner:
    """Scanner for detecting secrets in codebase."""
    
    def __init__(self):
        """Initialize secret patterns."""
        self.patterns = {
            # API Keys
            'google_api_key': re.compile(r'AIza[0-9A-Za-z\-_]{35}'),
            'aws_access_key': re.compile(r'AKIA[0-9A-Z]{16}'),
            'aws_secret_key': re.compile(r'[0-9a-zA-Z/+]{40}'),
            'openai_api_key': re.compile(r'sk-[a-zA-Z0-9]{48}'),
            'anthropic_api_key': re.compile(r'sk-ant-[a-zA-Z0-9\-_]{32,}'),
            'elevenlabs_api_key': re.compile(r'[a-f0-9]{32}'),
            
            # Generic API Keys
            'generic_api_key': re.compile(r'api[_-]?key["\'\s]*[:=]["\'\s]*[a-zA-Z0-9_\-]{16,}', re.IGNORECASE),
            'bearer_token': re.compile(r'bearer\s+[a-zA-Z0-9_\-\.]{20,}', re.IGNORECASE),
            
            # Database URLs
            'postgres_url': re.compile(r'postgres://[^:]+:[^@]+@[^/]+/\w+'),
            'mysql_url': re.compile(r'mysql://[^:]+:[^@]+@[^/]+/\w+'),
            'mongodb_url': re.compile(r'mongodb://[^:]+:[^@]+@[^/]+/\w+'),
            
            # JWT Secrets
            'jwt_secret': re.compile(r'jwt[_-]?secret["\'\s]*[:=]["\'\s]*[a-zA-Z0-9_\-]{16,}', re.IGNORECASE),
            
            # Private Keys
            'private_key': re.compile(r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----'),
            'ssh_private_key': re.compile(r'-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----'),
            
            # Passwords
            'password': re.compile(r'password["\'\s]*[:=]["\'\s]*[^\s"\']{8,}', re.IGNORECASE),
            
            # GCP Service Account Keys
            'gcp_service_account': re.compile(r'"type":\s*"service_account"'),
            
            # Common secret env vars
            'secret_env_var': re.compile(r'(SECRET|TOKEN|KEY|PASSWORD|PASS)[_\w]*\s*=\s*["\']?[a-zA-Z0-9_\-\.]{8,}', re.IGNORECASE),
        }
        
        # File extensions to scan
        self.extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.json', '.yaml', '.yml', '.env', '.md', '.txt', '.sh'}
        
        # Directories to ignore
        self.ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env', 'dist', 'build'}
        
        # Files to ignore
        self.ignore_files = {'requirements.txt', 'package.json', 'package-lock.json', 'yarn.lock'}
        
        # Allowlisted patterns (not secrets)
        self.allowlist = [
            'your-api-key-here',
            'your-secret-here',
            'example-key',
            'test-key',
            'dummy-key',
            'placeholder',
            'REPLACE_WITH_ACTUAL',
            'your-gemini-api-key-here',
            'your-elevenlabs-api-key-here',
        ]

    def scan_file(self, filepath: Path) -> List[Dict]:
        """Scan a single file for secrets."""
        findings = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern_name, pattern in self.patterns.items():
                        matches = pattern.finditer(line)
                        for match in matches:
                            secret_value = match.group(0)
                            
                            # Skip allowlisted patterns
                            if any(allow in secret_value.lower() for allow in self.allowlist):
                                continue
                            
                            findings.append({
                                'file': str(filepath),
                                'line': line_num,
                                'pattern': pattern_name,
                                'match': secret_value,
                                'context': line.strip(),
                                'severity': self._get_severity(pattern_name)
                            })
                            
        except Exception as e:
            print(f"Error scanning {filepath}: {e}")
            
        return findings

    def _get_severity(self, pattern_name: str) -> str:
        """Get severity level for pattern."""
        high_severity = {'google_api_key', 'aws_access_key', 'aws_secret_key', 'openai_api_key', 'private_key', 'gcp_service_account'}
        medium_severity = {'generic_api_key', 'jwt_secret', 'postgres_url', 'mysql_url', 'mongodb_url'}
        
        if pattern_name in high_severity:
            return 'HIGH'
        elif pattern_name in medium_severity:
            return 'MEDIUM'
        else:
            return 'LOW'

    def scan_directory(self, directory: Path) -> List[Dict]:
        """Scan directory recursively for secrets."""
        all_findings = []
        
        for root, dirs, files in os.walk(directory):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                # Skip ignored files and extensions
                if file in self.ignore_files:
                    continue
                    
                file_path = Path(root) / file
                if file_path.suffix not in self.extensions:
                    continue
                    
                findings = self.scan_file(file_path)
                all_findings.extend(findings)
                
        return all_findings

    def scan_git_history(self) -> List[str]:
        """Check for secrets in git history (simplified check)."""
        warnings = []
        
        # Check for common secret patterns in git log
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'log', '--all', '--full-history', '--grep=password', '--grep=secret', '--grep=key', '-i'],
                capture_output=True, text=True, cwd=Path.cwd()
            )
            
            if result.stdout.strip():
                warnings.append("Found potential secret-related commits in git history")
                
        except subprocess.CalledProcessError:
            pass
        except FileNotFoundError:
            warnings.append("Git not available for history scan")
            
        return warnings


def generate_report(findings: List[Dict], git_warnings: List[str]) -> str:
    """Generate a human-readable report."""
    report = []
    report.append("=" * 80)
    report.append("SECRETS AUDIT REPORT")
    report.append("=" * 80)
    report.append("")
    
    if not findings and not git_warnings:
        report.append("✅ No secrets detected in codebase!")
        report.append("")
        report.append("Recommendations:")
        report.append("- Continue using environment variables for secrets")
        report.append("- Keep .env files in .gitignore")
        report.append("- Use secret management services in production")
        return "\n".join(report)
    
    # Summary
    high_count = sum(1 for f in findings if f['severity'] == 'HIGH')
    medium_count = sum(1 for f in findings if f['severity'] == 'MEDIUM')
    low_count = sum(1 for f in findings if f['severity'] == 'LOW')
    
    report.append(f"SUMMARY: {len(findings)} potential secrets found")
    report.append(f"- HIGH severity: {high_count}")
    report.append(f"- MEDIUM severity: {medium_count}")
    report.append(f"- LOW severity: {low_count}")
    report.append("")
    
    # Git warnings
    if git_warnings:
        report.append("GIT HISTORY WARNINGS:")
        for warning in git_warnings:
            report.append(f"⚠️  {warning}")
        report.append("")
    
    # Detailed findings
    if findings:
        report.append("DETAILED FINDINGS:")
        report.append("-" * 40)
        
        # Group by severity
        for severity in ['HIGH', 'MEDIUM', 'LOW']:
            severity_findings = [f for f in findings if f['severity'] == severity]
            if not severity_findings:
                continue
                
            report.append(f"\n{severity} SEVERITY ({len(severity_findings)} findings):")
            
            for finding in severity_findings:
                report.append(f"")
                report.append(f"File: {finding['file']}")
                report.append(f"Line: {finding['line']}")
                report.append(f"Pattern: {finding['pattern']}")
                report.append(f"Match: {finding['match'][:50]}{'...' if len(finding['match']) > 50 else ''}")
                report.append(f"Context: {finding['context'][:100]}{'...' if len(finding['context']) > 100 else ''}")
    
    report.append("")
    report.append("RECOMMENDATIONS:")
    report.append("- Remove all HIGH severity findings immediately")
    report.append("- Review MEDIUM severity findings")
    report.append("- Use environment variables for all secrets")
    report.append("- Add pre-commit hooks to prevent future secret commits")
    report.append("- Consider using a secret management service")
    
    return "\n".join(report)


def main():
    """Run secrets audit."""
    scanner = SecretScanner()
    
    print("Scanning codebase for exposed secrets...")
    print("This may take a moment...")
    print()
    
    # Scan current directory
    current_dir = Path.cwd()
    findings = scanner.scan_directory(current_dir)
    
    # Check git history
    git_warnings = scanner.scan_git_history()
    
    # Generate report
    report = generate_report(findings, git_warnings)
    print(report)
    
    # Save report to file
    report_file = current_dir / "secrets_audit_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_file}")
    
    # Exit with error code if secrets found
    if findings:
        high_severity = [f for f in findings if f['severity'] == 'HIGH']
        if high_severity:
            print(f"\n❌ {len(high_severity)} HIGH severity secrets found!")
            return 1
        else:
            print(f"\n⚠️  {len(findings)} potential secrets found (no high severity)")
            return 0
    else:
        print("\n✅ No secrets detected!")
        return 0


if __name__ == "__main__":
    sys.exit(main())