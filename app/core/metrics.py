"""
Metrics Collection Utilities

This module provides a unified interface for collecting and exposing metrics
to Prometheus. It uses the prometheus_client library and provides convenient
wrappers for common metric types.
"""

import functools
import logging
import time
from collections.abc import Callable
from contextlib import contextmanager

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Info, generate_latest

logger = logging.getLogger(__name__)

# Create a custom registry to avoid conflicts
REGISTRY = CollectorRegistry()

# Define metrics
http_requests_total = Counter(
    "http_requests_total", "Total number of HTTP requests", ["method", "endpoint", "status"], registry=REGISTRY
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=REGISTRY,
)

active_requests = Gauge(
    "http_requests_active", "Number of active HTTP requests", ["method", "endpoint"], registry=REGISTRY
)

# Content generation metrics
content_generation_total = Counter(
    "content_generation_total",
    "Total number of content generation requests",
    ["content_type", "status"],
    registry=REGISTRY,
)

content_generation_duration_seconds = Histogram(
    "content_generation_duration_seconds",
    "Content generation latency in seconds",
    ["content_type"],
    buckets=(1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0, 250.0),
    registry=REGISTRY,
)

# Audio generation metrics
audio_generation_total = Counter(
    "audio_generation_total", "Total number of audio generation requests", ["status"], registry=REGISTRY
)

audio_generation_duration_seconds = Histogram(
    "audio_generation_duration_seconds",
    "Audio generation latency in seconds",
    buckets=(1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0, 250.0),
    registry=REGISTRY,
)

# Database metrics
database_connections_active = Gauge(
    "database_connections_active", "Number of active database connections", ["database"], registry=REGISTRY
)

database_connections_max = Gauge(
    "database_connections_max", "Maximum number of database connections", ["database"], registry=REGISTRY
)

database_query_duration_seconds = Histogram(
    "database_query_duration_seconds",
    "Database query latency in seconds",
    ["operation", "table"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    registry=REGISTRY,
)

database_transactions_total = Counter(
    "database_transactions_total", "Total number of database transactions", ["status"], registry=REGISTRY
)

# Cache metrics
cache_operations_total = Counter(
    "cache_operations_total", "Total number of cache operations", ["operation", "status"], registry=REGISTRY
)

cache_hit_ratio = Gauge("cache_hit_ratio", "Cache hit ratio", registry=REGISTRY)

# External API metrics
external_api_requests_total = Counter(
    "external_api_requests_total",
    "Total number of external API requests",
    ["service", "endpoint", "status"],
    registry=REGISTRY,
)

external_api_duration_seconds = Histogram(
    "external_api_duration_seconds",
    "External API request latency in seconds",
    ["service", "endpoint"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0),
    registry=REGISTRY,
)

# Error metrics
errors_total = Counter("errors_total", "Total number of errors", ["error_type", "severity"], registry=REGISTRY)

# Business metrics
jobs_created_total = Counter("jobs_created_total", "Total number of jobs created", ["job_type"], registry=REGISTRY)

jobs_completed_total = Counter(
    "jobs_completed_total", "Total number of jobs completed", ["job_type", "status"], registry=REGISTRY
)

# System metrics
app_info = Info("app_info", "Application information", registry=REGISTRY)

# SLI metrics
sli_health_check_success_rate = Gauge(
    "sli_health_check_success_rate", "Health check success rate percentage", registry=REGISTRY
)

sli_api_latency_p95 = Gauge("sli_api_latency_p95", "API latency 95th percentile in milliseconds", registry=REGISTRY)

sli_api_latency_p99 = Gauge("sli_api_latency_p99", "API latency 99th percentile in milliseconds", registry=REGISTRY)

sli_api_error_rate = Gauge("sli_api_error_rate", "API error rate percentage", registry=REGISTRY)

sli_content_generation_success_rate = Gauge(
    "sli_content_generation_success_rate", "Content generation success rate percentage", registry=REGISTRY
)

sli_content_generation_p95 = Gauge(
    "sli_content_generation_p95", "Content generation latency 95th percentile in milliseconds", registry=REGISTRY
)

sli_audio_generation_success_rate = Gauge(
    "sli_audio_generation_success_rate", "Audio generation success rate percentage", registry=REGISTRY
)


class MetricsCollector:
    """Singleton class for metrics collection."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize metrics collector."""
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.registry = REGISTRY

            # Set application info
            app_info.info({"version": "1.0.0", "service": "la-factoria", "environment": "production"})

    def increment(self, metric_name: str, value: float = 1, tags: dict[str, str] | None = None):
        """Increment a counter metric."""
        try:
            metric = globals().get(metric_name)
            if isinstance(metric, Counter):
                if tags:
                    metric.labels(**tags).inc(value)
                else:
                    metric.inc(value)
            else:
                logger.warning(f"Metric {metric_name} not found or not a Counter")
        except Exception as e:
            logger.error(f"Error incrementing metric {metric_name}: {e}")

    def gauge(self, metric_name: str, value: float, tags: dict[str, str] | None = None):
        """Set a gauge metric value."""
        try:
            metric = globals().get(metric_name)
            if isinstance(metric, Gauge):
                if tags:
                    metric.labels(**tags).set(value)
                else:
                    metric.set(value)
            else:
                logger.warning(f"Metric {metric_name} not found or not a Gauge")
        except Exception as e:
            logger.error(f"Error setting gauge {metric_name}: {e}")

    def histogram(self, metric_name: str, value: float, tags: dict[str, str] | None = None):
        """Observe a histogram metric value."""
        try:
            metric = globals().get(metric_name)
            if isinstance(metric, Histogram):
                if tags:
                    metric.labels(**tags).observe(value)
                else:
                    metric.observe(value)
            else:
                logger.warning(f"Metric {metric_name} not found or not a Histogram")
        except Exception as e:
            logger.error(f"Error observing histogram {metric_name}: {e}")

    @contextmanager
    def timer(self, metric_name: str, tags: dict[str, str] | None = None):
        """Context manager for timing operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.histogram(metric_name, duration, tags)

    def track_request(self, method: str, endpoint: str):
        """Decorator for tracking HTTP requests."""

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                tags = {"method": method, "endpoint": endpoint}
                active_requests.labels(**tags).inc()

                start_time = time.time()
                status = "success"
                status_code = 200

                try:
                    result = await func(*args, **kwargs)
                    if hasattr(result, "status_code"):
                        status_code = result.status_code
                        status = str(status_code)
                    return result
                except Exception:
                    status = "error"
                    status_code = 500
                    raise
                finally:
                    duration = time.time() - start_time
                    active_requests.labels(**tags).dec()

                    http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()

                    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

            return wrapper

        return decorator

    def track_db_operation(self, operation: str, table: str):
        """Decorator for tracking database operations."""

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"

                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time
                    database_query_duration_seconds.labels(operation=operation, table=table).observe(duration)

                    database_transactions_total.labels(status=status).inc()

            return wrapper

        return decorator

    def track_external_api(self, service: str, endpoint: str):
        """Decorator for tracking external API calls."""

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"

                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time
                    external_api_requests_total.labels(service=service, endpoint=endpoint, status=status).inc()

                    external_api_duration_seconds.labels(service=service, endpoint=endpoint).observe(duration)

            return wrapper

        return decorator

    def get_metrics(self) -> bytes:
        """Generate metrics in Prometheus format."""
        return generate_latest(self.registry)


# Create global metrics instance
metrics = MetricsCollector()
