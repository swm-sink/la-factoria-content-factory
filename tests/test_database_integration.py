"""
Database Integration Tests for La Factoria
==========================================

Comprehensive database integration tests covering:
- Database connection and initialization
- CRUD operations for all database models
- Transaction handling and rollback
- Connection pooling and performance
- Data persistence and integrity
- Migration and schema operations
- Error handling and recovery
- Concurrent database operations

Tests work with both SQLite (development) and PostgreSQL (production).
"""

# Fix Python path for src imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import asyncio
import uuid
import time
import tempfile
import os
from typing import Dict, Any, List
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from sqlalchemy import text, inspect, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.database import (
    engine, SessionLocal, get_database, init_database,
    check_database_connection, get_database_info, DatabaseManager,
    Base, metadata
)
from src.models.educational import (
    EducationalContentDB, UserModel, LaFactoriaContentType,
    LearningLevel, CognitiveLevel
)
from src.core.config import settings


class TestDatabaseConnection:
    """Test database connection and basic operations"""

    @pytest.mark.database
    @pytest.mark.asyncio
    async def test_database_connection_health(self):
        """Test database connectivity health check"""
        is_healthy = await check_database_connection()
        assert is_healthy == True

    @pytest.mark.database
    @pytest.mark.asyncio
    async def test_database_info_retrieval(self):
        """Test database information retrieval"""
        db_info = await get_database_info()

        assert isinstance(db_info, dict)
        assert "status" in db_info

        if db_info["status"] == "healthy":
            assert "version" in db_info
            assert "url" in db_info
            assert "pool_size" in db_info
        else:
            assert "error" in db_info

    @pytest.mark.database
    def test_session_factory_creation(self):
        """Test database session factory creation"""
        session = SessionLocal()

        try:
            # Should be able to create session
            assert session is not None

            # Test basic query
            result = session.execute(text("SELECT 1")).fetchone()
            assert result[0] == 1

        finally:
            session.close()

    @pytest.mark.database
    def test_database_dependency_injection(self):
        """Test database dependency for FastAPI"""
        db_generator = get_database()

        # Should yield a database session
        db_session = next(db_generator)
        assert db_session is not None

        try:
            # Session should be functional
            result = db_session.execute(text("SELECT 1")).fetchone()
            assert result[0] == 1
        except StopIteration:
            pass  # Generator exhausted, which is expected

    @pytest.mark.database
    @pytest.mark.asyncio
    async def test_database_initialization(self):
        """Test database table initialization"""
        # This will create tables if they don't exist
        await init_database()

        # Verify tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_tables = ['educational_content', 'users']
        for table in expected_tables:
            assert table in tables

    @pytest.mark.database
    def test_database_url_configuration(self):
        """Test database URL configuration"""
        # Should have a valid database URL
        assert settings.database_url is not None
        assert len(settings.database_url) > 0

        # Should be either SQLite or PostgreSQL
        assert (settings.database_url.startswith("sqlite") or
                settings.database_url.startswith("postgresql"))


class TestEducationalContentDB:
    """Test CRUD operations for EducationalContentDB"""

    @pytest.fixture
    def test_session(self):
        """Create test database session"""
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @pytest.fixture
    def sample_educational_content(self):
        """Create sample educational content for testing"""
        return {
            "content_type": LaFactoriaContentType.STUDY_GUIDE.value,
            "topic": "Database Integration Testing",
            "age_group": LearningLevel.HIGH_SCHOOL.value,
            "learning_objectives": [
                {
                    "cognitive_level": "understanding",
                    "subject_area": "Computer Science",
                    "specific_skill": "Database operations",
                    "measurable_outcome": "Perform CRUD operations",
                    "difficulty_level": 6
                }
            ],
            "cognitive_load_metrics": {
                "intrinsic_load": 0.7,
                "extraneous_load": 0.3,
                "germane_load": 0.5,
                "total_cognitive_load": 1.5
            },
            "generated_content": {
                "title": "Database Integration Study Guide",
                "sections": [
                    {"title": "Introduction", "content": "Database fundamentals"},
                    {"title": "CRUD Operations", "content": "Create, Read, Update, Delete"}
                ],
                "summary": "Learn database operations"
            },
            "quality_score": 0.85,
            "generation_duration_ms": 2500,
            "ai_provider": "openai"
        }

    @pytest.mark.database
    def test_create_educational_content(self, test_session, sample_educational_content):
        """Test creating educational content in database"""
        content = EducationalContentDB(**sample_educational_content)

        test_session.add(content)
        test_session.commit()

        # Verify creation
        assert content.id is not None
        assert content.created_at is not None
        assert content.content_type == LaFactoriaContentType.STUDY_GUIDE.value

    @pytest.mark.database
    def test_read_educational_content(self, test_session, sample_educational_content):
        """Test reading educational content from database"""
        # Create content
        content = EducationalContentDB(**sample_educational_content)
        test_session.add(content)
        test_session.commit()

        content_id = content.id

        # Read content back
        retrieved_content = test_session.query(EducationalContentDB).filter_by(id=content_id).first()

        assert retrieved_content is not None
        assert retrieved_content.topic == "Database Integration Testing"
        assert retrieved_content.content_type == LaFactoriaContentType.STUDY_GUIDE.value
        assert retrieved_content.quality_score == 0.85

    @pytest.mark.database
    def test_update_educational_content(self, test_session, sample_educational_content):
        """Test updating educational content in database"""
        # Create content
        content = EducationalContentDB(**sample_educational_content)
        test_session.add(content)
        test_session.commit()

        content_id = content.id

        # Update content
        content.topic = "Updated Database Testing Topic"
        content.quality_score = 0.92
        test_session.commit()

        # Verify update
        updated_content = test_session.query(EducationalContentDB).filter_by(id=content_id).first()
        assert updated_content.topic == "Updated Database Testing Topic"
        assert updated_content.quality_score == 0.92
        assert updated_content.updated_at is not None

    @pytest.mark.database
    def test_delete_educational_content(self, test_session, sample_educational_content):
        """Test deleting educational content from database"""
        # Create content
        content = EducationalContentDB(**sample_educational_content)
        test_session.add(content)
        test_session.commit()

        content_id = content.id

        # Delete content
        test_session.delete(content)
        test_session.commit()

        # Verify deletion
        deleted_content = test_session.query(EducationalContentDB).filter_by(id=content_id).first()
        assert deleted_content is None

    @pytest.mark.database
    def test_educational_content_json_fields(self, test_session, sample_educational_content):
        """Test JSON field storage and retrieval"""
        content = EducationalContentDB(**sample_educational_content)
        test_session.add(content)
        test_session.commit()

        # Test JSON fields
        retrieved_content = test_session.query(EducationalContentDB).filter_by(id=content.id).first()

        # Learning objectives should be stored as JSON
        assert isinstance(retrieved_content.learning_objectives, list)
        assert len(retrieved_content.learning_objectives) == 1
        assert retrieved_content.learning_objectives[0]["cognitive_level"] == "understanding"

        # Generated content should be stored as JSON
        assert isinstance(retrieved_content.generated_content, dict)
        assert retrieved_content.generated_content["title"] == "Database Integration Study Guide"

        # Cognitive load metrics should be stored as JSON
        assert isinstance(retrieved_content.cognitive_load_metrics, dict)
        assert retrieved_content.cognitive_load_metrics["intrinsic_load"] == 0.7

    @pytest.mark.database
    def test_educational_content_indexes_performance(self, test_session):
        """Test database index performance"""
        # Create multiple content entries
        content_entries = []
        for i in range(10):
            content = EducationalContentDB(
                content_type=LaFactoriaContentType.FLASHCARDS.value,
                topic=f"Performance Test {i}",
                age_group=LearningLevel.MIDDLE_SCHOOL.value,
                learning_objectives=[],
                cognitive_load_metrics={},
                generated_content={"cards": []},
                quality_score=0.8 + (i * 0.01)
            )
            content_entries.append(content)

        test_session.add_all(content_entries)
        test_session.commit()

        # Test index performance on content_type
        start_time = time.time()
        results = test_session.query(EducationalContentDB).filter_by(
            content_type=LaFactoriaContentType.FLASHCARDS.value
        ).all()
        end_time = time.time()

        assert len(results) == 10
        # Query should be fast with index
        assert (end_time - start_time) < 1.0

    @pytest.mark.database
    def test_educational_content_topic_search(self, test_session):
        """Test topic-based searching"""
        # Create test content with various topics
        topics = ["Math Algebra", "Science Biology", "History World War", "Math Geometry"]

        for topic in topics:
            content = EducationalContentDB(
                content_type=LaFactoriaContentType.STUDY_GUIDE.value,
                topic=topic,
                age_group=LearningLevel.HIGH_SCHOOL.value,
                learning_objectives=[],
                cognitive_load_metrics={},
                generated_content={"title": topic}
            )
            test_session.add(content)

        test_session.commit()

        # Test topic search
        math_results = test_session.query(EducationalContentDB).filter(
            EducationalContentDB.topic.contains("Math")
        ).all()

        assert len(math_results) == 2
        assert all("Math" in result.topic for result in math_results)


class TestUserModel:
    """Test CRUD operations for UserModel"""

    @pytest.fixture
    def test_session(self):
        """Create test database session"""
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @pytest.fixture
    def sample_user_data(self):
        """Create sample user data for testing"""
        return {
            "username": "testuser123",
            "email": "testuser@lafactoria.test",
            "api_key_hash": "hashed_api_key_value_123",
            "is_active": True,
            "learning_preferences": {
                "preferred_content_types": ["study_guide", "flashcards"],
                "learning_level": "high_school",
                "language": "en"
            }
        }

    @pytest.mark.database
    def test_create_user(self, test_session, sample_user_data):
        """Test creating user in database"""
        user = UserModel(**sample_user_data)

        test_session.add(user)
        test_session.commit()

        # Verify creation
        assert user.id is not None
        assert user.created_at is not None
        assert user.username == "testuser123"

    @pytest.mark.database
    def test_read_user(self, test_session, sample_user_data):
        """Test reading user from database"""
        # Create user
        user = UserModel(**sample_user_data)
        test_session.add(user)
        test_session.commit()

        user_id = user.id

        # Read user back
        retrieved_user = test_session.query(UserModel).filter_by(id=user_id).first()

        assert retrieved_user is not None
        assert retrieved_user.email == "testuser@lafactoria.test"
        assert retrieved_user.is_active == True

    @pytest.mark.database
    def test_update_user(self, test_session, sample_user_data):
        """Test updating user in database"""
        # Create user
        user = UserModel(**sample_user_data)
        test_session.add(user)
        test_session.commit()

        user_id = user.id

        # Update user
        user.email = "updated@lafactoria.test"
        user.is_active = False
        test_session.commit()

        # Verify update
        updated_user = test_session.query(UserModel).filter_by(id=user_id).first()
        assert updated_user.email == "updated@lafactoria.test"
        assert updated_user.is_active == False
        assert updated_user.updated_at is not None

    @pytest.mark.database
    def test_delete_user(self, test_session, sample_user_data):
        """Test deleting user from database"""
        # Create user
        user = UserModel(**sample_user_data)
        test_session.add(user)
        test_session.commit()

        user_id = user.id

        # Delete user
        test_session.delete(user)
        test_session.commit()

        # Verify deletion
        deleted_user = test_session.query(UserModel).filter_by(id=user_id).first()
        assert deleted_user is None

    @pytest.mark.database
    def test_user_unique_constraints(self, test_session, sample_user_data):
        """Test unique constraints on username and email"""
        # Create first user
        user1 = UserModel(**sample_user_data)
        test_session.add(user1)
        test_session.commit()

        # Try to create second user with same email
        user2_data = sample_user_data.copy()
        user2_data["username"] = "differentuser"
        user2 = UserModel(**user2_data)
        test_session.add(user2)

        # Should raise integrity error due to duplicate email
        with pytest.raises(IntegrityError):
            test_session.commit()

        test_session.rollback()

        # Try to create user with same username
        user3_data = sample_user_data.copy()
        user3_data["email"] = "different@lafactoria.test"
        user3 = UserModel(**user3_data)
        test_session.add(user3)

        # Should raise integrity error due to duplicate username
        with pytest.raises(IntegrityError):
            test_session.commit()

    @pytest.mark.database
    def test_user_learning_preferences_json(self, test_session, sample_user_data):
        """Test user learning preferences JSON storage"""
        user = UserModel(**sample_user_data)
        test_session.add(user)
        test_session.commit()

        # Retrieve and verify JSON field
        retrieved_user = test_session.query(UserModel).filter_by(id=user.id).first()

        assert isinstance(retrieved_user.learning_preferences, dict)
        assert retrieved_user.learning_preferences["learning_level"] == "high_school"
        assert "study_guide" in retrieved_user.learning_preferences["preferred_content_types"]

    @pytest.mark.database
    def test_user_search_by_email(self, test_session):
        """Test user search by email"""
        # Create multiple users
        users_data = [
            {"username": "user1", "email": "user1@test.com", "api_key_hash": "hash1"},
            {"username": "user2", "email": "user2@test.com", "api_key_hash": "hash2"},
            {"username": "user3", "email": "admin@test.com", "api_key_hash": "hash3"}
        ]

        for user_data in users_data:
            user = UserModel(**user_data)
            test_session.add(user)

        test_session.commit()

        # Search by email
        user = test_session.query(UserModel).filter_by(email="user2@test.com").first()
        assert user is not None
        assert user.username == "user2"


class TestDatabaseTransactions:
    """Test database transaction handling"""

    @pytest.fixture
    def test_session(self):
        """Create test database session"""
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @pytest.mark.database
    def test_transaction_commit(self, test_session):
        """Test successful transaction commit"""
        # Create user and content in same transaction
        user = UserModel(
            username="transaction_user",
            email="transaction@test.com",
            api_key_hash="transaction_hash"
        )

        content = EducationalContentDB(
            content_type=LaFactoriaContentType.FLASHCARDS.value,
            topic="Transaction Test",
            age_group=LearningLevel.HIGH_SCHOOL.value,
            learning_objectives=[],
            cognitive_load_metrics={},
            generated_content={"cards": []}
        )

        test_session.add(user)
        test_session.add(content)
        test_session.commit()

        # Verify both were created
        assert test_session.query(UserModel).filter_by(username="transaction_user").first() is not None
        assert test_session.query(EducationalContentDB).filter_by(topic="Transaction Test").first() is not None

    @pytest.mark.database
    def test_transaction_rollback(self, test_session):
        """Test transaction rollback on error"""
        # Create user
        user = UserModel(
            username="rollback_user",
            email="rollback@test.com",
            api_key_hash="rollback_hash"
        )
        test_session.add(user)
        test_session.commit()

        # Start new transaction that will fail
        try:
            content = EducationalContentDB(
                content_type=LaFactoriaContentType.STUDY_GUIDE.value,
                topic="Rollback Test",
                age_group=LearningLevel.HIGH_SCHOOL.value,
                learning_objectives=[],
                cognitive_load_metrics={},
                generated_content={"title": "Test"}
            )
            test_session.add(content)

            # Create duplicate user (should fail due to unique constraint)
            duplicate_user = UserModel(
                username="rollback_user",  # Duplicate username
                email="different@test.com",
                api_key_hash="different_hash"
            )
            test_session.add(duplicate_user)
            test_session.commit()

        except IntegrityError:
            test_session.rollback()

        # Verify content was not created due to rollback
        assert test_session.query(EducationalContentDB).filter_by(topic="Rollback Test").first() is None

        # But original user should still exist
        assert test_session.query(UserModel).filter_by(username="rollback_user").first() is not None

    @pytest.mark.database
    @pytest.mark.asyncio
    async def test_concurrent_transactions(self):
        """Test concurrent database transactions"""

        async def create_content(topic_suffix: str):
            """Create content in separate session"""
            session = SessionLocal()
            try:
                content = EducationalContentDB(
                    content_type=LaFactoriaContentType.ONE_PAGER_SUMMARY.value,
                    topic=f"Concurrent Content {topic_suffix}",
                    age_group=LearningLevel.COLLEGE.value,
                    learning_objectives=[],
                    cognitive_load_metrics={},
                    generated_content={"summary": f"Content {topic_suffix}"}
                )
                session.add(content)
                session.commit()
                return content.id
            finally:
                session.close()

        # Create multiple concurrent transactions
        tasks = [create_content(str(i)) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == 5

        # Verify all content was created
        session = SessionLocal()
        try:
            count = session.query(EducationalContentDB).filter(
                EducationalContentDB.topic.contains("Concurrent Content")
            ).count()
            assert count == 5
        finally:
            session.close()


class TestConnectionPooling:
    """Test database connection pooling"""

    @pytest.mark.database
    @pytest.mark.slow
    def test_connection_pool_exhaustion(self):
        """Test behavior when connection pool is exhausted"""
        sessions = []

        try:
            # Create sessions up to pool limit
            for i in range(settings.DB_POOL_SIZE + settings.DB_MAX_OVERFLOW):
                session = SessionLocal()
                sessions.append(session)

                # Perform simple query to establish connection
                session.execute(text("SELECT 1"))

            # Should still be able to create more sessions (they will wait)
            extra_session = SessionLocal()
            sessions.append(extra_session)

            # This query might timeout or succeed depending on implementation
            result = extra_session.execute(text("SELECT 1")).fetchone()
            assert result[0] == 1

        finally:
            # Clean up all sessions
            for session in sessions:
                session.close()

    @pytest.mark.database
    def test_connection_reuse(self):
        """Test that connections are properly reused"""
        # Create and close multiple sessions
        for i in range(10):
            session = SessionLocal()
            try:
                result = session.execute(text("SELECT 1")).fetchone()
                assert result[0] == 1
            finally:
                session.close()

        # Connection pool should reuse connections efficiently
        # This is more of a behavioral test - hard to assert specific metrics

    @pytest.mark.database
    @pytest.mark.asyncio
    async def test_connection_health_check(self):
        """Test connection health checking"""
        # Test pool pre-ping functionality
        session = SessionLocal()
        try:
            # This should work with pool pre-ping enabled
            result = session.execute(text("SELECT 1")).fetchone()
            assert result[0] == 1
        finally:
            session.close()


class TestDatabaseManager:
    """Test DatabaseManager utility functions"""

    @pytest.mark.database
    @pytest.mark.asyncio
    async def test_get_table_stats(self):
        """Test getting table statistics"""
        stats = await DatabaseManager.get_table_stats()

        assert isinstance(stats, dict)

        if "error" not in stats:
            # Should have stats for expected tables
            expected_tables = ['educational_content', 'users']

            for table in expected_tables:
                if table in stats:
                    assert isinstance(stats[table], dict)
                    assert "row_count" in stats[table]

    @pytest.mark.database
    @pytest.mark.asyncio
    async def test_run_migration_success(self):
        """Test successful migration execution"""
        # Create temporary migration file
        migration_sql = """
        CREATE TABLE IF NOT EXISTS test_migration_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100)
        );

        INSERT INTO test_migration_table (name) VALUES ('test_data');
        """

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(migration_sql)
            migration_file = f.name

        try:
            # Run migration
            await DatabaseManager.run_migration(migration_file)

            # Verify migration was successful
            session = SessionLocal()
            try:
                result = session.execute(text("SELECT name FROM test_migration_table")).fetchone()
                assert result[0] == 'test_data'

                # Clean up test table
                session.execute(text("DROP TABLE test_migration_table"))
                session.commit()
            finally:
                session.close()

        finally:
            # Clean up temporary file
            os.unlink(migration_file)

    @pytest.mark.database
    @pytest.mark.asyncio
    async def test_run_migration_failure(self):
        """Test migration failure handling"""
        # Create migration with invalid SQL
        migration_sql = "INVALID SQL STATEMENT;"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(migration_sql)
            migration_file = f.name

        try:
            # Should raise exception on invalid SQL
            with pytest.raises(Exception):
                await DatabaseManager.run_migration(migration_file)
        finally:
            # Clean up temporary file
            os.unlink(migration_file)


class TestDatabasePerformance:
    """Test database performance under load"""

    @pytest.fixture
    def test_session(self):
        """Create test database session"""
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @pytest.mark.database
    @pytest.mark.slow
    def test_bulk_insert_performance(self, test_session):
        """Test bulk insert performance"""
        # Create large number of content entries
        content_entries = []
        start_time = time.time()

        for i in range(100):
            content = EducationalContentDB(
                content_type=LaFactoriaContentType.FAQ_COLLECTION.value,
                topic=f"Performance Test {i}",
                age_group=LearningLevel.ADULT_LEARNING.value,
                learning_objectives=[{"cognitive_level": "understanding"}],
                cognitive_load_metrics={"total_load": 1.0},
                generated_content={"faqs": [{"q": f"Question {i}", "a": f"Answer {i}"}]},
                quality_score=0.8
            )
            content_entries.append(content)

        # Bulk insert
        test_session.add_all(content_entries)
        test_session.commit()

        end_time = time.time()
        insert_time = end_time - start_time

        # Should complete bulk insert reasonably quickly
        assert insert_time < 10.0, f"Bulk insert took {insert_time:.2f} seconds"

        # Verify all entries were created
        count = test_session.query(EducationalContentDB).filter(
            EducationalContentDB.topic.contains("Performance Test")
        ).count()
        assert count == 100

    @pytest.mark.database
    @pytest.mark.slow
    def test_complex_query_performance(self, test_session):
        """Test performance of complex queries"""
        # Create test data
        content_types = list(LaFactoriaContentType)
        age_groups = list(LearningLevel)

        for i in range(50):
            content = EducationalContentDB(
                content_type=content_types[i % len(content_types)].value,
                topic=f"Complex Query Test {i}",
                age_group=age_groups[i % len(age_groups)].value,
                learning_objectives=[],
                cognitive_load_metrics={},
                generated_content={"content": f"Content {i}"},
                quality_score=0.7 + (i % 3) * 0.1
            )
            test_session.add(content)

        test_session.commit()

        # Complex query with joins and filtering
        start_time = time.time()

        results = test_session.query(EducationalContentDB).filter(
            EducationalContentDB.quality_score >= 0.75,
            EducationalContentDB.content_type.in_([
                LaFactoriaContentType.STUDY_GUIDE.value,
                LaFactoriaContentType.FLASHCARDS.value
            ])
        ).order_by(EducationalContentDB.created_at.desc()).limit(10).all()

        end_time = time.time()
        query_time = end_time - start_time

        # Query should complete quickly with proper indexing
        assert query_time < 1.0, f"Complex query took {query_time:.3f} seconds"
        assert len(results) <= 10

    @pytest.mark.database
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_concurrent_read_write_performance(self):
        """Test concurrent read/write performance"""

        async def write_operations():
            """Perform write operations"""
            session = SessionLocal()
            try:
                for i in range(10):
                    content = EducationalContentDB(
                        content_type=LaFactoriaContentType.READING_GUIDE_QUESTIONS.value,
                        topic=f"Concurrent Write {i}",
                        age_group=LearningLevel.HIGH_SCHOOL.value,
                        learning_objectives=[],
                        cognitive_load_metrics={},
                        generated_content={"questions": []}
                    )
                    session.add(content)
                session.commit()
            finally:
                session.close()

        async def read_operations():
            """Perform read operations"""
            session = SessionLocal()
            try:
                for i in range(20):
                    results = session.query(EducationalContentDB).limit(5).all()
                    # Just ensure we can read data
                    assert isinstance(results, list)
            finally:
                session.close()

        # Run concurrent read and write operations
        start_time = time.time()

        tasks = [
            write_operations(),
            read_operations(),
            read_operations()  # Multiple readers
        ]

        await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # Should handle concurrent operations efficiently
        assert total_time < 5.0, f"Concurrent operations took {total_time:.2f} seconds"


class TestDatabaseErrorHandling:
    """Test database error handling and recovery"""

    @pytest.fixture
    def test_session(self):
        """Create test database session"""
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @pytest.mark.database
    def test_constraint_violation_handling(self, test_session):
        """Test handling of constraint violations"""
        # Create user
        user1 = UserModel(
            username="constraint_test",
            email="constraint@test.com",
            api_key_hash="hash123"
        )
        test_session.add(user1)
        test_session.commit()

        # Try to create duplicate user
        user2 = UserModel(
            username="constraint_test",  # Duplicate username
            email="different@test.com",
            api_key_hash="hash456"
        )
        test_session.add(user2)

        # Should raise IntegrityError
        with pytest.raises(IntegrityError):
            test_session.commit()

        # Session should be in rollback state
        assert test_session.in_transaction() == False or test_session.is_active == False

    @pytest.mark.database
    def test_invalid_data_type_handling(self, test_session):
        """Test handling of invalid data types"""
        try:
            # Try to create content with invalid data
            content = EducationalContentDB(
                content_type="invalid_content_type",  # Invalid enum value
                topic="Error Test",
                age_group=LearningLevel.HIGH_SCHOOL.value,
                learning_objectives=[],
                cognitive_load_metrics={},
                generated_content={"content": "test"}
            )
            test_session.add(content)
            test_session.commit()

            # If this doesn't fail at the database level,
            # the application should validate enum values

        except (SQLAlchemyError, ValueError):
            # Expected behavior - invalid data rejected
            test_session.rollback()

    @pytest.mark.database
    @pytest.mark.asyncio
    async def test_connection_recovery(self):
        """Test connection recovery after failure"""
        # This test simulates connection recovery
        # In a real scenario, this would test actual connection failures

        # Test that connection health check works
        is_healthy = await check_database_connection()

        if not is_healthy:
            # If connection is not healthy, subsequent operations should handle gracefully
            db_info = await get_database_info()
            assert db_info["status"] == "unhealthy"
            assert "error" in db_info
        else:
            assert is_healthy == True

    @pytest.mark.database
    def test_session_cleanup_after_error(self):
        """Test proper session cleanup after errors"""
        session = SessionLocal()

        try:
            # Force an error
            session.execute(text("SELECT * FROM nonexistent_table"))
        except SQLAlchemyError:
            # Expected error
            pass
        finally:
            # Session should be cleanable
            session.close()

        # Should be able to create new session after error
        new_session = SessionLocal()
        try:
            result = new_session.execute(text("SELECT 1")).fetchone()
            assert result[0] == 1
        finally:
            new_session.close()


class TestDataIntegrity:
    """Test data integrity and consistency"""

    @pytest.fixture
    def test_session(self):
        """Create test database session"""
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @pytest.mark.database
    def test_uuid_generation_uniqueness(self, test_session):
        """Test UUID generation for unique IDs"""
        # Create multiple records and verify UUID uniqueness
        users = []
        for i in range(10):
            user = UserModel(
                username=f"uuid_test_{i}",
                email=f"uuid{i}@test.com",
                api_key_hash=f"hash_{i}"
            )
            users.append(user)

        test_session.add_all(users)
        test_session.commit()

        # Verify all UUIDs are unique
        user_ids = [user.id for user in users]
        assert len(set(user_ids)) == 10  # All unique

    @pytest.mark.database
    def test_timestamp_automatic_generation(self, test_session):
        """Test automatic timestamp generation"""
        # Create content
        content = EducationalContentDB(
            content_type=LaFactoriaContentType.PODCAST_SCRIPT.value,
            topic="Timestamp Test",
            age_group=LearningLevel.COLLEGE.value,
            learning_objectives=[],
            cognitive_load_metrics={},
            generated_content={"script": "test"}
        )

        test_session.add(content)
        test_session.commit()

        # created_at should be automatically set
        assert content.created_at is not None
        assert isinstance(content.created_at, datetime)

        # updated_at should be None initially
        assert content.updated_at is None

        # Update the record
        original_created_at = content.created_at
        content.topic = "Updated Timestamp Test"
        test_session.commit()

        # created_at should remain the same
        assert content.created_at == original_created_at

        # updated_at should now be set
        assert content.updated_at is not None
        assert content.updated_at > content.created_at

    @pytest.mark.database
    def test_json_field_integrity(self, test_session):
        """Test JSON field data integrity"""
        # Create content with complex JSON data
        complex_data = {
            "learning_objectives": [
                {
                    "cognitive_level": "analyzing",
                    "subject_area": "Data Science",
                    "specific_skill": "statistical analysis",
                    "measurable_outcome": "interpret statistical results",
                    "difficulty_level": 8
                }
            ],
            "cognitive_load_metrics": {
                "intrinsic_load": 0.8,
                "extraneous_load": 0.2,
                "germane_load": 0.6,
                "total_cognitive_load": 1.6,
                "nested_data": {
                    "complexity_factors": ["statistical_concepts", "data_interpretation"],
                    "mitigation_strategies": ["visual_aids", "step_by_step_guidance"]
                }
            },
            "generated_content": {
                "title": "Advanced Statistical Analysis",
                "sections": [
                    {
                        "title": "Introduction to Statistics",
                        "content": "Statistics is the science of collecting and analyzing data.",
                        "subsections": [
                            {"title": "Descriptive Statistics", "content": "Mean, median, mode"},
                            {"title": "Inferential Statistics", "content": "Hypothesis testing"}
                        ]
                    }
                ],
                "exercises": [
                    {"question": "Calculate the mean", "answer": "Sum all values and divide by count"},
                    {"question": "What is a p-value?", "answer": "Probability of observing results"}
                ]
            }
        }

        content = EducationalContentDB(
            content_type=LaFactoriaContentType.DETAILED_READING_MATERIAL.value,
            topic="JSON Integrity Test",
            age_group=LearningLevel.COLLEGE.value,
            **complex_data
        )

        test_session.add(content)
        test_session.commit()

        # Retrieve and verify complex JSON data integrity
        retrieved_content = test_session.query(EducationalContentDB).filter_by(id=content.id).first()

        # Verify nested JSON structure
        assert len(retrieved_content.learning_objectives) == 1
        assert retrieved_content.learning_objectives[0]["cognitive_level"] == "analyzing"

        # Verify deeply nested JSON
        nested_data = retrieved_content.cognitive_load_metrics["nested_data"]
        assert "complexity_factors" in nested_data
        assert len(nested_data["complexity_factors"]) == 2

        # Verify complex generated content structure
        sections = retrieved_content.generated_content["sections"]
        assert len(sections) == 1
        assert len(sections[0]["subsections"]) == 2
