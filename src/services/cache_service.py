"""
Redis Cache Service for La Factoria
===================================

Intelligent caching service to reduce AI generation costs by up to 90%
through strategic caching of:
- Generated content for identical topics/content types
- Quality assessment results
- Prompt template compilations
- AI provider responses
"""

import asyncio
import hashlib
import json
import logging
import time
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta, timezone

from ..core.config import settings

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False


class CacheService:
    """Redis-based caching service for educational content generation optimization"""

    def __init__(self):
        self.redis_client = None
        self.cache_enabled = False
        self._initialize_redis()

    def _initialize_redis(self):
        """Initialize Redis connection if available and configured"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available - install with: pip install redis")
            return

        if not settings.REDIS_URL:
            logger.info("Redis URL not configured - caching disabled")
            return

        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            self.cache_enabled = True
            logger.info("Redis cache service initialized successfully")

        except Exception as e:
            logger.warning(f"Failed to initialize Redis: {e}")
            self.cache_enabled = False

    async def health_check(self) -> Dict[str, Any]:
        """Check Redis health and connection status"""
        if not self.cache_enabled:
            return {"status": "disabled", "reason": "Redis not configured or unavailable"}

        try:
            # Test basic Redis operations
            test_key = "health_check_test"
            await self.redis_client.set(test_key, "test_value", ex=10)
            value = await self.redis_client.get(test_key)
            await self.redis_client.delete(test_key)

            if value == "test_value":
                return {
                    "status": "healthy",
                    "response_time_ms": await self._measure_redis_latency(),
                    "memory_usage": await self._get_redis_memory_info()
                }
            else:
                return {"status": "unhealthy", "reason": "Redis read/write test failed"}

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def get_content_cache(
        self,
        content_type: str,
        topic: str,
        age_group: str,
        additional_requirements: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached content for identical generation parameters
        
        Cache key includes all parameters that affect content generation
        """
        if not self.cache_enabled:
            return None

        try:
            cache_key = self._generate_content_cache_key(
                content_type, topic, age_group, additional_requirements
            )

            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                content = json.loads(cached_data)
                
                # Add cache metadata
                content["metadata"]["from_cache"] = True
                content["metadata"]["cache_key"] = cache_key
                content["metadata"]["cached_at"] = content["metadata"].get("cached_at")
                
                logger.info(f"Cache HIT for {content_type}:{topic[:30]}")
                return content

            logger.debug(f"Cache MISS for {content_type}:{topic[:30]}")
            return None

        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            return None

    async def set_content_cache(
        self,
        content_type: str,
        topic: str,
        age_group: str,
        content: Dict[str, Any],
        additional_requirements: Optional[str] = None,
        ttl_hours: int = 24
    ):
        """
        Cache generated content with intelligent TTL based on content type
        """
        if not self.cache_enabled:
            return

        try:
            cache_key = self._generate_content_cache_key(
                content_type, topic, age_group, additional_requirements
            )

            # Add cache metadata
            cache_content = content.copy()
            cache_content["metadata"]["cached_at"] = datetime.now(timezone.utc).isoformat()
            cache_content["metadata"]["cache_ttl_hours"] = ttl_hours

            # Determine TTL based on content type and quality
            content_quality = content.get("quality_metrics", {}).get("overall_quality_score", 0)
            actual_ttl = self._calculate_cache_ttl(content_type, content_quality, ttl_hours)

            await self.redis_client.set(
                cache_key,
                json.dumps(cache_content, default=str),
                ex=actual_ttl
            )

            logger.info(f"Cached content: {content_type}:{topic[:30]} (TTL: {actual_ttl/3600:.1f}h)")

        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")

    async def get_quality_assessment_cache(
        self,
        content_hash: str,
        content_type: str,
        age_group: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached quality assessment results"""
        if not self.cache_enabled:
            return None

        try:
            cache_key = f"quality:{content_hash}:{content_type}:{age_group}"
            cached_quality = await self.redis_client.get(cache_key)
            
            if cached_quality:
                logger.debug("Quality assessment cache HIT")
                return json.loads(cached_quality)

            return None

        except Exception as e:
            logger.warning(f"Quality cache retrieval failed: {e}")
            return None

    async def set_quality_assessment_cache(
        self,
        content_hash: str,
        content_type: str,
        age_group: str,
        quality_metrics: Dict[str, Any],
        ttl_hours: int = 48
    ):
        """Cache quality assessment results (longer TTL since quality is stable)"""
        if not self.cache_enabled:
            return

        try:
            cache_key = f"quality:{content_hash}:{content_type}:{age_group}"
            await self.redis_client.set(
                cache_key,
                json.dumps(quality_metrics, default=str),
                ex=ttl_hours * 3600
            )

            logger.debug("Quality assessment cached successfully")

        except Exception as e:
            logger.warning(f"Quality cache storage failed: {e}")

    async def get_prompt_compilation_cache(
        self,
        template_hash: str,
        variables_hash: str
    ) -> Optional[str]:
        """Get cached compiled prompt"""
        if not self.cache_enabled:
            return None

        try:
            cache_key = f"prompt:{template_hash}:{variables_hash}"
            cached_prompt = await self.redis_client.get(cache_key)
            
            if cached_prompt:
                logger.debug("Prompt compilation cache HIT")
                return cached_prompt

            return None

        except Exception as e:
            logger.warning(f"Prompt cache retrieval failed: {e}")
            return None

    async def set_prompt_compilation_cache(
        self,
        template_hash: str,
        variables_hash: str,
        compiled_prompt: str,
        ttl_hours: int = 12
    ):
        """Cache compiled prompts (medium TTL since templates may change)"""
        if not self.cache_enabled:
            return

        try:
            cache_key = f"prompt:{template_hash}:{variables_hash}"
            await self.redis_client.set(
                cache_key,
                compiled_prompt,
                ex=ttl_hours * 3600
            )

            logger.debug("Compiled prompt cached successfully")

        except Exception as e:
            logger.warning(f"Prompt cache storage failed: {e}")

    def _generate_content_cache_key(
        self,
        content_type: str,
        topic: str,
        age_group: str,
        additional_requirements: Optional[str] = None
    ) -> str:
        """Generate deterministic cache key for content generation parameters"""
        # Create normalized key components
        key_data = {
            "content_type": content_type.lower(),
            "topic": topic.lower().strip(),
            "age_group": age_group.lower(),
            "additional_requirements": additional_requirements.lower().strip() if additional_requirements else ""
        }

        # Create hash for consistent key generation
        key_string = json.dumps(key_data, sort_keys=True)
        content_hash = hashlib.md5(key_string.encode()).hexdigest()[:12]
        
        return f"content:{content_type}:{content_hash}"

    def _calculate_cache_ttl(
        self,
        content_type: str,
        quality_score: float,
        default_ttl_hours: int
    ) -> int:
        """Calculate intelligent TTL based on content type and quality"""
        # Base TTL in seconds
        base_ttl = default_ttl_hours * 3600

        # Quality bonus: higher quality content cached longer
        quality_multiplier = 1.0 + (quality_score - 0.7) * 2  # 0.7=1x, 1.0=1.6x TTL

        # Content type adjustments
        type_multipliers = {
            "flashcards": 2.0,              # Stable content, cache longer
            "master_content_outline": 1.5,   # Structural content, stable
            "one_pager_summary": 1.2,       # Concise content, fairly stable
            "faq_collection": 1.3,          # Q&A format, stable
            "study_guide": 1.0,             # Default caching
            "detailed_reading_material": 0.8, # Long content, may need updates
            "podcast_script": 0.9,          # Audio content, may need revisions
            "reading_guide_questions": 1.1  # Discussion questions, stable
        }

        type_multiplier = type_multipliers.get(content_type, 1.0)
        
        # Calculate final TTL
        final_ttl = int(base_ttl * quality_multiplier * type_multiplier)
        
        # Ensure reasonable bounds (1 hour minimum, 7 days maximum)
        return max(3600, min(final_ttl, 7 * 24 * 3600))

    async def _measure_redis_latency(self) -> float:
        """Measure Redis response latency"""
        start_time = time.time()
        await self.redis_client.ping()
        latency_ms = (time.time() - start_time) * 1000
        return round(latency_ms, 2)

    async def _get_redis_memory_info(self) -> Dict[str, Any]:
        """Get Redis memory usage information"""
        try:
            info = await self.redis_client.info("memory")
            return {
                "used_memory_human": info.get("used_memory_human"),
                "used_memory_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2),
                "maxmemory_mb": round(info.get("maxmemory", 0) / 1024 / 1024, 2) if info.get("maxmemory") else None
            }
        except Exception as e:
            return {"error": str(e)}

    async def clear_content_cache(self, pattern: str = "content:*") -> int:
        """Clear cached content by pattern"""
        if not self.cache_enabled:
            return 0

        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                deleted_count = await self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted_count} cache entries with pattern: {pattern}")
                return deleted_count
            return 0

        except Exception as e:
            logger.warning(f"Cache clearing failed: {e}")
            return 0

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        if not self.cache_enabled:
            return {"status": "disabled", "reason": "Redis not configured"}

        try:
            # Get key counts by type
            content_keys = await self.redis_client.keys("content:*")
            quality_keys = await self.redis_client.keys("quality:*")
            prompt_keys = await self.redis_client.keys("prompt:*")

            # Get Redis info
            info = await self.redis_client.info()

            return {
                "status": "enabled",
                "key_counts": {
                    "content_cache": len(content_keys),
                    "quality_cache": len(quality_keys), 
                    "prompt_cache": len(prompt_keys),
                    "total_keys": info.get("db0", {}).get("keys", 0)
                },
                "memory": await self._get_redis_memory_info(),
                "performance": {
                    "latency_ms": await self._measure_redis_latency(),
                    "commands_processed": info.get("total_commands_processed", 0),
                    "connected_clients": info.get("connected_clients", 0)
                }
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def generate_content_hash(self, content: str) -> str:
        """Generate consistent hash for content caching"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def generate_variables_hash(self, variables: Dict[str, Any]) -> str:
        """Generate hash for template variables"""
        # Normalize variables for consistent hashing
        normalized = json.dumps(variables, sort_keys=True, default=str)
        return hashlib.md5(normalized.encode()).hexdigest()[:12]

    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")