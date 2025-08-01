"""
Search service package for content discovery and filtering.

This package provides search functionality including:
- Full-text search across content
- Advanced filtering and faceted search
- Search suggestions and auto-complete
- Search analytics and tracking
- Saved searches
"""

from .aggregations import AggregationBuilder, FacetConfig
from .base import SearchBackend, SearchConfig
from .query_builder import QueryBuilder, SearchQuery
from .simple_search import SimpleSearchBackend

__all__ = [
    "SearchBackend",
    "SearchConfig",
    "SimpleSearchBackend",
    "QueryBuilder",
    "SearchQuery",
    "AggregationBuilder",
    "FacetConfig",
]
