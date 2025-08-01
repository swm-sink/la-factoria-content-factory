"""
Search-related data models for content discovery and filtering.

This module defines the data structures used for search operations,
including search queries, filters, facets, and results.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class SortOrder(str, Enum):
    """Sort order enumeration."""

    ASC = "asc"
    DESC = "desc"


class SearchOperator(str, Enum):
    """Search operator enumeration for advanced queries."""

    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


class SearchFilter(BaseModel):
    """Individual search filter."""

    field: str = Field(..., description="Field name to filter on")
    operator: SearchOperator = Field(default=SearchOperator.EQUALS, description="Filter operator")
    value: Any = Field(..., description="Filter value")


class DateRange(BaseModel):
    """Date range filter."""

    start: Optional[datetime] = Field(None, description="Start date (inclusive)")
    end: Optional[datetime] = Field(None, description="End date (inclusive)")

    @field_validator("end")
    @classmethod
    def validate_date_range(cls, v: Optional[datetime], values: Dict[str, Any]) -> Optional[datetime]:
        if v and values.get("start") and v < values["start"]:
            raise ValueError("End date must be after start date")
        return v


class SortField(BaseModel):
    """Sort field specification."""

    field: str = Field(..., description="Field name to sort by")
    order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")


class SearchFacet(BaseModel):
    """Search facet for aggregations."""

    field: str = Field(..., description="Field to aggregate")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of facet values")


class SavedSearch(BaseModel):
    """Saved search configuration."""

    id: Optional[str] = None
    user_id: str
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    sort: Optional[List[SortField]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = Field(default=False)
    tags: List[str] = Field(default_factory=list)


class SearchAnalytics(BaseModel):
    """Search analytics data."""

    query: str
    user_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    result_count: int = Field(ge=0)
    clicked_results: List[str] = Field(default_factory=list)
    search_duration_ms: float = Field(ge=0)
    filters_used: Dict[str, Any] = Field(default_factory=dict)
    facets_used: List[str] = Field(default_factory=list)


class SearchSuggestion(BaseModel):
    """Search suggestion item."""

    text: str
    score: float = Field(ge=0, le=1)
    type: str = Field(default="query")  # query, filter, tag, etc.
    metadata: Optional[Dict[str, Any]] = None


class FacetValue(BaseModel):
    """Facet value with count."""

    value: str
    count: int = Field(ge=0)
    label: Optional[str] = None  # Human-readable label


class FacetResult(BaseModel):
    """Facet aggregation result."""

    field: str
    values: List[FacetValue]
    total_count: int = Field(ge=0)
    missing_count: int = Field(default=0, ge=0)


class SearchHit(BaseModel):
    """Individual search result."""

    id: str
    score: float = Field(ge=0)
    source: Dict[str, Any]
    highlights: Optional[Dict[str, List[str]]] = None
    explanation: Optional[str] = None


class SearchResult(BaseModel):
    """Complete search result response."""

    query: Optional[str] = None
    total: int = Field(ge=0)
    hits: List[SearchHit]
    facets: Optional[Dict[str, FacetResult]] = None
    took_ms: float = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_pages: int = Field(ge=0)
    suggestions: Optional[List[SearchSuggestion]] = None


class SearchIndex(BaseModel):
    """Search index document structure."""

    id: str
    user_id: str
    title: str
    overview: Optional[str] = None
    content_type: str
    difficulty: Optional[str] = None
    target_audience: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    quality_score: Optional[float] = Field(None, ge=0, le=1)
    estimated_duration: Optional[int] = Field(None, ge=0)  # in minutes
    status: str = Field(default="published")
    searchable_text: str  # Combined text for full-text search
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
