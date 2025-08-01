"""
Unit tests for the metrics collection system.
"""

from unittest.mock import MagicMock

import pytest

from app.core.metrics import (
    MetricsCollector,
    content_generation_total,
    database_connections_active,
    http_request_duration_seconds,
    http_requests_total,
    metrics,
)


class TestMetricsCollector:
    """Test the MetricsCollector class."""

    def test_singleton_instance(self):
        """Test that MetricsCollector is a singleton."""
        collector1 = MetricsCollector()
        collector2 = MetricsCollector()
        assert collector1 is collector2

    def test_increment_counter(self):
        """Test incrementing a counter metric."""
        # Reset the counter for testing
        http_requests_total._metrics.clear()

        # Increment with tags
        metrics.increment("http_requests_total", tags={"method": "GET", "endpoint": "/test", "status": "200"})

        # Check the metric was incremented
        sample = list(http_requests_total.collect())[0].samples[0]
        assert sample.value == 1

    def test_set_gauge(self):
        """Test setting a gauge metric."""
        # Set gauge value
        metrics.gauge("database_connections_active", 10, tags={"database": "test"})

        # Check the value was set
        samples = list(database_connections_active.collect())[0].samples
        assert any(s.value == 10 for s in samples)

    def test_observe_histogram(self):
        """Test observing a histogram metric."""
        # Observe a value
        metrics.histogram("http_request_duration_seconds", 0.123, tags={"method": "GET", "endpoint": "/test"})

        # Check that the histogram has data
        metric_data = list(http_request_duration_seconds.collect())[0]
        assert len(metric_data.samples) > 0

    def test_timer_context_manager(self):
        """Test the timer context manager."""
        import time

        # Use timer to measure a short operation
        with metrics.timer("http_request_duration_seconds", tags={"method": "POST", "endpoint": "/api/test"}):
            time.sleep(0.01)  # Sleep for 10ms

        # Check that time was recorded
        metric_data = list(http_request_duration_seconds.collect())[0]
        # Find the sum sample (total time observed)
        sum_sample = next(s for s in metric_data.samples if s.name.endswith("_sum"))
        assert sum_sample.value >= 0.01  # At least 10ms

    @pytest.mark.asyncio
    async def test_track_request_decorator(self):
        """Test the track_request decorator."""

        # Create a mock async function
        @metrics.track_request("GET", "/api/test")
        async def mock_endpoint():
            return MagicMock(status_code=200)

        # Call the decorated function
        result = await mock_endpoint()

        # Check that metrics were recorded
        samples = list(http_requests_total.collect())[0].samples
        assert len(samples) > 0

    @pytest.mark.asyncio
    async def test_track_db_operation_decorator(self):
        """Test the track_db_operation decorator."""

        # Create a mock async function
        @metrics.track_db_operation("select", "users")
        async def mock_db_query():
            return {"id": 1, "name": "Test"}

        # Call the decorated function
        result = await mock_db_query()

        # Check the result
        assert result == {"id": 1, "name": "Test"}

    @pytest.mark.asyncio
    async def test_track_external_api_decorator(self):
        """Test the track_external_api decorator."""

        # Create a mock async function
        @metrics.track_external_api("openai", "completions")
        async def mock_api_call():
            return {"response": "test"}

        # Call the decorated function
        result = await mock_api_call()

        # Check the result
        assert result == {"response": "test"}

    def test_get_metrics_prometheus_format(self):
        """Test that get_metrics returns Prometheus format."""
        # Get metrics
        metrics_data = metrics.get_metrics()

        # Check it's bytes
        assert isinstance(metrics_data, bytes)

        # Check it contains Prometheus format markers
        metrics_text = metrics_data.decode("utf-8")
        assert "# HELP" in metrics_text
        assert "# TYPE" in metrics_text

    def test_error_handling_in_increment(self, caplog):
        """Test error handling when incrementing non-existent metric."""
        # Try to increment a non-existent metric
        metrics.increment("non_existent_metric")

        # Check warning was logged
        assert "not found or not a Counter" in caplog.text

    def test_error_handling_in_gauge(self, caplog):
        """Test error handling when setting non-existent gauge."""
        # Try to set a non-existent gauge
        metrics.gauge("non_existent_gauge", 42)

        # Check warning was logged
        assert "not found or not a Gauge" in caplog.text

    def test_error_handling_in_histogram(self, caplog):
        """Test error handling when observing non-existent histogram."""
        # Try to observe a non-existent histogram
        metrics.histogram("non_existent_histogram", 1.23)

        # Check warning was logged
        assert "not found or not a Histogram" in caplog.text


class TestMetricsMiddleware:
    """Test the metrics middleware integration."""

    @pytest.mark.asyncio
    async def test_metrics_middleware_integration(self):
        """Test that metrics middleware can be imported and instantiated."""
        from starlette.applications import Starlette

        from app.middleware.metrics import MetricsMiddleware

        # Create a test app
        app = Starlette()

        # Create middleware instance
        middleware = MetricsMiddleware(app)

        # Check it has the required method
        assert hasattr(middleware, "dispatch")

    def test_metrics_endpoint_registration(self):
        """Test that the metrics endpoint is properly registered."""
        from app.main import app

        # Check that /metrics route exists
        routes = [route.path for route in app.routes]
        assert "/metrics" in routes


class TestBusinessMetrics:
    """Test business-specific metrics."""

    def test_content_generation_metrics(self):
        """Test content generation metrics."""
        # Reset metric
        content_generation_total._metrics.clear()

        # Record successful generation
        metrics.increment("content_generation_total", tags={"content_type": "study_guide", "status": "success"})

        # Record failed generation
        metrics.increment("content_generation_total", tags={"content_type": "study_guide", "status": "error"})

        # Check both were recorded
        samples = list(content_generation_total.collect())[0].samples
        assert len(samples) == 2

        # Check values
        success_sample = next(s for s in samples if "success" in str(s.labels))
        error_sample = next(s for s in samples if "error" in str(s.labels))

        assert success_sample.value == 1
        assert error_sample.value == 1
