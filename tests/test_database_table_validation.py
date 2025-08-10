"""
Database Table Validation Tests for La Factoria
==============================================

Tests to ensure all required database tables are created properly.
Following TDD approach: RED -> GREEN -> REFACTOR
"""

import pytest
import asyncio
import sqlite3
import os
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.database import engine, Base, init_database, SessionLocal
from src.models.educational import EducationalContentDB, UserModel


class TestDatabaseTableValidation:
    """Test database table creation and validation"""
    
    @pytest.mark.asyncio
    async def test_database_tables_exist(self):
        """
        Test that all required database tables exist after initialization.
        
        Required tables:
        - users (UserModel)
        - educational_content (EducationalContentDB)
        """
        # Initialize database
        await init_database()
        
        # Get inspector to check table existence
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        # Check that required tables exist
        required_tables = ['users', 'educational_content']
        
        for table_name in required_tables:
            assert table_name in table_names, f"Required table '{table_name}' not found in database. Found tables: {table_names}"
    
    @pytest.mark.asyncio
    async def test_users_table_structure(self):
        """Test that users table has the correct structure"""
        await init_database()
        
        inspector = inspect(engine)
        columns = inspector.get_columns('users')
        column_names = [col['name'] for col in columns]
        
        # Check required columns exist
        required_columns = ['id', 'username', 'email', 'is_active', 'created_at', 'updated_at']
        
        for column_name in required_columns:
            assert column_name in column_names, f"Required column '{column_name}' not found in users table. Found columns: {column_names}"
    
    @pytest.mark.asyncio 
    async def test_educational_content_table_structure(self):
        """Test that educational_content table has the correct structure"""
        await init_database()
        
        inspector = inspect(engine)
        columns = inspector.get_columns('educational_content')
        column_names = [col['name'] for col in columns]
        
        # Check required columns exist
        required_columns = ['id', 'content_type', 'topic', 'age_group', 'generated_content', 'created_at', 'updated_at']
        
        for column_name in required_columns:
            assert column_name in column_names, f"Required column '{column_name}' not found in educational_content table. Found columns: {column_names}"
    
    @pytest.mark.asyncio
    async def test_database_connection_works(self):
        """Test that database connection is functional"""
        await init_database()
        
        # Test basic database operation
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1, "Database connection test failed"
    
    @pytest.mark.asyncio
    async def test_tables_can_be_queried(self):
        """Test that tables can be queried without errors"""
        await init_database()
        
        with engine.connect() as connection:
            # Test querying users table
            try:
                connection.execute(text("SELECT COUNT(*) FROM users"))
            except Exception as e:
                pytest.fail(f"Failed to query users table: {e}")
            
            # Test querying educational_content table
            try:
                connection.execute(text("SELECT COUNT(*) FROM educational_content"))
            except Exception as e:
                pytest.fail(f"Failed to query educational_content table: {e}")
    
    @pytest.mark.asyncio
    async def test_table_indexes_exist(self):
        """Test that required indexes are created"""
        await init_database()
        
        inspector = inspect(engine)
        
        # Check users table indexes
        users_indexes = inspector.get_indexes('users')
        users_index_names = [idx['name'] for idx in users_indexes]
        
        expected_users_indexes = ['idx_users_email', 'idx_users_username']
        for index_name in expected_users_indexes:
            assert any(index_name in idx_name for idx_name in users_index_names), \
                f"Expected index '{index_name}' not found in users table indexes: {users_index_names}"
        
        # Check educational_content table indexes
        content_indexes = inspector.get_indexes('educational_content')
        content_index_names = [idx['name'] for idx in content_indexes]
        
        expected_content_indexes = ['idx_educational_content_content_type', 'idx_educational_content_topic', 'idx_educational_content_created_at']
        for index_name in expected_content_indexes:
            assert any(index_name in idx_name for idx_name in content_index_names), \
                f"Expected index '{index_name}' not found in educational_content table indexes: {content_index_names}"

    def test_database_models_are_registered_with_base(self):
        """Test that all database models are properly registered with SQLAlchemy Base"""
        # Check that models are registered with Base metadata
        table_names = list(Base.metadata.tables.keys())
        
        expected_tables = ['users', 'educational_content']
        
        for table_name in expected_tables:
            assert table_name in table_names, f"Model for table '{table_name}' not registered with Base. Registered tables: {table_names}"
    
    @pytest.mark.asyncio
    async def test_session_creation_works(self):
        """Test that database sessions can be created and used"""
        await init_database()
        
        # Test session creation
        session = SessionLocal()
        
        try:
            # Test basic session operation
            result = session.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1, "Session operation failed"
        finally:
            session.close()


class TestDatabaseInitialization:
    """Test database initialization process"""
    
    @pytest.mark.asyncio
    async def test_init_database_creates_all_tables(self):
        """Test that init_database creates all required tables"""
        # Clean up any existing database
        if os.path.exists("test_la_factoria.db"):
            os.remove("test_la_factoria.db")
        
        # Initialize database
        await init_database()
        
        # Check that tables were created
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        assert len(table_names) >= 2, f"Expected at least 2 tables, found {len(table_names)}: {table_names}"
        assert 'users' in table_names, "users table not created"
        assert 'educational_content' in table_names, "educational_content table not created"
    
    @pytest.mark.asyncio
    async def test_init_database_handles_already_existing_tables(self):
        """Test that init_database can handle already existing tables"""
        # Initialize database twice
        await init_database()
        await init_database()  # Should not raise an error
        
        # Check that tables still exist
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        assert 'users' in table_names, "users table missing after re-initialization"
        assert 'educational_content' in table_names, "educational_content table missing after re-initialization"