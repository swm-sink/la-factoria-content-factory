"""
Independent conftest.py for CI tests
Minimal configuration without main application dependencies
"""

import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent.parent.parent

@pytest.fixture(scope="session") 
def workflows_dir(project_root):
    """Get workflows directory"""
    return project_root / '.github' / 'workflows'