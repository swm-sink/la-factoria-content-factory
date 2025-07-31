"""
Cache configuration for HTTP response headers.
"""

from typing import Dict, Optional
from enum import Enum


class CacheStrategy(str, Enum):
    """Cache strategies for different content types."""
    NO_CACHE = "no-cache"
    PRIVATE = "private"
    PUBLIC = "public"
    IMMUTABLE = "immutable"


class CacheConfig:
    """Cache configuration for different content types."""
    
    # Static assets (CSS, JS, images) - 1 year cache
    STATIC_CACHE_MAX_AGE = 31536000  # 1 year in seconds
    
    # API responses - Short-term caching
    API_CACHE_MAX_AGE = 300  # 5 minutes for general API responses
    API_CACHE_MAX_AGE_LONG = 900  # 15 minutes for rarely changing data
    
    # Dynamic content - Conditional caching
    DYNAMIC_CACHE_MAX_AGE = 60  # 1 minute for dynamic content
    
    # User-specific content - No caching or private caching
    USER_CACHE_MAX_AGE = 0  # No caching for user-specific data
    
    # Content type mappings
    CONTENT_TYPE_CACHE_CONFIG: Dict[str, Dict[str, any]] = {
        # Static file types
        "text/css": {
            "max_age": STATIC_CACHE_MAX_AGE,
            "strategy": CacheStrategy.PUBLIC,
            "immutable": True
        },
        "application/javascript": {
            "max_age": STATIC_CACHE_MAX_AGE,
            "strategy": CacheStrategy.PUBLIC,
            "immutable": True
        },
        "image/png": {
            "max_age": STATIC_CACHE_MAX_AGE,
            "strategy": CacheStrategy.PUBLIC,
            "immutable": True
        },
        "image/jpeg": {
            "max_age": STATIC_CACHE_MAX_AGE,
            "strategy": CacheStrategy.PUBLIC,
            "immutable": True
        },
        "image/webp": {
            "max_age": STATIC_CACHE_MAX_AGE,
            "strategy": CacheStrategy.PUBLIC,
            "immutable": True
        },
        "image/svg+xml": {
            "max_age": STATIC_CACHE_MAX_AGE,
            "strategy": CacheStrategy.PUBLIC,
            "immutable": True
        },
        "font/woff2": {
            "max_age": STATIC_CACHE_MAX_AGE,
            "strategy": CacheStrategy.PUBLIC,
            "immutable": True
        },
        "font/woff": {
            "max_age": STATIC_CACHE_MAX_AGE,
            "strategy": CacheStrategy.PUBLIC,
            "immutable": True
        },
        
        # API responses
        "application/json": {
            "max_age": API_CACHE_MAX_AGE,
            "strategy": CacheStrategy.PRIVATE,
            "immutable": False
        },
        
        # HTML pages
        "text/html": {
            "max_age": DYNAMIC_CACHE_MAX_AGE,
            "strategy": CacheStrategy.PRIVATE,
            "immutable": False
        },
        
        # Audio files (generated content)
        "audio/mpeg": {
            "max_age": 86400,  # 24 hours
            "strategy": CacheStrategy.PUBLIC,
            "immutable": False
        },
        "audio/mp3": {
            "max_age": 86400,  # 24 hours
            "strategy": CacheStrategy.PUBLIC,
            "immutable": False
        },
        
        # Documents (generated content)
        "application/pdf": {
            "max_age": 3600,  # 1 hour
            "strategy": CacheStrategy.PRIVATE,
            "immutable": False
        }
    }
    
    # Path-based cache rules
    PATH_CACHE_CONFIG: Dict[str, Dict[str, any]] = {
        # Static assets
        "/static/": {
            "max_age": STATIC_CACHE_MAX_AGE,
            "strategy": CacheStrategy.PUBLIC,
            "immutable": True
        },
        "/assets/": {
            "max_age": STATIC_CACHE_MAX_AGE,
            "strategy": CacheStrategy.PUBLIC,
            "immutable": True
        },
        
        # API endpoints
        "/api/v1/content/types": {
            "max_age": API_CACHE_MAX_AGE_LONG,
            "strategy": CacheStrategy.PUBLIC,
            "immutable": False
        },
        "/api/v1/content/templates": {
            "max_age": API_CACHE_MAX_AGE_LONG,
            "strategy": CacheStrategy.PUBLIC,
            "immutable": False
        },
        "/api/v1/prompts": {
            "max_age": API_CACHE_MAX_AGE,
            "strategy": CacheStrategy.PRIVATE,
            "immutable": False
        },
        
        # User-specific endpoints - no caching
        "/api/v1/user/": {
            "max_age": USER_CACHE_MAX_AGE,
            "strategy": CacheStrategy.NO_CACHE,
            "immutable": False
        },
        "/api/v1/auth/": {
            "max_age": USER_CACHE_MAX_AGE,
            "strategy": CacheStrategy.NO_CACHE,
            "immutable": False
        },
        
        # Health checks - no caching
        "/healthz": {
            "max_age": 0,
            "strategy": CacheStrategy.NO_CACHE,
            "immutable": False
        },
        "/api/v1/health": {
            "max_age": 0,
            "strategy": CacheStrategy.NO_CACHE,
            "immutable": False
        }
    }
    
    @classmethod
    def get_cache_config(cls, path: str, content_type: Optional[str] = None) -> Dict[str, any]:
        """Get cache configuration for a given path and content type."""
        # Check path-based rules first (more specific)
        for path_prefix, config in cls.PATH_CACHE_CONFIG.items():
            if path.startswith(path_prefix):
                return config
        
        # Fall back to content-type based rules
        if content_type:
            # Normalize content type (remove charset, etc.)
            base_content_type = content_type.split(";")[0].strip().lower()
            if base_content_type in cls.CONTENT_TYPE_CACHE_CONFIG:
                return cls.CONTENT_TYPE_CACHE_CONFIG[base_content_type]
        
        # Default configuration - short cache for safety
        return {
            "max_age": cls.DYNAMIC_CACHE_MAX_AGE,
            "strategy": CacheStrategy.PRIVATE,
            "immutable": False
        }
    
    @classmethod
    def should_use_etag(cls, path: str) -> bool:
        """Determine if ETag should be used for this path."""
        # Use ETags for dynamic content and API responses
        # Don't use for static assets (they have immutable flag)
        no_etag_prefixes = ["/static/", "/assets/", "/healthz"]
        return not any(path.startswith(prefix) for prefix in no_etag_prefixes)