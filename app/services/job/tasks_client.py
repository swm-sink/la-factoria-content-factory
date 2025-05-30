"""Cloud Tasks client for enqueuing asynchronous content generation jobs."""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

from app.core.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CloudTasksClient:
    """Client for managing Cloud Tasks queues and enqueuing jobs."""

    def __init__(self):
        """Initialize the Cloud Tasks client."""
        self.project_id = settings.gcp_project_id
        self.location = settings.gcp_location
        self.queue_name = "content-generation-queue"

        # Initialize the client only if we have project info
        self.client = None
        if self.project_id:
            try:
                self.client = tasks_v2.CloudTasksClient()
                self.queue_path = self.client.queue_path(
                    self.project_id, self.location, self.queue_name
                )
                logger.info(
                    f"Cloud Tasks client initialized for queue: {self.queue_path}"
                )
            except Exception as e:
                logger.error(f"Failed to initialize Cloud Tasks client: {e}")
                self.client = None
        else:
            logger.warning(
                "GCP_PROJECT_ID not set. Cloud Tasks client not initialized."
            )

    async def enqueue_content_generation_job(
        self,
        job_id: str,
        worker_endpoint: str = "/internal/v1/process-generation-task",
        delay_seconds: int = 0,
        retry_config: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Enqueue a content generation job to Cloud Tasks.

        Args:
            job_id: Unique job identifier
            worker_endpoint: Internal endpoint to call for processing
            delay_seconds: Delay before processing the task
            retry_config: Optional retry configuration

        Returns:
            True if task was successfully enqueued, False otherwise
        """
        if not self.client:
            logger.error("Cloud Tasks client not initialized. Cannot enqueue job.")
            return False

        try:
            # Create the task payload
            task_payload = {
                "job_id": job_id,
                "timestamp": datetime.utcnow().isoformat(),
                "worker_endpoint": worker_endpoint,
            }

            # Create the task
            task = {
                "http_request": {
                    "http_method": tasks_v2.HttpMethod.POST,
                    "url": f"https://{settings.gcp_project_id}.run.app{worker_endpoint}",
                    "headers": {
                        "Content-Type": "application/json",
                        # Add OIDC token for authentication to Cloud Run
                        "Authorization": (
                            "Bearer " + self._get_oidc_token()
                            if hasattr(self, "_get_oidc_token")
                            else ""
                        ),
                    },
                    "body": json.dumps(task_payload).encode(),
                }
            }

            # Add delay if specified
            if delay_seconds > 0:
                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(
                    datetime.utcnow() + timedelta(seconds=delay_seconds)
                )
                task["schedule_time"] = timestamp

            # Add retry configuration
            if retry_config:
                task["retry_config"] = retry_config
            else:
                # Default retry configuration
                task["retry_config"] = {
                    "max_attempts": 3,
                    "max_retry_duration": "600s",  # 10 minutes
                    "min_backoff": "10s",
                    "max_backoff": "300s",
                    "max_doublings": 3,
                }

            # Create the task
            response = self.client.create_task(parent=self.queue_path, task=task)

            logger.info(
                f"Successfully enqueued job {job_id}. Task name: {response.name}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to enqueue job {job_id}: {e}", exc_info=True)
            return False

    async def get_queue_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the Cloud Tasks queue.

        Returns:
            Queue information dictionary or None if error
        """
        if not self.client:
            logger.error("Cloud Tasks client not initialized.")
            return None

        try:
            queue = self.client.get_queue(name=self.queue_path)
            return {
                "name": queue.name,
                "state": queue.state.name,
                "purge_time": (
                    queue.purge_time.ToDatetime() if queue.purge_time else None
                ),
                "rate_limits": {
                    "max_dispatches_per_second": queue.rate_limits.max_dispatches_per_second,
                    "max_burst_size": queue.rate_limits.max_burst_size,
                    "max_concurrent_dispatches": queue.rate_limits.max_concurrent_dispatches,
                },
                "retry_config": {
                    "max_attempts": queue.retry_config.max_attempts,
                    "max_retry_duration": (
                        queue.retry_config.max_retry_duration.seconds
                        if queue.retry_config.max_retry_duration
                        else None
                    ),
                    "min_backoff": (
                        queue.retry_config.min_backoff.seconds
                        if queue.retry_config.min_backoff
                        else None
                    ),
                    "max_backoff": (
                        queue.retry_config.max_backoff.seconds
                        if queue.retry_config.max_backoff
                        else None
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Failed to get queue info: {e}")
            return None

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on Cloud Tasks client.

        Returns:
            Health check results
        """
        try:
            if not self.client:
                return {
                    "status": "unhealthy",
                    "error": "Cloud Tasks client not initialized",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # Try to get queue info as a health check
            queue_info = self.client.get_queue(name=self.queue_path)

            return {
                "status": "healthy",
                "queue_state": queue_info.state.name,
                "queue_name": self.queue_name,
                "project_id": self.project_id,
                "location": self.location,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Cloud Tasks health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Global client instance
_tasks_client: Optional[CloudTasksClient] = None


def get_cloud_tasks_client() -> CloudTasksClient:
    """Get or create the global Cloud Tasks client instance.

    Returns:
        CloudTasksClient instance
    """
    global _tasks_client
    if _tasks_client is None:
        _tasks_client = CloudTasksClient()
    return _tasks_client
