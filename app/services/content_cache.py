"""
Content caching service for storing and retrieving generated content using Redis.

This service provides a scalable caching solution using Redis (Google Cloud Memorystore)
for caching generated content across multiple instances of the application.
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from prometheus_client import Counter, Histogram
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config.settings import get_settings
from app.models.pydantic.content import ContentResponse
from app.utils.redis_pool import (
    redis_get,
    redis_set,
    redis_delete,
    redis_exists,
    redis_batch_operation,
    get_redis_pool,
)

# Prometheus metrics
CACHE_HITS = Counter("content_cache_hits_total", "Total cache hits")
CACHE_MISSES = Counter("content_cache_misses_total", "Total cache misses")
CACHE_ERRORS = Counter(
    "content_cache_errors_total", "Total cache errors", ["error_type"]
)
CACHE_OPERATIONS = Histogram(
    "content_cache_operation_duration_seconds",
    "Cache operation duration",
    ["operation"],
)
CACHE_WARMING_OPERATIONS = Counter(
    "content_cache_warming_total", "Total cache warming operations", ["status"]
)
CACHE_HIT_RATIO = Histogram("content_cache_hit_ratio", "Cache hit ratio over time")


@dataclass
class CacheEntry:
    """Cache entry for content."""

    content: ContentResponse
    created_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheEntry":
        """Create CacheEntry from dictionary."""
        return cls(
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            metadata=data.get("metadata", {}),
        )


class ContentCacheService:
    """Service for caching generated content using Redis."""

    def __init__(
        self, max_size: Optional[int] = None, default_ttl: Optional[int] = None
    ):
        """
        Initialize the cache service with Redis connection.

        Args:
            max_size: Maximum number of entries to store (from settings if None)
            default_ttl: Default time to live in seconds (from settings if None)
        """
        settings = get_settings()
        self.max_size = max_size or settings.cache_max_size
        self.default_ttl = default_ttl or settings.cache_ttl_seconds
        self.logger = logging.getLogger(__name__)

        # Namespace for cache keys to avoid collisions
        self.namespace = "content_cache"

        # Check if caching is enabled
        self.cache_enabled = settings.enable_cache
        if not self.cache_enabled:
            self.logger.info(
                "Caching is disabled. ContentCacheService will operate in no-op mode."
            )

    async def _ensure_pool_ready(self) -> bool:
        """Ensure Redis pool is ready."""
        try:
            pool = await get_redis_pool()
            return pool is not None
        except Exception as e:
            self.logger.error(f"Failed to get Redis pool: {e}")
            CACHE_ERRORS.labels(error_type="connection").inc()
            return False

    def _generate_cache_key(
        self,
        syllabus_text: str,
        target_format: str,
        target_duration: Optional[float] = None,
        target_pages: Optional[int] = None,
        version: str = "default_v1",
    ) -> str:
        """Generate a cache key for the given parameters."""
        key_data = {
            "syllabus": syllabus_text.strip(),
            "format": target_format,
            "duration": target_duration,
            "pages": target_pages,
            "cache_version": version,
        }
        key_str = json.dumps(key_data, sort_keys=True)
        hash_key = hashlib.md5(key_str.encode()).hexdigest()
        return f"{self.namespace}:{hash_key}"

    def _serialize_content(self, content: Any) -> str:
        """Serialize content for Redis storage."""
        if isinstance(content, BaseModel):
            # Pydantic model - use model_dump_json for efficient serialization
            return content.model_dump_json(exclude_none=True)
        elif isinstance(content, dict):
            return json.dumps(content)
        else:
            return json.dumps({"data": content})

    def _deserialize_content(self, content_str: str) -> Any:
        """Deserialize content from Redis storage."""
        try:
            # Try to parse as JSON first
            content_data = json.loads(content_str)

            # If it looks like a Pydantic model dump (has specific fields we expect)
            # We'll leave it as a dict for the caller to reconstruct if needed
            return content_data
        except json.JSONDecodeError:
            self.logger.warning("Failed to deserialize content, returning as string")
            return content_str

    async def get(
        self,
        syllabus_text: str,
        target_format: str,
        target_duration: Optional[float] = None,
        target_pages: Optional[int] = None,
        version: str = "default_v1",
    ) -> Optional[
        Tuple[Any, Optional[Dict[str, Any]]]
    ]:  # Returns (content, quality_metrics_dict)
        """
        Get cached content and its quality metrics if available.

        Returns:
            A tuple (content, quality_metrics_dict) or None if not found/expired.
        """
        # Return None if caching is disabled
        if not self.cache_enabled:
            return None

        with CACHE_OPERATIONS.labels(operation="get").time():
            try:
                cache_key = self._generate_cache_key(
                    syllabus_text, target_format, target_duration, target_pages, version
                )

                # Get entry from Redis using pooled function
                entry_json = await redis_get(f"{cache_key}:entry")
                if not entry_json:
                    CACHE_MISSES.inc()
                    return None

                # Deserialize entry
                entry_data = json.loads(entry_json)
                entry = CacheEntry.from_dict(entry_data)

                # Check expiration
                if datetime.utcnow() > entry.expires_at:
                    await redis_delete(f"{cache_key}:entry", f"{cache_key}:content")
                    CACHE_MISSES.inc()
                    self.logger.info(f"Cache entry expired: {cache_key}")
                    return None

                # Get content
                content_str = await redis_get(f"{cache_key}:content")
                if not content_str:
                    CACHE_MISSES.inc()
                    return None

                CACHE_HITS.inc()
                self.logger.info(f"Cache hit: {cache_key}")
                # Deserialize content and return with quality metrics from entry
                deserialized_content = self._deserialize_content(content_str)
                return deserialized_content, entry.metadata

            except Exception as e:
                self.logger.error(f"Cache get error: {e}")
                CACHE_ERRORS.labels(error_type="get").inc()
                return None

    async def set(
        self,
        syllabus_text: str,
        target_format: str,
        content: Any,
        target_duration: Optional[float] = None,
        target_pages: Optional[int] = None,
        quality_metrics_obj: Optional[
            BaseModel
        ] = None,  # Accept Pydantic QualityMetrics
        ttl: Optional[int] = None,
        version: str = "default_v1",
    ) -> None:
        """
        Store content and its quality metrics in cache.

        Args:
            syllabus_text: The source syllabus text
            target_format: The content format
            content: The generated content to cache
            target_duration: Target duration for podcasts
            target_pages: Target pages for guides
            ttl: Time to live in seconds (uses default if None)
        """
        # Skip if caching is disabled
        if not self.cache_enabled:
            return
            
        with CACHE_OPERATIONS.labels(operation="set").time():
            try:
                cache_key = self._generate_cache_key(
                    syllabus_text, target_format, target_duration, target_pages, version
                )

                # Check cache size and evict if necessary
                pool = await get_redis_pool()
                # Use pool stats instead of dbsize
                
                # Create cache entry
                # Serialize quality metrics if provided
                quality_metrics_dict: Optional[Dict[str, Any]] = None
                if quality_metrics_obj and isinstance(quality_metrics_obj, BaseModel):
                    quality_metrics_dict = quality_metrics_obj.model_dump(
                        exclude_none=True
                    )

                entry = CacheEntry(
                    content=content,
                    created_at=datetime.utcnow(),
                    expires_at=datetime.utcnow()
                    + timedelta(seconds=ttl or self.default_ttl),
                    metadata=quality_metrics_dict or {},
                )

                # Serialize main content payload
                content_str = self._serialize_content(content)

                # Store in Redis with expiration using pooled function
                expire_time = ttl or self.default_ttl
                await redis_set(
                    f"{cache_key}:entry",
                    json.dumps(asdict(entry)),
                    ex=expire_time
                )
                await redis_set(
                    f"{cache_key}:content",
                    content_str,
                    ex=expire_time
                )

                self.logger.info(f"Content cached: {cache_key}")

            except Exception as e:
                self.logger.error(f"Cache set error: {e}")
                CACHE_ERRORS.labels(error_type="set").inc()

    def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        try:
            # Get all cache entry keys
            pattern = f"{self.namespace}:*:entry"
            entry_keys = list(
                self._redis_operation("scan_iter", match=pattern, count=100)
            )

            if not entry_keys:
                return

            # Find LRU entry
            lru_key = None
            lru_time = None

            for key in entry_keys:
                entry_json = self._redis_operation("get", key)
                if entry_json:
                    entry_data = json.loads(entry_json)
                    last_accessed = entry_data.get("created_at")
                    if lru_time is None or last_accessed < lru_time:
                        lru_time = last_accessed
                        lru_key = key.replace(":entry", "")

            # Delete LRU entry
            if lru_key:
                self._redis_operation(
                    "delete", f"{lru_key}:entry", f"{lru_key}:content"
                )
                self.logger.info(f"Evicted LRU entry: {lru_key}")

        except RedisError as e:
            self.logger.error(f"LRU eviction error: {e}")
            CACHE_ERRORS.labels(error_type="evict").inc()

    def invalidate(
        self,
        syllabus_text: str,
        target_format: str,
        target_duration: Optional[float] = None,
        target_pages: Optional[int] = None,
        version: str = "default_v1",
    ) -> bool:
        """
        Invalidate a specific cache entry.

        Returns:
            True if entry was found and removed, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(
                syllabus_text, target_format, target_duration, target_pages, version
            )

            # Delete both entry and content
            deleted = self._redis_operation(
                "delete", f"{cache_key}:entry", f"{cache_key}:content"
            )

            if deleted > 0:
                self.logger.info(f"Cache entry invalidated: {cache_key}")
                return True

            return False

        except RedisError as e:
            self.logger.error(f"Cache invalidate error: {e}")
            CACHE_ERRORS.labels(error_type="invalidate").inc()
            return False

    def clear(self) -> None:
        """Clear all cache entries."""
        try:
            self._redis_operation("flushdb")
            self.logger.info("Cache cleared")
        except RedisError as e:
            self.logger.error(f"Cache clear error: {e}")
            CACHE_ERRORS.labels(error_type="clear").inc()

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of entries removed
        """
        try:
            pattern = f"{self.namespace}:*:entry"
            entry_keys = list(
                self._redis_operation("scan_iter", match=pattern, count=100)
            )

            expired_count = 0
            for key in entry_keys:
                entry_json = self._redis_operation("get", key)
                if entry_json:
                    entry_data = json.loads(entry_json)
                    entry = CacheEntry.from_dict(entry_data)
                    if datetime.utcnow() > entry.expires_at:
                        cache_key = key.replace(":entry", "")
                        self._redis_operation(
                            "delete", f"{cache_key}:entry", f"{cache_key}:content"
                        )
                        expired_count += 1

            if expired_count > 0:
                self.logger.info(f"Cleaned up {expired_count} expired entries")

            return expired_count

        except RedisError as e:
            self.logger.error(f"Cleanup error: {e}")
            CACHE_ERRORS.labels(error_type="cleanup").inc()
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            info = self._redis_operation("info", "memory")
            dbsize = self._redis_operation("dbsize")

            # Count actual cache entries (divide by 2 since we store entry + content)
            pattern = f"{self.namespace}:*:entry"
            entry_count = len(
                list(self._redis_operation("scan_iter", match=pattern, count=100))
            )

            return {
                "total_entries": entry_count,
                "total_keys": dbsize,
                "max_size": self.max_size,
                "cache_utilization": (
                    entry_count / self.max_size if self.max_size > 0 else 0
                ),
                "memory_used": info.get("used_memory_human", "unknown"),
                "memory_peak": info.get("used_memory_peak_human", "unknown"),
            }
        except RedisError as e:
            self.logger.error(f"Get stats error: {e}")
            CACHE_ERRORS.labels(error_type="stats").inc()
            return {
                "error": str(e),
                "total_entries": 0,
                "max_size": self.max_size,
            }

    def get_popular_content(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most accessed content."""
        try:
            pattern = f"{self.namespace}:*:entry"
            entry_keys = list(
                self._redis_operation("scan_iter", match=pattern, count=100)
            )

            entries = []
            for key in entry_keys:
                entry_json = self._redis_operation("get", key)
                if entry_json:
                    entry_data = json.loads(entry_json)
                    entries.append(
                        {
                            "key": entry_data["key"],
                            "access_count": entry_data["access_count"],
                            "created_at": entry_data["created_at"],
                            "last_accessed": entry_data["last_accessed"],
                        }
                    )

            # Sort by access count
            entries.sort(key=lambda x: x["access_count"], reverse=True)

            return entries[:limit]

        except RedisError as e:
            self.logger.error(f"Get popular content error: {e}")
            CACHE_ERRORS.labels(error_type="popular").inc()
            return []

    def health_check(self) -> Dict[str, Any]:
        """Check Redis connection health."""
        try:
            start_time = datetime.utcnow()
            self._redis_operation("ping")
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000

            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "connection_pool": {
                    "created_connections": self.redis_pool.connection_kwargs.get(
                        "max_connections", 0
                    ),
                    "available_connections": len(
                        self.redis_pool._available_connections
                    ),
                    "in_use_connections": len(self.redis_pool._in_use_connections),
                },
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def warm_cache(self, popular_queries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Warm the cache with frequently requested content.

        Args:
            popular_queries: List of query dictionaries with 'syllabus_text', 'target_format', etc.

        Returns:
            Dictionary with warming statistics
        """
        if not self.cache_enabled:
            return {"status": "disabled", "warmed": 0, "failed": 0}

        warmed_count = 0
        failed_count = 0

        for query in popular_queries:
            try:
                # Check if already cached
                existing = self.get(
                    query.get("syllabus_text", ""),
                    query.get("target_format", ""),
                    query.get("target_duration"),
                    query.get("target_pages"),
                    query.get("version", "default_v1"),
                )

                if existing is None:
                    # Would need to generate content here in a real implementation
                    # For now, just log the warming attempt
                    self.logger.info(
                        f"Cache warming opportunity: {query.get('target_format')}"
                    )
                    CACHE_WARMING_OPERATIONS.labels(status="attempted").inc()
                else:
                    warmed_count += 1
                    CACHE_WARMING_OPERATIONS.labels(status="already_cached").inc()

            except Exception as e:
                self.logger.error(f"Cache warming failed for query {query}: {e}")
                failed_count += 1
                CACHE_WARMING_OPERATIONS.labels(status="failed").inc()

        CACHE_WARMING_OPERATIONS.labels(status="completed").inc()
        return {
            "warmed": warmed_count,
            "failed": failed_count,
            "total": len(popular_queries),
        }

    def get_cache_hit_ratio(self) -> float:
        """Calculate current cache hit ratio."""
        try:
            # Get current metric values (this is a simplified version)
            # In production, you'd want to calculate this over a time window
            hits = (
                CACHE_HITS._value._value if hasattr(CACHE_HITS._value, "_value") else 0
            )
            misses = (
                CACHE_MISSES._value._value
                if hasattr(CACHE_MISSES._value, "_value")
                else 0
            )

            total = hits + misses
            if total == 0:
                return 0.0

            ratio = hits / total
            CACHE_HIT_RATIO.observe(ratio)
            return ratio

        except Exception as e:
            self.logger.error(f"Error calculating cache hit ratio: {e}")
            return 0.0

    def __del__(self):
        """Cleanup Redis connection on deletion."""
        try:
            if hasattr(self, "redis_pool"):
                self.redis_pool.disconnect()
        except Exception:
            pass
