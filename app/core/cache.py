"""
Cache backend for query optimization.

Simple in-memory cache implementation for development.
"""

import asyncio
import time
from typing import Any, Dict, Optional


class CacheBackend:
    """Simple in-memory cache backend."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry['expires_at'] > time.time():
                    return entry['value']
                else:
                    # Expired, remove it
                    del self._cache[key]
            return None
            
    async def set(self, key: str, value: Any, ttl: int = 300, expire: int = None):
        """Set value in cache with TTL."""
        # Use expire parameter if provided, otherwise use ttl
        expiry_time = expire if expire is not None else ttl
        async with self._lock:
            self._cache[key] = {
                'value': value,
                'expires_at': time.time() + expiry_time
            }
            
    async def delete(self, key: str):
        """Delete value from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                
    async def clear(self):
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            
    async def cleanup_expired(self):
        """Remove expired entries."""
        async with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry['expires_at'] <= current_time
            ]
            for key in expired_keys:
                del self._cache[key]
    
    async def keys(self, pattern: str = "*") -> list:
        """Get all keys matching pattern."""
        async with self._lock:
            if pattern == "*":
                return list(self._cache.keys())
            # Simple pattern matching (supports * wildcard)
            import fnmatch
            return [key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)]


# Global cache instance
_cache_backend: Optional[CacheBackend] = None


def get_cache_backend() -> CacheBackend:
    """Get or create cache backend instance."""
    global _cache_backend
    if _cache_backend is None:
        _cache_backend = CacheBackend()
    return _cache_backend