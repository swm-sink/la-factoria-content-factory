"""
Configuration settings for La Factoria platform
Using Pydantic Settings for environment variable management
"""

from typing import List, Optional, Dict, Any
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application settings
    APP_NAME: str = "La Factoria"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    # API settings
    API_V1_PREFIX: str = "/api/v1"
    API_KEY: Optional[str] = Field(default=None, alias="LA_FACTORIA_API_KEY")
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production")

    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    # Database settings (PostgreSQL on Railway)
    DATABASE_URL: Optional[str] = Field(default=None)
    DB_POOL_SIZE: int = Field(default=10)
    DB_MAX_OVERFLOW: int = Field(default=20)

    # Redis settings (for caching and sessions)
    REDIS_URL: Optional[str] = Field(default=None)
    CACHE_TTL: int = Field(default=3600)  # 1 hour default

    # AI Provider settings
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None)
    ELEVENLABS_API_KEY: Optional[str] = Field(default=None)
    GOOGLE_CLOUD_PROJECT: Optional[str] = Field(default=None)
    GOOGLE_CLOUD_REGION: str = Field(default="us-central1")

    # Langfuse settings (for prompt management and observability)
    LANGFUSE_SECRET_KEY: Optional[str] = Field(default=None)
    LANGFUSE_PUBLIC_KEY: Optional[str] = Field(default=None)
    LANGFUSE_HOST: str = Field(default="https://cloud.langfuse.com")

    # Content generation settings
    DEFAULT_MAX_TOKENS: int = Field(default=3000)
    CONTENT_GENERATION_TIMEOUT: int = Field(default=120)  # seconds
    MAX_CONCURRENT_GENERATIONS: int = Field(default=10)

    # Quality assessment thresholds (from la-factoria-railway-deployment.md)
    QUALITY_THRESHOLD_OVERALL: float = Field(default=0.70)
    QUALITY_THRESHOLD_EDUCATIONAL: float = Field(default=0.75)
    QUALITY_THRESHOLD_FACTUAL: float = Field(default=0.85)

    # Rate limiting settings
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60)
    RATE_LIMIT_GENERATIONS_PER_HOUR: int = Field(default=100)

    # File storage settings
    UPLOAD_MAX_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    STATIC_FILES_DIR: str = Field(default="static")

    # Logging settings
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Monitoring and health check settings
    HEALTH_CHECK_TIMEOUT: int = Field(default=30)
    METRICS_ENABLED: bool = Field(default=True)

    @property
    def database_url(self) -> str:
        """Get database URL with fallback to SQLite for development"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.ENVIRONMENT == "development":
            return "sqlite:///./la_factoria_dev.db"
        raise ValueError("DATABASE_URL must be set for non-development environments")

    @property
    def has_langfuse_config(self) -> bool:
        """Check if Langfuse is properly configured"""
        return bool(self.LANGFUSE_SECRET_KEY and self.LANGFUSE_PUBLIC_KEY)

    @property
    def has_openai_config(self) -> bool:
        """Check if OpenAI is configured"""
        return bool(self.OPENAI_API_KEY)

    @property
    def has_anthropic_config(self) -> bool:
        """Check if Anthropic is configured"""
        return bool(self.ANTHROPIC_API_KEY)

    @property
    def has_elevenlabs_config(self) -> bool:
        """Check if ElevenLabs is configured"""
        return bool(self.ELEVENLABS_API_KEY)

    @property
    def available_ai_providers(self) -> List[str]:
        """Get list of available AI providers based on configuration"""
        providers = []
        if self.has_openai_config:
            providers.append("openai")
        if self.has_anthropic_config:
            providers.append("anthropic")
        if self.GOOGLE_CLOUD_PROJECT:
            providers.append("vertex_ai")
        return providers

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"

    def get_ai_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for specific AI provider"""
        configs = {
            "openai": {
                "api_key": self.OPENAI_API_KEY,
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": self.DEFAULT_MAX_TOKENS
            },
            "anthropic": {
                "api_key": self.ANTHROPIC_API_KEY,
                "model": "claude-3-sonnet-20240229",
                "temperature": 0.7,
                "max_tokens": self.DEFAULT_MAX_TOKENS
            },
            "vertex_ai": {
                "project": self.GOOGLE_CLOUD_PROJECT,
                "location": self.GOOGLE_CLOUD_REGION,
                "model": "text-bison",
                "temperature": 0.7,
                "max_tokens": self.DEFAULT_MAX_TOKENS
            },
            "elevenlabs": {
                "api_key": self.ELEVENLABS_API_KEY,
                "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Default voice
                "model_id": "eleven_monolingual_v1"
            }
        }
        return configs.get(provider, {})

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

# Global settings instance
settings = Settings()

# Validate critical settings on import
def validate_settings():
    """Validate critical settings and warn about missing configuration"""
    import warnings

    if settings.is_production:
        # Production validation
        if not settings.DATABASE_URL:
            raise ValueError("DATABASE_URL is required in production")

        if settings.SECRET_KEY == "dev-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be changed in production")

        if not settings.API_KEY:
            warnings.warn("LA_FACTORIA_API_KEY not set - API will be unprotected")

    # AI provider validation
    if not settings.available_ai_providers:
        warnings.warn("No AI providers configured - content generation will fail")

    # Optional service warnings
    if not settings.has_langfuse_config:
        warnings.warn("Langfuse not configured - prompt management and observability disabled")

    if not settings.REDIS_URL:
        warnings.warn("Redis not configured - caching disabled")

# Run validation on import
validate_settings()
