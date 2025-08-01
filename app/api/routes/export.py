"""
Export API routes for content export functionality.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user
from app.models.export import ExportJob, ExportJobList, ExportJobResponse, ExportRequest, ExportStatus
from app.models.pydantic.user import User
from app.schemas.export import (
    BulkExportRequestSchema,
    ExportJobResponseSchema,
    ExportProgressSchema,
    ExportRequestSchema,
)
from app.services.export_manager import ExportManager
from app.services.job.firestore_client import (
    create_or_update_job_in_firestore,
    get_job_from_firestore,
    query_jobs_by_user,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/export", tags=["export"])

# Initialize export manager
export_manager = ExportManager()


@router.post("/", response_model=ExportJobResponseSchema)
async def create_export(
    request: ExportRequestSchema, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)
) -> ExportJobResponseSchema:
    """
    Create a new export job for content.

    This endpoint creates an asynchronous export job that will process
    the requested content and generate the export file in the specified format.
    """
    logger.info(f"Creating export job for user {current_user.id} with format {request.format}")

    # Create export job
    job_id = str(uuid4())
    export_job = ExportJob(
        id=job_id,
        user_id=current_user.id,
        status=ExportStatus.PENDING,
        format=request.format,
        content_count=len(request.content_ids),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        metadata={
            "include_metadata": request.include_metadata,
            "include_quality_metrics": request.include_quality_metrics,
            "filters": request.filters,
        },
    )

    # Save job to database
    job_data = export_job.model_dump()
    await create_or_update_job_in_firestore("export_jobs", job_id, job_data)

    # Queue background task
    background_tasks.add_task(
        export_manager.process_export_job,
        job_id=job_id,
        user_id=current_user.id,
        content_ids=request.content_ids,
        format=request.format,
        options={
            "include_metadata": request.include_metadata,
            "include_quality_metrics": request.include_quality_metrics,
            "filters": request.filters,
        },
    )

    return ExportJobResponseSchema(
        job_id=job_id,
        status=export_job.status,
        format=export_job.format,
        progress=0.0,
        download_url=None,
        expires_at=None,
        message="Export job created successfully. Processing will begin shortly.",
    )


@router.get("/jobs/{job_id}", response_model=ExportJobResponseSchema)
async def get_export_job(job_id: str, current_user: User = Depends(get_current_user)) -> ExportJobResponseSchema:
    """
    Get the status of an export job.

    Returns the current status, progress, and download URL (if completed)
    for the specified export job.
    """
    # Get job from database
    job_data = await get_job_from_firestore("export_jobs", job_id)

    if not job_data:
        raise HTTPException(status_code=404, detail="Export job not found")

    # Verify user owns this job
    if job_data.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    export_job = ExportJob(**job_data)

    # Prepare response
    return ExportJobResponseSchema(
        job_id=export_job.id,
        status=export_job.status,
        format=export_job.format,
        progress=export_job.progress,
        download_url=export_job.download_url,
        expires_at=export_job.expires_at,
        message=export_job.error_message or f"Export job is {export_job.status.value}",
    )


@router.get("/jobs/{job_id}/download")
async def download_export(job_id: str, current_user: User = Depends(get_current_user)):
    """
    Download the exported file.

    Returns the exported file as a streaming response. The file must be
    ready (export job completed) and the download URL must not be expired.
    """
    # Get job from database
    job_data = await get_job_from_firestore("export_jobs", job_id)

    if not job_data:
        raise HTTPException(status_code=404, detail="Export job not found")

    # Verify user owns this job
    if job_data.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    export_job = ExportJob(**job_data)

    # Check if export is completed
    if export_job.status != ExportStatus.COMPLETED:
        raise HTTPException(status_code=400, detail=f"Export is not ready. Current status: {export_job.status.value}")

    # Check if download URL is expired
    if export_job.expires_at and export_job.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Download link has expired. Please create a new export.")

    # Get file from export manager
    try:
        file_content, content_type, filename = await export_manager.get_export_file(
            job_id=job_id, user_id=current_user.id
        )

        return StreamingResponse(
            file_content, media_type=content_type, headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Export file not found")
    except Exception as e:
        logger.error(f"Error downloading export: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading export file")


@router.get("/jobs", response_model=ExportJobList)
async def list_export_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[ExportStatus] = None,
    format: Optional[str] = None,
    current_user: User = Depends(get_current_user),
) -> ExportJobList:
    """
    List export jobs for the current user.

    Returns a paginated list of export jobs with optional filtering
    by status and format.
    """
    # Query jobs for user
    filters = {"user_id": current_user.id}
    if status:
        filters["status"] = status.value
    if format:
        filters["format"] = format

    jobs_data = await query_jobs_by_user(
        collection="export_jobs", user_id=current_user.id, filters=filters, page=page, page_size=page_size
    )

    # Convert to ExportJob models
    jobs = [ExportJob(**job_data) for job_data in jobs_data["jobs"]]

    return ExportJobList(
        jobs=jobs, total=jobs_data["total"], page=page, page_size=page_size, total_pages=jobs_data["total_pages"]
    )


@router.post("/bulk", response_model=ExportJobResponseSchema)
async def create_bulk_export(
    request: BulkExportRequestSchema, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)
) -> ExportJobResponseSchema:
    """
    Create a bulk export job based on filters.

    This endpoint allows exporting multiple content items based on
    filter criteria rather than explicit content IDs.
    """
    logger.info(f"Creating bulk export job for user {current_user.id}")

    # Query content IDs based on filters
    content_ids = await export_manager.query_content_ids(
        user_id=current_user.id, filters=request.filters, max_items=request.max_items
    )

    if not content_ids:
        raise HTTPException(status_code=404, detail="No content found matching the specified filters")

    # Create export job
    job_id = str(uuid4())
    export_job = ExportJob(
        id=job_id,
        user_id=current_user.id,
        status=ExportStatus.PENDING,
        format=request.format,
        content_count=len(content_ids),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        metadata={"bulk_export": True, "filters": request.filters, "max_items": request.max_items},
    )

    # Save job to database
    job_data = export_job.model_dump()
    await create_or_update_job_in_firestore("export_jobs", job_id, job_data)

    # Queue background task
    background_tasks.add_task(
        export_manager.process_export_job,
        job_id=job_id,
        user_id=current_user.id,
        content_ids=content_ids,
        format=request.format,
        options={"bulk_export": True},
    )

    return ExportJobResponseSchema(
        job_id=job_id,
        status=export_job.status,
        format=export_job.format,
        progress=0.0,
        download_url=None,
        expires_at=None,
        message=f"Bulk export job created for {len(content_ids)} items. Processing will begin shortly.",
    )


@router.delete("/jobs/{job_id}")
async def cancel_export_job(job_id: str, current_user: User = Depends(get_current_user)):
    """
    Cancel an export job.

    This will cancel a pending or processing export job and clean up
    any associated resources.
    """
    # Get job from database
    job_data = await get_job_from_firestore("export_jobs", job_id)

    if not job_data:
        raise HTTPException(status_code=404, detail="Export job not found")

    # Verify user owns this job
    if job_data.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    export_job = ExportJob(**job_data)

    # Check if job can be cancelled
    if export_job.status in [ExportStatus.COMPLETED, ExportStatus.FAILED]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel job with status: {export_job.status.value}")

    # Cancel the job
    await export_manager.cancel_export_job(job_id=job_id, user_id=current_user.id)

    return {"message": "Export job cancelled successfully"}


@router.get("/formats")
async def get_export_formats():
    """
    Get available export formats.

    Returns a list of supported export formats with their descriptions.
    """
    return {
        "formats": [
            {
                "format": "json",
                "description": "JavaScript Object Notation - structured data format",
                "mime_type": "application/json",
                "extension": ".json",
            },
            {
                "format": "csv",
                "description": "Comma-Separated Values - tabular data format",
                "mime_type": "text/csv",
                "extension": ".csv",
            },
            {
                "format": "pdf",
                "description": "Portable Document Format - formatted document",
                "mime_type": "application/pdf",
                "extension": ".pdf",
            },
            {
                "format": "docx",
                "description": "Microsoft Word Document - editable document",
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "extension": ".docx",
            },
            {
                "format": "txt",
                "description": "Plain Text - simple text format",
                "mime_type": "text/plain",
                "extension": ".txt",
            },
        ]
    }
