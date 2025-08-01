"""
Base search backend interface and configuration.

This module defines the abstract interface that all search backends must implement,
allowing for flexible switching between different search implementations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.search import SavedSearch, SearchAnalytics, SearchIndex, SearchResult, SearchSuggestion
from app.schemas.search import AdvancedSearchRequest


class SearchConfig(BaseModel):
    """Search backend configuration."""

    backend_type: str = Field(default="simple", description="Search backend type (simple, elasticsearch)")
    index_name: str = Field(default="content", description="Search index name")
    max_results: int = Field(default=10000, description="Maximum results to return")
    default_page_size: int = Field(default=20, description="Default page size")
    max_page_size: int = Field(default=100, description="Maximum page size")
    enable_analytics: bool = Field(default=True, description="Enable search analytics")
    enable_suggestions: bool = Field(default=True, description="Enable search suggestions")
    enable_highlighting: bool = Field(default=True, description="Enable search result highlighting")
    suggestion_min_length: int = Field(default=2, description="Minimum query length for suggestions")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    elasticsearch_url: Optional[str] = Field(None, description="Elasticsearch URL if using ES backend")


class SearchBackend(ABC):
    """Abstract base class for search backends."""

    def __init__(self, config: SearchConfig):
        """Initialize search backend with configuration."""
        self.config = config

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the search backend (create indices, etc.)."""
        pass

    @abstractmethod
    async def index_document(self, document: SearchIndex) -> bool:
        """
        Index a single document.

        Args:
            document: Document to index

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def bulk_index_documents(self, documents: List[SearchIndex]) -> Dict[str, Any]:
        """
        Bulk index multiple documents.

        Args:
            documents: List of documents to index

        Returns:
            Results with success/failure counts
        """
        pass

    @abstractmethod
    async def update_document(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a document in the index.

        Args:
            doc_id: Document ID
            updates: Fields to update

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the index.

        Args:
            doc_id: Document ID

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def search(self, request: AdvancedSearchRequest, user_id: Optional[str] = None) -> SearchResult:
        """
        Perform a search based on the request.

        Args:
            request: Search request parameters
            user_id: User ID for filtering/analytics

        Returns:
            Search results
        """
        pass

    @abstractmethod
    async def suggest(self, query: str, limit: int = 10) -> List[SearchSuggestion]:
        """
        Get search suggestions for a partial query.

        Args:
            query: Partial search query
            limit: Maximum suggestions to return

        Returns:
            List of suggestions
        """
        pass

    @abstractmethod
    async def get_popular_searches(self, limit: int = 20, time_range: Optional[str] = "7d") -> List[Dict[str, Any]]:
        """
        Get popular searches.

        Args:
            limit: Maximum results
            time_range: Time range (e.g., "1d", "7d", "30d")

        Returns:
            List of popular searches with counts
        """
        pass

    @abstractmethod
    async def track_search(self, analytics: SearchAnalytics) -> bool:
        """
        Track search analytics.

        Args:
            analytics: Search analytics data

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def save_search(self, search: SavedSearch) -> SavedSearch:
        """
        Save a search configuration.

        Args:
            search: Search to save

        Returns:
            Saved search with ID
        """
        pass

    @abstractmethod
    async def get_saved_searches(self, user_id: str, include_public: bool = True) -> List[SavedSearch]:
        """
        Get saved searches for a user.

        Args:
            user_id: User ID
            include_public: Include public searches

        Returns:
            List of saved searches
        """
        pass

    @abstractmethod
    async def delete_saved_search(self, search_id: str, user_id: str) -> bool:
        """
        Delete a saved search.

        Args:
            search_id: Search ID
            user_id: User ID (for ownership verification)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def refresh_index(self) -> bool:
        """
        Refresh the search index to make recent changes searchable.

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_index_stats(self) -> Dict[str, Any]:
        """
        Get search index statistics.

        Returns:
            Index statistics (document count, size, etc.)
        """
        pass

    async def close(self) -> None:
        """Close search backend connections."""
        pass
