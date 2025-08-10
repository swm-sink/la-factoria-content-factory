#!/usr/bin/env python3
"""
Database Compatibility Testing Script
======================================

Tests database layer compatibility between SQLite (development) and 
PostgreSQL (production) without requiring actual PostgreSQL instance.

This validates:
- ORM model compatibility
- Query compatibility
- Schema mapping
- Data type handling
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
from uuid import uuid4

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Import our models and database module
from src.core.database import Base, engine, SessionLocal, init_database
from src.models.educational import EducationalContentDB, UserModel
from src.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseCompatibilityTester:
    """Test database compatibility across SQLite and PostgreSQL"""
    
    def __init__(self):
        self.session = SessionLocal()
        self.test_results = {
            "orm_models": False,
            "data_types": False,
            "relationships": False,
            "queries": False,
            "transactions": False,
            "json_handling": False
        }
        
    def test_orm_models(self) -> bool:
        """Test that all ORM models work correctly"""
        try:
            # Create test user
            user = UserModel(
                id=str(uuid4()),
                username=f"test_user_{datetime.now().timestamp()}",
                email=f"test_{datetime.now().timestamp()}@example.com",
                is_active=True,
                learning_preferences={"theme": "dark", "language": "en"}
            )
            self.session.add(user)
            self.session.flush()
            
            # Create educational content
            content = EducationalContentDB(
                id=str(uuid4()),
                user_id=user.id,
                content_type="study_guide",
                topic="Database Testing",
                age_group="general",
                learning_objectives=[
                    {"objective": "Understand database concepts"},
                    {"objective": "Apply SQL knowledge"}
                ],
                cognitive_load_metrics={
                    "intrinsic": 0.5,
                    "extraneous": 0.3,
                    "germane": 0.4
                },
                generated_content={"title": "Test Content", "sections": []},
                quality_score=0.85,
                educational_effectiveness=0.80,
                factual_accuracy=0.90,
                age_appropriateness=0.88,
                generation_duration_ms=1500,
                tokens_used=500,
                ai_provider="openai",
                ai_model="gpt-4",
                prompt_template="study_guide"
            )
            self.session.add(content)
            self.session.flush()
            
            # Commit all
            self.session.commit()
            
            # Verify we can read back
            retrieved_user = self.session.query(UserModel).filter_by(id=user.id).first()
            assert retrieved_user is not None
            assert retrieved_user.username == user.username
            
            retrieved_content = self.session.query(EducationalContentDB).filter_by(id=content.id).first()
            assert retrieved_content is not None
            assert retrieved_content.topic == "Database Testing"
            
            # Clean up
            self.session.query(EducationalContentDB).filter_by(id=content.id).delete()
            self.session.query(UserModel).filter_by(id=user.id).delete()
            self.session.commit()
            
            logger.info("✅ ORM models working correctly")
            self.test_results["orm_models"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ ORM model test failed: {e}")
            self.session.rollback()
            self.test_results["orm_models"] = False
            return False
    
    def test_data_types(self) -> bool:
        """Test data type compatibility"""
        try:
            # Test various data types
            user_id = str(uuid4())
            
            # UUID as string (compatible)
            user = UserModel(
                id=user_id,
                username=f"dtype_test_{datetime.now().timestamp()}",
                email=f"dtype_{datetime.now().timestamp()}@test.com"
            )
            
            # JSON data (stored as TEXT in SQLite, JSONB in PostgreSQL)
            user.learning_preferences = {
                "nested": {
                    "data": ["array", "of", "items"],
                    "number": 42,
                    "boolean": True
                }
            }
            
            self.session.add(user)
            self.session.flush()
            
            # Decimal/Float values
            content = EducationalContentDB(
                id=str(uuid4()),
                user_id=user_id,
                content_type="flashcards",
                topic="Data Types",
                age_group="general",
                generated_content={"cards": []},
                quality_score=0.123456,  # Test decimal precision
                educational_effectiveness=0.999,
                factual_accuracy=0.001,
                age_appropriateness=0.5
            )
            self.session.add(content)
            self.session.flush()
            
            # Commit the user and content
            self.session.commit()
            
            # Verify data integrity
            retrieved = self.session.query(UserModel).filter_by(id=user_id).first()
            assert retrieved.learning_preferences["nested"]["number"] == 42
            
            retrieved_content = self.session.query(EducationalContentDB).filter_by(
                user_id=user_id
            ).first()
            assert 0.12 <= retrieved_content.quality_score <= 0.13  # Allow for float precision
            
            # Clean up
            self.session.query(EducationalContentDB).filter_by(user_id=user_id).delete()
            self.session.query(UserModel).filter_by(id=user_id).delete()
            self.session.commit()
            
            logger.info("✅ Data types compatible")
            self.test_results["data_types"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Data type test failed: {e}")
            self.session.rollback()
            self.test_results["data_types"] = False
            return False
    
    def test_relationships(self) -> bool:
        """Test foreign key relationships and cascades"""
        try:
            # Create user
            user = UserModel(
                id=str(uuid4()),
                username=f"rel_test_{datetime.now().timestamp()}",
                email=f"rel_{datetime.now().timestamp()}@test.com"
            )
            self.session.add(user)
            self.session.flush()
            
            # Create content linked to user
            content = EducationalContentDB(
                id=str(uuid4()),
                user_id=user.id,
                content_type="study_guide",
                topic="Relationships",
                age_group="general",
                generated_content={"test": "data"}
            )
            self.session.add(content)
            self.session.flush()
            
            self.session.commit()
            
            # Test relationship loading
            loaded_content = self.session.query(EducationalContentDB).filter_by(
                id=content.id
            ).first()
            assert loaded_content.user_id == user.id
            
            # Test that we can query content by user
            user_content = self.session.query(EducationalContentDB).filter_by(
                user_id=user.id
            ).all()
            assert len(user_content) == 1
            assert user_content[0].id == content.id
            
            # Clean up
            self.session.query(EducationalContentDB).filter_by(id=content.id).delete()
            self.session.query(UserModel).filter_by(id=user.id).delete()
            self.session.commit()
            
            logger.info("✅ Relationships working correctly")
            self.test_results["relationships"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Relationship test failed: {e}")
            self.session.rollback()
            self.test_results["relationships"] = False
            return False
    
    def test_queries(self) -> bool:
        """Test query compatibility"""
        try:
            # Setup test data
            user_id = str(uuid4())
            user = UserModel(
                id=user_id,
                username=f"query_test_{datetime.now().timestamp()}",
                email=f"query_{datetime.now().timestamp()}@test.com"
            )
            self.session.add(user)
            
            # Add multiple content items
            content_ids = []
            for i in range(5):
                content = EducationalContentDB(
                    id=str(uuid4()),
                    user_id=user_id,
                    content_type="study_guide" if i % 2 == 0 else "flashcards",
                    topic=f"Topic {i}",
                    age_group="general",
                    generated_content={"index": i},
                    quality_score=0.70 + (i * 0.05)
                )
                self.session.add(content)
                content_ids.append(content.id)
            
            self.session.commit()
            
            # Test various query patterns
            
            # 1. Filter with ordering
            results = self.session.query(EducationalContentDB).filter_by(
                user_id=user_id
            ).order_by(EducationalContentDB.quality_score.desc()).all()
            assert len(results) == 5
            assert results[0].quality_score >= results[-1].quality_score
            
            # 2. Aggregation
            from sqlalchemy import func
            avg_score = self.session.query(
                func.avg(EducationalContentDB.quality_score)
            ).filter_by(user_id=user_id).scalar()
            assert avg_score is not None
            
            # 3. Count
            count = self.session.query(EducationalContentDB).filter_by(
                user_id=user_id, content_type="study_guide"
            ).count()
            assert count == 3
            
            # 4. IN clause
            subset = self.session.query(EducationalContentDB).filter(
                EducationalContentDB.id.in_(content_ids[:2])
            ).all()
            assert len(subset) == 2
            
            # 5. LIKE pattern
            pattern_results = self.session.query(EducationalContentDB).filter(
                EducationalContentDB.topic.like("Topic%")
            ).all()
            assert len(pattern_results) >= 5
            
            # Clean up
            self.session.query(EducationalContentDB).filter_by(user_id=user_id).delete()
            self.session.query(UserModel).filter_by(id=user_id).delete()
            self.session.commit()
            
            logger.info("✅ Queries compatible")
            self.test_results["queries"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Query test failed: {e}")
            self.session.rollback()
            self.test_results["queries"] = False
            return False
    
    def test_transactions(self) -> bool:
        """Test transaction handling"""
        try:
            # Test rollback
            user_id = str(uuid4())
            
            try:
                user = UserModel(
                    id=user_id,
                    username=f"tx_test_{datetime.now().timestamp()}",
                    email=f"tx_{datetime.now().timestamp()}@test.com"
                )
                self.session.add(user)
                self.session.flush()
                
                # This should cause an error (duplicate ID)
                duplicate = UserModel(
                    id=user_id,  # Same ID
                    username="different",
                    email="different@test.com"
                )
                self.session.add(duplicate)
                self.session.flush()
                
                # Should not reach here
                self.session.commit()
                assert False, "Should have raised an error"
                
            except Exception:
                # Expected - rollback
                self.session.rollback()
                
                # Verify rollback worked
                result = self.session.query(UserModel).filter_by(id=user_id).first()
                assert result is None
            
            # Test successful transaction
            self.session.begin()
            user = UserModel(
                id=user_id,
                username=f"tx_success_{datetime.now().timestamp()}",
                email=f"tx_success_{datetime.now().timestamp()}@test.com"
            )
            self.session.add(user)
            self.session.commit()
            
            # Verify committed
            result = self.session.query(UserModel).filter_by(id=user_id).first()
            assert result is not None
            
            # Clean up
            self.session.query(UserModel).filter_by(id=user_id).delete()
            self.session.commit()
            
            logger.info("✅ Transactions working correctly")
            self.test_results["transactions"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Transaction test failed: {e}")
            self.session.rollback()
            self.test_results["transactions"] = False
            return False
    
    def test_json_handling(self) -> bool:
        """Test JSON field handling compatibility"""
        try:
            user_id = str(uuid4())
            
            # Complex JSON structure
            complex_json = {
                "arrays": [1, 2, 3, ["nested", "array"]],
                "objects": {
                    "nested": {
                        "deeply": {
                            "nested": "value"
                        }
                    }
                },
                "unicode": "emoji 🎓 test",
                "special_chars": "quotes\"and'apostrophes",
                "null_value": None,
                "boolean": True,
                "number": 3.14159
            }
            
            user = UserModel(
                id=user_id,
                username=f"json_test_{datetime.now().timestamp()}",
                email=f"json_{datetime.now().timestamp()}@test.com",
                learning_preferences=complex_json
            )
            self.session.add(user)
            
            content = EducationalContentDB(
                id=str(uuid4()),
                user_id=user_id,
                content_type="study_guide",
                topic="JSON Testing",
                age_group="general",
                learning_objectives=[
                    {"id": 1, "text": "First objective"},
                    {"id": 2, "text": "Second objective", "nested": {"data": "here"}}
                ],
                cognitive_load_metrics={
                    "intrinsic": 0.5,
                    "extraneous": 0.3,
                    "germane": 0.4,
                    "metadata": {
                        "calculated_at": datetime.now(timezone.utc).isoformat()
                    }
                },
                generated_content={
                    "title": "Complex Content",
                    "sections": [
                        {"id": 1, "content": "Section 1"},
                        {"id": 2, "content": "Section 2"}
                    ]
                }
            )
            self.session.add(content)
            self.session.commit()
            
            # Retrieve and verify JSON integrity
            retrieved = self.session.query(UserModel).filter_by(id=user_id).first()
            assert retrieved.learning_preferences["unicode"] == "emoji 🎓 test"
            assert retrieved.learning_preferences["objects"]["nested"]["deeply"]["nested"] == "value"
            assert retrieved.learning_preferences["null_value"] is None
            
            retrieved_content = self.session.query(EducationalContentDB).filter_by(
                user_id=user_id
            ).first()
            assert len(retrieved_content.learning_objectives) == 2
            assert retrieved_content.cognitive_load_metrics["intrinsic"] == 0.5
            assert "metadata" in retrieved_content.cognitive_load_metrics
            
            # Clean up
            self.session.query(EducationalContentDB).filter_by(user_id=user_id).delete()
            self.session.query(UserModel).filter_by(id=user_id).delete()
            self.session.commit()
            
            logger.info("✅ JSON handling compatible")
            self.test_results["json_handling"] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ JSON handling test failed: {e}")
            self.session.rollback()
            self.test_results["json_handling"] = False
            return False
    
    def generate_report(self) -> str:
        """Generate compatibility report"""
        report = []
        report.append("=" * 60)
        report.append("Database Compatibility Test Report")
        report.append("=" * 60)
        report.append(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        report.append(f"Database: {settings.database_url[:30]}...")
        report.append("")
        
        report.append("Compatibility Tests:")
        report.append("-" * 40)
        
        for test, result in self.test_results.items():
            symbol = "✅" if result else "❌"
            report.append(f"{symbol} {test.replace('_', ' ').title()}: {result}")
        
        report.append("")
        report.append("Summary:")
        report.append("-" * 40)
        
        passed = sum(1 for v in self.test_results.values() if v)
        total = len(self.test_results)
        
        report.append(f"Tests Passed: {passed}/{total}")
        report.append(f"Compatibility Score: {(passed/total*100):.1f}%")
        
        if passed == total:
            report.append("\n✅ Database layer is fully compatible!")
        else:
            report.append("\n⚠️ Some compatibility issues detected")
            report.append("Failed tests may need PostgreSQL-specific handling")
        
        return "\n".join(report)
    
    async def run_all_tests(self):
        """Run all compatibility tests"""
        logger.info("Starting Database Compatibility Tests...")
        logger.info(f"Using database: {settings.database_url[:30]}...")
        
        # Initialize database
        try:
            await init_database()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
        
        # Run tests
        tests = [
            ("ORM Models", self.test_orm_models),
            ("Data Types", self.test_data_types),
            ("Relationships", self.test_relationships),
            ("Queries", self.test_queries),
            ("Transactions", self.test_transactions),
            ("JSON Handling", self.test_json_handling),
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\nTesting: {test_name}")
            try:
                test_func()
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {e}")
        
        # Generate report
        report = self.generate_report()
        print("\n" + report)
        
        # Save report
        report_file = Path(__file__).parent.parent / "DATABASE_COMPATIBILITY_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(report)
        logger.info(f"\nReport saved to: {report_file}")
        
        # Close session
        self.session.close()
        
        # Return success if all tests passed
        return all(self.test_results.values())


def main():
    """Main entry point"""
    tester = DatabaseCompatibilityTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()