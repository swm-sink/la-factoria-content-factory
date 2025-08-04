"""
Database Models Example for La Factoria
=======================================

This example bridges the abstract database architecture with concrete SQLAlchemy models.
Demonstrates the implementation of the database schema defined in project-overview.md.

Key patterns demonstrated:
- SQLAlchemy models for educational content platform
- Proper relationships between users, content, and quality scores
- GDPR-compliant data handling patterns
- Indexing for performance optimization
- Educational metadata structures
"""

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, Text, JSON,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """
    User accounts and API key management

    Bridges Architecture Concept:
    - "users - User accounts and API keys" from project-overview.md
    - GDPR-compliant user deletion capability
    """
    __tablename__ = "users"

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_key_hash = Column(String(64), unique=True, nullable=False, index=True)

    # Basic user information (minimal for privacy)
    email = Column(String(255), unique=True, nullable=True)  # Optional for anonymous usage
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow)

    # Usage tracking
    total_generations = Column(Integer, default=0)
    monthly_generations = Column(Integer, default=0)
    monthly_reset_date = Column(DateTime, default=datetime.utcnow)

    # Account status
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String(20), default="free")  # free, pro, enterprise

    # Relationships
    generated_content = relationship("GeneratedContent", back_populates="user", cascade="all, delete-orphan")
    usage_analytics = relationship("UsageAnalytics", back_populates="user", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index('idx_user_api_key', 'api_key_hash'),
        Index('idx_user_email', 'email'),
        Index('idx_user_active', 'is_active', 'last_active'),
    )

class GeneratedContent(Base):
    """
    Generated educational content with metadata

    Bridges Architecture Concept:
    - "content - Generated educational content with metadata" from project-overview.md
    - Links to 8 content types from educational content system
    """
    __tablename__ = "generated_content"

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Content specification
    topic = Column(String(500), nullable=False)
    content_type = Column(String(50), nullable=False)  # One of 8 types from architecture
    target_audience = Column(String(50), nullable=False)
    language = Column(String(10), default="en")

    # Generated content
    content_text = Column(Text, nullable=False)
    content_metadata = Column(JSON)  # Structured metadata about content

    # Generation details
    ai_provider = Column(String(20), nullable=False)  # openai, anthropic, vertex_ai
    prompt_template_version = Column(String(20))
    tokens_used = Column(Integer)
    generation_time_ms = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="generated_content")
    quality_scores = relationship("QualityScore", back_populates="content", cascade="all, delete-orphan")

    # Indexes for educational content queries
    __table_args__ = (
        Index('idx_content_user_type', 'user_id', 'content_type'),
        Index('idx_content_audience', 'target_audience'),
        Index('idx_content_created', 'created_at'),
        Index('idx_content_topic', 'topic'),
    )

class QualityScore(Base):
    """
    Content quality assessment results

    Bridges Architecture Concept:
    - "quality_scores - Content quality assessment results" from project-overview.md
    - Implements quality metrics from Quality Assessment System (≥0.75 educational, ≥0.85 factual, ≥0.70 overall)
    """
    __tablename__ = "quality_scores"

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id"), nullable=False)

    # Quality dimensions (from architecture: Educational value, Factual accuracy, Age appropriateness, etc)
    overall_score = Column(Float, nullable=False)  # ≥0.70 threshold
    educational_value = Column(Float, nullable=False)  # ≥0.75 threshold
    factual_accuracy = Column(Float, nullable=False)  # ≥0.85 threshold
    age_appropriateness = Column(Float, nullable=False)
    structural_quality = Column(Float, nullable=False)
    engagement_level = Column(Float, nullable=False)

    # Assessment metadata
    assessment_method = Column(String(50))  # ai_judge, rubric_based, expert_review
    assessment_details = Column(JSON)  # Detailed breakdown of assessment
    meets_quality_threshold = Column(Boolean, nullable=False)

    # Assessment tracking
    assessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    assessor_version = Column(String(20))  # Version of quality assessment algorithm

    # Relationships
    content = relationship("GeneratedContent", back_populates="quality_scores")

    # Indexes for quality analysis
    __table_args__ = (
        Index('idx_quality_content', 'content_id'),
        Index('idx_quality_overall', 'overall_score'),
        Index('idx_quality_educational', 'educational_value'),
        Index('idx_quality_factual', 'factual_accuracy'),
        Index('idx_quality_threshold', 'meets_quality_threshold'),
    )

class UsageAnalytics(Base):
    """
    Generation statistics and performance metrics

    Bridges Architecture Concept:
    - "usage_analytics - Generation statistics and performance metrics" from project-overview.md
    - Supports monitoring and cost optimization
    """
    __tablename__ = "usage_analytics"

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Request details
    endpoint = Column(String(100), nullable=False)
    content_type = Column(String(50))
    ai_provider = Column(String(20))

    # Performance metrics
    response_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    request_size_bytes = Column(Integer)
    response_size_bytes = Column(Integer)

    # Request outcome
    status_code = Column(Integer, nullable=False)
    success = Column(Boolean, nullable=False)
    error_type = Column(String(100))  # If request failed

    # Cost tracking
    estimated_cost_usd = Column(Float)  # Based on provider pricing

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="usage_analytics")

    # Indexes for analytics queries
    __table_args__ = (
        Index('idx_analytics_user_date', 'user_id', 'created_at'),
        Index('idx_analytics_endpoint', 'endpoint'),
        Index('idx_analytics_provider', 'ai_provider'),
        Index('idx_analytics_success', 'success', 'created_at'),
    )

class ContentTypeTemplate(Base):
    """
    Prompt template versioning and management

    Bridges Architecture Concept:
    - Links prompt templates from prompts/ directory with database versioning
    - Supports A/B testing and template evolution
    """
    __tablename__ = "content_type_templates"

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_type = Column(String(50), nullable=False)

    # Template details
    template_name = Column(String(100), nullable=False)
    template_version = Column(String(20), nullable=False)
    template_content = Column(Text, nullable=False)

    # Template metadata
    description = Column(Text)
    target_audiences = Column(JSON)  # List of supported audiences
    estimated_tokens = Column(Integer)

    # Template status
    is_active = Column(Boolean, default=True)
    performance_score = Column(Float)  # Based on usage analytics

    # Versioning
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(100))  # User or system that created template

    # Unique constraint on active templates
    __table_args__ = (
        Index('idx_template_type_version', 'content_type', 'template_version'),
        Index('idx_template_active', 'content_type', 'is_active'),
        UniqueConstraint('content_type', 'is_active', name='uq_active_template_per_type'),
    )

# Educational domain-specific models
class LearningObjective(Base):
    """
    Learning objectives linked to generated content

    Bridges Architecture Concept:
    - Supports Bloom's taxonomy from educational content system
    - Links to specific generated content pieces
    """
    __tablename__ = "learning_objectives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id"), nullable=False)

    # Bloom's taxonomy classification
    cognitive_level = Column(String(20), nullable=False)  # remember, understand, apply, analyze, evaluate, create
    objective_text = Column(Text, nullable=False)

    # Educational metadata
    subject_area = Column(String(100))
    difficulty_level = Column(String(20))  # beginner, intermediate, advanced
    estimated_time_minutes = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_objective_content', 'content_id'),
        Index('idx_objective_cognitive', 'cognitive_level'),
    )

"""
Usage Example:
==============

# Database initialization
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://user:password@localhost/lafactoria")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create user and generate content
session = SessionLocal()
user = User(api_key_hash="hashed_api_key", email="educator@school.edu")
session.add(user)
session.commit()

content = GeneratedContent(
    user_id=user.id,
    topic="Python Programming Basics",
    content_type="study_guide",
    target_audience="high_school",
    content_text="Generated study guide content...",
    ai_provider="openai",
    tokens_used=1500
)
session.add(content)
session.commit()

# Add quality assessment
quality = QualityScore(
    content_id=content.id,
    overall_score=0.85,
    educational_value=0.88,
    factual_accuracy=0.92,
    age_appropriateness=0.82,
    structural_quality=0.86,
    engagement_level=0.79,
    meets_quality_threshold=True,
    assessment_method="ai_judge"
)
session.add(quality)
session.commit()
"""
