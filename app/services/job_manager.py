"""
Job manager service for handling content generation jobs.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from app.models.pydantic.content import ContentRequest
from app.models.pydantic.job import Job, JobList, JobStatus, JobUpdate

logger = logging.getLogger(__name__)


class JobManager:
    """Manages content generation jobs."""

    def __init__(self):
        """Initialize the job manager."""
        self.jobs: Dict[str, Job] = {}

    async def create_job(self, content_request: ContentRequest) -> Job:
        """
        Create a new job and enqueue it for processing.

        Args:
            content_request: The content generation request data.

        Returns:
            Created job instance
        """
        logger.info("Creating new content generation job")

        # Create job with unique ID
        job_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Create job data for Firestore
        job_data = {
            "id": job_id,
            "status": JobStatus.PENDING.value,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "completed_at": None,
            "error": None,
            "progress": {
                "current_step": "Job created, queuing for processing",
                "total_steps": 7,
                "completed_steps": 1,
                "percentage": 10.0,
            },
            "result": None,
            "request_data": content_request.model_dump(),  # Store request for worker
            "metadata": {
                "syllabus_length": len(content_request.syllabus_text),
                "target_format": content_request.target_format,
                "use_parallel": content_request.use_parallel,
                "use_cache": content_request.use_cache,
            },
        }

        try:
            # Store job in Firestore
            await create_or_update_job_in_firestore(
                job_id, job_data, self._collection_name
            )
            logger.info(f"Job {job_id} created in Firestore")

            # Enqueue job for processing via Cloud Tasks
            enqueue_success = await self._tasks_client.enqueue_content_generation_job(
                job_id
            )

            if enqueue_success:
                # Update job status to indicate it's queued
                await update_job_field_in_firestore(
                    job_id,
                    "progress.current_step",
                    "Queued for processing",
                    self._collection_name,
                )
                await update_job_field_in_firestore(
                    job_id, "progress.percentage", 15.0, self._collection_name
                )
                logger.info(f"Job {job_id} successfully enqueued for processing")
            else:
                # Failed to enqueue, update job with error
                error_data = {
                    "code": JobErrorCode.JOB_PROCESSING_ERROR.value,
                    "message": "Failed to enqueue job for processing",
                    "timestamp": datetime.utcnow().isoformat(),
                }
                await update_job_field_in_firestore(
                    job_id, "status", JobStatus.FAILED.value, self._collection_name
                )
                await update_job_field_in_firestore(
                    job_id, "error", error_data, self._collection_name
                )
                logger.error(f"Failed to enqueue job {job_id}")

            # Convert Firestore data to Job model
            job_data["id"] = UUID(job_id)
            job_data["created_at"] = now
            job_data["updated_at"] = now
            job_data["status"] = JobStatus(job_data["status"])

            if job_data["progress"]:
                job_data["progress"] = JobProgress(**job_data["progress"])

            job = Job(**job_data)
            return job

        except Exception as e:
            logger.error(f"Failed to create job: {e}", exc_info=True)
            raise RuntimeError(f"Failed to create job: {str(e)}")

    async def get_job(self, job_id: UUID) -> Optional[Job]:
        """
        Get a job by ID from Firestore.

        Args:
            job_id: Job identifier

        Returns:
            Job instance if found, None otherwise
        """
        try:
            job_data = await get_job_from_firestore(str(job_id), self._collection_name)
            if not job_data:
                return None

            # Convert Firestore data to Job model
            return self._firestore_to_job_model(job_data)

        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None

    async def list_jobs(
        self, status: Optional[JobStatus] = None, page: int = 1, page_size: int = 10
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
        try:
            # Convert page to offset (0-based)
            offset = (page - 1) * page_size

            # Convert JobStatus enum to string if provided
            status_str = status.value if status else None

            # Query jobs from Firestore
            job_docs = await query_jobs_by_status(
                status=status_str,
                limit=page_size,
                offset=offset,
                collection_name=self._collection_name,
            )

            # Get total count for pagination
            total = await count_jobs_by_status(
                status=status_str, collection_name=self._collection_name
            )

            # Convert Firestore documents to Job models
            jobs = []
            for doc in job_docs:
                try:
                    job = self._firestore_to_job_model(doc)
                    jobs.append(job)
                except Exception as e:
                    logger.error(f"Failed to convert job document to model: {e}")
                    continue

            # Calculate total pages
            total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

            logger.info(
                f"Listed {len(jobs)} jobs (page {page}/{total_pages}, total: {total})"
            )

            return JobList(
                jobs=jobs,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            )

        except Exception as e:
            logger.error(f"Failed to list jobs: {e}", exc_info=True)
            return JobList(
                jobs=[], total=0, page=page, page_size=page_size, total_pages=0
            )

    async def update_job(self, job_id: UUID, update: JobUpdate) -> Optional[Job]:
        """
        Update a job in Firestore.

        Args:
            job_id: Job identifier
            update: Job update data

        Returns:
            Updated job instance if found, None otherwise
        """
        try:
            # Check if job exists
            existing_job = await get_job_from_firestore(
                str(job_id), self._collection_name
            )
            if not existing_job:
                return None

            # Prepare update data
            update_data = update.model_dump(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow().isoformat()

            # Update each field in Firestore
            for field, value in update_data.items():
                if field == "status" and isinstance(value, JobStatus):
                    value = value.value
                elif field == "error" and isinstance(value, JobError):
                    value = value.model_dump()
                elif field == "progress" and isinstance(value, JobProgress):
                    value = value.model_dump()

                await update_job_field_in_firestore(
                    str(job_id), field, value, self._collection_name
                )

            # Get updated job
            updated_job_data = await get_job_from_firestore(
                str(job_id), self._collection_name
            )
            if updated_job_data:
                return self._firestore_to_job_model(updated_job_data)

            return None

        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {e}")
            return None

    async def delete_job(self, job_id: UUID) -> bool:
        """
        Delete a job from Firestore.

        Args:
            job_id: Job identifier

        Returns:
            True if job was found and deleted, False otherwise
        """
        try:
            # For MVP, we'll just mark as deleted rather than actually deleting
            # This preserves audit trail

            existing_job = await get_job_from_firestore(
                str(job_id), self._collection_name
            )
            if not existing_job:
                return False

            # Mark as deleted
            await update_job_field_in_firestore(
                str(job_id), "status", JobStatus.DELETED.value, self._collection_name
            )
            await update_job_field_in_firestore(
                str(job_id),
                "deleted_at",
                datetime.utcnow().isoformat(),
                self._collection_name,
            )

            logger.info(f"Job {job_id} marked as deleted")
            return True

        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False

    def _firestore_to_job_model(self, firestore_data: Dict) -> Job:
        """Convert Firestore data to Job model.

        Args:
            firestore_data: Raw data from Firestore

        Returns:
            Job model instance
        """
        # Convert string dates to datetime objects
        if "created_at" in firestore_data and isinstance(
            firestore_data["created_at"], str
        ):
            firestore_data["created_at"] = datetime.fromisoformat(
                firestore_data["created_at"]
            )
        if "updated_at" in firestore_data and isinstance(
            firestore_data["updated_at"], str
        ):
            firestore_data["updated_at"] = datetime.fromisoformat(
                firestore_data["updated_at"]
            )
        if "completed_at" in firestore_data and firestore_data["completed_at"]:
            firestore_data["completed_at"] = datetime.fromisoformat(
                firestore_data["completed_at"]
            )

        # Convert string ID to UUID
        if "id" in firestore_data and isinstance(firestore_data["id"], str):
            firestore_data["id"] = UUID(firestore_data["id"])

        # Convert status string to enum
        if "status" in firestore_data and isinstance(firestore_data["status"], str):
            firestore_data["status"] = JobStatus(firestore_data["status"])

        # Convert nested objects
        if "error" in firestore_data and firestore_data["error"]:
            firestore_data["error"] = JobError(**firestore_data["error"])

        if "progress" in firestore_data and firestore_data["progress"]:
            firestore_data["progress"] = JobProgress(**firestore_data["progress"])

        return Job(**firestore_data)

    async def get_job_statistics(self) -> Dict[str, int]:
        """Get job statistics.

        Returns:
            Dictionary with job counts by status
        """
        try:
            # Get all job status counts from Firestore
            status_counts = await get_all_job_statuses(self._collection_name)

            # Map status strings to lowercase for consistent output
            # and ensure all expected statuses are present
            statistics = {
                "total": sum(status_counts.values()),
                "pending": status_counts.get(JobStatus.PENDING.value, 0),
                "processing": status_counts.get(JobStatus.PROCESSING.value, 0),
                "completed": status_counts.get(JobStatus.COMPLETED.value, 0),
                "failed": status_counts.get(JobStatus.FAILED.value, 0),
                "deleted": status_counts.get(JobStatus.DELETED.value, 0),
                "cancelled": status_counts.get(JobStatus.CANCELLED.value, 0),
            }

            # Add any other statuses that might exist in the database
            for status, count in status_counts.items():
                if status not in [
                    JobStatus.PENDING.value,
                    JobStatus.PROCESSING.value,
                    JobStatus.COMPLETED.value,
                    JobStatus.FAILED.value,
                    JobStatus.DELETED.value,
                    JobStatus.CANCELLED.value,
                ]:
                    statistics[f"other_{status.lower()}"] = count

            logger.info(f"Job statistics: {statistics}")
            return statistics

        except Exception as e:
            logger.error(f"Failed to get job statistics: {e}", exc_info=True)
            return {
                "total": 0,
                "pending": 0,
                "processing": 0,
                "completed": 0,
                "failed": 0,
                "error": str(e),
            }


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
