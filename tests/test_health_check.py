"""
Unit tests for health check functionality
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.health_check import (
    ComponentHealth,
    HealthChecker,
    HealthCheckResponse,
    HealthStatus,
    SystemResources,
    get_http_status_for_health,
)


@pytest.fixture
def health_checker():
    """Create a health checker instance for testing"""
    return HealthChecker()


@pytest.fixture
def mock_redis_health():
    """Mock Redis health check response"""
    return {
        "status": "healthy",
        "latency_ms": 5.2,
        "details": {"pool_stats": {"current_size": 5, "available": 3, "in_use": 2}, "test_successful": True},
    }


@pytest.fixture
def mock_firestore_health():
    """Mock Firestore health check response"""
    return {
        "status": "healthy",
        "latency_ms": 12.5,
        "details": {"pool_stats": {"current_size": 3, "available": 2, "in_use": 1}, "test_successful": True},
    }


@pytest.fixture
def mock_vertex_health():
    """Mock Vertex AI health check response"""
    return {"status": "healthy", "latency_ms": 150.3, "details": {"response_received": True, "model": "gemini-pro"}}


@pytest.fixture
def mock_system_resources():
    """Mock system resources"""
    return SystemResources(
        cpu_percent=45.5,
        memory_percent=62.3,
        memory_available_mb=1024.5,
        disk_percent=75.0,
        disk_available_gb=50.2,
        open_connections=125,
    )


class TestHealthChecker:
    """Test HealthChecker class"""

    @pytest.mark.asyncio
    async def test_check_liveness(self, health_checker):
        """Test liveness check returns basic info"""
        result = await health_checker.check_liveness()

        assert result["status"] == "alive"
        assert "timestamp" in result
        assert "uptime_seconds" in result
        assert result["uptime_seconds"] >= 0

    @pytest.mark.asyncio
    async def test_check_readiness_all_healthy(self, health_checker):
        """Test readiness when all components are healthy"""
        with (
            patch.object(health_checker, "_quick_redis_check", return_value=True),
            patch.object(health_checker, "_quick_firestore_check", return_value=True),
        ):

            result = await health_checker.check_readiness()

            assert result["ready"] is True
            assert result["components"]["redis"] == "ready"
            assert result["components"]["firestore"] == "ready"

    @pytest.mark.asyncio
    async def test_check_readiness_redis_down(self, health_checker):
        """Test readiness when Redis is down"""
        with (
            patch.object(health_checker, "_quick_redis_check", return_value=False),
            patch.object(health_checker, "_quick_firestore_check", return_value=True),
        ):

            result = await health_checker.check_readiness()

            assert result["ready"] is False
            assert result["components"]["redis"] == "not_ready"
            assert result["components"]["firestore"] == "ready"

    @pytest.mark.asyncio
    async def test_check_all_healthy(
        self, health_checker, mock_redis_health, mock_firestore_health, mock_vertex_health, mock_system_resources
    ):
        """Test comprehensive health check when all components are healthy"""
        with (
            patch.object(health_checker, "_check_redis", return_value=mock_redis_health),
            patch.object(health_checker, "_check_firestore", return_value=mock_firestore_health),
            patch.object(health_checker, "_check_vertex_ai", return_value=mock_vertex_health),
            patch.object(health_checker, "_check_system_resources", return_value=mock_system_resources),
        ):

            result = await health_checker.check_all(detailed=True)

            assert isinstance(result, HealthCheckResponse)
            assert result.status == HealthStatus.HEALTHY
            assert len(result.components) == 3
            assert result.resources == mock_system_resources
            assert result.details is not None

    @pytest.mark.asyncio
    async def test_check_all_degraded(
        self, health_checker, mock_redis_health, mock_firestore_health, mock_system_resources
    ):
        """Test health check when Vertex AI is down (degraded state)"""
        unhealthy_vertex = {"status": "unhealthy", "error": "Connection timeout", "latency_ms": 5000.0}

        with (
            patch.object(health_checker, "_check_redis", return_value=mock_redis_health),
            patch.object(health_checker, "_check_firestore", return_value=mock_firestore_health),
            patch.object(health_checker, "_check_vertex_ai", return_value=unhealthy_vertex),
            patch.object(health_checker, "_check_system_resources", return_value=mock_system_resources),
        ):

            result = await health_checker.check_all()

            assert result.status == HealthStatus.DEGRADED
            vertex_component = next(c for c in result.components if c.name == "Vertex AI")
            assert vertex_component.status == HealthStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_check_all_unhealthy(self, health_checker, mock_vertex_health, mock_system_resources):
        """Test health check when critical components are down"""
        unhealthy_redis = {"status": "unhealthy", "error": "Connection refused"}
        unhealthy_firestore = {"status": "unhealthy", "error": "Authentication failed"}

        with (
            patch.object(health_checker, "_check_redis", return_value=unhealthy_redis),
            patch.object(health_checker, "_check_firestore", return_value=unhealthy_firestore),
            patch.object(health_checker, "_check_vertex_ai", return_value=mock_vertex_health),
            patch.object(health_checker, "_check_system_resources", return_value=mock_system_resources),
        ):

            result = await health_checker.check_all()

            assert result.status == HealthStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_check_all_high_resource_usage(
        self, health_checker, mock_redis_health, mock_firestore_health, mock_vertex_health
    ):
        """Test health check with high resource usage"""
        high_resource_usage = SystemResources(
            cpu_percent=85.0,
            memory_percent=92.0,  # Over 90% threshold
            memory_available_mb=100.0,
            disk_percent=88.0,
            disk_available_gb=5.0,
            open_connections=500,
        )

        with (
            patch.object(health_checker, "_check_redis", return_value=mock_redis_health),
            patch.object(health_checker, "_check_firestore", return_value=mock_firestore_health),
            patch.object(health_checker, "_check_vertex_ai", return_value=mock_vertex_health),
            patch.object(health_checker, "_check_system_resources", return_value=high_resource_usage),
        ):

            result = await health_checker.check_all()

            assert result.status == HealthStatus.DEGRADED

    @pytest.mark.asyncio
    async def test_component_health_processing(self, health_checker):
        """Test component result processing"""
        # Test exception handling
        exception_result = Exception("Test error")
        component = health_checker._process_component_result("Test", exception_result)
        assert component.status == HealthStatus.UNHEALTHY
        assert component.error == "Test error"

        # Test valid result
        valid_result = {"status": "healthy", "latency_ms": 10.5, "details": {"test": "data"}}
        component = health_checker._process_component_result("Test", valid_result)
        assert component.status == HealthStatus.HEALTHY
        assert component.latency_ms == 10.5
        assert component.details == {"test": "data"}

        # Test invalid status
        invalid_result = {"status": "unknown"}
        component = health_checker._process_component_result("Test", invalid_result)
        assert component.status == HealthStatus.UNHEALTHY

    def test_update_overall_status(self, health_checker):
        """Test overall status calculation"""
        # Healthy + Healthy = Healthy
        status = health_checker._update_overall_status(HealthStatus.HEALTHY, HealthStatus.HEALTHY)
        assert status == HealthStatus.HEALTHY

        # Healthy + Degraded = Degraded
        status = health_checker._update_overall_status(HealthStatus.HEALTHY, HealthStatus.DEGRADED)
        assert status == HealthStatus.DEGRADED

        # Degraded + Unhealthy = Unhealthy
        status = health_checker._update_overall_status(HealthStatus.DEGRADED, HealthStatus.UNHEALTHY)
        assert status == HealthStatus.UNHEALTHY

        # Unhealthy + anything = Unhealthy
        status = health_checker._update_overall_status(HealthStatus.UNHEALTHY, HealthStatus.HEALTHY)
        assert status == HealthStatus.UNHEALTHY


class TestHealthStatusMapping:
    """Test HTTP status code mapping"""

    def test_get_http_status_for_health(self):
        """Test health status to HTTP status mapping"""
        assert get_http_status_for_health(HealthStatus.HEALTHY) == 200
        assert get_http_status_for_health(HealthStatus.DEGRADED) == 200
        assert get_http_status_for_health(HealthStatus.UNHEALTHY) == 503


@pytest.mark.asyncio
class TestHealthCheckIntegration:
    """Integration tests for health check system"""

    async def test_redis_health_check_integration(self, health_checker):
        """Test Redis health check with mocked pool"""
        with patch("app.core.health_check.check_redis_health") as mock_check:
            mock_check.return_value = {"status": "healthy", "pool_stats": {"available": 5}, "test_successful": True}

            result = await health_checker._check_redis()

            assert result["status"] == "healthy"
            assert "latency_ms" in result
            assert result["details"]["test_successful"] is True

    async def test_firestore_health_check_integration(self, health_checker):
        """Test Firestore health check with mocked pool"""
        with patch("app.core.health_check.check_firestore_health") as mock_check:
            mock_check.return_value = {"status": "healthy", "pool_stats": {"available": 3}, "test_successful": True}

            result = await health_checker._check_firestore()

            assert result["status"] == "healthy"
            assert "latency_ms" in result

    async def test_vertex_ai_health_check_integration(self, health_checker):
        """Test Vertex AI health check"""
        mock_client = MagicMock()
        mock_client.generate_content = MagicMock(return_value="OK")
        mock_client.model_name = "gemini-pro"

        with patch.object(health_checker, "llm_client", mock_client):
            result = await health_checker._check_vertex_ai()

            assert result["status"] == "healthy"
            assert "latency_ms" in result
            assert result["details"]["response_received"] is True
            assert result["details"]["model"] == "gemini-pro"
