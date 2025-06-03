"""
Feature Flag Manager - Dynamic configuration management
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

import yaml
from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer


class FeatureFlagHandler(FileSystemEventHandler):
    """Handle feature flag file changes"""

    def __init__(self, manager: "FeatureFlagManager"):
        self.manager = manager

    def on_modified(self, event: FileModifiedEvent):
        if not event.is_directory and event.src_path.endswith("features.yaml"):
            self.manager.reload_flags()


class FeatureFlagManager:
    """
    Manage feature flags with hot reload capability.
    Single source of truth for runtime configuration.
    """

    def __init__(self, config_path: str = "app/config/features.yaml"):
        """Initialize feature flag manager"""
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.flags: Dict[str, Any] = {}
        self.last_loaded: Optional[datetime] = None
        self._observer: Optional[Observer] = None

        # Load initial configuration
        self.reload_flags()

        # Start watching for changes in production
        if os.getenv("ENVIRONMENT") != "test":
            self._start_watching()

    def reload_flags(self) -> None:
        """Reload feature flags from file"""
        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
                self.flags = config.get("features", {})
                self.last_loaded = datetime.utcnow()
                self.logger.info(
                    f"Feature flags reloaded at {self.last_loaded.isoformat()}"
                )
        except Exception as e:
            self.logger.error(f"Failed to load feature flags: {e}")
            # Keep existing flags on error

    def _start_watching(self) -> None:
        """Start watching configuration file for changes"""
        try:
            event_handler = FeatureFlagHandler(self)
            self._observer = Observer()
            self._observer.schedule(
                event_handler, path=os.path.dirname(self.config_path), recursive=False
            )
            self._observer.start()
            self.logger.info("Started watching feature flags for changes")
        except Exception as e:
            self.logger.warning(f"Could not start file watcher: {e}")

    def get(self, flag_path: str, default: Any = None) -> Any:
        """
        Get a feature flag value using dot notation.

        Example:
            get("content_generation.use_unified_service", False)
        """
        keys = flag_path.split(".")
        value = self.flags

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def is_enabled(self, flag_path: str) -> bool:
        """Check if a boolean feature flag is enabled"""
        return bool(self.get(flag_path, False))

    def should_use_unified_service(self, job_id: str) -> bool:
        """
        Determine if a request should use the unified service.
        Uses percentage-based rollout or explicit flag.
        """
        # Check explicit flag first
        if self.get("content_generation.use_unified_service", False):
            return True

        # Check percentage-based rollout
        rollout_percentage = self.get("rollout.unified_service_percentage", 0)
        if rollout_percentage >= 100:
            return True
        elif rollout_percentage <= 0:
            return False

        # Use job_id for deterministic assignment
        hash_value = hash(job_id)
        return (hash_value % 100) < rollout_percentage

    def get_circuit_breaker_config(self, service: str) -> Dict[str, Any]:
        """Get circuit breaker configuration for a service"""
        return self.get(
            f"circuit_breakers.{service}",
            {"enabled": False, "failure_threshold": 5, "timeout_seconds": 60},
        )

    def get_all_flags(self) -> Dict[str, Any]:
        """Get all feature flags (for debugging)"""
        return self.flags.copy()

    def stop_watching(self) -> None:
        """Stop watching for file changes"""
        if self._observer and self._observer.is_alive():
            self._observer.stop()
            self._observer.join()
            self.logger.info("Stopped watching feature flags")


# Global instance
_feature_flag_manager: Optional[FeatureFlagManager] = None


def get_feature_flags() -> FeatureFlagManager:
    """Get or create feature flag manager instance"""
    global _feature_flag_manager
    if _feature_flag_manager is None:
        _feature_flag_manager = FeatureFlagManager()
    return _feature_flag_manager
