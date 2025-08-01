"""
Background tasks for search indexing.

This module handles asynchronous indexing of content for search functionality,
including initial indexing, updates, and maintenance tasks.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.core.config.settings import get_settings
from app.models.pydantic.job import JobStatus
from app.models.search import SearchIndex
from app.services.job.firestore_client import get_document_from_firestore, query_documents
from app.services.search import SearchBackend, SearchConfig, SimpleSearchBackend

logger = logging.getLogger(__name__)
settings = get_settings()


class SearchIndexingTasks:
    """Handles background search indexing tasks."""

    def __init__(self, search_backend: Optional[SearchBackend] = None):
        """Initialize indexing tasks."""
        if not search_backend:
            config = SearchConfig()
            search_backend = SimpleSearchBackend(config)
        self.search_backend = search_backend
        self._jobs_collection = "jobs"

    async def index_job_content(self, job_id: str) -> bool:
        """
        Index content from a completed job.

        Args:
            job_id: Job ID to index

        Returns:
            True if indexing successful
        """
        try:
            # Get job data
            job_data = await get_document_from_firestore(document_id=job_id, collection_name=self._jobs_collection)

            if not job_data:
                logger.warning(f"Job {job_id} not found for indexing")
                return False

            # Check job status
            if job_data.get("status") != JobStatus.COMPLETED:
                logger.info(f"Job {job_id} not completed, skipping indexing")
                return False

            # Extract content from job results
            results = job_data.get("results", {})
            content = results.get("content", {})

            if not content:
                logger.warning(f"No content found in job {job_id}")
                return False

            # Build search index document
            index_doc = await self._build_index_document(job_id, job_data, content)

            if not index_doc:
                logger.warning(f"Failed to build index document for job {job_id}")
                return False

            # Index the document
            success = await self.search_backend.index_document(index_doc)

            if success:
                logger.info(f"Successfully indexed job {job_id}")
            else:
                logger.error(f"Failed to index job {job_id}")

            return success

        except Exception as e:
            logger.error(f"Error indexing job {job_id}: {e}")
            return False

    async def _build_index_document(
        self, job_id: str, job_data: Dict[str, Any], content: Dict[str, Any]
    ) -> Optional[SearchIndex]:
        """Build search index document from job data."""
        try:
            # Extract content outline
            content_outline = content.get("content_outline", {})

            if not content_outline:
                return None

            # Extract metadata
            metadata = content.get("metadata", {})
            quality_metrics = content.get("quality_metrics", {})

            # Build sections for indexing
            sections = []
            for section in content_outline.get("sections", []):
                sections.append(
                    {
                        "title": section.get("title", ""),
                        "description": section.get("description", ""),
                        "key_points": section.get("key_points", []),
                    }
                )

            # Determine content types available
            content_types = []
            if content.get("podcast_script"):
                content_types.append("podcast")
            if content.get("study_guide"):
                content_types.append("study_guide")
            if content.get("one_pager_summary"):
                content_types.append("one_pager")
            if content.get("detailed_reading_material"):
                content_types.append("detailed_reading")
            if content.get("faqs"):
                content_types.append("faqs")
            if content.get("flashcards"):
                content_types.append("flashcards")
            if content.get("reading_guide_questions"):
                content_types.append("reading_guide")

            # Create searchable text
            searchable_parts = [
                content_outline.get("title", ""),
                content_outline.get("overview", ""),
            ]

            # Add learning objectives
            searchable_parts.extend(content_outline.get("learning_objectives", []))

            # Add section content
            for section in sections:
                searchable_parts.append(section["title"])
                searchable_parts.append(section["description"])
                searchable_parts.extend(section["key_points"])

            searchable_text = " ".join(filter(None, searchable_parts))

            # Build index document
            index_doc = SearchIndex(
                id=job_id,
                user_id=job_data.get("user_id", ""),
                title=content_outline.get("title", "Untitled"),
                overview=content_outline.get("overview", ""),
                content_type=",".join(content_types) if content_types else "unknown",
                difficulty=content_outline.get("difficulty_level", "intermediate"),
                target_audience=content_outline.get("target_audience", ""),
                tags=[],  # Could extract from content
                categories=[],  # Could derive from content type
                created_at=job_data.get("created_at", datetime.utcnow()),
                updated_at=job_data.get("updated_at", datetime.utcnow()),
                quality_score=quality_metrics.get("overall_score"),
                estimated_duration=content_outline.get("estimated_total_duration"),
                status="published",
                searchable_text=searchable_text,
                sections=sections,
                metadata={
                    "job_id": job_id,
                    "ai_model": metadata.get("ai_model_used"),
                    "tokens_consumed": metadata.get("tokens_consumed"),
                    "content_types": content_types,
                },
            )

            return index_doc

        except Exception as e:
            logger.error(f"Error building index document: {e}")
            return None

    async def reindex_all_content(self, batch_size: int = 100, since_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Reindex all content or content since a specific date.

        Args:
            batch_size: Number of documents to process at once
            since_date: Only index content created/updated after this date

        Returns:
            Results summary
        """
        results = {"total": 0, "success": 0, "failed": 0, "errors": []}

        try:
            logger.info("Starting content reindexing")

            # Build filters
            filters = {"status": JobStatus.COMPLETED}

            if since_date:
                filters["updated_at__gte"] = since_date.isoformat()

            # Get all completed jobs
            offset = 0

            while True:
                # Get batch of jobs
                jobs = await query_documents(
                    collection=self._jobs_collection,
                    filters=filters,
                    limit=batch_size,
                    offset=offset,
                    order_by="created_at",
                )

                if not jobs:
                    break

                # Index each job
                for job in jobs:
                    job_id = job.get("id")
                    if not job_id:
                        continue

                    results["total"] += 1

                    if await self.index_job_content(job_id):
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Failed to index job {job_id}")

                offset += batch_size

                # Log progress
                logger.info(f"Indexed {results['success']}/{results['total']} documents")

                # Small delay to avoid overwhelming the system
                await asyncio.sleep(0.1)

            logger.info(f"Reindexing complete: {results}")

            # Refresh index
            await self.search_backend.refresh_index()

        except Exception as e:
            logger.error(f"Error during reindexing: {e}")
            results["errors"].append(str(e))

        return results

    async def update_index_for_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update search index when job is updated.

        Args:
            job_id: Job ID
            updates: Fields that were updated

        Returns:
            True if update successful
        """
        try:
            # Check if updates affect searchable content
            searchable_fields = {
                "results.content.content_outline.title",
                "results.content.content_outline.overview",
                "results.content.quality_metrics.overall_score",
                "status",
            }

            # Check if any searchable field was updated
            if not any(field in updates for field in searchable_fields):
                return True  # No search-relevant updates

            # Reindex the entire document
            return await self.index_job_content(job_id)

        except Exception as e:
            logger.error(f"Error updating index for job {job_id}: {e}")
            return False

    async def remove_from_index(self, job_id: str) -> bool:
        """
        Remove a job from the search index.

        Args:
            job_id: Job ID to remove

        Returns:
            True if removal successful
        """
        try:
            success = await self.search_backend.delete_document(job_id)

            if success:
                logger.info(f"Removed job {job_id} from search index")
            else:
                logger.warning(f"Failed to remove job {job_id} from search index")

            return success

        except Exception as e:
            logger.error(f"Error removing job {job_id} from index: {e}")
            return False

    async def cleanup_orphaned_index_entries(self) -> Dict[str, Any]:
        """
        Remove index entries for jobs that no longer exist.

        Returns:
            Cleanup results
        """
        results = {"checked": 0, "removed": 0, "errors": []}

        try:
            logger.info("Starting orphaned index cleanup")

            # Get all indexed documents
            # This is a simplified approach - in production, you'd want to
            # paginate through the index
            index_stats = await self.search_backend.get_index_stats()

            # For now, we'll just return stats
            # A full implementation would iterate through indexed docs
            # and check if corresponding jobs exist

            logger.info(f"Index cleanup complete: {results}")

        except Exception as e:
            logger.error(f"Error during index cleanup: {e}")
            results["errors"].append(str(e))

        return results

    async def optimize_index(self) -> bool:
        """
        Optimize the search index for better performance.

        Returns:
            True if optimization successful
        """
        try:
            logger.info("Starting index optimization")

            # For simple backend, just refresh
            success = await self.search_backend.refresh_index()

            if success:
                logger.info("Index optimization complete")
            else:
                logger.warning("Index optimization failed")

            return success

        except Exception as e:
            logger.error(f"Error optimizing index: {e}")
            return False


# Celery task wrappers (if using Celery)
async def index_job_task(job_id: str) -> bool:
    """Celery task to index a job."""
    indexer = SearchIndexingTasks()
    return await indexer.index_job_content(job_id)


async def reindex_all_task(since_days: Optional[int] = None) -> Dict[str, Any]:
    """Celery task to reindex all content."""
    indexer = SearchIndexingTasks()

    since_date = None
    if since_days:
        since_date = datetime.utcnow() - timedelta(days=since_days)

    return await indexer.reindex_all_content(since_date=since_date)


async def cleanup_index_task() -> Dict[str, Any]:
    """Celery task to cleanup orphaned index entries."""
    indexer = SearchIndexingTasks()
    return await indexer.cleanup_orphaned_index_entries()


async def optimize_index_task() -> bool:
    """Celery task to optimize the search index."""
    indexer = SearchIndexingTasks()
    return await indexer.optimize_index()
