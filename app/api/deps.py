"""
FastAPI dependencies for authentication and user management.

This module provides reusable dependencies for API routes, primarily
for handling OAuth2 authentication and retrieving the current authenticated user.
"""

import logging  # Added for logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import ValidationError

from app.core.security.tokens import verify_token, TokenData
from app.models.pydantic.user import User
from app.services.job.firestore_client import (
    get_job_from_firestore,
)  # Re-using for user fetching
from app.core.config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)  # Added logger instance
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/login"
)  # Corrected tokenUrl

USER_COLLECTION = "users"  # As defined in auth.py


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Dependency to get the current user from a token.
    Decodes the token and returns TokenData.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = verify_token(token, credentials_exception)
        if token_data is None:  # Should not happen if verify_token raises on error
            raise credentials_exception
        return token_data
    except (
        JWTError
    ):  # verify_token can raise JWTError directly or via credentials_exception
        raise credentials_exception
    except ValidationError:  # If TokenData model validation fails (should be rare)
        raise credentials_exception


async def get_current_active_user(
    current_user_token_data: TokenData = Depends(get_current_user),
) -> User:
    """
    Dependency to get the current active user from token data, then fetch full user details.
    """
    if current_user_token_data.username is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token data: username missing",
        )

    user_data_dict = await get_job_from_firestore(
        current_user_token_data.username, collection_name=USER_COLLECTION
    )
    if user_data_dict is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Assuming user_data_dict contains fields for User model (e.g., id, email)
    # and potentially is_active if that's part of your User model in Firestore
    # For now, directly creating User Pydantic model.
    # Ensure User model in pydantic/user.py matches Firestore structure or adapt this.
    try:
        user = User(**user_data_dict)
    except ValidationError as e:
        logger.error(
            f"Error validating user data from Firestore for user {current_user_token_data.username}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing user data",
        )

    # if not user.is_active: # Add is_active field to your User model and Firestore if needed
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user
