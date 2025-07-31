"""
Connection Pool Manager for Redis and Firestore.

Provides centralized connection pooling with health monitoring,
automatic recovery, and performance tracking.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol

from prometheus_client import Counter, Gauge, Histogram

# Metrics
CONNECTION_POOL_SIZE = Gauge(
    "connection_pool_size", "Current connection pool size", ["pool_name", "state"]
)
CONNECTION_POOL_WAIT_TIME = Histogram(
    "connection_pool_wait_seconds", "Time waiting for connection", ["pool_name"]
)
CONNECTION_POOL_ERRORS = Counter(
    "connection_pool_errors_total", "Connection pool errors", ["pool_name", "error_type"]
)
CONNECTION_POOL_HEALTH_CHECKS = Counter(
    "connection_pool_health_checks_total", "Health check results", ["pool_name", "status"]
)
CONNECTION_USAGE = Histogram(
    "connection_usage_seconds", "Connection usage duration", ["pool_name"]
)


class ConnectionState(Enum):
    """Connection states."""
    IDLE = "idle"
    ACTIVE = "active"
    UNHEALTHY = "unhealthy"
    CLOSED = "closed"


@dataclass
class ConnectionStats:
    """Statistics for a connection."""
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: datetime = field(default_factory=datetime.utcnow)
    total_uses: int = 0
    total_errors: int = 0
    last_error: Optional[str] = None
    health_check_failures: int = 0


class Connection(Protocol):
    """Protocol for poolable connections."""
    
    async def is_healthy(self) -> bool:
        """Check if connection is healthy."""
        ...
    
    async def close(self) -> None:
        """Close the connection."""
        ...


@dataclass
class PooledConnection:
    """Wrapper for pooled connections with metadata."""
    connection: Any
    state: ConnectionState = ConnectionState.IDLE
    stats: ConnectionStats = field(default_factory=ConnectionStats)
    pool_name: str = ""
    
    def mark_active(self) -> None:
        """Mark connection as active."""
        self.state = ConnectionState.ACTIVE
        self.stats.last_used = datetime.utcnow()
        self.stats.total_uses += 1
    
    def mark_idle(self) -> None:
        """Mark connection as idle."""
        self.state = ConnectionState.IDLE
    
    def mark_unhealthy(self, error: str) -> None:
        """Mark connection as unhealthy."""
        self.state = ConnectionState.UNHEALTHY
        self.stats.total_errors += 1
        self.stats.last_error = error
    
    def is_stale(self, max_idle_time: timedelta) -> bool:
        """Check if connection has been idle too long."""
        if self.state != ConnectionState.IDLE:
            return False
        return datetime.utcnow() - self.stats.last_used > max_idle_time


class ConnectionPoolBase(ABC):
    """Base class for connection pools."""
    
    def __init__(
        self,
        name: str,
        min_size: int = 1,
        max_size: int = 10,
        max_idle_time: int = 300,  # 5 minutes
        health_check_interval: int = 30,  # 30 seconds
        create_connection_func: Optional[Callable] = None,
    ):
        """
        Initialize connection pool.
        
        Args:
            name: Pool name for identification
            min_size: Minimum number of connections
            max_size: Maximum number of connections
            max_idle_time: Maximum idle time in seconds before closing
            health_check_interval: Health check interval in seconds
            create_connection_func: Function to create new connections
        """
        self.name = name
        self.min_size = min_size
        self.max_size = max_size
        self.max_idle_time = timedelta(seconds=max_idle_time)
        self.health_check_interval = health_check_interval
        self.create_connection_func = create_connection_func
        
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # Connection storage
        self._connections: List[PooledConnection] = []
        self._lock = asyncio.Lock()
        self._available = asyncio.Queue(maxsize=max_size)
        
        # State tracking
        self._closed = False
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Initialize metrics
        CONNECTION_POOL_SIZE.labels(pool_name=name, state="idle").set(0)
        CONNECTION_POOL_SIZE.labels(pool_name=name, state="active").set(0)
        CONNECTION_POOL_SIZE.labels(pool_name=name, state="total").set(0)
    
    @abstractmethod
    async def _create_connection(self) -> Any:
        """Create a new connection (implementation-specific)."""
        pass
    
    @abstractmethod
    async def _is_connection_healthy(self, connection: Any) -> bool:
        """Check if connection is healthy (implementation-specific)."""
        pass
    
    @abstractmethod
    async def _close_connection(self, connection: Any) -> None:
        """Close a connection (implementation-specific)."""
        pass
    
    async def initialize(self) -> None:
        """Initialize the pool with minimum connections."""
        async with self._lock:
            # Create minimum connections
            for _ in range(self.min_size):
                try:
                    conn = await self._create_connection_wrapper()
                    if conn:
                        self._connections.append(conn)
                        await self._available.put(conn)
                except Exception as e:
                    self.logger.error(f"Failed to create initial connection: {e}")
                    CONNECTION_POOL_ERRORS.labels(
                        pool_name=self.name, error_type="initialization"
                    ).inc()
            
            # Start health check task
            if not self._health_check_task:
                self._health_check_task = asyncio.create_task(self._health_check_loop())
            
            self._update_metrics()
            self.logger.info(
                f"Pool '{self.name}' initialized with {len(self._connections)} connections"
            )
    
    async def _create_connection_wrapper(self) -> Optional[PooledConnection]:
        """Create a new connection with wrapper."""
        try:
            if self.create_connection_func:
                conn = await self.create_connection_func()
            else:
                conn = await self._create_connection()
            
            if conn:
                return PooledConnection(
                    connection=conn,
                    pool_name=self.name,
                    state=ConnectionState.IDLE
                )
            return None
        except Exception as e:
            self.logger.error(f"Failed to create connection: {e}")
            CONNECTION_POOL_ERRORS.labels(
                pool_name=self.name, error_type="creation"
            ).inc()
            return None
    
    async def acquire(self, timeout: Optional[float] = None) -> Any:
        """
        Acquire a connection from the pool.
        
        Args:
            timeout: Maximum time to wait for connection
            
        Returns:
            A connection from the pool
            
        Raises:
            TimeoutError: If timeout is reached
            RuntimeError: If pool is closed
        """
        if self._closed:
            raise RuntimeError(f"Pool '{self.name}' is closed")
        
        start_time = time.time()
        
        try:
            # Try to get available connection
            try:
                conn_wrapper = await asyncio.wait_for(
                    self._available.get(), 
                    timeout=timeout or 5.0
                )
            except asyncio.TimeoutError:
                # No available connections, try to create new one
                async with self._lock:
                    if len(self._connections) < self.max_size:
                        conn_wrapper = await self._create_connection_wrapper()
                        if conn_wrapper:
                            self._connections.append(conn_wrapper)
                        else:
                            raise RuntimeError("Failed to create new connection")
                    else:
                        raise TimeoutError(
                            f"No available connections in pool '{self.name}'"
                        )
            
            # Check if connection is healthy
            if not await self._is_connection_healthy(conn_wrapper.connection):
                # Connection unhealthy, create replacement
                await self._replace_connection(conn_wrapper)
                return await self.acquire(timeout)  # Retry
            
            # Mark as active and return
            conn_wrapper.mark_active()
            
            wait_time = time.time() - start_time
            CONNECTION_POOL_WAIT_TIME.labels(pool_name=self.name).observe(wait_time)
            
            self._update_metrics()
            return conn_wrapper.connection
            
        except Exception as e:
            CONNECTION_POOL_ERRORS.labels(
                pool_name=self.name, error_type="acquire"
            ).inc()
            raise
    
    async def release(self, connection: Any) -> None:
        """
        Release a connection back to the pool.
        
        Args:
            connection: The connection to release
        """
        if self._closed:
            # Pool is closed, just close the connection
            await self._close_connection(connection)
            return
        
        # Find the wrapper
        conn_wrapper = None
        async with self._lock:
            for wrapper in self._connections:
                if wrapper.connection == connection:
                    conn_wrapper = wrapper
                    break
        
        if not conn_wrapper:
            self.logger.warning("Released connection not found in pool")
            await self._close_connection(connection)
            return
        
        # Check health before returning to pool
        if await self._is_connection_healthy(connection):
            conn_wrapper.mark_idle()
            try:
                await self._available.put(conn_wrapper)
            except asyncio.QueueFull:
                # Pool is full, close the connection
                await self._remove_connection(conn_wrapper)
        else:
            # Unhealthy connection, replace it
            await self._replace_connection(conn_wrapper)
        
        self._update_metrics()
    
    async def _replace_connection(self, conn_wrapper: PooledConnection) -> None:
        """Replace an unhealthy connection."""
        async with self._lock:
            # Remove old connection
            if conn_wrapper in self._connections:
                self._connections.remove(conn_wrapper)
            
            # Close old connection
            try:
                await self._close_connection(conn_wrapper.connection)
            except Exception as e:
                self.logger.error(f"Error closing connection: {e}")
            
            # Create new connection
            new_wrapper = await self._create_connection_wrapper()
            if new_wrapper:
                self._connections.append(new_wrapper)
                try:
                    await self._available.put(new_wrapper)
                except asyncio.QueueFull:
                    pass
    
    async def _remove_connection(self, conn_wrapper: PooledConnection) -> None:
        """Remove a connection from the pool."""
        async with self._lock:
            if conn_wrapper in self._connections:
                self._connections.remove(conn_wrapper)
            
            try:
                await self._close_connection(conn_wrapper.connection)
            except Exception as e:
                self.logger.error(f"Error closing connection: {e}")
    
    async def _health_check_loop(self) -> None:
        """Periodic health check for all connections."""
        while not self._closed:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._check_all_connections()
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                CONNECTION_POOL_ERRORS.labels(
                    pool_name=self.name, error_type="health_check"
                ).inc()
    
    async def _check_all_connections(self) -> None:
        """Check health of all connections."""
        async with self._lock:
            unhealthy = []
            stale = []
            
            for wrapper in self._connections:
                # Skip active connections
                if wrapper.state == ConnectionState.ACTIVE:
                    continue
                
                # Check for stale connections
                if wrapper.is_stale(self.max_idle_time):
                    stale.append(wrapper)
                    continue
                
                # Check health
                try:
                    if not await self._is_connection_healthy(wrapper.connection):
                        wrapper.stats.health_check_failures += 1
                        if wrapper.stats.health_check_failures >= 3:
                            unhealthy.append(wrapper)
                        CONNECTION_POOL_HEALTH_CHECKS.labels(
                            pool_name=self.name, status="failed"
                        ).inc()
                    else:
                        wrapper.stats.health_check_failures = 0
                        CONNECTION_POOL_HEALTH_CHECKS.labels(
                            pool_name=self.name, status="passed"
                        ).inc()
                except Exception as e:
                    self.logger.error(f"Health check failed: {e}")
                    unhealthy.append(wrapper)
            
            # Remove unhealthy and stale connections
            for wrapper in unhealthy + stale:
                await self._remove_connection(wrapper)
            
            # Ensure minimum connections
            while len(self._connections) < self.min_size:
                new_wrapper = await self._create_connection_wrapper()
                if new_wrapper:
                    self._connections.append(new_wrapper)
                    try:
                        await self._available.put(new_wrapper)
                    except asyncio.QueueFull:
                        pass
    
    def _update_metrics(self) -> None:
        """Update pool metrics."""
        idle_count = sum(1 for c in self._connections if c.state == ConnectionState.IDLE)
        active_count = sum(1 for c in self._connections if c.state == ConnectionState.ACTIVE)
        
        CONNECTION_POOL_SIZE.labels(pool_name=self.name, state="idle").set(idle_count)
        CONNECTION_POOL_SIZE.labels(pool_name=self.name, state="active").set(active_count)
        CONNECTION_POOL_SIZE.labels(pool_name=self.name, state="total").set(
            len(self._connections)
        )
    
    async def close(self) -> None:
        """Close the pool and all connections."""
        self._closed = True
        
        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        async with self._lock:
            for wrapper in self._connections:
                try:
                    await self._close_connection(wrapper.connection)
                except Exception as e:
                    self.logger.error(f"Error closing connection: {e}")
            
            self._connections.clear()
        
        self.logger.info(f"Pool '{self.name}' closed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        idle_count = sum(1 for c in self._connections if c.state == ConnectionState.IDLE)
        active_count = sum(1 for c in self._connections if c.state == ConnectionState.ACTIVE)
        unhealthy_count = sum(1 for c in self._connections if c.state == ConnectionState.UNHEALTHY)
        
        total_uses = sum(c.stats.total_uses for c in self._connections)
        total_errors = sum(c.stats.total_errors for c in self._connections)
        
        return {
            "name": self.name,
            "size": {
                "current": len(self._connections),
                "min": self.min_size,
                "max": self.max_size,
            },
            "connections": {
                "idle": idle_count,
                "active": active_count,
                "unhealthy": unhealthy_count,
            },
            "usage": {
                "total_uses": total_uses,
                "total_errors": total_errors,
                "error_rate": total_errors / total_uses if total_uses > 0 else 0,
            },
            "available_slots": self._available.qsize(),
            "closed": self._closed,
        }


# Context manager for automatic connection release
class PooledConnectionContext:
    """Context manager for pooled connections."""
    
    def __init__(self, pool: ConnectionPoolBase, timeout: Optional[float] = None):
        self.pool = pool
        self.timeout = timeout
        self.connection = None
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        self.connection = await self.pool.acquire(self.timeout)
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            await self.pool.release(self.connection)
            
            # Record usage time
            if self.start_time:
                usage_time = time.time() - self.start_time
                CONNECTION_USAGE.labels(pool_name=self.pool.name).observe(usage_time)