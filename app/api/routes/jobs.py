"""
API routes for managing asynchronous content generation jobs.

This module provides endpoints for creating, monitoring, and managing
asynchronous content generation jobs.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.core.schemas.job import Job, JobCreate, JobList, JobStatus, JobUpdate
from app.services.job_manager import JobManager, get_job_manager
from app.api.routes.content import ContentRequest

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=Job, status_code=201)
async def create_job(
    content_request: ContentRequest,
    job_manager: JobManager = Depends(get_job_manager),
) -> Job:
    """
    Create a new content generation job.
    The request body should match the ContentRequest schema.
    
    Args:
        content_request: Content generation request data, conforming to ContentRequest schema.
        job_manager: Job manager service
        
    Returns:
        Created job instance
    """
    return await job_manager.create_job(content_request)


@router.get("", response_model=JobList)
async def list_jobs(
    status: Optional[JobStatus] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    job_manager: JobManager = Depends(get_job_manager),
) -> JobList:
    """
    List all jobs with optional filtering and pagination.
    
    Args:
        status: Optional status filter
        page: Page number (1-based)
        page_size: Number of items per page
        job_manager: Job manager service
        
    Returns:
        Paginated list of jobs
    """
    return await job_manager.list_jobs(status, page, page_size)


@router.get("/{job_id}", response_model=Job)
async def get_job(
    job_id: UUID,
    job_manager: JobManager = Depends(get_job_manager),
) -> Job:
    """
    Get a specific job by ID.
    
    Args:
        job_id: Job identifier
        job_manager: Job manager service
        
    Returns:
        Job instance
        
    Raises:
        HTTPException: If job not found
    """
    job = await job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/{job_id}", response_model=Job)
async def update_job(
    job_id: UUID,
    job_update: JobUpdate,
    job_manager: JobManager = Depends(get_job_manager),
) -> Job:
    """
    Update a job's status, progress, or metadata.
    
    Args:
        job_id: Job identifier
        job_update: Job update data
        job_manager: Job manager service
        
    Returns:
        Updated job instance
        
    Raises:
        HTTPException: If job not found or update invalid
    """
    job = await job_manager.update_job(job_id, job_update)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/{job_id}", status_code=204)
async def delete_job(
    job_id: UUID,
    job_manager: JobManager = Depends(get_job_manager),
) -> None:
    """
    Delete a job.
    
    Args:
        job_id: Job identifier
        job_manager: Job manager service
        
    Raises:
        HTTPException: If job not found
    """
    if not await job_manager.delete_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return JSONResponse(status_code=204, content=None) 