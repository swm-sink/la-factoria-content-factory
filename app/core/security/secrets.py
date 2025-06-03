"""Handles integration with Google Secret Manager."""

import logging
from functools import lru_cache
from typing import List, Optional

from google.api_core.exceptions import NotFound, PermissionDenied
from google.cloud import secretmanager
from google.cloud.secretmanager_v1.types import AccessSecretVersionResponse

logger = logging.getLogger(__name__)


class SecretManagerClient:
    """Client for interacting with Google Cloud Secret Manager."""

    def __init__(self, project_id: str):
        """Initialize the SecretManagerClient.

        Args:
            project_id: The Google Cloud Project ID.
        """
        self.project_id = project_id
        try:
            self.client = secretmanager.SecretManagerServiceClient()
            logger.info("SecretManagerServiceClient initialized successfully.")
        except Exception as e:
            logger.error(
                f"Failed to initialize SecretManagerServiceClient: {e}", exc_info=True
            )
            self.client = None

    @lru_cache(maxsize=32)
    def get_secret(self, secret_id: str, version_id: str = "latest") -> Optional[str]:
        """Retrieves a secret value from Google Secret Manager.

        Args:
            secret_id: The ID of the secret.
            version_id: The version of the secret (default: "latest").

        Returns:
            The secret value as a string, or None if an error occurs.
        """
        if not self.client:
            logger.error(
                "SecretManagerClient not available (failed to initialize or no project_id)."
            )
            return None
        if (
            not self.project_id
        ):  # Should not happen if client is initialized and __init__ requires project_id
            logger.error("Project_id is missing for get_secret.")
            return None

        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
        try:
            response: AccessSecretVersionResponse = self.client.access_secret_version(
                request={"name": name}
            )
            payload: str = response.payload.data.decode("UTF-8")
            logger.info(
                f"Successfully accessed secret: projects/{self.project_id}/secrets/{secret_id}"
            )
            return payload
        except NotFound:
            logger.warning(f"Secret not found: {name}")
        except PermissionDenied:
            logger.error(
                f"Permission denied for secret: {name}. Ensure service account has 'Secret Manager Secret Accessor' role."
            )
        except Exception as e:
            logger.error(f"Failed to access secret {name}: {e}", exc_info=True)
        return None

    def list_secrets(self) -> List[str]:
        """Lists all secret IDs in the configured project.

        Returns:
            A list of secret IDs, or an empty list if an error occurs.
        """
        if not self.client:
            logger.error(
                "SecretManagerClient not available (failed to initialize or no project_id) for list_secrets."
            )
            return []
        if not self.project_id:  # Should not happen if client is initialized
            logger.error("Project_id is missing for list_secrets.")
            return []

        parent = f"projects/{self.project_id}"
        secret_ids: List[str] = []
        try:
            for secret in self.client.list_secrets(request={"parent": parent}):
                # secret.name is projects/{project_id}/secrets/{secret_id}
                secret_ids.append(secret.name.split("/")[-1])
            logger.info(
                f"Successfully listed {len(secret_ids)} secrets in project {self.project_id}."
            )
            return secret_ids
        except PermissionDenied:
            logger.error(
                f"Permission denied for listing secrets in project: {self.project_id}."
            )
        except Exception as e:
            logger.error(
                f"Failed to list secrets in project {self.project_id}: {e}",
                exc_info=True,
            )
        return []
