---
name: /la-factoria-postgres
description: "TASK-004: PostgreSQL setup using hyper-specific La Factoria educational schema patterns"
usage: "/la-factoria-postgres [setup|test|verify] [options]"
tools: Read, Write, Edit, Bash, Grep
---

# La Factoria PostgreSQL - TASK-004

**PostgreSQL database implementation using hyper-specific patterns from our educational context engineering and schema design.**

## Context Imports (Anthropic-Compliant)

### Core Database & Platform Context
@.claude/context/postgresql-sqlalchemy.md
@.claude/context/educational-content-assessment.md
@.claude/context/railway.md

### La Factoria Specific Context
@.claude/context/la-factoria-educational-schema.md
@.claude/context/la-factoria-railway-deployment.md
@.claude/context/la-factoria-testing-framework.md
@.claude/context/la-factoria-prompt-integration.md

### Implementation References
@.claude/prp/PRP-002-Backend-API-Architecture.md
@.claude/domains/technical/README.md

## Context-Driven Implementation Process

```bash
# Phase 1: Educational Database Schema (Using Context Patterns)
/la-factoria-postgres create-educational-schema # Uses la-factoria-educational-schema.md lines 20-95
/la-factoria-postgres create-sqlalchemy-models  # Generate SQLAlchemy models from context patterns
/la-factoria-postgres create-migrations         # Alembic migrations for educational content

# Phase 2: Railway PostgreSQL Integration (Railway Context)
/la-factoria-postgres setup-railway-db          # Uses la-factoria-railway-deployment.md lines 369-423
/la-factoria-postgres configure-connection      # Database connection with Railway environment
/la-factoria-postgres create-health-checks      # PostgreSQL health monitoring

# Phase 3: Educational CRUD Operations (Simple & Efficient)
/la-factoria-postgres create-content-repository # Educational content repository pattern
/la-factoria-postgres create-user-operations    # User management for educational platform
/la-factoria-postgres add-quality-metrics       # Quality assessment data operations

# Phase 4: TDD Testing (Using Testing Framework Context)
/la-factoria-postgres write-database-tests      # Uses la-factoria-testing-framework.md database patterns
/la-factoria-postgres test-educational-queries  # Test educational content queries
/la-factoria-postgres test-quality-operations   # Test quality metrics storage and retrieval
```

## Generated Files with Context Integration

### 1. Educational Database Schema (`migrations/001_la_factoria_schema.sql`)
**Uses Exact Patterns From**: `context/la-factoria-educational-schema.md` lines 20-95 + `context/postgresql-sqlalchemy.md`

```sql
-- Generated from la-factoria-educational-schema.md lines 20-62: Educational content schema
-- La Factoria educational platform database schema

-- Users table for educational platform
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    learning_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Educational content table for 8 La Factoria content types
CREATE TABLE educational_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Content type from our 8 specific types (la-factoria-educational-schema.md lines 28-32)
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN (
        'master_content_outline', 'podcast_script', 'study_guide',
        'one_pager_summary', 'detailed_reading_material', 'faq_collection',
        'flashcards', 'reading_guide_questions'
    )),
    
    -- Input data
    topic VARCHAR(500) NOT NULL,
    age_group VARCHAR(50) DEFAULT 'general',
    additional_requirements TEXT,
    
    -- Learning science data (la-factoria-educational-schema.md lines 40-42)
    learning_objectives JSONB NOT NULL,
    cognitive_load_metrics JSONB NOT NULL,
    bloom_taxonomy_level VARCHAR(20),
    
    -- Generated content (using exact prompt template structure)
    generated_content JSONB NOT NULL,
    
    -- Quality assessment (la-factoria-educational-schema.md lines 48-51)
    quality_score DECIMAL(3,2) CHECK (quality_score BETWEEN 0 AND 1),
    educational_effectiveness_score DECIMAL(3,2),
    readability_score DECIMAL(3,2),
    engagement_score DECIMAL(3,2),
    
    -- Metadata (la-factoria-educational-schema.md lines 53-57)
    generation_duration_ms INTEGER,
    tokens_used INTEGER,
    cost_cents INTEGER,
    langfuse_trace_id VARCHAR(255),
    ai_provider VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Learning objectives table (la-factoria-educational-schema.md lines 72-95)
CREATE TABLE learning_objectives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES educational_content(id) ON DELETE CASCADE,
    
    -- Bloom's taxonomy classification
    cognitive_level VARCHAR(20) NOT NULL CHECK (cognitive_level IN (
        'remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'
    )),
    
    -- Objective details
    subject_area VARCHAR(100) NOT NULL,
    specific_skill VARCHAR(255) NOT NULL,
    measurable_outcome TEXT NOT NULL,
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 10),
    
    -- Assessment criteria
    assessment_method VARCHAR(100),
    success_criteria TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content quality metrics table (la-factoria-educational-schema.md lines 98-127)
CREATE TABLE content_quality_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID REFERENCES educational_content(id) ON DELETE CASCADE,
    
    -- Cognitive load metrics
    intrinsic_load DECIMAL(3,2) CHECK (intrinsic_load BETWEEN 0 AND 1),
    extraneous_load DECIMAL(3,2) CHECK (extraneous_load BETWEEN 0 AND 1),
    germane_load DECIMAL(3,2) CHECK (germane_load BETWEEN 0 AND 1),
    total_cognitive_load DECIMAL(3,2),
    
    -- Readability metrics
    flesch_reading_ease DECIMAL(5,2),
    flesch_kincaid_grade DECIMAL(4,1),
    automated_readability_index DECIMAL(4,1),
    
    -- Educational effectiveness
    learning_objective_alignment DECIMAL(3,2),
    content_structure_score DECIMAL(3,2),
    engagement_elements_score DECIMAL(3,2),
    assessment_integration_score DECIMAL(3,2),
    
    -- AI-powered quality scores
    ai_quality_assessment JSONB,
    human_review_score DECIMAL(3,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for educational platform performance (la-factoria-educational-schema.md lines 64-69)
CREATE INDEX idx_educational_content_user_id ON educational_content(user_id);
CREATE INDEX idx_educational_content_type ON educational_content(content_type);
CREATE INDEX idx_educational_content_topic ON educational_content USING gin(to_tsvector('english', topic));
CREATE INDEX idx_educational_content_quality ON educational_content(quality_score);
CREATE INDEX idx_educational_content_bloom ON educational_content(bloom_taxonomy_level);
CREATE INDEX idx_educational_content_created_at ON educational_content(created_at);

-- Content validation functions from la-factoria-educational-schema.md lines 132-183
CREATE OR REPLACE FUNCTION validate_master_outline(content JSONB) 
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (
        content ? 'title' AND
        content ? 'overview' AND
        content ? 'learning_objectives' AND
        content ? 'sections' AND
        jsonb_typeof(content->'sections') = 'array' AND
        jsonb_array_length(content->'sections') > 0
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION validate_podcast_script(content JSONB)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (
        content ? 'title' AND
        content ? 'introduction' AND
        content ? 'main_content' AND
        content ? 'conclusion' AND
        content ? 'estimated_duration_minutes'
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION validate_study_guide(content JSONB)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (
        content ? 'title' AND
        content ? 'introduction' AND
        content ? 'key_concepts' AND
        content ? 'study_sections' AND
        content ? 'summary' AND
        jsonb_typeof(content->'key_concepts') = 'array'
    );
END;
$$ LANGUAGE plpgsql;
```

### 2. SQLAlchemy Models (`src/models/educational.py`)
**Uses Exact Patterns From**: `context/la-factoria-educational-schema.md` lines 185-233 + `context/postgresql-sqlalchemy.md`

```python
# Generated from la-factoria-educational-schema.md lines 185-233: SQLAlchemy models
from sqlalchemy import Column, String, Text, DateTime, Integer, Numeric, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql import func
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid
from datetime import datetime

class Base(DeclarativeBase):
    pass

class LaFactoriaContentType(Enum):
    """8 specific La Factoria educational content types"""
    MASTER_CONTENT_OUTLINE = "master_content_outline"
    PODCAST_SCRIPT = "podcast_script"
    STUDY_GUIDE = "study_guide"
    ONE_PAGER_SUMMARY = "one_pager_summary"
    DETAILED_READING_MATERIAL = "detailed_reading_material"
    FAQ_COLLECTION = "faq_collection"
    FLASHCARDS = "flashcards"
    READING_GUIDE_QUESTIONS = "reading_guide_questions"

class User(Base):
    """User model for La Factoria educational platform"""
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    learning_preferences: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    educational_content: Mapped[List["EducationalContent"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class EducationalContent(Base):
    """Educational content model for La Factoria 8 content types"""
    __tablename__ = "educational_content"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    
    # Content classification (la-factoria-educational-schema.md lines 200-202)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    age_group: Mapped[str] = mapped_column(String(50), default="general")
    additional_requirements: Mapped[Optional[str]] = mapped_column(Text)
    
    # Learning science data (la-factoria-educational-schema.md lines 205-208)
    learning_objectives: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    cognitive_load_metrics: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    bloom_taxonomy_level: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Generated content
    generated_content: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    # Quality scores (la-factoria-educational-schema.md lines 214-217)
    quality_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    educational_effectiveness_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    readability_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    engagement_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    
    # Performance metrics (la-factoria-educational-schema.md lines 219-223)
    generation_duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    cost_cents: Mapped[Optional[int]] = mapped_column(Integer)
    langfuse_trace_id: Mapped[Optional[str]] = mapped_column(String(255))
    ai_provider: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="educational_content")
    learning_objectives_rel: Mapped[List["LearningObjective"]] = relationship(back_populates="content", cascade="all, delete-orphan")
    quality_metrics: Mapped[List["ContentQualityMetrics"]] = relationship(back_populates="content", cascade="all, delete-orphan")
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "content_type IN ('master_content_outline', 'podcast_script', 'study_guide', 'one_pager_summary', 'detailed_reading_material', 'faq_collection', 'flashcards', 'reading_guide_questions')",
            name="valid_content_type"
        ),
        CheckConstraint("quality_score BETWEEN 0 AND 1", name="valid_quality_score"),
    )

class LearningObjective(Base):
    """Learning objectives following Bloom's taxonomy"""
    __tablename__ = "learning_objectives"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("educational_content.id", ondelete="CASCADE"))
    
    # Bloom's taxonomy classification
    cognitive_level: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Objective details
    subject_area: Mapped[str] = mapped_column(String(100), nullable=False)
    specific_skill: Mapped[str] = mapped_column(String(255), nullable=False)
    measurable_outcome: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty_level: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Assessment criteria
    assessment_method: Mapped[Optional[str]] = mapped_column(String(100))
    success_criteria: Mapped[Optional[str]] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    content: Mapped["EducationalContent"] = relationship(back_populates="learning_objectives_rel")
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "cognitive_level IN ('remember', 'understand', 'apply', 'analyze', 'evaluate', 'create')",
            name="valid_cognitive_level"
        ),
        CheckConstraint("difficulty_level BETWEEN 1 AND 10", name="valid_difficulty_level"),
    )

class ContentQualityMetrics(Base):
    """Detailed quality metrics for educational content"""
    __tablename__ = "content_quality_metrics"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("educational_content.id", ondelete="CASCADE"))
    
    # Cognitive load metrics
    intrinsic_load: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    extraneous_load: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    germane_load: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    total_cognitive_load: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    
    # Readability metrics
    flesch_reading_ease: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    flesch_kincaid_grade: Mapped[Optional[float]] = mapped_column(Numeric(4, 1))
    automated_readability_index: Mapped[Optional[float]] = mapped_column(Numeric(4, 1))
    
    # Educational effectiveness
    learning_objective_alignment: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    content_structure_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    engagement_elements_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    assessment_integration_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    
    # AI-powered quality scores
    ai_quality_assessment: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    human_review_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    content: Mapped["EducationalContent"] = relationship(back_populates="quality_metrics")
    
    # Table constraints
    __table_args__ = (
        CheckConstraint("intrinsic_load BETWEEN 0 AND 1", name="valid_intrinsic_load"),
        CheckConstraint("extraneous_load BETWEEN 0 AND 1", name="valid_extraneous_load"),
        CheckConstraint("germane_load BETWEEN 0 AND 1", name="valid_germane_load"),
    )
```