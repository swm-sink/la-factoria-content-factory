"""
Query monitoring middleware for tracking database performance.

This middleware monitors and logs database query patterns to identify performance issues.
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import get_metrics_collector

logger = logging.getLogger(__name__)


class QueryMonitor:
    """Monitors database queries for performance analysis."""
    
    def __init__(self):
        self._queries: List[Dict[str, Any]] = []
        self._query_count = 0
        self._total_time = 0.0
        self._slow_query_threshold = 1.0  # seconds
        
    def record_query(
        self,
        query_type: str,
        collection: str,
        operation: str,
        duration: float,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Record a database query.
        
        Args:
            query_type: Type of query (e.g., 'firestore', 'postgres')
            collection: Collection/table name
            operation: Operation type (e.g., 'get', 'update', 'batch')
            duration: Query duration in seconds
            details: Additional query details
        """
        query_info = {
            'query_type': query_type,
            'collection': collection,
            'operation': operation,
            'duration': duration,
            'timestamp': time.time(),
            'details': details or {}
        }
        
        self._queries.append(query_info)
        self._query_count += 1
        self._total_time += duration
        
        # Log slow queries
        if duration > self._slow_query_threshold:
            logger.warning(
                f"Slow query detected: {query_type}.{collection}.{operation} "
                f"took {duration:.3f}s"
            )
            
        # Send metrics
        metrics = get_metrics_collector()
        metrics.increment('database.query.count', tags={
            'type': query_type,
            'collection': collection,
            'operation': operation
        })
        metrics.timing('database.query.duration', duration * 1000, tags={
            'type': query_type,
            'collection': collection,
            'operation': operation
        })
        
    def get_stats(self) -> Dict[str, Any]:
        """Get query statistics."""
        if self._query_count == 0:
            return {
                'query_count': 0,
                'total_time': 0.0,
                'average_time': 0.0,
                'queries_by_type': {},
                'queries_by_collection': {},
                'slow_queries': []
            }
            
        # Aggregate by type
        queries_by_type = {}
        queries_by_collection = {}
        slow_queries = []
        
        for query in self._queries:
            # By type
            query_type = query['query_type']
            if query_type not in queries_by_type:
                queries_by_type[query_type] = {'count': 0, 'total_time': 0.0}
            queries_by_type[query_type]['count'] += 1
            queries_by_type[query_type]['total_time'] += query['duration']
            
            # By collection
            collection = query['collection']
            if collection not in queries_by_collection:
                queries_by_collection[collection] = {'count': 0, 'total_time': 0.0}
            queries_by_collection[collection]['count'] += 1
            queries_by_collection[collection]['total_time'] += query['duration']
            
            # Slow queries
            if query['duration'] > self._slow_query_threshold:
                slow_queries.append({
                    'type': query['query_type'],
                    'collection': query['collection'],
                    'operation': query['operation'],
                    'duration': query['duration']
                })
                
        return {
            'query_count': self._query_count,
            'total_time': self._total_time,
            'average_time': self._total_time / self._query_count,
            'queries_by_type': queries_by_type,
            'queries_by_collection': queries_by_collection,
            'slow_queries': sorted(slow_queries, key=lambda x: x['duration'], reverse=True)[:10]
        }
        
    def reset(self):
        """Reset query statistics."""
        self._queries.clear()
        self._query_count = 0
        self._total_time = 0.0
        
    def detect_n_plus_one(self) -> List[Dict[str, Any]]:
        """
        Detect potential N+1 query patterns.
        
        Returns:
            List of potential N+1 patterns detected
        """
        patterns = []
        
        # Group queries by collection and operation
        query_groups = {}
        for query in self._queries:
            key = f"{query['query_type']}.{query['collection']}.{query['operation']}"
            if key not in query_groups:
                query_groups[key] = []
            query_groups[key].append(query)
            
        # Look for repeated patterns
        for key, queries in query_groups.items():
            if len(queries) > 5:  # Threshold for potential N+1
                # Check if queries happened in quick succession
                time_diffs = []
                for i in range(1, len(queries)):
                    time_diff = queries[i]['timestamp'] - queries[i-1]['timestamp']
                    time_diffs.append(time_diff)
                    
                avg_time_diff = sum(time_diffs) / len(time_diffs) if time_diffs else 0
                
                # If queries are happening within 100ms of each other, likely N+1
                if avg_time_diff < 0.1:
                    patterns.append({
                        'pattern': key,
                        'count': len(queries),
                        'total_time': sum(q['duration'] for q in queries),
                        'average_interval': avg_time_diff
                    })
                    
        return patterns


# Global query monitor instance
_query_monitor: Optional[QueryMonitor] = None


def get_query_monitor() -> QueryMonitor:
    """Get or create global query monitor instance."""
    global _query_monitor
    if _query_monitor is None:
        _query_monitor = QueryMonitor()
    return _query_monitor


class QueryMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware that monitors database queries per request."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and monitor queries."""
        # Get or create query monitor for this request
        monitor = QueryMonitor()
        request.state.query_monitor = monitor
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        request_time = time.time() - start_time
        
        # Get query stats
        stats = monitor.get_stats()
        
        # Log if too many queries
        if stats['query_count'] > 50:
            logger.warning(
                f"High query count detected for {request.method} {request.url.path}: "
                f"{stats['query_count']} queries in {request_time:.3f}s"
            )
            
        # Check for N+1 patterns
        n_plus_one_patterns = monitor.detect_n_plus_one()
        if n_plus_one_patterns:
            logger.error(
                f"Potential N+1 query patterns detected for {request.method} {request.url.path}: "
                f"{n_plus_one_patterns}"
            )
            
        # Add query stats to response headers (for debugging)
        if stats['query_count'] > 0:
            response.headers['X-DB-Query-Count'] = str(stats['query_count'])
            response.headers['X-DB-Query-Time'] = f"{stats['total_time']:.3f}"
            
        # Send overall request metrics
        metrics = get_metrics_collector()
        metrics.timing('request.database.queries', stats['query_count'], tags={
            'method': request.method,
            'path': request.url.path
        })
        metrics.timing('request.database.time', stats['total_time'] * 1000, tags={
            'method': request.method,
            'path': request.url.path
        })
        
        return response


def monitor_query(query_type: str = 'firestore'):
    """
    Decorator to monitor database queries.
    
    Args:
        query_type: Type of query being monitored
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Extract collection name from args/kwargs if possible
            collection = 'unknown'
            if 'collection_name' in kwargs:
                collection = kwargs['collection_name']
            elif 'collection' in kwargs:
                collection = kwargs['collection']
            elif len(args) > 1 and isinstance(args[1], str):
                collection = args[1]
                
            # Determine operation from function name
            operation = func.__name__.split('_')[0]  # e.g., 'get', 'update', 'query'
            
            # Monitor query execution
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record in monitor
                monitor = get_query_monitor()
                monitor.record_query(
                    query_type=query_type,
                    collection=collection,
                    operation=operation,
                    duration=duration,
                    details={'args': str(args)[:100], 'kwargs': str(kwargs)[:100]}
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Query failed after {duration:.3f}s: {e}")
                raise
                
        return wrapper
    return decorator