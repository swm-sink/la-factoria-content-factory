# PostgreSQL with SQLAlchemy Async Context

## SQLAlchemy 2.0 Async Architecture

### Core Async Patterns
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from typing import List, Optional
import datetime

# Modern SQLAlchemy 2.0 Base
class Base(DeclarativeBase):
    pass

# Async engine configuration for PostgreSQL
async_engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost:5432/la_factoria",
    echo=True,  # Enable SQL logging in development
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Async session factory
AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_session() -> AsyncSession:
    """Dependency for FastAPI async database sessions."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

## Educational Content Data Models

### 1. Core Educational Models
```python
from sqlalchemy import Table, Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any, List
import uuid

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Educational preferences
    learning_preferences: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    subscription_tier: Mapped[str] = mapped_column(String(20), default="free")
    
    # Relationships
    api_keys: Mapped[List["APIKey"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    content_items: Mapped[List["Content"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    learning_progress: Mapped[List["LearningProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    feedback_entries: Mapped[List["ContentFeedback"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    
    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    rate_limit: Mapped[int] = mapped_column(Integer, default=100)  # requests per hour
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="api_keys")

class Content(Base):
    __tablename__ = "content"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    
    # Content metadata
    title: Mapped[str] = mapped_column(String(255), index=True)
    content_type: Mapped[str] = mapped_column(String(50), index=True)  # study_guide, flashcards, quiz, podcast
    audience_level: Mapped[str] = mapped_column(String(50), index=True)  # elementary, middle_school, etc.
    subject_area: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    
    # Content data
    content_text: Mapped[str] = mapped_column(Text)
    content_structured: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)  # Structured content data
    
    # Generation metadata
    generation_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    llm_provider: Mapped[Optional[str]] = mapped_column(String(50))
    llm_model: Mapped[Optional[str]] = mapped_column(String(100))
    generation_cost: Mapped[Optional[float]] = mapped_column()
    generation_tokens: Mapped[Optional[int]] = mapped_column()
    
    # Quality and assessment
    quality_score: Mapped[Optional[float]] = mapped_column()
    quality_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    review_status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, approved, rejected
    
    # Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="content_items")
    versions: Mapped[List["ContentVersion"]] = relationship(back_populates="content", cascade="all, delete-orphan")
    feedback_entries: Mapped[List["ContentFeedback"]] = relationship(back_populates="content", cascade="all, delete-orphan")
    learning_progress: Mapped[List["LearningProgress"]] = relationship(back_populates="content")
    audio_files: Mapped[List["AudioFile"]] = relationship(back_populates="content", cascade="all, delete-orphan")

class ContentVersion(Base):
    __tablename__ = "content_versions"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id: Mapped[str] = mapped_column(ForeignKey("content.id"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    
    # Version-specific data
    content_text: Mapped[str] = mapped_column(Text)
    content_structured: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    change_summary: Mapped[Optional[str]] = mapped_column(Text)
    
    # Metadata
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    created_by: Mapped[str] = mapped_column(String(50))  # "user", "ai_revision", "quality_improvement"
    
    # Relationships
    content: Mapped["Content"] = relationship(back_populates="versions")

class LearningProgress(Base):
    __tablename__ = "learning_progress"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    content_id: Mapped[str] = mapped_column(ForeignKey("content.id"), index=True)
    
    # Progress tracking
    status: Mapped[str] = mapped_column(String(20), default="not_started")  # not_started, in_progress, completed
    progress_percentage: Mapped[float] = mapped_column(default=0.0)
    time_spent_minutes: Mapped[int] = mapped_column(default=0)
    
    # Assessment data
    quiz_scores: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    flashcard_scores: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    learning_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Timestamps
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    last_accessed: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="learning_progress")
    content: Mapped["Content"] = relationship(back_populates="learning_progress")

class ContentFeedback(Base):
    __tablename__ = "content_feedback"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    content_id: Mapped[str] = mapped_column(ForeignKey("content.id"), index=True)
    
    # Feedback data
    rating: Mapped[Optional[int]] = mapped_column()  # 1-5 scale
    feedback_text: Mapped[Optional[str]] = mapped_column(Text)
    feedback_type: Mapped[str] = mapped_column(String(50))  # quality, accuracy, usefulness, difficulty
    
    # Structured feedback
    feedback_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="feedback_entries")
    content: Mapped["Content"] = relationship(back_populates="feedback_entries")

class AudioFile(Base):
    __tablename__ = "audio_files"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id: Mapped[str] = mapped_column(ForeignKey("content.id"), index=True)
    
    # File metadata
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    file_size: Mapped[int] = mapped_column()
    duration_seconds: Mapped[Optional[float]] = mapped_column()
    format: Mapped[str] = mapped_column(String(10))  # mp3, wav, etc.
    
    # Generation metadata
    tts_provider: Mapped[Optional[str]] = mapped_column(String(50))  # elevenlabs, openai, etc.
    voice_id: Mapped[Optional[str]] = mapped_column(String(100))
    voice_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    generation_cost: Mapped[Optional[float]] = mapped_column()
    
    # Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    content: Mapped["Content"] = relationship(back_populates="audio_files")
```

## Advanced Async Repository Patterns

### 1. Base Repository Pattern
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from abc import ABC, abstractmethod

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T], ABC):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model
    
    async def create(self, **kwargs) -> T:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance
    
    async def get_by_id(self, id: str) -> Optional[T]:
        """Get record by ID."""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        offset: int = 0, 
        limit: int = 100,
        **filters
    ) -> List[T]:
        """Get multiple records with pagination and filtering."""
        stmt = select(self.model)
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                stmt = stmt.where(getattr(self.model, key) == value)
        
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def update(self, id: str, **kwargs) -> Optional[T]:
        """Update record by ID."""
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def delete(self, id: str) -> bool:
        """Delete record by ID."""
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def count(self, **filters) -> int:
        """Count records with optional filtering."""
        stmt = select(func.count(self.model.id))
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                stmt = stmt.where(getattr(self.model, key) == value)
        
        result = await self.session.execute(stmt)
        return result.scalar()

class ContentRepository(BaseRepository[Content]):
    """Specialized repository for Content model."""
    
    async def get_by_user(
        self, 
        user_id: str,
        content_type: Optional[str] = None,
        audience_level: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[Content]:
        """Get content for a specific user with filtering."""
        stmt = select(Content).where(Content.user_id == user_id)
        
        if content_type:
            stmt = stmt.where(Content.content_type == content_type)
        if audience_level:
            stmt = stmt.where(Content.audience_level == audience_level)
        
        stmt = stmt.order_by(Content.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_quality_range(
        self,
        min_score: float,
        max_score: float,
        content_type: Optional[str] = None
    ) -> List[Content]:
        """Get content within quality score range."""
        stmt = select(Content).where(
            Content.quality_score.between(min_score, max_score)
        )
        
        if content_type:
            stmt = stmt.where(Content.content_type == content_type)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_recent_popular(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get recently popular content based on feedback."""
        from datetime import timedelta
        cutoff_date = datetime.datetime.utcnow() - timedelta(days=days)
        
        stmt = (
            select(
                Content.id,
                Content.title,
                Content.content_type,
                func.avg(ContentFeedback.rating).label("avg_rating"),
                func.count(ContentFeedback.id).label("feedback_count")
            )
            .join(ContentFeedback)
            .where(Content.created_at >= cutoff_date)
            .group_by(Content.id, Content.title, Content.content_type)
            .having(func.count(ContentFeedback.id) >= 3)
            .order_by(func.avg(ContentFeedback.rating).desc())
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return [dict(row._mapping) for row in result]
    
    async def update_quality_score(self, content_id: str, quality_data: Dict[str, Any]) -> None:
        """Update quality score and metrics for content."""
        stmt = (
            update(Content)
            .where(Content.id == content_id)
            .values(
                quality_score=quality_data.get("overall_score"),
                quality_metrics=quality_data,
                updated_at=datetime.datetime.utcnow()
            )
        )
        await self.session.execute(stmt)
```

## Database Migration Strategies

### 1. Alembic Configuration
```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio

# Import your models
from app.models import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 2. Migration Best Practices
```python
# Migration template for educational content schema
"""Add content quality tracking

Revision ID: 001_content_quality
Revises: base
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001_content_quality'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create content table with quality tracking
    op.create_table(
        'content',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('audience_level', sa.String(length=50), nullable=False),
        sa.Column('subject_area', sa.String(length=100), nullable=True),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('content_structured', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('generation_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('llm_provider', sa.String(length=50), nullable=True),
        sa.Column('llm_model', sa.String(length=100), nullable=True),
        sa.Column('generation_cost', sa.Float(), nullable=True),
        sa.Column('generation_tokens', sa.Integer(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('quality_metrics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_reviewed', sa.Boolean(), nullable=False, default=False),
        sa.Column('review_status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('ix_content_user_id', 'content', ['user_id'])
    op.create_index('ix_content_content_type', 'content', ['content_type'])
    op.create_index('ix_content_audience_level', 'content', ['audience_level'])
    op.create_index('ix_content_subject_area', 'content', ['subject_area'])
    op.create_index('ix_content_created_at', 'content', ['created_at'])
    op.create_index('ix_content_quality_score', 'content', ['quality_score'])
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_content_user_id',
        'content', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade() -> None:
    op.drop_table('content')
```

## Performance Optimization Strategies

### 1. Connection Pooling
```python
from sqlalchemy.pool import QueuePool
import os

def create_optimized_async_engine():
    """Create async engine with optimized connection pooling."""
    
    # Railway production configuration
    if os.environ.get("RAILWAY_ENVIRONMENT") == "production":
        return create_async_engine(
            os.environ["DATABASE_URL"].replace("postgres://", "postgresql+asyncpg://"),
            echo=False,
            pool_size=5,  # Conservative for Railway
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            poolclass=QueuePool,
            connect_args={
                "server_settings": {
                    "application_name": "la-factoria-prod",
                    "jit": "off"  # Disable JIT for better connection stability
                }
            }
        )
    
    # Development configuration
    else:
        return create_async_engine(
            "postgresql+asyncpg://user:password@localhost:5432/la_factoria_dev",
            echo=True,
            pool_size=2,
            max_overflow=5,
            pool_pre_ping=True,
            pool_recycle=3600
        )

# Usage monitoring
async def monitor_connection_pool(engine):
    """Monitor connection pool health."""
    pool = engine.pool
    
    metrics = {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalid()
    }
    
    # Log if pool utilization is high
    utilization = (metrics["checked_out"] + metrics["overflow"]) / (metrics["pool_size"] + pool._max_overflow)
    if utilization > 0.8:
        logger.warning(f"High connection pool utilization: {utilization:.2%}")
    
    return metrics
```

### 2. Query Optimization
```python
from sqlalchemy.orm import selectinload, joinedload, contains_eager
from sqlalchemy import and_, or_

class OptimizedContentQueries:
    """Optimized queries for educational content."""
    
    @staticmethod
    async def get_content_with_relations(session: AsyncSession, content_id: str) -> Optional[Content]:
        """Get content with all related data in single query."""
        stmt = (
            select(Content)
            .options(
                selectinload(Content.versions),
                selectinload(Content.feedback_entries),
                selectinload(Content.audio_files),
                joinedload(Content.user)
            )
            .where(Content.id == content_id)
        )
        
        result = await session.execute(stmt)
        return result.unique().scalar_one_or_none()
    
    @staticmethod
    async def get_user_dashboard_data(session: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user dashboard data efficiently."""
        
        # Content summary query
        content_summary_stmt = (
            select(
                Content.content_type,
                func.count(Content.id).label("count"),
                func.avg(Content.quality_score).label("avg_quality")
            )
            .where(Content.user_id == user_id)
            .group_by(Content.content_type)
        )
        
        # Recent content query
        recent_content_stmt = (
            select(Content)
            .where(Content.user_id == user_id)
            .order_by(Content.created_at.desc())
            .limit(5)
        )
        
        # Learning progress query
        progress_stmt = (
            select(
                LearningProgress.content_id,
                LearningProgress.status,
                LearningProgress.progress_percentage,
                Content.title,
                Content.content_type
            )
            .join(Content)
            .where(LearningProgress.user_id == user_id)
            .order_by(LearningProgress.last_accessed.desc())
            .limit(10)
        )
        
        # Execute all queries
        content_summary_result = await session.execute(content_summary_stmt)
        recent_content_result = await session.execute(recent_content_stmt)
        progress_result = await session.execute(progress_stmt)
        
        return {
            "content_summary": [dict(row._mapping) for row in content_summary_result],
            "recent_content": recent_content_result.scalars().all(),
            "learning_progress": [dict(row._mapping) for row in progress_result]
        }
    
    @staticmethod
    async def search_content(
        session: AsyncSession,
        query: str,
        content_type: Optional[str] = None,
        audience_level: Optional[str] = None,
        min_quality: Optional[float] = None,
        limit: int = 20
    ) -> List[Content]:
        """Full-text search with filtering."""
        
        # Base search using PostgreSQL full-text search
        stmt = select(Content).where(
            or_(
                Content.title.ilike(f"%{query}%"),
                Content.content_text.ilike(f"%{query}%")
            )
        )
        
        # Apply filters
        if content_type:
            stmt = stmt.where(Content.content_type == content_type)
        if audience_level:
            stmt = stmt.where(Content.audience_level == audience_level)
        if min_quality:
            stmt = stmt.where(Content.quality_score >= min_quality)
        
        # Order by relevance (simplified)
        stmt = stmt.order_by(Content.created_at.desc()).limit(limit)
        
        result = await session.execute(stmt)
        return result.scalars().all()
```

## Sources
61. SQLAlchemy 2.0 Official Documentation - Async Patterns
62. PostgreSQL with asyncpg High-Performance Integration
63. Educational Content Database Design Patterns
64. SQLAlchemy Async Repository Implementation Examples
65. Database Migration Strategies with Alembic
66. PostgreSQL Connection Pooling and Performance Optimization
67. FastAPI + SQLAlchemy Async Production Examples (grillazz/fastapi-sqlalchemy-asyncpg)
68. Official FastAPI Full-Stack Template Database Patterns
69. Educational Platform Data Modeling Best Practices
70. PostgreSQL Full-Text Search and Query Optimization