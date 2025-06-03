"""
Content versioning service with Firestore persistence.

This module provides content versioning functionality with Firestore backend,
allowing tracking and retrieval of different versions of generated content.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from app.models.pydantic.content import GeneratedContent
from app.services.job.firestore_client import (
    create_or_update_document_in_firestore,
    get_document_from_firestore,
    get_firestore_client,
)

logger = logging.getLogger(__name__)


class ContentStatus(Enum):
    """Status of content generation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


class ContentFormat(Enum):
    """Supported content formats."""

    PODCAST = "podcast"
    GUIDE = "guide"
    ONE_PAGER = "one_pager"
    STUDY_GUIDE = "study_guide"
    FLASHCARDS = "flashcards"
    FAQ = "faq"
    SUMMARY = "summary"
    OUTLINE = "outline"
    ALL = "all"  # When all formats are generated


class ContentVersionManager:
    """Manages content versions with Firestore persistence."""

    def __init__(self, collection_name: str = "content_versions"):
        """Initialize the version manager with Firestore backend.

        Args:
            collection_name: Name of the Firestore collection for content versions
        """
        self._collection_name = collection_name
        self._client = get_firestore_client()
        logger.info(
            f"ContentVersionManager initialized with collection: {collection_name}"
        )

    async def create_version(
        self,
        syllabus_text: str,
        target_format: str,
        content: GeneratedContent,
        metadata: Dict[str, Any],
        generation_time: float,
        token_usage: Dict[str, int],
        quality_score: Optional[float] = None,
        parent_version_id: Optional[str] = None,
    ) -> str:
        """Create a new content version in Firestore.

        Args:
            syllabus_text: The input syllabus text
            target_format: Target format (e.g., 'podcast', 'all')
            content: The generated content object
            metadata: Additional metadata
            generation_time: Time taken to generate content (seconds)
            token_usage: Token usage statistics
            quality_score: Optional quality score
            parent_version_id: Optional parent version for tracking history

        Returns:
            Version ID of the created version
        """
        # Generate content hash and version ID
        content_dict = content.model_dump(exclude_none=True)
        content_hash = self._generate_content_hash(
            syllabus_text, target_format, content_dict
        )
        version_id = self._generate_version_id(content_hash)

        # Create version document
        version_data = {
            "version_id": version_id,
            "content_hash": content_hash,
            "syllabus_text": syllabus_text,
            "target_format": target_format,
            "content": content_dict,
            "metadata": metadata,
            "status": ContentStatus.COMPLETED.value,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "generation_time": generation_time,
            "token_usage": token_usage,
            "quality_score": quality_score,
            "parent_version_id": parent_version_id,
        }

        # Store in Firestore
        await create_or_update_document_in_firestore(
            version_id, version_data, self._collection_name
        )

        # Also create an index entry for hash lookups
        await self._create_hash_index(content_hash, version_id)

        logger.info(
            f"Created content version: {version_id} with hash: {content_hash[:8]}"
        )
        return version_id

    async def get_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific version by ID.

        Args:
            version_id: The version ID to retrieve

        Returns:
            Version data if found, None otherwise
        """
        version_data = await get_document_from_firestore(
            version_id, self._collection_name
        )
        if version_data:
            logger.debug(f"Retrieved version: {version_id}")
        return version_data

    async def get_by_hash(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Get a version by content hash.

        Args:
            content_hash: The content hash to lookup

        Returns:
            Version data if found, None otherwise
        """
        # Look up version ID from hash index
        hash_doc = await get_document_from_firestore(
            f"hash_{content_hash}", f"{self._collection_name}_hash_index"
        )

        if hash_doc and "version_id" in hash_doc:
            return await self.get_version(hash_doc["version_id"])

        return None

    async def check_duplicate(
        self, syllabus_text: str, target_format: str, content: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check if content already exists.

        Args:
            syllabus_text: The input syllabus text
            target_format: Target format
            content: The content to check

        Returns:
            Existing version data if duplicate found, None otherwise
        """
        content_hash = self._generate_content_hash(
            syllabus_text, target_format, content
        )
        existing_version = await self.get_by_hash(content_hash)

        if existing_version:
            logger.info(f"Found duplicate content with hash: {content_hash[:8]}")

        return existing_version

    async def get_versions_for_format(
        self, target_format: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get all versions for a specific format.

        Args:
            target_format: The format to filter by
            limit: Maximum number of versions to return

        Returns:
            List of version data dictionaries
        """
        query = (
            self._client.collection(self._collection_name)
            .where("target_format", "==", target_format)
            .order_by("created_at", direction="DESCENDING")
            .limit(limit)
        )

        docs = await query.get()
        versions = []

        for doc in docs:
            version_data = doc.to_dict()
            versions.append(version_data)

        logger.info(f"Retrieved {len(versions)} versions for format: {target_format}")
        return versions

    async def get_latest_versions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent versions.

        Args:
            limit: Maximum number of versions to return

        Returns:
            List of version data dictionaries
        """
        query = (
            self._client.collection(self._collection_name)
            .order_by("created_at", direction="DESCENDING")
            .limit(limit)
        )

        docs = await query.get()
        versions = []

        for doc in docs:
            version_data = doc.to_dict()
            versions.append(version_data)

        logger.info(f"Retrieved {len(versions)} latest versions")
        return versions

    async def get_version_history(self, version_id: str) -> List[Dict[str, Any]]:
        """Get the version history for a content item.

        Args:
            version_id: The version ID to start from

        Returns:
            List of version data in chronological order
        """
        history = []
        current_id = version_id

        # Follow parent chain
        while current_id:
            version = await self.get_version(current_id)
            if not version:
                break

            history.append(version)
            current_id = version.get("parent_version_id")

        # Return in chronological order (oldest first)
        history.reverse()
        logger.info(f"Retrieved {len(history)} versions in history for: {version_id}")
        return history

    async def update_quality_score(self, version_id: str, score: float) -> bool:
        """Update the quality score for a version.

        Args:
            version_id: The version ID to update
            score: The new quality score

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            from app.services.job.firestore_client import (
                update_document_field_in_firestore,
            )

            await update_document_field_in_firestore(
                version_id, "quality_score", score, self._collection_name
            )
            await update_document_field_in_firestore(
                version_id,
                "updated_at",
                datetime.utcnow().isoformat(),
                self._collection_name,
            )

            logger.info(f"Updated quality score for version {version_id} to {score}")
            return True

        except Exception as e:
            logger.error(f"Failed to update quality score: {e}")
            return False

    async def get_versions_by_syllabus(
        self, syllabus_text: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get all versions generated from a specific syllabus.

        Args:
            syllabus_text: The syllabus text to search for
            limit: Maximum number of versions to return

        Returns:
            List of version data dictionaries
        """
        # Create a hash of the syllabus for efficient lookup
        syllabus_hash = hashlib.sha256(syllabus_text.encode()).hexdigest()

        query = (
            self._client.collection(self._collection_name)
            .where("syllabus_hash", "==", syllabus_hash)
            .order_by("created_at", direction="DESCENDING")
            .limit(limit)
        )

        docs = await query.get()
        versions = []

        for doc in docs:
            version_data = doc.to_dict()
            versions.append(version_data)

        logger.info(
            f"Retrieved {len(versions)} versions for syllabus hash: {syllabus_hash[:8]}"
        )
        return versions

    async def cleanup_old_versions(self, days_to_keep: int = 30) -> int:
        """Clean up old versions to save storage.

        Args:
            days_to_keep: Number of days to keep versions

        Returns:
            Number of versions deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        cutoff_date_str = cutoff_date.isoformat()

        # Query for old versions
        query = (
            self._client.collection(self._collection_name)
            .where("created_at", "<", cutoff_date_str)
            .select([])
        )  # Only get document IDs

        deleted_count = 0
        batch = self._client.batch()
        batch_size = 0

        async for doc in query.stream():
            batch.delete(doc.reference)
            batch_size += 1
            deleted_count += 1

            # Commit batch every 500 documents
            if batch_size >= 500:
                await batch.commit()
                batch = self._client.batch()
                batch_size = 0

        # Commit remaining deletions
        if batch_size > 0:
            await batch.commit()

        logger.info(f"Cleaned up {deleted_count} old versions")
        return deleted_count

    # Private helper methods

    def _generate_content_hash(
        self, syllabus_text: str, target_format: str, content: Dict[str, Any]
    ) -> str:
        """Generate a hash for the content.

        Args:
            syllabus_text: The input syllabus text
            target_format: Target format
            content: The content dictionary

        Returns:
            SHA256 hash of the content
        """
        content_str = json.dumps(
            {
                "syllabus": syllabus_text,
                "format": target_format,
                "content": content,
            },
            sort_keys=True,
        )
        return hashlib.sha256(content_str.encode()).hexdigest()

    def _generate_version_id(self, content_hash: str) -> str:
        """Generate a version ID from content hash.

        Args:
            content_hash: The content hash

        Returns:
            Version ID with timestamp and hash prefix
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"v_{timestamp}_{content_hash[:8]}"

    async def _create_hash_index(self, content_hash: str, version_id: str) -> None:
        """Create a hash index entry for efficient lookups.

        Args:
            content_hash: The content hash
            version_id: The version ID
        """
        index_data = {
            "content_hash": content_hash,
            "version_id": version_id,
            "created_at": datetime.utcnow().isoformat(),
        }

        await create_or_update_document_in_firestore(
            f"hash_{content_hash}", index_data, f"{self._collection_name}_hash_index"
        )


# Global instance management

_version_manager: Optional[ContentVersionManager] = None


def get_content_version_manager() -> ContentVersionManager:
    """Get or create the global content version manager instance.

    Returns:
        ContentVersionManager instance
    """
    global _version_manager
    if _version_manager is None:
        _version_manager = ContentVersionManager()
    return _version_manager
