"""
Password hashing utilities using passlib.

This module provides helper functions for hashing and verifying passwords
using bcrypt as the hashing algorithm.
"""

from passlib.context import CryptContext

# Use bcrypt for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHashing:
    """Provides static methods for password hashing and verification."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain password against a hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hashes a plain password."""
        return pwd_context.hash(password)
