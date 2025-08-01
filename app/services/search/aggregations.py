"""
Search aggregations and faceting functionality.

This module provides utilities for building search aggregations
and processing faceted search results.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from app.models.search import FacetResult, FacetValue


class FacetConfig(BaseModel):
    """Configuration for a search facet."""

    field: str
    size: int = Field(default=10, ge=1, le=100)
    order_by: str = Field(default="count")  # count or value
    order_desc: bool = Field(default=True)
    include_missing: bool = Field(default=False)
    min_count: int = Field(default=1, ge=0)


class DateHistogramConfig(BaseModel):
    """Configuration for date histogram aggregation."""

    field: str = Field(default="created_at")
    interval: str = Field(default="day")  # hour, day, week, month, year
    format: str = Field(default="%Y-%m-%d")
    min_doc_count: int = Field(default=0)


class AggregationBuilder:
    """Builder for search aggregations."""

    def __init__(self):
        """Initialize aggregation builder."""
        self.facets: Dict[str, FacetConfig] = {}
        self.date_histograms: Dict[str, DateHistogramConfig] = {}
        self.stats_fields: List[str] = []

    def add_facet(
        self,
        field: str,
        size: int = 10,
        order_by: str = "count",
        order_desc: bool = True,
        include_missing: bool = False,
        min_count: int = 1,
    ) -> "AggregationBuilder":
        """Add a facet aggregation."""
        config = FacetConfig(
            field=field,
            size=size,
            order_by=order_by,
            order_desc=order_desc,
            include_missing=include_missing,
            min_count=min_count,
        )
        self.facets[field] = config
        return self

    def add_date_histogram(
        self, field: str = "created_at", interval: str = "day", format: str = "%Y-%m-%d", min_doc_count: int = 0
    ) -> "AggregationBuilder":
        """Add a date histogram aggregation."""
        config = DateHistogramConfig(field=field, interval=interval, format=format, min_doc_count=min_doc_count)
        self.date_histograms[field] = config
        return self

    def add_stats(self, field: str) -> "AggregationBuilder":
        """Add statistical aggregation for a numeric field."""
        self.stats_fields.append(field)
        return self

    def build(self) -> Dict[str, Any]:
        """Build aggregation configuration."""
        aggs = {}

        # Add facet aggregations
        for field, config in self.facets.items():
            aggs[field] = {
                "terms": {
                    "field": field,
                    "size": config.size,
                    "min_doc_count": config.min_count,
                    "order": {
                        "_count" if config.order_by == "count" else "_key": "desc" if config.order_desc else "asc"
                    },
                }
            }

            if config.include_missing:
                aggs[f"{field}_missing"] = {"missing": {"field": field}}

        # Add date histogram aggregations
        for field, config in self.date_histograms.items():
            aggs[f"{field}_histogram"] = {
                "date_histogram": {
                    "field": field,
                    "interval": config.interval,
                    "format": config.format,
                    "min_doc_count": config.min_doc_count,
                }
            }

        # Add stats aggregations
        for field in self.stats_fields:
            aggs[f"{field}_stats"] = {"stats": {"field": field}}

        return aggs


class FacetProcessor:
    """Process search results to extract facets."""

    @staticmethod
    def process_simple_facets(
        documents: List[Dict[str, Any]], facet_fields: List[str], facet_configs: Optional[Dict[str, FacetConfig]] = None
    ) -> Dict[str, FacetResult]:
        """
        Process documents to extract facet counts.

        This is used for simple search backends that don't have
        native aggregation support.
        """
        facet_configs = facet_configs or {}
        results = {}

        for field in facet_fields:
            config = facet_configs.get(field, FacetConfig(field=field))

            # Count values
            value_counts: Dict[str, int] = defaultdict(int)
            missing_count = 0

            for doc in documents:
                value = doc.get(field)

                if value is None:
                    missing_count += 1
                elif isinstance(value, list):
                    # Handle multi-valued fields
                    for v in value:
                        if v is not None:
                            value_counts[str(v)] += 1
                else:
                    value_counts[str(value)] += 1

            # Build facet values
            facet_values = []
            for value, count in value_counts.items():
                if count >= config.min_count:
                    facet_values.append(
                        FacetValue(value=value, count=count, label=FacetProcessor._get_label(field, value))
                    )

            # Sort facet values
            if config.order_by == "count":
                facet_values.sort(key=lambda x: x.count, reverse=config.order_desc)
            else:
                facet_values.sort(key=lambda x: x.value, reverse=config.order_desc)

            # Limit to configured size
            facet_values = facet_values[: config.size]

            # Create facet result
            results[field] = FacetResult(
                field=field,
                values=facet_values,
                total_count=sum(value_counts.values()),
                missing_count=missing_count if config.include_missing else 0,
            )

        return results

    @staticmethod
    def _get_label(field: str, value: str) -> Optional[str]:
        """Get human-readable label for facet value."""
        # Define label mappings for common fields
        labels = {
            "content_type": {
                "study_guide": "Study Guide",
                "flashcards": "Flashcards",
                "podcast": "Podcast",
                "one_pager": "One-Pager",
                "faqs": "FAQs",
                "reading_guide": "Reading Guide",
                "detailed_reading": "Detailed Reading",
            },
            "difficulty": {"beginner": "Beginner", "intermediate": "Intermediate", "advanced": "Advanced"},
            "target_audience": {
                "elementary": "Elementary School",
                "middle_school": "Middle School",
                "high_school": "High School",
                "university": "University",
                "professional": "Professional",
            },
            "status": {"draft": "Draft", "published": "Published", "archived": "Archived"},
        }

        field_labels = labels.get(field, {})
        return field_labels.get(value, value.replace("_", " ").title())

    @staticmethod
    def process_date_histogram(
        documents: List[Dict[str, Any]], field: str, interval: str = "day"
    ) -> List[Dict[str, Any]]:
        """Process documents to create date histogram."""
        # Group documents by date interval
        date_buckets: Dict[str, int] = defaultdict(int)

        for doc in documents:
            date_value = doc.get(field)
            if date_value:
                if isinstance(date_value, str):
                    date_value = datetime.fromisoformat(date_value.replace("Z", "+00:00"))

                # Determine bucket key based on interval
                if interval == "hour":
                    bucket_key = date_value.strftime("%Y-%m-%d %H:00")
                elif interval == "day":
                    bucket_key = date_value.strftime("%Y-%m-%d")
                elif interval == "week":
                    # Start of week
                    start_of_week = date_value - timedelta(days=date_value.weekday())
                    bucket_key = start_of_week.strftime("%Y-%m-%d")
                elif interval == "month":
                    bucket_key = date_value.strftime("%Y-%m")
                elif interval == "year":
                    bucket_key = date_value.strftime("%Y")
                else:
                    bucket_key = date_value.strftime("%Y-%m-%d")

                date_buckets[bucket_key] += 1

        # Convert to list of buckets
        buckets = [{"key": key, "doc_count": count} for key, count in sorted(date_buckets.items())]

        return buckets

    @staticmethod
    def get_unique_values(documents: List[Dict[str, Any]], field: str, limit: Optional[int] = None) -> List[str]:
        """Get unique values for a field."""
        values: Set[str] = set()

        for doc in documents:
            value = doc.get(field)
            if value is not None:
                if isinstance(value, list):
                    values.update(str(v) for v in value if v is not None)
                else:
                    values.add(str(value))

        sorted_values = sorted(values)

        if limit:
            return sorted_values[:limit]
        return sorted_values
