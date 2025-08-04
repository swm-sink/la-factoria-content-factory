"""
Content Request and Response Models for La Factoria API
Following FastAPI and Pydantic best practices
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

from .educational import (
    LaFactoriaContentType,
    LearningLevel,
    LearningObjectiveModel,
    QualityMetrics,
    EducationalContentMetadata
)

class ContentRequest(BaseModel):
    """Request model for educational content generation"""
    topic: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="The educational topic or subject to generate content for",
        example="Introduction to Python Programming"
    )
    age_group: LearningLevel = Field(
        default=LearningLevel.GENERAL,
        description="Target learning level for content generation"
    )
    learning_objectives: Optional[List[LearningObjectiveModel]] = Field(
        default=None,
        description="Specific learning objectives to incorporate into the content"
    )
    additional_requirements: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Additional requirements or constraints for content generation"
    )

    class Config:
        schema_extra = {
            "example": {
                "topic": "Introduction to Python Programming",
                "age_group": "high_school",
                "learning_objectives": [
                    {
                        "cognitive_level": "understanding",
                        "subject_area": "Computer Science",
                        "specific_skill": "Python syntax comprehension",
                        "measurable_outcome": "Student can explain basic Python syntax elements",
                        "difficulty_level": 6
                    }
                ],
                "additional_requirements": "Include practical coding examples and exercises"
            }
        }

class ContentResponse(BaseModel):
    """Response model for generated educational content"""
    id: str = Field(..., description="Unique identifier for the generated content")
    content_type: LaFactoriaContentType = Field(..., description="Type of educational content generated")
    topic: str = Field(..., description="The educational topic that was processed")
    age_group: LearningLevel = Field(..., description="Target learning level")
    generated_content: Dict[str, Any] = Field(..., description="The generated educational content structure")
    quality_metrics: Optional[QualityMetrics] = Field(default=None, description="Quality assessment metrics")
    metadata: Optional[EducationalContentMetadata] = Field(default=None, description="Generation metadata and statistics")
    created_at: datetime = Field(..., description="Timestamp when content was generated")

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "content_type": "study_guide",
                "topic": "Introduction to Python Programming",
                "age_group": "high_school",
                "generated_content": {
                    "title": "Python Programming Study Guide",
                    "overview": "Comprehensive guide to Python basics",
                    "sections": [
                        {
                            "title": "Variables and Data Types",
                            "content": "Python variables are containers for storing data...",
                            "examples": ["x = 5", "name = 'Alice'"],
                            "exercises": ["Create a variable for your age"]
                        }
                    ]
                },
                "quality_metrics": {
                    "overall_quality_score": 0.85,
                    "educational_value": 0.88,
                    "factual_accuracy": 0.92,
                    "age_appropriateness": 0.84,
                    "structural_quality": 0.87,
                    "engagement_level": 0.79
                },
                "metadata": {
                    "generation_duration_ms": 2500,
                    "tokens_used": 1200,
                    "prompt_template": "study_guide",
                    "ai_provider": "openai"
                },
                "created_at": "2025-01-03T10:30:00Z"
            }
        }

class ContentTypeInfo(BaseModel):
    """Information about a specific content type"""
    name: str = Field(..., description="Content type identifier")
    display_name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Description of the content type")
    typical_use_cases: List[str] = Field(..., description="Common use cases for this content type")
    estimated_generation_time: str = Field(..., description="Estimated time to generate content")

class ContentTypesResponse(BaseModel):
    """Response model for available content types"""
    content_types: List[ContentTypeInfo] = Field(..., description="List of available educational content types")
    total_count: int = Field(..., description="Total number of supported content types")

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Detailed error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Application version")
    services: Dict[str, str] = Field(default_factory=dict, description="Status of dependent services")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Content type configurations
CONTENT_TYPE_CONFIGS = {
    LaFactoriaContentType.MASTER_CONTENT_OUTLINE: ContentTypeInfo(
        name="master_content_outline",
        display_name="Master Content Outline",
        description="Foundation structure with learning objectives and scaffolding for other content types",
        typical_use_cases=[
            "Course planning and organization",
            "Curriculum development",
            "Learning pathway design",
            "Educational content mapping"
        ],
        estimated_generation_time="30-45 seconds"
    ),
    LaFactoriaContentType.PODCAST_SCRIPT: ContentTypeInfo(
        name="podcast_script",
        display_name="Podcast Script",
        description="Conversational audio content with speaker notes and timing guidance",
        typical_use_cases=[
            "Educational podcasts",
            "Audio learning materials",
            "Spoken presentations",
            "Voice-over scripts"
        ],
        estimated_generation_time="45-60 seconds"
    ),
    LaFactoriaContentType.STUDY_GUIDE: ContentTypeInfo(
        name="study_guide",
        display_name="Study Guide",
        description="Comprehensive educational material with key concepts, examples, and exercises",
        typical_use_cases=[
            "Exam preparation",
            "Self-study materials",
            "Course review guides",
            "Supplemental learning resources"
        ],
        estimated_generation_time="60-90 seconds"
    ),
    LaFactoriaContentType.ONE_PAGER_SUMMARY: ContentTypeInfo(
        name="one_pager_summary",
        display_name="One-Pager Summary",
        description="Concise overview with essential takeaways and key information",
        typical_use_cases=[
            "Quick reference materials",
            "Executive summaries",
            "Concept overviews",
            "Cheat sheets"
        ],
        estimated_generation_time="20-30 seconds"
    ),
    LaFactoriaContentType.DETAILED_READING_MATERIAL: ContentTypeInfo(
        name="detailed_reading_material",
        display_name="Detailed Reading Material",
        description="In-depth content with examples, exercises, and comprehensive explanations",
        typical_use_cases=[
            "Textbook chapters",
            "Research materials",
            "Deep-dive learning content",
            "Academic resources"
        ],
        estimated_generation_time="90-120 seconds"
    ),
    LaFactoriaContentType.FAQ_COLLECTION: ContentTypeInfo(
        name="faq_collection",
        display_name="FAQ Collection",
        description="Question-answer pairs covering common topics and addressing misconceptions",
        typical_use_cases=[
            "Student support materials",
            "Common questions database",
            "Help documentation",
            "Learning troubleshooting"
        ],
        estimated_generation_time="40-60 seconds"
    ),
    LaFactoriaContentType.FLASHCARDS: ContentTypeInfo(
        name="flashcards",
        display_name="Flashcards",
        description="Term-definition pairs optimized for memorization and spaced repetition",
        typical_use_cases=[
            "Vocabulary learning",
            "Fact memorization",
            "Quick recall practice",
            "Spaced repetition systems"
        ],
        estimated_generation_time="30-45 seconds"
    ),
    LaFactoriaContentType.READING_GUIDE_QUESTIONS: ContentTypeInfo(
        name="reading_guide_questions",
        display_name="Reading Guide Questions",
        description="Discussion questions for comprehension and critical thinking development",
        typical_use_cases=[
            "Book clubs and discussions",
            "Comprehension assessment",
            "Critical thinking exercises",
            "Group learning activities"
        ],
        estimated_generation_time="35-50 seconds"
    )
}
