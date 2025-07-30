"""Rate limiting middleware for API protection."""

import logging
import time
from typing import Callable, Optional

from fastapi import HTTPException, Request, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.core.config.settings import get_settings
from app.core.errors import create_error_response

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Initialize Redis client for distributed rate limiting
try:
    import redis
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password,
        ssl=settings.redis_ssl,
        decode_responses=True,
    )
    # Test connection
    redis_client.ping()
    logger.info("Redis connected for rate limiting")
except Exception as e:
    logger.warning(f"Redis not available for rate limiting: {e}. Using in-memory storage.")
    redis_client = None


def get_rate_limit_key(request: Request) -> str:
    """
    Get rate limit key from request.
    
    Prioritizes API key if present, otherwise uses IP address.
    """
    # Check for API key
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key}"
    
    # Check for authenticated user
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.id}"
    
    # Fall back to IP address
    return get_remote_address(request) or "unknown"


# Create limiter instance
limiter = Limiter(
    key_func=get_rate_limit_key,
    storage_uri=f"redis://{settings.redis_host}:{settings.redis_port}" if redis_client else "memory://",
    default_limits=["200 per day", "50 per hour"],
)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with per-endpoint configuration.
    """
    
    # Endpoint-specific limits
    ENDPOINT_LIMITS = {
        # Content generation endpoints - more restrictive
        "/api/v1/content/generate": "10 per hour",
        "/api/v1/content/generate-outline": "20 per hour",
        "/api/v1/content/batch": "5 per hour",
        
        # Auth endpoints - prevent brute force
        "/api/v1/auth/login": "10 per minute",
        "/api/v1/auth/register": "5 per hour",
        "/api/v1/auth/reset-password": "5 per hour",
        
        # General API endpoints
        "/api/v1/users": "100 per hour",
        "/api/v1/content": "200 per hour",
        
        # Health checks - very permissive
        "/api/v1/health": "1000 per minute",
        "/health": "1000 per minute",
        
        # Admin endpoints - moderate limits
        "/api/v1/admin": "50 per hour",
    }
    
    # Exempt paths from rate limiting
    EXEMPT_PATHS = {
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/internal/health",
    }
    
    # Cost multipliers for expensive operations
    COST_MULTIPLIERS = {
        "podcast_script": 5,
        "study_guide": 3,
        "detailed_reading": 4,
        "flashcards": 2,
        "faqs": 2,
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting to requests."""
        path = request.url.path
        
        # Skip rate limiting for exempt paths
        if path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # Skip for internal requests
        if request.headers.get("X-Internal-Request") == "true":
            return await call_next(request)
        
        # Get the appropriate rate limit for this endpoint
        rate_limit = self._get_rate_limit_for_path(path)
        
        # Apply rate limiting
        try:
            # Check rate limit
            if not self._check_rate_limit(request, rate_limit):
                raise RateLimitExceeded
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            self._add_rate_limit_headers(request, response, rate_limit)
            
            return response
            
        except RateLimitExceeded:
            logger.warning(
                f"Rate limit exceeded for {get_rate_limit_key(request)} on {path}"
            )
            return self._create_rate_limit_response(request, rate_limit)
        
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Don't block request on rate limiting errors
            return await call_next(request)
    
    def _get_rate_limit_for_path(self, path: str) -> str:
        """Get rate limit for a specific path."""
        # Check exact match first
        if path in self.ENDPOINT_LIMITS:
            return self.ENDPOINT_LIMITS[path]
        
        # Check prefix match
        for endpoint, limit in self.ENDPOINT_LIMITS.items():
            if path.startswith(endpoint):
                return limit
        
        # Default limit
        return "100 per hour"
    
    def _check_rate_limit(self, request: Request, rate_limit: str) -> bool:
        """Check if request is within rate limit."""
        key = get_rate_limit_key(request)
        
        # Parse rate limit
        count, period = rate_limit.split(" per ")
        count = int(count)
        
        # Convert period to seconds
        period_seconds = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        }.get(period, 3600)
        
        # Apply cost multiplier for expensive operations
        cost = self._get_request_cost(request)
        
        if redis_client:
            # Use Redis for distributed rate limiting
            return self._check_redis_rate_limit(key, count, period_seconds, cost)
        else:
            # Fall back to in-memory (not recommended for production)
            return self._check_memory_rate_limit(key, count, period_seconds, cost)
    
    def _get_request_cost(self, request: Request) -> int:
        """Calculate the cost of a request for rate limiting."""
        # Check if this is a content generation request
        if request.url.path.startswith("/api/v1/content/generate"):
            # Try to get content type from request
            if hasattr(request, "json"):
                try:
                    body = request.json()
                    content_type = body.get("content_type", "")
                    return self.COST_MULTIPLIERS.get(content_type, 1)
                except:
                    pass
        return 1
    
    def _check_redis_rate_limit(
        self, key: str, limit: int, period: int, cost: int = 1
    ) -> bool:
        """Check rate limit using Redis."""
        try:
            current_time = int(time.time())
            window_start = current_time - period
            redis_key = f"rate_limit:{key}:{window_start // period}"
            
            # Get current count
            current = redis_client.get(redis_key)
            current_count = int(current) if current else 0
            
            # Check if limit exceeded
            if current_count + cost > limit:
                return False
            
            # Increment counter
            redis_client.incrby(redis_key, cost)
            redis_client.expire(redis_key, period)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            # Allow request on error
            return True
    
    def _check_memory_rate_limit(
        self, key: str, limit: int, period: int, cost: int = 1
    ) -> bool:
        """Simple in-memory rate limiting (not distributed)."""
        # This is a placeholder - in production, always use Redis
        return True
    
    def _add_rate_limit_headers(
        self, request: Request, response: Response, rate_limit: str
    ) -> None:
        """Add rate limit headers to response."""
        key = get_rate_limit_key(request)
        count, period = rate_limit.split(" per ")
        count = int(count)
        
        # Calculate period in seconds
        period_seconds = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        }.get(period, 3600)
        
        if redis_client:
            try:
                current_time = int(time.time())
                window_start = current_time - period_seconds
                redis_key = f"rate_limit:{key}:{window_start // period_seconds}"
                
                current = redis_client.get(redis_key)
                current_count = int(current) if current else 0
                
                response.headers["X-RateLimit-Limit"] = str(count)
                response.headers["X-RateLimit-Remaining"] = str(
                    max(0, count - current_count)
                )
                response.headers["X-RateLimit-Reset"] = str(
                    window_start + period_seconds
                )
            except Exception as e:
                logger.error(f"Error adding rate limit headers: {e}")
    
    def _create_rate_limit_response(self, request: Request, rate_limit: str) -> Response:
        """Create rate limit exceeded response."""
        # Calculate retry after
        _, period = rate_limit.split(" per ")
        period_seconds = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        }.get(period, 3600)
        
        retry_after = min(period_seconds, 300)  # Max 5 minutes
        
        # Create error response
        error_response = create_error_response(
            code="RATE_LIMIT_EXCEEDED",
            message=f"Rate limit exceeded. Please retry after {retry_after} seconds.",
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            details={
                "limit": rate_limit,
                "retry_after": retry_after,
                "key": get_rate_limit_key(request),
            }
        )
        
        # Create response
        response = Response(
            content=error_response,
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": rate_limit.split(" ")[0],
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + retry_after),
            },
            media_type="application/json"
        )
        
        return response