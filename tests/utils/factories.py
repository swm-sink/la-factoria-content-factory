"""
Test data factories for La Factoria test suite
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from faker import Faker

fake = Faker()


class ContentRequestFactory:
    """Factory for creating content generation requests"""
    
    CONTENT_TYPES = [
        "master_content_outline",
        "study_guide", 
        "one_pager_summary",
        "detailed_reading_material",
        "faq_collection",
        "flashcards",
        "podcast_script",
        "reading_guide_questions"
    ]
    
    DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced", "expert"]
    
    TOPICS = [
        "Python Programming",
        "Machine Learning",
        "Data Science",
        "Web Development",
        "Cloud Computing",
        "Cybersecurity",
        "Database Design",
        "Software Architecture",
        "DevOps",
        "Artificial Intelligence"
    ]
    
    @classmethod
    def create(cls, **overrides) -> Dict[str, Any]:
        """Create a content request with optional overrides"""
        request = {
            "topic": random.choice(cls.TOPICS),
            "content_type": random.choice(cls.CONTENT_TYPES),
            "difficulty_level": random.choice(cls.DIFFICULTY_LEVELS),
            "learning_objectives": cls._generate_learning_objectives(),
            "target_audience": cls._generate_target_audience(),
            "additional_requirements": fake.sentence()
        }
        request.update(overrides)
        return request
    
    @classmethod
    def create_batch(cls, count: int = 5) -> List[Dict[str, Any]]:
        """Create multiple content requests"""
        return [cls.create() for _ in range(count)]
    
    @classmethod
    def _generate_learning_objectives(cls) -> List[str]:
        """Generate random learning objectives"""
        objectives = [
            f"Understand {fake.word()} concepts",
            f"Master {fake.word()} techniques",
            f"Apply {fake.word()} in practice",
            f"Analyze {fake.word()} patterns",
            f"Evaluate {fake.word()} solutions"
        ]
        return random.sample(objectives, k=random.randint(2, 4))
    
    @classmethod
    def _generate_target_audience(cls) -> str:
        """Generate random target audience"""
        audiences = [
            "College students",
            "Professional developers",
            "Data scientists",
            "Business analysts",
            "Technical managers",
            "Graduate students",
            "Bootcamp participants"
        ]
        return random.choice(audiences)


class UserFactory:
    """Factory for creating test users"""
    
    @classmethod
    def create(cls, **overrides) -> Dict[str, Any]:
        """Create a user with optional overrides"""
        user = {
            "id": str(uuid.uuid4()),
            "email": fake.email(),
            "api_key": cls._generate_api_key(),
            "created_at": datetime.utcnow(),
            "is_active": True,
            "is_admin": False,
            "usage_count": random.randint(0, 100),
            "last_active": datetime.utcnow()
        }
        user.update(overrides)
        return user
    
    @classmethod
    def create_admin(cls) -> Dict[str, Any]:
        """Create an admin user"""
        return cls.create(is_admin=True, api_key="admin_" + cls._generate_api_key())
    
    @classmethod
    def _generate_api_key(cls) -> str:
        """Generate a valid API key"""
        return f"key_{uuid.uuid4().hex}"


class EducationalContentFactory:
    """Factory for creating educational content"""
    
    @classmethod
    def create(cls, content_type: str = "study_guide", **overrides) -> Dict[str, Any]:
        """Create educational content with optional overrides"""
        content = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "content_type": content_type,
            "topic": random.choice(ContentRequestFactory.TOPICS),
            "difficulty_level": random.choice(ContentRequestFactory.DIFFICULTY_LEVELS),
            "content": cls._generate_content_by_type(content_type),
            "metadata": cls._generate_metadata(),
            "quality_score": round(random.uniform(0.7, 1.0), 2),
            "created_at": datetime.utcnow(),
            "processing_time": round(random.uniform(0.5, 5.0), 2)
        }
        content.update(overrides)
        return content
    
    @classmethod
    def _generate_content_by_type(cls, content_type: str) -> Dict[str, Any]:
        """Generate content structure based on type"""
        if content_type == "study_guide":
            return {
                "title": fake.sentence(),
                "introduction": fake.paragraph(),
                "sections": [
                    {"title": fake.sentence(), "content": fake.paragraph()}
                    for _ in range(random.randint(3, 6))
                ],
                "summary": fake.paragraph(),
                "review_questions": [fake.sentence() + "?" for _ in range(5)]
            }
        elif content_type == "flashcards":
            return {
                "cards": [
                    {"front": fake.sentence() + "?", "back": fake.sentence()}
                    for _ in range(random.randint(10, 20))
                ]
            }
        elif content_type == "faq_collection":
            return {
                "questions": [
                    {"question": fake.sentence() + "?", "answer": fake.paragraph()}
                    for _ in range(random.randint(5, 10))
                ]
            }
        else:
            return {
                "title": fake.sentence(),
                "content": fake.text(),
                "sections": [fake.sentence() for _ in range(random.randint(3, 8))]
            }
    
    @classmethod
    def _generate_metadata(cls) -> Dict[str, Any]:
        """Generate content metadata"""
        return {
            "word_count": random.randint(500, 5000),
            "reading_time": f"{random.randint(5, 30)} minutes",
            "difficulty_score": round(random.uniform(0.1, 1.0), 2),
            "keywords": [fake.word() for _ in range(random.randint(3, 8))],
            "language": "en",
            "format_version": "2.0"
        }


class QualityMetricsFactory:
    """Factory for creating quality assessment metrics"""
    
    @classmethod
    def create(cls, **overrides) -> Dict[str, Any]:
        """Create quality metrics with optional overrides"""
        metrics = {
            "clarity_score": round(random.uniform(0.6, 1.0), 2),
            "completeness_score": round(random.uniform(0.6, 1.0), 2),
            "accuracy_score": round(random.uniform(0.7, 1.0), 2),
            "relevance_score": round(random.uniform(0.7, 1.0), 2),
            "engagement_score": round(random.uniform(0.5, 1.0), 2),
            "overall_score": round(random.uniform(0.65, 0.95), 2),
            "feedback": cls._generate_feedback(),
            "suggestions": cls._generate_suggestions()
        }
        metrics.update(overrides)
        return metrics
    
    @classmethod
    def _generate_feedback(cls) -> List[str]:
        """Generate quality feedback"""
        feedback_options = [
            "Content is well-structured and clear",
            "Good use of examples",
            "Could benefit from more visual aids",
            "Excellent coverage of the topic",
            "Consider adding more practice exercises",
            "Strong theoretical foundation"
        ]
        return random.sample(feedback_options, k=random.randint(2, 4))
    
    @classmethod
    def _generate_suggestions(cls) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = [
            "Add more real-world examples",
            "Include a glossary of terms",
            "Provide additional resources",
            "Add interactive elements",
            "Include self-assessment questions",
            "Add visual diagrams"
        ]
        return random.sample(suggestions, k=random.randint(1, 3))


class APIResponseFactory:
    """Factory for creating API responses"""
    
    @classmethod
    def create_success(cls, data: Any = None, **overrides) -> Dict[str, Any]:
        """Create a successful API response"""
        response = {
            "status": "success",
            "data": data or {"message": "Operation completed successfully"},
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": str(uuid.uuid4())
        }
        response.update(overrides)
        return response
    
    @classmethod
    def create_error(cls, error_message: str = None, status_code: int = 400) -> Dict[str, Any]:
        """Create an error API response"""
        return {
            "status": "error",
            "error": {
                "message": error_message or fake.sentence(),
                "code": status_code,
                "details": fake.paragraph()
            },
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": str(uuid.uuid4())
        }
    
    @classmethod
    def create_validation_error(cls, field: str = "input") -> Dict[str, Any]:
        """Create a validation error response"""
        return cls.create_error(
            error_message=f"Validation failed for field: {field}",
            status_code=422
        )