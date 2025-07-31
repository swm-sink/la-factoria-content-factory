"""
HTTP response caching headers middleware for FastAPI.
"""

import json
import time
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timezone, timedelta
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp
import logging

from app.core.config.cache_config import CacheConfig, CacheStrategy
from app.utils.cache_utils import CacheUtils


logger = logging.getLogger(__name__)


class CacheHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add appropriate cache headers to responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.cache_config = CacheConfig()
        self.cache_utils = CacheUtils()
        self.invalidation_handler = CacheInvalidationHandler()
        
        # Track resource versions for cache invalidation
        self.resource_versions: Dict[str, str] = {}
        
        # Cache metrics
        self.cache_hits = 0
        self.cache_misses = 0
        self.conditional_requests = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add cache headers to response."""
        start_time = time.time()
        
        # Get cache configuration for this path
        cache_config = self.cache_config.get_cache_config(
            request.url.path,
            request.headers.get("accept", "application/json")
        )
        
        # Check for conditional request headers
        if_none_match = request.headers.get("if-none-match")
        if_modified_since = request.headers.get("if-modified-since")
        
        # Track conditional requests
        if if_none_match or if_modified_since:
            self.conditional_requests += 1
        
        # Process the request
        response = await call_next(request)
        
        # Skip cache headers for error responses (except 304)
        if response.status_code >= 400:
            return response
        
        # Apply cache headers based on configuration
        await self._apply_cache_headers(request, response, cache_config)
        
        # Handle conditional requests
        if response.status_code == 200 and (if_none_match or if_modified_since):
            if await self._handle_conditional_request(request, response, if_none_match, if_modified_since):
                # Return 304 Not Modified
                response.status_code = 304
                # Remove body for 304 responses
                response.body = b""
                self.cache_hits += 1
            else:
                self.cache_misses += 1
        
        # Add performance timing header
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        # Log cache performance periodically
        if (self.cache_hits + self.cache_misses) % 1000 == 0:
            self._log_cache_metrics()
        
        return response
    
    async def _apply_cache_headers(self, request: Request, response: Response, cache_config: Dict[str, Any]) -> None:
        """Apply cache headers to the response."""
        max_age = cache_config.get("max_age", 0)
        strategy = cache_config.get("strategy", CacheStrategy.PRIVATE)
        immutable = cache_config.get("immutable", False)
        
        # Build Cache-Control header
        cache_control = self.cache_utils.build_cache_control_header(
            max_age=max_age,
            public=(strategy == CacheStrategy.PUBLIC),
            private=(strategy == CacheStrategy.PRIVATE),
            no_cache=(strategy == CacheStrategy.NO_CACHE),
            immutable=immutable,
            must_revalidate=(not immutable and max_age > 0),
            stale_while_revalidate=60 if max_age > 0 and not immutable else None
        )
        
        response.headers["Cache-Control"] = cache_control
        
        # Add Expires header for backward compatibility
        if max_age > 0:
            expires = datetime.now(timezone.utc) + timedelta(seconds=max_age)
            response.headers["Expires"] = self.cache_utils.format_http_date(expires)
        
        # Add ETag for dynamic content
        if self.cache_config.should_use_etag(request.url.path):
            etag = await self._generate_response_etag(response)
            if etag:
                response.headers["ETag"] = etag
        
        # Add Last-Modified header
        response.headers["Last-Modified"] = self.cache_utils.format_http_date()
        
        # Add Vary header for content negotiation
        if "accept" in request.headers:
            self._add_vary_header(response, "Accept")
        
        if "accept-encoding" in request.headers:
            self._add_vary_header(response, "Accept-Encoding")
        
        # For authenticated endpoints, vary by authorization
        if request.url.path.startswith("/api/v1/") and "authorization" in request.headers:
            self._add_vary_header(response, "Authorization")
    
    async def _generate_response_etag(self, response: Response) -> Optional[str]:
        """Generate ETag for response content."""
        try:
            # For JSON responses, generate ETag from content
            content_type = response.headers.get("content-type", "")
            
            if "application/json" in content_type:
                # Read response body
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                
                # Generate ETag
                etag = self.cache_utils.generate_etag(body)
                
                # Reset body iterator
                async def new_body_iterator():
                    yield body
                
                response.body_iterator = new_body_iterator()
                return etag
            
            # For other content types, use content hash if available
            if hasattr(response, "_content_hash"):
                return f'W/"{response._content_hash}"'
            
        except Exception as e:
            logger.warning(f"Failed to generate ETag: {e}")
        
        return None
    
    async def _handle_conditional_request(
        self,
        request: Request,
        response: Response,
        if_none_match: Optional[str],
        if_modified_since: Optional[str]
    ) -> bool:
        """Handle conditional request and return True if 304 should be returned."""
        # Get current ETag and Last-Modified from response
        etag = response.headers.get("etag")
        last_modified_str = response.headers.get("last-modified")
        
        # Parse Last-Modified
        last_modified = None
        if last_modified_str:
            last_modified = self.cache_utils.parse_if_modified_since(last_modified_str)
        
        # Check if 304 should be returned
        return self.cache_utils.should_return_304(
            etag=etag,
            if_none_match=if_none_match,
            last_modified=last_modified,
            if_modified_since=if_modified_since
        )
    
    def _add_vary_header(self, response: Response, value: str) -> None:
        """Add value to Vary header."""
        existing = response.headers.get("vary", "")
        if existing:
            values = set(v.strip() for v in existing.split(","))
            values.add(value)
            response.headers["Vary"] = ", ".join(sorted(values))
        else:
            response.headers["Vary"] = value
    
    def _log_cache_metrics(self) -> None:
        """Log cache performance metrics."""
        total_requests = self.cache_hits + self.cache_misses
        if total_requests > 0:
            hit_rate = (self.cache_hits / total_requests) * 100
            logger.info(
                f"Cache metrics - Hits: {self.cache_hits}, Misses: {self.cache_misses}, "
                f"Hit rate: {hit_rate:.2f}%, Conditional requests: {self.conditional_requests}"
            )
    
    def invalidate_cache(self, pattern: str) -> None:
        """Invalidate cache for resources matching pattern."""
        # This is a placeholder for cache invalidation logic
        # In a real implementation, this would interact with CDN or cache layer
        logger.info(f"Cache invalidation requested for pattern: {pattern}")
        
        # Update resource version to force cache miss
        import uuid
        self.resource_versions[pattern] = str(uuid.uuid4())[:8]


class CacheInvalidationHandler:
    """Global cache invalidation handler."""
    
    _instance = None
    _invalidated_patterns: Dict[str, datetime] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def invalidate(self, pattern: str) -> None:
        """Mark a pattern as invalidated."""
        self._invalidated_patterns[pattern] = datetime.now(timezone.utc)
        logger.info(f"Cache invalidation marked for pattern: {pattern}")
    
    def is_invalidated(self, path: str, since: datetime) -> bool:
        """Check if a path matches any invalidated pattern since a given time."""
        for pattern, invalidation_time in self._invalidated_patterns.items():
            if invalidation_time > since and self._matches_pattern(path, pattern):
                return True
        return False
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches pattern (supports * wildcard)."""
        if "*" in pattern:
            prefix = pattern.replace("*", "")
            return path.startswith(prefix)
        return path == pattern
    
    def cleanup_old_invalidations(self, max_age_hours: int = 24) -> None:
        """Remove old invalidation records."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        self._invalidated_patterns = {
            k: v for k, v in self._invalidated_patterns.items()
            if v > cutoff
        }