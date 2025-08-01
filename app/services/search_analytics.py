"""
Search analytics service for tracking and analyzing search behavior.

This service provides insights into search patterns, popular queries,
and search performance metrics.
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.core.config.settings import get_settings
from app.models.search import SearchAnalytics
from app.services.job.firestore_client import create_or_update_document_in_firestore, query_documents
from app.utils.cache_utils import cache_with_ttl

logger = logging.getLogger(__name__)
settings = get_settings()


class SearchAnalyticsService:
    """Service for managing search analytics."""

    def __init__(self):
        """Initialize search analytics service."""
        self._collection = "search_analytics"

    async def track_search(
        self,
        query: str,
        user_id: Optional[str],
        result_count: int,
        duration_ms: float,
        filters: Optional[Dict[str, Any]] = None,
        clicked_results: Optional[List[str]] = None,
    ) -> bool:
        """
        Track a search event.

        Args:
            query: Search query text
            user_id: User ID (optional for anonymous searches)
            result_count: Number of results returned
            duration_ms: Search duration in milliseconds
            filters: Applied filters
            clicked_results: IDs of clicked results

        Returns:
            True if tracking successful
        """
        try:
            analytics = SearchAnalytics(
                query=query,
                user_id=user_id,
                result_count=result_count,
                search_duration_ms=duration_ms,
                filters_used=filters or {},
                clicked_results=clicked_results or [],
            )

            # Generate document ID
            doc_id = f"search_{int(datetime.utcnow().timestamp() * 1000)}_{user_id or 'anon'}"

            await create_or_update_document_in_firestore(
                document_id=doc_id, data=analytics.dict(), collection_name=self._collection
            )

            logger.debug(f"Tracked search: query='{query}', results={result_count}")
            return True

        except Exception as e:
            logger.error(f"Failed to track search: {e}")
            return False

    async def track_click(
        self, search_query: str, result_id: str, position: int, user_id: Optional[str] = None
    ) -> bool:
        """
        Track a search result click.

        Args:
            search_query: Original search query
            result_id: Clicked result ID
            position: Position in search results
            user_id: User ID

        Returns:
            True if tracking successful
        """
        try:
            # Create click event
            click_data = {
                "event_type": "click",
                "query": search_query,
                "result_id": result_id,
                "position": position,
                "user_id": user_id,
                "timestamp": datetime.utcnow(),
            }

            doc_id = f"click_{int(datetime.utcnow().timestamp() * 1000)}_{user_id or 'anon'}"

            await create_or_update_document_in_firestore(
                document_id=doc_id, data=click_data, collection_name=f"{self._collection}_clicks"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to track click: {e}")
            return False

    @cache_with_ttl(ttl=300)  # Cache for 5 minutes
    async def get_popular_searches(
        self, days: int = 7, limit: int = 20, exclude_empty: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get popular searches within a time period.

        Args:
            days: Number of days to look back
            limit: Maximum results to return
            exclude_empty: Exclude searches with no results

        Returns:
            List of popular searches with metadata
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

            # Build filters
            filters = {"timestamp__gte": cutoff_date}
            if exclude_empty:
                filters["result_count__gt"] = 0

            # Query analytics
            analytics = await query_documents(collection=self._collection, filters=filters)

            # Aggregate by query
            query_stats = defaultdict(
                lambda: {
                    "count": 0,
                    "total_results": 0,
                    "avg_duration_ms": 0,
                    "unique_users": set(),
                    "click_through_rate": 0,
                }
            )

            for record in analytics:
                query = record.get("query", "").strip()
                if not query:
                    continue

                stats = query_stats[query]
                stats["count"] += 1
                stats["total_results"] += record.get("result_count", 0)
                stats["avg_duration_ms"] += record.get("search_duration_ms", 0)

                user_id = record.get("user_id")
                if user_id:
                    stats["unique_users"].add(user_id)

                if record.get("clicked_results"):
                    stats["click_through_rate"] += 1

            # Calculate averages and convert to list
            popular_searches = []

            for query, stats in query_stats.items():
                count = stats["count"]

                popular_searches.append(
                    {
                        "query": query,
                        "search_count": count,
                        "unique_users": len(stats["unique_users"]),
                        "avg_results": stats["total_results"] / count if count > 0 else 0,
                        "avg_duration_ms": stats["avg_duration_ms"] / count if count > 0 else 0,
                        "click_through_rate": stats["click_through_rate"] / count if count > 0 else 0,
                    }
                )

            # Sort by search count
            popular_searches.sort(key=lambda x: x["search_count"], reverse=True)

            return popular_searches[:limit]

        except Exception as e:
            logger.error(f"Failed to get popular searches: {e}")
            return []

    @cache_with_ttl(ttl=300)
    async def get_trending_searches(
        self, current_period_days: int = 1, previous_period_days: int = 7, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get trending searches (increasing in popularity).

        Args:
            current_period_days: Days for current period
            previous_period_days: Days for comparison period
            limit: Maximum results

        Returns:
            List of trending searches
        """
        try:
            # Get current period stats
            current_cutoff = (datetime.utcnow() - timedelta(days=current_period_days)).isoformat()
            current_analytics = await query_documents(
                collection=self._collection, filters={"timestamp__gte": current_cutoff}
            )

            # Get previous period stats
            previous_start = (datetime.utcnow() - timedelta(days=previous_period_days)).isoformat()
            previous_end = current_cutoff
            previous_analytics = await query_documents(
                collection=self._collection, filters={"timestamp__gte": previous_start, "timestamp__lt": previous_end}
            )

            # Aggregate current period
            current_counts = defaultdict(int)
            for record in current_analytics:
                query = record.get("query", "").strip()
                if query:
                    current_counts[query] += 1

            # Aggregate previous period
            previous_counts = defaultdict(int)
            for record in previous_analytics:
                query = record.get("query", "").strip()
                if query:
                    previous_counts[query] += 1

            # Calculate trends
            trending = []

            for query, current_count in current_counts.items():
                previous_count = previous_counts.get(query, 0)

                # Calculate trend score
                if previous_count == 0:
                    trend_score = current_count  # New query
                else:
                    trend_score = (current_count - previous_count) / previous_count

                trending.append(
                    {
                        "query": query,
                        "current_count": current_count,
                        "previous_count": previous_count,
                        "trend_score": trend_score,
                        "trend_percentage": trend_score * 100 if previous_count > 0 else None,
                        "is_new": previous_count == 0,
                    }
                )

            # Sort by trend score
            trending.sort(key=lambda x: x["trend_score"], reverse=True)

            return trending[:limit]

        except Exception as e:
            logger.error(f"Failed to get trending searches: {e}")
            return []

    @cache_with_ttl(ttl=300)
    async def get_failed_searches(self, days: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get searches that returned no results.

        Args:
            days: Number of days to look back
            limit: Maximum results

        Returns:
            List of failed searches
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

            # Query searches with no results
            analytics = await query_documents(
                collection=self._collection, filters={"timestamp__gte": cutoff_date, "result_count": 0}
            )

            # Aggregate by query
            failed_queries = defaultdict(lambda: {"count": 0, "unique_users": set()})

            for record in analytics:
                query = record.get("query", "").strip()
                if not query:
                    continue

                stats = failed_queries[query]
                stats["count"] += 1

                user_id = record.get("user_id")
                if user_id:
                    stats["unique_users"].add(user_id)

            # Convert to list
            failed_searches = []

            for query, stats in failed_queries.items():
                failed_searches.append(
                    {"query": query, "fail_count": stats["count"], "unique_users": len(stats["unique_users"])}
                )

            # Sort by fail count
            failed_searches.sort(key=lambda x: x["fail_count"], reverse=True)

            return failed_searches[:limit]

        except Exception as e:
            logger.error(f"Failed to get failed searches: {e}")
            return []

    async def get_user_search_history(self, user_id: str, days: int = 30, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get search history for a specific user.

        Args:
            user_id: User ID
            days: Number of days to look back
            limit: Maximum results

        Returns:
            List of user's searches
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

            # Query user's searches
            searches = await query_documents(
                collection=self._collection,
                filters={"user_id": user_id, "timestamp__gte": cutoff_date},
                order_by="timestamp",
                order_direction="desc",
                limit=limit,
            )

            # Format results
            history = []

            for search in searches:
                history.append(
                    {
                        "query": search.get("query", ""),
                        "timestamp": search.get("timestamp"),
                        "result_count": search.get("result_count", 0),
                        "duration_ms": search.get("search_duration_ms", 0),
                        "filters": search.get("filters_used", {}),
                        "clicked_results": search.get("clicked_results", []),
                    }
                )

            return history

        except Exception as e:
            logger.error(f"Failed to get user search history: {e}")
            return []

    @cache_with_ttl(ttl=600)  # Cache for 10 minutes
    async def get_search_metrics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get overall search metrics.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary of search metrics
        """
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

            # Query all searches in period
            analytics = await query_documents(collection=self._collection, filters={"timestamp__gte": cutoff_date})

            # Calculate metrics
            total_searches = len(analytics)
            unique_users = set()
            total_duration = 0
            total_results = 0
            searches_with_results = 0
            searches_with_clicks = 0

            for record in analytics:
                user_id = record.get("user_id")
                if user_id:
                    unique_users.add(user_id)

                total_duration += record.get("search_duration_ms", 0)
                result_count = record.get("result_count", 0)
                total_results += result_count

                if result_count > 0:
                    searches_with_results += 1

                if record.get("clicked_results"):
                    searches_with_clicks += 1

            # Calculate averages
            metrics = {
                "total_searches": total_searches,
                "unique_users": len(unique_users),
                "avg_searches_per_user": total_searches / len(unique_users) if unique_users else 0,
                "avg_duration_ms": total_duration / total_searches if total_searches > 0 else 0,
                "avg_results_per_search": total_results / total_searches if total_searches > 0 else 0,
                "search_success_rate": searches_with_results / total_searches if total_searches > 0 else 0,
                "click_through_rate": searches_with_clicks / total_searches if total_searches > 0 else 0,
                "period_days": days,
            }

            return metrics

        except Exception as e:
            logger.error(f"Failed to get search metrics: {e}")
            return {"error": str(e), "total_searches": 0}
