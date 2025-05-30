"""Firestore client for interacting with the jobs collection."""

import logging
import os
from typing import Optional, Dict, Any, List
from google.cloud import firestore_async  # type: ignore # Handle potential import linting if type stubs not perfect

from app.core.config.settings import get_settings

# Import Pydantic models for Job data later if needed for type hinting or validation here
# from app.models.pydantic.job import Job, JobStatus

logger = logging.getLogger(__name__)
settings = get_settings()

# Global client instance, initialized once
_db_client: Optional[firestore_async.AsyncClient] = None


def get_firestore_client() -> firestore_async.AsyncClient:
    """Initializes and returns the Firestore AsyncClient.

    Ensures that the client is initialized only once.
    For local development against an emulator, set the FIRESTORE_EMULATOR_HOST environment variable.
    Example: FIRESTORE_EMULATOR_HOST=localhost:8686
    """
    global _db_client
    if _db_client is None:
        try:
            project_id = settings.gcp_project_id
            if not project_id and "FIRESTORE_EMULATOR_HOST" not in os.environ:
                logger.warning(
                    "GCP_PROJECT_ID is not set and FIRESTORE_EMULATOR_HOST is not set. Firestore client might not connect to the correct project."
                )

            _db_client = firestore_async.AsyncClient(
                project=project_id if project_id else None
            )
            logger.info(
                f"Firestore AsyncClient initialized for project: {project_id or 'default (emulator?)'}"
            )
        except Exception as e:
            logger.error(
                f"Failed to initialize Firestore AsyncClient: {e}", exc_info=True
            )
            raise  # Re-raise to prevent app startup if DB connection is critical
    return _db_client


async def get_job_from_firestore(
    job_id: str, collection_name: str = "jobs"
) -> Optional[Dict[str, Any]]:
    """Fetches a job document from Firestore by its ID."""
    client = get_firestore_client()
    logger.debug(
        f"Fetching job '{job_id}' from Firestore collection '{collection_name}'."
    )
    doc_ref = client.collection(collection_name).document(job_id)
    doc = await doc_ref.get()
    if doc.exists:
        logger.info(f"Job '{job_id}' found in Firestore.")
        return doc.to_dict()
    logger.warning(
        f"Job '{job_id}' not found in Firestore collection '{collection_name}'."
    )
    return None


async def create_or_update_job_in_firestore(
    job_id: str, job_data: Dict[str, Any], collection_name: str = "jobs"
) -> None:
    """Creates or updates a job document in Firestore."""
    client = get_firestore_client()
    logger.info(
        f"Creating/Updating job '{job_id}' in Firestore collection '{collection_name}' with data: {job_data}"
    )
    # Ensure complex objects like error/progress are serializable if they are Pydantic models passed in
    # For example, if job_data contains Pydantic models, they should be .model_dump()'d before this call.
    await client.collection(collection_name).document(job_id).set(
        job_data, merge=True
    )  # merge=True for updates
    logger.info(f"Job '{job_id}' created/updated in Firestore.")


async def update_job_field_in_firestore(
    job_id: str, field_path: str, value: Any, collection_name: str = "jobs"
) -> None:
    """Updates a specific field or nested field in a job document using dot notation.
    Example: field_path = "status", value = "COMPLETED"
             field_path = "results.final_url", value = "http://..."
    """
    client = get_firestore_client()
    logger.info(
        f"Updating job '{job_id}' field '{field_path}' to '{value}' in Firestore collection '{collection_name}'."
    )
    doc_ref = client.collection(collection_name).document(job_id)
    await doc_ref.update({field_path: value})
    logger.info(f"Job '{job_id}' field '{field_path}' updated in Firestore.")


# Add other specific CRUD operations as needed, e.g., for querying jobs by status, etc.
