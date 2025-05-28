"""
Content caching service for storing and retrieving generated content.
"""

import json
import logging
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from prometheus_client import Counter, Histogram

# Prometheus metrics
CACHE_HITS = Counter('content_cache_hits_total', 'Total cache hits')
CACHE_MISSES = Counter('content_cache_misses_total', 'Total cache misses')
CACHE_OPERATIONS = Histogram('content_cache_operation_duration_seconds', 'Cache operation duration')

@dataclass
class CacheEntry:
    """Represents a cached content entry."""
    key: str
    content: Dict[str, Any]
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl: int  # Time to live in seconds
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl <= 0:  # No expiration
            return False
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl)
    
    def touch(self) -> None:
        """Update last accessed time and increment access count."""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1

class ContentCacheService:
    """Service for caching generated content."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize the cache service.
        
        Args:
            max_size: Maximum number of entries to store
            default_ttl: Default time to live in seconds (1 hour)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self.logger = logging.getLogger(__name__)
    
    def _generate_cache_key(
        self,
        syllabus_text: str,
        target_format: str,
        target_duration: Optional[float] = None,
        target_pages: Optional[int] = None
    ) -> str:
        """Generate a cache key for the given parameters."""
        key_data = {
            'syllabus': syllabus_text.strip(),
            'format': target_format,
            'duration': target_duration,
            'pages': target_pages
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(
        self,
        syllabus_text: str,
        target_format: str,
        target_duration: Optional[float] = None,
        target_pages: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached content if available.
        
        Returns:
            Cached content or None if not found/expired
        """
        with CACHE_OPERATIONS.time():
            cache_key = self._generate_cache_key(
                syllabus_text, target_format, target_duration, target_pages
            )
            
            entry = self._cache.get(cache_key)
            if not entry:
                CACHE_MISSES.inc()
                return None
            
            if entry.is_expired():
                self._cache.pop(cache_key, None)
                CACHE_MISSES.inc()
                self.logger.info(f"Cache entry expired: {cache_key}")
                return None
            
            entry.touch()
            CACHE_HITS.inc()
            self.logger.info(f"Cache hit: {cache_key}")
            return entry.content
    
    def set(
        self,
        syllabus_text: str,
        target_format: str,
        content: Dict[str, Any],
        target_duration: Optional[float] = None,
        target_pages: Optional[int] = None,
        ttl: Optional[int] = None
    ) -> None:
        """
        Store content in cache.
        
        Args:
            syllabus_text: The source syllabus text
            target_format: The content format
            content: The generated content to cache
            target_duration: Target duration for podcasts
            target_pages: Target pages for guides
            ttl: Time to live in seconds (uses default if None)
        """
        with CACHE_OPERATIONS.time():
            cache_key = self._generate_cache_key(
                syllabus_text, target_format, target_duration, target_pages
            )
            
            # Evict if cache is full
            if len(self._cache) >= self.max_size:
                self._evict_lru()
            
            entry = CacheEntry(
                key=cache_key,
                content=content,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                access_count=1,
                ttl=ttl or self.default_ttl
            )
            
            self._cache[cache_key] = entry
            self.logger.info(f"Content cached: {cache_key}")
    
    def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if not self._cache:
            return
        
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )
        
        self._cache.pop(lru_key, None)
        self.logger.info(f"Evicted LRU entry: {lru_key}")
    
    def invalidate(
        self,
        syllabus_text: str,
        target_format: str,
        target_duration: Optional[float] = None,
        target_pages: Optional[int] = None
    ) -> bool:
        """
        Invalidate a specific cache entry.
        
        Returns:
            True if entry was found and removed, False otherwise
        """
        cache_key = self._generate_cache_key(
            syllabus_text, target_format, target_duration, target_pages
        )
        
        if cache_key in self._cache:
            self._cache.pop(cache_key)
            self.logger.info(f"Cache entry invalidated: {cache_key}")
            return True
        
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self.logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            self._cache.pop(key, None)
        
        if expired_keys:
            self.logger.info(f"Cleaned up {len(expired_keys)} expired entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self._cache)
        expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired())
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries,
            'max_size': self.max_size,
            'cache_utilization': total_entries / self.max_size if self.max_size > 0 else 0
        }
    
    def get_popular_content(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most accessed content."""
        sorted_entries = sorted(
            self._cache.values(),
            key=lambda e: e.access_count,
            reverse=True
        )
        
        return [
            {
                'key': entry.key,
                'access_count': entry.access_count,
                'created_at': entry.created_at.isoformat(),
                'last_accessed': entry.last_accessed.isoformat()
            }
            for entry in sorted_entries[:limit]
        ] 