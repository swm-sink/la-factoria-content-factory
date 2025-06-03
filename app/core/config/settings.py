"""Settings configuration for the AI Content Factory.

This module provides centralized configuration management for the application,
including environment variables, API settings, and other configuration options.

Secrets are loaded with the following precedence:
1. Google Secret Manager (if GCP_PROJECT_ID is set and secret exists)
2. Environment Variables / .env file
"""

import json
import logging
import os
from functools import lru_cache
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import Field, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.security.secrets import SecretManagerClient  # New Import

logger = logging.getLogger(__name__)

# Define names for secrets in Google Secret Manager
GSM_API_KEY_NAME = "AI_CONTENT_FACTORY_API_KEY"
GSM_ELEVENLABS_API_KEY_NAME = "AI_CONTENT_FACTORY_ELEVENLABS_KEY"
GSM_JWT_SECRET_KEY_NAME = "AI_CONTENT_FACTORY_JWT_SECRET_KEY"
GSM_SENTRY_DSN_NAME = "AI_CONTENT_FACTORY_SENTRY_DSN"


class Settings(BaseSettings):
    """Application settings loaded from environment variables or Secret Manager."""

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )

    # Class variable to hold the secrets client, initialized in root_validator
    _secrets_client: ClassVar[Optional[SecretManagerClient]] = None

    # Core Settings
    gcp_project_id: Optional[str] = Field(
        pattern="^[a-z][a-z0-9-]{4,28}[a-z0-9]$",
        description="Google Cloud Project ID. Required if using Secret Manager.",
        env="GCP_PROJECT_ID",  # Explicitly define env var for clarity
    )
    gcp_location: str = Field(
        default="us-central1", env="GCP_LOCATION", description="GCP Location"
    )
    app_port: int = Field(
        default=8080,
        env="APP_PORT",
        description="Port to run the Uvicorn server on, for local development.",
    )

    # Sensitive fields - will attempt to load from Secret Manager first, then Env
    api_key: Optional[str] = Field(
        env="API_KEY",
        min_length=1,
        description="API Key for accessing the application. Loaded from GSM or ENV.",
    )
    elevenlabs_api_key: Optional[str] = Field(
        env="ELEVENLABS_API_KEY",
        min_length=1,
        description="ElevenLabs API Key. Loaded from GSM or ENV.",
    )
    jwt_secret_key: Optional[str] = Field(
        env="JWT_SECRET_KEY",
        min_length=32,  # Good practice for JWT secrets
        description="Secret key for signing JWTs. Loaded from GSM or ENV. Should be a long, random string.",
    )
    sentry_dsn: Optional[str] = Field(
        env="SENTRY_DSN",
        description="Sentry DSN for error reporting. Loaded from GSM or ENV.",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES",
        description="Access token expiration time in minutes.",
    )
    jwt_algorithm: str = Field(
        default="HS256",
        env="JWT_ALGORITHM",
        description="Algorithm for JWT signing (e.g., HS256).",
    )

    elevenlabs_voice_id: str = Field(
        default="21m00Tcm4TlvDq8ikWAM",
        pattern="^[a-zA-Z0-9]{20}$",
        description="ElevenLabs Voice ID. Must be a 20-character alphanumeric string. Default: 21m00Tcm4TlvDq8ikWAM (Rachel voice)",
    )
    project_name: str = Field("AI Content Factory", description="Application name")

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: _get_default_cors_origins(),
        env="CORS_ORIGINS",
        description="CORS allowed origins. Comma-separated list or JSON array.",
    )

    # Storage
    storage_bucket: str = Field(
        "ai-content-factory", description="Cloud storage bucket name"
    )

    # Redis/Cache Configuration
    redis_host: str = Field(
        default="localhost", env="REDIS_HOST", description="Redis host address"
    )
    redis_port: int = Field(
        default=6379, env="REDIS_PORT", description="Redis port number"
    )
    redis_db: int = Field(
        default=0, env="REDIS_DB", description="Redis database number"
    )
    redis_password: Optional[str] = Field(
        env="REDIS_PASSWORD", description="Redis password (if required)"
    )
    redis_ssl: bool = Field(
        default=False, env="REDIS_SSL", description="Enable SSL for Redis connection"
    )
    redis_max_connections: int = Field(
        default=50,
        env="REDIS_MAX_CONNECTIONS",
        description="Maximum number of Redis connections",
    )
    redis_socket_timeout: int = Field(
        default=5,
        env="REDIS_SOCKET_TIMEOUT",
        description="Redis socket timeout in seconds",
    )
    redis_socket_connect_timeout: int = Field(
        default=5,
        env="REDIS_SOCKET_CONNECT_TIMEOUT",
        description="Redis socket connection timeout in seconds",
    )
    redis_retry_on_timeout: bool = Field(
        default=True,
        env="REDIS_RETRY_ON_TIMEOUT",
        description="Retry Redis operations on timeout",
    )
    redis_health_check_interval: int = Field(
        default=30,
        env="REDIS_HEALTH_CHECK_INTERVAL",
        description="Redis health check interval in seconds",
    )

    # Cache settings
    cache_ttl_seconds: int = Field(
        default=3600,
        env="CACHE_TTL_SECONDS",
        description="Default cache TTL in seconds (1 hour)",
    )
    cache_max_size: int = Field(
        default=1000,
        env="CACHE_MAX_SIZE",
        description="Maximum number of cache entries",
    )
    enable_cache: bool = Field(
        default=True, env="ENABLE_CACHE", description="Enable content caching"
    )
    cache_min_quality_retrieval: float = Field(
        default=0.7,
        env="CACHE_MIN_QUALITY_RETRIEVAL",
        description="Minimum quality score for cache retrieval",
    )

    # Async processing
    max_parallel_requests: int = Field(
        8, description="Max parallel requests for async jobs"
    )
    quality_cache_ttl: int = Field(
        604800, description="TTL for quality metrics cache (seconds)"
    )

    # AI Model Settings
    gemini_model_name: str = Field(
        default="models/gemini-2.5-flash-preview-05-20",
        pattern="^models/gemini-(1\\.0-pro|1\\.5-pro|1\\.5-flash|2\\.5-flash-preview-05-20)(-latest|-001|-002)?$",
        description="Gemini Model Name. Must be one of: models/gemini-1.0-pro, models/gemini-1.5-pro, models/gemini-1.5-flash, models/gemini-2.5-flash-preview-05-20, with optional -latest, -001, or -002 suffix.",
        env="GEMINI_MODEL_NAME",
    )

    # AI Model Pricing (USD)
    gemini_1_5_flash_pricing: Dict[str, float] = Field(
        default_factory=lambda: {
            "input_per_1k_tokens": 0.00035,
            "output_per_1k_tokens": 0.00105,
        },
        description="Pricing for Gemini model (per 1000 tokens).",
    )

    elevenlabs_tts_pricing_per_1k_chars: float = Field(
        default=0.30,  # Example: $0.30 per 1000 characters for standard quality
        description="ElevenLabs TTS pricing per 1000 characters (USD).",
    )

    # Content Generation Settings
    max_refinement_iterations: int = Field(
        default=2,
        env="MAX_REFINEMENT_ITERATIONS",
        description="Maximum number of refinement iterations for quality improvement",
    )

    max_tokens_per_content_type: Dict[str, int] = Field(
        default_factory=lambda: {
            "outline": 800,
            "podcast_script": 1500,
            "study_guide": 1200,
            "one_pager_summary": 400,
            "detailed_reading": 2000,
            "faqs": 800,
            "flashcards": 800,
            "reading_guide_questions": 800,
        },
        description="Maximum tokens per content type",
    )
    max_total_tokens: int = Field(
        10000, description="Maximum total tokens for a generation job"
    )
    max_generation_time: int = Field(
        90, description="Maximum generation time in seconds"
    )
    max_retries: int = Field(3, description="Maximum retries for API calls")
    retry_delay: int = Field(2, description="Delay between retries in seconds")

    # Monitoring & Logging
    enable_cost_tracking: bool = Field(
        default=True, env="ENABLE_COST_TRACKING", description="Enable cost tracking"
    )
    enable_performance_tracking: bool = Field(
        True, description="Enable performance tracking"
    )
    enable_quality_metrics: bool = Field(
        default=True,
        env="ENABLE_QUALITY_METRICS",
        description="Enable quality metrics tracking",
    )
    enable_parallel_processing: bool = Field(
        default=True,
        env="ENABLE_PARALLEL_PROCESSING",
        description="Enable parallel content generation",
    )
    log_level: str = Field("INFO", description="Logging level")
    metrics_export_interval: int = Field(
        60, description="Interval for exporting metrics in seconds"
    )
    log_format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s",  # Added correlation_id placeholder
        description="Log message format. Expects correlation_id to be available in LogRecord.",
    )
    prometheus_port: int = Field(
        default=9000,
        env="PROMETHEUS_PORT",
        description="Port for Prometheus metrics server.",
    )

    # Cloud Tasks
    tasks_queue_name: str = Field(
        default="content-generation-queue",
        env="TASKS_QUEUE_NAME",
        description="Name of the Cloud Tasks queue for content generation.",
    )
    tasks_worker_service_url: Optional[str] = Field(
        default=None,  # If None, will attempt to construct from GCP_PROJECT_ID
        env="TASKS_WORKER_SERVICE_URL",
        description="Full base URL of the worker service (e.g., Cloud Run URL). If None, attempts to use default Cloud Run URL format.",
    )
    cloud_tasks_service_account: Optional[str] = Field(
        default=None,
        env="CLOUD_TASKS_SERVICE_ACCOUNT",
        description="Service account email for Cloud Tasks to use when invoking the worker",
    )

    @model_validator(mode="before")
    @classmethod
    def _load_secrets_from_gsm(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Load secrets from Google Secret Manager if configured."""
        gcp_project_id_env = os.getenv("GCP_PROJECT_ID")  # Check env var directly first
        gcp_project_id = values.get("gcp_project_id", gcp_project_id_env)

        if gcp_project_id:
            logger.info(
                f"GCP_PROJECT_ID is set to '{gcp_project_id}'. Attempting to initialize SecretManagerClient."
            )
            if cls._secrets_client is None:
                cls._secrets_client = SecretManagerClient(project_id=gcp_project_id)

            if (
                cls._secrets_client and cls._secrets_client.client
            ):  # Check if client was initialized successfully
                logger.info(
                    "SecretManagerClient initialized. Attempting to load secrets."
                )
                # Try to load api_key if not already provided (e.g., by a .env file directly for the field)
                if not values.get("api_key"):
                    api_key_gsm = cls._secrets_client.get_secret(GSM_API_KEY_NAME)
                    if api_key_gsm:
                        values["api_key"] = api_key_gsm
                        logger.info(
                            f"Setting 'api_key' loaded from Google Secret Manager (secret: {GSM_API_KEY_NAME})"
                        )
                    else:
                        api_key_env = os.getenv("API_KEY")
                        if api_key_env:
                            values["api_key"] = api_key_env
                            logger.info(
                                "Setting 'api_key' loaded from environment variable (API_KEY)"
                            )
                        else:
                            logger.info(
                                "Setting 'api_key' not found in GSM or environment. Will use default if set."
                            )

                # Try to load elevenlabs_api_key if not already provided
                if not values.get("elevenlabs_api_key"):
                    el_api_key_gsm = cls._secrets_client.get_secret(
                        GSM_ELEVENLABS_API_KEY_NAME
                    )
                    if el_api_key_gsm:
                        values["elevenlabs_api_key"] = el_api_key_gsm
                        logger.info(
                            f"Setting 'elevenlabs_api_key' loaded from Google Secret Manager (secret: {GSM_ELEVENLABS_API_KEY_NAME})"
                        )
                    else:
                        el_api_key_env = os.getenv("ELEVENLABS_API_KEY")
                        if el_api_key_env:
                            values["elevenlabs_api_key"] = el_api_key_env
                            logger.info(
                                "Setting 'elevenlabs_api_key' loaded from environment variable (ELEVENLABS_API_KEY)"
                            )
                        else:
                            logger.info(
                                "Setting 'elevenlabs_api_key' not found in GSM or environment. Will use default if set."
                            )

                # Load JWT_SECRET_KEY from GSM
                if not values.get("jwt_secret_key"):
                    jwt_secret_gsm = cls._secrets_client.get_secret(
                        GSM_JWT_SECRET_KEY_NAME
                    )
                    if jwt_secret_gsm:
                        values["jwt_secret_key"] = jwt_secret_gsm
                        logger.info(
                            f"Setting 'jwt_secret_key' loaded from Google Secret Manager (secret: {GSM_JWT_SECRET_KEY_NAME})"
                        )
                    else:
                        jwt_secret_key_env = os.getenv("JWT_SECRET_KEY")
                        if jwt_secret_key_env:
                            values["jwt_secret_key"] = jwt_secret_key_env
                            logger.info(
                                "Setting 'jwt_secret_key' loaded from environment variable (JWT_SECRET_KEY)"
                            )
                        else:
                            logger.info(
                                "Setting 'jwt_secret_key' not found in GSM or environment. Will use default if set."
                            )

                # Load SENTRY_DSN from GSM
                if not values.get("sentry_dsn"):
                    sentry_dsn_gsm = cls._secrets_client.get_secret(GSM_SENTRY_DSN_NAME)
                    if sentry_dsn_gsm:
                        values["sentry_dsn"] = sentry_dsn_gsm
                        logger.info(
                            f"Setting 'sentry_dsn' loaded from Google Secret Manager (secret: {GSM_SENTRY_DSN_NAME})"
                        )
                    else:
                        sentry_dsn_env = os.getenv("SENTRY_DSN")
                        if sentry_dsn_env:
                            values["sentry_dsn"] = sentry_dsn_env
                            logger.info(
                                "Setting 'sentry_dsn' loaded from environment variable (SENTRY_DSN)"
                            )
                        else:
                            logger.info(
                                "Setting 'sentry_dsn' not found in GSM or environment. Will use default if set."
                            )
            else:
                logger.warning(
                    "SecretManagerClient could not be initialized (client is None). Secrets will not be loaded from GSM."
                )
        else:
            logger.info(
                "GCP_PROJECT_ID is not set. Secrets will not be loaded from Google Secret Manager."
            )

        # Load secrets from environment variables if not already loaded
        if not values.get("api_key"):
            api_key_env = os.getenv("API_KEY")
            if api_key_env:
                values["api_key"] = api_key_env
                logger.info(
                    "Setting 'api_key' loaded from environment variable (API_KEY)"
                )

        if not values.get("elevenlabs_api_key"):
            el_api_key_env = os.getenv("ELEVENLABS_API_KEY")
            if el_api_key_env:
                values["elevenlabs_api_key"] = el_api_key_env
                logger.info(
                    "Setting 'elevenlabs_api_key' loaded from environment variable (ELEVENLABS_API_KEY)"
                )

        if not values.get("jwt_secret_key"):
            jwt_secret_key_env = os.getenv("JWT_SECRET_KEY")
            if jwt_secret_key_env:
                values["jwt_secret_key"] = jwt_secret_key_env
                logger.info(
                    "Setting 'jwt_secret_key' loaded from environment variable (JWT_SECRET_KEY)"
                )

        if not values.get("sentry_dsn"):
            sentry_dsn_env = os.getenv("SENTRY_DSN")
            if sentry_dsn_env:
                values["sentry_dsn"] = sentry_dsn_env
                logger.info(
                    "Setting 'sentry_dsn' loaded from environment variable (SENTRY_DSN)"
                )

        return values

    @model_validator(mode="before")
    @classmethod
    def _process_cors_origins(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not values.get("cors_origins"):
            values["cors_origins"] = _get_default_cors_origins()
        return values


def _get_default_cors_origins() -> List[str]:
    """Get default CORS origins based on environment"""
    env_value = os.getenv("CORS_ORIGINS")
    if env_value:
        # Handle both comma-separated and JSON array formats
        if env_value.startswith("["):
            try:
                return json.loads(env_value)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in CORS_ORIGINS: {env_value}")
        else:
            return [origin.strip() for origin in env_value.split(",")]

    # Default origins for development
    return [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",  # Docker compose
    ]


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
        logger.error(
            "Error loading application settings:", exc_info=False
        )  # Keep it concise
        error_messages = []
        for error in e.errors():
            field_name = error.get("loc", ["unknown_field"])[0]
            msg = error.get("msg", "Unknown validation error")
            error_messages.append(f"  Field: {field_name}, Message: {msg}")
        logger.error("\n".join(error_messages))
        # Add a note about checking GSM and ENV vars
        logger.error(
            "Please ensure all required settings (e.g., API_KEY, ELEVENLABS_API_KEY, GCP_PROJECT_ID if using GSM) are correctly set in Google Secret Manager or your environment variables / .env file."
        )
        raise ValueError(
            "Failed to load application settings. Check logs and environment variables/Secret Manager."
        ) from e
