"""
Job-related Pydantic models for asynchronous content generation.

This module defines the data structures used for tracking and managing
asynchronous content generation jobs.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Enumeration of possible job statuses."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobErrorCode(str, Enum):
    """Enumeration of specific job error codes."""

    # General Errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"  # Generic internal error
    JOB_PROCESSING_ERROR = "JOB_PROCESSING_ERROR"  # Error during job manager processing
    INVALID_REQUEST_METADATA = (
        "INVALID_REQUEST_METADATA"  # Job metadata (ContentRequest) validation failed
    )

    # Content Generation Service Errors
    CONTENT_GENERATION_FAILED = "CONTENT_GENERATION_FAILED"  # General failure in EnhancedMultiStepContentGenerationService
    TOPIC_DECOMPOSITION_FAILED = "TOPIC_DECOMPOSITION_FAILED"
    TOPIC_DECOMPOSITION_AI_ERROR = "TOPIC_DECOMPOSITION_AI_ERROR"
    TOPIC_DECOMPOSITION_PARSING_ERROR = "TOPIC_DECOMPOSITION_PARSING_ERROR"
    TOPIC_DECOMPOSITION_INVALID_FORMAT = "TOPIC_DECOMPOSITION_INVALID_FORMAT"

    SECTION_OUTLINE_GENERATION_FAILED = "SECTION_OUTLINE_GENERATION_FAILED"
    SECTION_OUTLINE_AI_ERROR = "SECTION_OUTLINE_AI_ERROR"
    SECTION_OUTLINE_PARSING_ERROR = "SECTION_OUTLINE_PARSING_ERROR"

    SECTION_CONTENT_GENERATION_FAILED = "SECTION_CONTENT_GENERATION_FAILED"
    SECTION_CONTENT_AI_ERROR = "SECTION_CONTENT_AI_ERROR"
    SECTION_CONTENT_PARSING_ERROR = "SECTION_CONTENT_PARSING_ERROR"
    SECTION_GENERATION_PARALLEL_TASK_FAILED = "SECTION_GENERATION_PARALLEL_TASK_FAILED"

    CONTENT_ASSEMBLY_FAILED = "CONTENT_ASSEMBLY_FAILED"
    CONTENT_ASSEMBLY_AI_ERROR = "CONTENT_ASSEMBLY_AI_ERROR"
    CONTENT_ASSEMBLY_PARSING_ERROR = "CONTENT_ASSEMBLY_PARSING_ERROR"

    QUALITY_EVALUATION_FAILED = "QUALITY_EVALUATION_FAILED"
    VERSIONING_FAILED = "VERSIONING_FAILED"
    CACHE_OPERATION_FAILED = "CACHE_OPERATION_FAILED"


class JobError(BaseModel):
    """Model for job error information."""

    code: JobErrorCode = Field(..., description="Specific error code identifier")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Union[str, int, float, bool]]] = Field(
        None, description="Additional error details"
    )


class JobProgress(BaseModel):
    """Model for tracking job progress."""

    current_step: str = Field(..., description="Current processing step")
    total_steps: int = Field(..., description="Total number of steps")
    completed_steps: int = Field(0, description="Number of completed steps")
    percentage: float = Field(0.0, description="Overall progress percentage")
    estimated_time_remaining: Optional[float] = Field(
        None, description="Estimated time remaining in seconds"
    )


class Job(BaseModel):
    """Model for a content generation job."""

    id: UUID = Field(default_factory=uuid4, description="Unique job identifier")
    status: JobStatus = Field(JobStatus.PENDING, description="Current job status")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Job creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    completed_at: Optional[datetime] = Field(
        None, description="Job completion timestamp"
    )
    error: Optional[JobError] = Field(
        None, description="Error information if job failed"
    )
    progress: Optional[JobProgress] = Field(None, description="Current job progress")
    result: Optional[Dict] = Field(None, description="Job result data")
    metadata: Dict[str, Union[str, int, float, bool]] = Field(
        default_factory=dict, description="Additional job metadata"
    )


class JobCreate(BaseModel):
    """Model for creating a new job."""

    metadata: Dict[str, Union[str, int, float, bool]] = Field(
        default_factory=dict, description="Initial job metadata"
    )


class JobUpdate(BaseModel):
    """Model for updating an existing job."""

    status: Optional[JobStatus] = Field(None, description="New job status")
    error: Optional[JobError] = Field(None, description="Error information")
    progress: Optional[JobProgress] = Field(None, description="Updated progress")
    result: Optional[Dict] = Field(None, description="Job result data")
    metadata: Optional[Dict[str, Union[str, int, float, bool]]] = Field(
        None, description="Updated metadata"
    )


class JobList(BaseModel):
    """Model for listing jobs."""

    jobs: List[Job] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total number of jobs")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of jobs per page")
    total_pages: int = Field(..., description="Total number of pages")
