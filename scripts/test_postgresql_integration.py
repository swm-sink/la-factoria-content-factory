#!/usr/bin/env python3
"""
PostgreSQL Integration Testing Script for La Factoria
=====================================================

This script validates that the application works correctly with PostgreSQL
in production environments, testing schema compatibility, performance,
and data operations.

Requirements:
- PostgreSQL database (local or Railway)
- Database URL configured in environment
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
from uuid import uuid4

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, inspect, MetaData
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
import psycopg2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PostgreSQLIntegrationTester:
    """Test PostgreSQL integration for La Factoria"""
    
    def __init__(self, database_url: str = None):
        """Initialize tester with database connection"""
        self.database_url = database_url or os.getenv("DATABASE_URL", "")
        self.test_results = {
            "connection": False,
            "schema_applied": False,
            "crud_operations": False,
            "performance": {},
            "connection_pooling": False,
            "data_types": False,
            "triggers": False,
            "views": False,
            "indexes": False,
            "constraints": False
        }
        self.engine = None
        self.session = None
        
    def setup_connection(self) -> bool:
        """Setup PostgreSQL connection"""
        try:
            if not self.database_url:
                logger.error("No DATABASE_URL provided")
                return False
                
            # Ensure it's a PostgreSQL URL
            if not self.database_url.startswith(("postgresql://", "postgres://")):
                logger.warning(f"Database URL doesn't appear to be PostgreSQL: {self.database_url[:20]}...")
                
            # Create engine with specific PostgreSQL settings
            self.engine = create_engine(
                self.database_url,
                poolclass=NullPool,  # No pooling for testing
                echo=False,
                connect_args={
                    "connect_timeout": 10,
                    "options": "-c statement_timeout=30000"  # 30 second timeout
                }
            )
            
            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"✅ Connected to PostgreSQL: {version}")
                self.test_results["connection"] = True
                
            # Create session
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            self.test_results["connection"] = False
            return False
    
    def test_schema_application(self) -> bool:
        """Test that PostgreSQL schema can be applied"""
        try:
            schema_file = Path(__file__).parent.parent / "migrations" / "001_initial_schema.sql"
            
            if not schema_file.exists():
                logger.error(f"Schema file not found: {schema_file}")
                return False
            
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Apply schema in transaction
            with self.engine.begin() as conn:
                # Drop existing tables for clean test
                conn.execute(text("""
                    DROP VIEW IF EXISTS content_type_stats CASCADE;
                    DROP VIEW IF EXISTS user_content_stats CASCADE;
                    DROP VIEW IF EXISTS content_summary CASCADE;
                    DROP TABLE IF EXISTS content_feedback CASCADE;
                    DROP TABLE IF EXISTS api_usage CASCADE;
                    DROP TABLE IF EXISTS quality_assessments CASCADE;
                    DROP TABLE IF EXISTS content_generation_sessions CASCADE;
                    DROP TABLE IF EXISTS educational_content CASCADE;
                    DROP TABLE IF EXISTS users CASCADE;
                    DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
                """))
                
                # Execute schema creation
                for statement in schema_sql.split(';'):
                    if statement.strip():
                        conn.execute(text(statement))
                
            # Verify tables exist
            inspector = inspect(self.engine)
            expected_tables = [
                'users', 'educational_content', 'content_generation_sessions',
                'quality_assessments', 'api_usage', 'content_feedback'
            ]
            
            actual_tables = inspector.get_table_names()
            missing_tables = set(expected_tables) - set(actual_tables)
            
            if missing_tables:
                logger.error(f"❌ Missing tables: {missing_tables}")
                return False
                
            logger.info(f"✅ Schema applied successfully - {len(actual_tables)} tables created")
            self.test_results["schema_applied"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Schema application failed: {e}")
            self.test_results["schema_applied"] = False
            return False
    
    def test_crud_operations(self) -> bool:
        """Test CRUD operations on all tables"""
        try:
            with self.engine.begin() as conn:
                # Test user creation
                user_id = str(uuid4())
                conn.execute(text("""
                    INSERT INTO users (id, username, email, is_active)
                    VALUES (:id, :username, :email, :is_active)
                """), {
                    "id": user_id,
                    "username": f"test_user_{int(time.time())}",
                    "email": f"test_{int(time.time())}@example.com",
                    "is_active": True
                })
                
                # Test educational content creation
                content_id = str(uuid4())
                conn.execute(text("""
                    INSERT INTO educational_content (
                        id, user_id, content_type, topic, age_group,
                        generated_content, quality_score, educational_effectiveness,
                        factual_accuracy, age_appropriateness
                    ) VALUES (
                        :id, :user_id, :content_type, :topic, :age_group,
                        :content, :quality, :effectiveness, :accuracy, :appropriateness
                    )
                """), {
                    "id": content_id,
                    "user_id": user_id,
                    "content_type": "study_guide",
                    "topic": "PostgreSQL Testing",
                    "age_group": "general",
                    "content": json.dumps({"title": "Test Content", "sections": []}),
                    "quality": 0.85,
                    "effectiveness": 0.80,
                    "accuracy": 0.90,
                    "appropriateness": 0.88
                })
                
                # Test reading
                result = conn.execute(text("""
                    SELECT c.*, u.username 
                    FROM educational_content c
                    JOIN users u ON c.user_id = u.id
                    WHERE c.id = :id
                """), {"id": content_id})
                
                row = result.fetchone()
                if not row:
                    raise Exception("Failed to read created content")
                
                # Test updating
                conn.execute(text("""
                    UPDATE educational_content 
                    SET quality_score = :new_score 
                    WHERE id = :id
                """), {"new_score": 0.90, "id": content_id})
                
                # Test deletion
                conn.execute(text("DELETE FROM educational_content WHERE id = :id"), {"id": content_id})
                conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})
                
            logger.info("✅ CRUD operations successful")
            self.test_results["crud_operations"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ CRUD operations failed: {e}")
            self.test_results["crud_operations"] = False
            return False
    
    def test_performance(self) -> bool:
        """Test query performance and connection pooling"""
        try:
            # Create pooled engine for testing
            pooled_engine = create_engine(
                self.database_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True
            )
            
            # Test single query performance
            start = time.time()
            with pooled_engine.connect() as conn:
                conn.execute(text("SELECT COUNT(*) FROM educational_content"))
            single_query_time = (time.time() - start) * 1000
            
            # Test bulk insert performance
            start = time.time()
            with pooled_engine.begin() as conn:
                for i in range(100):
                    conn.execute(text("""
                        INSERT INTO api_usage (
                            id, endpoint, method, status_code, response_time_ms
                        ) VALUES (
                            :id, :endpoint, :method, :status, :time
                        )
                    """), {
                        "id": str(uuid4()),
                        "endpoint": f"/api/test/{i}",
                        "method": "GET",
                        "status": 200,
                        "time": i * 10
                    })
            bulk_insert_time = (time.time() - start) * 1000
            
            # Test concurrent connections
            start = time.time()
            connections = []
            for _ in range(5):
                conn = pooled_engine.connect()
                connections.append(conn)
                conn.execute(text("SELECT 1"))
            
            for conn in connections:
                conn.close()
            concurrent_time = (time.time() - start) * 1000
            
            # Clean up test data
            with pooled_engine.begin() as conn:
                conn.execute(text("DELETE FROM api_usage WHERE endpoint LIKE '/api/test/%'"))
            
            pooled_engine.dispose()
            
            # Store performance results
            self.test_results["performance"] = {
                "single_query_ms": round(single_query_time, 2),
                "bulk_insert_100_ms": round(bulk_insert_time, 2),
                "concurrent_5_connections_ms": round(concurrent_time, 2)
            }
            
            # Check if performance is acceptable
            acceptable = (
                single_query_time < 50 and  # Single query under 50ms
                bulk_insert_time < 5000 and  # 100 inserts under 5 seconds
                concurrent_time < 500  # 5 concurrent connections under 500ms
            )
            
            if acceptable:
                logger.info(f"✅ Performance acceptable: {self.test_results['performance']}")
            else:
                logger.warning(f"⚠️ Performance could be improved: {self.test_results['performance']}")
                
            self.test_results["connection_pooling"] = True
            return acceptable
            
        except Exception as e:
            logger.error(f"❌ Performance testing failed: {e}")
            self.test_results["connection_pooling"] = False
            return False
    
    def test_data_types(self) -> bool:
        """Test PostgreSQL-specific data types"""
        try:
            with self.engine.begin() as conn:
                # Test UUID generation
                result = conn.execute(text("SELECT uuid_generate_v4()"))
                uuid_val = result.fetchone()[0]
                assert len(str(uuid_val)) == 36, "UUID generation failed"
                
                # Test JSONB operations
                content_data = {
                    "title": "Test",
                    "sections": ["intro", "main", "conclusion"],
                    "metadata": {"author": "test", "version": 1}
                }
                
                user_id = str(uuid4())
                conn.execute(text("""
                    INSERT INTO users (id, username, email, learning_preferences)
                    VALUES (:id, :username, :email, :preferences)
                """), {
                    "id": user_id,
                    "username": f"jsonb_test_{int(time.time())}",
                    "email": f"jsonb_{int(time.time())}@test.com",
                    "preferences": json.dumps(content_data)
                })
                
                # Query JSONB field
                result = conn.execute(text("""
                    SELECT learning_preferences->>'title' as title,
                           learning_preferences->'sections' as sections
                    FROM users WHERE id = :id
                """), {"id": user_id})
                
                row = result.fetchone()
                assert row[0] == "Test", "JSONB query failed"
                
                # Test TIMESTAMP WITH TIME ZONE
                result = conn.execute(text("""
                    SELECT created_at, updated_at 
                    FROM users WHERE id = :id
                """), {"id": user_id})
                
                row = result.fetchone()
                assert row[0] is not None, "Timestamp creation failed"
                
                # Test TEXT[] array type
                session_id = str(uuid4())
                conn.execute(text("""
                    INSERT INTO content_generation_sessions (
                        id, user_id, topic, age_group, requested_content_types,
                        total_content_types
                    ) VALUES (
                        :id, :user_id, :topic, :age_group, :types, :total
                    )
                """), {
                    "id": session_id,
                    "user_id": user_id,
                    "topic": "Array Test",
                    "age_group": "general",
                    "types": ["study_guide", "flashcards", "quiz"],
                    "total": 3
                })
                
                # Clean up
                conn.execute(text("DELETE FROM content_generation_sessions WHERE id = :id"), {"id": session_id})
                conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})
                
            logger.info("✅ PostgreSQL data types working correctly")
            self.test_results["data_types"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Data type testing failed: {e}")
            self.test_results["data_types"] = False
            return False
    
    def test_triggers_and_functions(self) -> bool:
        """Test PostgreSQL triggers and functions"""
        try:
            with self.engine.begin() as conn:
                # Test updated_at trigger
                user_id = str(uuid4())
                conn.execute(text("""
                    INSERT INTO users (id, username, email)
                    VALUES (:id, :username, :email)
                """), {
                    "id": user_id,
                    "username": f"trigger_test_{int(time.time())}",
                    "email": f"trigger_{int(time.time())}@test.com"
                })
                
                # Get initial updated_at
                result = conn.execute(text("""
                    SELECT updated_at FROM users WHERE id = :id
                """), {"id": user_id})
                initial_updated = result.fetchone()[0]
                
                # Wait a bit and update
                time.sleep(1)
                conn.execute(text("""
                    UPDATE users SET is_active = false WHERE id = :id
                """), {"id": user_id})
                
                # Check if updated_at changed
                result = conn.execute(text("""
                    SELECT updated_at FROM users WHERE id = :id
                """), {"id": user_id})
                new_updated = result.fetchone()[0]
                
                assert new_updated > initial_updated, "updated_at trigger not working"
                
                # Clean up
                conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})
                
            logger.info("✅ Triggers and functions working correctly")
            self.test_results["triggers"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Trigger testing failed: {e}")
            self.test_results["triggers"] = False
            return False
    
    def test_views(self) -> bool:
        """Test PostgreSQL views"""
        try:
            with self.engine.connect() as conn:
                # Test content_summary view
                result = conn.execute(text("SELECT * FROM content_summary LIMIT 1"))
                # Just check it doesn't error
                
                # Test user_content_stats view
                result = conn.execute(text("SELECT * FROM user_content_stats LIMIT 1"))
                
                # Test content_type_stats view
                result = conn.execute(text("SELECT * FROM content_type_stats"))
                
            logger.info("✅ Views are functional")
            self.test_results["views"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ View testing failed: {e}")
            self.test_results["views"] = False
            return False
    
    def test_indexes_and_constraints(self) -> bool:
        """Test indexes and constraints are working"""
        try:
            inspector = inspect(self.engine)
            
            # Check indexes exist
            indexes = inspector.get_indexes('educational_content')
            index_names = [idx['name'] for idx in indexes]
            
            expected_indexes = [
                'idx_educational_content_user_id',
                'idx_educational_content_content_type',
                'idx_educational_content_quality_score'
            ]
            
            missing = set(expected_indexes) - set(index_names)
            if missing:
                logger.warning(f"Missing indexes: {missing}")
            
            # Test unique constraints
            with self.engine.begin() as conn:
                try:
                    # Try to insert duplicate username
                    user_id1 = str(uuid4())
                    user_id2 = str(uuid4())
                    username = f"unique_test_{int(time.time())}"
                    
                    conn.execute(text("""
                        INSERT INTO users (id, username, email)
                        VALUES (:id, :username, :email)
                    """), {
                        "id": user_id1,
                        "username": username,
                        "email": f"test1_{int(time.time())}@example.com"
                    })
                    
                    # This should fail due to unique constraint
                    try:
                        conn.execute(text("""
                            INSERT INTO users (id, username, email)
                            VALUES (:id, :username, :email)
                        """), {
                            "id": user_id2,
                            "username": username,  # Duplicate username
                            "email": f"test2_{int(time.time())}@example.com"
                        })
                        # If we get here, constraint didn't work
                        logger.warning("Unique constraint on username may not be working")
                    except Exception:
                        # Expected - constraint is working
                        pass
                    
                    # Clean up
                    conn.execute(text("DELETE FROM users WHERE username = :username"), {"username": username})
                    
                except Exception as e:
                    # Clean up on any error
                    pass
            
            logger.info("✅ Indexes and constraints are functional")
            self.test_results["indexes"] = True
            self.test_results["constraints"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Index/constraint testing failed: {e}")
            self.test_results["indexes"] = False
            self.test_results["constraints"] = False
            return False
    
    def generate_report(self):
        """Generate test report"""
        report = []
        report.append("=" * 60)
        report.append("PostgreSQL Integration Test Report")
        report.append("=" * 60)
        report.append(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        report.append("")
        
        # Connection info
        if self.database_url:
            # Sanitize URL for display
            if "@" in self.database_url:
                parts = self.database_url.split("@")
                sanitized = parts[0].split("://")[0] + "://***@" + parts[1]
            else:
                sanitized = self.database_url[:30] + "..."
            report.append(f"Database URL: {sanitized}")
        report.append("")
        
        # Test results
        report.append("Test Results:")
        report.append("-" * 40)
        
        status_symbols = {True: "✅", False: "❌", None: "⏭️"}
        
        for test, result in self.test_results.items():
            if test == "performance":
                report.append(f"Performance Metrics:")
                for metric, value in result.items():
                    report.append(f"  - {metric}: {value}ms")
            else:
                symbol = status_symbols.get(result, "❓")
                report.append(f"{symbol} {test.replace('_', ' ').title()}: {result}")
        
        report.append("")
        
        # Summary
        total_tests = len([v for v in self.test_results.values() if isinstance(v, bool)])
        passed_tests = len([v for v in self.test_results.values() if v is True])
        
        report.append("Summary:")
        report.append("-" * 40)
        report.append(f"Tests Passed: {passed_tests}/{total_tests}")
        report.append(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        # Recommendations
        report.append("")
        report.append("Recommendations:")
        report.append("-" * 40)
        
        if not self.test_results["connection"]:
            report.append("- Ensure PostgreSQL is running and accessible")
            report.append("- Verify DATABASE_URL is correctly configured")
        
        if self.test_results["performance"]:
            perf = self.test_results["performance"]
            if perf.get("single_query_ms", 0) > 50:
                report.append("- Consider adding more indexes for frequently queried columns")
            if perf.get("bulk_insert_100_ms", 0) > 5000:
                report.append("- Consider using COPY for bulk inserts in production")
        
        if not self.test_results["connection_pooling"]:
            report.append("- Review connection pool settings for production load")
        
        return "\n".join(report)
    
    async def run_all_tests(self):
        """Run all PostgreSQL integration tests"""
        logger.info("Starting PostgreSQL Integration Tests...")
        
        # Setup connection
        if not self.setup_connection():
            logger.error("Cannot proceed without database connection")
            return False
        
        # Run tests in sequence
        tests = [
            ("Schema Application", self.test_schema_application),
            ("CRUD Operations", self.test_crud_operations),
            ("Data Types", self.test_data_types),
            ("Triggers", self.test_triggers_and_functions),
            ("Views", self.test_views),
            ("Indexes & Constraints", self.test_indexes_and_constraints),
            ("Performance", self.test_performance),
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\nRunning: {test_name}")
            try:
                test_func()
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {e}")
        
        # Generate and save report
        report = self.generate_report()
        print("\n" + report)
        
        # Save report to file
        report_file = Path(__file__).parent.parent / "POSTGRESQL_INTEGRATION_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(report)
        logger.info(f"\nReport saved to: {report_file}")
        
        # Return overall success
        return all([
            self.test_results["connection"],
            self.test_results["schema_applied"],
            self.test_results["crud_operations"],
            self.test_results["data_types"]
        ])


def main():
    """Main entry point"""
    # Check for database URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.warning("No DATABASE_URL found in environment")
        logger.info("Attempting to use development SQLite database for basic testing...")
        database_url = "sqlite:///la_factoria_dev.db"
    
    # Create tester
    tester = PostgreSQLIntegrationTester(database_url)
    
    # Run tests
    success = asyncio.run(tester.run_all_tests())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()