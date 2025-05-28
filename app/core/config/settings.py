# This file is now located at backend/app/core/settings.py
# The content has been moved and refactored to use Pydantic BaseSettings.

"""Settings configuration for the AI Content Factory.

This module provides centralized configuration management for the application,
including environment variables, API settings, and other configuration options.

Secrets are loaded with the following precedence:
1. Google Secret Manager (if GCP_PROJECT_ID is set and secret exists)
2. Environment Variables / .env file
"""

import logging
import os
from functools import lru_cache
from typing import Dict, Any, List, Optional, ClassVar

from pydantic import Field, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.security.secrets import SecretManagerClient # New Import

logger = logging.getLogger(__name__)

# Define names for secrets in Google Secret Manager
GSM_API_KEY_NAME = "AI_CONTENT_FACTORY_API_KEY"
GSM_ELEVENLABS_API_KEY_NAME = "AI_CONTENT_FACTORY_ELEVENLABS_KEY"

class Settings(BaseSettings):
    """Application settings loaded from environment variables or Secret Manager."""

    model_config = SettingsConfigDict(env_file='.env', case_sensitive=True, extra='ignore')

    # Class variable to hold the secrets client, initialized in root_validator
    _secrets_client: ClassVar[Optional[SecretManagerClient]] = None
    
    # Core Settings
    gcp_project_id: Optional[str] = Field(
        default=None, # Can be None if not using Secret Manager
        pattern="^[a-z][a-z0-9-]{4,28}[a-z0-9]$", 
        description="Google Cloud Project ID. Required if using Secret Manager.",
        env="GCP_PROJECT_ID" # Explicitly define env var for clarity
    )
    gcp_location: str = Field("us-central1", description="GCP Location")
    
    # Sensitive fields - will attempt to load from Secret Manager first, then Env
    api_key: Optional[str] = Field(
        default=None, # Validation (min_length=1) will be applied after attempting load
        env="API_KEY", 
        min_length=1, 
        description="API Key for accessing the application. Loaded from GSM or ENV."
    )
    elevenlabs_api_key: Optional[str] = Field(
        default=None, # Validation (min_length=1) will be applied after attempting load
        env="ELEVENLABS_API_KEY", 
        min_length=1, 
        description="ElevenLabs API Key. Loaded from GSM or ENV."
    )

    elevenlabs_voice_id: str = Field(
        default="21m00Tcm4TlvDq8ikWAM", 
        pattern="^[a-zA-Z0-9]{20}$", 
        description="ElevenLabs Voice ID. Must be a 20-character alphanumeric string. Default: 21m00Tcm4TlvDq8ikWAM (Rachel voice)"
    )
    project_name: str = Field("AI Content Factory", description="Application name")
    api_v1_prefix: str = Field(
        default="/api/v1", 
        pattern="^/api/v[1-9][0-9]*$", 
        description="API version prefix (e.g., /api/v1)"
    )

    # CORS
    cors_origins: List[str] = Field(default_factory=lambda: [
        "http://localhost:3000",
        "http://localhost:5173"
    ], description="Allowed CORS origins")

    # Database
    database_url: str = Field("sqlite:///./app.db", description="Database connection string")

    # Storage
    storage_bucket: str = Field("ai-content-factory", description="Cloud storage bucket name")

    # Redis/Cache
    redis_url: str = Field("redis://localhost:6379/0", description="Redis connection string")
    cache_ttl_seconds: int = Field(86400, description="Cache TTL in seconds")
    max_parallel_requests: int = Field(8, description="Max parallel requests for async jobs")
    quality_cache_ttl: int = Field(604800, description="TTL for quality metrics cache (seconds)")

    # AI Model Settings
    gemini_model_name: str = Field(
        default="gemini-1.5-flash-latest", 
        pattern="^gemini-(1\\.0-pro|1\\.5-pro|1\\.5-flash)(-latest|-001|-002)?$",
        description="Gemini Model Name. Must be one of: gemini-1.0-pro, gemini-1.5-pro, gemini-1.5-flash, with optional -latest, -001, or -002 suffix. Default: gemini-1.5-flash-latest"
    )
    
    # Content Generation Settings
    max_tokens_per_content_type: Dict[str, int] = Field(
        default_factory=lambda: {
            "outline": 800,
            "podcast_script": 1500,
            "study_guide": 1200,
            "one_pager_summary": 400,
            "detailed_reading": 2000,
            "faqs": 800,
            "flashcards": 800,
            "reading_guide_questions": 800
        },
        description="Maximum tokens per content type"
    )
    max_total_tokens: int = Field(10000, description="Maximum total tokens for a generation job")
    max_generation_time: int = Field(90, description="Maximum generation time in seconds")
    max_retries: int = Field(3, description="Maximum retries for API calls")
    retry_delay: int = Field(2, description="Delay between retries in seconds")

    # Monitoring & Logging
    enable_cost_tracking: bool = Field(True, description="Enable cost tracking")
    enable_performance_tracking: bool = Field(True, description="Enable performance tracking")
    log_level: str = Field("INFO", description="Logging level")
    metrics_export_interval: int = Field(60, description="Interval for exporting metrics in seconds")
    log_format: str = Field("%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log message format")

    @model_validator(mode='before')
    @classmethod
    def _load_secrets_from_gsm(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Load secrets from Google Secret Manager if configured."""
        gcp_project_id_env = os.getenv("GCP_PROJECT_ID") # Check env var directly first
        gcp_project_id = values.get("gcp_project_id", gcp_project_id_env)

        if gcp_project_id:
            logger.info(f"GCP_PROJECT_ID is set to '{gcp_project_id}'. Attempting to initialize SecretManagerClient.")
            if cls._secrets_client is None:
                cls._secrets_client = SecretManagerClient(project_id=gcp_project_id)
            
            if cls._secrets_client and cls._secrets_client.client: # Check if client was initialized successfully
                logger.info("SecretManagerClient initialized. Attempting to load secrets.")
                # Try to load api_key if not already provided (e.g., by a .env file directly for the field)
                if not values.get("api_key"):
                    api_key_gsm = cls._secrets_client.get_secret(GSM_API_KEY_NAME)
                    if api_key_gsm:
                        values["api_key"] = api_key_gsm
                        logger.info(f"Loaded '{GSM_API_KEY_NAME}' from Google Secret Manager.")
                    else:
                        logger.info(f"'{GSM_API_KEY_NAME}' not found in GSM or client error. Will rely on env/default for api_key.")
                
                # Try to load elevenlabs_api_key if not already provided
                if not values.get("elevenlabs_api_key"):
                    el_api_key_gsm = cls._secrets_client.get_secret(GSM_ELEVENLABS_API_KEY_NAME)
                    if el_api_key_gsm:
                        values["elevenlabs_api_key"] = el_api_key_gsm
                        logger.info(f"Loaded '{GSM_ELEVENLABS_API_KEY_NAME}' from Google Secret Manager.")
                    else:
                        logger.info(f"'{GSM_ELEVENLABS_API_KEY_NAME}' not found in GSM or client error. Will rely on env/default for elevenlabs_api_key.")
            else:
                logger.warning("SecretManagerClient could not be initialized (client is None). Secrets will not be loaded from GSM.")
        else:
            logger.info("GCP_PROJECT_ID is not set. Secrets will not be loaded from Google Secret Manager.")
        
        return values

@lru_cache()
def get_settings() -> Settings:
    """Get application settings.

    Settings are loaded with precedence: Google Secret Manager > Environment Variables > .env file.
    
    Returns:
        Settings: Application settings instance.
        
    Raises:
        ValueError: If required settings (after attempting all load mechanisms) are missing or invalid.
    """
    try:
        return Settings()
    except ValidationError as e:
        logger.error("Error loading application settings:", exc_info=False) # Keep it concise
        error_messages = []
        for error in e.errors():
            field_name = error.get('loc', ['unknown_field'])[0]
            msg = error.get('msg', 'Unknown validation error')
            error_messages.append(f"  Field: {field_name}, Message: {msg}")
        logger.error("\n".join(error_messages))
        # Add a note about checking GSM and ENV vars
        logger.error("Please ensure all required settings (e.g., API_KEY, ELEVENLABS_API_KEY, GCP_PROJECT_ID if using GSM) are correctly set in Google Secret Manager or your environment variables / .env file.")
        raise ValueError("Failed to load application settings. Check logs and environment variables/Secret Manager.") from e 