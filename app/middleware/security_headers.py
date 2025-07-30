"""Security headers middleware for comprehensive protection."""

import secrets
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config.settings import get_settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    
    Implements OWASP security headers recommendations.
    """
    
    def __init__(self, app, strict: bool = None):
        super().__init__(app)
        self.settings = get_settings()
        self.strict = strict if strict is not None else (self.settings.env == "production")
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        # Generate nonce for CSP if needed
        nonce = secrets.token_urlsafe(16)
        
        # Store nonce in request state for use in templates
        request.state.csp_nonce = nonce
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response, request, nonce)
        
        return response
    
    def _add_security_headers(self, response: Response, request: Request, nonce: str) -> None:
        """Add all security headers to response."""
        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-XSS-Protection (legacy but still recommended)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "camera=(), "
            "microphone=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "accelerometer=(), "
            "gyroscope=()"
        )
        
        # Strict-Transport-Security (HSTS)
        self._add_hsts_header(response)
        
        # Content-Security-Policy
        self._add_csp_header(response, request, nonce)
        
        # Cache-Control for sensitive endpoints
        self._add_cache_control(response, request)
        
        # Remove or obscure server header
        self._handle_server_header(response)
    
    def _add_hsts_header(self, response: Response) -> None:
        """Add HSTS header with appropriate settings."""
        # Only add HSTS in production or if explicitly strict
        if self.strict or self.settings.env == "production":
            max_age = 31536000  # 1 year
            hsts_header = f"max-age={max_age}; includeSubDomains"
            
            # Add preload directive in production
            if self.settings.env == "production":
                hsts_header += "; preload"
            
            response.headers["Strict-Transport-Security"] = hsts_header
    
    def _add_csp_header(self, response: Response, request: Request, nonce: str) -> None:
        """Add Content Security Policy header."""
        # Build CSP based on environment
        csp_directives = self._build_csp_directives(nonce)
        
        # Use report-only in development for easier debugging
        if self.settings.env == "development" and not self.strict:
            header_name = "Content-Security-Policy-Report-Only"
        else:
            header_name = "Content-Security-Policy"
        
        response.headers[header_name] = "; ".join(csp_directives)
    
    def _build_csp_directives(self, nonce: str) -> list:
        """Build CSP directives based on environment."""
        # Base directives
        directives = [
            "default-src 'self'",
            "frame-ancestors 'none'",  # Prevent clickjacking
            "base-uri 'self'",
            "form-action 'self'",
        ]
        
        if self.settings.env == "production" or self.strict:
            # Strict CSP for production
            directives.extend([
                f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",  # Allow inline styles with caution
                "img-src 'self' data: https:",
                "font-src 'self' https://fonts.gstatic.com",
                "connect-src 'self' https://api.lafactoria.ai",
                "media-src 'self'",
                "object-src 'none'",
                "upgrade-insecure-requests",
            ])
        else:
            # More permissive CSP for development
            directives.extend([
                f"script-src 'self' 'nonce-{nonce}' 'unsafe-eval' http://localhost:*",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: http: https:",
                "font-src 'self' data:",
                "connect-src 'self' http://localhost:* ws://localhost:*",
                "media-src 'self'",
                "object-src 'none'",
            ])
        
        # Add report URI if configured
        if hasattr(self.settings, 'csp_report_uri') and self.settings.csp_report_uri:
            directives.append(f"report-uri {self.settings.csp_report_uri}")
        
        return directives
    
    def _add_cache_control(self, response: Response, request: Request) -> None:
        """Add cache control headers for sensitive endpoints."""
        path = request.url.path
        
        # API endpoints should not be cached
        if path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        # Auth endpoints especially should not be cached
        elif path.startswith("/auth/") or path.startswith("/api/v1/auth/"):
            response.headers["Cache-Control"] = "no-store"
            response.headers["Pragma"] = "no-cache"
        
        # Static assets can be cached
        elif path.startswith("/static/") or path.startswith("/_next/"):
            # Cache static assets for 1 year with revalidation
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    
    def _handle_server_header(self, response: Response) -> None:
        """Remove or obscure server header to prevent information disclosure."""
        # Remove server header entirely in production
        if self.settings.env == "production":
            response.headers.pop("Server", None)
        else:
            # Replace with generic value in other environments
            response.headers["Server"] = "LaFactoria"


class SecurityConfig:
    """Configuration for security headers."""
    
    def __init__(self):
        self.settings = get_settings()
        
    def get_csp_directives(self) -> dict:
        """Get CSP directives by environment."""
        base_directives = {
            "default-src": ["'self'"],
            "frame-ancestors": ["'none'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
            "object-src": ["'none'"],
        }
        
        if self.settings.env == "production":
            return {
                **base_directives,
                "script-src": ["'self'", "https://cdn.jsdelivr.net"],
                "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
                "img-src": ["'self'", "data:", "https:"],
                "font-src": ["'self'", "https://fonts.gstatic.com"],
                "connect-src": ["'self'", "https://api.lafactoria.ai"],
                "upgrade-insecure-requests": [],
            }
        else:
            return {
                **base_directives,
                "script-src": ["'self'", "'unsafe-eval'", "http://localhost:*"],
                "style-src": ["'self'", "'unsafe-inline'"],
                "img-src": ["'self'", "data:", "http:", "https:"],
                "connect-src": ["'self'", "http://localhost:*", "ws://localhost:*"],
            }
    
    def get_permissions_policy(self) -> dict:
        """Get Permissions Policy configuration."""
        return {
            "geolocation": [],
            "camera": [],
            "microphone": [],
            "payment": [],
            "usb": [],
            "magnetometer": [],
            "accelerometer": [],
            "gyroscope": [],
            "ambient-light-sensor": [],
            "autoplay": ["'self'"],
            "encrypted-media": ["'self'"],
            "fullscreen": ["'self'"],
            "picture-in-picture": ["'self'"],
        }