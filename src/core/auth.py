"""
Authentication and authorization for La Factoria API
Simple API key-based authentication following FastAPI security patterns
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib
import hmac
import logging
from typing import Optional

from .config import settings

logger = logging.getLogger(__name__)

# Security scheme for API key authentication
security = HTTPBearer()

def hash_api_key(api_key: str) -> str:
    """Hash API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def verify_api_key_hash(api_key: str, stored_hash: str) -> bool:
    """Verify API key against stored hash"""
    return hmac.compare_digest(hash_api_key(api_key), stored_hash)

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify API key authentication

    In production, this validates against configured API keys.
    In development, accepts any non-empty key for testing.
    """
    api_key = credentials.credentials

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Development mode - accept any non-empty key
    if settings.is_development and not settings.API_KEY:
        logger.info(f"Development mode: accepting API key {api_key[:8]}...")
        return api_key

    # Production mode - validate against configured key
    if settings.API_KEY:
        if not hmac.compare_digest(api_key, settings.API_KEY):
            logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info(f"Valid API key authenticated: {api_key[:8]}...")
        return api_key

    # No API key configured - warn and allow access
    logger.warning("No API key configured - allowing unrestricted access")
    return api_key

async def verify_admin_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Verify admin API key for administrative operations

    Currently uses the same key as regular API access.
    In a full implementation, this would check against admin-specific keys.
    """
    # For now, use the same verification as regular API key
    api_key = await verify_api_key(credentials)

    # In the future, add admin-specific validation here
    # if not is_admin_key(api_key):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin access required"
    #     )

    return api_key

class APIKeyManager:
    """Manage API keys for the La Factoria platform"""

    def __init__(self):
        self.master_key = settings.API_KEY

    def generate_api_key(self, user_id: str) -> str:
        """Generate a new API key for a user (placeholder implementation)"""
        import secrets
        return f"lf_{user_id[:8]}_{secrets.token_urlsafe(32)}"

    def validate_key_format(self, api_key: str) -> bool:
        """Validate API key format"""
        if not api_key:
            return False

        # Development keys can be anything
        if settings.is_development:
            return len(api_key) > 0

        # Production keys should follow format: lf_<prefix>_<token>
        if api_key.startswith("lf_"):
            parts = api_key.split("_")
            return len(parts) >= 3 and len(parts[2]) >= 16

        # Master key validation
        return api_key == self.master_key

    def get_key_info(self, api_key: str) -> dict:
        """Get information about an API key"""
        if not self.validate_key_format(api_key):
            return {"valid": False, "type": "invalid"}

        if api_key == self.master_key:
            return {
                "valid": True,
                "type": "master",
                "permissions": ["read", "write", "admin"]
            }

        if api_key.startswith("lf_"):
            return {
                "valid": True,
                "type": "user",
                "permissions": ["read", "write"],
                "user_prefix": api_key.split("_")[1] if len(api_key.split("_")) > 1 else "unknown"
            }

        return {
            "valid": True,
            "type": "development",
            "permissions": ["read", "write"]
        }

# Global API key manager instance
api_key_manager = APIKeyManager()

# Optional dependencies for when authentication is not required
async def optional_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """Optional API key verification for endpoints that don't require authentication"""
    if not credentials:
        return None

    try:
        return await verify_api_key(credentials)
    except HTTPException:
        return None

# Rate limiting helper (placeholder implementation)
class RateLimiter:
    """Simple rate limiter for API key usage"""

    def __init__(self):
        self.request_counts = {}  # In production, use Redis or database

    def check_rate_limit(self, api_key: str, limit: int = None) -> bool:
        """Check if API key is within rate limits"""
        if settings.is_development:
            return True  # No rate limiting in development

        # Placeholder implementation
        # In production, implement proper rate limiting with Redis
        limit = limit or settings.RATE_LIMIT_REQUESTS_PER_MINUTE

        # Always allow for now - implement proper rate limiting later
        return True

    def increment_usage(self, api_key: str):
        """Increment usage count for API key"""
        # Placeholder - implement with Redis in production
        pass

# Global rate limiter instance
rate_limiter = RateLimiter()
