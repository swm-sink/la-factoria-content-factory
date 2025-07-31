"""
Test GitHub Actions workflow configurations
Validates workflow syntax, job dependencies, and CI pipeline structure
"""

import pytest
import yaml
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Ensure this test module can run independently without main app dependencies
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class TestGitHubWorkflows:
    """Test GitHub Actions workflow configurations"""
    
    @pytest.fixture
    def workflows_dir(self) -> Path:
        """Get workflows directory path"""
        return Path(__file__).parent.parent.parent.parent / '.github' / 'workflows'
    
    @pytest.fixture
    def ci_workflow_file(self, workflows_dir: Path) -> Path:
        """Get CI workflow file path"""
        return workflows_dir / 'ci.yml'
        
    def test_workflows_directory_exists(self, workflows_dir: Path):
        """Test that .github/workflows directory exists"""
        assert workflows_dir.exists(), "GitHub workflows directory should exist"
        assert workflows_dir.is_dir(), "Workflows path should be a directory"
        
    def test_ci_workflow_exists(self, ci_workflow_file: Path):
        """Test that CI workflow file exists"""
        assert ci_workflow_file.exists(), "CI workflow file should exist"
        
    def test_ci_workflow_valid_yaml(self, ci_workflow_file: Path):
        """Test that CI workflow is valid YAML"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        try:
            with open(ci_workflow_file, 'r') as f:
                workflow = yaml.safe_load(f)
            assert isinstance(workflow, dict), "Workflow should be a valid YAML dict"
        except yaml.YAMLError as e:
            pytest.fail(f"CI workflow is not valid YAML: {e}")
            
    def test_ci_workflow_structure(self, ci_workflow_file: Path):
        """Test CI workflow has required structure"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        with open(ci_workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
            
        # Test required top-level keys
        required_keys = ['name', 'on', 'jobs']
        for key in required_keys:
            assert key in workflow, f"Workflow should have '{key}' key"
            
        # Test trigger events
        assert 'push' in workflow['on'], "Workflow should trigger on push"
        assert 'pull_request' in workflow['on'], "Workflow should trigger on PR"
        
        # Test jobs exist
        assert len(workflow['jobs']) > 0, "Workflow should have at least one job"
        
    def test_ci_workflow_jobs(self, ci_workflow_file: Path):
        """Test CI workflow jobs configuration"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        with open(ci_workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
            
        jobs = workflow.get('jobs', {})
        
        # Test required jobs exist
        expected_jobs = ['test', 'lint', 'security']
        for job_name in expected_jobs:
            assert job_name in jobs, f"Workflow should have '{job_name}' job"
            
        # Test job structure
        for job_name, job_config in jobs.items():
            assert 'runs-on' in job_config, f"Job '{job_name}' should specify runs-on"
            assert 'steps' in job_config, f"Job '{job_name}' should have steps"
            assert len(job_config['steps']) > 0, f"Job '{job_name}' should have at least one step"
            
    def test_python_setup_step(self, ci_workflow_file: Path):
        """Test Python setup step configuration"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        with open(ci_workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
            
        # Find Python setup in any job
        python_setup_found = False
        python_versions = []
        
        for job_name, job_config in workflow.get('jobs', {}).items():
            for step in job_config.get('steps', []):
                if step.get('uses', '').startswith('actions/setup-python'):
                    python_setup_found = True
                    with_config = step.get('with', {})
                    if 'python-version' in with_config:
                        version = with_config['python-version']
                        if isinstance(version, list):
                            python_versions.extend(version)
                        else:
                            python_versions.append(version)
                            
        assert python_setup_found, "Workflow should include Python setup step"
        assert len(python_versions) > 0, "Python setup should specify versions"
        
        # Test Python version format
        for version in python_versions:
            version_str = str(version)
            assert '3.' in version_str, f"Python version should be 3.x, got {version_str}"
            
    def test_node_setup_step(self, ci_workflow_file: Path):
        """Test Node.js setup step configuration"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        with open(ci_workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
            
        # Find Node setup in any job
        node_setup_found = False
        
        for job_name, job_config in workflow.get('jobs', {}).items():
            for step in job_config.get('steps', []):
                if step.get('uses', '').startswith('actions/setup-node'):
                    node_setup_found = True
                    with_config = step.get('with', {})
                    assert 'node-version' in with_config, "Node setup should specify version"
                    
        assert node_setup_found, "Workflow should include Node.js setup step"
        
    def test_dependency_caching(self, ci_workflow_file: Path):
        """Test dependency caching configuration"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        with open(ci_workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
            
        # Find caching steps
        cache_steps = []
        
        for job_name, job_config in workflow.get('jobs', {}).items():
            for step in job_config.get('steps', []):
                if step.get('uses', '').startswith('actions/cache'):
                    cache_steps.append(step)
                    
        assert len(cache_steps) > 0, "Workflow should include dependency caching"
        
        # Test cache configuration
        for cache_step in cache_steps:
            with_config = cache_step.get('with', {})
            assert 'path' in with_config, "Cache step should specify path"
            assert 'key' in with_config, "Cache step should specify key"
            
    def test_test_execution_steps(self, ci_workflow_file: Path):
        """Test test execution steps"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        with open(ci_workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
            
        # Find test execution steps
        test_commands = []
        
        for job_name, job_config in workflow.get('jobs', {}).items():
            for step in job_config.get('steps', []):
                run_command = step.get('run', '')
                if 'pytest' in run_command.lower():
                    test_commands.append(run_command)
                    
        assert len(test_commands) > 0, "Workflow should include pytest commands"
        
        # Test coverage reporting
        coverage_found = False
        for command in test_commands:
            if '--cov' in command:
                coverage_found = True
                break
                
        assert coverage_found, "Test commands should include coverage reporting"
        
    def test_linting_steps(self, ci_workflow_file: Path):
        """Test linting and code quality steps"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        with open(ci_workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
            
        # Find linting commands
        linting_tools = ['ruff', 'black', 'isort']
        found_tools = []
        
        for job_name, job_config in workflow.get('jobs', {}).items():
            for step in job_config.get('steps', []):
                run_command = step.get('run', '').lower()
                for tool in linting_tools:
                    if tool in run_command:
                        found_tools.append(tool)
                        
        assert len(found_tools) > 0, "Workflow should include linting tools"
        
    def test_security_scanning_steps(self, ci_workflow_file: Path):
        """Test security scanning steps"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        with open(ci_workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
            
        # Find security scanning commands
        security_tools = ['bandit', 'safety', 'semgrep']
        found_tools = []
        
        for job_name, job_config in workflow.get('jobs', {}).items():
            for step in job_config.get('steps', []):
                run_command = step.get('run', '').lower()
                for tool in security_tools:
                    if tool in run_command:
                        found_tools.append(tool)
                        
        assert len(found_tools) > 0, "Workflow should include security tools"
        
    def test_job_dependencies(self, ci_workflow_file: Path):
        """Test job dependency configuration"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        with open(ci_workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
            
        jobs = workflow.get('jobs', {})
        
        # Check for proper job ordering
        if 'deploy' in jobs:
            deploy_job = jobs['deploy']
            assert 'needs' in deploy_job, "Deploy job should depend on other jobs"
            
            needs = deploy_job['needs']
            if isinstance(needs, str):
                needs = [needs]
                
            required_deps = ['test', 'lint', 'security']
            for dep in required_deps:
                if dep in jobs:
                    assert dep in needs, f"Deploy should depend on {dep} job"
                    
    def test_environment_variables(self, ci_workflow_file: Path):
        """Test environment variable configuration"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        with open(ci_workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
            
        # Check for environment variables in jobs
        env_found = False
        
        for job_name, job_config in workflow.get('jobs', {}).items():
            if 'env' in job_config:
                env_found = True
                env_vars = job_config['env']
                
                # Test for common required env vars
                if 'ENVIRONMENT' in env_vars:
                    assert env_vars['ENVIRONMENT'] in ['test', 'ci'], \
                        "Environment should be set to test or ci"
                        
        # Environment variables can also be in steps
        for job_name, job_config in workflow.get('jobs', {}).items():
            for step in job_config.get('steps', []):
                if 'env' in step:
                    env_found = True
                    
        # Note: env vars are optional, so we don't assert they must exist
        
    def test_artifact_handling(self, ci_workflow_file: Path):
        """Test artifact upload/download configuration"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        with open(ci_workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
            
        # Find artifact steps
        upload_steps = []
        download_steps = []
        
        for job_name, job_config in workflow.get('jobs', {}).items():
            for step in job_config.get('steps', []):
                uses = step.get('uses', '')
                if 'actions/upload-artifact' in uses:
                    upload_steps.append(step)
                elif 'actions/download-artifact' in uses:
                    download_steps.append(step)
                    
        # Test artifact configuration if present
        for step in upload_steps:
            with_config = step.get('with', {})
            assert 'name' in with_config, "Artifact upload should specify name"
            assert 'path' in with_config, "Artifact upload should specify path"
            
    def test_conditional_execution(self, ci_workflow_file: Path):
        """Test conditional job/step execution"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        with open(ci_workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
            
        # Check for conditional execution patterns
        conditional_patterns = ['if:', 'github.event_name', 'github.ref']
        conditionals_found = False
        
        def check_conditionals(obj):
            nonlocal conditionals_found
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == 'if' or any(pattern in str(value) for pattern in conditional_patterns):
                        conditionals_found = True
                    check_conditionals(value)
            elif isinstance(obj, list):
                for item in obj:
                    check_conditionals(item)
                    
        check_conditionals(workflow)
        
        # Conditionals are recommended but not required
        if conditionals_found:
            # If conditionals exist, they should be valid
            for job_name, job_config in workflow.get('jobs', {}).items():
                if 'if' in job_config:
                    if_condition = job_config['if']
                    assert isinstance(if_condition, str), f"Job {job_name} 'if' should be string"
                    
    def test_workflow_permissions(self, ci_workflow_file: Path):
        """Test workflow permissions configuration"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        with open(ci_workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
            
        # Check for permissions (security best practice)
        if 'permissions' in workflow:
            permissions = workflow['permissions']
            assert isinstance(permissions, dict), "Permissions should be a dict"
            
            # Test for principle of least privilege
            for perm_type, perm_value in permissions.items():
                assert perm_value in ['read', 'write', 'none'], \
                    f"Permission {perm_type} should be read/write/none, got {perm_value}"
                    
    def test_timeout_configuration(self, ci_workflow_file: Path):
        """Test job timeout configuration"""
        if not ci_workflow_file.exists():
            pytest.skip("CI workflow file does not exist yet")
            
        with open(ci_workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
            
        # Check for timeout configuration
        for job_name, job_config in workflow.get('jobs', {}).items():
            if 'timeout-minutes' in job_config:
                timeout = job_config['timeout-minutes']
                assert isinstance(timeout, int), f"Job {job_name} timeout should be integer"
                assert 1 <= timeout <= 360, f"Job {job_name} timeout should be 1-360 minutes"


class TestWorkflowIntegration:
    """Test workflow integration with project structure"""
    
    def test_workflow_matches_project_structure(self):
        """Test workflow configuration matches project structure"""
        project_root = Path(__file__).parent.parent.parent.parent
        
        # Check for Python backend
        if (project_root / 'app').exists():
            # Should have Python testing in workflow
            workflows_dir = project_root / '.github' / 'workflows'
            if (workflows_dir / 'ci.yml').exists():
                with open(workflows_dir / 'ci.yml', 'r') as f:
                    content = f.read()
                    assert 'python' in content.lower(), "Workflow should include Python setup"
                    
        # Check for Node.js frontend
        if (project_root / 'frontend' / 'package.json').exists():
            # Should have Node.js testing in workflow
            workflows_dir = project_root / '.github' / 'workflows'
            if (workflows_dir / 'ci.yml').exists():
                with open(workflows_dir / 'ci.yml', 'r') as f:
                    content = f.read()
                    assert 'node' in content.lower(), "Workflow should include Node.js setup"
                    
    def test_workflow_validates_requirements(self):
        """Test workflow validates all project requirements"""
        project_root = Path(__file__).parent.parent.parent.parent
        
        # Check for requirements.txt validation
        if (project_root / 'requirements.txt').exists():
            workflows_dir = project_root / '.github' / 'workflows'
            if (workflows_dir / 'ci.yml').exists():
                with open(workflows_dir / 'ci.yml', 'r') as f:
                    content = f.read()
                    # Should install requirements
                    assert any(cmd in content for cmd in ['pip install', 'requirements.txt']), \
                        "Workflow should install Python requirements"
                        
        # Check for package.json validation
        if (project_root / 'frontend' / 'package.json').exists():
            workflows_dir = project_root / '.github' / 'workflows'
            if (workflows_dir / 'ci.yml').exists():
                with open(workflows_dir / 'ci.yml', 'r') as f:
                    content = f.read()
                    # Should install npm dependencies
                    assert any(cmd in content for cmd in ['npm install', 'npm ci']), \
                        "Workflow should install Node.js dependencies"