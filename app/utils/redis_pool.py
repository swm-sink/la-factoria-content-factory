"""
Redis connection pooling implementation.

Provides a managed connection pool for Redis with health monitoring
and automatic recovery.
"""

import asyncio
import logging
from typing import Any, Optional

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool as RedisConnectionPool
from redis.exceptions import ConnectionError, RedisError, TimeoutError

from app.core.config.connection_config import get_pool_config
from app.core.config.settings import get_settings
from app.core.connection_pool import ConnectionPoolBase, PooledConnectionContext


class RedisPool(ConnectionPoolBase):
    """Redis-specific connection pool implementation."""
    
    def __init__(self, **kwargs):
        """Initialize Redis pool with settings."""
        settings = get_settings()
        config = get_pool_config("redis")
        
        # Override with any provided kwargs
        pool_config = {
            "name": kwargs.get("name", "redis_pool"),
            "min_size": kwargs.get("min_size", config.min_size),
            "max_size": kwargs.get("max_size", config.max_size),
            "max_idle_time": kwargs.get("max_idle_time", config.max_idle_time),
            "health_check_interval": kwargs.get("health_check_interval", config.health_check_interval),
        }
        
        super().__init__(**pool_config)
        
        # Redis-specific configuration
        self.redis_config = {
            "host": settings.redis_host,
            "port": settings.redis_port,
            "db": settings.redis_db,
            "password": settings.redis_password,
            "ssl": settings.redis_ssl,
            "socket_timeout": settings.redis_socket_timeout,
            "socket_connect_timeout": settings.redis_socket_connect_timeout,
            "retry_on_timeout": settings.redis_retry_on_timeout,
            "decode_responses": True,
        }
        
        # Create underlying Redis connection pool
        self._redis_pool = self._create_redis_pool()
    
    def _create_redis_pool(self) -> RedisConnectionPool:
        """Create Redis connection pool."""
        pool_kwargs = {
            **self.redis_config,
            "max_connections": self.max_size,
            "health_check_interval": self.health_check_interval,
        }
        
        # Add SSL configuration if enabled
        if self.redis_config.get("ssl"):
            pool_kwargs["ssl_cert_reqs"] = "required"
        
        return RedisConnectionPool(**pool_kwargs)
    
    async def _create_connection(self) -> redis.Redis:
        """Create a new Redis connection."""
        try:
            # Create connection from pool
            client = redis.Redis(connection_pool=self._redis_pool)
            
            # Test connection
            await client.ping()
            
            self.logger.debug("Created new Redis connection")
            return client
            
        except (ConnectionError, TimeoutError) as e:
            self.logger.error(f"Failed to create Redis connection: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating Redis connection: {e}")
            raise
    
    async def _is_connection_healthy(self, connection: redis.Redis) -> bool:
        """Check if Redis connection is healthy."""
        try:
            # Simple ping test
            response = await connection.ping()
            return response is True
        except (ConnectionError, TimeoutError, RedisError):
            return False
        except Exception as e:
            self.logger.warning(f"Health check failed with unexpected error: {e}")
            return False
    
    async def _close_connection(self, connection: redis.Redis) -> None:
        """Close a Redis connection."""
        try:
            await connection.close()
        except Exception as e:
            self.logger.error(f"Error closing Redis connection: {e}")
    
    async def execute(self, command: str, *args, **kwargs) -> Any:
        """
        Execute a Redis command with automatic connection management.
        
        Args:
            command: Redis command to execute
            *args: Command arguments
            **kwargs: Command keyword arguments
            
        Returns:
            Command result
        """
        async with PooledConnectionContext(self) as conn:
            method = getattr(conn, command)
            return await method(*args, **kwargs)
    
    async def pipeline(self) -> redis.client.Pipeline:
        """
        Create a Redis pipeline for batch operations.
        
        Returns:
            Redis pipeline object
        """
        conn = await self.acquire()
        return conn.pipeline()
    
    async def close(self) -> None:
        """Close the pool and underlying Redis pool."""
        await super().close()
        
        # Close underlying Redis pool
        if hasattr(self, "_redis_pool"):
            await self._redis_pool.disconnect()


# Global pool instance
_redis_pool: Optional[RedisPool] = None


async def get_redis_pool() -> RedisPool:
    """
    Get or create the global Redis pool.
    
    Returns:
        Redis connection pool
    """
    global _redis_pool
    
    if _redis_pool is None:
        _redis_pool = RedisPool(name="global_redis_pool")
        await _redis_pool.initialize()
        logging.info("Global Redis pool initialized")
    
    return _redis_pool


async def close_redis_pool() -> None:
    """Close the global Redis pool."""
    global _redis_pool
    
    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None
        logging.info("Global Redis pool closed")


# Convenience functions for common operations
async def redis_get(key: str) -> Optional[str]:
    """Get value from Redis."""
    pool = await get_redis_pool()
    return await pool.execute("get", key)


async def redis_set(key: str, value: str, ex: Optional[int] = None) -> bool:
    """Set value in Redis with optional expiration."""
    pool = await get_redis_pool()
    return await pool.execute("set", key, value, ex=ex)


async def redis_delete(*keys: str) -> int:
    """Delete keys from Redis."""
    pool = await get_redis_pool()
    return await pool.execute("delete", *keys)


async def redis_exists(*keys: str) -> int:
    """Check if keys exist in Redis."""
    pool = await get_redis_pool()
    return await pool.execute("exists", *keys)


async def redis_expire(key: str, seconds: int) -> bool:
    """Set expiration on a key."""
    pool = await get_redis_pool()
    return await pool.execute("expire", key, seconds)


async def redis_incr(key: str, amount: int = 1) -> int:
    """Increment a counter."""
    pool = await get_redis_pool()
    return await pool.execute("incrby", key, amount)


async def redis_hget(key: str, field: str) -> Optional[str]:
    """Get hash field value."""
    pool = await get_redis_pool()
    return await pool.execute("hget", key, field)


async def redis_hset(key: str, field: str, value: str) -> int:
    """Set hash field value."""
    pool = await get_redis_pool()
    return await pool.execute("hset", key, field, value)


async def redis_batch_operation(operations: list) -> list:
    """
    Execute multiple Redis operations in a pipeline.
    
    Args:
        operations: List of (command, args, kwargs) tuples
        
    Returns:
        List of results
    """
    pool = await get_redis_pool()
    
    async with PooledConnectionContext(pool) as conn:
        pipe = conn.pipeline()
        
        for command, args, kwargs in operations:
            method = getattr(pipe, command)
            method(*args, **kwargs)
        
        return await pipe.execute()


# Health check function
async def check_redis_health() -> dict:
    """
    Check Redis pool health.
    
    Returns:
        Health status dictionary
    """
    try:
        pool = await get_redis_pool()
        
        # Get pool stats
        stats = pool.get_stats()
        
        # Try a simple operation
        test_key = "_health_check_test"
        await redis_set(test_key, "1", ex=1)
        result = await redis_get(test_key)
        
        return {
            "status": "healthy" if result == "1" else "degraded",
            "pool_stats": stats,
            "test_successful": result == "1",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }