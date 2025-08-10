"""
Comprehensive Input Validation Module for La Factoria
Implements security-focused validation to prevent common attacks
"""

import re
import html
from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field, field_validator, ConfigDict
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

# Security constants
MAX_STRING_LENGTH = 5000
MAX_TOPIC_LENGTH = 500
MAX_REQUIREMENTS_LENGTH = 2000
MAX_LIST_LENGTH = 50
MAX_JSON_DEPTH = 10

# Dangerous patterns to block
DANGEROUS_PATTERNS = [
    r'<script[^>]*>.*?</script>',  # XSS attempts
    r'javascript:',  # JavaScript protocol
    r'on\w+\s*=',  # Event handlers
    r'\x00',  # Null bytes
    r'\.\./',  # Path traversal
    r'[;&|`$]',  # Shell command injection
    r'--\s*$',  # SQL comment
    r';\s*(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE)\s',  # SQL commands
    r"'\s*OR\s*'?\d*'\s*=\s*'?\d*",  # SQL injection pattern
    r'<iframe',  # iframe injection
    r'<object',  # object injection
    r'<embed',  # embed injection
]

# Compile patterns for efficiency
COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE | re.DOTALL) 
                     for pattern in DANGEROUS_PATTERNS]

class SecurityValidator:
    """Security-focused validation utilities"""
    
    @staticmethod
    def sanitize_string(value: str, field_name: str = "input", 
                       max_length: int = MAX_STRING_LENGTH) -> str:
        """
        Sanitize string input to prevent security vulnerabilities
        
        Args:
            value: The string to sanitize
            field_name: Name of the field for error messages
            max_length: Maximum allowed string length
            
        Returns:
            Sanitized string
            
        Raises:
            HTTPException: If input is invalid or dangerous
        """
        if not isinstance(value, str):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field_name} must be a string"
            )
        
        # Check length
        if len(value) > max_length:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field_name} exceeds maximum length of {max_length}"
            )
        
        # Check for dangerous patterns
        for pattern in COMPILED_PATTERNS:
            if pattern.search(value):
                logger.warning(f"Blocked dangerous pattern in {field_name}: {pattern.pattern}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid characters or patterns in {field_name}"
                )
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # HTML escape special characters
        value = html.escape(value, quote=False)
        
        # Normalize whitespace
        value = ' '.join(value.split())
        
        # Strip leading/trailing whitespace
        value = value.strip()
        
        # Ensure not empty after sanitization
        if not value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field_name} cannot be empty"
            )
        
        return value
    
    @staticmethod
    def validate_enum_value(value: str, allowed_values: List[str], 
                          field_name: str = "field") -> str:
        """
        Validate enum-like values against a whitelist
        
        Args:
            value: The value to validate
            allowed_values: List of allowed values
            field_name: Name of the field for error messages
            
        Returns:
            Validated value
            
        Raises:
            HTTPException: If value is not in allowed list
        """
        if value not in allowed_values:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid {field_name}. Must be one of: {', '.join(allowed_values)}"
            )
        return value
    
    @staticmethod
    def validate_list_length(items: List[Any], max_length: int = MAX_LIST_LENGTH,
                           field_name: str = "list") -> List[Any]:
        """
        Validate list length to prevent resource exhaustion
        
        Args:
            items: The list to validate
            max_length: Maximum allowed list length
            field_name: Name of the field for error messages
            
        Returns:
            Validated list
            
        Raises:
            HTTPException: If list is too long
        """
        if len(items) > max_length:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field_name} exceeds maximum length of {max_length}"
            )
        return items
    
    @staticmethod
    def validate_json_depth(obj: Any, max_depth: int = MAX_JSON_DEPTH, 
                          current_depth: int = 0) -> Any:
        """
        Validate JSON depth to prevent stack overflow attacks
        
        Args:
            obj: The object to validate
            max_depth: Maximum allowed nesting depth
            current_depth: Current recursion depth
            
        Returns:
            Validated object
            
        Raises:
            HTTPException: If nesting is too deep
        """
        if current_depth > max_depth:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"JSON nesting too deep (max {max_depth} levels)"
            )
        
        if isinstance(obj, dict):
            for value in obj.values():
                SecurityValidator.validate_json_depth(value, max_depth, current_depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                SecurityValidator.validate_json_depth(item, max_depth, current_depth + 1)
        
        return obj

class SecureContentRequest(BaseModel):
    """Secure version of ContentRequest with comprehensive validation"""
    
    topic: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="The educational topic or subject to generate content for"
    )
    learning_level: Optional[str] = Field(
        default="general",
        description="Target learning level for content generation"
    )
    additional_requirements: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Additional requirements or constraints"
    )
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    @field_validator('topic')
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate and sanitize topic"""
        return SecurityValidator.sanitize_string(v, "topic", MAX_TOPIC_LENGTH)
    
    @field_validator('learning_level')
    @classmethod
    def validate_learning_level(cls, v: Optional[str]) -> Optional[str]:
        """Validate learning level against allowed values"""
        if v is None:
            return "general"
        
        allowed_levels = [
            "elementary", "middle_school", "high_school", 
            "college", "adult_learning", "general"
        ]
        return SecurityValidator.validate_enum_value(v, allowed_levels, "learning_level")
    
    @field_validator('additional_requirements')
    @classmethod
    def validate_requirements(cls, v: Optional[str]) -> Optional[str]:
        """Validate and sanitize additional requirements"""
        if v is None:
            return None
        return SecurityValidator.sanitize_string(v, "additional_requirements", 
                                                MAX_REQUIREMENTS_LENGTH)

def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format and characteristics
    
    Args:
        api_key: The API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        return False
    
    # Check length (typical API keys are 32-128 characters)
    if len(api_key) < 20 or len(api_key) > 256:
        return False
    
    # Check for dangerous patterns
    for pattern in COMPILED_PATTERNS:
        if pattern.search(api_key):
            logger.warning(f"Blocked dangerous pattern in API key")
            return False
    
    # API keys should be alphanumeric with some special chars
    if not re.match(r'^[A-Za-z0-9_\-\.]+$', api_key):
        return False
    
    return True

def validate_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize query parameters
    
    Args:
        params: Dictionary of query parameters
        
    Returns:
        Sanitized parameters
        
    Raises:
        HTTPException: If parameters are invalid
    """
    sanitized = {}
    
    for key, value in params.items():
        # Validate parameter names
        if not re.match(r'^[a-zA-Z0-9_]+$', key):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid parameter name: {key}"
            )
        
        # Validate common parameter types
        if key in ['limit', 'offset', 'page', 'page_size']:
            try:
                int_value = int(value)
                if int_value < 0:
                    raise ValueError("Must be non-negative")
                if key == 'limit' and int_value > 1000:
                    int_value = 1000  # Cap at reasonable limit
                sanitized[key] = int_value
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"{key} must be a non-negative integer"
                )
        
        elif key in ['sort', 'order', 'filter']:
            # Validate against whitelist
            if isinstance(value, str):
                # Remove dangerous characters
                sanitized[key] = re.sub(r'[^a-zA-Z0-9_,\-\. ]', '', value)
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"{key} must be a string"
                )
        
        else:
            # Default string sanitization
            if isinstance(value, str):
                sanitized[key] = SecurityValidator.sanitize_string(
                    value, key, MAX_STRING_LENGTH
                )
            else:
                sanitized[key] = value
    
    return sanitized

# Middleware for request size limiting
async def validate_request_size(request_body: bytes, max_size: int = 1024 * 1024):
    """
    Validate request body size
    
    Args:
        request_body: The raw request body
        max_size: Maximum allowed size in bytes (default 1MB)
        
    Raises:
        HTTPException: If request is too large
    """
    if len(request_body) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_PAYLOAD_TOO_LARGE,
            detail=f"Request body too large (max {max_size} bytes)"
        )