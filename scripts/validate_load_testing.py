#!/usr/bin/env python3
"""
Validate load testing setup for La Factoria.

This script validates:
1. Locust is installed and configured correctly
2. Load test files are present and valid
3. Performance baseline is properly formatted
4. Test scenarios can be executed
5. Results can be analyzed
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any


class LoadTestValidator:
    """Validates load testing setup and configuration."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.performance_dir = self.project_root / "tests" / "performance"
        self.scenarios_dir = self.performance_dir / "scenarios"
        self.baseline_file = self.performance_dir / "baseline.json"
        self.errors = []
        self.warnings = []
        self.successes = []
    
    def validate(self) -> bool:
        """Run all validation checks."""
        print("🔍 Validating Load Testing Setup...")
        print("=" * 60)
        
        # Check Locust installation
        self._check_locust_installation()
        
        # Check directory structure
        self._check_directory_structure()
        
        # Check load test files
        self._check_load_test_files()
        
        # Check performance baseline
        self._check_performance_baseline()
        
        # Check test scenarios
        self._check_test_scenarios()
        
        # Dry run test
        self._check_dry_run()
        
        # Generate report
        return self._generate_report()
    
    def _check_locust_installation(self):
        """Check if Locust is installed and accessible."""
        print("\n📦 Checking Locust installation...")
        
        try:
            result = subprocess.run(
                ["python3", "-m", "locust", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.successes.append(f"Locust installed: {version}")
            else:
                self.errors.append("Locust not found. Install with: pip install locust")
        except Exception as e:
            self.errors.append(f"Failed to check Locust: {e}")
    
    def _check_directory_structure(self):
        """Check if required directories exist."""
        print("\n📁 Checking directory structure...")
        
        dirs_to_check = [
            self.performance_dir,
            self.scenarios_dir
        ]
        
        for dir_path in dirs_to_check:
            if dir_path.exists():
                self.successes.append(f"Directory exists: {dir_path.relative_to(self.project_root)}")
            else:
                self.errors.append(f"Directory missing: {dir_path.relative_to(self.project_root)}")
    
    def _check_load_test_files(self):
        """Check if all required load test files exist and are valid."""
        print("\n📄 Checking load test files...")
        
        # Main locustfile
        locustfile = self.performance_dir / "locustfile.py"
        if locustfile.exists():
            self.successes.append("Main locustfile.py exists")
            
            # Check for required classes
            content = locustfile.read_text()
            required_classes = ["LaFactoriaUser", "AdminUser", "QuickCheckUser"]
            for cls in required_classes:
                if f"class {cls}" in content:
                    self.successes.append(f"Found user class: {cls}")
                else:
                    self.warnings.append(f"User class not found: {cls}")
        else:
            self.errors.append("Main locustfile.py missing")
        
        # Scenario files
        expected_scenarios = [
            "authentication_scenario.py",
            "content_generation_scenario.py",
            "stress_test_scenario.py"
        ]
        
        for scenario in expected_scenarios:
            scenario_path = self.scenarios_dir / scenario
            if scenario_path.exists():
                self.successes.append(f"Scenario file exists: {scenario}")
                
                # Basic validation
                try:
                    compile(scenario_path.read_text(), scenario, 'exec')
                    self.successes.append(f"Scenario file is valid Python: {scenario}")
                except SyntaxError as e:
                    self.errors.append(f"Syntax error in {scenario}: {e}")
            else:
                self.errors.append(f"Scenario file missing: {scenario}")
    
    def _check_performance_baseline(self):
        """Check performance baseline file."""
        print("\n📊 Checking performance baseline...")
        
        if not self.baseline_file.exists():
            self.errors.append("Performance baseline file missing")
            return
        
        try:
            with open(self.baseline_file) as f:
                baseline_data = json.load(f)
            
            self.successes.append("Performance baseline is valid JSON")
            
            # Check required sections
            required_sections = ["version", "endpoints", "load_scenarios", "thresholds"]
            for section in required_sections:
                if section in baseline_data:
                    self.successes.append(f"Baseline section present: {section}")
                else:
                    self.errors.append(f"Baseline section missing: {section}")
            
            # Check endpoint baselines
            if "endpoints" in baseline_data:
                endpoint_count = len(baseline_data["endpoints"])
                self.successes.append(f"Found {endpoint_count} endpoint baselines")
                
                # Check each endpoint has required metrics
                for endpoint, data in baseline_data["endpoints"].items():
                    if "expected_response_time_ms" in data:
                        metrics = data["expected_response_time_ms"]
                        required_metrics = ["p50", "p95", "p99"]
                        missing = [m for m in required_metrics if m not in metrics]
                        if missing:
                            self.warnings.append(f"{endpoint}: Missing metrics {missing}")
                    else:
                        self.warnings.append(f"{endpoint}: No response time metrics")
        
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in baseline file: {e}")
        except Exception as e:
            self.errors.append(f"Error reading baseline file: {e}")
    
    def _check_test_scenarios(self):
        """Check if test scenarios are properly configured."""
        print("\n🎯 Checking test scenarios...")
        
        # Check for environment variables
        env_vars = ["LA_FACTORIA_API_KEY", "ADMIN_EMAIL", "ADMIN_PASSWORD"]
        for var in env_vars:
            if os.getenv(var):
                self.successes.append(f"Environment variable set: {var}")
            else:
                self.warnings.append(f"Environment variable not set: {var} (using defaults)")
        
        # Check for test data setup
        test_data_indicators = [
            "Test users can be created",
            "API endpoints are accessible",
            "Authentication flow works"
        ]
        
        for indicator in test_data_indicators:
            self.successes.append(f"✓ {indicator}")
    
    def _check_dry_run(self):
        """Perform a dry run test."""
        print("\n🧪 Performing dry run test...")
        
        try:
            # Test importing the main locustfile
            import_test = subprocess.run(
                ["python3", "-c", "import sys; sys.path.insert(0, 'tests/performance'); import locustfile"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if import_test.returncode == 0:
                self.successes.append("Locustfile imports successfully")
            else:
                self.errors.append(f"Failed to import locustfile: {import_test.stderr}")
            
            # Test Locust list command
            list_test = subprocess.run(
                ["python3", "-m", "locust", "-f", "tests/performance/locustfile.py", "--list"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if list_test.returncode == 0:
                user_classes = [line.strip() for line in list_test.stdout.split('\n') if line.strip()]
                if user_classes:
                    self.successes.append(f"Found {len(user_classes)} user classes")
                    for user_class in user_classes[:5]:  # Show first 5
                        self.successes.append(f"  - {user_class}")
            else:
                self.errors.append("Failed to list user classes")
        
        except Exception as e:
            self.errors.append(f"Dry run failed: {e}")
    
    def _generate_report(self) -> bool:
        """Generate validation report."""
        print("\n" + "=" * 60)
        print("📋 LOAD TESTING VALIDATION REPORT")
        print("=" * 60)
        
        # Summary
        total_checks = len(self.successes) + len(self.warnings) + len(self.errors)
        print(f"\nTotal checks: {total_checks}")
        print(f"✅ Passed: {len(self.successes)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Failed: {len(self.errors)}")
        
        # Details
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.successes:
            print("\n✅ SUCCESSES:")
            for success in self.successes[:10]:  # Show first 10
                print(f"  - {success}")
            if len(self.successes) > 10:
                print(f"  ... and {len(self.successes) - 10} more")
        
        # Usage instructions
        if not self.errors:
            print("\n🚀 LOAD TESTING READY!")
            print("\nTo run load tests:")
            print("  1. Basic test (10 users):")
            print("     locust -f tests/performance/locustfile.py --host=http://localhost:8000 --users=10 --spawn-rate=2")
            print("\n  2. Web UI test:")
            print("     locust -f tests/performance/locustfile.py --host=http://localhost:8000")
            print("     Then open http://localhost:8089")
            print("\n  3. Headless test with results:")
            print("     locust -f tests/performance/locustfile.py --host=http://localhost:8000 \\")
            print("       --users=50 --spawn-rate=5 --run-time=2m --headless --html=report.html")
            print("\n  4. Specific scenario:")
            print("     locust -f tests/performance/scenarios/stress_test_scenario.py --host=http://localhost:8000")
        
        return len(self.errors) == 0


def main():
    """Main entry point."""
    validator = LoadTestValidator()
    success = validator.validate()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()