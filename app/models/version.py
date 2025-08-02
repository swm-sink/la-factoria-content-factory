"""
Version data models for content versioning system.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChangeType(str, Enum):
    """Type of version change."""

    MAJOR = "major"  # Breaking changes, complete restructure
    MINOR = "minor"  # New features, sections added
    PATCH = "patch"  # Bug fixes, small edits
    AUTO = "auto"  # Automatically determined


class VersionStatus(str, Enum):
    """Status of a version."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ContentLockStatus(str, Enum):
    """Status of content lock."""

    LOCKED = "locked"
    UNLOCKED = "unlocked"
    EXPIRED = "expired"


class Author(BaseModel):
    """Author information for a version."""

    user_id: str
    name: str
    email: str


class ChangeSummary(BaseModel):
    """Summary of changes in a version."""

    sections_added: int = 0
    sections_modified: int = 0
    sections_removed: int = 0
    learning_objectives_changed: bool = False
    total_changes: int = 0
    change_percentage: float = 0.0


class VersionMetadata(BaseModel):
    """Metadata for a version."""

    tags: List[str] = Field(default_factory=list)
    is_draft: bool = False
    is_published: bool = True
    change_summary: ChangeSummary
    review_status: Optional[str] = None
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None


class VersionStatistics(BaseModel):
    """Statistics for a version."""

    content_size: int
    diff_size: int
    changes_count: int
    compression_ratio: float = 0.0


class ContentVersion(BaseModel):
    """Complete content version model."""

    version_id: str
    content_id: str
    user_id: str
    version_number: str  # Semantic version (e.g., "1.2.3")
    parent_version: Optional[str] = None
    branch_name: str = "main"
    created_at: datetime
    change_type: ChangeType
    change_description: str
    author: Author
    metadata: VersionMetadata
    content_snapshot: Dict[str, Any]  # Full content or delta
    statistics: VersionStatistics
    is_delta: bool = False  # Whether content_snapshot is a delta or full snapshot


class ContentLock(BaseModel):
    """Content lock information."""

    lock_id: str
    content_id: str
    user_id: str
    locked_at: datetime
    expires_at: datetime
    status: ContentLockStatus
    lock_reason: Optional[str] = None
    force_released_by: Optional[str] = None
    force_released_at: Optional[datetime] = None


class VersionComparison(BaseModel):
    """Comparison between two versions."""

    version_1: str
    version_2: str
    compared_at: datetime
    differences: Dict[str, Any]
    similarity_score: float
    change_summary: ChangeSummary
    conflict_regions: List[Dict[str, Any]] = Field(default_factory=list)


class BranchInfo(BaseModel):
    """Information about a content branch."""

    branch_name: str
    base_version: str
    created_by: str
    created_at: datetime
    last_updated: datetime
    is_active: bool = True
    is_merged: bool = False
    merged_into: Optional[str] = None
    merge_date: Optional[datetime] = None
    version_count: int = 0


class MergeRequest(BaseModel):
    """Request to merge branches."""

    source_branch: str
    target_branch: str = "main"
    merge_strategy: str = "auto"  # auto, manual, theirs, ours
    conflict_resolution: Optional[Dict[str, Any]] = None
    merge_description: str


class VersionHistoryEntry(BaseModel):
    """Entry in version history."""

    version_id: str
    version_number: str
    created_at: datetime
    author: Author
    change_type: ChangeType
    change_description: str
    branch_name: str
    is_merge_commit: bool = False


class VersionSearchCriteria(BaseModel):
    """Criteria for searching versions."""

    content_id: Optional[str] = None
    user_id: Optional[str] = None
    branch_name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    change_types: List[ChangeType] = Field(default_factory=list)
    status: Optional[VersionStatus] = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
