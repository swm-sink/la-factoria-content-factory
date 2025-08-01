"""
Pydantic schemas for search API endpoints.

This module defines request and response schemas for the search functionality,
including basic search, advanced search, faceted search, and saved searches.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

from app.models.search import SearchOperator, SortField, SortOrder


class BasicSearchRequest(BaseModel):
    """Basic search request schema."""

    q: str = Field(..., min_length=1, max_length=500, description="Search query")
    content_type: Optional[str] = Field(None, description="Filter by content type")
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Results per page")
    sort: Optional[str] = Field(None, description="Sort field (prefix with - for desc)")


class AdvancedSearchFilters(BaseModel):
    """Advanced search filters."""

    content_type: Optional[List[str]] = Field(None, description="Content types to include")
    difficulty: Optional[List[str]] = Field(None, description="Difficulty levels")
    target_audience: Optional[List[str]] = Field(None, description="Target audiences")
    tags: Optional[List[str]] = Field(None, description="Tags to filter by")
    categories: Optional[List[str]] = Field(None, description="Categories to filter by")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range with start/end")
    quality_score_min: Optional[float] = Field(None, ge=0, le=1, description="Minimum quality score")
    quality_score_max: Optional[float] = Field(None, ge=0, le=1, description="Maximum quality score")
    duration_min: Optional[int] = Field(None, ge=0, description="Minimum duration in minutes")
    duration_max: Optional[int] = Field(None, ge=0, description="Maximum duration in minutes")
    status: Optional[List[str]] = Field(None, description="Content status filters")
    user_id: Optional[str] = Field(None, description="Filter by user (admin only)")

    @field_validator("date_range")
    @classmethod
    def validate_date_range(cls, v: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        if v:
            if "start" in v and "end" in v:
                try:
                    start = datetime.fromisoformat(v["start"])
                    end = datetime.fromisoformat(v["end"])
                    if end < start:
                        raise ValueError("End date must be after start date")
                except ValueError as e:
                    raise ValueError(f"Invalid date format: {e}")
        return v


class AdvancedSearchRequest(BaseModel):
    """Advanced search request schema."""

    query: Optional[str] = Field(None, max_length=500, description="Search query text")
    filters: Optional[AdvancedSearchFilters] = Field(None, description="Search filters")
    sort: Optional[List[SortField]] = Field(None, description="Sort criteria")
    facets: Optional[List[str]] = Field(None, description="Fields to aggregate for faceted search")
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Results per page")
    highlight: bool = Field(default=True, description="Include search highlights")
    explain: bool = Field(default=False, description="Include relevance explanation")


class SearchSuggestionsRequest(BaseModel):
    """Search suggestions request schema."""

    q: str = Field(..., min_length=1, max_length=100, description="Partial query for suggestions")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum suggestions to return")
    types: Optional[List[str]] = Field(None, description="Types of suggestions to include")


class SaveSearchRequest(BaseModel):
    """Save search request schema."""

    name: str = Field(..., min_length=1, max_length=100, description="Search name")
    description: Optional[str] = Field(None, max_length=500, description="Search description")
    query: Optional[str] = Field(None, description="Search query")
    filters: Optional[AdvancedSearchFilters] = Field(None, description="Search filters")
    sort: Optional[List[SortField]] = Field(None, description="Sort criteria")
    is_public: bool = Field(default=False, description="Make search public")
    tags: Optional[List[str]] = Field(None, description="Tags for organizing saved searches")


class SearchAnalyticsRequest(BaseModel):
    """Search analytics request schema."""

    period: str = Field(default="7d", description="Time period (1d, 7d, 30d, etc.)")
    limit: int = Field(default=20, ge=1, le=100, description="Number of results")
    metric: str = Field(default="popular", description="Metric type (popular, trending, failed)")
    user_id: Optional[str] = Field(None, description="Filter by user (admin only)")


class SearchHitResponse(BaseModel):
    """Individual search hit response."""

    id: str
    title: str
    overview: Optional[str] = None
    content_type: str
    difficulty: Optional[str] = None
    target_audience: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    quality_score: Optional[float] = None
    estimated_duration: Optional[int] = None
    highlights: Optional[Dict[str, List[str]]] = None
    score: float = Field(ge=0, description="Relevance score")


class FacetValueResponse(BaseModel):
    """Facet value response."""

    value: str
    count: int
    label: Optional[str] = None


class FacetResponse(BaseModel):
    """Facet aggregation response."""

    field: str
    values: List[FacetValueResponse]
    total: int


class SearchResponse(BaseModel):
    """Search response schema."""

    query: Optional[str] = None
    total: int = Field(ge=0, description="Total matching results")
    hits: List[SearchHitResponse]
    facets: Optional[Dict[str, FacetResponse]] = None
    page: int
    page_size: int
    total_pages: int
    took_ms: float = Field(ge=0, description="Search duration in milliseconds")
    suggestions: Optional[List[Dict[str, Any]]] = None


class SearchSuggestionsResponse(BaseModel):
    """Search suggestions response."""

    suggestions: List[Dict[str, Any]]
    took_ms: float


class SavedSearchResponse(BaseModel):
    """Saved search response."""

    id: str
    name: str
    description: Optional[str] = None
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    sort: Optional[List[Dict[str, str]]] = None
    is_public: bool
    tags: List[str]
    created_at: datetime
    updated_at: datetime


class SearchAnalyticsResponse(BaseModel):
    """Search analytics response."""

    period: str
    metric: str
    data: List[Dict[str, Any]]
    total_searches: int
    unique_users: int
    avg_results: float
    avg_duration_ms: float
