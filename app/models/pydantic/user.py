"""
Pydantic models for user management.

This module defines the data structures for user creation, updates,
and representations for API responses and database storage.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid  # Keep for potential future use, though not for ID if email is ID


class UserBase(BaseModel):
    """Base model for user properties."""

    email: EmailStr = Field(..., description="User's email address.")
    # is_active: bool = Field(default=True, description="Whether the user is active.")
    # is_superuser: bool = Field(default=False, description="Whether the user has superuser privileges.")
    # full_name: Optional[str] = Field(None, description="User's full name.")


class UserCreate(UserBase):
    """Model for creating a new user."""

    password: str = Field(
        ..., min_length=8, description="User's password (min 8 characters)."
    )


class UserUpdate(UserBase):
    """Model for updating an existing user's properties."""

    email: Optional[EmailStr] = Field(
        default=None, description="User's new email address (optional)."
    )
    password: Optional[str] = Field(
        default=None,
        min_length=8,
        description="User's new password (optional, min 8 characters).",
    )
    # is_active: Optional[bool] = None
    # is_superuser: Optional[bool] = None
    # full_name: Optional[str] = None


class UserInDBBase(UserBase):
    """Base model for user data as stored in the database."""

    # In the current auth.py, email is used as the document ID in Firestore.
    # So, 'id' here should reflect that if this model is used for data from DB.
    # If a separate UUID is desired, auth.py needs to be updated.
    # For now, aligning with auth.py's use of email as ID.
    id: EmailStr = Field(
        ..., description="Unique user identifier (typically the email address)."
    )
    hashed_password: str = Field(..., description="Hashed password for the user.")

    class Config:
        from_attributes = True  # For Pydantic V2 compatibility


class User(UserInDBBase):
    """Pydantic model for returning user data to the client (excludes hashed_password)."""

    # This model inherits hashed_password but it should be excluded in API responses.
    # FastAPI response_model handles this if UserResponse in auth.py is User.
    # Or, define specific fields here if UserInDBBase is too broad.
    # For now, assuming UserResponse in auth.py (aliased to this User model)
    # will be constructed carefully to exclude hashed_password.
    # A more explicit approach:
    # email: EmailStr
    # id: EmailStr
    # is_active: Optional[bool] = None
    # is_superuser: Optional[bool] = None
    # full_name: Optional[str] = None
    model_config = {"fields": {"hashed_password": {"exclude": True}}}


class UserInDB(UserInDBBase):
    """Pydantic model representing a user document as stored in the database,
    including the hashed password.
    """

    pass
