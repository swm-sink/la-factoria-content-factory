"""Internal worker endpoints for processing asynchronous jobs.

This module provides internal endpoints that are called by Cloud Tasks
to process content generation jobs. These endpoints should NOT be exposed
via API Gateway and are for internal use only.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from app.core.schemas.job import JobStatus, JobError, JobErrorCode, JobProgress
from app.services.job.firestore_client import (
    get_job_from_firestore,
    update_job_field_in_firestore,
    create_or_update_job_in_firestore,
)
from app.services.multi_step_content_generation import (
    EnhancedMultiStepContentGenerationService,
)
from app.services.content_validation import get_content_validation_service
from app.models.pydantic.content import ContentRequest, ContentResponse

logger = logging.getLogger(__name__)

# Internal router - should NOT be included in public API Gateway
router = APIRouter(prefix="/internal/v1", tags=["internal"])


class TaskPayload(BaseModel):
    """Model for Cloud Tasks payload."""

    job_id: str
    timestamp: str
    worker_endpoint: str


class WorkerResponse(BaseModel):
    """Model for worker response."""

    success: bool
    job_id: str
    status: JobStatus
    message: str
    processing_time_seconds: float


@router.post("/process-generation-task", response_model=WorkerResponse)
async def process_content_generation_task(
    payload: TaskPayload, request: Request
) -> WorkerResponse:
    """Process a content generation task from Cloud Tasks.

    This endpoint:
    1. Receives job_id from Cloud Tasks payload
    2. Fetches job details from Firestore
    3. Performs content generation
    4. Validates AI output with Pydantic models
    5. Updates job status and results in Firestore

    Args:
        payload: Task payload from Cloud Tasks
        request: FastAPI request object

    Returns:
        WorkerResponse with processing results

    Security:
        This endpoint should only be accessible by Cloud Tasks service.
        In production, validate OIDC token from Cloud Tasks.
    """
    start_time = datetime.utcnow()
    job_id = payload.job_id

    logger.info(f"Starting content generation task for job {job_id}")

    try:
        # Step 1: Fetch job details from Firestore
        job_data = await get_job_from_firestore(job_id)
        if not job_data:
            error_msg = f"Job {job_id} not found in Firestore"
            logger.error(error_msg)
            raise HTTPException(status_code=404, detail=error_msg)

        # Step 2: Update job status to PROCESSING
        await update_job_field_in_firestore(
            job_id, "status", JobStatus.PROCESSING.value
        )
        await update_job_field_in_firestore(
            job_id, "updated_at", datetime.utcnow().isoformat()
        )

        # Step 3: Extract and validate content request
        request_data = job_data.get("request_data", {})
        if not request_data:
            error_msg = f"No request data found for job {job_id}"
            logger.error(error_msg)
            await _update_job_error(
                job_id, JobErrorCode.INVALID_REQUEST_METADATA, error_msg
            )
            return _create_worker_response(
                False, job_id, JobStatus.FAILED, error_msg, start_time
            )

        try:
            content_request = ContentRequest(**request_data)
        except ValidationError as e:
            error_msg = f"Invalid request data for job {job_id}: {e}"
            logger.error(error_msg)
            await _update_job_error(
                job_id, JobErrorCode.INVALID_REQUEST_METADATA, error_msg
            )
            return _create_worker_response(
                False, job_id, JobStatus.FAILED, error_msg, start_time
            )

        # Step 4: Initialize content generation service
        content_service = EnhancedMultiStepContentGenerationService()
        validation_service = get_content_validation_service()

        # Step 5: Update progress for content generation start
        await _update_job_progress(
            job_id, "Generating content with AI models", 25, 4, 7
        )

        # Step 6: Generate content
        logger.info(f"Generating content for job {job_id}")
        generated_tuple = content_service.generate_long_form_content(
            content_request.syllabus_text,
            content_request.target_format,
            target_duration=content_request.target_duration,
            target_pages=content_request.target_pages,
            use_cache=content_request.use_cache,
            use_parallel=content_request.use_parallel,
        )

        generated_data, status_code, headers = generated_tuple

        if status_code != 200:
            error_msg = generated_data.get("error", "Content generation failed")
            logger.error(f"Content generation failed for job {job_id}: {error_msg}")
            await _update_job_error(
                job_id, JobErrorCode.CONTENT_GENERATION_FAILED, error_msg
            )
            return _create_worker_response(
                False, job_id, JobStatus.FAILED, error_msg, start_time
            )

        # Step 7: Validate AI output with Pydantic models
        await _update_job_progress(
            job_id, "Validating and processing generated content", 75, 6, 7
        )

        logger.info(f"Validating AI output for job {job_id}")
        validation_success, validation_result = (
            validation_service.validate_raw_ai_output(
                generated_data,
                job_id=job_id,
                ai_model="gemini-1.5-flash",  # TODO: Get from actual model used
                tokens_used=None,  # TODO: Extract from generation response
            )
        )

        if not validation_success:
            error_msg = f"Content validation failed: {validation_result.error if hasattr(validation_result, 'error') else 'Unknown validation error'}"
            logger.error(f"Content validation failed for job {job_id}: {error_msg}")
            await _update_job_error(
                job_id, JobErrorCode.CONTENT_GENERATION_FAILED, error_msg
            )
            return _create_worker_response(
                False, job_id, JobStatus.FAILED, error_msg, start_time
            )

        # Step 8: Store results in Firestore
        await _update_job_progress(job_id, "Storing results", 95, 7, 7)

        # Store the validated ContentResponse
        content_response = validation_result
        results_data = content_response.model_dump()

        await update_job_field_in_firestore(job_id, "result", results_data)
        await update_job_field_in_firestore(job_id, "status", JobStatus.COMPLETED.value)
        await update_job_field_in_firestore(
            job_id, "completed_at", datetime.utcnow().isoformat()
        )
        await update_job_field_in_firestore(
            job_id, "updated_at", datetime.utcnow().isoformat()
        )

        # Final progress update
        await _update_job_progress(
            job_id, "Content generation completed successfully", 100, 7, 7
        )

        processing_time = (datetime.utcnow() - start_time).total_seconds()
        success_msg = f"Content generation completed successfully for job {job_id}"
        logger.info(success_msg)

        return _create_worker_response(
            True, job_id, JobStatus.COMPLETED, success_msg, start_time
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error processing job {job_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)

        try:
            await _update_job_error(
                job_id, JobErrorCode.JOB_PROCESSING_ERROR, error_msg
            )
        except Exception as update_error:
            logger.error(f"Failed to update job error for {job_id}: {update_error}")

        return _create_worker_response(
            False, job_id, JobStatus.FAILED, error_msg, start_time
        )


@router.get("/health", response_model=Dict[str, Any])
async def worker_health_check() -> Dict[str, Any]:
    """Health check endpoint for worker services.

    Returns:
        Health status of worker services
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "worker_version": "1.0.0",
        "services": {
            "content_generation": "available",
            "content_validation": "available",
            "firestore": "available",
        },
    }


# Helper functions


async def _update_job_progress(
    job_id: str,
    current_step: str,
    percentage: float,
    completed_steps: int,
    total_steps: int,
) -> None:
    """Update job progress in Firestore.

    Args:
        job_id: Job identifier
        current_step: Description of current step
        percentage: Completion percentage
        completed_steps: Number of completed steps
        total_steps: Total number of steps
    """
    try:
        progress_data = {
            "current_step": current_step,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "percentage": percentage,
            "updated_at": datetime.utcnow().isoformat(),
        }
        await update_job_field_in_firestore(job_id, "progress", progress_data)
    except Exception as e:
        logger.warning(f"Failed to update progress for job {job_id}: {e}")


async def _update_job_error(
    job_id: str, error_code: JobErrorCode, error_message: str
) -> None:
    """Update job with error information.

    Args:
        job_id: Job identifier
        error_code: Error code
        error_message: Error message
    """
    try:
        error_data = {
            "code": error_code.value,
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await update_job_field_in_firestore(job_id, "error", error_data)
        await update_job_field_in_firestore(job_id, "status", JobStatus.FAILED.value)
        await update_job_field_in_firestore(
            job_id, "completed_at", datetime.utcnow().isoformat()
        )
        await update_job_field_in_firestore(
            job_id, "updated_at", datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Failed to update error for job {job_id}: {e}")


def _create_worker_response(
    success: bool, job_id: str, status: JobStatus, message: str, start_time: datetime
) -> WorkerResponse:
    """Create a worker response object.

    Args:
        success: Whether the operation was successful
        job_id: Job identifier
        status: Final job status
        message: Result message
        start_time: When processing started

    Returns:
        WorkerResponse object
    """
    processing_time = (datetime.utcnow() - start_time).total_seconds()
    return WorkerResponse(
        success=success,
        job_id=job_id,
        status=status,
        message=message,
        processing_time_seconds=processing_time,
    )
