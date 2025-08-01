"""
Pydantic models for content export functionality.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.services.export.base import ExportFormat


class ExportStatus(str, Enum):
    """Export job status enumeration."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class ExportRequest(BaseModel):
    """Request model for content export."""
    
    content_ids: List[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of content IDs to export (max 100)"
    )
    format: ExportFormat = Field(
        ...,
        description="Export format (json, csv, pdf, docx, txt)"
    )
    include_metadata: bool = Field(
        default=True,
        description="Include content metadata in export"
    )
    include_quality_metrics: bool = Field(
        default=True,
        description="Include quality metrics in export"
    )
    include_version_info: bool = Field(
        default=True,
        description="Include version information in export"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional filters for content selection"
    )
    template_name: Optional[str] = Field(
        default=None,
        description="Custom template name for formatted exports (PDF/DOCX)"
    )
    
    @field_validator('content_ids')
    @classmethod
    def validate_content_ids(cls, v: List[str]) -> List[str]:
        """Validate content IDs are not empty strings."""
        for content_id in v:
            if not content_id.strip():
                raise ValueError("Content IDs cannot be empty strings")
        return v


class ExportJob(BaseModel):
    """Model representing an export job."""
    
    id: str = Field(
        ...,
        description="Unique export job identifier"
    )
    user_id: str = Field(
        ...,
        description="User who requested the export"
    )
    status: ExportStatus = Field(
        default=ExportStatus.PENDING,
        description="Current export status"
    )
    format: ExportFormat = Field(
        ...,
        description="Export format"
    )
    content_count: int = Field(
        ...,
        ge=0,
        description="Number of content items to export"
    )
    file_size: Optional[int] = Field(
        default=None,
        description="Export file size in bytes"
    )
    download_url: Optional[str] = Field(
        default=None,
        description="Secure download URL (when completed)"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Download URL expiration time"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if export failed"
    )
    progress: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Export progress percentage"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Export job creation time"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update time"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Export completion time"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional export metadata"
    )


class ExportJobCreate(BaseModel):
    """Model for creating an export job."""
    
    user_id: str
    format: ExportFormat
    content_ids: List[str]
    options: Optional[Dict[str, Any]] = None


class ExportJobUpdate(BaseModel):
    """Model for updating an export job."""
    
    status: Optional[ExportStatus] = None
    progress: Optional[float] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None


class ExportJobResponse(BaseModel):
    """Response model for export job."""
    
    job: ExportJob
    message: str = Field(
        default="Export job created successfully",
        description="Response message"
    )


class ExportJobList(BaseModel):
    """Model for listing export jobs."""
    
    jobs: List[ExportJob]
    total: int
    page: int = 1
    page_size: int = 20
    total_pages: int


class ExportHistory(BaseModel):
    """Model for user's export history."""
    
    exports: List[ExportJob]
    total_exports: int
    total_size: int = Field(
        description="Total size of all exports in bytes"
    )
    formats_used: Dict[str, int] = Field(
        description="Count of exports by format"
    )