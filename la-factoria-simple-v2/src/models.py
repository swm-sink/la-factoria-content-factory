"""
Simple Pydantic models for request/response validation
"""

import uuid
from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

# All content types we support (from extracted prompts)
ContentType = Literal[
    "study_guide",
    "study_guide_enhanced",
    "flashcards",
    "podcast_script",
    "one_pager_summary",
    "detailed_reading_material",
    "faq_collection",
    "reading_guide_questions",
    "master_content_outline",
]


class GenerateRequest(BaseModel):
    """Request model for content generation."""

    topic: str = Field(..., min_length=10, max_length=500, description="Topic for content generation")
    content_type: ContentType = Field(default="study_guide", description="Type of content to generate")

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Custom validation for topic."""
        v = v.strip()
        if len(v) < 10:
            raise ValueError("Topic must be at least 10 characters long")
        if len(v) > 500:
            raise ValueError("Topic must be at most 500 characters long")
        return v


class GenerateResponse(BaseModel):
    """Response model for content generation."""

    content: str
    content_type: ContentType
    topic: str
    generated_at: str
    request_id: str

    @classmethod
    def create(cls, content: str, content_type: ContentType, topic: str):
        """Factory method to create response with auto-generated fields."""
        return cls(
            content=content,
            content_type=content_type,
            topic=topic,
            generated_at=datetime.now(timezone.utc).isoformat(),
            request_id=str(uuid.uuid4()),
        )
