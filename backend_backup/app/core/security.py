from .config import settings
import hmac
import hashlib
from typing import Optional
import os

def verify_api_key(api_key: str) -> bool:
    """
    Verify the provided API key against the configured key.
    Uses constant-time comparison to prevent timing attacks.
    """
    if not api_key or not settings.API_KEY:
        return False
    
    return hmac.compare_digest(api_key.encode(), settings.API_KEY.encode())

def generate_api_key() -> str:
    """
    Generate a new API key.
    This should be used only for initial setup or key rotation.
    """
    return hashlib.sha256(os.urandom(32)).hexdigest() 