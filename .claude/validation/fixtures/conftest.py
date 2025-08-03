"""
Pytest Configuration and Shared Fixtures for La Factoria Validation System
Based on 2024-2025 testing best practices and Claude Code integration patterns
"""

import pytest
import yaml
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"

@pytest.fixture(scope="session")
def validation_config():
    """Load validation configuration for tests"""
    config_path = Path(".claude/validation/config/validation.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Default test configuration
        return {
            'validation': {
                'global': {
                    'zero_tolerance_failures': True,
                    'minimum_coverage_threshold': 0.95
                }
            }
        }

@pytest.fixture(scope="session")
def test_directory_structure():
    """Create temporary directory structure for testing"""
    temp_dir = tempfile.mkdtemp(prefix="claude_validation_test_")
    
    # Create test .claude structure
    claude_dir = Path(temp_dir) / ".claude"
    claude_dir.mkdir()
    
    # Create subdirectories
    subdirs = [
        "agents", "commands", "context", "domains", "examples", 
        "memory", "indexes", "validation/scripts", "validation/config",
        "artifacts/reports/validation", "hooks"
    ]
    
    for subdir in subdirs:
        (claude_dir / subdir).mkdir(parents=True)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_agent_file():
    """Create a sample agent file for testing"""
    return """---
name: test-agent
description: "Test agent for validation testing"
tools: Read, Write, Edit
---

# Test Agent

This is a test agent for validation purposes.

## Instructions

1. Test instruction one
2. Test instruction two
3. Test instruction three
"""

@pytest.fixture
def sample_command_file():
    """Create a sample command file for testing"""
    return """---
name: /test-command
description: "Test command for validation testing"
usage: "/test-command [arguments]"
tools: Read, Write
---

# Test Command

Test command for validation purposes.

## Instructions

1. Execute test procedure
2. Validate results
3. Report findings

## Usage

```bash
/test-command arg1 arg2
```

## Examples

```bash
/test-command example-arg
```
"""

@pytest.fixture
def sample_context_file():
    """Create a sample context file for testing"""
    return """# Test Context File

This is a test context file for La Factoria educational content generation.

## Educational Framework

- Content type: Study Guide
- Target audience: High School
- Learning objectives: Understanding, Application, Analysis

## Implementation Details

Educational content should follow pedagogical best practices and maintain
factual accuracy while being age-appropriate for the target audience.

## Related Files

- [Master Outline](master-outline.md)
- [Study Guide Template](study-guide-template.md)
"""

@pytest.fixture
def mock_validation_results():
    """Mock validation results for testing"""
    return {
        'agents': {
            'status': 'PASS',
            'steps_completed': 5,
            'steps_passed': 5,
            'steps_failed': 0,
            'success_rate': 1.0
        },
        'context': {
            'status': 'PASS', 
            'steps_completed': 6,
            'steps_passed': 6,
            'steps_failed': 0,
            'success_rate': 1.0
        },
        'commands': {
            'status': 'PASS',
            'steps_completed': 5, 
            'steps_passed': 5,
            'steps_failed': 0,
            'success_rate': 1.0
        }
    }

@pytest.fixture
def reports_directory():
    """Create temporary reports directory"""
    temp_dir = tempfile.mkdtemp(prefix="validation_reports_")
    
    # Create date-based subdirectory
    date_dir = Path(temp_dir) / datetime.now().strftime("%Y-%m-%d")
    date_dir.mkdir(parents=True)
    
    yield date_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def validation_standards():
    """2024-2025 validation standards for testing"""
    return {
        'max_directory_depth': 4,
        'min_file_size': 1024,
        'max_file_size': 51200,
        'min_cross_reference_coverage': 0.80,
        'required_directories': ['commands', 'examples', 'context', 'memory'],
        'navigation_hop_limit': 3,
        'content_quality_threshold': 0.90,
        'project_alignment_threshold': 0.95
    }

@pytest.fixture
def la_factoria_keywords():
    """La Factoria specific keywords for testing"""
    return [
        'educational', 'content generation', 'study guide', 'flashcards',
        'podcast script', 'master outline', 'Railway', 'FastAPI', 'Claude API'
    ]

@pytest.fixture
def educational_content_types():
    """Educational content types for La Factoria testing"""
    return [
        'master_content_outline', 'podcast_script', 'study_guide',
        'one_pager_summary', 'detailed_reading_material', 'faq_collection',
        'flashcards', 'reading_guide_questions'
    ]

class ValidationTestHelper:
    """Helper class for validation testing"""
    
    @staticmethod
    def create_test_file(directory: Path, filename: str, content: str) -> Path:
        """Create a test file with given content"""
        file_path = directory / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    @staticmethod
    def count_validation_steps(results: Dict[str, Any]) -> int:
        """Count total validation steps from results"""
        return sum(
            result.get('steps_completed', 0) 
            for result in results.values() 
            if isinstance(result, dict)
        )
    
    @staticmethod
    def calculate_overall_success_rate(results: Dict[str, Any]) -> float:
        """Calculate overall success rate from validation results"""
        total_steps = 0
        passed_steps = 0
        
        for result in results.values():
            if isinstance(result, dict):
                total_steps += result.get('steps_completed', 0)
                passed_steps += result.get('steps_passed', 0)
        
        return passed_steps / max(total_steps, 1)

@pytest.fixture
def validation_helper():
    """Validation test helper instance"""
    return ValidationTestHelper()

# Pytest configuration
def pytest_configure(config):
    """Configure pytest for validation testing"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests" 
    )
    config.addinivalue_line(
        "markers", "validation: marks tests as validation tests"
    )
    config.addinivalue_line(
        "markers", "hooks: marks tests as Claude Code hooks tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on test file location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "validation" in str(item.fspath):
            item.add_marker(pytest.mark.validation)
        elif "hooks" in str(item.fspath):
            item.add_marker(pytest.mark.hooks)

# Test data creation functions
def create_test_data_files():
    """Create test data files if they don't exist"""
    if not TEST_DATA_DIR.exists():
        TEST_DATA_DIR.mkdir(parents=True)
        
        # Create sample test files
        sample_files = {
            "valid_agent.md": """---
name: sample-agent
description: "Sample agent for testing"
tools: Read, Write
---

# Sample Agent

## Instructions
1. Read input
2. Process data
3. Write output
""",
            "valid_command.md": """# Sample Command

Sample command for testing.

## Instructions
1. Execute command
2. Return results

## Usage
/sample-command [args]
""",
            "valid_context.md": """# Sample Context

Educational context for testing La Factoria system.

## Educational Framework
- Content type: Test content
- Target: Testing purposes
"""
        }
        
        for filename, content in sample_files.items():
            with open(TEST_DATA_DIR / filename, 'w') as f:
                f.write(content)

# Auto-create test data on import
create_test_data_files()