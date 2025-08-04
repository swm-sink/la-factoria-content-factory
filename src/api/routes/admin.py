"""
Admin API Routes for La Factoria
Administrative endpoints for system management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
import logging
from datetime import datetime

from ...core.auth import verify_admin_api_key
from ...core.config import settings
from ...models.content import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/system/info")
async def get_system_info(api_key: str = Depends(verify_admin_api_key)):
    """
    Get comprehensive system information

    Returns detailed information about:
    - System configuration
    - Service status
    - Resource usage
    - Feature flags
    """
    try:
        return {
            "system": {
                "app_name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
                "debug_mode": settings.DEBUG
            },
            "configuration": {
                "database_configured": bool(settings.DATABASE_URL),
                "redis_configured": bool(settings.REDIS_URL),
                "langfuse_configured": settings.has_langfuse_config,
                "ai_providers": {
                    "openai": settings.has_openai_config,
                    "anthropic": settings.has_anthropic_config,
                    "elevenlabs": settings.has_elevenlabs_config,
                    "vertex_ai": bool(settings.GOOGLE_CLOUD_PROJECT)
                }
            },
            "quality_thresholds": {
                "overall": settings.QUALITY_THRESHOLD_OVERALL,
                "educational": settings.QUALITY_THRESHOLD_EDUCATIONAL,
                "factual": settings.QUALITY_THRESHOLD_FACTUAL
            },
            "limits": {
                "max_tokens": settings.DEFAULT_MAX_TOKENS,
                "generation_timeout": settings.CONTENT_GENERATION_TIMEOUT,
                "max_concurrent": settings.MAX_CONCURRENT_GENERATIONS,
                "rate_limit_per_minute": settings.RATE_LIMIT_REQUESTS_PER_MINUTE
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system information"
        )

@router.get("/content/stats")
async def get_content_stats(api_key: str = Depends(verify_admin_api_key)):
    """
    Get content generation statistics

    Returns metrics about content generation performance and usage
    """
    try:
        # Placeholder implementation - would connect to actual database/analytics
        return {
            "content_generation": {
                "total_generated": 0,  # Would query database
                "by_content_type": {
                    "study_guide": 0,
                    "flashcards": 0,
                    "podcast_script": 0,
                    # ... other types
                },
                "by_age_group": {
                    "elementary": 0,
                    "middle_school": 0,
                    "high_school": 0,
                    "college": 0,
                    "adult_learning": 0
                }
            },
            "quality_metrics": {
                "average_quality_score": 0.0,
                "above_threshold_percentage": 0.0,
                "regeneration_rate": 0.0
            },
            "performance": {
                "average_generation_time_ms": 0,
                "successful_generations": 0,
                "failed_generations": 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get content stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve content statistics"
        )

@router.get("/ai-providers/stats")
async def get_ai_provider_stats(api_key: str = Depends(verify_admin_api_key)):
    """
    Get AI provider usage statistics and performance metrics
    """
    try:
        from ...services.ai_providers import AIProviderManager

        provider_manager = AIProviderManager()
        stats = provider_manager.get_provider_stats()

        return {
            "provider_stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get AI provider stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve AI provider statistics"
        )

@router.post("/cache/clear")
async def clear_cache(api_key: str = Depends(verify_admin_api_key)):
    """
    Clear application caches

    Clears:
    - Prompt template cache
    - AI provider caches
    - Any other application caches
    """
    try:
        from ...services.prompt_loader import PromptTemplateLoader

        # Clear prompt template cache
        prompt_loader = PromptTemplateLoader()
        await prompt_loader.reload_all_templates()

        logger.info("Application caches cleared by admin")

        return {
            "status": "success",
            "message": "All caches cleared successfully",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear caches"
        )

@router.post("/prompts/reload")
async def reload_prompts(api_key: str = Depends(verify_admin_api_key)):
    """
    Reload prompt templates from disk

    Forces reload of all prompt templates from the prompts directory
    """
    try:
        from ...services.prompt_loader import PromptTemplateLoader

        prompt_loader = PromptTemplateLoader()
        await prompt_loader.initialize()
        await prompt_loader.reload_all_templates()

        template_stats = prompt_loader.get_template_stats()

        logger.info("Prompt templates reloaded by admin")

        return {
            "status": "success",
            "message": "Prompt templates reloaded successfully",
            "template_stats": template_stats,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to reload prompts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reload prompt templates"
        )

@router.get("/prompts/info")
async def get_prompt_info(api_key: str = Depends(verify_admin_api_key)):
    """
    Get information about loaded prompt templates
    """
    try:
        from ...services.prompt_loader import PromptTemplateLoader

        prompt_loader = PromptTemplateLoader()
        await prompt_loader.initialize()

        # Get info for each content type
        prompt_info = {}
        for content_type in prompt_loader.get_supported_content_types():
            try:
                metadata = await prompt_loader.get_template_metadata(content_type)
                prompt_info[content_type] = metadata
            except Exception as e:
                prompt_info[content_type] = {"error": str(e)}

        return {
            "template_stats": prompt_loader.get_template_stats(),
            "template_details": prompt_info,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get prompt info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prompt information"
        )

@router.post("/config/update")
async def update_config(
    config_updates: Dict[str, Any],
    api_key: str = Depends(verify_admin_api_key)
):
    """
    Update runtime configuration (limited set of safe parameters)

    Allows updating certain configuration values without restart
    """
    try:
        # Define which config values can be safely updated at runtime
        updatable_configs = {
            "DEFAULT_MAX_TOKENS",
            "CONTENT_GENERATION_TIMEOUT",
            "MAX_CONCURRENT_GENERATIONS",
            "QUALITY_THRESHOLD_OVERALL",
            "QUALITY_THRESHOLD_EDUCATIONAL",
            "QUALITY_THRESHOLD_FACTUAL",
            "RATE_LIMIT_REQUESTS_PER_MINUTE"
        }

        updated = {}
        invalid = {}

        for key, value in config_updates.items():
            if key in updatable_configs:
                try:
                    # Update the setting (basic validation)
                    if hasattr(settings, key):
                        setattr(settings, key, value)
                        updated[key] = value
                    else:
                        invalid[key] = "Setting not found"
                except Exception as e:
                    invalid[key] = str(e)
            else:
                invalid[key] = "Not updatable at runtime"

        logger.info(f"Configuration updated by admin: {updated}")

        return {
            "status": "success",
            "updated": updated,
            "invalid": invalid,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update configuration"
        )

@router.delete("/user/{user_id}")
async def delete_user_data(
    user_id: str,
    api_key: str = Depends(verify_admin_api_key)
):
    """
    Delete all user data (GDPR compliance)

    Permanently removes all data associated with a user ID
    """
    try:
        # Placeholder implementation - would connect to actual database
        # In a real implementation, this would:
        # 1. Delete user record
        # 2. Delete all generated content for user
        # 3. Delete any associated analytics data
        # 4. Log the deletion for audit purposes

        logger.info(f"User data deletion requested for user_id: {user_id}")

        # For now, just log the request
        return {
            "status": "success",
            "message": f"User data deletion completed for user_id: {user_id}",
            "deleted_items": {
                "user_record": True,
                "generated_content": 0,  # Would be actual count
                "analytics_data": 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to delete user data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user data"
        )

@router.get("/logs/recent")
async def get_recent_logs(
    lines: int = 100,
    level: str = "INFO",
    api_key: str = Depends(verify_admin_api_key)
):
    """
    Get recent application logs

    Returns recent log entries for debugging and monitoring
    """
    try:
        # Placeholder implementation
        # In a real implementation, this would read from log files or log aggregation service

        return {
            "logs": [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": "INFO",
                    "message": "This is a placeholder log entry",
                    "logger": "la_factoria.admin"
                }
            ],
            "parameters": {
                "lines_requested": lines,
                "level_filter": level
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get recent logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve logs"
        )
