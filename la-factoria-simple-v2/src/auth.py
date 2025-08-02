"""
Simple Authentication System for La Factoria
Task: API-003 - Implement simple authentication
"""

import json
import secrets
import string
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


class ApiKeyStore:
    """Simple file-based API key storage."""

    def __init__(self, storage_file: Optional[str] = None):
        """Initialize API key store with file storage."""
        if storage_file is None:
            # Use project root for storage
            project_root = Path(__file__).parent.parent
            storage_file = project_root / "api_keys.json"

        self.storage_file = Path(storage_file)
        self._load_keys()

    def _load_keys(self) -> None:
        """Load API keys from storage file."""
        try:
            if self.storage_file.exists():
                with open(self.storage_file, "r") as f:
                    self.keys = json.load(f)
            else:
                self.keys = {}
        except (json.JSONDecodeError, IOError):
            self.keys = {}

    def _save_keys(self) -> None:
        """Save API keys to storage file."""
        try:
            with open(self.storage_file, "w") as f:
                json.dump(self.keys, f, indent=2)
        except IOError:
            # In production, log this error
            pass

    def generate_key(self, name: str) -> str:
        """Generate a new API key for a user/service."""
        # Generate secure random key (32 chars)
        alphabet = string.ascii_letters + string.digits
        key_id = "".join(secrets.choice(alphabet) for _ in range(32))

        # La Factoria prefix
        full_key = f"lf_{key_id}"

        # Store key info
        now = datetime.now(timezone.utc).isoformat()
        self.keys[full_key] = {"key_id": key_id, "name": name, "created_at": now, "last_used": None, "active": True}

        self._save_keys()
        return full_key

    def is_valid(self, api_key: str) -> bool:
        """Check if API key is valid and active."""
        return api_key in self.keys and self.keys[api_key].get("active", False)

    def get_key_info(self, api_key: str) -> Optional[Dict]:
        """Get information about an API key."""
        return self.keys.get(api_key)

    def record_usage(self, api_key: str) -> None:
        """Record that an API key was used."""
        if api_key in self.keys:
            self.keys[api_key]["last_used"] = datetime.now(timezone.utc).isoformat()
            self._save_keys()

    def delete_key(self, api_key: str) -> bool:
        """Delete/revoke an API key."""
        if api_key in self.keys:
            self.keys[api_key]["active"] = False
            self._save_keys()
            return True
        return False

    def list_keys(self) -> List[Dict]:
        """List all keys (for management purposes)."""
        return [
            {
                "key_id": info["key_id"],
                "name": info["name"],
                "created_at": info["created_at"],
                "last_used": info["last_used"],
                "active": info.get("active", False),
            }
            for key, info in self.keys.items()
            if info.get("active", False)
        ]


# Global key store instance
_key_store = None


def get_key_store() -> ApiKeyStore:
    """Get global API key store instance."""
    global _key_store
    if _key_store is None:
        _key_store = ApiKeyStore()
    return _key_store
