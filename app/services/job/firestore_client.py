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

# Import pooled functions from firestore_pool
from app.utils.firestore_pool import (
    get_firestore_pool,
    get_document_from_firestore as pooled_get_document,
    create_or_update_document_in_firestore as pooled_create_or_update,
    update_document_field_in_firestore as pooled_update_field,
)


@monitor_query('firestore')
async def get_document_from_firestore(
    document_id: str, collection_name: str = "jobs"
) -> Optional[Dict[str, Any]]:
    """Fetches a document from Firestore by its ID from the given collection."""
    logger.debug(
        f"Fetching document '{document_id}' from Firestore collection '{collection_name}'."
    )
    # Use pooled function
    result = await pooled_get_document(document_id, collection_name)
    if result:
        logger.info(
            f"Document '{document_id}' found in Firestore collection '{collection_name}'."
        )
    else:
        logger.warning(
            f"Document '{document_id}' not found in Firestore collection '{collection_name}'."
        )
    return result


@monitor_query('firestore')
async def create_or_update_document_in_firestore(
    document_id: str, data: Dict[str, Any], collection_name: str = "jobs"
) -> None:
    """Creates or updates a document in Firestore in the given collection."""
    logger.info(
        f"Creating/Updating document '{document_id}' in Firestore collection '{collection_name}' with data: {data}"
    )
    # Use pooled function
    await pooled_create_or_update(document_id, data, collection_name)
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
    logger.info(
        f"Updating document '{document_id}' field '{field_path}' to '{value}' in Firestore collection '{collection_name}'."
    )
    # Use pooled function
    await pooled_update_field(document_id, field_path, value, collection_name)
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
    pool = await get_firestore_pool()
    
    # Build filters
    filters = [("status", "==", status)] if status else None
    
    # Use pooled query function
    results = await pool.query_documents(
        collection=collection_name,
        filters=filters,
        order_by="created_at",
        limit=limit,
        offset=offset
    )

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
    pool = await get_firestore_pool()
    
    # Build filters
    filters = [("status", "==", status)] if status else None
    
    # Use pooled query function without limit to get all
    results = await pool.query_documents(
        collection=collection_name,
        filters=filters
    )
    
    count = len(results)
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
    pool = await get_firestore_pool()
    
    # Get all documents - we'll need to fetch them to count by status
    all_jobs = await pool.query_documents(
        collection=collection_name
    )
    
    status_counts = {}
    for job in all_jobs:
        status = job.get("status", "UNKNOWN")
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
    pool = await get_firestore_pool()
    
    # Check if document exists first
    doc = await pool.get_document(collection_name, document_id)
    
    if not doc:
        logger.warning(f"Document '{document_id}' not found for deletion")
        return False

    # Delete the document
    await pool.delete_document(collection_name, document_id)
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
    pool = await get_firestore_pool()
    
    # Convert to batch write operations format
    operations = []
    for update in updates:
        operations.append({
            "type": "update",
            "collection": collection_name,
            "document_id": update['document_id'],
            "data": update['fields']
        })
    
    # Use pooled batch write
    await pool.batch_write(operations)
    logger.info(f"Batch updated {len(updates)} documents in {collection_name}")


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
    pool = await get_firestore_pool()
    
    # Use pooled batch get
    results = await pool.batch_get_documents(collection_name, document_ids)
    
    logger.info(f"Batch fetched {len(document_ids)} documents from {collection_name}")
    return results
