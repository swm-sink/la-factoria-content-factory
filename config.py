import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from functools import lru_cache
import logging

@dataclass
class ContentGenerationConfig:
    """Configuration for content generation parameters.
    
    Attributes:
        max_tokens_per_content_type: Maximum tokens allowed per content type
        max_total_tokens: Maximum total tokens allowed across all content types
        max_generation_time: Maximum time allowed for generation in seconds
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
    """
    max_tokens_per_content_type: Dict[str, int] = field(default_factory=lambda: {
        "outline": 1000,
        "podcast_script": 2000,
        "study_guide": 1500,
        "one_pager_summary": 500,
        "detailed_reading": 3000,
        "faqs": 1000,
        "flashcards": 1000,
        "reading_guide_questions": 1000
    })
    max_total_tokens: int = 10000
    max_generation_time: int = 90
    max_retries: int = 3
    retry_delay: int = 2

    def validate(self) -> None:
        """Validate content generation settings."""
        if self.max_total_tokens <= 0:
            raise ValueError("max_total_tokens must be positive")
        if self.max_generation_time <= 0:
            raise ValueError("max_generation_time must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        if self.retry_delay < 0:
            raise ValueError("retry_delay cannot be negative")
        
        for content_type, tokens in self.max_tokens_per_content_type.items():
            if tokens <= 0:
                raise ValueError(f"max_tokens for {content_type} must be positive")

@dataclass
class APIConfig:
    """Configuration for external API settings.
    
    Attributes:
        gemini_model_name: Name of the Gemini model to use
        elevenlabs_voice_id: ID of the ElevenLabs voice to use
        max_requests_per_minute: Rate limit for requests per minute
        max_requests_per_hour: Rate limit for requests per hour
    """
    gemini_model_name: str = "gemini-1.5-flash-001"
    elevenlabs_voice_id: str = "EXAVITQu4vr4xnSDxMaL"
    max_requests_per_minute: int = 10
    max_requests_per_hour: int = 100

    def validate(self) -> None:
        """Validate API settings."""
        if not self.gemini_model_name:
            raise ValueError("gemini_model_name cannot be empty")
        if not self.elevenlabs_voice_id:
            raise ValueError("elevenlabs_voice_id cannot be empty")
        if self.max_requests_per_minute <= 0:
            raise ValueError("max_requests_per_minute must be positive")
        if self.max_requests_per_hour <= 0:
            raise ValueError("max_requests_per_hour must be positive")

@dataclass
class MonitoringConfig:
    """Configuration for monitoring and metrics.
    
    Attributes:
        enable_cost_tracking: Whether to track API costs
        enable_performance_tracking: Whether to track performance metrics
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        metrics_export_interval: Interval for exporting metrics in seconds
        log_format: Format string for log messages
    """
    enable_cost_tracking: bool = True
    enable_performance_tracking: bool = True
    log_level: str = "INFO"
    metrics_export_interval: int = 60
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def validate(self) -> None:
        """Validate monitoring settings."""
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level not in valid_log_levels:
            raise ValueError(f"log_level must be one of {valid_log_levels}")
        if self.metrics_export_interval <= 0:
            raise ValueError("metrics_export_interval must be positive")

@dataclass
class AppConfig:
    """Main application configuration.
    
    Attributes:
        content_generation: Configuration for content generation
        api: Configuration for external APIs
        monitoring: Configuration for monitoring and metrics
        gcp_project_id: Google Cloud project ID
        elevenlabs_api_key: ElevenLabs API key
    """
    content_generation: ContentGenerationConfig = field(default_factory=ContentGenerationConfig)
    api: APIConfig = field(default_factory=APIConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Environment variables
    gcp_project_id: str = os.getenv("GCP_PROJECT_ID", "")
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")
    
    def validate(self) -> None:
        """Validate all configuration settings."""
        if not self.gcp_project_id:
            raise ValueError("GCP_PROJECT_ID environment variable is required")
        if not self.elevenlabs_api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is required")
        
        # Validate all sub-configurations
        self.content_generation.validate()
        self.api.validate()
        self.monitoring.validate()
        
        # Validate content generation settings
        if sum(self.content_generation.max_tokens_per_content_type.values()) > self.content_generation.max_total_tokens:
            raise ValueError("Total max tokens per content type exceeds max_total_tokens")

@lru_cache()
def get_config() -> AppConfig:
    """Get cached application configuration.
    
    Returns:
        AppConfig: The validated application configuration
        
    Raises:
        ValueError: If any configuration validation fails
    """
    config = AppConfig()
    config.validate()
    return config 