"""Request validation middleware for security and safety."""

import json
import logging
import re
import time
from typing import Callable, Dict, List, Optional, Pattern
from urllib.parse import unquote

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_413_REQUEST_ENTITY_TOO_LARGE

from app.core.config.settings import get_settings
from app.core.errors import create_error_response
from app.services.security_event_logger import log_malicious_request, log_suspicious_activity

logger = logging.getLogger(__name__)


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request validation and security.
    
    Protects against:
    - Oversized requests
    - SQL injection
    - XSS attacks
    - Command injection
    - Path traversal
    - Malicious user agents
    - JSON bombs
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        
        # Configuration
        self.max_request_size = getattr(self.settings, 'max_request_size', 10 * 1024 * 1024)  # 10MB
        self.max_json_depth = 50
        self.max_json_keys = 1000
        
        # Compile patterns for performance
        self._compile_patterns()
        
        # Exempted paths
        self.exempt_paths = {
            '/health',
            '/metrics',
            '/docs',
            '/redoc',
            '/openapi.json',
        }
        
        # Suspicious user agents
        self.malicious_user_agents = {
            'sqlmap', 'nikto', 'w3af', 'zmeu', 'nessus', 'openvas',
            'nmap', 'masscan', 'zap', 'burp', 'scanner'
        }
    
    def _compile_patterns(self):
        """Compile regex patterns for performance."""
        # SQL Injection patterns
        self.sql_patterns = [
            re.compile(r"(?i)(union\s+select|drop\s+table|delete\s+from)", re.IGNORECASE),
            re.compile(r"(?i)('|\"|;).*(-{2}|#)", re.IGNORECASE),
            re.compile(r"(?i)(exec|execute|sp_|xp_)\s*\(", re.IGNORECASE),
            re.compile(r"(?i)(or|and)\s+\d+\s*=\s*\d+", re.IGNORECASE),
        ]
        
        # XSS patterns
        self.xss_patterns = [
            re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
            re.compile(r"javascript:", re.IGNORECASE),
            re.compile(r"on\w+\s*=", re.IGNORECASE),
            re.compile(r"<iframe[^>]*>", re.IGNORECASE),
            re.compile(r"<object[^>]*>", re.IGNORECASE),
            re.compile(r"<embed[^>]*>", re.IGNORECASE),
        ]
        
        # Command injection patterns
        self.command_patterns = [
            re.compile(r"[;&|`]", re.IGNORECASE),
            re.compile(r"\$\([^)]*\)", re.IGNORECASE),
            re.compile(r"`[^`]*`", re.IGNORECASE),
            re.compile(r"(&&|\|\|)", re.IGNORECASE),
        ]
        
        # Path traversal patterns
        self.path_patterns = [
            re.compile(r"\.\./", re.IGNORECASE),
            re.compile(r"\.\.\\", re.IGNORECASE),
            re.compile(r"\.{2,}", re.IGNORECASE),
            re.compile(r"%2e%2e", re.IGNORECASE),
            re.compile(r"(etc/passwd|windows/system32)", re.IGNORECASE),
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate request before processing."""
        start_time = time.time()
        
        try:
            # Skip validation for exempt paths
            if request.url.path in self.exempt_paths:
                return await call_next(request)
            
            # Validate request size
            if not self._validate_request_size(request):
                log_suspicious_activity(
                    source_ip=request.client.host if request.client else "unknown",
                    activity_type="oversized_request",
                    confidence_score=0.7,
                    endpoint=request.url.path,
                    method=request.method,
                    content_length=request.headers.get("content-length")
                )
                return self._create_error_response(
                    "REQUEST_TOO_LARGE",
                    "Request body too large",
                    HTTP_413_REQUEST_ENTITY_TOO_LARGE
                )
            
            # Validate user agent
            if not self._validate_user_agent(request):
                log_malicious_request(
                    source_ip=request.client.host if request.client else "unknown",
                    endpoint=request.url.path,
                    method=request.method,
                    attack_type="malicious_user_agent",
                    user_agent=request.headers.get("user-agent", "")[:100]
                )
                return self._create_error_response(
                    "MALICIOUS_USER_AGENT",
                    "Suspicious user agent detected",
                    HTTP_400_BAD_REQUEST
                )
            
            # For POST/PUT requests, validate body content
            if request.method in ["POST", "PUT", "PATCH"]:
                is_valid, error_message = await self._validate_request_body(request)
                if not is_valid:
                    # Get a sample of the body for logging (limit to avoid sensitive data)
                    try:
                        body = await request.body()
                        body_sample = body.decode('utf-8', errors='ignore')[:200] if body else ""
                    except:
                        body_sample = "Unable to decode body"
                    
                    log_malicious_request(
                        source_ip=request.client.host if request.client else "unknown",
                        endpoint=request.url.path,
                        method=request.method,
                        attack_type="malicious_content",
                        payload_sample=body_sample,
                        error_details=error_message
                    )
                    
                    return self._create_error_response(
                        "MALICIOUS_CONTENT",
                        error_message,
                        HTTP_400_BAD_REQUEST
                    )
            
            # Validate query parameters
            if not self._validate_query_params(request):
                query_string = str(request.query_params)[:200]  # Limit query string sample
                log_malicious_request(
                    source_ip=request.client.host if request.client else "unknown",
                    endpoint=request.url.path,
                    method=request.method,
                    attack_type="malicious_query_params",
                    payload_sample=query_string
                )
                return self._create_error_response(
                    "MALICIOUS_QUERY",
                    "Malicious content detected in query parameters",
                    HTTP_400_BAD_REQUEST
                )
            
            # Process request
            response = await call_next(request)
            
            # Log validation time for monitoring
            validation_time = time.time() - start_time
            if validation_time > 0.1:  # Log if validation takes >100ms
                logger.warning(f"Slow request validation: {validation_time:.3f}s for {request.url.path}")
            
            return response
            
        except Exception as e:
            logger.error(f"Request validation error: {e}", exc_info=True)
            # Don't block request on validation errors in production
            if self.settings.env == "production":
                return await call_next(request)
            else:
                return self._create_error_response(
                    "VALIDATION_ERROR",
                    "Request validation failed",
                    HTTP_400_BAD_REQUEST
                )
    
    def _validate_request_size(self, request: Request) -> bool:
        """Validate request size."""
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_request_size:
                    logger.warning(f"Oversized request blocked: {size} bytes from {request.client.host if request.client else 'unknown'}")
                    return False
            except ValueError:
                # Invalid content-length header
                logger.warning(f"Invalid content-length header: {content_length}")
                return False
        
        return True
    
    def _validate_user_agent(self, request: Request) -> bool:
        """Validate user agent for suspicious patterns."""
        user_agent = request.headers.get("user-agent", "").lower()
        
        if not user_agent:
            # Missing user agent might be suspicious
            return True  # Allow but could be flagged
        
        for malicious_agent in self.malicious_user_agents:
            if malicious_agent in user_agent:
                logger.warning(f"Malicious user agent blocked: {user_agent[:100]} from {request.client.host if request.client else 'unknown'}")
                return False
        
        return True
    
    async def _validate_request_body(self, request: Request) -> tuple[bool, str]:
        """Validate request body content."""
        try:
            # Read body
            body = await request.body()
            if not body:
                return True, ""
            
            # Try to parse as JSON
            try:
                json_data = json.loads(body)
                
                # Validate JSON structure
                if not self._validate_json_structure(json_data):
                    return False, "JSON structure too complex or large"
                
                # Convert to string for pattern matching
                content_str = json.dumps(json_data)
                
            except json.JSONDecodeError:
                # Not JSON, treat as raw text
                content_str = body.decode('utf-8', errors='ignore')
            
            # Check for malicious patterns
            if self._contains_malicious_content(content_str):
                logger.warning(f"Malicious content blocked from {request.client.host if request.client else 'unknown'}: {content_str[:200]}")
                return False, "Malicious content detected in request body"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Error validating request body: {e}")
            return True, ""  # Allow on validation error
    
    def _validate_json_structure(self, data, depth=0) -> bool:
        """Validate JSON structure to prevent DoS attacks."""
        if depth > self.max_json_depth:
            return False
        
        if isinstance(data, dict):
            if len(data) > self.max_json_keys:
                return False
            for value in data.values():
                if not self._validate_json_structure(value, depth + 1):
                    return False
        elif isinstance(data, list):
            if len(data) > self.max_json_keys:
                return False
            for item in data:
                if not self._validate_json_structure(item, depth + 1):
                    return False
        
        return True
    
    def _validate_query_params(self, request: Request) -> bool:
        """Validate query parameters."""
        for key, value in request.query_params.items():
            # Decode URL-encoded content
            decoded_value = unquote(value)
            combined_content = f"{key}={decoded_value}"
            
            if self._contains_malicious_content(combined_content):
                logger.warning(f"Malicious query param blocked from {request.client.host if request.client else 'unknown'}: {combined_content[:100]}")
                return False
        
        return True
    
    def _contains_malicious_content(self, content: str) -> bool:
        """Check if content contains malicious patterns."""
        content_lower = content.lower()
        
        # URL decode for better detection
        decoded_content = unquote(content)
        
        # Check all pattern groups
        for patterns in [self.sql_patterns, self.xss_patterns, self.command_patterns, self.path_patterns]:
            for pattern in patterns:
                if pattern.search(content) or pattern.search(decoded_content):
                    return True
        
        return False
    
    def _create_error_response(self, code: str, message: str, status_code: int) -> Response:
        """Create standardized error response."""
        error_data = create_error_response(
            code=code,
            message=message,
            status_code=status_code,
            details={
                "timestamp": time.time(),
                "validation_failed": True
            }
        )
        
        return Response(
            content=json.dumps(error_data),
            status_code=status_code,
            media_type="application/json"
        )


class ContentSanitizer:
    """Helper class for content sanitization."""
    
    @staticmethod
    def sanitize_html(content: str) -> str:
        """Basic HTML sanitization."""
        # Remove script tags
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove dangerous attributes
        content = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
        
        # Remove javascript: protocols
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
        
        return content
    
    @staticmethod
    def sanitize_sql(content: str) -> str:
        """Basic SQL sanitization."""
        # Escape single quotes
        content = content.replace("'", "''")
        
        # Remove SQL comments
        content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        return content


# Configuration class for request validation
class RequestValidationConfig:
    """Configuration for request validation middleware."""
    
    def __init__(self):
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.max_json_depth = 50
        self.max_json_keys = 1000
        self.enable_content_sanitization = True
        self.log_blocked_requests = True
        self.strict_mode = False  # Block on any suspicious content
        
        # Patterns can be customized per environment
        self.custom_patterns = []
        
        # Allowed file types for uploads
        self.allowed_file_types = {'.txt', '.md', '.json', '.csv', '.pdf'}
        
        # Rate limiting integration
        self.validation_rate_limit = "1000 per hour"  # Requests to validation endpoint