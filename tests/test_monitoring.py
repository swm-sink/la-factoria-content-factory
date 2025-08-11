"""
Comprehensive tests for the monitoring module
Tests all monitoring endpoints and helper functions with proper mocking
"""

import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock, patch, Mock
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.api.routes import monitoring
from src.core.config import settings


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    @pytest.mark.asyncio
    async def test_basic_health_check(self):
        """Test basic health check returns correct structure"""
        result = await monitoring.health_check()
        
        assert result["status"] == "healthy"
        assert "timestamp" in result
        assert result["version"] == "1.0.0"
        assert result["environment"] == settings.ENVIRONMENT
    
    @pytest.mark.asyncio
    async def test_detailed_health_check_all_healthy(self):
        """Test detailed health check when all systems are healthy"""
        # Create mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=MagicMock())
        
        # Mock helper functions
        with patch.object(monitoring, '_check_database_health', return_value={
            "status": "healthy",
            "connection": "ok",
            "tables_available": 3,
            "required_tables": ['users', 'educational_content', 'quality_assessments']
        }):
            with patch.object(monitoring, '_check_ai_providers_health', return_value={
                "status": "healthy",
                "available_providers": ["openai"],
                "total_configured": 1,
                "providers": {"openai": True}
            }):
                with patch.object(monitoring, '_check_system_resources', return_value={
                    "status": "healthy",
                    "cpu_percent": 50.0,
                    "memory_percent": 60.0,
                    "disk_percent": 70.0
                }):
                    with patch.object(monitoring, '_get_application_metrics', return_value={
                        "total_content_generated": 100,
                        "content_last_24h": 10,
                        "average_quality_24h": 0.85
                    }):
                        result = await monitoring.detailed_health_check(mock_db)
        
        assert result["status"] == "healthy"
        assert "timestamp" in result
        assert "checks" in result
        assert "metrics" in result
        assert "response_time_ms" in result
        assert result["checks"]["database"]["status"] == "healthy"
        assert result["checks"]["ai_providers"]["status"] == "healthy"
        assert result["checks"]["system_resources"]["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_detailed_health_check_degraded(self):
        """Test detailed health check when some services are unhealthy"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        with patch.object(monitoring, '_check_database_health', return_value={
            "status": "unhealthy",
            "error": "Connection failed"
        }):
            with patch.object(monitoring, '_check_ai_providers_health', return_value={
                "status": "healthy",
                "available_providers": ["openai"],
                "total_configured": 1
            }):
                with patch.object(monitoring, '_check_system_resources', return_value={
                    "status": "healthy",
                    "cpu_percent": 50.0
                }):
                    with patch.object(monitoring, '_get_application_metrics', return_value={}):
                        result = await monitoring.detailed_health_check(mock_db)
        
        assert result["status"] == "degraded"
        assert "failed_checks" in result
        assert "database" in result["failed_checks"]
    
    @pytest.mark.asyncio
    async def test_detailed_health_check_exception(self):
        """Test detailed health check handles exceptions gracefully"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        with patch.object(monitoring, '_check_database_health', side_effect=Exception("Database error")):
            result = await monitoring.detailed_health_check(mock_db)
        
        assert result["status"] == "unhealthy"
        assert "error" in result
        assert "Database error" in result["error"]


class TestMetricsEndpoints:
    """Test metrics collection endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_system_metrics_success(self):
        """Test system metrics collection"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        with patch.object(monitoring, '_get_system_metrics', return_value={
            "cpu": {"percent": 50.0},
            "memory": {"percent_used": 60.0}
        }):
            with patch.object(monitoring, '_get_application_metrics', return_value={
                "total_content_generated": 100
            }):
                with patch.object(monitoring, '_get_educational_metrics', return_value={
                    "content_type_distribution": {"study_guide": 50}
                }):
                    with patch.object(monitoring, '_get_performance_metrics', return_value={
                        "generation_performance_by_type": {}
                    }):
                        result = await monitoring.get_system_metrics(mock_db)
        
        assert "timestamp" in result
        assert "system" in result
        assert "application" in result
        assert "educational" in result
        assert "performance" in result
    
    @pytest.mark.asyncio
    async def test_get_system_metrics_exception(self):
        """Test metrics collection handles exceptions"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        with patch.object(monitoring, '_get_system_metrics', side_effect=Exception("Metrics error")):
            with pytest.raises(HTTPException) as exc_info:
                await monitoring.get_system_metrics(mock_db)
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Metrics collection failed" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_educational_metrics_success(self):
        """Test educational metrics endpoint"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock database query results
        mock_result = MagicMock()
        mock_result._mapping = {
            "content_type": "study_guide",
            "total_generated": 10,
            "avg_quality": 0.85
        }
        
        mock_execute = AsyncMock()
        mock_execute.return_value = [mock_result]
        mock_db.execute = mock_execute
        
        result = await monitoring.get_educational_metrics(mock_db)
        
        assert "timestamp" in result
        assert "content_type_stats" in result
        assert "quality_distribution" in result
        assert "generation_trends" in result
        assert "quality_thresholds" in result
    
    @pytest.mark.asyncio
    async def test_get_educational_metrics_exception(self):
        """Test educational metrics handles database errors"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(HTTPException) as exc_info:
            await monitoring.get_educational_metrics(mock_db)
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Educational metrics collection failed" in str(exc_info.value.detail)


class TestStatusEndpoint:
    """Test service status endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_service_status_success(self):
        """Test service status returns complete information"""
        with patch.object(monitoring, '_get_uptime', return_value={
            "uptime_seconds": 3600,
            "uptime_human": "1:00:00"
        }):
            result = await monitoring.get_service_status()
        
        assert result["platform"] == "La Factoria Educational Content Platform"
        assert result["version"] == "1.0.0"
        assert result["environment"] == settings.ENVIRONMENT
        assert "timestamp" in result
        assert "uptime" in result
        assert "services" in result
        assert "features" in result
        assert "configuration" in result
    
    @pytest.mark.asyncio
    async def test_get_service_status_exception(self):
        """Test service status handles exceptions"""
        with patch.object(monitoring, '_get_uptime', side_effect=Exception("Uptime error")):
            with pytest.raises(HTTPException) as exc_info:
                await monitoring.get_service_status()
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Status check failed" in str(exc_info.value.detail)


class TestHelperFunctions:
    """Test monitoring helper functions"""
    
    @pytest.mark.asyncio
    async def test_check_database_health_success(self):
        """Test database health check when connection is successful"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(return_value=MagicMock())
        
        with patch('src.api.routes.monitoring.inspect') as mock_inspect:
            mock_inspector = MagicMock()
            mock_inspector.get_table_names.return_value = ['users', 'educational_content', 'quality_assessments']
            mock_inspect.return_value = mock_inspector
            
            result = await monitoring._check_database_health(mock_db)
        
        assert result["status"] == "healthy"
        assert result["connection"] == "ok"
        assert result["tables_available"] == 3
        assert "users" in result["required_tables"]
    
    @pytest.mark.asyncio
    async def test_check_database_health_failure(self):
        """Test database health check when connection fails"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(side_effect=Exception("Connection refused"))
        
        result = await monitoring._check_database_health(mock_db)
        
        assert result["status"] == "unhealthy"
        assert "error" in result
        assert "Connection refused" in result["error"]
    
    @pytest.mark.asyncio
    async def test_check_ai_providers_health_with_providers(self):
        """Test AI providers health check with configured providers"""
        # Mock the property methods directly on settings
        with patch.object(type(settings), 'has_openai_config', new_callable=lambda: property(lambda self: True)):
            with patch.object(type(settings), 'has_anthropic_config', new_callable=lambda: property(lambda self: False)):
                with patch.object(type(settings), 'has_elevenlabs_config', new_callable=lambda: property(lambda self: False)):
                    with patch.object(settings, 'GOOGLE_CLOUD_PROJECT', None):
                        result = await monitoring._check_ai_providers_health()
        
        assert result["status"] == "healthy"
        assert "openai" in result["available_providers"]
        assert result["total_configured"] == 1
    
    @pytest.mark.asyncio
    async def test_check_ai_providers_health_no_providers(self):
        """Test AI providers health check with no configured providers"""
        # Mock the property methods
        with patch.object(type(settings), 'has_openai_config', new_callable=lambda: property(lambda self: False)):
            with patch.object(type(settings), 'has_anthropic_config', new_callable=lambda: property(lambda self: False)):
                with patch.object(settings, 'GOOGLE_CLOUD_PROJECT', None):
                    with patch.object(type(settings), 'has_elevenlabs_config', new_callable=lambda: property(lambda self: False)):
                        result = await monitoring._check_ai_providers_health()
        
        assert result["status"] == "unhealthy"
        assert result["total_configured"] == 0
        assert len(result["available_providers"]) == 0
    
    def test_check_system_resources_healthy(self):
        """Test system resources check when resources are healthy"""
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value = MagicMock(percent=60.0, available=4 * 1024**3)
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value = MagicMock(percent=70.0, free=100 * 1024**3)
                    
                    result = monitoring._check_system_resources()
        
        assert result["status"] == "healthy"
        assert result["cpu_percent"] == 50.0
        assert result["memory_percent"] == 60.0
        assert result["disk_percent"] == 70.0
    
    def test_check_system_resources_warning(self):
        """Test system resources check when resources are high"""
        with patch('psutil.cpu_percent', return_value=85.0):
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value = MagicMock(percent=82.0, available=1 * 1024**3)
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value = MagicMock(percent=88.0, free=20 * 1024**3)
                    
                    result = monitoring._check_system_resources()
        
        assert result["status"] == "warning"
    
    def test_check_system_resources_critical(self):
        """Test system resources check when resources are critical"""
        with patch('psutil.cpu_percent', return_value=96.0):
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value = MagicMock(percent=96.0, available=0.1 * 1024**3)
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value = MagicMock(percent=96.0, free=1 * 1024**3)
                    
                    result = monitoring._check_system_resources()
        
        assert result["status"] == "critical"
    
    def test_check_system_resources_exception(self):
        """Test system resources check handles exceptions"""
        with patch('psutil.cpu_percent', side_effect=Exception("CPU error")):
            result = monitoring._check_system_resources()
        
        assert result["status"] == "unknown"
        assert "error" in result
    
    def test_get_system_metrics_success(self):
        """Test system metrics collection"""
        with patch('psutil.cpu_percent', return_value=50.0):
            with patch('psutil.cpu_count', return_value=4):
                with patch('psutil.getloadavg', return_value=(1.0, 2.0, 3.0)):
                    with patch('psutil.virtual_memory') as mock_memory:
                        mock_memory.return_value = MagicMock(
                            total=16 * 1024**3,
                            available=8 * 1024**3,
                            percent=50.0
                        )
                        with patch('psutil.disk_usage') as mock_disk:
                            mock_disk.return_value = MagicMock(
                                total=500 * 1024**3,
                                free=250 * 1024**3,
                                percent=50.0
                            )
                            with patch('psutil.net_io_counters') as mock_net:
                                mock_net.return_value = MagicMock(_asdict=lambda: {"bytes_sent": 1000})
                                
                                result = monitoring._get_system_metrics()
        
        assert "cpu" in result
        assert result["cpu"]["percent"] == 50.0
        assert result["cpu"]["count"] == 4
        assert "memory" in result
        assert "disk" in result
        assert "network" in result
    
    def test_get_system_metrics_exception(self):
        """Test system metrics handles exceptions"""
        with patch('psutil.cpu_percent', side_effect=Exception("Metrics error")):
            result = monitoring._get_system_metrics()
        
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_get_application_metrics_success(self):
        """Test application metrics collection"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock count query
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 100
        
        # Mock average query
        mock_avg_result = MagicMock()
        mock_avg_result.scalar.return_value = 0.85
        
        mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_count_result, mock_avg_result])
        
        with patch.object(monitoring, '_get_uptime', return_value={"uptime_seconds": 3600}):
            result = await monitoring._get_application_metrics(mock_db)
        
        assert result["total_content_generated"] == 100
        assert result["content_last_24h"] == 100
        assert result["average_quality_24h"] == 0.85
        assert "uptime" in result
    
    @pytest.mark.asyncio
    async def test_get_application_metrics_exception(self):
        """Test application metrics handles exceptions"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(side_effect=Exception("Database error"))
        
        with patch.object(monitoring, '_get_uptime', return_value={"uptime_seconds": 3600}):
            result = await monitoring._get_application_metrics(mock_db)
        
        assert "error" in result
        assert "uptime" in result
    
    @pytest.mark.asyncio
    async def test_get_educational_metrics_success(self):
        """Test educational metrics collection"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock content distribution result
        mock_dist_result = MagicMock()
        mock_dist_result.__iter__ = lambda self: iter([("study_guide", 10), ("flashcards", 5)])
        
        # Mock quality metrics result
        mock_quality_result = MagicMock()
        mock_quality_result.fetchone.return_value = (8, 9, 10, 10)  # meets_overall, meets_edu, meets_factual, total
        
        mock_db.execute = AsyncMock(side_effect=[mock_dist_result, mock_quality_result])
        
        result = await monitoring._get_educational_metrics(mock_db)
        
        assert "content_type_distribution" in result
        assert result["content_type_distribution"]["study_guide"] == 10
        assert "quality_compliance" in result
        assert result["quality_compliance"]["overall_threshold_rate"] == 80.0
    
    @pytest.mark.asyncio
    async def test_get_educational_metrics_exception(self):
        """Test educational metrics handles exceptions"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(side_effect=Exception("Query error"))
        
        result = await monitoring._get_educational_metrics(mock_db)
        
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics_success(self):
        """Test performance metrics collection"""
        mock_db = AsyncMock(spec=AsyncSession)
        
        # Mock performance result
        mock_perf_result = MagicMock()
        mock_perf_result.__iter__ = lambda self: iter([("study_guide", 1500.5, 10)])
        
        mock_db.execute = AsyncMock(return_value=mock_perf_result)
        
        result = await monitoring._get_performance_metrics(mock_db)
        
        assert "generation_performance_by_type" in result
        assert "study_guide" in result["generation_performance_by_type"]
        assert result["generation_performance_by_type"]["study_guide"]["avg_duration_ms"] == 1500.5
        assert "targets" in result
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics_exception(self):
        """Test performance metrics handles exceptions"""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute = AsyncMock(side_effect=Exception("Performance error"))
        
        result = await monitoring._get_performance_metrics(mock_db)
        
        assert "error" in result
    
    def test_get_uptime_success(self):
        """Test uptime calculation"""
        mock_boot_time = datetime.now().timestamp() - 3600  # 1 hour ago
        
        with patch('psutil.boot_time', return_value=mock_boot_time):
            result = monitoring._get_uptime()
        
        assert "boot_time" in result
        assert "uptime_seconds" in result
        assert "uptime_human" in result
        assert result["uptime_seconds"] >= 3600
    
    def test_get_uptime_exception(self):
        """Test uptime handles exceptions"""
        with patch('psutil.boot_time', side_effect=Exception("Boot time error")):
            result = monitoring._get_uptime()
        
        assert result["uptime_human"] == "unknown"


class TestIntegration:
    """Integration tests for monitoring module"""
    
    @pytest.mark.asyncio
    async def test_monitoring_endpoints_with_mock_app(self, async_client):
        """Test monitoring endpoints through the actual FastAPI app"""
        # Since monitoring router is commented out in main.py, 
        # we'll test the health endpoints that ARE available
        
        # Test basic health endpoint (this is from health router)
        response = await async_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        
        # Test ready endpoint (from health router)
        response = await async_client.get("/api/v1/ready")
        assert response.status_code == 200
        
        # Test live endpoint (from health router)
        response = await async_client.get("/api/v1/live")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_detailed_health_with_database(self, async_client, test_database):
        """Test detailed health check with actual database connection"""
        # Test the health/detailed endpoint from health router
        response = await async_client.get("/api/v1/health/detailed")
        # May be 200 or 503 depending on actual system state
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data