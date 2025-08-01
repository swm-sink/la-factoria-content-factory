"""
Search suggestions and auto-complete service.

This service provides intelligent search suggestions based on:
- Popular searches
- User search history
- Content titles and tags
- Spell correction
"""

import logging
import re
from collections import defaultdict
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Set

from app.core.config.settings import get_settings
from app.models.search import SearchSuggestion
from app.services.job.firestore_client import query_documents
from app.utils.cache_utils import cache_with_ttl

logger = logging.getLogger(__name__)
settings = get_settings()


class SearchSuggestionsService:
    """Service for generating search suggestions and auto-complete."""

    def __init__(self):
        """Initialize suggestions service."""
        self._search_index_collection = "search_index"
        self._analytics_collection = "search_analytics"
        self._suggestion_cache_ttl = 300  # 5 minutes

    @cache_with_ttl(ttl=300)
    async def get_suggestions(
        self, query: str, user_id: Optional[str] = None, limit: int = 10, types: Optional[List[str]] = None
    ) -> List[SearchSuggestion]:
        """
        Get search suggestions for a partial query.

        Args:
            query: Partial search query
            user_id: User ID for personalized suggestions
            limit: Maximum suggestions to return
            types: Types of suggestions to include

        Returns:
            List of suggestions
        """
        if not query or len(query) < 2:
            return []

        types = types or ["query", "content", "tag", "correction"]
        suggestions = []

        try:
            query_lower = query.lower().strip()

            # Get suggestions from different sources
            if "query" in types:
                query_suggestions = await self._get_query_suggestions(query_lower, user_id)
                suggestions.extend(query_suggestions)

            if "content" in types:
                content_suggestions = await self._get_content_suggestions(query_lower)
                suggestions.extend(content_suggestions)

            if "tag" in types:
                tag_suggestions = await self._get_tag_suggestions(query_lower)
                suggestions.extend(tag_suggestions)

            if "correction" in types:
                correction_suggestions = await self._get_spell_corrections(query_lower)
                suggestions.extend(correction_suggestions)

            # Remove duplicates and sort by score
            unique_suggestions = self._deduplicate_suggestions(suggestions)
            unique_suggestions.sort(key=lambda x: x.score, reverse=True)

            return unique_suggestions[:limit]

        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            return []

    async def _get_query_suggestions(self, query: str, user_id: Optional[str] = None) -> List[SearchSuggestion]:
        """Get suggestions from popular and user queries."""
        suggestions = []

        try:
            # Get recent popular searches
            cutoff_date = (datetime.utcnow() - timedelta(days=30)).isoformat()

            filters = {"timestamp__gte": cutoff_date, "result_count__gt": 0}

            # Include user's searches if user_id provided
            if user_id:
                # Get user's searches
                user_searches = await query_documents(
                    collection=self._analytics_collection,
                    filters={**filters, "user_id": user_id},
                    order_by="timestamp",
                    order_direction="desc",
                    limit=100,
                )

                # Get popular searches
                popular_searches = await query_documents(
                    collection=self._analytics_collection, filters=filters, limit=500
                )

                all_searches = user_searches + popular_searches
            else:
                all_searches = await query_documents(collection=self._analytics_collection, filters=filters, limit=500)

            # Aggregate query frequencies
            query_freq = defaultdict(lambda: {"count": 0, "results": 0, "is_user": False})

            for search in all_searches:
                search_query = search.get("query", "").lower().strip()
                if not search_query:
                    continue

                stats = query_freq[search_query]
                stats["count"] += 1
                stats["results"] += search.get("result_count", 0)

                if user_id and search.get("user_id") == user_id:
                    stats["is_user"] = True

            # Find matching queries
            for search_query, stats in query_freq.items():
                if search_query.startswith(query):
                    # Calculate score based on frequency and match quality
                    base_score = self._calculate_match_score(query, search_query)
                    freq_boost = min(stats["count"] / 100, 0.3)  # Max 0.3 boost
                    user_boost = 0.2 if stats["is_user"] else 0  # Boost user's own searches

                    score = base_score + freq_boost + user_boost

                    suggestions.append(
                        SearchSuggestion(
                            text=search_query,
                            score=min(score, 1.0),
                            type="query",
                            metadata={
                                "search_count": stats["count"],
                                "avg_results": stats["results"] // stats["count"] if stats["count"] > 0 else 0,
                                "is_user_query": stats["is_user"],
                            },
                        )
                    )

        except Exception as e:
            logger.error(f"Failed to get query suggestions: {e}")

        return suggestions

    async def _get_content_suggestions(self, query: str) -> List[SearchSuggestion]:
        """Get suggestions from content titles."""
        suggestions = []

        try:
            # Search for matching titles
            all_content = await query_documents(
                collection=self._search_index_collection, limit=1000  # Get a reasonable sample
            )

            for content in all_content:
                title = content.get("title", "").lower()

                if query in title:
                    # Calculate score based on match position and quality
                    score = self._calculate_match_score(query, title)

                    # Boost if query matches start of title
                    if title.startswith(query):
                        score += 0.2

                    suggestions.append(
                        SearchSuggestion(
                            text=content.get("title", ""),
                            score=min(score, 1.0),
                            type="content",
                            metadata={
                                "content_id": content.get("id"),
                                "content_type": content.get("content_type"),
                                "quality_score": content.get("quality_score"),
                            },
                        )
                    )

        except Exception as e:
            logger.error(f"Failed to get content suggestions: {e}")

        return suggestions

    async def _get_tag_suggestions(self, query: str) -> List[SearchSuggestion]:
        """Get suggestions from tags and categories."""
        suggestions = []

        try:
            # Get all unique tags and categories
            all_content = await query_documents(collection=self._search_index_collection, limit=1000)

            # Collect tags and categories with frequencies
            tag_freq = defaultdict(int)
            category_freq = defaultdict(int)

            for content in all_content:
                for tag in content.get("tags", []):
                    tag_freq[tag.lower()] += 1

                for category in content.get("categories", []):
                    category_freq[category.lower()] += 1

            # Find matching tags
            for tag, freq in tag_freq.items():
                if query in tag:
                    score = self._calculate_match_score(query, tag)
                    freq_boost = min(freq / 50, 0.2)  # Max 0.2 boost

                    suggestions.append(
                        SearchSuggestion(
                            text=tag,
                            score=min(score + freq_boost, 1.0),
                            type="tag",
                            metadata={"frequency": freq, "field": "tags"},
                        )
                    )

            # Find matching categories
            for category, freq in category_freq.items():
                if query in category:
                    score = self._calculate_match_score(query, category)
                    freq_boost = min(freq / 50, 0.2)

                    suggestions.append(
                        SearchSuggestion(
                            text=category,
                            score=min(score + freq_boost, 1.0),
                            type="tag",
                            metadata={"frequency": freq, "field": "categories"},
                        )
                    )

        except Exception as e:
            logger.error(f"Failed to get tag suggestions: {e}")

        return suggestions

    async def _get_spell_corrections(self, query: str) -> List[SearchSuggestion]:
        """Get spelling correction suggestions."""
        suggestions = []

        try:
            # Get common terms from recent searches
            cutoff_date = (datetime.utcnow() - timedelta(days=7)).isoformat()

            recent_searches = await query_documents(
                collection=self._analytics_collection,
                filters={"timestamp__gte": cutoff_date, "result_count__gt": 0},
                limit=200,
            )

            # Build vocabulary from successful searches
            vocabulary = set()
            for search in recent_searches:
                search_query = search.get("query", "").lower().strip()
                if search_query:
                    # Split into words
                    words = re.findall(r"\w+", search_query)
                    vocabulary.update(words)

            # Find similar words using edit distance
            query_words = re.findall(r"\w+", query)

            for word in query_words:
                if len(word) < 3:  # Skip short words
                    continue

                best_matches = []

                for vocab_word in vocabulary:
                    if vocab_word == word:  # Skip exact matches
                        continue

                    # Calculate similarity
                    similarity = SequenceMatcher(None, word, vocab_word).ratio()

                    if similarity > 0.8:  # High similarity threshold
                        best_matches.append((vocab_word, similarity))

                # Sort by similarity
                best_matches.sort(key=lambda x: x[1], reverse=True)

                # Take top matches
                for match_word, similarity in best_matches[:3]:
                    # Create corrected query
                    corrected = query.replace(word, match_word)

                    suggestions.append(
                        SearchSuggestion(
                            text=corrected,
                            score=similarity * 0.8,  # Slightly lower score for corrections
                            type="correction",
                            metadata={"original": query, "correction": {word: match_word}},
                        )
                    )

        except Exception as e:
            logger.error(f"Failed to get spell corrections: {e}")

        return suggestions

    def _calculate_match_score(self, query: str, text: str) -> float:
        """Calculate match score between query and text."""
        if not query or not text:
            return 0.0

        # Exact match
        if query == text:
            return 1.0

        # Prefix match
        if text.startswith(query):
            return 0.9 - (len(text) - len(query)) / len(text) * 0.3

        # Contains match
        if query in text:
            position = text.index(query)
            return 0.6 - position / len(text) * 0.2

        # No match
        return 0.0

    def _deduplicate_suggestions(self, suggestions: List[SearchSuggestion]) -> List[SearchSuggestion]:
        """Remove duplicate suggestions, keeping highest scores."""
        seen = {}

        for suggestion in suggestions:
            key = suggestion.text.lower()

            if key not in seen or suggestion.score > seen[key].score:
                seen[key] = suggestion

        return list(seen.values())

    async def precompute_suggestions(self) -> bool:
        """
        Precompute common suggestions for better performance.

        This can be run periodically to build a suggestion index.
        """
        try:
            logger.info("Starting suggestion precomputation")

            # Get popular starting letters/words
            cutoff_date = (datetime.utcnow() - timedelta(days=30)).isoformat()

            searches = await query_documents(
                collection=self._analytics_collection,
                filters={"timestamp__gte": cutoff_date, "result_count__gt": 0},
                limit=10000,
            )

            # Build prefix tree of common queries
            prefix_tree = defaultdict(list)

            for search in searches:
                query = search.get("query", "").lower().strip()
                if not query:
                    continue

                # Add to prefix tree
                for i in range(2, min(len(query) + 1, 10)):
                    prefix = query[:i]
                    prefix_tree[prefix].append(query)

            # Store precomputed suggestions
            # This could be stored in a cache or separate collection
            logger.info(f"Precomputed suggestions for {len(prefix_tree)} prefixes")

            return True

        except Exception as e:
            logger.error(f"Failed to precompute suggestions: {e}")
            return False
