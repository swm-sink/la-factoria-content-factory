"""
Independent conftest.py for coverage tests
Minimal configuration without main application dependencies
"""

import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent.parent.parent

@pytest.fixture(scope="session") 
def coverage_config_files(project_root):
    """Get coverage configuration files"""
    return {
        'pytest_ini': project_root / 'pytest.ini',
        'coveragerc': project_root / '.coveragerc',
        'pyproject_toml': project_root / 'pyproject.toml'
    }