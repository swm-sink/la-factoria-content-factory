"""
Query builder for constructing complex search queries.

This module provides a flexible query builder pattern for constructing
search queries that can be translated to different backend formats.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from app.models.search import SearchOperator, SortField
from app.schemas.search import AdvancedSearchFilters


class QueryType(str, Enum):
    """Query type enumeration."""

    MATCH = "match"
    TERM = "term"
    RANGE = "range"
    WILDCARD = "wildcard"
    PREFIX = "prefix"
    FUZZY = "fuzzy"
    BOOL = "bool"


class QueryClause(BaseModel):
    """Individual query clause."""

    type: QueryType
    field: Optional[str] = None
    value: Optional[Any] = None
    operator: Optional[SearchOperator] = None
    boost: float = Field(default=1.0, ge=0)
    options: Dict[str, Any] = Field(default_factory=dict)


class BoolQuery(BaseModel):
    """Boolean query combining multiple clauses."""

    must: List[QueryClause] = Field(default_factory=list)
    should: List[QueryClause] = Field(default_factory=list)
    must_not: List[QueryClause] = Field(default_factory=list)
    filter: List[QueryClause] = Field(default_factory=list)
    minimum_should_match: Optional[int] = None


class SearchQuery(BaseModel):
    """Complete search query."""

    query: Optional[Union[QueryClause, BoolQuery]] = None
    filters: List[QueryClause] = Field(default_factory=list)
    sort: List[SortField] = Field(default_factory=list)
    facets: List[str] = Field(default_factory=list)
    highlight_fields: List[str] = Field(default_factory=list)
    from_: int = Field(default=0, alias="from", ge=0)
    size: int = Field(default=20, ge=1)

    class Config:
        populate_by_name = True


class QueryBuilder:
    """
    Fluent interface for building search queries.

    Example:
        query = (QueryBuilder()
            .match("title", "machine learning")
            .filter_term("content_type", "study_guide")
            .filter_range("quality_score", gte=0.7)
            .sort_by("created_at", "desc")
            .facet("content_type")
            .paginate(page=2, size=20)
            .build())
    """

    def __init__(self):
        """Initialize query builder."""
        self._bool_query = BoolQuery()
        self._filters: List[QueryClause] = []
        self._sort: List[SortField] = []
        self._facets: List[str] = []
        self._highlight_fields: List[str] = []
        self._from = 0
        self._size = 20

    def match(self, field: str, value: str, boost: float = 1.0) -> "QueryBuilder":
        """Add a match query (full-text search)."""
        clause = QueryClause(type=QueryType.MATCH, field=field, value=value, boost=boost)
        self._bool_query.must.append(clause)
        return self

    def match_all(self, query: str, fields: List[str], boost: float = 1.0) -> "QueryBuilder":
        """Match query across multiple fields."""
        for field in fields:
            clause = QueryClause(type=QueryType.MATCH, field=field, value=query, boost=boost)
            self._bool_query.should.append(clause)

        if len(fields) > 1:
            self._bool_query.minimum_should_match = 1
        return self

    def term(self, field: str, value: Any, boost: float = 1.0) -> "QueryBuilder":
        """Add an exact term query."""
        clause = QueryClause(type=QueryType.TERM, field=field, value=value, boost=boost)
        self._bool_query.must.append(clause)
        return self

    def filter_term(self, field: str, value: Any) -> "QueryBuilder":
        """Add a term filter (doesn't affect scoring)."""
        clause = QueryClause(type=QueryType.TERM, field=field, value=value)
        self._filters.append(clause)
        return self

    def filter_terms(self, field: str, values: List[Any]) -> "QueryBuilder":
        """Add a terms filter (match any of the values)."""
        clause = QueryClause(type=QueryType.TERM, field=field, value=values, operator=SearchOperator.IN)
        self._filters.append(clause)
        return self

    def filter_range(
        self,
        field: str,
        gte: Optional[Any] = None,
        gt: Optional[Any] = None,
        lte: Optional[Any] = None,
        lt: Optional[Any] = None,
    ) -> "QueryBuilder":
        """Add a range filter."""
        options = {}
        if gte is not None:
            options["gte"] = gte
        if gt is not None:
            options["gt"] = gt
        if lte is not None:
            options["lte"] = lte
        if lt is not None:
            options["lt"] = lt

        clause = QueryClause(type=QueryType.RANGE, field=field, options=options)
        self._filters.append(clause)
        return self

    def wildcard(self, field: str, pattern: str, boost: float = 1.0) -> "QueryBuilder":
        """Add a wildcard query."""
        clause = QueryClause(type=QueryType.WILDCARD, field=field, value=pattern, boost=boost)
        self._bool_query.must.append(clause)
        return self

    def prefix(self, field: str, prefix: str, boost: float = 1.0) -> "QueryBuilder":
        """Add a prefix query."""
        clause = QueryClause(type=QueryType.PREFIX, field=field, value=prefix, boost=boost)
        self._bool_query.must.append(clause)
        return self

    def fuzzy(self, field: str, value: str, fuzziness: int = 2) -> "QueryBuilder":
        """Add a fuzzy query."""
        clause = QueryClause(type=QueryType.FUZZY, field=field, value=value, options={"fuzziness": fuzziness})
        self._bool_query.must.append(clause)
        return self

    def must_not(self, field: str, value: Any) -> "QueryBuilder":
        """Add a must_not clause."""
        clause = QueryClause(type=QueryType.TERM, field=field, value=value)
        self._bool_query.must_not.append(clause)
        return self

    def sort_by(self, field: str, order: str = "asc") -> "QueryBuilder":
        """Add a sort field."""
        from app.models.search import SortOrder

        sort_field = SortField(field=field, order=SortOrder.ASC if order.lower() == "asc" else SortOrder.DESC)
        self._sort.append(sort_field)
        return self

    def facet(self, field: str) -> "QueryBuilder":
        """Add a facet field."""
        self._facets.append(field)
        return self

    def highlight(self, fields: List[str]) -> "QueryBuilder":
        """Add fields to highlight."""
        self._highlight_fields.extend(fields)
        return self

    def paginate(self, page: int = 1, size: int = 20) -> "QueryBuilder":
        """Set pagination parameters."""
        self._from = (page - 1) * size
        self._size = size
        return self

    def from_filters(self, filters: AdvancedSearchFilters) -> "QueryBuilder":
        """Build query from advanced search filters."""
        if filters.content_type:
            self.filter_terms("content_type", filters.content_type)

        if filters.difficulty:
            self.filter_terms("difficulty", filters.difficulty)

        if filters.target_audience:
            self.filter_terms("target_audience", filters.target_audience)

        if filters.tags:
            self.filter_terms("tags", filters.tags)

        if filters.categories:
            self.filter_terms("categories", filters.categories)

        if filters.status:
            self.filter_terms("status", filters.status)

        if filters.user_id:
            self.filter_term("user_id", filters.user_id)

        if filters.quality_score_min is not None or filters.quality_score_max is not None:
            self.filter_range("quality_score", gte=filters.quality_score_min, lte=filters.quality_score_max)

        if filters.duration_min is not None or filters.duration_max is not None:
            self.filter_range("estimated_duration", gte=filters.duration_min, lte=filters.duration_max)

        if filters.date_range:
            date_range = filters.date_range
            if "start" in date_range or "end" in date_range:
                self.filter_range("created_at", gte=date_range.get("start"), lte=date_range.get("end"))

        return self

    def build(self) -> SearchQuery:
        """Build the final search query."""
        # Determine the main query
        if self._bool_query.must or self._bool_query.should or self._bool_query.must_not or self._bool_query.filter:
            query = self._bool_query
        else:
            query = None

        return SearchQuery(
            query=query,
            filters=self._filters,
            sort=self._sort,
            facets=self._facets,
            highlight_fields=self._highlight_fields,
            from_=self._from,
            size=self._size,
        )
