"""
Pydantic models for content feedback.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FeedbackBase(BaseModel):
    """Base model for feedback."""

    rating: bool = Field(
        ...,
        description="User's rating for the content (e.g., True for like, False for dislike).",
    )
    comment: Optional[str] = Field(
        None, max_length=1000, description="Optional user comment."
    )


class FeedbackCreate(FeedbackBase):
    """Model for creating new feedback."""


class FeedbackResponse(FeedbackBase):
    """Model for returning feedback information."""

    id: UUID = Field(..., description="Unique feedback identifier.")
    content_id: str = Field(
        ..., description="Identifier of the content being rated."
    )  # Assuming content_id might be a string from job results
    user_id: str = Field(
        ..., description="Identifier of the user providing feedback."
    )  # Assuming user_id is a string
    created_at: datetime = Field(
        ..., description="Timestamp of when the feedback was created."
    )

    class Config:
        from_attributes = True  # For Pydantic V2 compatibility
