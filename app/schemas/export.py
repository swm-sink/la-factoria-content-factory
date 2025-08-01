"""
Pydantic schemas for export API endpoints.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

from app.models.export import ExportFormat, ExportStatus


class ExportRequestSchema(BaseModel):
    """Schema for export request."""
    
    content_ids: List[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of content IDs to export",
        examples=[["content-123", "content-456"]]
    )
    format: ExportFormat = Field(
        ...,
        description="Export format",
        examples=[ExportFormat.PDF]
    )
    include_metadata: bool = Field(
        default=True,
        description="Include metadata in export"
    )
    include_quality_metrics: bool = Field(
        default=True,
        description="Include quality metrics in export"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional filters",
        examples=[{"content_type": "study_guide", "date_from": "2024-01-01"}]
    )


class ExportJobResponseSchema(BaseModel):
    """Schema for export job response."""
    
    job_id: str = Field(..., description="Export job ID")
    status: ExportStatus = Field(..., description="Export status")
    format: ExportFormat = Field(..., description="Export format")
    progress: float = Field(..., description="Progress percentage")
    download_url: Optional[str] = Field(None, description="Download URL when ready")
    expires_at: Optional[datetime] = Field(None, description="URL expiration time")
    message: str = Field(..., description="Status message")


class ExportProgressSchema(BaseModel):
    """Schema for export progress updates."""
    
    job_id: str
    status: ExportStatus
    progress: float
    estimated_time_remaining: Optional[int] = Field(
        None,
        description="Estimated seconds remaining"
    )


class BulkExportRequestSchema(BaseModel):
    """Schema for bulk export request."""
    
    format: ExportFormat = Field(..., description="Export format for all content")
    filters: Dict[str, Any] = Field(
        ...,
        description="Filters to select content",
        examples=[{
            "date_from": "2024-01-01",
            "date_to": "2024-12-31",
            "content_types": ["study_guide", "flashcards"],
            "user_id": "user-123"
        }]
    )
    max_items: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximum number of items to export"
    )