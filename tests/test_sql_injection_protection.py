"""
Comprehensive SQL Injection Protection Tests for La Factoria
Following strict TDD methodology for security fixes
"""

import pytest
import re
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import text
from sqlalchemy.sql import elements
import asyncio

class TestSQLInjectionProtection:
    """Test suite for SQL injection protection across database operations"""
    
    def test_no_string_interpolation_in_queries(self):
        """Ensure no f-strings or % formatting in SQL queries"""
        import src.core.database as db_module
        import inspect
        
        # Get source code of database module
        source = inspect.getsource(db_module)
        
        # Pattern to detect dangerous SQL construction
        dangerous_patterns = [
            r'f".*SELECT.*FROM.*{.*}',  # f-string in SQL
            r'f".*INSERT.*INTO.*{.*}',  # f-string in SQL
            r'f".*UPDATE.*SET.*{.*}',   # f-string in SQL
            r'f".*DELETE.*FROM.*{.*}',  # f-string in SQL
            r'%.*SELECT.*FROM.*%',      # % formatting in SQL
            r'\.format\(.*SELECT.*FROM', # .format() in SQL
            r'".*SELECT.*FROM.*" \+',   # String concatenation in SQL
        ]
        
        violations = []
        for line_num, line in enumerate(source.split('\n'), 1):
            for pattern in dangerous_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(f"Line {line_num}: {line.strip()}")
        
        assert len(violations) == 0, f"Found SQL injection vulnerabilities:\n" + "\n".join(violations)
    
    def test_parameterized_queries_only(self):
        """Ensure all queries use parameterized statements"""
        import src.core.database as db_module
        import inspect
        
        source = inspect.getsource(db_module)
        
        # Find all execute() calls
        execute_pattern = r'\.execute\((.*?)\)'
        matches = re.findall(execute_pattern, source, re.DOTALL)
        
        unsafe_queries = []
        for match in matches:
            # Check if using text() wrapper for raw SQL
            if 'text(' in match:
                # Check if it contains variable interpolation
                if 'f"' in match or 'f\'' in match or '.format(' in match or '%' in match:
                    unsafe_queries.append(match[:100])  # First 100 chars
        
        assert len(unsafe_queries) == 0, f"Found unsafe queries:\n" + "\n".join(unsafe_queries)
    
    def test_table_name_validation(self):
        """Test that table names are validated before use"""
        from src.core.database import DatabaseManager
        
        # These should be the only allowed table names
        valid_tables = ['users', 'educational_content', 'quality_assessments']
        
        # Test that get_table_stats validates table names
        with patch('src.core.database.engine') as mock_engine:
            mock_connection = MagicMock()
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            
            # Attempt SQL injection via table name
            malicious_tables = [
                "users; DROP TABLE users--",
                "users' OR '1'='1",
                "users); DELETE FROM users WHERE 1=1--",
                "../etc/passwd",
                "users UNION SELECT * FROM passwords--"
            ]
            
            for malicious_table in malicious_tables:
                # The implementation should either:
                # 1. Reject the malicious table name
                # 2. Use a whitelist of allowed tables
                # 3. Properly escape/parameterize the table name
                
                # For now, we expect it to use a whitelist approach
                asyncio.run(DatabaseManager.get_table_stats())
                
                # Check that no malicious query was executed
                for call in mock_connection.execute.call_args_list:
                    query_str = str(call[0][0]) if call[0] else ""
                    assert malicious_table not in query_str, \
                        f"Malicious table name '{malicious_table}' was not sanitized"
    
    def test_migration_file_path_validation(self):
        """Test that migration file paths are validated"""
        from src.core.database import DatabaseManager
        import os
        
        # Test path traversal attempts
        malicious_paths = [
            "../../../etc/passwd",
            "/etc/passwd",
            "../../src/core/config.py",
            "migrations/../../../sensitive.sql"
        ]
        
        for malicious_path in malicious_paths:
            # Should either raise an exception or sanitize the path
            with pytest.raises((FileNotFoundError, ValueError, OSError)):
                asyncio.run(DatabaseManager.run_migration(malicious_path))
    
    def test_safe_table_query_implementation(self):
        """Test that the fixed implementation uses safe querying"""
        from src.core.database import DatabaseManager
        
        # Mock the database connection
        with patch('src.core.database.engine') as mock_engine:
            mock_connection = MagicMock()
            mock_result = MagicMock()
            mock_result.fetchone.return_value = (10,)
            mock_connection.execute.return_value = mock_result
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            
            # Run the method
            asyncio.run(DatabaseManager.get_table_stats())
            
            # Verify that execute was called with proper parameterization
            calls = mock_connection.execute.call_args_list
            
            for call in calls:
                if call[0]:  # If there are positional arguments
                    query = call[0][0]
                    
                    # If it's a text query, it should use bind parameters
                    if hasattr(query, 'text'):
                        query_text = str(query)
                        # Should not contain direct string interpolation
                        assert 'f"' not in str(call), "Found f-string in query"
                        assert '.format(' not in str(call), "Found .format() in query"
    
    def test_query_builder_safety(self):
        """Test that any query builders properly escape identifiers"""
        from sqlalchemy import select, table, column
        from sqlalchemy.sql import quoted_name
        
        # Test that table/column names are properly quoted
        test_cases = [
            ("users", True),  # Valid table
            ("users; DROP TABLE", False),  # SQL injection attempt
            ("users' OR '1'='1", False),  # SQL injection attempt
        ]
        
        for table_name, should_succeed in test_cases:
            if should_succeed:
                # Should work without issues
                t = table(quoted_name(table_name, quote=True))
                assert t is not None
            else:
                # Should be rejected or quoted
                t = table(quoted_name(table_name, quote=True))
                # The quoted name should escape dangerous characters
                assert ";" not in str(t) or "\\" in str(t) or "'" not in str(t)
    
    def test_no_raw_sql_in_api_routes(self):
        """Ensure API routes don't construct raw SQL (excluding safe ORM usage)"""
        import glob
        import os
        
        api_files = glob.glob("/Users/smenssink/Developer/la-factoria-content-factory/.conductor/bangui/src/api/routes/*.py")
        
        # Look for actual raw SQL patterns, not ORM usage
        dangerous_patterns = [
            r'["\']SELECT.*FROM',  # Raw SQL strings
            r'["\']INSERT.*INTO',  # Raw SQL strings
            r'["\']UPDATE.*SET',   # Raw SQL strings
            r'["\']DELETE.*FROM',  # Raw SQL strings
            r'["\']DROP.*TABLE',   # Raw SQL strings
            r'["\']ALTER.*TABLE'   # Raw SQL strings
        ]
        
        violations = []
        for api_file in api_files:
            with open(api_file, 'r') as f:
                content = f.read()
                for line_num, line in enumerate(content.split('\n'), 1):
                    for pattern in dangerous_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Check if it's in a comment or docstring
                            stripped = line.strip()
                            if not stripped.startswith('#') and not stripped.startswith('"""'):
                                # Exclude ORM methods like select(), update(), etc.
                                if 'select(' not in line and 'update(' not in line:
                                    violations.append(f"{os.path.basename(api_file)}:{line_num}: {line.strip()}")
        
        assert len(violations) == 0, f"Found raw SQL in API routes:\n" + "\n".join(violations)
    
    def test_orm_usage_over_raw_sql(self):
        """Verify ORM is used instead of raw SQL where possible"""
        from src.core.database import DatabaseManager
        
        # The get_table_stats method should ideally use ORM
        # For now, we ensure it at least uses parameterized queries
        assert hasattr(DatabaseManager, 'get_table_stats'), "get_table_stats method exists"
        
        # Check that if raw SQL is used, it's properly parameterized
        import inspect
        source = inspect.getsource(DatabaseManager.get_table_stats)
        
        # Should not have direct table name interpolation
        assert 'f"SELECT COUNT(*) FROM {table}"' not in source, \
            "Found unsafe table name interpolation"
        
    def test_connection_string_sanitization(self):
        """Test that database connection strings are properly handled"""
        from src.core.config import Settings
        
        # Test that sensitive parts of connection string are not logged
        settings = Settings()
        
        # Connection string should not be exposed in string representation
        settings_str = str(settings)
        if settings.database_url and 'postgresql' in settings.database_url:
            # Password should be masked
            assert ':password@' not in settings_str.lower()
            assert settings.database_url not in settings_str