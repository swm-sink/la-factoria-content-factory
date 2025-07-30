"""Rate limiting configuration."""

from typing import Dict, Optional

from pydantic import BaseModel, Field


class RateLimitConfig(BaseModel):
    """Configuration for rate limiting."""
    
    # Default limits
    default_limit: str = Field(
        "100 per hour",
        description="Default rate limit for endpoints"
    )
    
    # Per-endpoint limits
    endpoint_limits: Dict[str, str] = Field(
        default_factory=lambda: {
            # Content generation - most expensive
            "/api/v1/content/generate": "10 per hour",
            "/api/v1/content/generate-outline": "20 per hour",
            "/api/v1/content/batch": "5 per hour",
            "/api/v1/audio/generate": "5 per hour",
            
            # Authentication - prevent brute force
            "/api/v1/auth/login": "10 per minute",
            "/api/v1/auth/register": "5 per hour",
            "/api/v1/auth/forgot-password": "5 per hour",
            "/api/v1/auth/reset-password": "5 per hour",
            
            # User operations
            "/api/v1/users": "100 per hour",
            "/api/v1/users/me": "200 per hour",
            
            # Content queries - more permissive
            "/api/v1/content": "200 per hour",
            "/api/v1/content/search": "100 per hour",
            
            # Admin operations
            "/api/v1/admin": "50 per hour",
            "/api/v1/admin/users": "30 per hour",
            
            # Health checks - very permissive
            "/api/v1/health": "1000 per minute",
            "/health": "1000 per minute",
            "/api/health": "1000 per minute",
            
            # Metrics - no limit for internal monitoring
            "/metrics": "10000 per minute",
        },
        description="Per-endpoint rate limits"
    )
    
    # API key multipliers (authenticated users get higher limits)
    api_key_multiplier: float = Field(
        2.0,
        description="Multiplier for rate limits when using API key"
    )
    
    # User tier multipliers
    user_tier_multipliers: Dict[str, float] = Field(
        default_factory=lambda: {
            "free": 1.0,
            "basic": 2.0,
            "premium": 5.0,
            "enterprise": 10.0,
        },
        description="Rate limit multipliers by user tier"
    )
    
    # Cost-based rate limiting for expensive operations
    operation_costs: Dict[str, int] = Field(
        default_factory=lambda: {
            # Content types
            "podcast_script": 5,
            "study_guide": 3,
            "detailed_reading": 4,
            "one_pager_summary": 2,
            "flashcards": 2,
            "faqs": 2,
            "reading_questions": 1,
            
            # Audio generation
            "audio_generation": 10,
            
            # Batch operations
            "batch_generation": 20,
        },
        description="Cost units for different operations"
    )
    
    # Burst allowance (temporary spike handling)
    burst_multiplier: float = Field(
        1.5,
        description="Multiplier for temporary burst allowance"
    )
    
    # Rate limit window configurations
    window_configs: Dict[str, int] = Field(
        default_factory=lambda: {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        },
        description="Window duration in seconds"
    )
    
    # Headers configuration
    include_headers: bool = Field(
        True,
        description="Include rate limit headers in responses"
    )
    
    # Exempt paths (no rate limiting)
    exempt_paths: set = Field(
        default_factory=lambda: {
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/robots.txt",
            "/_next",  # Next.js assets
            "/static",  # Static files
            "/internal/health",  # Internal health checks
        },
        description="Paths exempt from rate limiting"
    )
    
    # Exempt IPs (for internal services)
    exempt_ips: set = Field(
        default_factory=set,
        description="IP addresses exempt from rate limiting"
    )
    
    # Redis configuration for distributed rate limiting
    use_redis: bool = Field(
        True,
        description="Use Redis for distributed rate limiting"
    )
    
    redis_prefix: str = Field(
        "rate_limit",
        description="Redis key prefix for rate limiting"
    )
    
    # Graceful degradation
    allow_on_error: bool = Field(
        True,
        description="Allow requests if rate limiter fails"
    )
    
    # Logging configuration
    log_violations: bool = Field(
        True,
        description="Log rate limit violations"
    )
    
    violation_log_level: str = Field(
        "WARNING",
        description="Log level for violations"
    )


def get_rate_limit_config() -> RateLimitConfig:
    """Get rate limit configuration."""
    return RateLimitConfig()


def get_limit_for_endpoint(path: str, config: Optional[RateLimitConfig] = None) -> str:
    """Get rate limit for a specific endpoint."""
    if config is None:
        config = get_rate_limit_config()
    
    # Check exact match
    if path in config.endpoint_limits:
        return config.endpoint_limits[path]
    
    # Check prefix match
    for endpoint, limit in config.endpoint_limits.items():
        if path.startswith(endpoint):
            return limit
    
    # Return default
    return config.default_limit


def calculate_cost(operation_type: str, config: Optional[RateLimitConfig] = None) -> int:
    """Calculate cost units for an operation."""
    if config is None:
        config = get_rate_limit_config()
    
    return config.operation_costs.get(operation_type, 1)


def is_exempt(path: str, ip: Optional[str] = None, config: Optional[RateLimitConfig] = None) -> bool:
    """Check if a request is exempt from rate limiting."""
    if config is None:
        config = get_rate_limit_config()
    
    # Check path exemption
    if path in config.exempt_paths:
        return True
    
    # Check path prefix exemption
    for exempt_path in config.exempt_paths:
        if path.startswith(exempt_path):
            return True
    
    # Check IP exemption
    if ip and ip in config.exempt_ips:
        return True
    
    return False