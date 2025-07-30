"""Security configuration for the application."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class HSTSConfig(BaseModel):
    """HSTS (HTTP Strict Transport Security) configuration."""
    
    enabled: bool = Field(
        True,
        description="Enable HSTS header"
    )
    
    max_age: int = Field(
        31536000,  # 1 year
        description="HSTS max-age in seconds"
    )
    
    include_subdomains: bool = Field(
        True,
        description="Include subdomains in HSTS policy"
    )
    
    preload: bool = Field(
        False,
        description="Include preload directive (only for production)"
    )


class CSPConfig(BaseModel):
    """Content Security Policy configuration."""
    
    enabled: bool = Field(
        True,
        description="Enable CSP header"
    )
    
    report_only: bool = Field(
        False,
        description="Use CSP in report-only mode"
    )
    
    report_uri: Optional[str] = Field(
        None,
        description="URI to send CSP violation reports"
    )
    
    directives: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "default-src": ["'self'"],
            "frame-ancestors": ["'none'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
            "object-src": ["'none'"],
        },
        description="CSP directives"
    )
    
    nonce_enabled: bool = Field(
        True,
        description="Enable nonce for inline scripts"
    )


class SecurityHeadersConfig(BaseModel):
    """Security headers configuration."""
    
    # Basic security headers
    x_content_type_options: str = Field(
        "nosniff",
        description="X-Content-Type-Options header value"
    )
    
    x_frame_options: str = Field(
        "DENY",
        description="X-Frame-Options header value"
    )
    
    x_xss_protection: str = Field(
        "1; mode=block",
        description="X-XSS-Protection header value"
    )
    
    referrer_policy: str = Field(
        "strict-origin-when-cross-origin",
        description="Referrer-Policy header value"
    )
    
    # HSTS configuration
    hsts: HSTSConfig = Field(
        default_factory=HSTSConfig,
        description="HSTS configuration"
    )
    
    # CSP configuration
    csp: CSPConfig = Field(
        default_factory=CSPConfig,
        description="CSP configuration"
    )
    
    # Permissions Policy
    permissions_policy: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "geolocation": [],
            "camera": [],
            "microphone": [],
            "payment": [],
            "usb": [],
            "magnetometer": [],
            "accelerometer": [],
            "gyroscope": [],
            "ambient-light-sensor": [],
            "autoplay": ["self"],
            "encrypted-media": ["self"],
            "fullscreen": ["self"],
            "picture-in-picture": ["self"],
        },
        description="Permissions Policy directives"
    )
    
    # Cache control for sensitive endpoints
    api_cache_control: str = Field(
        "no-store, no-cache, must-revalidate",
        description="Cache-Control for API endpoints"
    )
    
    auth_cache_control: str = Field(
        "no-store",
        description="Cache-Control for auth endpoints"
    )
    
    static_cache_control: str = Field(
        "public, max-age=31536000, immutable",
        description="Cache-Control for static assets"
    )
    
    # Server header handling
    remove_server_header: bool = Field(
        True,
        description="Remove server header in production"
    )
    
    server_header_value: str = Field(
        "LaFactoria",
        description="Custom server header value"
    )


class SecurityConfig(BaseModel):
    """Overall security configuration."""
    
    # Security headers
    headers: SecurityHeadersConfig = Field(
        default_factory=SecurityHeadersConfig,
        description="Security headers configuration"
    )
    
    # Environment-specific settings
    enforce_https: bool = Field(
        True,
        description="Enforce HTTPS in production"
    )
    
    # Security monitoring
    log_security_events: bool = Field(
        True,
        description="Log security-related events"
    )
    
    security_event_level: str = Field(
        "WARNING",
        description="Log level for security events"
    )
    
    # Additional security features
    enable_request_validation: bool = Field(
        True,
        description="Enable request validation middleware"
    )
    
    max_request_size: int = Field(
        10 * 1024 * 1024,  # 10MB
        description="Maximum request size in bytes"
    )
    
    # API security
    require_api_key: bool = Field(
        True,
        description="Require API key for API endpoints"
    )
    
    api_key_header: str = Field(
        "X-API-Key",
        description="Header name for API key"
    )
    
    # Session security
    session_cookie_secure: bool = Field(
        True,
        description="Set secure flag on session cookies"
    )
    
    session_cookie_httponly: bool = Field(
        True,
        description="Set httponly flag on session cookies"
    )
    
    session_cookie_samesite: str = Field(
        "strict",
        description="SameSite attribute for session cookies"
    )


def get_security_config(env: str = "production") -> SecurityConfig:
    """Get security configuration for the given environment."""
    config = SecurityConfig()
    
    if env == "production":
        # Strict settings for production
        config.headers.hsts.preload = True
        config.headers.csp.report_only = False
        config.headers.remove_server_header = True
        config.enforce_https = True
        
        # Production CSP directives
        config.headers.csp.directives = {
            "default-src": ["'self'"],
            "script-src": ["'self'", "https://cdn.jsdelivr.net"],
            "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
            "img-src": ["'self'", "data:", "https:"],
            "font-src": ["'self'", "https://fonts.gstatic.com"],
            "connect-src": ["'self'", "https://api.lafactoria.ai"],
            "frame-ancestors": ["'none'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
            "object-src": ["'none'"],
            "upgrade-insecure-requests": [],
        }
    
    elif env == "development":
        # More permissive settings for development
        config.headers.hsts.enabled = False
        config.headers.csp.report_only = True
        config.headers.remove_server_header = False
        config.enforce_https = False
        config.require_api_key = False
        
        # Development CSP directives
        config.headers.csp.directives = {
            "default-src": ["'self'"],
            "script-src": ["'self'", "'unsafe-eval'", "http://localhost:*"],
            "style-src": ["'self'", "'unsafe-inline'"],
            "img-src": ["'self'", "data:", "http:", "https:"],
            "font-src": ["'self'", "data:"],
            "connect-src": ["'self'", "http://localhost:*", "ws://localhost:*"],
            "frame-ancestors": ["'self'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
            "object-src": ["'none'"],
        }
    
    return config


def format_csp_header(directives: Dict[str, List[str]]) -> str:
    """Format CSP directives into header string."""
    parts = []
    for directive, values in directives.items():
        if values:
            parts.append(f"{directive} {' '.join(values)}")
        else:
            parts.append(directive)
    return "; ".join(parts)


def format_permissions_policy(permissions: Dict[str, List[str]]) -> str:
    """Format Permissions Policy into header string."""
    parts = []
    for feature, allowlist in permissions.items():
        if allowlist:
            allowed = " ".join(f'"{x}"' if x != "self" else "'self'" for x in allowlist)
            parts.append(f"{feature}=({allowed})")
        else:
            parts.append(f"{feature}=()")
    return ", ".join(parts)