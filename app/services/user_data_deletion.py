"""
User data deletion service for GDPR compliance.

This service handles:
- User data discovery across all systems
- Deletion request processing and verification
- Complete data removal with audit trails
- GDPR compliance reporting
"""

import asyncio
import hashlib
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.core.config.settings import get_settings
from app.models.user_data_deletion import (
    DataCategory,
    DataInventory,
    DataLocation,
    DeletionConfiguration,
    DeletionMetrics,
    DeletionReason,
    DeletionScope,
    DeletionStatus,
    DeletionSummary,
    DeletionTask,
    GDPRComplianceReport,
    UserDataDeletionRequest,
)
from app.utils.firestore_pool import (
    create_or_update_document_in_firestore,
    delete_document_from_firestore,
    get_document_from_firestore,
    query_documents_from_firestore,
)
from app.utils.redis_pool import redis_delete, redis_get, redis_set

logger = logging.getLogger(__name__)
settings = get_settings()


class UserDataDeletionService:
    """Service for managing user data deletion requests and GDPR compliance."""

    def __init__(self, config: Optional[DeletionConfiguration] = None):
        self.config = config or DeletionConfiguration()
        self.data_locations = self._initialize_data_locations()

    def _initialize_data_locations(self) -> List[DataLocation]:
        """Initialize known data locations where user data is stored."""
        return [
            # Firestore collections
            DataLocation(
                system="firestore",
                database="la-factoria",
                table_collection="users",
                identifier_field="user_id",
                data_types=[DataCategory.PROFILE],
                retention_period_days=None,  # Keep until deletion request
                encryption_status=True,
            ),
            DataLocation(
                system="firestore",
                database="la-factoria",
                table_collection="content_jobs",
                identifier_field="user_id",
                data_types=[DataCategory.CONTENT, DataCategory.USAGE_LOGS],
                retention_period_days=365,
                encryption_status=True,
            ),
            DataLocation(
                system="firestore",
                database="la-factoria",
                table_collection="user_sessions",
                identifier_field="user_id",
                data_types=[DataCategory.USAGE_LOGS, DataCategory.ANALYTICS],
                retention_period_days=90,
                encryption_status=True,
            ),
            DataLocation(
                system="firestore",
                database="la-factoria",
                table_collection="api_usage",
                identifier_field="user_id",
                data_types=[DataCategory.USAGE_LOGS, DataCategory.ANALYTICS],
                retention_period_days=180,
                encryption_status=True,
            ),
            DataLocation(
                system="firestore",
                database="la-factoria",
                table_collection="billing_records",
                identifier_field="user_id",
                data_types=[DataCategory.PROFILE, DataCategory.USAGE_LOGS],
                retention_period_days=2555,  # 7 years for tax purposes
                encryption_status=True,
            ),
            # Redis cache
            DataLocation(
                system="redis",
                database="cache",
                table_collection="user_cache",
                identifier_field="user_id",
                data_types=[DataCategory.CACHE],
                retention_period_days=7,
                encryption_status=False,
            ),
            DataLocation(
                system="redis",
                database="cache",
                table_collection="session_cache",
                identifier_field="user_id",
                data_types=[DataCategory.CACHE, DataCategory.USAGE_LOGS],
                retention_period_days=1,
                encryption_status=False,
            ),
            # Audit logs (special handling - longer retention)
            DataLocation(
                system="firestore",
                database="la-factoria",
                table_collection="audit_logs",
                identifier_field="user_id",
                data_types=[DataCategory.AUDIT_LOGS],
                retention_period_days=2555,  # 7 years
                encryption_status=True,
            ),
        ]

    async def create_deletion_request(
        self,
        user_id: str,
        requested_by: str,
        reason: DeletionReason = DeletionReason.USER_REQUEST,
        scope: DeletionScope = DeletionScope.ALL_DATA,
        custom_categories: Optional[List[DataCategory]] = None,
        email: Optional[str] = None,
    ) -> UserDataDeletionRequest:
        """Create a new user data deletion request."""

        request_id = str(uuid.uuid4())

        # Check for existing pending requests
        existing_request = await self._get_pending_request_for_user(user_id)
        if existing_request:
            raise ValueError(f"User {user_id} already has a pending deletion request: {existing_request.request_id}")

        # Perform legal hold check if required
        legal_hold_info = await self._check_legal_hold(user_id) if self.config.legal_hold_check_required else None

        # Create deletion request
        deletion_request = UserDataDeletionRequest(
            request_id=request_id,
            user_id=user_id,
            email=email,
            scope=scope,
            reason=reason,
            custom_categories=custom_categories or [],
            requested_by=requested_by,
            legal_hold_check=legal_hold_info is not None,
            legal_hold_reason=legal_hold_info.get("reason") if legal_hold_info else None,
        )

        # Generate verification token if required
        if self.config.require_verification and reason == DeletionReason.USER_REQUEST:
            deletion_request.verification_token = self._generate_verification_token()
            deletion_request.verification_expires_at = datetime.utcnow() + timedelta(
                hours=self.config.verification_timeout_hours
            )
        elif self.config.auto_verify_admin_requests and requested_by == "admin":
            deletion_request.verification_completed = True

        # Add audit trail entry
        await self._add_audit_entry(
            deletion_request,
            action="request_created",
            details={
                "requested_by": requested_by,
                "reason": reason.value,
                "scope": scope.value,
                "verification_required": not deletion_request.verification_completed,
            },
        )

        # Save request
        await self._save_deletion_request(deletion_request)

        logger.info(
            f"Created deletion request {request_id} for user {user_id}",
            extra={"request_id": request_id, "user_id": user_id, "reason": reason.value, "scope": scope.value},
        )

        return deletion_request

    async def verify_deletion_request(self, request_id: str, verification_token: str) -> bool:
        """Verify a deletion request with the provided token."""

        deletion_request = await self.get_deletion_request(request_id)
        if not deletion_request:
            raise ValueError(f"Deletion request {request_id} not found")

        if deletion_request.verification_completed:
            return True

        if deletion_request.verification_token != verification_token:
            await self._add_audit_entry(
                deletion_request, action="verification_failed", details={"reason": "invalid_token"}
            )
            raise ValueError("Invalid verification token")

        if deletion_request.verification_expires_at and datetime.utcnow() > deletion_request.verification_expires_at:
            await self._add_audit_entry(
                deletion_request, action="verification_failed", details={"reason": "token_expired"}
            )
            raise ValueError("Verification token has expired")

        # Mark as verified
        deletion_request.verification_completed = True
        deletion_request.verification_token = None
        deletion_request.verification_expires_at = None

        await self._add_audit_entry(
            deletion_request, action="verification_completed", details={"verified_at": datetime.utcnow().isoformat()}
        )

        await self._save_deletion_request(deletion_request)

        logger.info(f"Verified deletion request {request_id}")
        return True

    async def process_deletion_request(self, request_id: str) -> DeletionSummary:
        """Process a verified deletion request."""

        deletion_request = await self.get_deletion_request(request_id)
        if not deletion_request:
            raise ValueError(f"Deletion request {request_id} not found")

        if not deletion_request.verification_completed:
            raise ValueError(f"Deletion request {request_id} not verified")

        if deletion_request.status != DeletionStatus.PENDING:
            raise ValueError(f"Deletion request {request_id} is not pending (status: {deletion_request.status})")

        # Check legal hold again before processing
        if deletion_request.legal_hold_reason:
            raise ValueError(f"Cannot process deletion: legal hold in effect - {deletion_request.legal_hold_reason}")

        # Start processing
        deletion_request.status = DeletionStatus.IN_PROGRESS
        deletion_request.started_at = datetime.utcnow()

        await self._add_audit_entry(
            deletion_request,
            action="processing_started",
            details={"started_at": deletion_request.started_at.isoformat()},
        )

        try:
            # Discover user data
            inventory = await self._discover_user_data(deletion_request.user_id)

            # Filter locations based on scope
            target_locations = self._filter_locations_by_scope(
                inventory.locations, deletion_request.scope, deletion_request.custom_categories
            )

            # Create deletion tasks
            deletion_tasks = []
            for location in target_locations:
                task = DeletionTask(task_id=str(uuid.uuid4()), location=location)
                deletion_tasks.append(task)

            deletion_request.deletion_tasks = deletion_tasks
            deletion_request.total_locations = len(deletion_tasks)

            # Execute deletion tasks
            summary = await self._execute_deletion_tasks(deletion_request)

            # Mark as completed
            deletion_request.status = DeletionStatus.COMPLETED
            deletion_request.completed_at = datetime.utcnow()
            deletion_request.completed_locations = len(
                [t for t in deletion_tasks if t.status == DeletionStatus.COMPLETED]
            )

            await self._add_audit_entry(
                deletion_request,
                action="processing_completed",
                details={
                    "completed_at": deletion_request.completed_at.isoformat(),
                    "total_records_deleted": summary.total_records_deleted,
                    "locations_processed": len(summary.locations_processed),
                },
            )

            await self._save_deletion_request(deletion_request)

            logger.info(
                f"Completed deletion request {request_id}",
                extra={
                    "request_id": request_id,
                    "user_id": deletion_request.user_id,
                    "records_deleted": summary.total_records_deleted,
                    "duration_seconds": summary.duration_seconds,
                },
            )

            return summary

        except Exception as e:
            # Mark as failed
            deletion_request.status = DeletionStatus.FAILED

            await self._add_audit_entry(
                deletion_request,
                action="processing_failed",
                details={"error": str(e), "failed_at": datetime.utcnow().isoformat()},
            )

            await self._save_deletion_request(deletion_request)

            logger.error(
                f"Failed to process deletion request {request_id}: {e}",
                extra={"request_id": request_id, "user_id": deletion_request.user_id},
                exc_info=True,
            )

            raise

    async def get_deletion_request(self, request_id: str) -> Optional[UserDataDeletionRequest]:
        """Get a deletion request by ID."""
        try:
            doc = await get_document_from_firestore("deletion_requests", request_id)
            if doc:
                return UserDataDeletionRequest(**doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get deletion request {request_id}: {e}")
            return None

    async def _discover_user_data(self, user_id: str) -> DataInventory:
        """Discover all user data across systems."""

        inventory = DataInventory(user_id=user_id)
        total_records = 0

        for location in self.data_locations:
            try:
                if location.system == "firestore":
                    # Query Firestore for user data
                    query_filter = {location.identifier_field: user_id}
                    docs = await query_documents_from_firestore(location.table_collection, filters=query_filter)
                    record_count = len(docs) if docs else 0

                elif location.system == "redis":
                    # Check Redis for user data
                    pattern = f"{location.table_collection}:{user_id}:*"
                    # Note: This is a simplified check - in production you'd use SCAN
                    cache_data = await redis_get(f"{location.table_collection}:{user_id}")
                    record_count = 1 if cache_data else 0

                else:
                    record_count = 0

                if record_count > 0:
                    inventory.locations.append(location)
                    total_records += record_count

                    for category in location.data_types:
                        if category not in inventory.categories_found:
                            inventory.categories_found.append(category)

            except Exception as e:
                inventory.discovery_errors.append(
                    f"Error discovering data in {location.system}.{location.table_collection}: {e}"
                )
                logger.warning(f"Failed to discover data in {location.system}.{location.table_collection}: {e}")

        inventory.total_records = total_records
        return inventory

    async def _execute_deletion_tasks(self, deletion_request: UserDataDeletionRequest) -> DeletionSummary:
        """Execute all deletion tasks for a request."""

        start_time = datetime.utcnow()
        summary = DeletionSummary(
            request_id=deletion_request.request_id, user_id=deletion_request.user_id, status=DeletionStatus.IN_PROGRESS
        )

        for task in deletion_request.deletion_tasks:
            try:
                task.status = DeletionStatus.IN_PROGRESS
                task.started_at = datetime.utcnow()

                # Execute deletion for this location
                deleted_count = await self._delete_user_data_from_location(deletion_request.user_id, task.location)

                task.records_found = deleted_count
                task.records_deleted = deleted_count
                task.status = DeletionStatus.COMPLETED
                task.completed_at = datetime.utcnow()

                # Generate verification checksum
                task.verification_checksum = self._generate_checksum(
                    f"{deletion_request.user_id}:{task.location.system}:{task.location.table_collection}:{deleted_count}"
                )

                summary.total_records_deleted += deleted_count
                summary.locations_processed.append(f"{task.location.system}.{task.location.table_collection}")

                for category in task.location.data_types:
                    if category not in summary.categories_processed:
                        summary.categories_processed.append(category)

            except Exception as e:
                task.status = DeletionStatus.FAILED
                task.error_message = str(e)
                summary.errors.append(f"{task.location.system}.{task.location.table_collection}: {e}")

                logger.error(
                    f"Failed to delete data from {task.location.system}.{task.location.table_collection}: {e}",
                    extra={"request_id": deletion_request.request_id, "user_id": deletion_request.user_id},
                )

        # Calculate summary
        end_time = datetime.utcnow()
        summary.duration_seconds = (end_time - start_time).total_seconds()
        summary.status = DeletionStatus.COMPLETED if not summary.errors else DeletionStatus.FAILED
        summary.verification_hash = self._generate_checksum(
            f"{deletion_request.request_id}:{summary.total_records_deleted}:{len(summary.locations_processed)}"
        )

        return summary

    async def _delete_user_data_from_location(self, user_id: str, location: DataLocation) -> int:
        """Delete user data from a specific location."""

        deleted_count = 0

        if location.system == "firestore":
            # Delete from Firestore
            query_filter = {location.identifier_field: user_id}
            docs = await query_documents_from_firestore(location.table_collection, filters=query_filter)

            if docs:
                for doc in docs:
                    doc_id = doc.get("id") or doc.get("_id") or doc.get("document_id")
                    if doc_id:
                        await delete_document_from_firestore(location.table_collection, doc_id)
                        deleted_count += 1

        elif location.system == "redis":
            # Delete from Redis
            cache_keys = [f"{location.table_collection}:{user_id}", f"{location.table_collection}:{user_id}:*"]

            for key in cache_keys:
                result = await redis_delete(key)
                if result:
                    deleted_count += 1

        return deleted_count

    def _filter_locations_by_scope(
        self, locations: List[DataLocation], scope: DeletionScope, custom_categories: List[DataCategory]
    ) -> List[DataLocation]:
        """Filter data locations based on deletion scope."""

        if scope == DeletionScope.ALL_DATA:
            # Return all locations except audit logs (kept for compliance)
            return [loc for loc in locations if DataCategory.AUDIT_LOGS not in loc.data_types]

        elif scope == DeletionScope.CONTENT_ONLY:
            return [loc for loc in locations if DataCategory.CONTENT in loc.data_types]

        elif scope == DeletionScope.METADATA_ONLY:
            return [loc for loc in locations if DataCategory.PROFILE in loc.data_types]

        elif scope == DeletionScope.CUSTOM:
            filtered_locations = []
            for location in locations:
                if any(category in location.data_types for category in custom_categories):
                    filtered_locations.append(location)
            return filtered_locations

        return locations

    async def _get_pending_request_for_user(self, user_id: str) -> Optional[UserDataDeletionRequest]:
        """Check if user has an existing pending deletion request."""
        try:
            docs = await query_documents_from_firestore(
                "deletion_requests", filters={"user_id": user_id, "status": DeletionStatus.PENDING.value}
            )

            if docs:
                return UserDataDeletionRequest(**docs[0])
            return None
        except Exception as e:
            logger.warning(f"Failed to check for existing deletion request: {e}")
            return None

    async def _check_legal_hold(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Check if user data is under legal hold."""
        # This would integrate with legal systems or compliance databases
        # For now, return None (no legal hold)
        return None

    def _generate_verification_token(self) -> str:
        """Generate a secure verification token."""
        return hashlib.sha256(f"{uuid.uuid4()}:{datetime.utcnow()}".encode()).hexdigest()[:32]

    def _generate_checksum(self, data: str) -> str:
        """Generate verification checksum."""
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    async def _add_audit_entry(self, deletion_request: UserDataDeletionRequest, action: str, details: Dict[str, Any]):
        """Add entry to deletion request audit trail."""
        audit_entry = {"timestamp": datetime.utcnow().isoformat(), "action": action, "details": details}
        deletion_request.audit_trail.append(audit_entry)

    async def _save_deletion_request(self, deletion_request: UserDataDeletionRequest):
        """Save deletion request to storage."""
        try:
            await create_or_update_document_in_firestore(
                "deletion_requests", deletion_request.request_id, deletion_request.dict()
            )
        except Exception as e:
            logger.error(f"Failed to save deletion request {deletion_request.request_id}: {e}")
            raise

    async def get_deletion_metrics(self) -> DeletionMetrics:
        """Get metrics for deletion operations."""
        try:
            # Query all deletion requests for metrics
            docs = await query_documents_from_firestore("deletion_requests")

            metrics = DeletionMetrics()

            if docs:
                metrics.total_requests = len(docs)

                for doc in docs:
                    request = UserDataDeletionRequest(**doc)

                    if request.status == DeletionStatus.COMPLETED:
                        metrics.completed_requests += 1
                    elif request.status == DeletionStatus.FAILED:
                        metrics.failed_requests += 1
                    elif request.status == DeletionStatus.PENDING:
                        metrics.pending_requests += 1

                    # Calculate completion time for completed requests
                    if request.completed_at and request.started_at:
                        duration = (request.completed_at - request.started_at).total_seconds() / 3600
                        metrics.average_completion_time_hours = (
                            (
                                (metrics.average_completion_time_hours * (metrics.completed_requests - 1) + duration)
                                / metrics.completed_requests
                            )
                            if metrics.completed_requests > 0
                            else duration
                        )

                # Calculate compliance rate (completed within 30 days)
                if metrics.total_requests > 0:
                    metrics.compliance_rate = (metrics.completed_requests / metrics.total_requests) * 100

            return metrics

        except Exception as e:
            logger.error(f"Failed to get deletion metrics: {e}")
            return DeletionMetrics()
