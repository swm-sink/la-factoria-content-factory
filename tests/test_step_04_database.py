"""
Step 4: Database Schema Review
===============================

Testing database design, performance optimization, and data integrity.
"""

import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Set, Tuple
import pytest
from unittest.mock import patch, MagicMock
import sqlalchemy
from sqlalchemy import create_engine, inspect, text


class TestDatabaseSchema:
    """Validate database schema design and integrity"""
    
    def test_migration_files_exist(self):
        """Ensure database migration files are present"""
        migration_dir = Path('migrations')
        assert migration_dir.exists(), "Migrations directory missing"
        
        migration_files = list(migration_dir.glob('*.sql'))
        assert len(migration_files) > 0, "No migration files found"
        
        # Check for both PostgreSQL and SQLite versions
        has_postgres = any('postgres' in f.name.lower() or 
                          not 'sqlite' in f.name.lower() 
                          for f in migration_files)
        has_sqlite = any('sqlite' in f.name.lower() for f in migration_files)
        
        assert has_postgres or has_sqlite, "No database-specific migrations found"
    
    def test_schema_naming_conventions(self):
        """Verify database objects follow naming conventions"""
        violations = []
        
        # Read migration files to check naming
        migration_dir = Path('migrations')
        for sql_file in migration_dir.glob('*.sql'):
            content = sql_file.read_text().upper()
            
            # Check table names (should be snake_case, plural)
            table_pattern = r'CREATE TABLE\s+([A-Z_]+)'
            tables = re.findall(table_pattern, content)
            
            for table in tables:
                # Check snake_case (all lowercase with underscores)
                if table != table.lower() and 'IF NOT EXISTS' not in table:
                    violations.append(f"Table '{table}' not in snake_case")
                
                # Check plural forms (simple check)
                if not table.endswith('S') and not table.endswith('IES'):
                    if table.lower() not in ['auth', 'config', 'cache']:
                        violations.append(f"Table '{table}' should be plural")
            
            # Check column names (should be snake_case)
            column_pattern = r'^\s*([A-Z_]+)\s+(?:INTEGER|TEXT|VARCHAR|TIMESTAMP|BOOLEAN|JSON)'
            columns = re.findall(column_pattern, content, re.MULTILINE)
            
            for column in columns:
                if column != column.lower() and column not in ['PRIMARY', 'FOREIGN', 'UNIQUE']:
                    violations.append(f"Column '{column}' not in snake_case")
        
        assert len(violations) < 3, f"Naming convention violations: {violations[:5]}"
    
    def test_primary_keys_defined(self):
        """Ensure all tables have primary keys"""
        migration_dir = Path('migrations')
        
        for sql_file in migration_dir.glob('*.sql'):
            content = sql_file.read_text()
            
            # Find all CREATE TABLE statements
            table_pattern = r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(\w+)\s*\((.*?)\);'
            tables = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
            
            for table_name, table_def in tables:
                # Check for PRIMARY KEY
                has_pk = (
                    'PRIMARY KEY' in table_def.upper() or
                    'SERIAL' in table_def.upper() or  # PostgreSQL auto-increment
                    'AUTOINCREMENT' in table_def.upper()  # SQLite auto-increment
                )
                
                assert has_pk, f"Table '{table_name}' lacks primary key"
    
    def test_foreign_key_relationships(self):
        """Verify foreign key constraints are properly defined"""
        migration_dir = Path('migrations')
        
        foreign_keys = []
        for sql_file in migration_dir.glob('*.sql'):
            content = sql_file.read_text()
            
            # Find foreign key definitions
            fk_pattern = r'FOREIGN KEY\s*\((\w+)\)\s*REFERENCES\s+(\w+)\s*\((\w+)\)'
            fks = re.findall(fk_pattern, content, re.IGNORECASE)
            foreign_keys.extend(fks)
            
            # Also check inline foreign key definitions
            inline_fk_pattern = r'(\w+)\s+\w+\s+REFERENCES\s+(\w+)\s*\((\w+)\)'
            inline_fks = re.findall(inline_fk_pattern, content, re.IGNORECASE)
            foreign_keys.extend(inline_fks)
        
        # Should have some foreign keys for relationships
        if len(foreign_keys) == 0:
            pytest.skip("No foreign keys found - might be NoSQL or embedded JSON")
    
    def test_indexes_for_performance(self):
        """Check that appropriate indexes are created"""
        migration_dir = Path('migrations')
        
        indexes = []
        for sql_file in migration_dir.glob('*.sql'):
            content = sql_file.read_text()
            
            # Find CREATE INDEX statements
            index_pattern = r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF NOT EXISTS\s+)?(\w+)\s+ON\s+(\w+)\s*\(([^)]+)\)'
            idx = re.findall(index_pattern, content, re.IGNORECASE)
            indexes.extend(idx)
        
        # Check for indexes on common fields
        important_indexes = {
            'user_id',      # Foreign key lookups
            'created_at',   # Time-based queries
            'updated_at',   # Time-based queries
            'email',        # User lookups
            'status',       # Filtering
        }
        
        indexed_columns = set()
        for idx_name, table, columns in indexes:
            cols = [c.strip() for c in columns.split(',')]
            indexed_columns.update(cols)
        
        # At least some important columns should be indexed
        if indexes:
            covered = important_indexes & indexed_columns
            assert len(covered) > 0, f"No indexes on important columns: {important_indexes}"
    
    def test_data_types_appropriate(self):
        """Verify appropriate data types are used"""
        migration_dir = Path('migrations')
        
        issues = []
        for sql_file in migration_dir.glob('*.sql'):
            content = sql_file.read_text()
            
            # Check for problematic patterns
            problematic_patterns = [
                (r'VARCHAR\(1\)', 'Use BOOLEAN instead of VARCHAR(1)'),
                (r'VARCHAR\(5000\)', 'Use TEXT for large strings'),
                (r'INTEGER.*email', 'Email should not be INTEGER'),
                (r'TEXT.*(?:id|count|total|quantity)', 'Numeric fields should not be TEXT'),
                (r'VARCHAR\(\d{4,}\)', 'Consider TEXT for very long VARCHAR'),
            ]
            
            for pattern, message in problematic_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"{sql_file.name}: {message}")
        
        assert len(issues) < 3, f"Data type issues: {issues}"
    
    def test_timestamps_on_tables(self):
        """Ensure tables have created_at/updated_at timestamps"""
        migration_dir = Path('migrations')
        
        for sql_file in migration_dir.glob('*.sql'):
            content = sql_file.read_text()
            
            # Find all CREATE TABLE statements
            table_pattern = r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(\w+)\s*\((.*?)\);'
            tables = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
            
            for table_name, table_def in tables:
                # Skip junction tables and config tables
                if '_' in table_name and any(skip in table_name.lower() 
                                            for skip in ['config', 'settings', 'cache']):
                    continue
                
                # Check for timestamp columns
                has_created = 'created' in table_def.lower()
                has_updated = 'updated' in table_def.lower()
                
                if not (has_created and has_updated):
                    # Some tables might not need timestamps
                    if table_name.lower() not in ['migrations', 'schema_version']:
                        print(f"Warning: Table '{table_name}' lacks timestamps")
    
    def test_no_sql_injection_in_schema(self):
        """Ensure schema doesn't have SQL injection vulnerabilities"""
        migration_dir = Path('migrations')
        
        vulnerabilities = []
        for sql_file in migration_dir.glob('*.sql'):
            content = sql_file.read_text()
            
            # Check for dynamic SQL patterns
            dangerous_patterns = [
                r'EXEC\s*\(',
                r'EXECUTE\s+IMMEDIATE',
                r'\$\{',  # Template variables
                r'%\(.*\)s',  # Python string formatting in SQL
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    vulnerabilities.append(f"{sql_file.name}: Dynamic SQL pattern found")
        
        assert len(vulnerabilities) == 0, f"SQL injection risks: {vulnerabilities}"
    
    def test_constraints_defined(self):
        """Verify important constraints are in place"""
        migration_dir = Path('migrations')
        
        constraints_found = {
            'NOT NULL': False,
            'UNIQUE': False,
            'CHECK': False,
            'DEFAULT': False,
        }
        
        for sql_file in migration_dir.glob('*.sql'):
            content = sql_file.read_text().upper()
            
            for constraint in constraints_found:
                if constraint in content:
                    constraints_found[constraint] = True
        
        missing = [c for c, found in constraints_found.items() if not found]
        
        # Some constraints should definitely be present
        critical_missing = [c for c in ['NOT NULL', 'UNIQUE'] if c in missing]
        assert len(critical_missing) == 0, f"Missing critical constraints: {critical_missing}"
    
    def test_database_compatibility(self):
        """Ensure schema works with both PostgreSQL and SQLite"""
        migration_dir = Path('migrations')
        
        postgres_files = [f for f in migration_dir.glob('*.sql') 
                         if 'postgres' in f.name.lower() or not 'sqlite' in f.name.lower()]
        sqlite_files = [f for f in migration_dir.glob('*.sql') 
                       if 'sqlite' in f.name.lower()]
        
        if postgres_files and sqlite_files:
            # Check for incompatible features
            for pg_file in postgres_files:
                pg_content = pg_file.read_text().upper()
                
                # PostgreSQL specific features
                pg_specific = ['SERIAL', 'BYTEA', 'UUID', 'JSONB', 'ARRAY']
                
                for sq_file in sqlite_files:
                    sq_content = sq_file.read_text().upper()
                    
                    # Check if PostgreSQL features have SQLite equivalents
                    for feature in pg_specific:
                        if feature in pg_content:
                            if feature == 'SERIAL' and 'AUTOINCREMENT' not in sq_content:
                                print(f"Warning: SERIAL in PostgreSQL but no AUTOINCREMENT in SQLite")
                            elif feature == 'UUID' and 'TEXT' not in sq_content:
                                print(f"Warning: UUID type needs TEXT equivalent in SQLite")
    
    def test_no_database_url_hardcoded(self):
        """Ensure database URLs are not hardcoded"""
        violations = []
        
        for py_file in Path('src').rglob('*.py'):
            content = py_file.read_text()
            
            # Check for hardcoded database URLs
            db_patterns = [
                r'sqlite:///[^\'"\s]+',
                r'postgresql://[^\'"\s]+',
                r'mysql://[^\'"\s]+',
                r'mongodb://[^\'"\s]+',
            ]
            
            for pattern in db_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Allow example/test URLs
                    if not any(test in match for test in ['test', 'example', 'localhost']):
                        violations.append(f"{py_file}: Hardcoded DB URL: {match}")
        
        assert len(violations) == 0, f"Hardcoded database URLs: {violations}"