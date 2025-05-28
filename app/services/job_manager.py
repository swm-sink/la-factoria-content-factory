"""
Job manager service for handling asynchronous content generation jobs.

This module provides the core functionality for managing job lifecycle,
including creation, monitoring, and cleanup of asynchronous jobs.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import UUID

from fastapi import Depends
from pydantic import ValidationError

from app.core.schemas.job import Job, JobCreate, JobList, JobStatus, JobUpdate, JobProgress, JobError, JobErrorCode
from app.core.config.settings import get_settings
from app.services.multi_step_content_generation import EnhancedMultiStepContentGenerationService
from app.api.routes.content import ContentRequest # Assuming ContentRequest is the input for the service


class JobManager:
    """Service for managing asynchronous content generation jobs."""
    
    def __init__(self):
        """Initialize the job manager."""
        self._jobs: Dict[UUID, Job] = {}
        self._settings = get_settings()
        self._content_service = EnhancedMultiStepContentGenerationService()
    
    async def create_job(self, job_creation_data: ContentRequest) -> Job:
        """
        Create a new job.
        
        Args:
            job_creation_data: The content generation request data.
            
        Returns:
            Created job instance
        """
        # Store the request data directly in metadata for the processor to use
        job = Job(metadata=job_creation_data.model_dump()) 
        self._jobs[job.id] = job
        
        # Start job processing in background
        asyncio.create_task(self._process_job(job.id))
        
        return job
    
    async def get_job(self, job_id: UUID) -> Optional[Job]:
        """
        Get a job by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job instance if found, None otherwise
        """
        return self._jobs.get(job_id)
    
    async def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        page: int = 1,
        page_size: int = 10
    ) -> JobList:
        """
        List jobs with optional filtering and pagination.
        
        Args:
            status: Optional status filter
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Paginated list of jobs
        """
        # Filter jobs by status if specified
        jobs = [
            job for job in self._jobs.values()
            if status is None or job.status == status
        ]
        
        # Calculate pagination
        total = len(jobs)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        total_pages = (total + page_size - 1) // page_size
        
        # Get page of jobs
        page_jobs = jobs[start_idx:end_idx]
        
        return JobList(
            jobs=page_jobs,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    async def update_job(self, job_id: UUID, update: JobUpdate) -> Optional[Job]:
        """
        Update a job.
        
        Args:
            job_id: Job identifier
            update: Job update data
            
        Returns:
            Updated job instance if found, None otherwise
        """
        job = self._jobs.get(job_id)
        if not job:
            return None
        
        # Update job fields
        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)
        
        job.updated_at = datetime.utcnow()
        return job
    
    async def delete_job(self, job_id: UUID) -> bool:
        """
        Delete a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if job was found and deleted, False otherwise
        """
        if job_id in self._jobs:
            del self._jobs[job_id]
            return True
        return False
    
    async def _process_job(self, job_id: UUID) -> None:
        """
        Process a job in the background.
        This involves calling the EnhancedMultiStepContentGenerationService.
        
        Args:
            job_id: Job identifier
        """
        job = self._jobs.get(job_id)
        if not job:
            # Log this scenario, though it shouldn't happen if create_job is the only entry point
            print(f"ERROR: Job {job_id} not found for processing.") # Replace with proper logging
            return
        
        try:
            job.status = JobStatus.PROCESSING
            job.updated_at = datetime.utcnow()
            
            # Define the stages of content generation with their approximate time distribution
            stages = [
                ("Initializing and Validating Request", 5),    # 5% - Initial setup and validation
                ("Checking Content Cache", 10),                # 10% - Cache lookup
                ("Analyzing Syllabus and Topic Decomposition", 15),  # 15% - Topic analysis
                ("Generating Content Sections", 40),           # 40% - Main content generation
                ("Assembling and Structuring Content", 15),    # 15% - Content assembly
                ("Quality Assessment and Versioning", 10),     # 10% - Quality checks
                ("Finalizing and Storing Results", 5)          # 5% - Final steps
            ]
            
            total_stages = len(stages)
            current_percentage = 0
            
            def _update_job_progress(stage_name: str, stage_percentage: int):
                nonlocal current_percentage
                current_percentage += stage_percentage
                job.progress = JobProgress(
                    current_step=stage_name,
                    total_steps=total_stages,
                    completed_steps=len([s for s, _ in stages if s == stage_name or stages.index((s, _)) < stages.index((stage_name, stage_percentage))]),
                    percentage=current_percentage
                )
                self._jobs[job.id] = job # Ensure update is reflected in the in-memory store

            # Stage 1: Initialize and validate
            _update_job_progress(*stages[0])
            request_data = ContentRequest(**job.metadata)

            # Stage 2: Cache check
            _update_job_progress(*stages[1])

            # Stage 3: Topic decomposition
            _update_job_progress(*stages[2])

            # Stage 4: Content generation (main processing)
            _update_job_progress(*stages[3])

            # Call the content generation service
            generated_content_tuple = await asyncio.to_thread(
                self._content_service.generate_long_form_content,
                request_data.syllabus_text,
                request_data.target_format,
                target_duration=request_data.target_duration,
                target_pages=request_data.target_pages,
                use_cache=request_data.use_cache,
                use_parallel=request_data.use_parallel
            )
            
            generated_data, status_code, _ = generated_content_tuple

            if status_code == 200:
                # Stage 5: Assembly
                _update_job_progress(*stages[4])
                
                # Stage 6: Quality assessment
                _update_job_progress(*stages[5])
                
                # Stage 7: Finalization
                _update_job_progress(*stages[6])
                
                job.status = JobStatus.COMPLETED
                job.result = generated_data
            else:
                job.status = JobStatus.FAILED
                job.error = JobError(
                    code=JobErrorCode.CONTENT_GENERATION_FAILED,
                    message=generated_data.get("error", "Unknown error from content service")
                )
                # Update progress to reflect failure at the current stage
                failed_step = job.progress.current_step if job.progress else stages[3][0]
                job.progress = JobProgress(
                    current_step=f"Failed during {failed_step}: {generated_data.get('error', 'Unknown')}",
                    total_steps=total_stages,
                    completed_steps=job.progress.completed_steps if job.progress else 3,
                    percentage=current_percentage
                )

        except ValidationError as ve:
            job.status = JobStatus.FAILED
            job.error = JobError(code=JobErrorCode.INVALID_REQUEST_METADATA, message=str(ve))
            job.progress = JobProgress(
                current_step="Failed during request validation",
                total_steps=total_stages,
                completed_steps=0,
                percentage=0.0
            )
        except Exception as e:
            # Log the full exception
            print(f"ERROR: Exception during job {job_id} processing: {e}") # Replace with proper logging
            job.status = JobStatus.FAILED
            job.error = JobError(code=JobErrorCode.JOB_PROCESSING_ERROR, message=str(e))
            if job.progress:
                job.progress.current_step = f"Failed during {job.progress.current_step}"
            else:
                job.progress = JobProgress(
                    current_step="Failed during initialization",
                    total_steps=total_stages,
                    completed_steps=0,
                    percentage=0.0
                )
        
        finally:
            job.completed_at = datetime.utcnow() # Mark completion/failure time
            job.updated_at = datetime.utcnow()
            self._jobs[job.id] = job # Ensure final state is saved


# Dependency for getting job manager instance
_job_manager: Optional[JobManager] = None

async def get_job_manager() -> JobManager:
    """
    Get or create job manager instance.
    
    Returns:
        Job manager instance
    """
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
    return _job_manager 