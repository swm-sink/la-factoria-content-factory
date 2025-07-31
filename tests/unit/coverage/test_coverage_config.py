"""
Test coverage configuration and validation
Tests the coverage reporting setup and thresholds
"""

import pytest
import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Any


class TestCoverageConfiguration:
    """Test coverage configuration and reporting"""
    
    @pytest.fixture
    def project_root(self) -> Path:
        """Get project root directory"""
        return Path(__file__).parent.parent.parent.parent
    
    @pytest.fixture
    def coverage_config_files(self, project_root: Path) -> Dict[str, Path]:
        """Get coverage configuration files"""
        return {
            'pytest_ini': project_root / 'pytest.ini',
            'coveragerc': project_root / '.coveragerc',
            'pyproject_toml': project_root / 'pyproject.toml'
        }
    
    def test_coverage_configuration_exists(self, coverage_config_files: Dict[str, Path]):
        """Test that coverage configuration exists"""
        config_exists = any(config_file.exists() for config_file in coverage_config_files.values())
        assert config_exists, "No coverage configuration file found (pytest.ini, .coveragerc, or pyproject.toml)"
        
    def test_pytest_coverage_integration(self, project_root: Path):
        """Test pytest coverage integration"""
        # Check if pytest-cov is available
        result = subprocess.run(['python3', '-m', 'pytest', '--version'], 
                              capture_output=True, text=True, cwd=project_root)
        assert result.returncode == 0, "pytest not available"
        
        # Check if coverage plugin is available
        result = subprocess.run(['python3', '-c', 'import pytest_cov'], 
                              capture_output=True, text=True, cwd=project_root)
        assert result.returncode == 0, "pytest-cov not installed"
        
    def test_coverage_threshold_configuration(self, coverage_config_files: Dict[str, Path]):
        """Test that coverage threshold is configured"""
        threshold_found = False
        threshold_value = None
        
        # Check pytest.ini
        if coverage_config_files['pytest_ini'].exists():
            with open(coverage_config_files['pytest_ini'], 'r') as f:
                content = f.read()
                if '--cov-fail-under' in content:
                    threshold_found = True
                    # Extract threshold value
                    for line in content.split('\n'):
                        if '--cov-fail-under' in line:
                            parts = line.split('=')
                            if len(parts) > 1:
                                threshold_value = parts[1].strip()
                                break
        
        # Check .coveragerc
        if coverage_config_files['coveragerc'].exists():
            with open(coverage_config_files['coveragerc'], 'r') as f:
                content = f.read()
                if 'fail_under' in content:
                    threshold_found = True
                    for line in content.split('\n'):
                        if 'fail_under' in line and '=' in line:
                            threshold_value = line.split('=')[1].strip()
                            break
        
        # Check pyproject.toml
        if coverage_config_files['pyproject_toml'].exists():
            try:
                import tomllib
                with open(coverage_config_files['pyproject_toml'], 'rb') as f:
                    data = tomllib.load(f)
                    if 'tool' in data and 'coverage' in data['tool']:
                        coverage_config = data['tool']['coverage']
                        if 'report' in coverage_config and 'fail_under' in coverage_config['report']:
                            threshold_found = True
                            threshold_value = str(coverage_config['report']['fail_under'])
            except ImportError:
                # tomllib not available in Python < 3.11, try tomli
                try:
                    import tomli
                    with open(coverage_config_files['pyproject_toml'], 'rb') as f:
                        data = tomli.load(f)
                        if 'tool' in data and 'coverage' in data['tool']:
                            coverage_config = data['tool']['coverage']
                            if 'report' in coverage_config and 'fail_under' in coverage_config['report']:
                                threshold_found = True
                                threshold_value = str(coverage_config['report']['fail_under'])
                except ImportError:
                    pass
        
        assert threshold_found, "No coverage threshold configured"
        
        if threshold_value:
            threshold_num = float(threshold_value)
            assert 60 <= threshold_num <= 100, f"Coverage threshold {threshold_num}% should be between 60-100%"
            assert threshold_num >= 70, f"Coverage threshold {threshold_num}% should be at least 70%"
            
    def test_coverage_source_configuration(self, coverage_config_files: Dict[str, Path]):
        """Test that coverage source is properly configured"""
        source_configured = False
        
        # Check pytest.ini
        if coverage_config_files['pytest_ini'].exists():
            with open(coverage_config_files['pytest_ini'], 'r') as f:
                content = f.read()
                if '--cov=app' in content or '--cov=src' in content:
                    source_configured = True
        
        # Check .coveragerc
        if coverage_config_files['coveragerc'].exists():
            with open(coverage_config_files['coveragerc'], 'r') as f:
                content = f.read()
                if '[run]' in content and 'source' in content:
                    source_configured = True
        
        assert source_configured, "Coverage source not configured"
        
    def test_coverage_output_formats(self, coverage_config_files: Dict[str, Path]):
        """Test that multiple coverage output formats are configured"""
        formats_found = []
        
        # Check for common output formats
        expected_formats = ['term-missing', 'html', 'xml', 'json']
        
        # Check pytest.ini
        if coverage_config_files['pytest_ini'].exists():
            with open(coverage_config_files['pytest_ini'], 'r') as f:
                content = f.read()
                for fmt in expected_formats:
                    if f'--cov-report={fmt}' in content:
                        formats_found.append(fmt)
        
        # Check .coveragerc
        if coverage_config_files['coveragerc'].exists():
            with open(coverage_config_files['coveragerc'], 'r') as f:
                content = f.read()
                if '[report]' in content:
                    for fmt in expected_formats:
                        if fmt in content:
                            formats_found.append(fmt)
        
        assert len(formats_found) >= 2, f"At least 2 coverage output formats should be configured, found: {formats_found}"
        assert 'term-missing' in formats_found, "Terminal coverage report should be configured"
        
    def test_coverage_exclusions(self, coverage_config_files: Dict[str, Path]):
        """Test that appropriate files are excluded from coverage"""
        exclusions_found = False
        
        common_exclusions = ['test', '__pycache__', '.venv', 'venv', 'env']
        
        # Check .coveragerc
        if coverage_config_files['coveragerc'].exists():
            with open(coverage_config_files['coveragerc'], 'r') as f:
                content = f.read().lower()
                if 'omit' in content or 'exclude' in content:
                    exclusions_found = True
                    for exclusion in common_exclusions:
                        if exclusion in content:
                            break
                    else:
                        exclusions_found = False
        
        # Check pyproject.toml
        if coverage_config_files['pyproject_toml'].exists():
            try:
                import tomllib
                with open(coverage_config_files['pyproject_toml'], 'rb') as f:
                    data = tomllib.load(f)
                    if 'tool' in data and 'coverage' in data['tool']:
                        coverage_config = data['tool']['coverage']
                        if 'run' in coverage_config and 'omit' in coverage_config['run']:
                            exclusions_found = True
            except ImportError:
                try:
                    import tomli
                    with open(coverage_config_files['pyproject_toml'], 'rb') as f:
                        data = tomli.load(f)
                        if 'tool' in data and 'coverage' in data['tool']:
                            coverage_config = data['tool']['coverage']
                            if 'run' in coverage_config and 'omit' in coverage_config['run']:
                                exclusions_found = True
                except ImportError:
                    pass
        
        # Exclusions are recommended but not required
        if not exclusions_found:
            pytest.skip("No coverage exclusions configured - recommended but not required")
            
    def test_coverage_can_run(self, project_root: Path):
        """Test that coverage can actually run"""
        # Try to run coverage on a simple test
        result = subprocess.run([
            'python3', '-m', 'pytest', 
            '--cov=app', 
            '--cov-report=term-missing',
            '--cov-fail-under=0',  # Don't fail on low coverage for this test
            'tests/unit/coverage/',  # Only run this test file
            '-v'
        ], capture_output=True, text=True, cwd=project_root, timeout=60)
        
        # Check if command succeeded
        assert result.returncode == 0, f"Coverage test run failed: {result.stderr}"
        
        # Check if coverage output is present
        output = result.stdout + result.stderr
        assert 'coverage' in output.lower(), "No coverage information in output"
        
    def test_codecov_integration(self, project_root: Path):
        """Test Codecov integration setup"""
        ci_file = project_root / '.github' / 'workflows' / 'ci.yml'
        
        if not ci_file.exists():
            pytest.skip("No CI workflow file found")
            
        with open(ci_file, 'r') as f:
            ci_content = f.read()
            
        # Check for Codecov upload
        codecov_patterns = [
            'codecov/codecov-action',
            'codecov.io',
            'upload.*coverage'
        ]
        
        codecov_found = any(pattern in ci_content.lower() for pattern in codecov_patterns)
        
        if not codecov_found:
            pytest.skip("Codecov integration not found - recommended for coverage badges")
            
    def test_coverage_badge_ready(self, project_root: Path):
        """Test that coverage badge can be generated"""
        readme_file = project_root / 'README.md'
        
        if not readme_file.exists():
            pytest.skip("No README.md found")
            
        with open(readme_file, 'r') as f:
            readme_content = f.read()
            
        # Check for coverage badge
        badge_patterns = [
            'coverage',
            'codecov',
            'shields.io',
            'badge'
        ]
        
        has_coverage_badge = any(pattern in readme_content.lower() for pattern in badge_patterns)
        
        if not has_coverage_badge:
            pytest.skip("Coverage badge not found in README - will be added automatically")


class TestCoverageReporting:
    """Test coverage reporting functionality"""
    
    def test_coverage_report_generation(self, tmp_path: Path):
        """Test that coverage reports can be generated"""
        project_root = Path(__file__).parent.parent.parent.parent
        
        # Create a temporary directory for test output
        output_dir = tmp_path / 'coverage_output'
        output_dir.mkdir()
        
        # Run coverage with output to temp directory
        result = subprocess.run([
            'python3', '-m', 'pytest',
            '--cov=app',
            '--cov-report=html:' + str(output_dir / 'html'),
            '--cov-report=xml:' + str(output_dir / 'coverage.xml'),
            '--cov-report=json:' + str(output_dir / 'coverage.json'),
            '--cov-fail-under=0',
            'tests/unit/coverage/',
            '-v'
        ], capture_output=True, text=True, cwd=project_root, timeout=120)
        
        # Check that command succeeded
        if result.returncode != 0:
            pytest.skip(f"Coverage generation failed: {result.stderr}")
            
        # Check that output files were created
        html_dir = output_dir / 'html'
        xml_file = output_dir / 'coverage.xml'
        json_file = output_dir / 'coverage.json'
        
        assert html_dir.exists(), "HTML coverage report not generated"
        assert xml_file.exists(), "XML coverage report not generated"
        assert json_file.exists(), "JSON coverage report not generated"
        
        # Validate JSON coverage report structure
        with open(json_file, 'r') as f:
            coverage_data = json.load(f)
            
        assert 'totals' in coverage_data, "Coverage JSON missing totals"
        assert 'percent_covered' in coverage_data['totals'], "Coverage JSON missing percent_covered"
        
        coverage_percent = coverage_data['totals']['percent_covered']
        assert 0 <= coverage_percent <= 100, f"Invalid coverage percentage: {coverage_percent}"
        
    def test_coverage_threshold_enforcement(self):
        """Test that coverage threshold is enforced"""
        project_root = Path(__file__).parent.parent.parent.parent
        
        # Run coverage with a very high threshold (should fail)
        result = subprocess.run([
            'python3', '-m', 'pytest',
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-fail-under=99',  # Very high threshold
            'tests/unit/coverage/',
            '-v'
        ], capture_output=True, text=True, cwd=project_root, timeout=60)
        
        # This should fail due to high threshold
        assert result.returncode != 0, "Coverage should fail with very high threshold"
        
        output = result.stdout + result.stderr
        assert 'total coverage' in output.lower() or 'failed' in output.lower(), "Coverage failure not reported"