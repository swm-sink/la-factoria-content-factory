"""
Test Project Setup - TDD First!
Task: SETUP-001
"""
import os
import pytest


def test_project_structure_exists():
    """Test that all required directories exist."""
    required_dirs = ['src', 'static', 'tests', 'scripts', 'docs']
    
    for dir_name in required_dirs:
        dir_path = os.path.join(os.path.dirname(__file__), '..', dir_name)
        assert os.path.exists(dir_path), f"Directory {dir_name} should exist"
        assert os.path.isdir(dir_path), f"{dir_name} should be a directory"


def test_project_is_not_overcomplicated():
    """Test that we're not adding unnecessary complexity."""
    # Count total files in project (excluding __pycache__ and .git)
    total_files = 0
    project_root = os.path.join(os.path.dirname(__file__), '..')
    
    for root, dirs, files in os.walk(project_root):
        # Skip cache and git directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.pytest_cache']]
        total_files += len(files)
    
    # Should have less than 20 files total
    assert total_files < 20, f"Project has {total_files} files - too complex!"


def test_no_unnecessary_dependencies():
    """Test that we haven't added complex dependencies."""
    requirements_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            dependencies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        assert len(dependencies) < 15, f"Too many dependencies: {len(dependencies)}"