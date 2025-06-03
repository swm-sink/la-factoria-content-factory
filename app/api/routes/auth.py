"""
API routes for user authentication (registration, login).
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  # For login form
from pydantic import BaseModel

from app.api.deps import get_current_active_user  # Import the dependency
from app.core.security.hashing import PasswordHashing
from app.core.security.tokens import create_access_token
from app.models.pydantic.user import User as UserResponse  # User is the response model
from app.models.pydantic.user import UserCreate
from app.services.job.firestore_client import (
    create_or_update_document_in_firestore,
    get_document_from_firestore,
)

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Authentication"],
)

USER_COLLECTION = "users"


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_new_user(user_in: UserCreate) -> Any:
    """Processes user registration.

    Creates a new user in Firestore with a hashed password.
    """
    logger.info(f"Registration attempt for email: {user_in.email}")

    # Check if user already exists
    existing_user_data = await get_document_from_firestore(
        user_in.email, collection_name=USER_COLLECTION
    )  # Using email as ID for simplicity
    if existing_user_data:
        logger.warning(
            f"Registration failed: Email {user_in.email} already registered."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

    hashed_password = PasswordHashing.get_password_hash(user_in.password)

    # For UserInDB model, we'd ideally have a proper UserInDB Pydantic model
    # For now, constructing the dict directly. ID will be email for this example.
    new_user_data_db = {
        "id": user_in.email,  # Using email as user ID for simplicity
        "email": user_in.email,
        "hashed_password": hashed_password,
        # "is_active": True, # Default if part of your model
    }

    try:
        await create_or_update_document_in_firestore(
            document_id=user_in.email,  # Using email as document ID
            data=new_user_data_db,
            collection_name=USER_COLLECTION,
        )
        logger.info(f"User {user_in.email} registered successfully.")

        # Prepare response: exclude hashed_password
        # This assumes UserResponse can be created from this dict.
        # Ideally, fetch the created user or use a UserInDB model then convert to UserResponse.
        response_user_data = new_user_data_db.copy()
        del response_user_data[
            "hashed_password"
        ]  # Ensure hashed_password is not in response

        return UserResponse(**response_user_data)  # Create UserResponse model from dict

    except Exception as e:
        logger.error(
            f"Error during user registration for {user_in.email}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during user registration.",
        )


class Token(BaseModel):
    """Response model for the token."""

    access_token: str
    token_type: str


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Processes user login and returns an access token."""
    logger.info(f"Login attempt for username: {form_data.username}")
    # form_data.username is typically email in our case
    user_data = await get_document_from_firestore(
        form_data.username, collection_name=USER_COLLECTION
    )

    if not user_data:
        logger.warning(f"Login failed: User {form_data.username} not found.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not PasswordHashing.verify_password(
        form_data.password, user_data.get("hashed_password", "")
    ):
        logger.warning(f"Login failed: Invalid password for user {form_data.username}.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": form_data.username
        }  # "sub" (subject) is standard claim for user identifier
    )
    logger.info(f"User {form_data.username} logged in successfully.")
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_active_user)):
    """
    Get current authenticated user.
    """
    return current_user
