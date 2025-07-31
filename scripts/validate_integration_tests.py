#!/usr/bin/env python3
"""
Validation script for integration tests.

This script validates that integration tests are properly implemented,
test real service boundaries, and follow best practices.
"""

import ast
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class IntegrationTestValidator:
    """Validates integration test implementation and quality."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tests_dir = project_root / "tests" / "integration"
        self.validation_results = {
            "total_files": 0,
            "total_tests": 0,
            "placeholder_tests": 0,
            "real_tests": 0,
            "test_coverage": {},
            "issues": [],
            "warnings": []
        }
    
    def validate_all(self) -> Dict:
        """Run all validation checks."""
        print("🔍 Validating integration tests...")
        
        # Check test structure
        self._validate_test_structure()
        
        # Analyze test files
        self._analyze_test_files()
        
        # Check test coverage
        self._check_service_coverage()
        
        # Run integration tests
        self._run_integration_tests()
        
        # Generate report
        self._generate_report()
        
        return self.validation_results
    
    def _validate_test_structure(self):
        """Validate the test directory structure."""
        if not self.tests_dir.exists():
            self.validation_results["issues"].append(
                "Integration tests directory not found at tests/integration/"
            )
            return
        
        required_files = [
            "__init__.py",
            "test_service_interactions.py",
            "test_api.py",
            "test_endpoints.py"
        ]
        
        for required_file in required_files:
            file_path = self.tests_dir / required_file
            if not file_path.exists():
                self.validation_results["warnings"].append(
                    f"Expected integration test file not found: {required_file}"
                )
    
    def _analyze_test_files(self):
        """Analyze each test file for quality and completeness."""
        test_files = list(self.tests_dir.glob("test_*.py"))
        self.validation_results["total_files"] = len(test_files)
        
        for test_file in test_files:
            self._analyze_single_file(test_file)
    
    def _analyze_single_file(self, file_path: Path):
        """Analyze a single test file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Count test methods
            test_count = 0
            placeholder_count = 0
            integration_markers = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check test methods inside classes
                    class_has_integration_marker = self._has_integration_marker(node)
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                            test_count += 1
                            
                            # Check if it's a placeholder
                            if self._is_placeholder_test(item):
                                placeholder_count += 1
                            
                            # Check for integration marker
                            if class_has_integration_marker or self._has_integration_marker(item):
                                integration_markers += 1
                
                elif isinstance(node, ast.FunctionDef):
                    # Top-level test functions
                    if node.name.startswith("test_"):
                        test_count += 1
                        
                        # Check if it's a placeholder
                        if self._is_placeholder_test(node):
                            placeholder_count += 1
                        
                        # Check for integration marker
                        if self._has_integration_marker(node):
                            integration_markers += 1
            
            # Update results
            self.validation_results["total_tests"] += test_count
            self.validation_results["placeholder_tests"] += placeholder_count
            self.validation_results["real_tests"] += (test_count - placeholder_count)
            
            # Check for common issues
            issues = self._check_common_issues(content, file_path)
            self.validation_results["issues"].extend(issues)
            
            # Track coverage
            relative_path = file_path.relative_to(self.tests_dir)
            self.validation_results["test_coverage"][str(relative_path)] = {
                "total_tests": test_count,
                "placeholder_tests": placeholder_count,
                "real_tests": test_count - placeholder_count,
                "has_integration_markers": integration_markers > 0
            }
            
        except Exception as e:
            self.validation_results["issues"].append(
                f"Error analyzing {file_path}: {str(e)}"
            )
    
    def _is_placeholder_test(self, node: ast.FunctionDef) -> bool:
        """Check if a test function is a placeholder."""
        # Check for pass statement
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            return True
        
        # Check for NotImplementedError
        for stmt in node.body:
            if isinstance(stmt, ast.Raise):
                if isinstance(stmt.exc, ast.Call):
                    if hasattr(stmt.exc.func, 'id') and stmt.exc.func.id == 'NotImplementedError':
                        return True
        
        # Check for TODO comments
        if node.body and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant):
                if "TODO" in str(node.body[0].value.value) or "placeholder" in str(node.body[0].value.value).lower():
                    return True
        
        return False
    
    def _has_integration_marker(self, node) -> bool:
        """Check if a node has pytest.mark.integration decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute):
                if (hasattr(decorator.value, 'attr') and 
                    decorator.value.attr == 'mark' and
                    hasattr(decorator, 'attr') and
                    decorator.attr == 'integration'):
                    return True
            elif isinstance(decorator, ast.Name) and decorator.id == 'integration':
                return True
        return False
    
    def _check_common_issues(self, content: str, file_path: Path) -> List[str]:
        """Check for common issues in test files."""
        issues = []
        
        # Check for proper mocking
        if "mock" not in content.lower() and "patch" not in content.lower():
            issues.append(f"{file_path}: No mocking found - integration tests should mock external dependencies")
        
        # Check for assertions
        if "assert" not in content:
            issues.append(f"{file_path}: No assertions found")
        
        # Check for async tests
        if "async def test_" in content and "@pytest.mark.asyncio" not in content:
            issues.append(f"{file_path}: Async tests found without @pytest.mark.asyncio decorator")
        
        # Check for service imports
        if "from app.services" not in content and "test_service" in str(file_path):
            issues.append(f"{file_path}: Service test file doesn't import any services")
        
        return issues
    
    def _check_service_coverage(self):
        """Check which services have integration tests."""
        services_dir = self.project_root / "app" / "services"
        if not services_dir.exists():
            return
        
        # Get all service files
        service_files = [f.stem for f in services_dir.glob("*.py") if f.stem != "__init__"]
        
        # Check which services are tested
        tested_services = set()
        
        for test_file in self.tests_dir.glob("test_*.py"):
            with open(test_file, 'r') as f:
                content = f.read()
                
            for service in service_files:
                if service in content:
                    tested_services.add(service)
        
        # Report untested services
        untested_services = set(service_files) - tested_services
        if untested_services:
            self.validation_results["warnings"].append(
                f"Services without integration tests: {', '.join(sorted(untested_services))}"
            )
    
    def _run_integration_tests(self):
        """Run integration tests and capture results."""
        print("🏃 Running integration tests...")
        
        try:
            # Run pytest with integration marker
            result = subprocess.run(
                ["pytest", "-m", "integration", "-v", "--tb=short", "--json-report", "--json-report-file=integration_test_report.json"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            # Parse results
            if Path("integration_test_report.json").exists():
                with open("integration_test_report.json", 'r') as f:
                    test_report = json.load(f)
                
                self.validation_results["test_run"] = {
                    "total": test_report.get("summary", {}).get("total", 0),
                    "passed": test_report.get("summary", {}).get("passed", 0),
                    "failed": test_report.get("summary", {}).get("failed", 0),
                    "skipped": test_report.get("summary", {}).get("skipped", 0),
                    "duration": test_report.get("duration", 0)
                }
                
                # Clean up report file
                os.remove("integration_test_report.json")
            else:
                # Fallback to parsing stdout
                self.validation_results["test_run"] = {
                    "output": result.stdout,
                    "errors": result.stderr,
                    "return_code": result.returncode
                }
                
        except Exception as e:
            self.validation_results["issues"].append(f"Failed to run integration tests: {str(e)}")
    
    def _generate_report(self):
        """Generate validation report."""
        print("\n" + "="*60)
        print("INTEGRATION TEST VALIDATION REPORT")
        print("="*60)
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"  Total test files: {self.validation_results['total_files']}")
        print(f"  Total tests: {self.validation_results['total_tests']}")
        print(f"  Real tests: {self.validation_results['real_tests']}")
        print(f"  Placeholder tests: {self.validation_results['placeholder_tests']}")
        
        # Test run results
        if "test_run" in self.validation_results:
            print(f"\n🏃 Test Run Results:")
            if "total" in self.validation_results["test_run"]:
                run = self.validation_results["test_run"]
                print(f"  Total: {run['total']}")
                print(f"  Passed: {run['passed']}")
                print(f"  Failed: {run['failed']}")
                print(f"  Skipped: {run['skipped']}")
                print(f"  Duration: {run['duration']:.2f}s")
            else:
                print(f"  Return code: {self.validation_results['test_run'].get('return_code', 'N/A')}")
        
        # Coverage by file
        print(f"\n📁 Test Coverage by File:")
        for file_path, coverage in self.validation_results["test_coverage"].items():
            marker = "✅" if coverage["has_integration_markers"] else "⚠️"
            print(f"  {marker} {file_path}:")
            print(f"     Total: {coverage['total_tests']}, Real: {coverage['real_tests']}, Placeholders: {coverage['placeholder_tests']}")
        
        # Issues
        if self.validation_results["issues"]:
            print(f"\n❌ Issues Found ({len(self.validation_results['issues'])}):")
            for issue in self.validation_results["issues"]:
                print(f"  - {issue}")
        
        # Warnings
        if self.validation_results["warnings"]:
            print(f"\n⚠️  Warnings ({len(self.validation_results['warnings'])}):")
            for warning in self.validation_results["warnings"]:
                print(f"  - {warning}")
        
        # Score
        if self.validation_results["total_tests"] > 0:
            real_test_percentage = (self.validation_results["real_tests"] / self.validation_results["total_tests"]) * 100
            print(f"\n🎯 Integration Test Quality Score: {real_test_percentage:.1f}%")
            
            if real_test_percentage >= 90:
                print("   Status: EXCELLENT ✨")
            elif real_test_percentage >= 70:
                print("   Status: GOOD 👍")
            elif real_test_percentage >= 50:
                print("   Status: NEEDS IMPROVEMENT 📈")
            else:
                print("   Status: POOR ❌")
        
        print("\n" + "="*60)


def main():
    """Main entry point."""
    # Get project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    
    # Run validation
    validator = IntegrationTestValidator(project_root)
    results = validator.validate_all()
    
    # Save results to file
    output_file = project_root / "integration_test_validation_report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Full report saved to: {output_file}")
    
    # Exit with appropriate code
    if results["issues"] or results["placeholder_tests"] > results["real_tests"]:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()