"""
JWT (JSON Web Token) creation and verification utilities.

This module provides functions to create new access tokens and to verify
existing tokens for user authentication.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from app.core.config.settings import get_settings
from app.models.pydantic.user import (  # Import TokenData from the central location
    TokenData,
)

# from pydantic import BaseModel # BaseModel no longer needed here if TokenData is removed


settings = get_settings()

ALGORITHM = settings.jwt_algorithm  # Use algorithm from settings
ACCESS_TOKEN_EXPIRE_MINUTES = (
    settings.access_token_expire_minutes
)  # Directly from settings


# class TokenData(BaseModel): # Removed duplicate TokenData model
#     \"\"\"
#     Pydantic model for data extracted from a JWT token.
#
#     Attributes:
#         username: The username (or email/user_id) extracted from the token\'s \'sub\' claim.
#     \"\"\"
#
#     username: Optional[str] = None  # Or email, or user_id
#     # Add other claims like scopes if needed


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Creates a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    if not settings.jwt_secret_key:
        raise ValueError("JWT_SECRET_KEY is not configured in settings.")

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception: Exception) -> Optional[TokenData]:
    """Verifies a JWT token and returns its data if valid.

    Args:
        token: The JWT token string.
        credentials_exception: The exception to raise if token is invalid.

    Returns:
        TokenData if valid, otherwise raises credentials_exception.
    """
    try:
        if not settings.jwt_secret_key:
            raise JWTError("JWT_SECRET_KEY is not configured.")

        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get(
            "sub"
        )  # Assuming "sub" (subject) claim holds the username/email
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data
