"""
User data deletion models for GDPR compliance.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DeletionStatus(str, Enum):
    """Status of user data deletion request."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DeletionScope(str, Enum):
    """Scope of data deletion."""

    ALL_DATA = "all_data"
    CONTENT_ONLY = "content_only"
    METADATA_ONLY = "metadata_only"
    CUSTOM = "custom"


class DataCategory(str, Enum):
    """Categories of user data."""

    PROFILE = "profile"
    CONTENT = "content"
    USAGE_LOGS = "usage_logs"
    ANALYTICS = "analytics"
    CACHE = "cache"
    BACKUPS = "backups"
    AUDIT_LOGS = "audit_logs"


class DeletionReason(str, Enum):
    """Reason for data deletion request."""

    USER_REQUEST = "user_request"
    GDPR_RIGHT_TO_ERASURE = "gdpr_right_to_erasure"
    ACCOUNT_CLOSURE = "account_closure"
    DATA_RETENTION_POLICY = "data_retention_policy"
    ADMIN_REQUEST = "admin_request"
    LEGAL_REQUIREMENT = "legal_requirement"


class DataLocation(BaseModel):
    """Information about where user data is stored."""

    system: str = Field(..., description="System or service name")
    database: str = Field(..., description="Database or storage name")
    table_collection: str = Field(..., description="Table or collection name")
    identifier_field: str = Field(..., description="Field used to identify user data")
    data_types: List[DataCategory] = Field(..., description="Types of data stored")
    retention_period_days: Optional[int] = Field(None, description="Data retention period")
    encryption_status: bool = Field(default=False, description="Whether data is encrypted")
    backup_locations: List[str] = Field(default_factory=list, description="Backup storage locations")


class DeletionTask(BaseModel):
    """Individual deletion task for a specific data location."""

    task_id: str = Field(..., description="Unique task identifier")
    location: DataLocation = Field(..., description="Data location to clean")
    status: DeletionStatus = Field(default=DeletionStatus.PENDING)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    records_found: Optional[int] = None
    records_deleted: Optional[int] = None
    error_message: Optional[str] = None
    verification_checksum: Optional[str] = None


class UserDataDeletionRequest(BaseModel):
    """User data deletion request model."""

    request_id: str = Field(..., description="Unique deletion request ID")
    user_id: str = Field(..., description="User ID requesting deletion")
    email: Optional[str] = Field(None, description="User email for verification")
    scope: DeletionScope = Field(default=DeletionScope.ALL_DATA)
    reason: DeletionReason = Field(default=DeletionReason.USER_REQUEST)
    custom_categories: List[DataCategory] = Field(default_factory=list)
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    requested_by: str = Field(..., description="Who requested the deletion")

    # Processing information
    status: DeletionStatus = Field(default=DeletionStatus.PENDING)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Tasks and progress
    deletion_tasks: List[DeletionTask] = Field(default_factory=list)
    total_locations: int = Field(default=0)
    completed_locations: int = Field(default=0)

    # Verification and compliance
    verification_token: Optional[str] = None
    verification_expires_at: Optional[datetime] = None
    verification_completed: bool = Field(default=False)

    # Audit trail
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)

    # Compliance tracking
    compliance_notes: Optional[str] = None

    # Legal hold check
    legal_hold_check: bool = Field(default=False)
    legal_hold_reason: Optional[str] = None


class DeletionSummary(BaseModel):
    """Summary of deletion operation."""

    request_id: str
    user_id: str
    status: DeletionStatus
    total_records_deleted: int = 0
    categories_processed: List[DataCategory] = Field(default_factory=list)
    locations_processed: List[str] = Field(default_factory=list)
    duration_seconds: Optional[float] = None
    errors: List[str] = Field(default_factory=list)
    verification_hash: Optional[str] = None
    completion_certificate: Optional[str] = None


class DeletionConfiguration(BaseModel):
    """Configuration for user data deletion system."""

    enabled: bool = Field(default=True)
    require_verification: bool = Field(default=True)
    verification_timeout_hours: int = Field(default=24)
    auto_verify_admin_requests: bool = Field(default=False)
    legal_hold_check_required: bool = Field(default=True)
    retention_period_days: int = Field(default=30)
    hard_delete_after_days: int = Field(default=90)
    notification_email_template: str = Field(default="deletion_notification")
    backup_cleanup_enabled: bool = Field(default=True)
    audit_retention_years: int = Field(default=7)


class DeletionMetrics(BaseModel):
    """Metrics for user data deletion operations."""

    total_requests: int = 0
    completed_requests: int = 0
    failed_requests: int = 0
    pending_requests: int = 0
    average_completion_time_hours: float = 0.0
    total_records_deleted: int = 0
    categories_breakdown: Dict[str, int] = Field(default_factory=dict)
    error_breakdown: Dict[str, int] = Field(default_factory=dict)
    compliance_rate: float = 0.0


class DataInventory(BaseModel):
    """Inventory of user data across all systems."""

    user_id: str
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    locations: List[DataLocation] = Field(default_factory=list)
    total_records: int = 0
    estimated_size_mb: float = 0.0
    categories_found: List[DataCategory] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    discovery_errors: List[str] = Field(default_factory=list)


class DeletionSearchCriteria(BaseModel):
    """Search criteria for deletion requests."""

    user_id: Optional[str] = None
    email: Optional[str] = None
    status: Optional[DeletionStatus] = None
    reason: Optional[DeletionReason] = None
    requested_after: Optional[datetime] = None
    requested_before: Optional[datetime] = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    include_audit_trail: bool = Field(default=False)


class DeletionVerificationRequest(BaseModel):
    """Request to verify user data deletion."""

    request_id: str
    verification_token: str
    user_confirmation: bool = Field(default=True)
    additional_notes: Optional[str] = None


class DeletionCancellationRequest(BaseModel):
    """Request to cancel pending deletion."""

    request_id: str
    reason: str
    cancelled_by: str
    force_cancel: bool = Field(default=False)


class GDPRComplianceReport(BaseModel):
    """GDPR compliance report for deletion operations."""

    report_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    period_start: datetime
    period_end: datetime
    total_deletion_requests: int = 0
    completed_within_30_days: int = 0
    compliance_percentage: float = 0.0
    average_completion_days: float = 0.0
    failed_requests_details: List[Dict[str, Any]] = Field(default_factory=list)
    legal_basis_breakdown: Dict[str, int] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
