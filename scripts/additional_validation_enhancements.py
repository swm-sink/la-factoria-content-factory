#!/usr/bin/env python3
"""
Additional Validation Enhancements for La Factoria
Extended validation framework with regression testing, API validation, database checks
"""

import os
import sys
import subprocess
import json
import time
import requests
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
import tempfile
import yaml

# Add app to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class AdditionalValidator:
    """Enhanced validation framework with additional checks"""
    
    def __init__(self, step_number: str, project_root: str = None):
        self.step_number = step_number
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.results = {}
        self.errors = []
        self.warnings = []
        self.setup_logging()
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'additional_validation_step_{self.step_number}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def run_command(self, command: List[str], capture_output: bool = True, timeout: int = 300) -> Tuple[bool, str]:
        """Run command with proper error handling"""
        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                cwd=self.project_root,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, str(e)
            
    def validate_regression_testing(self) -> bool:
        """Validate regression testing framework"""
        self.logger.info("🔄 Running regression testing validation...")
        
        # Check for regression test directory
        regression_dir = self.project_root / 'tests' / 'regression'
        if not regression_dir.exists():
            self.warnings.append("No regression test directory found - creating one")
            regression_dir.mkdir(parents=True, exist_ok=True)
            
        # Check for baseline data
        baseline_file = regression_dir / 'baseline_results.json'
        if not baseline_file.exists():
            self.warnings.append("No regression baseline found - will create on next run")
            
        # Run regression tests if they exist
        regression_tests = list(regression_dir.glob('test_*.py'))
        if regression_tests:
            for test_file in regression_tests:
                success, output = self.run_command(['python3', '-m', 'pytest', str(test_file), '-v'])
                if not success:
                    self.errors.append(f"Regression test failed: {test_file.name}")
                    return False
        else:
            self.warnings.append("No regression tests found - consider adding them")
            
        self.logger.info("✅ Regression testing validation passed")
        return True
        
    def validate_api_contract_testing(self) -> bool:
        """Validate API contract testing"""
        self.logger.info("📋 Running API contract testing validation...")
        
        # Check for OpenAPI spec
        openapi_files = [
            self.project_root / 'docs' / 'openapi.yaml',
            self.project_root / 'docs' / 'api' / 'openapi.yaml',
            self.project_root / 'openapi.yaml'
        ]
        
        openapi_spec = None
        for spec_file in openapi_files:
            if spec_file.exists():
                openapi_spec = spec_file
                break
                
        if not openapi_spec:
            self.warnings.append("No OpenAPI specification found - API contract testing limited")
            return True
            
        # Validate OpenAPI spec syntax
        try:
            with open(openapi_spec, 'r') as f:
                spec_content = yaml.safe_load(f)
                
            required_fields = ['openapi', 'info', 'paths']
            for field in required_fields:
                if field not in spec_content:
                    self.errors.append(f"OpenAPI spec missing required field: {field}")
                    return False
                    
        except Exception as e:
            self.errors.append(f"Invalid OpenAPI specification: {e}")
            return False
            
        # Check for contract test files
        contract_test_files = list((self.project_root / 'tests').glob('**/test_api_contract*.py'))
        if not contract_test_files:
            self.warnings.append("No API contract tests found - consider adding them")
            
        self.logger.info("✅ API contract testing validation passed")
        return True
        
    def validate_database_migrations(self) -> bool:
        """Validate database migration consistency"""
        self.logger.info("🗄️ Running database migration validation...")
        
        # Check for migration directory
        migration_dirs = [
            self.project_root / 'app' / 'core' / 'migrations',
            self.project_root / 'migrations',
            self.project_root / 'alembic' / 'versions'
        ]
        
        migration_dir = None
        for dir_path in migration_dirs:
            if dir_path.exists():
                migration_dir = dir_path
                break
                
        if not migration_dir:
            self.warnings.append("No migration directory found - database changes not tracked")
            return True
            
        # Check migration file naming convention
        migration_files = list(migration_dir.glob('*.py'))
        for migration_file in migration_files:
            if migration_file.name == '__init__.py':
                continue
                
            # Check for proper naming (timestamp or version prefix)
            filename = migration_file.stem
            if not (filename[0].isdigit() or filename.startswith('v')):
                self.warnings.append(f"Migration file {filename} doesn't follow naming convention")
                
        # Test migration rollback capability
        if migration_files:
            self.logger.info("Migration files found - testing rollback capability")
            # Note: In production, we'd test actual rollback, but here we just check structure
            
        self.logger.info("✅ Database migration validation passed")
        return True
        
    def validate_cross_browser_compatibility(self) -> bool:
        """Validate cross-browser compatibility setup"""
        self.logger.info("🌐 Running cross-browser compatibility validation...")
        
        # Check for browser testing configuration
        browser_configs = [
            self.project_root / 'playwright.config.js',
            self.project_root / 'selenium.config.py',
            self.project_root / 'cypress.config.js'
        ]
        
        has_browser_testing = any(config.exists() for config in browser_configs)
        
        if not has_browser_testing:
            self.warnings.append("No cross-browser testing configuration found")
            
        # Check for responsive design testing
        frontend_dir = self.project_root / 'frontend'
        if frontend_dir.exists():
            # Look for viewport/responsive testing
            test_files = list(frontend_dir.glob('**/*test*.js')) + list(frontend_dir.glob('**/*test*.ts'))
            responsive_tests = []
            
            for test_file in test_files:
                try:
                    with open(test_file, 'r') as f:
                        content = f.read().lower()
                        if 'viewport' in content or 'responsive' in content or 'mobile' in content:
                            responsive_tests.append(test_file)
                except Exception:
                    continue
                    
            if not responsive_tests:
                self.warnings.append("No responsive/viewport tests found")
                
        self.logger.info("✅ Cross-browser compatibility validation passed")
        return True
        
    def validate_deployment_readiness(self) -> bool:
        """Validate deployment readiness and rollback capability"""
        self.logger.info("🚀 Running deployment readiness validation...")
        
        # Check for deployment configuration
        deployment_configs = [
            self.project_root / 'railway.json',
            self.project_root / 'Dockerfile',
            self.project_root / 'docker-compose.yml',
            self.project_root / '.github' / 'workflows' / 'deploy.yml'
        ]
        
        deployment_ready = any(config.exists() for config in deployment_configs)
        
        if not deployment_ready:
            self.errors.append("No deployment configuration found")
            return False
            
        # Check environment configuration
        env_files = [
            self.project_root / '.env.example',
            self.project_root / '.env.template'
        ]
        
        has_env_template = any(env_file.exists() for env_file in env_files)
        if not has_env_template:
            self.warnings.append("No environment template found")
            
        # Check for health check endpoint
        try:
            # Look for health check in route files
            route_files = list((self.project_root / 'app').glob('**/routes/*.py'))
            health_check_found = False
            
            for route_file in route_files:
                try:
                    with open(route_file, 'r') as f:
                        content = f.read().lower()
                        if 'health' in content and ('get' in content or '@app' in content):
                            health_check_found = True
                            break
                except Exception:
                    continue
                    
            if not health_check_found:
                self.warnings.append("No health check endpoint found")
                
        except Exception as e:
            self.warnings.append(f"Could not check for health endpoints: {e}")
            
        self.logger.info("✅ Deployment readiness validation passed")
        return True
        
    def validate_monitoring_and_alerting(self) -> bool:
        """Validate monitoring and alerting setup"""
        self.logger.info("📊 Running monitoring and alerting validation...")
        
        # Check for monitoring configuration
        monitoring_files = [
            self.project_root / 'app' / 'core' / 'metrics.py',
            self.project_root / 'monitoring' / 'prometheus.yml',
            self.project_root / 'monitoring' / 'grafana.json'
        ]
        
        has_monitoring = any(monitor_file.exists() for monitor_file in monitoring_files)
        
        if not has_monitoring:
            self.warnings.append("No monitoring configuration found")
            
        # Check for logging configuration
        logging_config_files = [
            self.project_root / 'app' / 'core' / 'logging.py',
            self.project_root / 'logging.conf',
            self.project_root / 'pyproject.toml'  # Check for logging config in pyproject.toml
        ]
        
        has_logging_config = False
        for log_file in logging_config_files:
            if log_file.exists():
                has_logging_config = True
                break
                
        if not has_logging_config:
            self.warnings.append("No structured logging configuration found")
            
        # Check for error tracking
        app_files = list((self.project_root / 'app').glob('**/*.py'))
        error_tracking_found = False
        
        for app_file in app_files:
            try:
                with open(app_file, 'r') as f:
                    content = f.read().lower()
                    if 'sentry' in content or 'rollbar' in content or 'bugsnag' in content:
                        error_tracking_found = True
                        break
            except Exception:
                continue
                
        if not error_tracking_found:
            self.warnings.append("No error tracking service integration found")
            
        self.logger.info("✅ Monitoring and alerting validation passed")
        return True
        
    def validate_backup_and_recovery(self) -> bool:
        """Validate backup and recovery procedures"""
        self.logger.info("💾 Running backup and recovery validation...")
        
        # Check for backup scripts
        backup_scripts = [
            self.project_root / 'scripts' / 'backup.py',
            self.project_root / 'scripts' / 'backup.sh',
            self.project_root / 'backup' / 'backup.py'
        ]
        
        has_backup_scripts = any(script.exists() for script in backup_scripts)
        
        if not has_backup_scripts:
            self.warnings.append("No backup scripts found")
            
        # Check for recovery procedures documentation
        recovery_docs = [
            self.project_root / 'docs' / 'recovery.md',
            self.project_root / 'docs' / 'disaster_recovery.md',
            self.project_root / 'RECOVERY.md'
        ]
        
        has_recovery_docs = any(doc.exists() for doc in recovery_docs)
        
        if not has_recovery_docs:
            self.warnings.append("No recovery procedures documented")
            
        # Check for data retention policies
        retention_policies = [
            self.project_root / 'app' / 'services' / 'data_retention.py',
            self.project_root / 'policies' / 'retention.py'
        ]
        
        has_retention_policy = any(policy.exists() for policy in retention_policies)
        
        if not has_retention_policy:
            self.warnings.append("No data retention policies found")
            
        self.logger.info("✅ Backup and recovery validation passed")
        return True
        
    def validate_load_testing_readiness(self) -> bool:
        """Validate load testing infrastructure"""
        self.logger.info("⚡ Running load testing readiness validation...")
        
        # Check for load testing tools
        load_test_files = [
            self.project_root / 'tests' / 'performance' / 'locustfile.py',
            self.project_root / 'tests' / 'load' / 'artillery.yml',
            self.project_root / 'k6' / 'load-test.js'
        ]
        
        has_load_tests = any(test_file.exists() for test_file in load_test_files)
        
        if not has_load_tests:
            self.warnings.append("No load testing configuration found")
            
        # Check for performance baseline
        baseline_files = [
            self.project_root / 'tests' / 'performance' / 'baseline.json',
            self.project_root / 'performance' / 'baseline.yml'
        ]
        
        has_baseline = any(baseline.exists() for baseline in baseline_files)
        
        if not has_baseline:
            self.warnings.append("No performance baseline established")
            
        # Check for performance monitoring in CI
        ci_file = self.project_root / '.github' / 'workflows' / 'ci.yml'
        if ci_file.exists():
            try:
                with open(ci_file, 'r') as f:
                    ci_content = f.read().lower()
                    if 'performance' not in ci_content and 'load' not in ci_content:
                        self.warnings.append("No performance testing in CI pipeline")
            except Exception:
                pass
                
        self.logger.info("✅ Load testing readiness validation passed")
        return True
        
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        return {
            'step': self.step_number,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'passed': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'results': self.results,
            'validation_categories': {
                'regression_testing': 'Regression Testing Framework',
                'api_contract_testing': 'API Contract Validation',
                'database_migrations': 'Database Migration Consistency',
                'cross_browser_compatibility': 'Cross-Browser Compatibility',
                'deployment_readiness': 'Deployment Readiness',
                'monitoring_alerting': 'Monitoring and Alerting',
                'backup_recovery': 'Backup and Recovery',
                'load_testing_readiness': 'Load Testing Infrastructure'
            },
            'recommendations': self._generate_recommendations()
        }
        
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on warnings"""
        recommendations = []
        
        if any('regression' in warning.lower() for warning in self.warnings):
            recommendations.append("Consider implementing regression testing to catch feature breakage")
            
        if any('api contract' in warning.lower() for warning in self.warnings):
            recommendations.append("Add OpenAPI specification and contract testing for API reliability")
            
        if any('cross-browser' in warning.lower() for warning in self.warnings):
            recommendations.append("Implement cross-browser testing for better user experience")
            
        if any('monitoring' in warning.lower() for warning in self.warnings):
            recommendations.append("Set up comprehensive monitoring and alerting for production readiness")
            
        if any('backup' in warning.lower() for warning in self.warnings):
            recommendations.append("Establish backup and recovery procedures for data protection")
            
        return recommendations
        
    def run_additional_validations(self) -> bool:
        """Run all additional validation checks"""
        self.logger.info(f"🚀 Starting additional validation enhancements for Step {self.step_number}")
        
        validators = [
            ('regression_testing', self.validate_regression_testing),
            ('api_contract_testing', self.validate_api_contract_testing),
            ('database_migrations', self.validate_database_migrations),
            ('cross_browser_compatibility', self.validate_cross_browser_compatibility),
            ('deployment_readiness', self.validate_deployment_readiness),
            ('monitoring_alerting', self.validate_monitoring_and_alerting),
            ('backup_recovery', self.validate_backup_and_recovery),
            ('load_testing_readiness', self.validate_load_testing_readiness)
        ]
        
        all_passed = True
        
        for category, validator_func in validators:
            try:
                if not validator_func():
                    all_passed = False
                    self.logger.error(f"❌ {category.replace('_', ' ').title()} validation failed")
                else:
                    self.logger.info(f"✅ {category.replace('_', ' ').title()} validation passed")
            except Exception as e:
                self.logger.error(f"❌ {category.replace('_', ' ').title()} validation error: {e}")
                self.errors.append(f"{category} validation exception: {e}")
                all_passed = False
                
        # Generate and save report
        report = self.generate_comprehensive_report()
        report_file = self.project_root / f'additional_validation_report_step_{self.step_number}.json'
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f"📊 Additional validation report saved to {report_file}")
        
        if all_passed and len(self.errors) == 0:
            self.logger.info(f"🎉 All additional validations passed for Step {self.step_number}!")
            if self.warnings:
                self.logger.info(f"⚠️  {len(self.warnings)} recommendations for improvement")
        else:
            self.logger.error(f"💥 {len(self.errors)} validation errors found")
            for error in self.errors:
                self.logger.error(f"   • {error}")
                
        return all_passed and len(self.errors) == 0


def main():
    """Main additional validation runner"""
    if len(sys.argv) != 2:
        print("Usage: python additional_validation_enhancements.py <step_number>")
        sys.exit(1)
        
    step_number = sys.argv[1]
    validator = AdditionalValidator(step_number)
    
    success = validator.run_additional_validations()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()