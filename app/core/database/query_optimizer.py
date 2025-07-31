"""
Query optimization utilities for database operations.

This module provides query optimization strategies and utilities to improve database performance.
"""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar

from app.core.cache import get_cache_backend

logger = logging.getLogger(__name__)

T = TypeVar('T')


class QueryOptimizer:
    """Provides query optimization strategies."""
    
    def __init__(self):
        self._query_cache = {}
        self._query_stats = {}
        
    async def with_cache(
        self, 
        cache_key: str, 
        query_func: Callable[[], Any], 
        ttl: int = 300
    ) -> Any:
        """
        Execute query with caching.
        
        Args:
            cache_key: Cache key for the query result
            query_func: Function that executes the query
            ttl: Time to live in seconds
            
        Returns:
            Query result (from cache or fresh)
        """
        cache = get_cache_backend()
        
        # Try to get from cache
        cached = await cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit for key: {cache_key}")
            self._record_query_stat(cache_key, cached=True)
            return cached
            
        # Execute query
        start_time = time.time()
        result = await query_func()
        query_time = time.time() - start_time
        
        # Cache result
        await cache.set(cache_key, result, ttl)
        
        self._record_query_stat(cache_key, cached=False, query_time=query_time)
        logger.debug(f"Query executed and cached: {cache_key} (took {query_time:.3f}s)")
        
        return result
        
    def _record_query_stat(
        self, 
        cache_key: str, 
        cached: bool, 
        query_time: Optional[float] = None
    ):
        """Record query statistics for monitoring."""
        if cache_key not in self._query_stats:
            self._query_stats[cache_key] = {
                'total_calls': 0,
                'cache_hits': 0,
                'total_query_time': 0.0,
                'avg_query_time': 0.0
            }
            
        stats = self._query_stats[cache_key]
        stats['total_calls'] += 1
        
        if cached:
            stats['cache_hits'] += 1
        elif query_time:
            stats['total_query_time'] += query_time
            uncached_calls = stats['total_calls'] - stats['cache_hits']
            if uncached_calls > 0:
                stats['avg_query_time'] = stats['total_query_time'] / uncached_calls
                
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get query statistics."""
        return self._query_stats.copy()


class QueryBatcher:
    """Batches similar queries together for efficient execution."""
    
    def __init__(self, window_ms: int = 10):
        """
        Initialize query batcher.
        
        Args:
            window_ms: Time window in milliseconds to wait for batching
        """
        self.window_ms = window_ms
        self._pending_queries: Dict[str, List[asyncio.Future]] = {}
        self._batch_tasks: Dict[str, asyncio.Task] = {}
        
    async def batch_query(
        self, 
        query_type: str, 
        query_func: Callable[[List[Any]], Dict[Any, Any]], 
        query_args: Any
    ) -> Any:
        """
        Batch a query with similar queries.
        
        Args:
            query_type: Type/category of query for batching
            query_func: Function that executes batched queries
            query_args: Arguments for this specific query
            
        Returns:
            Query result for the specific arguments
        """
        if query_type not in self._pending_queries:
            self._pending_queries[query_type] = []
            
        future = asyncio.Future()
        self._pending_queries[query_type].append((query_args, future))
        
        # Schedule batch execution
        if query_type not in self._batch_tasks or self._batch_tasks[query_type].done():
            self._batch_tasks[query_type] = asyncio.create_task(
                self._execute_batch(query_type, query_func)
            )
            
        return await future
        
    async def _execute_batch(
        self, 
        query_type: str, 
        query_func: Callable[[List[Any]], Dict[Any, Any]]
    ):
        """Execute a batch of queries."""
        # Wait for batching window
        await asyncio.sleep(self.window_ms / 1000.0)
        
        queries = self._pending_queries.get(query_type, [])
        if not queries:
            return
            
        # Extract arguments
        all_args = [args for args, _ in queries]
        
        try:
            # Execute batched query
            start_time = time.time()
            results = await query_func(all_args)
            query_time = time.time() - start_time
            
            logger.info(
                f"Executed batch query '{query_type}' with {len(queries)} items "
                f"in {query_time:.3f}s"
            )
            
            # Resolve futures
            for args, future in queries:
                if not future.done():
                    future.set_result(results.get(args))
                    
        except Exception as e:
            logger.error(f"Batch query '{query_type}' failed: {e}")
            # Reject all futures
            for _, future in queries:
                if not future.done():
                    future.set_exception(e)
                    
        finally:
            # Clear pending queries
            self._pending_queries[query_type] = []


class ConnectionPool:
    """Manages database connections efficiently."""
    
    def __init__(self, max_connections: int = 10):
        """
        Initialize connection pool.
        
        Args:
            max_connections: Maximum number of concurrent connections
        """
        self.max_connections = max_connections
        self._semaphore = asyncio.Semaphore(max_connections)
        self._active_connections = 0
        
    async def acquire(self):
        """Acquire a connection from the pool."""
        await self._semaphore.acquire()
        self._active_connections += 1
        logger.debug(f"Connection acquired ({self._active_connections}/{self.max_connections})")
        
    def release(self):
        """Release a connection back to the pool."""
        self._semaphore.release()
        self._active_connections -= 1
        logger.debug(f"Connection released ({self._active_connections}/{self.max_connections})")
        
    def get_stats(self) -> Dict[str, int]:
        """Get connection pool statistics."""
        return {
            'active_connections': self._active_connections,
            'max_connections': self.max_connections,
            'available_connections': self.max_connections - self._active_connections
        }


def optimize_query(func: Callable) -> Callable:
    """
    Decorator to automatically optimize database queries.
    
    This decorator adds caching and batching capabilities to query functions.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Generate cache key from function name and arguments
        cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
        
        # Use query optimizer
        optimizer = get_query_optimizer()
        
        # Create query function
        query_func = functools.partial(func, *args, **kwargs)
        
        # Execute with optimization
        return await optimizer.with_cache(cache_key, query_func)
        
    return wrapper


# Global instances
_query_optimizer: Optional[QueryOptimizer] = None
_query_batcher: Optional[QueryBatcher] = None
_connection_pool: Optional[ConnectionPool] = None


def get_query_optimizer() -> QueryOptimizer:
    """Get or create global query optimizer instance."""
    global _query_optimizer
    if _query_optimizer is None:
        _query_optimizer = QueryOptimizer()
    return _query_optimizer


def get_query_batcher() -> QueryBatcher:
    """Get or create global query batcher instance."""
    global _query_batcher
    if _query_batcher is None:
        _query_batcher = QueryBatcher()
    return _query_batcher


def get_connection_pool() -> ConnectionPool:
    """Get or create global connection pool instance."""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = ConnectionPool()
    return _connection_pool