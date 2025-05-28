"""
Content versioning models for tracking generated content versions.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

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

@dataclass
class ContentVersion:
    """Represents a version of generated content."""
    version_id: str
    content_hash: str
    syllabus_text: str
    target_format: ContentFormat
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    status: ContentStatus
    created_at: datetime
    updated_at: datetime
    generation_time: float  # in seconds
    token_usage: Dict[str, int]
    quality_score: Optional[float] = None
    parent_version_id: Optional[str] = None
    
    @classmethod
    def create_new(
        cls,
        syllabus_text: str,
        target_format: ContentFormat,
        content: Dict[str, Any],
        metadata: Dict[str, Any],
        generation_time: float,
        token_usage: Dict[str, int],
        parent_version_id: Optional[str] = None
    ) -> 'ContentVersion':
        """Create a new content version."""
        content_hash = cls._generate_content_hash(syllabus_text, target_format, content)
        version_id = cls._generate_version_id(content_hash)
        
        return cls(
            version_id=version_id,
            content_hash=content_hash,
            syllabus_text=syllabus_text,
            target_format=target_format,
            content=content,
            metadata=metadata,
            status=ContentStatus.COMPLETED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            generation_time=generation_time,
            token_usage=token_usage,
            parent_version_id=parent_version_id
        )
    
    @staticmethod
    def _generate_content_hash(
        syllabus_text: str,
        target_format: ContentFormat,
        content: Dict[str, Any]
    ) -> str:
        """Generate a hash for the content."""
        content_str = json.dumps({
            'syllabus': syllabus_text,
            'format': target_format.value,
            'content': content
        }, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    @staticmethod
    def _generate_version_id(content_hash: str) -> str:
        """Generate a version ID from content hash."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"v_{timestamp}_{content_hash[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['target_format'] = self.target_format.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    def update_quality_score(self, score: float) -> None:
        """Update the quality score for this version."""
        self.quality_score = score
        self.updated_at = datetime.utcnow()

class ContentVersionManager:
    """Manages content versions and provides versioning functionality."""
    
    def __init__(self):
        """Initialize the version manager."""
        self._versions: Dict[str, ContentVersion] = {}
        self._hash_to_version: Dict[str, str] = {}
    
    def add_version(self, version: ContentVersion) -> None:
        """Add a new content version."""
        self._versions[version.version_id] = version
        self._hash_to_version[version.content_hash] = version.version_id
    
    def get_version(self, version_id: str) -> Optional[ContentVersion]:
        """Get a specific version by ID."""
        return self._versions.get(version_id)
    
    def get_by_hash(self, content_hash: str) -> Optional[ContentVersion]:
        """Get a version by content hash."""
        version_id = self._hash_to_version.get(content_hash)
        return self._versions.get(version_id) if version_id else None
    
    def get_versions_for_format(self, target_format: ContentFormat) -> List[ContentVersion]:
        """Get all versions for a specific format."""
        return [v for v in self._versions.values() if v.target_format == target_format]
    
    def get_latest_versions(self, limit: int = 10) -> List[ContentVersion]:
        """Get the most recent versions."""
        sorted_versions = sorted(
            self._versions.values(),
            key=lambda v: v.created_at,
            reverse=True
        )
        return sorted_versions[:limit]
    
    def check_duplicate(
        self,
        syllabus_text: str,
        target_format: ContentFormat,
        content: Dict[str, Any]
    ) -> Optional[ContentVersion]:
        """Check if content already exists."""
        content_hash = ContentVersion._generate_content_hash(
            syllabus_text, target_format, content
        )
        return self.get_by_hash(content_hash)
    
    def get_version_history(self, version_id: str) -> List[ContentVersion]:
        """Get the version history for a content item."""
        version = self.get_version(version_id)
        if not version:
            return []
        
        history = [version]
        current = version
        
        # Follow parent chain
        while current.parent_version_id:
            parent = self.get_version(current.parent_version_id)
            if parent:
                history.append(parent)
                current = parent
            else:
                break
        
        return list(reversed(history))  # Return chronological order 