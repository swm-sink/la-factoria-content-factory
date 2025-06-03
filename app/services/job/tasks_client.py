"""Cloud Tasks client for enqueuing asynchronous content generation jobs."""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from google.auth import compute_engine, default
from google.auth.transport import requests
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
        self.queue_name = settings.tasks_queue_name
        self.worker_base_url = settings.tasks_worker_service_url

        # Initialize credentials for OIDC token generation
        self._credentials = None
        self._auth_request = None

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

                # Initialize authentication components
                try:
                    self._credentials, _ = default()
                    self._auth_request = requests.Request()
                except Exception as auth_e:
                    logger.warning(f"Failed to initialize auth components: {auth_e}")

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

            # Construct the full URL
            if self.worker_base_url:
                task_url = f"{self.worker_base_url}{worker_endpoint}"
            else:
                # Default Cloud Run URL format
                service_name = (
                    "acpf-mvp-cr-apiserver"  # Adjust based on your service name
                )
                task_url = f"https://{service_name}-{self.project_id}.a.run.app{worker_endpoint}"

            # Create the task with OIDC token
            task = {
                "http_request": {
                    "http_method": tasks_v2.HttpMethod.POST,
                    "url": task_url,
                    "headers": {
                        "Content-Type": "application/json",
                    },
                    "body": json.dumps(task_payload).encode(),
                    "oidc_token": {
                        "service_account_email": self._get_service_account_email(),
                        "audience": task_url,
                    },
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

    def _get_service_account_email(self) -> str:
        """Get the service account email for OIDC token generation.

        Returns:
            Service account email for the Cloud Tasks to use
        """
        # First, check if a specific service account is configured
        tasks_service_account = os.getenv("CLOUD_TASKS_SERVICE_ACCOUNT")
        if tasks_service_account:
            return tasks_service_account

        # Otherwise, use the default compute service account
        try:
            # For Cloud Run, this will be the service account the Cloud Run service is running as
            if hasattr(compute_engine, "Credentials"):
                # Try to get the default service account
                project_number = (
                    self.project_id
                )  # This needs to be the project number, not ID
                return f"{project_number}-compute@developer.gserviceaccount.com"
        except Exception as e:
            logger.warning(f"Could not determine service account: {e}")

        # Fallback to a constructed service account email
        # You should set CLOUD_TASKS_SERVICE_ACCOUNT env var in production
        return f"cloud-tasks@{self.project_id}.iam.gserviceaccount.com"

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
