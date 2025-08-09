#!/usr/bin/env python3
"""
Fix import issues in test files by adding the src directory to Python path
"""

import os
import re

def fix_imports_in_file(file_path):
    """Fix imports in a single test file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file already has our fix
        if 'sys.path.insert(0, os.path.join(os.path.dirname(__file__), \'..\'))' in content:
            print(f"✓ {file_path} - Already fixed")
            return False
            
        # Check if file has src imports
        if not re.search(r'from src\.', content):
            print(f"- {file_path} - No src imports")
            return False
            
        # Find the first import statement
        lines = content.split('\n')
        import_line_index = -1
        
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_line_index = i
                break
        
        if import_line_index == -1:
            print(f"✗ {file_path} - No import statements found")
            return False
            
        # Insert our path fix before the first import
        fix_lines = [
            "# Fix Python path for src imports",
            "import sys",
            "import os",
            "sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))",
            ""
        ]
        
        # Insert the fix
        new_lines = lines[:import_line_index] + fix_lines + lines[import_line_index:]
        new_content = '\n'.join(new_lines)
        
        # Write the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"✓ {file_path} - Fixed")
        return True
        
    except Exception as e:
        print(f"✗ {file_path} - Error: {e}")
        return False

def main():
    """Fix imports in all test files"""
    test_files = [
        'tests/test_api_endpoints.py',
        'tests/test_quality_validation.py',
        'tests/test_rate_limiting.py',
        'tests/test_health_endpoint_alignment.py',
        'tests/test_e2e_content_generation.py',
        'tests/test_services.py',
        'tests/test_quality_integration.py',
        'tests/test_quality_assessment.py',
        'tests/test_performance.py',
        'tests/test_database_integration.py',
        'tests/test_auth_security.py',
        'tests/conftest.py'
    ]
    
    fixed_count = 0
    
    print("🔧 Fixing import issues in test files...")
    print()
    
    for test_file in test_files:
        if os.path.exists(test_file):
            if fix_imports_in_file(test_file):
                fixed_count += 1
        else:
            print(f"- {test_file} - File not found")
    
    print()
    print(f"📊 Fixed {fixed_count} test files")
    print("✅ Import fix process completed!")

if __name__ == "__main__":
    main()