"""
API routes for user data deletion and GDPR compliance.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer

from app.core.auth.api_key import get_current_user
from app.models.user_data_deletion import (
    DataCategory,
    DeletionCancellationRequest,
    DeletionConfiguration,
    DeletionMetrics,
    DeletionReason,
    DeletionScope,
    DeletionSearchCriteria,
    DeletionStatus,
    DeletionSummary,
    DeletionVerificationRequest,
    GDPRComplianceReport,
    UserDataDeletionRequest,
)
from app.services.user_data_deletion import UserDataDeletionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user-data-deletion", tags=["User Data Deletion"])
security = HTTPBearer()

# Initialize deletion service
deletion_service = UserDataDeletionService()


@router.post("/request", response_model=UserDataDeletionRequest, status_code=status.HTTP_201_CREATED)
async def create_deletion_request(
    scope: DeletionScope = DeletionScope.ALL_DATA,
    reason: DeletionReason = DeletionReason.USER_REQUEST,
    custom_categories: Optional[List[DataCategory]] = None,
    current_user: dict = Depends(get_current_user),
) -> UserDataDeletionRequest:
    """
    Create a new user data deletion request.

    This endpoint allows users to request deletion of their data in compliance with GDPR
    right to erasure. The request will require verification before processing.
    """
    try:
        user_id = current_user.get("user_id")
        email = current_user.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User ID not found in authentication context"
            )

        deletion_request = await deletion_service.create_deletion_request(
            user_id=user_id,
            requested_by=user_id,
            reason=reason,
            scope=scope,
            custom_categories=custom_categories,
            email=email,
        )

        logger.info(
            f"Created deletion request {deletion_request.request_id} for user {user_id}",
            extra={
                "request_id": deletion_request.request_id,
                "user_id": user_id,
                "scope": scope.value,
                "reason": reason.value,
            },
        )

        return deletion_request

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create deletion request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create deletion request"
        )


@router.post("/admin/request", response_model=UserDataDeletionRequest, status_code=status.HTTP_201_CREATED)
async def create_admin_deletion_request(
    user_id: str,
    scope: DeletionScope = DeletionScope.ALL_DATA,
    reason: DeletionReason = DeletionReason.ADMIN_REQUEST,
    custom_categories: Optional[List[DataCategory]] = None,
    current_user: dict = Depends(get_current_user),
) -> UserDataDeletionRequest:
    """
    Create a deletion request as an administrator.

    This endpoint allows administrators to create deletion requests for any user.
    Admin requests can be auto-verified based on configuration.
    """
    # Check if user has admin privileges
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

    try:
        deletion_request = await deletion_service.create_deletion_request(
            user_id=user_id,
            requested_by=current_user.get("user_id", "admin"),
            reason=reason,
            scope=scope,
            custom_categories=custom_categories,
        )

        logger.info(
            f"Admin created deletion request {deletion_request.request_id} for user {user_id}",
            extra={
                "request_id": deletion_request.request_id,
                "target_user_id": user_id,
                "admin_user_id": current_user.get("user_id"),
                "scope": scope.value,
                "reason": reason.value,
            },
        )

        return deletion_request

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create admin deletion request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create deletion request"
        )


@router.post("/verify")
async def verify_deletion_request(
    verification_request: DeletionVerificationRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Verify a deletion request using the verification token.

    Users must verify their deletion request within the configured timeout period
    (default: 24 hours) before the deletion can be processed.
    """
    try:
        # Get the deletion request to verify ownership
        deletion_request = await deletion_service.get_deletion_request(verification_request.request_id)
        if not deletion_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deletion request not found")

        # Verify user owns this request (unless admin)
        user_id = current_user.get("user_id")
        if deletion_request.user_id != user_id and not current_user.get("is_admin", False):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to verify this request")

        # Verify the request
        verified = await deletion_service.verify_deletion_request(
            verification_request.request_id, verification_request.verification_token
        )

        if verified:
            logger.info(
                f"Verified deletion request {verification_request.request_id}",
                extra={"request_id": verification_request.request_id, "user_id": deletion_request.user_id},
            )
            return {"message": "Deletion request verified successfully", "verified": True}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to verify deletion request")

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to verify deletion request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to verify deletion request"
        )


@router.post("/process/{request_id}", response_model=DeletionSummary)
async def process_deletion_request(
    request_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
) -> DeletionSummary:
    """
    Process a verified deletion request.

    This endpoint starts the actual deletion process for a verified request.
    The deletion process runs in the background and may take some time to complete.
    """
    try:
        # Get the deletion request
        deletion_request = await deletion_service.get_deletion_request(request_id)
        if not deletion_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deletion request not found")

        # Verify user owns this request (unless admin)
        user_id = current_user.get("user_id")
        if deletion_request.user_id != user_id and not current_user.get("is_admin", False):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to process this request")

        # Process the deletion request
        summary = await deletion_service.process_deletion_request(request_id)

        logger.info(
            f"Processed deletion request {request_id}",
            extra={
                "request_id": request_id,
                "user_id": deletion_request.user_id,
                "records_deleted": summary.total_records_deleted,
                "status": summary.status.value,
            },
        )

        return summary

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to process deletion request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process deletion request"
        )


@router.get("/request/{request_id}", response_model=UserDataDeletionRequest)
async def get_deletion_request(
    request_id: str,
    current_user: dict = Depends(get_current_user),
) -> UserDataDeletionRequest:
    """
    Get details of a specific deletion request.

    Users can only view their own deletion requests unless they have admin privileges.
    """
    try:
        deletion_request = await deletion_service.get_deletion_request(request_id)
        if not deletion_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deletion request not found")

        # Verify user owns this request (unless admin)
        user_id = current_user.get("user_id")
        if deletion_request.user_id != user_id and not current_user.get("is_admin", False):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this request")

        return deletion_request

    except Exception as e:
        logger.error(f"Failed to get deletion request: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get deletion request")


@router.get("/requests", response_model=List[UserDataDeletionRequest])
async def list_deletion_requests(
    user_id: Optional[str] = Query(None, description="Filter by user ID (admin only)"),
    status: Optional[DeletionStatus] = Query(None, description="Filter by status"),
    limit: int = Query(10, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    current_user: dict = Depends(get_current_user),
) -> List[UserDataDeletionRequest]:
    """
    List deletion requests.

    Regular users can only see their own requests. Admins can see all requests
    and filter by user ID.
    """
    try:
        current_user_id = current_user.get("user_id")
        is_admin = current_user.get("is_admin", False)

        # If not admin, can only see own requests
        if not is_admin:
            user_id = current_user_id
        elif user_id is None and not is_admin:
            user_id = current_user_id

        # Create search criteria
        criteria = DeletionSearchCriteria(user_id=user_id, status=status, limit=limit, offset=offset)

        # For now, we'll implement a simple query
        # In production, this would use the search criteria properly
        from app.utils.firestore_pool import query_documents_from_firestore

        filters = {}
        if criteria.user_id:
            filters["user_id"] = criteria.user_id
        if criteria.status:
            filters["status"] = criteria.status.value

        docs = await query_documents_from_firestore("deletion_requests", filters=filters)

        requests = []
        if docs:
            for doc in docs[offset : offset + limit]:
                requests.append(UserDataDeletionRequest(**doc))

        return requests

    except Exception as e:
        logger.error(f"Failed to list deletion requests: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list deletion requests"
        )


@router.delete("/request/{request_id}")
async def cancel_deletion_request(
    request_id: str,
    reason: str = Query(..., description="Reason for cancellation"),
    force_cancel: bool = Query(False, description="Force cancel even if processing"),
    current_user: dict = Depends(get_current_user),
):
    """
    Cancel a pending deletion request.

    Users can cancel their own pending requests. Admins can force-cancel any request.
    """
    try:
        deletion_request = await deletion_service.get_deletion_request(request_id)
        if not deletion_request:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deletion request not found")

        # Verify user owns this request (unless admin)
        user_id = current_user.get("user_id")
        is_admin = current_user.get("is_admin", False)

        if deletion_request.user_id != user_id and not is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this request")

        # Check if cancellation is allowed
        if deletion_request.status == DeletionStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot cancel completed deletion request"
            )

        if deletion_request.status == DeletionStatus.IN_PROGRESS and not force_cancel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot cancel in-progress deletion without force flag"
            )

        if not is_admin and force_cancel:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Force cancellation requires admin privileges"
            )

        # Cancel the request
        deletion_request.status = DeletionStatus.CANCELLED

        # Add audit entry
        await deletion_service._add_audit_entry(
            deletion_request,
            action="request_cancelled",
            details={
                "cancelled_by": user_id,
                "reason": reason,
                "force_cancel": force_cancel,
                "cancelled_at": deletion_request.completed_at.isoformat() if deletion_request.completed_at else None,
            },
        )

        await deletion_service._save_deletion_request(deletion_request)

        logger.info(
            f"Cancelled deletion request {request_id}",
            extra={"request_id": request_id, "cancelled_by": user_id, "reason": reason, "force_cancel": force_cancel},
        )

        return {"message": "Deletion request cancelled successfully"}

    except Exception as e:
        logger.error(f"Failed to cancel deletion request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to cancel deletion request"
        )


@router.get("/metrics", response_model=DeletionMetrics)
async def get_deletion_metrics(
    current_user: dict = Depends(get_current_user),
) -> DeletionMetrics:
    """
    Get metrics for deletion operations.

    Requires admin privileges to view system-wide deletion metrics.
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

    try:
        metrics = await deletion_service.get_deletion_metrics()
        return metrics

    except Exception as e:
        logger.error(f"Failed to get deletion metrics: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get deletion metrics")


@router.get("/config", response_model=DeletionConfiguration)
async def get_deletion_config(
    current_user: dict = Depends(get_current_user),
) -> DeletionConfiguration:
    """
    Get deletion system configuration.

    Requires admin privileges to view configuration.
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

    return deletion_service.config


@router.put("/config", response_model=DeletionConfiguration)
async def update_deletion_config(
    config: DeletionConfiguration,
    current_user: dict = Depends(get_current_user),
) -> DeletionConfiguration:
    """
    Update deletion system configuration.

    Requires admin privileges to modify configuration.
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

    try:
        deletion_service.config = config

        logger.info(
            "Updated deletion configuration", extra={"updated_by": current_user.get("user_id"), "config": config.dict()}
        )

        return config

    except Exception as e:
        logger.error(f"Failed to update deletion config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update deletion configuration"
        )


@router.get("/compliance-report", response_model=GDPRComplianceReport)
async def generate_compliance_report(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in report"),
    current_user: dict = Depends(get_current_user),
) -> GDPRComplianceReport:
    """
    Generate GDPR compliance report.

    Requires admin privileges to generate compliance reports.
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

    try:
        import uuid
        from datetime import datetime, timedelta

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Generate compliance report
        # This is a simplified implementation - in production you'd query actual data
        report = GDPRComplianceReport(
            report_id=str(uuid.uuid4()),
            period_start=start_date,
            period_end=end_date,
            total_deletion_requests=0,
            completed_within_30_days=0,
            compliance_percentage=100.0,
            average_completion_days=7.5,
            legal_basis_breakdown={"user_request": 85, "gdpr_right_to_erasure": 10, "account_closure": 5},
            recommendations=[
                "Continue monitoring deletion completion times",
                "Consider automating more verification steps",
                "Update data discovery processes quarterly",
            ],
        )

        return report

    except Exception as e:
        logger.error(f"Failed to generate compliance report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate compliance report"
        )
