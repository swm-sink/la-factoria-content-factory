"""Firestore client for interacting with the jobs collection."""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from google.cloud.firestore import (  # type: ignore # Use the async Firestore client
    AsyncClient,
)

from app.core.config.settings import get_settings
from app.middleware.query_monitor import monitor_query

# Import Pydantic models for Job data later if needed for type hinting or validation here
# from app.models.pydantic.job import Job, JobStatus

logger = logging.getLogger(__name__)
settings = get_settings()

# Global client instance, initialized once
_db_client: Optional[AsyncClient] = None


def get_firestore_client() -> AsyncClient:
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

            _db_client = AsyncClient(project=project_id if project_id else None)
            logger.info(
                f"Firestore AsyncClient initialized for project: {project_id or 'default (emulator?)'}"
            )
        except Exception as e:
            logger.error(
                f"Failed to initialize Firestore AsyncClient: {e}", exc_info=True
            )
            raise  # Re-raise to prevent app startup if DB connection is critical
    return _db_client


@monitor_query('firestore')
async def get_document_from_firestore(
    document_id: str, collection_name: str = "jobs"
) -> Optional[Dict[str, Any]]:
    """Fetches a document from Firestore by its ID from the given collection."""
    client = get_firestore_client()
    logger.debug(
        f"Fetching document '{document_id}' from Firestore collection '{collection_name}'."
    )
    doc_ref = client.collection(collection_name).document(document_id)
    doc = await doc_ref.get()
    if doc.exists:
        logger.info(
            f"Document '{document_id}' found in Firestore collection '{collection_name}'."
        )
        return doc.to_dict()
    logger.warning(
        f"Document '{document_id}' not found in Firestore collection '{collection_name}'."
    )
    return None


@monitor_query('firestore')
async def create_or_update_document_in_firestore(
    document_id: str, data: Dict[str, Any], collection_name: str = "jobs"
) -> None:
    """Creates or updates a document in Firestore in the given collection."""
    client = get_firestore_client()
    logger.info(
        f"Creating/Updating document '{document_id}' in Firestore collection '{collection_name}' with data: {data}"
    )
    await client.collection(collection_name).document(document_id).set(data, merge=True)
    logger.info(
        f"Document '{document_id}' created/updated in Firestore collection '{collection_name}'."
    )


@monitor_query('firestore')
async def update_document_field_in_firestore(
    document_id: str, field_path: str, value: Any, collection_name: str = "jobs"
) -> None:
    """Updates a specific field or nested field in a document using dot notation.
    Example: field_path = "status", value = "COMPLETED"
             field_path = "results.final_url", value = "http://..."
    """
    client = get_firestore_client()
    logger.info(
        f"Updating document '{document_id}' field '{field_path}' to '{value}' in Firestore collection '{collection_name}'."
    )
    doc_ref = client.collection(collection_name).document(document_id)
    await doc_ref.update({field_path: value})
    logger.info(
        f"Document '{document_id}' field '{field_path}' updated in Firestore collection '{collection_name}'."
    )


# Backward compatibility aliases
get_job_from_firestore = get_document_from_firestore
create_or_update_job_in_firestore = create_or_update_document_in_firestore
update_job_field_in_firestore = update_document_field_in_firestore


@monitor_query('firestore')
async def query_jobs_by_status(
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    collection_name: str = "jobs",
) -> List[Dict[str, Any]]:
    """Query jobs by status with pagination support.

    Args:
        status: Optional status filter (e.g., 'PENDING', 'PROCESSING')
        limit: Number of documents to return
        offset: Number of documents to skip
        collection_name: Firestore collection name

    Returns:
        List of job documents
    """
    client = get_firestore_client()
    query = client.collection(collection_name)

    if status:
        query = query.where("status", "==", status)

    # Add ordering for consistent pagination
    query = query.order_by("created_at", direction="DESCENDING")

    # Apply pagination
    query = query.offset(offset).limit(limit)

    # Execute query
    docs = await query.get()

    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id  # Include document ID
        results.append(data)

    logger.info(
        f"Found {len(results)} jobs with status={status}, offset={offset}, limit={limit}"
    )
    return results


@monitor_query('firestore')
async def count_jobs_by_status(
    status: Optional[str] = None, collection_name: str = "jobs"
) -> int:
    """Count jobs by status.

    Args:
        status: Optional status filter
        collection_name: Firestore collection name

    Returns:
        Count of matching documents
    """
    client = get_firestore_client()
    query = client.collection(collection_name)

    if status:
        query = query.where("status", "==", status)

    # For counting, we can use a more efficient approach
    # by selecting only the document ID
    query = query.select([])

    count = 0
    async for _ in query.stream():
        count += 1

    logger.info(f"Counted {count} jobs with status={status}")
    return count


@monitor_query('firestore')
async def get_all_job_statuses(collection_name: str = "jobs") -> Dict[str, int]:
    """Get count of jobs grouped by status.

    This is a more efficient implementation that gets all statuses in one query.

    Args:
        collection_name: Firestore collection name

    Returns:
        Dictionary mapping status to count
    """
    client = get_firestore_client()

    # Get all documents but only select status field for efficiency
    query = client.collection(collection_name).select(["status"])

    status_counts = {}
    async for doc in query.stream():
        data = doc.to_dict()
        status = data.get("status", "UNKNOWN")
        status_counts[status] = status_counts.get(status, 0) + 1

    logger.info(f"Job status counts: {status_counts}")
    return status_counts


@monitor_query('firestore')
async def delete_job_from_firestore(
    document_id: str, collection_name: str = "jobs"
) -> bool:
    """Delete a job document from Firestore.

    Args:
        document_id: ID of the document to delete
        collection_name: Firestore collection name

    Returns:
        True if document was deleted, False if not found
    """
    client = get_firestore_client()

    # Check if document exists first
    doc_ref = client.collection(collection_name).document(document_id)
    doc = await doc_ref.get()

    if not doc.exists:
        logger.warning(f"Document '{document_id}' not found for deletion")
        return False

    # Delete the document
    await doc_ref.delete()
    logger.info(f"Document '{document_id}' deleted from collection '{collection_name}'")
    return True


@monitor_query('firestore')
async def batch_update_documents(
    updates: List[Dict[str, Any]], collection_name: str = "jobs"
) -> None:
    """
    Batch update multiple documents in a single operation.
    
    Args:
        updates: List of updates, each containing 'document_id' and 'fields' to update
        collection_name: Firestore collection name
    """
    client = get_firestore_client()
    
    # Process in batches of 500 (Firestore limit)
    batch_size = 500
    for i in range(0, len(updates), batch_size):
        batch = client.batch()
        batch_updates = updates[i:i + batch_size]
        
        for update in batch_updates:
            doc_id = update['document_id']
            fields = update['fields']
            doc_ref = client.collection(collection_name).document(doc_id)
            batch.update(doc_ref, fields)
            
        # Commit the batch
        await batch.commit()
        logger.info(f"Batch updated {len(batch_updates)} documents in {collection_name}")


@monitor_query('firestore')
async def batch_get_documents(
    document_ids: List[str], collection_name: str = "jobs"
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Batch get multiple documents in a single operation.
    
    Args:
        document_ids: List of document IDs to fetch
        collection_name: Firestore collection name
        
    Returns:
        Dictionary mapping document ID to document data (None if not found)
    """
    client = get_firestore_client()
    results = {}
    
    # Get all documents in parallel
    tasks = []
    for doc_id in document_ids:
        doc_ref = client.collection(collection_name).document(doc_id)
        tasks.append(doc_ref.get())
        
    docs = await asyncio.gather(*tasks, return_exceptions=True)
    
    for doc_id, doc in zip(document_ids, docs):
        if isinstance(doc, Exception):
            logger.error(f"Failed to get document {doc_id}: {doc}")
            results[doc_id] = None
        elif doc.exists:
            results[doc_id] = doc.to_dict()
        else:
            results[doc_id] = None
            
    logger.info(f"Batch fetched {len(document_ids)} documents from {collection_name}")
    return results
