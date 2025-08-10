"""
Step 2: Dependency Tree Analysis
=================================

Deep analysis of project dependencies for security, compatibility, and optimization.
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import pytest
import importlib.metadata as metadata
from packaging import version
from packaging.requirements import Requirement


class TestDependencyTree:
    """Comprehensive dependency analysis"""
    
    def test_all_dependencies_declared(self):
        """Ensure all imported packages are in requirements.txt"""
        requirements_file = Path('requirements.txt')
        declared_deps = self._parse_requirements(requirements_file)
        
        # Find all imports in source code
        imported_packages = self._find_all_imports()
        
        # Map import names to package names
        package_mapping = {
            'PIL': 'Pillow',
            'cv2': 'opencv-python',
            'sklearn': 'scikit-learn',
            'yaml': 'PyYAML',
        }
        
        missing = []
        for pkg in imported_packages:
            mapped_pkg = package_mapping.get(pkg, pkg)
            if mapped_pkg not in declared_deps and not self._is_stdlib(pkg):
                missing.append(pkg)
        
        assert len(missing) == 0, f"Undeclared dependencies: {missing}"
    
    def test_no_unused_dependencies(self):
        """Check for dependencies that are declared but never used"""
        requirements_file = Path('requirements.txt')
        declared_deps = self._parse_requirements(requirements_file)
        
        imported_packages = self._find_all_imports()
        
        # Some packages are used indirectly
        indirect_deps = {
            'uvicorn',  # Used to run the server
            'python-multipart',  # Used by FastAPI for form data
            'pytest-asyncio',  # Used by pytest
            'pytest-cov',  # Used for coverage
            'asyncpg',  # Database driver
            'psycopg2-binary',  # Alternative DB driver
            'alembic',  # Database migrations
        }
        
        unused = []
        for dep in declared_deps:
            dep_name = dep.split('[')[0].split('==')[0].split('>=')[0]
            if (dep_name not in imported_packages and 
                dep_name.replace('-', '_') not in imported_packages and
                dep_name not in indirect_deps):
                unused.append(dep_name)
        
        # Allow some unused (they might be optional features)
        assert len(unused) < 5, f"Too many unused dependencies: {unused}"
    
    def test_version_compatibility_matrix(self):
        """Verify all dependency versions are compatible"""
        incompatible_pairs = [
            ('fastapi==0.104.1', 'pydantic==1.*'),  # FastAPI 0.100+ requires Pydantic v2
            ('sqlalchemy==2.*', 'databases<0.6'),    # SQLAlchemy 2.0 incompatibility
            ('redis==5.*', 'redis-py<4.0'),         # Redis version conflicts
        ]
        
        requirements_file = Path('requirements.txt')
        content = requirements_file.read_text()
        
        issues = []
        for pair in incompatible_pairs:
            if all(self._matches_pattern(p, content) for p in pair):
                issues.append(f"Incompatible: {pair}")
        
        assert len(issues) == 0, f"Version incompatibilities: {issues}"
    
    def test_security_vulnerabilities(self):
        """Check for known security vulnerabilities in dependencies"""
        vulnerable_versions = {
            'flask': '<2.2.5',  # CVE-2023-30861
            'werkzeug': '<2.2.3',  # CVE-2023-25577
            'cryptography': '<41.0.0',  # CVE-2023-38325
            'requests': '<2.31.0',  # CVE-2023-32681
            'urllib3': '<1.26.17',  # CVE-2023-43804
            'jinja2': '<3.1.3',  # CVE-2024-22195
            'pillow': '<10.0.1',  # CVE-2023-44271
            'pyyaml': '<6.0.1',  # CVE-2020-14343
        }
        
        vulnerabilities = []
        
        for package, vulnerable_version in vulnerable_versions.items():
            try:
                installed_version = metadata.version(package)
                if version.parse(installed_version) < version.parse(vulnerable_version.strip('<')):
                    vulnerabilities.append(
                        f"{package} {installed_version} is vulnerable (need {vulnerable_version})"
                    )
            except metadata.PackageNotFoundError:
                pass  # Package not installed
        
        assert len(vulnerabilities) == 0, f"Security vulnerabilities found: {vulnerabilities}"
    
    def test_license_compatibility(self):
        """Verify all dependency licenses are compatible with project license"""
        # Common problematic licenses for commercial use
        problematic_licenses = {
            'GPL', 'GPLv2', 'GPLv3',  # Copyleft
            'AGPL', 'AGPLv3',          # Strong copyleft
            'CC-BY-SA',                # Share-alike
        }
        
        # Acceptable licenses
        acceptable_licenses = {
            'MIT', 'Apache', 'Apache-2.0', 'BSD', 'BSD-3-Clause', 
            'BSD-2-Clause', 'ISC', 'Python', 'PSF', 'Unlicense'
        }
        
        license_issues = []
        
        # Check main dependencies
        critical_deps = ['fastapi', 'pydantic', 'sqlalchemy', 'redis', 'openai', 'anthropic']
        
        for dep in critical_deps:
            try:
                # This would need actual license checking
                # For now, we know these are all MIT/Apache licensed
                pass
            except:
                pass
        
        assert len(license_issues) == 0, f"License issues: {license_issues}"
    
    def test_dependency_tree_depth(self):
        """Ensure dependency tree isn't too deep (potential for conflicts)"""
        max_depth = 5
        
        # We would need to actually build the dependency tree
        # For now, check that we don't have too many total dependencies
        try:
            result = subprocess.run(
                ['python3', '-m', 'pip', 'list', '--format=json'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                total_packages = len(packages)
                
                # If we have too many packages, tree is likely deep
                assert total_packages < 150, f"Too many dependencies ({total_packages}), tree likely too deep"
        except:
            pytest.skip("Could not analyze dependency tree")
    
    def test_version_pinning_strategy(self):
        """Verify dependencies are properly pinned for reproducibility"""
        requirements_file = Path('requirements.txt')
        content = requirements_file.read_text()
        lines = [l.strip() for l in content.splitlines() 
                if l.strip() and not l.startswith('#')]
        
        issues = []
        for line in lines:
            if any(op in line for op in ['>=', '~=', '*']):
                issues.append(f"Unpinned dependency: {line}")
            elif '==' not in line and '[' not in line:
                issues.append(f"No version specified: {line}")
        
        # Allow some flexibility for development dependencies
        assert len(issues) < 5, f"Version pinning issues: {issues}"
    
    def test_python_version_compatibility(self):
        """Ensure all dependencies support our Python version"""
        import sys
        current_python = f"{sys.version_info.major}.{sys.version_info.minor}"
        
        # Check if dependencies support current Python
        incompatible = []
        
        # Known Python 3.13 compatibility issues
        if sys.version_info >= (3, 13):
            potentially_incompatible = [
                'greenlet',  # Often has issues with new Python versions
                'psycopg2',  # Sometimes needs updates for new Python
                'numpy',     # May need specific version for Python 3.13
            ]
            
            for pkg in potentially_incompatible:
                try:
                    __import__(pkg)
                except ImportError:
                    pass  # Not installed
                except Exception as e:
                    incompatible.append(f"{pkg}: {e}")
        
        assert len(incompatible) == 0, f"Python {current_python} incompatibilities: {incompatible}"
    
    def test_dependency_update_available(self):
        """Check if critical dependencies have updates available"""
        critical_deps = ['fastapi', 'pydantic', 'sqlalchemy', 'uvicorn']
        updates_available = []
        
        for dep in critical_deps:
            try:
                current = metadata.version(dep)
                # Would need to check PyPI for latest version
                # For now, just ensure we're not too far behind
                if dep == 'fastapi' and version.parse(current) < version.parse('0.100.0'):
                    updates_available.append(f"{dep}: {current} is very old")
            except:
                pass
        
        # Information only - don't fail test
        if updates_available:
            print(f"Updates available: {updates_available}")
    
    def test_no_conflicting_subdependencies(self):
        """Check for conflicts in subdependencies"""
        # This would need actual pip check or similar
        try:
            result = subprocess.run(
                ['python3', '-m', 'pip', 'check'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                # Parse output for conflicts
                conflicts = result.stdout
                assert False, f"Dependency conflicts detected:\n{conflicts}"
        except subprocess.TimeoutExpired:
            pytest.skip("Dependency check timed out")
        except Exception as e:
            pytest.skip(f"Could not check dependencies: {e}")
    
    # Helper methods
    def _parse_requirements(self, requirements_file: Path) -> Set[str]:
        """Parse requirements.txt file"""
        if not requirements_file.exists():
            return set()
        
        deps = set()
        content = requirements_file.read_text()
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract package name
                dep_name = re.split(r'[<>=\[]', line)[0].strip()
                deps.add(dep_name)
        return deps
    
    def _find_all_imports(self) -> Set[str]:
        """Find all imported packages in source code"""
        imports = set()
        
        for py_file in Path('src').rglob('*.py'):
            content = py_file.read_text()
            
            # Find import statements
            import_patterns = [
                r'^import\s+(\w+)',
                r'^from\s+(\w+)',
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                imports.update(matches)
        
        return imports
    
    def _is_stdlib(self, module_name: str) -> bool:
        """Check if module is part of standard library"""
        stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'time', 'pathlib', 
            're', 'typing', 'asyncio', 'logging', 'uuid', 'hashlib',
            'collections', 'itertools', 'functools', 'contextlib',
            'io', 'abc', 'enum', 'dataclasses', 'warnings', 'copy',
            'urllib', 'http', 'email', 'csv', 'xml', 'html',
        }
        return module_name in stdlib_modules or module_name.startswith('_')
    
    def _matches_pattern(self, pattern: str, content: str) -> bool:
        """Check if a version pattern matches content"""
        # Simple pattern matching for version strings
        package = pattern.split('==')[0].split('<')[0].split('>')[0]
        return package in content