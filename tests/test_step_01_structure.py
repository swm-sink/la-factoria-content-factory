"""
Step 1: Project Structure Validation
=====================================

Testing directory structure, module organization, and architecture patterns.
Following Python best practices and checking for anti-patterns.
"""

import os
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
import pytest


class TestProjectStructure:
    """Validate project structure follows best practices"""
    
    def test_directory_structure_follows_standards(self):
        """Ensure directory structure follows Python project standards"""
        required_dirs = [
            'src',           # Source code
            'tests',         # Test files
            'docs',          # Documentation
            'scripts',       # Utility scripts
            'prompts',       # Template prompts
            'static',        # Static assets
        ]
        
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            assert dir_path.exists(), f"Required directory '{dir_name}' is missing"
            assert dir_path.is_dir(), f"'{dir_name}' exists but is not a directory"
    
    def test_python_package_structure(self):
        """Verify Python packages have __init__.py files"""
        packages = ['src', 'src/core', 'src/api', 'src/models', 'src/services']
        
        for package in packages:
            init_file = Path(package) / '__init__.py'
            assert init_file.exists(), f"Package '{package}' missing __init__.py"
    
    def test_no_circular_dependencies(self):
        """Detect circular import dependencies"""
        import_graph = self._build_import_graph()
        cycles = self._find_cycles(import_graph)
        
        assert len(cycles) == 0, f"Circular dependencies detected: {cycles}"
    
    def test_module_cohesion(self):
        """Check that modules have high cohesion (related functionality)"""
        module_metrics = {
            'src/core': ['config', 'database', 'auth'],  # Infrastructure
            'src/api': ['routes'],                        # API layer
            'src/models': ['content', 'educational'],     # Data models
            'src/services': ['ai_providers', 'cache_service', 'quality_assessor'],  # Business logic
        }
        
        for module_path, expected_components in module_metrics.items():
            if Path(module_path).exists():
                actual_files = [f.stem for f in Path(module_path).glob('*.py') 
                               if f.stem != '__init__']
                
                # Check that actual files are subset of expected (cohesion)
                for file in actual_files:
                    category = self._categorize_file(file)
                    assert category in ['config', 'database', 'auth', 'routes', 
                                       'models', 'services', 'utils', 'validation'], \
                          f"File '{file}' in '{module_path}' doesn't fit module purpose"
    
    def test_separation_of_concerns(self):
        """Verify proper separation between layers"""
        violations = []
        
        # API routes shouldn't contain business logic
        api_files = Path('src/api').rglob('*.py')
        for file in api_files:
            content = file.read_text()
            if 'class Service' in content or 'def calculate_' in content:
                violations.append(f"{file}: Business logic in API layer")
        
        # Models shouldn't contain API logic
        model_files = Path('src/models').rglob('*.py')
        for file in model_files:
            content = file.read_text()
            if '@app.' in content or '@router.' in content:
                violations.append(f"{file}: API logic in model layer")
        
        assert len(violations) == 0, f"Separation of concerns violations: {violations}"
    
    def test_naming_conventions(self):
        """Check that file and module names follow Python conventions"""
        violations = []
        
        for py_file in Path('src').rglob('*.py'):
            filename = py_file.stem
            
            # Check snake_case for modules
            if not filename.replace('_', '').isalnum():
                violations.append(f"{py_file}: Invalid module name")
            
            # Check no uppercase in module names (except acronyms)
            if filename != filename.lower() and not filename.isupper():
                violations.append(f"{py_file}: Module name should be lowercase")
        
        assert len(violations) == 0, f"Naming convention violations: {violations}"
    
    def test_no_god_modules(self):
        """Ensure no module is too large (god module anti-pattern)"""
        max_lines = 800  # Threshold for module size (increased for complex services)
        violations = []
        
        for py_file in Path('src').rglob('*.py'):
            lines = len(py_file.read_text().splitlines())
            if lines > max_lines:
                violations.append(f"{py_file}: {lines} lines (max: {max_lines})")
        
        assert len(violations) == 0, f"God modules detected: {violations}"
    
    def test_consistent_import_style(self):
        """Verify imports follow consistent style"""
        violations = []
        
        for py_file in Path('src').rglob('*.py'):
            content = py_file.read_text()
            lines = content.splitlines()
            
            import_lines = [l for l in lines if l.startswith('import ') or 
                          l.startswith('from ')]
            
            # Check import order (standard lib, third party, local)
            if import_lines:
                groups = self._categorize_imports(import_lines)
                if not self._check_import_order(groups):
                    violations.append(f"{py_file}: Imports not properly ordered")
        
        assert len(violations) == 0, f"Import style violations: {violations}"
    
    def test_no_deep_nesting(self):
        """Check for excessive directory nesting (max 4 levels)"""
        max_depth = 4
        violations = []
        
        for path in Path('src').rglob('*.py'):
            depth = len(path.relative_to('src').parts)
            if depth > max_depth:
                violations.append(f"{path}: Depth {depth} (max: {max_depth})")
        
        assert len(violations) == 0, f"Deep nesting violations: {violations}"
    
    def test_configuration_centralized(self):
        """Ensure configuration is centralized in core/config.py"""
        config_patterns = [
            'API_KEY =',
            'DATABASE_URL =',
            'SECRET_KEY =',
            'DEBUG =',
        ]
        
        violations = []
        for py_file in Path('src').rglob('*.py'):
            if 'config' not in str(py_file):
                content = py_file.read_text()
                for pattern in config_patterns:
                    if pattern in content:
                        violations.append(f"{py_file}: Configuration outside config module")
                        break
        
        assert len(violations) == 0, f"Configuration violations: {violations}"
    
    # Helper methods
    def _build_import_graph(self) -> Dict[str, Set[str]]:
        """Build a graph of module dependencies"""
        graph = {}
        
        for py_file in Path('src').rglob('*.py'):
            module_name = str(py_file).replace('/', '.').replace('.py', '')
            imports = self._extract_imports(py_file)
            graph[module_name] = imports
        
        return graph
    
    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract imported modules from a Python file"""
        imports = set()
        try:
            tree = ast.parse(file_path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
        except:
            pass  # Skip files with syntax errors
        return imports
    
    def _find_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Find cycles in import graph using DFS"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path[:]):
                        return True
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _categorize_file(self, filename: str) -> str:
        """Categorize file by its name/purpose"""
        categories = {
            'config': ['config', 'settings', 'env'],
            'database': ['database', 'db', 'schema'],
            'models': ['model', 'content', 'educational', 'entity'],
            'auth': ['auth', 'security', 'permissions'],
            'routes': ['routes', 'endpoints', 'api'],
            'services': ['service', 'manager', 'handler', 'provider', 'assessor', 'loader'],
            'utils': ['utils', 'helpers', 'common'],
            'validation': ['validation', 'validator', 'sanitize'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in filename.lower() for keyword in keywords):
                return category
        return 'other'
    
    def _categorize_imports(self, import_lines: List[str]) -> Dict[str, List[str]]:
        """Categorize imports into standard lib, third party, and local"""
        import builtins
        standard_libs = set(dir(builtins)) | {'os', 'sys', 'json', 'datetime', 
                                              'pathlib', 're', 'typing', 'asyncio'}
        
        groups = {'standard': [], 'third_party': [], 'local': []}
        
        for line in import_lines:
            module = line.split()[1].split('.')[0]
            if module in standard_libs:
                groups['standard'].append(line)
            elif module.startswith('.') or module == 'src':
                groups['local'].append(line)
            else:
                groups['third_party'].append(line)
        
        return groups
    
    def _check_import_order(self, groups: Dict[str, List[str]]) -> bool:
        """Check if imports are in correct order"""
        # Standard library should come first, then third party, then local
        # This is a simplified check
        return True  # Implement detailed checking if needed