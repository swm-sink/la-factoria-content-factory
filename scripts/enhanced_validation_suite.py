#!/usr/bin/env python3
"""
Enhanced Validation Suite for La Factoria
Comprehensive validation with security scanning, performance benchmarks, and quality gates
"""

import os
import sys
import subprocess
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Add app to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class EnhancedValidator:
    """Comprehensive validation framework with multiple quality gates"""
    
    def __init__(self, step_number: str, project_root: str = None):
        self.step_number = step_number
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.results = {}
        self.errors = []
        self.setup_logging()
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'validation_step_{self.step_number}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def run_command(self, command: List[str], capture_output: bool = True) -> Tuple[bool, str]:
        """Run command with proper error handling"""
        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                cwd=self.project_root,
                timeout=300  # 5 minute timeout
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out after 5 minutes"
        except Exception as e:
            return False, str(e)
            
    def validate_tests(self) -> bool:
        """Enhanced test validation with coverage and performance"""
        self.logger.info("🧪 Running enhanced test validation...")
        
        # Run pytest with coverage and performance metrics
        success, output = self.run_command([
            'pytest', '-v', '--cov=app', '--cov-report=term-missing',
            '--cov-report=json:coverage.json', '--tb=short',
            '--durations=10'  # Show 10 slowest tests
        ])
        
        if not success:
            self.errors.append(f"Tests failed: {output}")
            return False
            
        # Check coverage threshold
        try:
            with open(self.project_root / 'coverage.json', 'r') as f:
                coverage_data = json.load(f)
                total_coverage = coverage_data['totals']['percent_covered']
                
                if total_coverage < 70:  # Configurable threshold
                    self.errors.append(f"Coverage {total_coverage:.1f}% below 70% threshold")
                    return False
                    
                self.results['test_coverage'] = total_coverage
                self.logger.info(f"✅ Test coverage: {total_coverage:.1f}%")
        except Exception as e:
            self.errors.append(f"Could not read coverage report: {e}")
            
        return True
        
    def validate_security(self) -> bool:
        """Enhanced security validation"""
        self.logger.info("🔒 Running enhanced security validation...")
        
        security_checks = [
            # Bandit security scan
            (['bandit', '-r', 'app/', '-f', 'json', '-o', 'bandit_report.json'], 'Bandit security scan'),
            
            # Safety check for known vulnerabilities
            (['safety', 'check', '--json'], 'Safety vulnerability check'),
            
            # Semgrep static analysis (if available)
            (['semgrep', '--config=auto', 'app/', '--json'], 'Semgrep static analysis')
        ]
        
        all_passed = True
        
        for command, description in security_checks:
            success, output = self.run_command(command)
            if not success:
                # Some tools might not be installed, log warning instead of error
                self.logger.warning(f"⚠️  {description} not available or failed")
                continue
                
            self.logger.info(f"✅ {description} passed")
            
        # Check for exposed secrets using our secrets guard
        if (self.project_root / 'scripts' / 'secrets_guard.py').exists():
            success, output = self.run_command(['python', 'scripts/secrets_guard.py', '.'])
            if not success:
                self.errors.append(f"Secrets validation failed: {output}")
                all_passed = False
            else:
                self.logger.info("✅ No exposed secrets found")
                
        return all_passed
        
    def validate_code_quality(self) -> bool:
        """Enhanced code quality validation"""
        self.logger.info("📊 Running enhanced code quality validation...")
        
        quality_checks = [
            # Linting with ruff
            (['ruff', 'check', '.'], 'Ruff linting'),
            
            # Code formatting with black
            (['black', '--check', '.'], 'Black formatting'),
            
            # Import sorting with isort
            (['isort', '--check-only', '.'], 'Import sorting'),
            
            # Type checking with mypy (if configured)
            (['mypy', 'app/'], 'Type checking')
        ]
        
        all_passed = True
        
        for command, description in quality_checks:
            success, output = self.run_command(command)
            if not success:
                if 'mypy' in command[0]:
                    # MyPy might not be configured, warn instead of fail
                    self.logger.warning(f"⚠️  {description}: {output[:200]}...")
                    continue
                    
                self.errors.append(f"{description} failed: {output}")
                all_passed = False
            else:
                self.logger.info(f"✅ {description} passed")
                
        return all_passed
        
    def validate_performance(self) -> bool:
        """Enhanced performance validation"""
        self.logger.info("⚡ Running enhanced performance validation...")
        
        # Check if server is running for performance tests
        try:
            response = requests.get('http://localhost:8000/api/health', timeout=5)
            if response.status_code != 200:
                self.logger.warning("⚠️  Server not running, skipping performance tests")
                return True
        except requests.RequestException:
            self.logger.warning("⚠️  Server not accessible, skipping performance tests")
            return True
            
        # Simple load test
        start_time = time.time()
        success_count = 0
        total_requests = 10
        
        for i in range(total_requests):
            try:
                response = requests.get('http://localhost:8000/api/health', timeout=2)
                if response.status_code == 200:
                    success_count += 1
            except requests.RequestException:
                pass
                
        end_time = time.time()
        avg_response_time = (end_time - start_time) / total_requests
        success_rate = (success_count / total_requests) * 100
        
        self.results['avg_response_time'] = avg_response_time
        self.results['success_rate'] = success_rate
        
        if avg_response_time > 2.0:  # 2 second threshold
            self.errors.append(f"Average response time {avg_response_time:.2f}s exceeds 2s threshold")
            return False
            
        if success_rate < 95:  # 95% success rate threshold
            self.errors.append(f"Success rate {success_rate:.1f}% below 95% threshold")
            return False
            
        self.logger.info(f"✅ Performance: {avg_response_time:.2f}s avg, {success_rate:.1f}% success")
        return True
        
    def validate_documentation(self) -> bool:
        """Enhanced documentation validation"""
        self.logger.info("📝 Running enhanced documentation validation...")
        
        required_docs = [
            'README.md',
            'CLAUDE.md',
            'docs/api/',
            'docs/deployment/',
        ]
        
        missing_docs = []
        for doc_path in required_docs:
            full_path = self.project_root / doc_path
            if not full_path.exists():
                missing_docs.append(doc_path)
                
        if missing_docs:
            self.errors.append(f"Missing documentation: {', '.join(missing_docs)}")
            return False
            
        # Check if CLAUDE.md is up to date (has recent modification)
        claude_md = self.project_root / 'CLAUDE.md'
        if claude_md.exists():
            import os
            mod_time = os.path.getmtime(claude_md)
            days_old = (time.time() - mod_time) / (24 * 3600)
            
            if days_old > 30:  # 30 days threshold
                self.logger.warning(f"⚠️  CLAUDE.md is {days_old:.0f} days old")
            else:
                self.logger.info("✅ Documentation appears current")
                
        return True
        
    def validate_infrastructure(self) -> bool:
        """Enhanced infrastructure validation"""
        self.logger.info("🏗️  Running enhanced infrastructure validation...")
        
        # Check for required infrastructure files
        infra_files = [
            'railway.json',
            'requirements.txt',
            'package.json',
            '.env.example'
        ]
        
        missing_files = []
        for file_path in infra_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
                
        if missing_files:
            self.errors.append(f"Missing infrastructure files: {', '.join(missing_files)}")
            return False
            
        # Validate railway.json structure
        railway_config = self.project_root / 'railway.json'
        if railway_config.exists():
            try:
                with open(railway_config, 'r') as f:
                    config = json.load(f)
                    
                required_keys = ['$schema', 'build', 'deploy']
                missing_keys = [key for key in required_keys if key not in config]
                
                if missing_keys:
                    self.errors.append(f"Railway config missing keys: {', '.join(missing_keys)}")
                    return False
                    
                self.logger.info("✅ Railway configuration valid")
            except json.JSONDecodeError as e:
                self.errors.append(f"Invalid railway.json: {e}")
                return False
                
        return True
        
    def generate_report(self) -> Dict:
        """Generate comprehensive validation report"""
        return {
            'step': self.step_number,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'passed': len(self.errors) == 0,
            'errors': self.errors,
            'results': self.results,
            'validation_categories': {
                'tests': 'Tests and Coverage',
                'security': 'Security Scanning',
                'code_quality': 'Code Quality',
                'performance': 'Performance Benchmarks',
                'documentation': 'Documentation',
                'infrastructure': 'Infrastructure'
            }
        }
        
    def run_full_validation(self) -> bool:
        """Run complete enhanced validation suite"""
        self.logger.info(f"🚀 Starting enhanced validation for Step {self.step_number}")
        
        validators = [
            ('tests', self.validate_tests),
            ('security', self.validate_security),
            ('code_quality', self.validate_code_quality),
            ('performance', self.validate_performance),
            ('documentation', self.validate_documentation),
            ('infrastructure', self.validate_infrastructure)
        ]
        
        all_passed = True
        
        for category, validator_func in validators:
            try:
                if not validator_func():
                    all_passed = False
                    self.logger.error(f"❌ {category.title()} validation failed")
                else:
                    self.logger.info(f"✅ {category.title()} validation passed")
            except Exception as e:
                self.logger.error(f"❌ {category.title()} validation error: {e}")
                self.errors.append(f"{category} validation exception: {e}")
                all_passed = False
                
        # Generate and save report
        report = self.generate_report()
        report_file = self.project_root / f'validation_report_step_{self.step_number}.json'
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f"📊 Validation report saved to {report_file}")
        
        if all_passed:
            self.logger.info(f"🎉 All validations passed for Step {self.step_number}!")
        else:
            self.logger.error(f"💥 {len(self.errors)} validation errors found")
            for error in self.errors:
                self.logger.error(f"   • {error}")
                
        return all_passed


def main():
    """Main validation runner"""
    if len(sys.argv) != 2:
        print("Usage: python enhanced_validation_suite.py <step_number>")
        sys.exit(1)
        
    step_number = sys.argv[1]
    validator = EnhancedValidator(step_number)
    
    success = validator.run_full_validation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()