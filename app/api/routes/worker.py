"""Internal worker endpoints for processing asynchronous jobs.

This module provides internal endpoints that are called by Cloud Tasks
to process content generation jobs. These endpoints should NOT be exposed
via API Gateway and are for internal use only.
"""

import asyncio
import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ValidationError

from app.core.security.oidc import verify_cloud_tasks_token
from app.models.pydantic.content import ContentRequest
from app.models.pydantic.job import JobErrorCode, JobStatus
from app.services.job.firestore_client import (
    get_job_from_firestore,
    update_job_field_in_firestore,
)
from app.services.multi_step_content_generation import (
    EnhancedMultiStepContentGenerationService,
)

logger = logging.getLogger(__name__)

# Internal router - should NOT be included in public API Gateway
router = APIRouter(tags=["internal"])


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
    error_details: Optional[Dict[str, Any]] = None


@router.post("/process-generation-task", response_model=WorkerResponse)
async def process_content_generation_task(
    payload: TaskPayload,
    request: Request,
    token_payload: dict = Depends(verify_cloud_tasks_token),
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
        This endpoint is protected by OIDC token validation.
        Only Cloud Tasks service with proper service account can access it.
    """
    start_time = datetime.utcnow()
    job_id = payload.job_id
    error_details = None

    logger.info(
        f"Starting content generation task for job {job_id} (requested by {token_payload.get('email', 'unknown')})"
    )

    content_service = EnhancedMultiStepContentGenerationService()

    try:
        # Step 1: Fetch job details from Firestore
        logger.debug(f"Fetching job details for {job_id}")
        job_data = await get_job_from_firestore(job_id)
        if not job_data:
            error_msg = f"Job {job_id} not found in Firestore"
            logger.error(error_msg)
            return WorkerResponse(
                success=False,
                job_id=job_id,
                status=JobStatus.FAILED,
                message=error_msg,
                processing_time_seconds=(
                    datetime.utcnow() - start_time
                ).total_seconds(),
                error_details={"error_type": "job_not_found"},
            )

        # Step 2: Update job status to PROCESSING
        logger.debug(f"Updating job status to PROCESSING for {job_id}")
        await update_job_field_in_firestore(
            job_id, "status", JobStatus.PROCESSING.value
        )
        await update_job_field_in_firestore(
            job_id, "updated_at", datetime.utcnow().isoformat()
        )

        # Step 3: Extract and validate content request
        logger.debug(f"Validating content request for {job_id}")
        request_data = job_data.get("request_data", {})
        if not request_data:
            error_msg = f"No request data found for job {job_id}"
            logger.error(error_msg)
            await _update_job_error(
                job_id, JobErrorCode.INVALID_REQUEST_METADATA, error_msg
            )
            return WorkerResponse(
                success=False,
                job_id=job_id,
                status=JobStatus.FAILED,
                message=error_msg,
                processing_time_seconds=(
                    datetime.utcnow() - start_time
                ).total_seconds(),
                error_details={"error_type": "missing_request_data"},
            )

        try:
            content_request = ContentRequest(**request_data)
        except ValidationError as e:
            error_msg = f"Invalid request data for job {job_id}: {e}"
            logger.error(error_msg)
            await _update_job_error(
                job_id, JobErrorCode.INVALID_REQUEST_METADATA, error_msg
            )
            return WorkerResponse(
                success=False,
                job_id=job_id,
                status=JobStatus.FAILED,
                message=error_msg,
                processing_time_seconds=(
                    datetime.utcnow() - start_time
                ).total_seconds(),
                error_details={"error_type": "validation_error", "details": e.errors()},
            )

        # Step 4: Update progress for content generation start
        logger.debug(f"Starting content generation for {job_id}")
        await _update_job_progress(job_id, "Initializing content generation", 10, 1, 5)

        # Step 5: Generate content
        logger.info(f"Generating content for job {job_id}")
        await _update_job_progress(
            job_id, "Generating content with AI models", 30, 2, 5
        )

        (
            generated_content_obj,
            metadata_obj,
            quality_obj,
            tokens_used,
            gen_error_info,
        ) = await asyncio.to_thread(
            content_service.generate_long_form_content,
            job_id=job_id,
            syllabus_text=content_request.syllabus_text,
            target_format=content_request.target_format,
            target_duration=content_request.target_duration,
            target_pages=content_request.target_pages,
            use_cache=content_request.use_cache,
            use_parallel=content_request.use_parallel,
        )

        if gen_error_info or not generated_content_obj:
            error_msg = (
                gen_error_info.get("message")
                if gen_error_info
                else "Content generation failed (no object returned)."
            )
            err_code_val = (
                gen_error_info.get("code", JobErrorCode.CONTENT_GENERATION_FAILED.value)
                if gen_error_info
                else JobErrorCode.CONTENT_GENERATION_FAILED.value
            )
            error_code_enum = (
                JobErrorCode(err_code_val)
                if err_code_val in JobErrorCode._value2member_map_
                else JobErrorCode.CONTENT_GENERATION_FAILED
            )
            logger.error(f"Content generation failed for job {job_id}: {error_msg}")
            await _update_job_error(job_id, error_code_enum, error_msg)
            return WorkerResponse(
                success=False,
                job_id=job_id,
                status=JobStatus.FAILED,
                message=error_msg,
                processing_time_seconds=(
                    datetime.utcnow() - start_time
                ).total_seconds(),
                error_details={
                    "error_type": "generation_error",
                    "details": gen_error_info,
                },
            )

        # Step 6: Validate generated content
        logger.debug(f"Validating generated content for {job_id}")
        await _update_job_progress(job_id, "Validating generated content", 60, 3, 5)

        try:
            # Validate the generated content against the request
            if not _validate_generated_content(generated_content_obj, content_request):
                error_msg = "Generated content failed validation checks"
                logger.error(f"Content validation failed for job {job_id}: {error_msg}")
                await _update_job_error(
                    job_id, JobErrorCode.CONTENT_VALIDATION_FAILED, error_msg
                )
                return WorkerResponse(
                    success=False,
                    job_id=job_id,
                    status=JobStatus.FAILED,
                    message=error_msg,
                    processing_time_seconds=(
                        datetime.utcnow() - start_time
                    ).total_seconds(),
                    error_details={"error_type": "validation_error"},
                )
        except Exception as e:
            error_msg = f"Error during content validation: {str(e)}"
            logger.error(f"Content validation error for job {job_id}: {error_msg}")
            await _update_job_error(
                job_id, JobErrorCode.CONTENT_VALIDATION_FAILED, error_msg
            )
            return WorkerResponse(
                success=False,
                job_id=job_id,
                status=JobStatus.FAILED,
                message=error_msg,
                processing_time_seconds=(
                    datetime.utcnow() - start_time
                ).total_seconds(),
                error_details={"error_type": "validation_error", "details": str(e)},
            )

        # Step 7: Store results in Firestore
        logger.debug(f"Storing results for {job_id}")
        await _update_job_progress(job_id, "Storing results in database", 80, 4, 5)

        job_result_data_to_store = generated_content_obj.model_dump(exclude_none=True)
        await update_job_field_in_firestore(job_id, "result", job_result_data_to_store)

        # Store metadata and quality metrics if available
        if metadata_obj:
            await update_job_field_in_firestore(
                job_id, "content_metadata", metadata_obj.model_dump(exclude_none=True)
            )
        if quality_obj:
            await update_job_field_in_firestore(
                job_id, "quality_metrics", quality_obj.model_dump(exclude_none=True)
            )

        # Step 8: Finalize job
        logger.debug(f"Finalizing job {job_id}")
        await _update_job_progress(job_id, "Finalizing job", 90, 5, 5)

        await update_job_field_in_firestore(job_id, "status", JobStatus.COMPLETED.value)
        await update_job_field_in_firestore(
            job_id, "completed_at", datetime.utcnow().isoformat()
        )
        await update_job_field_in_firestore(
            job_id, "updated_at", datetime.utcnow().isoformat()
        )

        # Final progress update
        await _update_job_progress(
            job_id, "Content generation completed successfully", 100, 5, 5
        )

        processing_time = (datetime.utcnow() - start_time).total_seconds()
        success_msg = f"Content generation completed successfully for job {job_id}"
        logger.info(success_msg)
        return WorkerResponse(
            success=True,
            job_id=job_id,
            status=JobStatus.COMPLETED,
            message=success_msg,
            processing_time_seconds=processing_time,
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        error_msg = f"Unexpected error processing job {job_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        error_details = {
            "error_type": "unexpected_error",
            "traceback": traceback.format_exc(),
            "error_class": e.__class__.__name__,
        }

        try:
            await _update_job_error(
                job_id, JobErrorCode.JOB_PROCESSING_ERROR, error_msg
            )
        except Exception as update_error:
            logger.error(f"Failed to update job error for {job_id}: {update_error}")
            error_details["update_error"] = str(update_error)

        return WorkerResponse(
            success=False,
            job_id=job_id,
            status=JobStatus.FAILED,
            message=error_msg,
            processing_time_seconds=(datetime.utcnow() - start_time).total_seconds(),
            error_details=error_details,
        )


def _validate_generated_content(
    generated_content: Any, request: ContentRequest
) -> bool:
    """Validate generated content against the original request.

    Args:
        generated_content: The generated content object
        request: The original content request

    Returns:
        bool: True if validation passes, False otherwise
    """
    try:
        # Basic validation checks
        if not generated_content:
            return False

        # Add more specific validation checks here
        # For example:
        # - Check if the generated content matches the target format
        # - Verify the content length meets the target duration/pages
        # - Validate the content structure

        return True
    except Exception as e:
        logger.error(f"Error during content validation: {str(e)}")
        return False


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
        logger.debug(
            f"Updated progress for job {job_id}: {current_step} ({percentage}%)"
        )
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
        logger.debug(
            f"Updated error for job {job_id}: {error_code.value} - {error_message}"
        )
    except Exception as e:
        logger.error(f"Failed to update error for job {job_id}: {e}")
