"""
Search API endpoints for content discovery and filtering.

This module provides comprehensive search functionality including:
- Basic and advanced search
- Faceted search with aggregations
- Search suggestions and auto-complete
- Saved searches
- Search analytics
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.api.deps import get_current_user
from app.core.config.settings import get_settings
from app.models.pydantic.user import User
from app.models.search import SavedSearch
from app.schemas.search import (
    AdvancedSearchRequest,
    BasicSearchRequest,
    FacetResponse,
    SavedSearchResponse,
    SaveSearchRequest,
    SearchAnalyticsRequest,
    SearchAnalyticsResponse,
    SearchHitResponse,
    SearchResponse,
    SearchSuggestionsRequest,
    SearchSuggestionsResponse,
)
from app.services.search import SearchBackend, SearchConfig, SimpleSearchBackend
from app.services.search_analytics import SearchAnalyticsService
from app.services.search_suggestions import SearchSuggestionsService
from app.tasks.search_indexing import SearchIndexingTasks

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/search", tags=["search"])


# Initialize services
search_config = SearchConfig()
search_backend = SimpleSearchBackend(search_config)
analytics_service = SearchAnalyticsService()
suggestions_service = SearchSuggestionsService()
indexing_tasks = SearchIndexingTasks(search_backend)


@router.get("", response_model=SearchResponse)
async def basic_search(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Results per page"),
    sort: Optional[str] = Query(None, description="Sort field (prefix with - for desc)"),
    current_user: User = Depends(get_current_user),
):
    """
    Perform a basic search across content.

    This endpoint provides simple search functionality with basic filtering
    and sorting options.
    """
    try:
        # Build advanced search request from basic parameters
        filters = {}
        if content_type:
            filters["content_type"] = [content_type]

        # Parse sort parameter
        sort_fields = []
        if sort:
            from app.models.search import SortField, SortOrder

            if sort.startswith("-"):
                sort_fields.append(SortField(field=sort[1:], order=SortOrder.DESC))
            else:
                sort_fields.append(SortField(field=sort, order=SortOrder.ASC))

        # Create advanced request
        from app.schemas.search import AdvancedSearchFilters

        request = AdvancedSearchRequest(
            query=q,
            filters=AdvancedSearchFilters(**filters) if filters else None,
            sort=sort_fields,
            page=page,
            size=size,
            highlight=True,
        )

        # Perform search
        result = await search_backend.search(request, user_id=current_user.id)

        # Convert to response format
        hits = []
        for hit in result.hits:
            hit_response = SearchHitResponse(
                id=hit.source.get("id"),
                title=hit.source.get("title"),
                overview=hit.source.get("overview"),
                content_type=hit.source.get("content_type"),
                difficulty=hit.source.get("difficulty"),
                target_audience=hit.source.get("target_audience"),
                tags=hit.source.get("tags", []),
                created_at=hit.source.get("created_at"),
                updated_at=hit.source.get("updated_at"),
                quality_score=hit.source.get("quality_score"),
                estimated_duration=hit.source.get("estimated_duration"),
                highlights=hit.highlights,
                score=hit.score,
            )
            hits.append(hit_response)

        return SearchResponse(
            query=result.query,
            total=result.total,
            hits=hits,
            facets=None,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages,
            took_ms=result.took_ms,
        )

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Search operation failed")


@router.post("/advanced", response_model=SearchResponse)
async def advanced_search(
    request: AdvancedSearchRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Perform an advanced search with complex filters and faceting.

    This endpoint provides full search capabilities including:
    - Complex query combinations
    - Multiple filters and ranges
    - Faceted search for navigation
    - Custom sorting
    - Result highlighting
    """
    try:
        # Admin users can search across all users' content
        user_id = None if current_user.is_admin else current_user.id

        # Perform search
        result = await search_backend.search(request, user_id=user_id)

        # Convert to response format
        hits = []
        for hit in result.hits:
            hit_response = SearchHitResponse(
                id=hit.source.get("id"),
                title=hit.source.get("title"),
                overview=hit.source.get("overview"),
                content_type=hit.source.get("content_type"),
                difficulty=hit.source.get("difficulty"),
                target_audience=hit.source.get("target_audience"),
                tags=hit.source.get("tags", []),
                created_at=hit.source.get("created_at"),
                updated_at=hit.source.get("updated_at"),
                quality_score=hit.source.get("quality_score"),
                estimated_duration=hit.source.get("estimated_duration"),
                highlights=hit.highlights if request.highlight else None,
                score=hit.score,
            )
            hits.append(hit_response)

        # Convert facets if present
        facets = None
        if result.facets:
            facets = {}
            for field, facet_result in result.facets.items():
                facets[field] = FacetResponse(
                    field=facet_result.field,
                    values=[{"value": v.value, "count": v.count, "label": v.label} for v in facet_result.values],
                    total=facet_result.total_count,
                )

        return SearchResponse(
            query=result.query,
            total=result.total,
            hits=hits,
            facets=facets,
            page=result.page,
            page_size=result.page_size,
            total_pages=result.total_pages,
            took_ms=result.took_ms,
            suggestions=result.suggestions,
        )

    except Exception as e:
        logger.error(f"Advanced search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Advanced search operation failed"
        )


@router.get("/suggestions", response_model=SearchSuggestionsResponse)
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="Partial query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum suggestions"),
    types: Optional[List[str]] = Query(None, description="Suggestion types to include"),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Get search suggestions for auto-complete.

    Returns suggestions based on:
    - Popular searches
    - User's search history
    - Content titles
    - Tags and categories
    - Spelling corrections
    """
    try:
        # Get suggestions
        suggestions = await suggestions_service.get_suggestions(
            query=q, user_id=current_user.id if current_user else None, limit=limit, types=types
        )

        # Convert to response format
        suggestion_list = [
            {"text": s.text, "score": s.score, "type": s.type, "metadata": s.metadata} for s in suggestions
        ]

        return SearchSuggestionsResponse(
            suggestions=suggestion_list, took_ms=0.0  # Would track actual time in production
        )

    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get search suggestions"
        )


@router.post("/saved", response_model=SavedSearchResponse)
async def save_search(
    request: SaveSearchRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Save a search configuration for later use.

    Saved searches can be:
    - Private to the user
    - Public for all users to see
    - Tagged for organization
    """
    try:
        # Create saved search
        saved_search = SavedSearch(
            user_id=current_user.id,
            name=request.name,
            description=request.description,
            query=request.query,
            filters=request.filters.dict() if request.filters else None,
            sort=[s.dict() for s in request.sort] if request.sort else None,
            is_public=request.is_public,
            tags=request.tags or [],
        )

        # Save to backend
        saved = await search_backend.save_search(saved_search)

        return SavedSearchResponse(
            id=saved.id,
            name=saved.name,
            description=saved.description,
            query=saved.query,
            filters=saved.filters,
            sort=saved.sort,
            is_public=saved.is_public,
            tags=saved.tags,
            created_at=saved.created_at,
            updated_at=saved.updated_at,
        )

    except Exception as e:
        logger.error(f"Failed to save search: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save search")


@router.get("/saved", response_model=List[SavedSearchResponse])
async def get_saved_searches(
    include_public: bool = Query(True, description="Include public searches"),
    current_user: User = Depends(get_current_user),
):
    """
    Get saved searches for the current user.

    Returns:
    - User's own saved searches
    - Optionally, public searches from other users
    """
    try:
        # Get saved searches
        searches = await search_backend.get_saved_searches(user_id=current_user.id, include_public=include_public)

        # Convert to response format
        return [
            SavedSearchResponse(
                id=s.id,
                name=s.name,
                description=s.description,
                query=s.query,
                filters=s.filters,
                sort=s.sort,
                is_public=s.is_public,
                tags=s.tags,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in searches
        ]

    except Exception as e:
        logger.error(f"Failed to get saved searches: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get saved searches")


@router.delete("/saved/{search_id}")
async def delete_saved_search(
    search_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a saved search."""
    try:
        success = await search_backend.delete_saved_search(search_id=search_id, user_id=current_user.id)

        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved search not found or access denied")

        return {"message": "Saved search deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete saved search: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete saved search")


@router.get("/analytics/popular", response_model=SearchAnalyticsResponse)
async def get_popular_searches(
    period: str = Query("7d", description="Time period (1d, 7d, 30d)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_user: User = Depends(get_current_user),
):
    """
    Get popular searches analytics.

    Returns the most popular searches within the specified time period.
    """
    try:
        # Parse period
        import re

        match = re.match(r"(\d+)d", period)
        days = int(match.group(1)) if match else 7

        # Get popular searches
        popular = await analytics_service.get_popular_searches(days=days, limit=limit)

        # Get metrics
        metrics = await analytics_service.get_search_metrics(days=days)

        return SearchAnalyticsResponse(
            period=period,
            metric="popular",
            data=popular,
            total_searches=metrics.get("total_searches", 0),
            unique_users=metrics.get("unique_users", 0),
            avg_results=metrics.get("avg_results_per_search", 0),
            avg_duration_ms=metrics.get("avg_duration_ms", 0),
        )

    except Exception as e:
        logger.error(f"Failed to get popular searches: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get search analytics")


@router.get("/analytics/trending", response_model=SearchAnalyticsResponse)
async def get_trending_searches(
    current_period: str = Query("1d", description="Current period"),
    comparison_period: str = Query("7d", description="Comparison period"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_user: User = Depends(get_current_user),
):
    """
    Get trending searches (increasing in popularity).

    Compares search frequency between two time periods to identify trends.
    """
    try:
        # Parse periods
        import re

        current_match = re.match(r"(\d+)d", current_period)
        current_days = int(current_match.group(1)) if current_match else 1

        comparison_match = re.match(r"(\d+)d", comparison_period)
        comparison_days = int(comparison_match.group(1)) if comparison_match else 7

        # Get trending searches
        trending = await analytics_service.get_trending_searches(
            current_period_days=current_days, previous_period_days=comparison_days, limit=limit
        )

        # Get metrics for current period
        metrics = await analytics_service.get_search_metrics(days=current_days)

        return SearchAnalyticsResponse(
            period=current_period,
            metric="trending",
            data=trending,
            total_searches=metrics.get("total_searches", 0),
            unique_users=metrics.get("unique_users", 0),
            avg_results=metrics.get("avg_results_per_search", 0),
            avg_duration_ms=metrics.get("avg_duration_ms", 0),
        )

    except Exception as e:
        logger.error(f"Failed to get trending searches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get trending analytics"
        )


@router.get("/analytics/failed", response_model=SearchAnalyticsResponse)
async def get_failed_searches(
    period: str = Query("7d", description="Time period"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_user: User = Depends(get_current_user),
):
    """
    Get searches that returned no results.

    Useful for identifying content gaps and improving search experience.
    """
    try:
        # Parse period
        import re

        match = re.match(r"(\d+)d", period)
        days = int(match.group(1)) if match else 7

        # Get failed searches
        failed = await analytics_service.get_failed_searches(days=days, limit=limit)

        # Get metrics
        metrics = await analytics_service.get_search_metrics(days=days)

        return SearchAnalyticsResponse(
            period=period,
            metric="failed",
            data=failed,
            total_searches=metrics.get("total_searches", 0),
            unique_users=metrics.get("unique_users", 0),
            avg_results=metrics.get("avg_results_per_search", 0),
            avg_duration_ms=metrics.get("avg_duration_ms", 0),
        )

    except Exception as e:
        logger.error(f"Failed to get failed searches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get failed search analytics"
        )


@router.get("/analytics/user/{user_id}")
async def get_user_search_history(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Days to look back"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
    current_user: User = Depends(get_current_user),
):
    """
    Get search history for a specific user.

    Note: Users can only view their own history unless they are admins.
    """
    try:
        # Check permissions
        if user_id != current_user.id and not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        # Get user search history
        history = await analytics_service.get_user_search_history(user_id=user_id, days=days, limit=limit)

        return {"user_id": user_id, "period_days": days, "searches": history}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user search history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get user search history"
        )


@router.post("/reindex")
async def trigger_reindex(
    since_days: Optional[int] = Query(None, description="Only reindex content from last N days"),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger a search index rebuild.

    Note: This operation requires admin privileges.
    """
    try:
        # Check admin permission
        if not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

        # Trigger reindex task
        from datetime import datetime, timedelta

        since_date = None
        if since_days:
            since_date = datetime.utcnow() - timedelta(days=since_days)

        # In a production environment, this would be queued as a background task
        # For now, we'll run it synchronously with a reasonable batch size
        results = await indexing_tasks.reindex_all_content(batch_size=50, since_date=since_date)

        return {"message": "Reindexing completed", "results": results}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger reindex: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to trigger reindex")


@router.get("/stats")
async def get_search_stats(
    current_user: User = Depends(get_current_user),
):
    """
    Get search index statistics.

    Note: This operation requires admin privileges.
    """
    try:
        # Check admin permission
        if not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

        # Get index stats
        stats = await search_backend.get_index_stats()

        return stats

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get search stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get search statistics")
