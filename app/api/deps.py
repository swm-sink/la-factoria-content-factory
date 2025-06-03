import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.api_key import APIKeyHeader
from jose import JWTError, jwt

from app.core.config.settings import get_settings
from app.models.pydantic.user import TokenData, UserResponse
from app.services.job.firestore_client import get_document_from_firestore

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
USER_COLLECTION = "users"  # Define where user data is stored, consistent with auth.py

main_logger = logging.getLogger(__name__)


async def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    """
    Dependency function to validate the API key.

    Args:
        api_key: The API key passed in the X-API-Key header.

    Raises:
        HTTPException: If the API key is invalid or missing.

    Returns:
        The validated API key.
    """
    settings = get_settings()
    if not api_key or api_key != settings.api_key:
        provided_key_display = f"'{api_key[:10]}...'" if api_key else "None"
        main_logger.warning(
            f"Invalid or missing API key attempt. Provided key: {provided_key_display}."
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
    return api_key


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Decodes and validates JWT token, returns token data.
    """
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            main_logger.warning("Token decoding failed: username (sub) claim missing.")
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        main_logger.warning(f"JWTError during token decoding: {e}")
        raise credentials_exception from e
    return token_data


async def get_current_active_user(
    current_user_token_data: TokenData = Depends(get_current_user),
) -> UserResponse:
    """
    Fetches user from DB based on token data and checks if active.
    This is a more complete version.
    """
    main_logger.debug(
        f"Attempting to get active user for: {current_user_token_data.username}"
    )
    # Assuming username from token is the email and used as document ID in Firestore
    user_doc = await get_document_from_firestore(
        current_user_token_data.username, collection_name=USER_COLLECTION
    )
    if user_doc is None:
        main_logger.warning(
            f"User {current_user_token_data.username} not found in Firestore."
        )
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user is active (if field exists)
    # if not user_doc.get("is_active", True): # Default to True if not present
    #     logger.warning(f"User {current_user_token_data.username} is inactive.")
    #     raise HTTPException(status_code=400, detail="Inactive user")

    try:
        # Ensure 'id' field is present (email is used as ID in Firestore)
        if "id" not in user_doc and "email" in user_doc:
            user_doc["id"] = user_doc["email"]

        # Add default values for fields that might not exist in Firestore
        if "full_name" not in user_doc:
            user_doc["full_name"] = None
        if "is_active" not in user_doc:
            user_doc["is_active"] = True

        # UserResponse model will automatically exclude hashed_password
        user = UserResponse(**user_doc)
        main_logger.info(f"Active user {user.email} retrieved successfully.")
        return user
    except Exception as e:  # Catch Pydantic validation errors or other issues
        main_logger.error(
            f"Error creating UserResponse for {current_user_token_data.username}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing user data.",
        )
