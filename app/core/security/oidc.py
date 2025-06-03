"""OIDC token validation for Cloud Tasks worker endpoints."""

import logging
import os
from functools import lru_cache
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

logger = logging.getLogger(__name__)


class OIDCTokenValidator:
    """Validates OIDC tokens from Cloud Tasks."""

    def __init__(self):
        """Initialize the OIDC token validator."""
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.expected_audience = None
        self.google_certs_url = "https://www.googleapis.com/oauth2/v3/certs"
        self._certs_cache = None

    @lru_cache(maxsize=1)
    async def _get_google_public_keys(self) -> Dict[str, Any]:
        """Fetch Google's public keys for token verification.

        Returns:
            Dictionary of public keys
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.google_certs_url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch Google public keys: {e}")
            raise

    async def validate_token(
        self, token: str, expected_audience: str
    ) -> Dict[str, Any]:
        """Validate an OIDC token from Cloud Tasks.

        Args:
            token: The JWT token to validate
            expected_audience: The expected audience claim

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid
        """
        try:
            # First decode without verification to get the header
            unverified_header = jwt.get_unverified_header(token)

            # Get Google's public keys
            keys = await self._get_google_public_keys()

            # Find the key that matches the token's key ID
            key_id = unverified_header.get("kid")
            if not key_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing key ID",
                )

            # Decode and verify the token
            payload = jwt.decode(
                token,
                keys,
                algorithms=["RS256"],
                audience=expected_audience,
                issuer="https://accounts.google.com",
                options={"verify_exp": True},
            )

            # Additional validation
            if not payload.get("email"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing email claim",
                )

            logger.info(f"Successfully validated OIDC token for {payload.get('email')}")
            return payload

        except JWTError as e:
            logger.error(f"JWT validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token validation failed",
            )


# Global validator instance
_oidc_validator: Optional[OIDCTokenValidator] = None


def get_oidc_validator() -> OIDCTokenValidator:
    """Get or create the global OIDC validator instance.

    Returns:
        OIDCTokenValidator instance
    """
    global _oidc_validator
    if _oidc_validator is None:
        _oidc_validator = OIDCTokenValidator()
    return _oidc_validator


async def verify_cloud_tasks_token(request: Request) -> Dict[str, Any]:
    """FastAPI dependency to verify Cloud Tasks OIDC token.

    Args:
        request: FastAPI request object

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or missing
    """
    # Get the authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        # In development, allow requests without token
        if os.getenv("ENVIRONMENT", "development") == "development":
            logger.warning("No OIDC token provided in development mode")
            return {"email": "dev@localhost", "sub": "dev"}

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    # Extract the token
    token = auth_header.split(" ")[1]

    # Get the expected audience (the URL of this endpoint)
    expected_audience = str(request.url).split("?")[0]  # Remove query params

    # Validate the token
    validator = get_oidc_validator()
    return await validator.validate_token(token, expected_audience)


# HTTP Bearer for Swagger UI
security = HTTPBearer(auto_error=False)


async def verify_cloud_tasks_token_swagger(
    credentials: Optional[HTTPAuthorizationCredentials] = security,
) -> Dict[str, Any]:
    """Alternative dependency that works with Swagger UI.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        Decoded token payload
    """
    if not credentials:
        # In development, allow requests without token
        if os.getenv("ENVIRONMENT", "development") == "development":
            logger.warning("No OIDC token provided in development mode")
            return {"email": "dev@localhost", "sub": "dev"}

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials"
        )

    # For now, in development, just return a mock response
    # In production, this would validate the actual token
    if os.getenv("ENVIRONMENT", "development") == "development":
        return {"email": "dev@localhost", "sub": "dev"}

    # In production, validate the actual token
    # This is a simplified version - you'd need the request URL
    validator = get_oidc_validator()
    return await validator.validate_token(
        credentials.credentials,
        "https://your-service-url.run.app",  # This needs to be dynamic
    )
