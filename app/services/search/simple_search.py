"""
Simple search backend implementation using Firestore.

This provides a basic search implementation that works with Firestore,
suitable for smaller datasets and development environments.
"""

import logging
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from app.core.config.settings import get_settings
from app.models.search import (
    FacetResult,
    SavedSearch,
    SearchAnalytics,
    SearchHit,
    SearchIndex,
    SearchResult,
    SearchSuggestion,
)
from app.schemas.search import AdvancedSearchRequest
from app.services.job.firestore_client import (
    batch_get_documents,
    create_or_update_document_in_firestore,
    delete_job_from_firestore,
    get_document_from_firestore,
    query_documents,
)
from app.services.search.aggregations import FacetProcessor
from app.services.search.base import SearchBackend, SearchConfig
from app.services.search.query_builder import QueryBuilder
from app.utils.cache_utils import cache_with_ttl

logger = logging.getLogger(__name__)
settings = get_settings()


class SimpleSearchBackend(SearchBackend):
    """
    Simple search backend using Firestore.

    This implementation provides basic search functionality suitable for
    smaller datasets. For production use with large datasets, consider
    using Elasticsearch.
    """

    def __init__(self, config: SearchConfig):
        """Initialize simple search backend."""
        super().__init__(config)
        self._search_collection = "search_index"
        self._saved_searches_collection = "saved_searches"
        self._analytics_collection = "search_analytics"

    async def initialize(self) -> None:
        """Initialize the search backend."""
        logger.info("Initializing simple search backend")
        # For Firestore, we don't need explicit index creation
        # Collections are created automatically

    async def index_document(self, document: SearchIndex) -> bool:
        """Index a single document."""
        try:
            # Prepare document for indexing
            doc_data = document.dict()
            doc_data["indexed_at"] = datetime.utcnow()

            # Create searchable text field combining multiple fields
            searchable_parts = [
                doc_data.get("title", ""),
                doc_data.get("overview", ""),
            ]

            # Add section content
            for section in doc_data.get("sections", []):
                if isinstance(section, dict):
                    searchable_parts.append(section.get("title", ""))
                    searchable_parts.append(section.get("description", ""))
                    searchable_parts.extend(section.get("key_points", []))

            doc_data["searchable_text"] = " ".join(filter(None, searchable_parts)).lower()

            # Index document
            await create_or_update_document_in_firestore(
                document_id=document.id, data=doc_data, collection_name=self._search_collection
            )

            logger.info(f"Indexed document {document.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to index document {document.id}: {e}")
            return False

    async def bulk_index_documents(self, documents: List[SearchIndex]) -> Dict[str, Any]:
        """Bulk index multiple documents."""
        results = {"total": len(documents), "success": 0, "failed": 0, "errors": []}

        for doc in documents:
            if await self.index_document(doc):
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"Failed to index {doc.id}")

        return results

    async def update_document(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        """Update a document in the index."""
        try:
            # Get existing document
            existing = await get_document_from_firestore(document_id=doc_id, collection_name=self._search_collection)

            if not existing:
                logger.warning(f"Document {doc_id} not found for update")
                return False

            # Apply updates
            existing.update(updates)
            existing["updated_at"] = datetime.utcnow()
            existing["indexed_at"] = datetime.utcnow()

            # Update searchable text if relevant fields changed
            if any(field in updates for field in ["title", "overview", "sections"]):
                searchable_parts = [
                    existing.get("title", ""),
                    existing.get("overview", ""),
                ]

                for section in existing.get("sections", []):
                    if isinstance(section, dict):
                        searchable_parts.append(section.get("title", ""))
                        searchable_parts.append(section.get("description", ""))
                        searchable_parts.extend(section.get("key_points", []))

                existing["searchable_text"] = " ".join(filter(None, searchable_parts)).lower()

            # Update document
            await create_or_update_document_in_firestore(
                document_id=doc_id, data=existing, collection_name=self._search_collection
            )

            return True

        except Exception as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            return False

    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the index."""
        try:
            return await delete_job_from_firestore(document_id=doc_id, collection_name=self._search_collection)
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False

    async def search(self, request: AdvancedSearchRequest, user_id: Optional[str] = None) -> SearchResult:
        """Perform a search based on the request."""
        start_time = time.time()

        try:
            # Build query filters
            filters = {}

            # Add user filter if provided
            if user_id:
                filters["user_id"] = user_id

            # Apply advanced filters
            if request.filters:
                # Content type filter
                if request.filters.content_type:
                    filters["content_type__in"] = request.filters.content_type

                # Difficulty filter
                if request.filters.difficulty:
                    filters["difficulty__in"] = request.filters.difficulty

                # Target audience filter
                if request.filters.target_audience:
                    filters["target_audience__in"] = request.filters.target_audience

                # Status filter
                if request.filters.status:
                    filters["status__in"] = request.filters.status

                # Quality score range
                if request.filters.quality_score_min is not None:
                    filters["quality_score__gte"] = request.filters.quality_score_min
                if request.filters.quality_score_max is not None:
                    filters["quality_score__lte"] = request.filters.quality_score_max

                # Duration range
                if request.filters.duration_min is not None:
                    filters["estimated_duration__gte"] = request.filters.duration_min
                if request.filters.duration_max is not None:
                    filters["estimated_duration__lte"] = request.filters.duration_max

                # Date range
                if request.filters.date_range:
                    if "start" in request.filters.date_range:
                        filters["created_at__gte"] = request.filters.date_range["start"]
                    if "end" in request.filters.date_range:
                        filters["created_at__lte"] = request.filters.date_range["end"]

                # User filter (admin only)
                if request.filters.user_id:
                    filters["user_id"] = request.filters.user_id

            # Get all matching documents for filtering
            all_docs = await query_documents(
                collection=self._search_collection, filters=filters, limit=None  # Get all for text search
            )

            # Apply text search if query provided
            if request.query:
                query_terms = request.query.lower().split()
                scored_docs = []

                for doc in all_docs:
                    searchable_text = doc.get("searchable_text", "").lower()
                    title = doc.get("title", "").lower()

                    # Calculate relevance score
                    score = 0.0
                    highlights = {}

                    for term in query_terms:
                        # Title matches worth more
                        if term in title:
                            score += 2.0
                            if "title" not in highlights:
                                highlights["title"] = []
                            highlights["title"].append(self._highlight_text(doc.get("title", ""), term))

                        # Count occurrences in searchable text
                        occurrences = searchable_text.count(term)
                        score += occurrences * 0.5

                        # Add overview highlights
                        if term in doc.get("overview", "").lower():
                            if "overview" not in highlights:
                                highlights["overview"] = []
                            highlights["overview"].append(self._highlight_text(doc.get("overview", ""), term))

                    if score > 0:
                        scored_docs.append((doc, score, highlights))

                # Sort by relevance score
                scored_docs.sort(key=lambda x: x[1], reverse=True)

                # Apply pagination
                total = len(scored_docs)
                start = (request.page - 1) * request.size
                end = start + request.size
                paginated_docs = scored_docs[start:end]

                # Build search hits
                hits = []
                for doc, score, highlights in paginated_docs:
                    hit = SearchHit(
                        id=doc.get("id", ""),
                        score=score,
                        source=doc,
                        highlights=highlights if request.highlight else None,
                    )
                    hits.append(hit)

            else:
                # No text search, just filter and paginate
                total = len(all_docs)

                # Apply sorting
                if request.sort:
                    for sort_field in reversed(request.sort):
                        reverse = sort_field.order == "desc"
                        all_docs.sort(key=lambda x: x.get(sort_field.field, ""), reverse=reverse)

                # Apply pagination
                start = (request.page - 1) * request.size
                end = start + request.size
                paginated_docs = all_docs[start:end]

                # Build search hits
                hits = []
                for doc in paginated_docs:
                    hit = SearchHit(id=doc.get("id", ""), score=1.0, source=doc)  # Default score for non-text searches
                    hits.append(hit)

            # Process facets if requested
            facets = None
            if request.facets:
                facets = FacetProcessor.process_simple_facets(all_docs, request.facets)

            # Track search analytics
            if self.config.enable_analytics:
                analytics = SearchAnalytics(
                    query=request.query or "",
                    user_id=user_id,
                    result_count=total,
                    search_duration_ms=(time.time() - start_time) * 1000,
                    filters_used=filters,
                    facets_used=request.facets or [],
                )
                await self.track_search(analytics)

            # Calculate total pages
            total_pages = (total + request.size - 1) // request.size if request.size > 0 else 0

            return SearchResult(
                query=request.query,
                total=total,
                hits=hits,
                facets=facets,
                took_ms=(time.time() - start_time) * 1000,
                page=request.page,
                page_size=request.size,
                total_pages=total_pages,
            )

        except Exception as e:
            logger.error(f"Search failed: {e}")
            # Return empty result on error
            return SearchResult(
                query=request.query,
                total=0,
                hits=[],
                facets=None,
                took_ms=(time.time() - start_time) * 1000,
                page=request.page,
                page_size=request.size,
                total_pages=0,
            )

    def _highlight_text(self, text: str, term: str, context_length: int = 50) -> str:
        """Highlight search term in text with context."""
        if not text or not term:
            return text

        # Find term position (case-insensitive)
        lower_text = text.lower()
        pos = lower_text.find(term.lower())

        if pos == -1:
            return text

        # Extract context around match
        start = max(0, pos - context_length)
        end = min(len(text), pos + len(term) + context_length)

        # Add ellipsis if truncated
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text) else ""

        # Build highlighted text
        highlighted = (
            prefix + text[start:pos] + f"<mark>{text[pos:pos+len(term)]}</mark>" + text[pos + len(term) : end] + suffix
        )

        return highlighted

    @cache_with_ttl(ttl=60)  # Cache for 1 minute
    async def suggest(self, query: str, limit: int = 10) -> List[SearchSuggestion]:
        """Get search suggestions for a partial query."""
        if len(query) < self.config.suggestion_min_length:
            return []

        try:
            query_lower = query.lower()

            # Get recent successful searches
            recent_searches = await self._get_recent_searches(limit=100)

            # Filter and score suggestions
            suggestions = []
            seen = set()

            for search in recent_searches:
                search_query = search.get("query", "").lower()

                # Skip if already seen
                if search_query in seen:
                    continue

                # Check if query matches
                if search_query.startswith(query_lower):
                    score = 1.0 - (len(search_query) - len(query_lower)) / len(search_query)
                    suggestions.append(
                        SearchSuggestion(
                            text=search.get("query", ""),
                            score=score,
                            type="query",
                            metadata={
                                "result_count": search.get("result_count", 0),
                                "frequency": search.get("frequency", 1),
                            },
                        )
                    )
                    seen.add(search_query)

            # Sort by score and limit
            suggestions.sort(key=lambda x: x.score, reverse=True)

            return suggestions[:limit]

        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            return []

    async def _get_recent_searches(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent successful searches."""
        # Query recent analytics
        cutoff_date = (datetime.utcnow() - timedelta(days=7)).isoformat()

        analytics = await query_documents(
            collection=self._analytics_collection,
            filters={"timestamp__gte": cutoff_date, "result_count__gt": 0},
            order_by="timestamp",
            order_direction="desc",
            limit=limit,
        )

        # Aggregate by query
        query_counts = defaultdict(lambda: {"count": 0, "total_results": 0})

        for record in analytics:
            query = record.get("query", "")
            if query:
                query_counts[query]["count"] += 1
                query_counts[query]["total_results"] += record.get("result_count", 0)

        # Convert to list
        searches = []
        for query, stats in query_counts.items():
            searches.append(
                {"query": query, "frequency": stats["count"], "result_count": stats["total_results"] // stats["count"]}
            )

        # Sort by frequency
        searches.sort(key=lambda x: x["frequency"], reverse=True)

        return searches

    async def get_popular_searches(self, limit: int = 20, time_range: Optional[str] = "7d") -> List[Dict[str, Any]]:
        """Get popular searches."""
        # Parse time range
        days = 7
        if time_range:
            match = re.match(r"(\d+)d", time_range)
            if match:
                days = int(match.group(1))

        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

        # Get recent searches
        searches = await self._get_recent_searches(limit=limit * 2)

        # Add trend information
        for search in searches:
            search["trend"] = "stable"  # Simplified trend

        return searches[:limit]

    async def track_search(self, analytics: SearchAnalytics) -> bool:
        """Track search analytics."""
        try:
            # Create analytics document
            doc_id = f"search_{int(time.time() * 1000)}_{analytics.user_id or 'anon'}"

            await create_or_update_document_in_firestore(
                document_id=doc_id, data=analytics.dict(), collection_name=self._analytics_collection
            )

            return True

        except Exception as e:
            logger.error(f"Failed to track search: {e}")
            return False

    async def save_search(self, search: SavedSearch) -> SavedSearch:
        """Save a search configuration."""
        try:
            # Generate ID if not provided
            if not search.id:
                search.id = f"saved_search_{int(time.time() * 1000)}_{search.user_id}"

            # Save to Firestore
            await create_or_update_document_in_firestore(
                document_id=search.id, data=search.dict(), collection_name=self._saved_searches_collection
            )

            return search

        except Exception as e:
            logger.error(f"Failed to save search: {e}")
            raise

    async def get_saved_searches(self, user_id: str, include_public: bool = True) -> List[SavedSearch]:
        """Get saved searches for a user."""
        try:
            # Build filters
            if include_public:
                # Get user's searches and public searches
                user_searches = await query_documents(
                    collection=self._saved_searches_collection,
                    filters={"user_id": user_id},
                    order_by="created_at",
                    order_direction="desc",
                )

                public_searches = await query_documents(
                    collection=self._saved_searches_collection,
                    filters={"is_public": True},
                    order_by="created_at",
                    order_direction="desc",
                )

                # Combine and deduplicate
                all_searches = user_searches + public_searches
                seen_ids = set()
                unique_searches = []

                for search in all_searches:
                    if search.get("id") not in seen_ids:
                        unique_searches.append(search)
                        seen_ids.add(search.get("id"))

                searches = unique_searches
            else:
                # Get only user's searches
                searches = await query_documents(
                    collection=self._saved_searches_collection,
                    filters={"user_id": user_id},
                    order_by="created_at",
                    order_direction="desc",
                )

            # Convert to SavedSearch models
            return [SavedSearch(**search) for search in searches]

        except Exception as e:
            logger.error(f"Failed to get saved searches: {e}")
            return []

    async def delete_saved_search(self, search_id: str, user_id: str) -> bool:
        """Delete a saved search."""
        try:
            # Verify ownership
            search = await get_document_from_firestore(
                document_id=search_id, collection_name=self._saved_searches_collection
            )

            if not search:
                return False

            if search.get("user_id") != user_id:
                logger.warning(f"User {user_id} attempted to delete search owned by {search.get('user_id')}")
                return False

            # Delete search
            return await delete_job_from_firestore(
                document_id=search_id, collection_name=self._saved_searches_collection
            )

        except Exception as e:
            logger.error(f"Failed to delete saved search: {e}")
            return False

    async def refresh_index(self) -> bool:
        """Refresh the search index."""
        # For Firestore, this is a no-op as queries are always fresh
        return True

    async def get_index_stats(self) -> Dict[str, Any]:
        """Get search index statistics."""
        try:
            # Get document count
            all_docs = await query_documents(collection=self._search_collection, limit=None)

            # Calculate statistics
            stats = {
                "total_documents": len(all_docs),
                "index_size_bytes": sum(len(str(doc)) for doc in all_docs),  # Approximate
                "content_types": {},
                "difficulty_levels": {},
                "quality_scores": {"min": 1.0, "max": 0.0, "avg": 0.0},
            }

            # Aggregate by content type and difficulty
            quality_scores = []

            for doc in all_docs:
                # Content type
                content_type = doc.get("content_type", "unknown")
                stats["content_types"][content_type] = stats["content_types"].get(content_type, 0) + 1

                # Difficulty
                difficulty = doc.get("difficulty", "unknown")
                stats["difficulty_levels"][difficulty] = stats["difficulty_levels"].get(difficulty, 0) + 1

                # Quality score
                if "quality_score" in doc and doc["quality_score"] is not None:
                    quality_scores.append(doc["quality_score"])

            # Calculate quality score stats
            if quality_scores:
                stats["quality_scores"]["min"] = min(quality_scores)
                stats["quality_scores"]["max"] = max(quality_scores)
                stats["quality_scores"]["avg"] = sum(quality_scores) / len(quality_scores)

            return stats

        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {"error": str(e), "total_documents": 0}
