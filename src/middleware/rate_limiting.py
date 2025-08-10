"""
Enhanced Rate Limiting Middleware for La Factoria
================================================

Redis-backed rate limiting with:
- Configurable limits per endpoint type
- Rate limit headers in responses  
- Graceful fallback to in-memory when Redis unavailable
- Different limits for expensive AI vs cheap endpoints
- Proper monitoring and metrics
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from fastapi import Request, Response, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.config import settings

logger = logging.getLogger(__name__)

# Try to import Redis for backend
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

class EnhancedRateLimiter:
    """Redis-backed rate limiter with configurable limits"""
    
    def __init__(self):
        self.redis_client = None
        self.redis_available = False
        self.fallback_storage = {}  # In-memory fallback
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection if available"""
        if not REDIS_AVAILABLE:
            logger.info("Redis not available, using in-memory rate limiting")
            return
            
        if not settings.REDIS_URL:
            logger.info("Redis URL not configured, using in-memory rate limiting")
            return
            
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8", 
                decode_responses=True,
                socket_timeout=2,  # Short timeout for rate limiting
                socket_connect_timeout=2
            )
            self.redis_available = True
            logger.info("Enhanced Redis rate limiter initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis for rate limiting: {e}")
            self.redis_available = False

    async def check_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limit
        
        Returns:
            (allowed: bool, headers: dict)
        """
        if self.redis_available:
            return await self._check_redis_rate_limit(key, limit, window_seconds)
        else:
            return await self._check_memory_rate_limit(key, limit, window_seconds)
    
    async def _check_redis_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit using Redis backend"""
        try:
            current_time = int(time.time())
            window_start = current_time - window_seconds
            
            # Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, window_seconds + 1)
            
            results = await pipe.execute()
            current_count = results[1]  # Count before adding current request
            
            # Calculate headers
            remaining = max(0, limit - current_count - 1)
            reset_time = current_time + window_seconds
            
            headers = {
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time),
                "X-RateLimit-Window": str(window_seconds)
            }
            
            allowed = current_count < limit
            
            if not allowed:
                headers["Retry-After"] = str(window_seconds)
            
            return allowed, headers
            
        except Exception as e:
            logger.warning(f"Redis rate limiting failed, falling back to memory: {e}")
            self.redis_available = False
            return await self._check_memory_rate_limit(key, limit, window_seconds)
    
    async def _check_memory_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """Fallback in-memory rate limiting"""
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Clean old entries
        if key in self.fallback_storage:
            self.fallback_storage[key] = [
                timestamp for timestamp in self.fallback_storage[key]
                if timestamp > window_start
            ]
        else:
            self.fallback_storage[key] = []
        
        current_count = len(self.fallback_storage[key])
        allowed = current_count < limit
        
        if allowed:
            self.fallback_storage[key].append(current_time)
        
        remaining = max(0, limit - current_count - (1 if allowed else 0))
        reset_time = int(current_time + window_seconds)
        
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining), 
            "X-RateLimit-Reset": str(reset_time),
            "X-RateLimit-Window": str(window_seconds),
            "X-RateLimit-Backend": "memory"
        }
        
        if not allowed:
            headers["Retry-After"] = str(window_seconds)
        
        return allowed, headers

    async def health_check(self) -> Dict[str, Any]:
        """Check rate limiter health"""
        if not self.redis_available:
            return {
                "status": "degraded",
                "backend": "memory",
                "reason": "Redis unavailable"
            }
        
        try:
            start_time = time.time()
            await self.redis_client.ping()
            latency = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "backend": "redis", 
                "latency_ms": round(latency, 2)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "backend": "redis",
                "error": str(e)
            }

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with configurable endpoint-specific limits"""
    
    def __init__(self, app, limiter: EnhancedRateLimiter):
        super().__init__(app)
        self.limiter = limiter
        
        # Configure endpoint-specific rate limits
        self.endpoint_limits = {
            # Expensive AI generation endpoints (lower limits)
            "generate/master_content_outline": (5, 300),    # 5 per 5 minutes
            "generate/podcast_script": (3, 300),            # 3 per 5 minutes
            "generate/detailed_reading_material": (5, 300), # 5 per 5 minutes
            "generate/study_guide": (8, 300),               # 8 per 5 minutes
            "generate/one_pager_summary": (10, 300),        # 10 per 5 minutes
            "generate/faq_collection": (10, 300),           # 10 per 5 minutes
            "generate/flashcards": (15, 300),               # 15 per 5 minutes
            "generate/reading_guide_questions": (15, 300),  # 15 per 5 minutes
            
            # Regular API endpoints (higher limits)
            "content-types": (100, 60),     # 100 per minute
            "health": (0, 0),               # No limit
            "metrics": (0, 0),              # No limit
            "ready": (0, 0),                # No limit
            "live": (0, 0),                 # No limit
        }
        
        # Default limits for unspecified endpoints
        self.default_limits = (settings.RATE_LIMIT_REQUESTS_PER_MINUTE, 60)

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Extract endpoint from path
        endpoint = self._extract_endpoint(request.url.path)
        
        # Get rate limits for this endpoint
        limit, window = self._get_endpoint_limits(endpoint)
        
        # Skip rate limiting for unlimited endpoints
        if limit == 0:
            response = await call_next(request)
            return response
            
        # Generate rate limit key
        client_id = get_remote_address(request)
        rate_limit_key = f"rate_limit:{endpoint}:{client_id}"
        
        # Check rate limit
        allowed, headers = await self.limiter.check_rate_limit(
            rate_limit_key, limit, window
        )
        
        if not allowed:
            # Rate limit exceeded
            logger.warning(f"Rate limit exceeded for {client_id} on {endpoint}")
            
            response = Response(
                content='{"detail": "Rate limit exceeded"}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers=headers
            )
            response.headers["Content-Type"] = "application/json"
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value
        
        return response
    
    def _extract_endpoint(self, path: str) -> str:
        """Extract endpoint identifier from request path"""
        # Remove /api/v1/ prefix and clean up path
        clean_path = path.lstrip('/')
        
        if clean_path.startswith('api/v1/'):
            clean_path = clean_path[7:]  # Remove 'api/v1/'
        
        # Handle nested paths
        parts = clean_path.split('/')
        if len(parts) >= 2 and parts[0] == 'generate':
            return f"{parts[0]}/{parts[1]}"
        
        return parts[0] if parts else "unknown"
    
    def _get_endpoint_limits(self, endpoint: str) -> Tuple[int, int]:
        """Get rate limits for specific endpoint"""
        return self.endpoint_limits.get(endpoint, self.default_limits)

# Global instances
enhanced_limiter = EnhancedRateLimiter()
rate_limiting_middleware = RateLimitingMiddleware

# Traditional slowapi limiter for backward compatibility
traditional_limiter = Limiter(key_func=get_remote_address)