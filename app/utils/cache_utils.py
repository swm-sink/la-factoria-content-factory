"""
Cache utility functions for HTTP response caching.
"""

import hashlib
import time
from typing import Optional, Union, Dict, Any
from datetime import datetime, timezone


class CacheUtils:
    """Utilities for cache header management."""
    
    @staticmethod
    def generate_etag(content: Union[str, bytes], weak: bool = True) -> str:
        """Generate an ETag for content."""
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        # Generate hash
        hash_digest = hashlib.sha256(content).hexdigest()[:16]
        
        # Return weak or strong ETag
        if weak:
            return f'W/"{hash_digest}"'
        return f'"{hash_digest}"'
    
    @staticmethod
    def generate_etag_from_dict(data: Dict[str, Any], weak: bool = True) -> str:
        """Generate an ETag from a dictionary (for JSON responses)."""
        # Create a stable string representation
        import json
        content = json.dumps(data, sort_keys=True)
        return CacheUtils.generate_etag(content, weak)
    
    @staticmethod
    def parse_if_none_match(header_value: Optional[str]) -> set:
        """Parse If-None-Match header and return set of ETags."""
        if not header_value:
            return set()
        
        # Handle wildcard
        if header_value.strip() == "*":
            return {"*"}
        
        # Parse comma-separated ETags
        etags = set()
        for etag in header_value.split(","):
            etag = etag.strip()
            if etag:
                etags.add(etag)
        
        return etags
    
    @staticmethod
    def parse_if_modified_since(header_value: Optional[str]) -> Optional[datetime]:
        """Parse If-Modified-Since header."""
        if not header_value:
            return None
        
        try:
            # Parse HTTP date format
            return datetime.strptime(header_value, "%a, %d %b %Y %H:%M:%S GMT").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    
    @staticmethod
    def format_http_date(dt: Optional[datetime] = None) -> str:
        """Format datetime as HTTP date string."""
        if dt is None:
            dt = datetime.now(timezone.utc)
        elif dt.tzinfo is None:
            # Assume UTC if no timezone
            dt = dt.replace(tzinfo=timezone.utc)
        
        # Convert to UTC and format
        utc_dt = dt.astimezone(timezone.utc)
        return utc_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    @staticmethod
    def build_cache_control_header(
        max_age: int = 0,
        s_maxage: Optional[int] = None,
        public: bool = False,
        private: bool = False,
        no_cache: bool = False,
        no_store: bool = False,
        must_revalidate: bool = False,
        proxy_revalidate: bool = False,
        immutable: bool = False,
        stale_while_revalidate: Optional[int] = None,
        stale_if_error: Optional[int] = None
    ) -> str:
        """Build a Cache-Control header value."""
        directives = []
        
        # Caching directives
        if no_store:
            directives.append("no-store")
        elif no_cache:
            directives.append("no-cache")
        else:
            if public:
                directives.append("public")
            elif private:
                directives.append("private")
            
            if max_age > 0:
                directives.append(f"max-age={max_age}")
            
            if s_maxage is not None:
                directives.append(f"s-maxage={s_maxage}")
        
        # Revalidation directives
        if must_revalidate:
            directives.append("must-revalidate")
        
        if proxy_revalidate:
            directives.append("proxy-revalidate")
        
        # Immutable directive
        if immutable:
            directives.append("immutable")
        
        # Stale directives
        if stale_while_revalidate is not None:
            directives.append(f"stale-while-revalidate={stale_while_revalidate}")
        
        if stale_if_error is not None:
            directives.append(f"stale-if-error={stale_if_error}")
        
        return ", ".join(directives)
    
    @staticmethod
    def get_cache_key(path: str, query_params: Optional[Dict[str, str]] = None, user_id: Optional[str] = None) -> str:
        """Generate a cache key for a request."""
        parts = [path]
        
        # Add sorted query parameters
        if query_params:
            sorted_params = sorted(query_params.items())
            params_str = "&".join(f"{k}={v}" for k, v in sorted_params)
            parts.append(params_str)
        
        # Add user ID for user-specific caching
        if user_id:
            parts.append(f"user:{user_id}")
        
        # Generate hash of the key
        key = "|".join(parts)
        return hashlib.md5(key.encode()).hexdigest()
    
    @staticmethod
    def should_return_304(
        etag: Optional[str],
        if_none_match: Optional[str],
        last_modified: Optional[datetime],
        if_modified_since: Optional[str]
    ) -> bool:
        """Determine if a 304 Not Modified response should be returned."""
        # Check ETag first (stronger validator)
        if etag and if_none_match:
            etags = CacheUtils.parse_if_none_match(if_none_match)
            if "*" in etags or etag in etags:
                return True
        
        # Check Last-Modified
        if last_modified and if_modified_since:
            if_modified_dt = CacheUtils.parse_if_modified_since(if_modified_since)
            if if_modified_dt and last_modified <= if_modified_dt:
                return True
        
        return False
    
    @staticmethod
    def add_cache_headers(
        headers: Dict[str, str],
        cache_control: Optional[str] = None,
        etag: Optional[str] = None,
        last_modified: Optional[datetime] = None,
        expires: Optional[datetime] = None,
        vary: Optional[str] = None
    ) -> Dict[str, str]:
        """Add cache-related headers to a response."""
        if cache_control:
            headers["Cache-Control"] = cache_control
        
        if etag:
            headers["ETag"] = etag
        
        if last_modified:
            headers["Last-Modified"] = CacheUtils.format_http_date(last_modified)
        
        if expires:
            headers["Expires"] = CacheUtils.format_http_date(expires)
        
        if vary:
            existing_vary = headers.get("Vary", "")
            if existing_vary:
                headers["Vary"] = f"{existing_vary}, {vary}"
            else:
                headers["Vary"] = vary
        
        return headers