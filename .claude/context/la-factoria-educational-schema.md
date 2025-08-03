# La Factoria Educational Content Schema Context

## 8 Specific Content Types Database Schema

### Content Type Enumeration
```python
from enum import Enum

class LaFactoriaContentType(Enum):
    MASTER_CONTENT_OUTLINE = "master_content_outline"
    PODCAST_SCRIPT = "podcast_script"
    STUDY_GUIDE = "study_guide"
    ONE_PAGER_SUMMARY = "one_pager_summary"
    DETAILED_READING_MATERIAL = "detailed_reading_material"
    FAQ_COLLECTION = "faq_collection"
    FLASHCARDS = "flashcards"
    READING_GUIDE_QUESTIONS = "reading_guide_questions"
```

### Educational Content Schema
```sql
-- Main educational content table for La Factoria's 8 content types
CREATE TABLE educational_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Content type from our 8 specific types
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN (
        'master_content_outline', 'podcast_script', 'study_guide',
        'one_pager_summary', 'detailed_reading_material', 'faq_collection',
        'flashcards', 'reading_guide_questions'
    )),
    
    -- Input data
    topic VARCHAR(500) NOT NULL,
    age_group VARCHAR(50) DEFAULT 'general',
    additional_requirements TEXT,
    
    -- Learning science data
    learning_objectives JSONB NOT NULL,
    cognitive_load_metrics JSONB NOT NULL,
    bloom_taxonomy_level VARCHAR(20),
    
    -- Generated content (using exact prompt template structure)
    generated_content JSONB NOT NULL,
    
    -- Quality assessment
    quality_score DECIMAL(3,2) CHECK (quality_score BETWEEN 0 AND 1),
    educational_effectiveness_score DECIMAL(3,2),
    readability_score DECIMAL(3,2),
    engagement_score DECIMAL(3,2),
    
    -- Metadata
    generation_duration_ms INTEGER,
    tokens_used INTEGER,
    cost_cents INTEGER,
    langfuse_trace_id VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for educational content queries
CREATE INDEX idx_educational_content_type ON educational_content(content_type);
CREATE INDEX idx_educational_content_user ON educational_content(user_id);
CREATE INDEX idx_educational_content_topic ON educational_content USING gin(to_tsvector('english', topic));
CREATE INDEX idx_educational_content_quality ON educational_content(quality_score);
CREATE INDEX idx_educational_content_bloom ON educational_content(bloom_taxonomy_level);
```

### Learning Objectives Table
```sql
-- Learning objectives following Bloom's taxonomy
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
```

### Content Quality Metrics Table
```sql
-- Detailed quality metrics for each piece of content
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
```

### Content Type Specific Schemas

#### Master Content Outline Schema
```sql
-- Schema validation for master_content_outline content type
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
```

#### Podcast Script Schema
```sql
-- Schema validation for podcast_script content type
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
```

#### Study Guide Schema
```sql
-- Schema validation for study_guide content type
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

### SQLAlchemy Models for La Factoria
```python
from sqlalchemy import Column, String, Text, DateTime, Integer, Numeric, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from enum import Enum
import uuid

class EducationalContent(Base):
    __tablename__ = "educational_content"
    
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Content classification
    content_type: Mapped[str] = mapped_column(String(50))
    topic: Mapped[str] = mapped_column(String(500))
    age_group: Mapped[str] = mapped_column(String(50), default="general")
    additional_requirements: Mapped[Optional[str]] = mapped_column(Text)
    
    # Learning science data
    learning_objectives: Mapped[dict] = mapped_column(JSONB)
    cognitive_load_metrics: Mapped[dict] = mapped_column(JSONB)
    bloom_taxonomy_level: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Generated content
    generated_content: Mapped[dict] = mapped_column(JSONB)
    
    # Quality scores
    quality_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    educational_effectiveness_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    readability_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    engagement_score: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    
    # Performance metrics
    generation_duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    cost_cents: Mapped[Optional[int]] = mapped_column(Integer)
    langfuse_trace_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="educational_content")
    learning_objectives_rel: Mapped[List["LearningObjective"]] = relationship(back_populates="content")
    quality_metrics: Mapped[List["ContentQualityMetrics"]] = relationship(back_populates="content")
```

### Migration Script for La Factoria Schema
```python
# migrations/001_la_factoria_educational_schema.py
"""Create La Factoria educational content schema

Revision ID: 001
Create Date: 2025-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create educational_content table
    op.create_table(
        'educational_content',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('content_type', sa.String(50), nullable=False),
        sa.Column('topic', sa.String(500), nullable=False),
        sa.Column('age_group', sa.String(50), default='general'),
        sa.Column('additional_requirements', sa.Text),
        sa.Column('learning_objectives', postgresql.JSONB, nullable=False),
        sa.Column('cognitive_load_metrics', postgresql.JSONB, nullable=False),
        sa.Column('bloom_taxonomy_level', sa.String(20)),
        sa.Column('generated_content', postgresql.JSONB, nullable=False),
        sa.Column('quality_score', sa.Numeric(3, 2)),
        sa.Column('educational_effectiveness_score', sa.Numeric(3, 2)),
        sa.Column('readability_score', sa.Numeric(3, 2)),
        sa.Column('engagement_score', sa.Numeric(3, 2)),
        sa.Column('generation_duration_ms', sa.Integer),
        sa.Column('tokens_used', sa.Integer),
        sa.Column('cost_cents', sa.Integer),
        sa.Column('langfuse_trace_id', sa.String(255)),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Add check constraints
    op.create_check_constraint(
        'valid_content_type',
        'educational_content',
        "content_type IN ('master_content_outline', 'podcast_script', 'study_guide', 'one_pager_summary', 'detailed_reading_material', 'faq_collection', 'flashcards', 'reading_guide_questions')"
    )
    
    # Create indexes
    op.create_index('idx_educational_content_type', 'educational_content', ['content_type'])
    op.create_index('idx_educational_content_user', 'educational_content', ['user_id'])
    op.create_index('idx_educational_content_quality', 'educational_content', ['quality_score'])

def downgrade():
    op.drop_table('educational_content')
```