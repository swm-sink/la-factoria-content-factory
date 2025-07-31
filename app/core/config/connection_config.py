"""
Connection pooling configuration.

Defines optimal pool sizes and connection parameters for different services.
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class PoolConfig:
    """Configuration for a connection pool."""
    min_size: int = 1
    max_size: int = 10
    max_idle_time: int = 300  # 5 minutes
    health_check_interval: int = 30  # 30 seconds
    acquire_timeout: float = 5.0  # 5 seconds
    retry_attempts: int = 3
    retry_delay: float = 1.0  # 1 second


# Predefined configurations for different services
POOL_CONFIGS: Dict[str, PoolConfig] = {
    # Redis configuration - higher pool size for caching
    "redis": PoolConfig(
        min_size=5,
        max_size=20,
        max_idle_time=600,  # 10 minutes
        health_check_interval=30,
        acquire_timeout=2.0,  # Fast timeout for cache
        retry_attempts=3,
        retry_delay=0.5,
    ),
    
    # Firestore configuration - moderate pool size
    "firestore": PoolConfig(
        min_size=2,
        max_size=10,
        max_idle_time=300,  # 5 minutes
        health_check_interval=60,  # Less frequent checks
        acquire_timeout=10.0,  # Longer timeout for DB
        retry_attempts=3,
        retry_delay=1.0,
    ),
    
    # Default configuration
    "default": PoolConfig(
        min_size=1,
        max_size=5,
        max_idle_time=300,
        health_check_interval=60,
        acquire_timeout=5.0,
        retry_attempts=3,
        retry_delay=1.0,
    ),
}


def get_pool_config(service_name: str) -> PoolConfig:
    """
    Get pool configuration for a service.
    
    Args:
        service_name: Name of the service (redis, firestore, etc.)
        
    Returns:
        Pool configuration
    """
    return POOL_CONFIGS.get(service_name, POOL_CONFIGS["default"])


def calculate_optimal_pool_size(
    expected_qps: float,
    avg_connection_time_ms: float,
    target_utilization: float = 0.75,
) -> Dict[str, int]:
    """
    Calculate optimal pool size based on expected load.
    
    Args:
        expected_qps: Expected queries per second
        avg_connection_time_ms: Average time a connection is held (milliseconds)
        target_utilization: Target pool utilization (0-1)
        
    Returns:
        Dictionary with min_size and max_size recommendations
    """
    # Convert to seconds
    avg_connection_time = avg_connection_time_ms / 1000
    
    # Calculate required connections for expected load
    # Connections needed = QPS * Connection Hold Time
    required_connections = expected_qps * avg_connection_time
    
    # Add buffer based on target utilization
    max_size = int(required_connections / target_utilization) + 1
    
    # Min size is typically 25-50% of max
    min_size = max(1, int(max_size * 0.3))
    
    return {
        "min_size": min_size,
        "max_size": max_size,
        "estimated_qps_capacity": max_size / avg_connection_time * target_utilization,
    }


class ConnectionPoolSettings:
    """
    Dynamic connection pool settings based on environment.
    """
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self._configs = self._load_environment_configs()
    
    def _load_environment_configs(self) -> Dict[str, PoolConfig]:
        """Load environment-specific configurations."""
        if self.environment == "production":
            return {
                "redis": PoolConfig(
                    min_size=10,
                    max_size=50,  # Higher for production load
                    max_idle_time=900,  # 15 minutes
                    health_check_interval=30,
                    acquire_timeout=2.0,
                    retry_attempts=5,
                    retry_delay=0.5,
                ),
                "firestore": PoolConfig(
                    min_size=5,
                    max_size=20,  # Higher for production
                    max_idle_time=600,  # 10 minutes
                    health_check_interval=60,
                    acquire_timeout=10.0,
                    retry_attempts=5,
                    retry_delay=1.0,
                ),
            }
        elif self.environment == "staging":
            return {
                "redis": PoolConfig(
                    min_size=5,
                    max_size=20,
                    max_idle_time=600,
                    health_check_interval=30,
                    acquire_timeout=3.0,
                    retry_attempts=3,
                    retry_delay=0.5,
                ),
                "firestore": PoolConfig(
                    min_size=3,
                    max_size=10,
                    max_idle_time=300,
                    health_check_interval=60,
                    acquire_timeout=10.0,
                    retry_attempts=3,
                    retry_delay=1.0,
                ),
            }
        else:  # development/test
            return POOL_CONFIGS
    
    def get_config(self, service: str) -> PoolConfig:
        """Get configuration for a service."""
        return self._configs.get(service, self._configs.get("default", POOL_CONFIGS["default"]))