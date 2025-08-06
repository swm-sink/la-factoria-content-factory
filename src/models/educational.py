"""
Educational Data Models for La Factoria
Generated from context/educational-content-assessment.md patterns
Following learning science and cognitive load theory principles
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid

# Educational content types supported by La Factoria
class LaFactoriaContentType(str, Enum):
    """8 educational content types supported by La Factoria platform"""
    MASTER_CONTENT_OUTLINE = "master_content_outline"
    PODCAST_SCRIPT = "podcast_script"
    STUDY_GUIDE = "study_guide"
    ONE_PAGER_SUMMARY = "one_pager_summary"
    DETAILED_READING_MATERIAL = "detailed_reading_material"
    FAQ_COLLECTION = "faq_collection"
    FLASHCARDS = "flashcards"
    READING_GUIDE_QUESTIONS = "reading_guide_questions"

# Learning levels for age-appropriate content generation
class LearningLevel(str, Enum):
    """Educational levels for age-appropriate content generation"""
    ELEMENTARY = "elementary"
    MIDDLE_SCHOOL = "middle_school"
    HIGH_SCHOOL = "high_school"
    COLLEGE = "college"
    ADULT_LEARNING = "adult_learning"
    GENERAL = "general"

# Bloom's Taxonomy cognitive levels for learning objectives
class CognitiveLevel(str, Enum):
    """Bloom's taxonomy cognitive levels for educational content"""
    REMEMBERING = "remembering"      # Recall facts and basic concepts
    UNDERSTANDING = "understanding"  # Explain ideas and concepts
    APPLYING = "applying"           # Use information in new situations
    ANALYZING = "analyzing"         # Draw connections among ideas
    EVALUATING = "evaluating"       # Justify a stand or decision
    CREATING = "creating"           # Produce new or original work

@dataclass
class LearningObjective:
    """
    Learning objective following educational standards
    Generated from educational-content-assessment.md lines 6-40
    """
    cognitive_level: CognitiveLevel  # Bloom's taxonomy level
    subject_area: str               # Domain of knowledge (e.g., "Mathematics", "Science")
    specific_skill: str             # Specific skill to be developed
    measurable_outcome: str         # How success will be measured
    difficulty_level: int = 5       # 1-10 scale

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "cognitive_level": self.cognitive_level.value,
            "subject_area": self.subject_area,
            "specific_skill": self.specific_skill,
            "measurable_outcome": self.measurable_outcome,
            "difficulty_level": self.difficulty_level
        }

@dataclass
class CognitiveLoadMetrics:
    """
    Cognitive load assessment following Cognitive Load Theory
    Generated from educational-content-assessment.md
    """
    intrinsic_load: float = 0.0      # Content complexity (0-1)
    extraneous_load: float = 0.0     # Presentation complexity (0-1)
    germane_load: float = 0.0        # Learning effort required (0-1)
    total_cognitive_load: float = 0.0  # Sum of all loads

    def __post_init__(self):
        """Calculate total cognitive load"""
        self.total_cognitive_load = self.intrinsic_load + self.extraneous_load + self.germane_load

    def is_appropriate_for_level(self, learning_level: LearningLevel) -> bool:
        """Check if cognitive load is appropriate for target learning level"""
        thresholds = {
            LearningLevel.ELEMENTARY: 1.5,
            LearningLevel.MIDDLE_SCHOOL: 2.0,
            LearningLevel.HIGH_SCHOOL: 2.5,
            LearningLevel.COLLEGE: 3.0,
            LearningLevel.ADULT_LEARNING: 2.8,
            LearningLevel.GENERAL: 2.3
        }
        return self.total_cognitive_load <= thresholds.get(learning_level, 2.3)

# Pydantic models for API requests and responses
class LearningObjectiveModel(BaseModel):
    """Pydantic model for learning objective API requests"""
    cognitive_level: CognitiveLevel
    subject_area: str = Field(..., min_length=1, max_length=100)
    specific_skill: str = Field(..., min_length=1, max_length=200)
    measurable_outcome: str = Field(..., min_length=1, max_length=300)
    difficulty_level: int = Field(default=5, ge=1, le=10)

    def to_learning_objective(self) -> LearningObjective:
        """Convert to dataclass"""
        return LearningObjective(
            cognitive_level=self.cognitive_level,
            subject_area=self.subject_area,
            specific_skill=self.specific_skill,
            measurable_outcome=self.measurable_outcome,
            difficulty_level=self.difficulty_level
        )

class CognitiveLoadMetricsModel(BaseModel):
    """Pydantic model for cognitive load metrics"""
    intrinsic_load: float = Field(ge=0.0, le=1.0)
    extraneous_load: float = Field(ge=0.0, le=1.0)
    germane_load: float = Field(ge=0.0, le=1.0)
    total_cognitive_load: Optional[float] = Field(default=None, ge=0.0, le=3.0)

    def __init__(self, **data):
        super().__init__(**data)
        if self.total_cognitive_load is None:
            self.total_cognitive_load = self.intrinsic_load + self.extraneous_load + self.germane_load

class EducationalContentMetadata(BaseModel):
    """Metadata for generated educational content"""
    generation_duration_ms: int
    tokens_used: int
    prompt_template: str
    ai_provider: str
    template_variables: Dict[str, Any]
    educational_effectiveness_score: Optional[float] = None
    cognitive_load_metrics: Optional[CognitiveLoadMetricsModel] = None
    readability_score: Optional[float] = None

class QualityMetrics(BaseModel):
    """Quality assessment metrics for educational content"""
    overall_quality_score: float = Field(ge=0.0, le=1.0)
    educational_value: float = Field(ge=0.0, le=1.0)
    factual_accuracy: float = Field(ge=0.0, le=1.0)
    age_appropriateness: float = Field(ge=0.0, le=1.0)
    structural_quality: float = Field(ge=0.0, le=1.0)
    engagement_level: float = Field(ge=0.0, le=1.0)

    # Quality thresholds from la-factoria-railway-deployment.md
    meets_minimum_threshold: bool = Field(default=False)
    meets_educational_threshold: bool = Field(default=False)
    meets_accuracy_threshold: bool = Field(default=False)

    def __init__(self, **data):
        super().__init__(**data)
        # Calculate threshold compliance
        self.meets_minimum_threshold = self.overall_quality_score >= 0.70
        self.meets_educational_threshold = self.educational_value >= 0.75
        self.meets_accuracy_threshold = self.factual_accuracy >= 0.85

class EducationalContent(BaseModel):
    """Main educational content model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_type: LaFactoriaContentType
    topic: str = Field(..., min_length=3, max_length=500)
    age_group: LearningLevel
    learning_objectives: List[LearningObjectiveModel] = Field(default_factory=list)
    generated_content: Dict[str, Any]
    quality_metrics: Optional[QualityMetrics] = None
    metadata: Optional[EducationalContentMetadata] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        use_enum_values=True
    )

# Database models (using SQLAlchemy patterns)
from sqlalchemy import Column, String, DateTime, JSON, Numeric, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa

Base = declarative_base()

class EducationalContentDB(Base):
    """SQLAlchemy model for educational content storage"""
    __tablename__ = "educational_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # Optional user tracking
    content_type = Column(String(50), nullable=False)
    topic = Column(String(500), nullable=False)
    age_group = Column(String(50), nullable=False)
    learning_objectives = Column(JSON, nullable=False, default=list)
    cognitive_load_metrics = Column(JSON, nullable=False, default=dict)
    generated_content = Column(JSON, nullable=False)
    quality_score = Column(Numeric(3, 2), nullable=True)
    generation_duration_ms = Column(Integer, nullable=True)
    ai_provider = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=sa.func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=sa.func.now())

    # Indexes for performance
    __table_args__ = (
        sa.Index('idx_educational_content_content_type', 'content_type'),
        sa.Index('idx_educational_content_topic', 'topic'),
        sa.Index('idx_educational_content_created_at', 'created_at'),
    )

class UserModel(Base):
    """User model for La Factoria platform"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    api_key_hash = Column(String(255), nullable=True)  # Hashed API key
    is_active = Column(Boolean, default=True)
    learning_preferences = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=sa.func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=sa.func.now())

    __table_args__ = (
        sa.Index('idx_users_email', 'email'),
        sa.Index('idx_users_username', 'username'),
    )
