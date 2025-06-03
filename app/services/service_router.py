"""
Service Router - Routes requests to appropriate service implementation
"""

import logging
from typing import Any, Dict, Optional, Tuple

from app.core.config.settings import Settings
from app.models.pydantic.content import GeneratedContent
from app.services.content_generation_service import ContentGenerationService
from app.services.feature_flags import get_feature_flags
from app.services.unified_content_service import ContentOptions, UnifiedContentService


class ServiceRouter:
    """
    Routes content generation requests to the appropriate service.
    Supports gradual rollout and A/B testing.
    """

    def __init__(self, settings: Settings):
        """Initialize router with both service implementations"""
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        self.feature_flags = get_feature_flags()

        # Initialize both services
        self.unified_service = UnifiedContentService(settings)
        self.legacy_service = ContentGenerationService(settings)

        self._log_configuration()

    def _log_configuration(self) -> None:
        """Log current routing configuration"""
        use_unified = self.feature_flags.get(
            "content_generation.use_unified_service", False
        )
        rollout_pct = self.feature_flags.get("rollout.unified_service_percentage", 0)

        self.logger.info(
            f"Service router initialized - "
            f"use_unified: {use_unified}, rollout: {rollout_pct}%"
        )

    async def generate_content(
        self, job_id: str, syllabus_text: str, **kwargs
    ) -> Tuple[Optional[GeneratedContent], Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Route content generation request to appropriate service.

        Returns:
            Tuple of (content, metadata, error)
        """
        # Determine which service to use
        use_unified = self.feature_flags.should_use_unified_service(job_id)

        self.logger.info(
            f"Routing job {job_id} to {'unified' if use_unified else 'legacy'} service"
        )

        try:
            if use_unified:
                return await self._call_unified_service(
                    job_id=job_id, syllabus_text=syllabus_text, **kwargs
                )
            else:
                return await self._call_legacy_service(
                    job_id=job_id, syllabus_text=syllabus_text, **kwargs
                )

        except Exception as e:
            self.logger.error(f"Service routing failed: {e}")
            return (
                None,
                {},
                {
                    "message": "Content generation failed",
                    "error": str(e),
                    "service": "unified" if use_unified else "legacy",
                },
            )

    async def _call_unified_service(
        self, job_id: str, syllabus_text: str, **kwargs
    ) -> Tuple[Optional[GeneratedContent], Dict[str, Any], Optional[Dict[str, Any]]]:
        """Call unified content service"""
        # Create options from kwargs
        options = ContentOptions(
            target_format=kwargs.get("target_format", "comprehensive"),
            use_cache=kwargs.get("use_cache", True),
            use_parallel=kwargs.get("use_parallel", False),
            quality_threshold=kwargs.get("quality_threshold", 0.7),
            debug_mode=self.feature_flags.get("content_generation.debug_mode", False),
        )

        # Call unified service
        result = await self.unified_service.generate_content(
            syllabus_text=syllabus_text, job_id=job_id, options=options
        )

        # Convert ContentResult to expected tuple format
        if result.error:
            return None, {}, result.error

        # Build metadata dict from result
        metadata = {}
        if result.metadata:
            metadata.update(result.metadata.model_dump(exclude_none=True))
        if result.metrics:
            metadata["quality_metrics"] = result.metrics.model_dump(exclude_none=True)
        if result.token_usage:
            metadata["token_usage"] = result.token_usage

        return result.content, metadata, None

    async def _call_legacy_service(
        self, job_id: str, syllabus_text: str, **kwargs
    ) -> Tuple[Optional[GeneratedContent], Dict[str, Any], Optional[Dict[str, Any]]]:
        """Call legacy content generation service"""
        # Legacy service has different return format, need to adapt
        result = self.legacy_service.generate_educational_content(
            job_id=job_id,
            syllabus_text=syllabus_text,
            target_format=kwargs.get("target_format", "comprehensive"),
            quality_threshold=kwargs.get("quality_threshold", 0.7),
            use_cache=kwargs.get("use_cache", True),
            use_parallel=kwargs.get("use_parallel", False),
        )

        # Unpack legacy format
        content, metadata, quality, tokens, error = result

        # Adapt to unified format
        if error:
            return None, metadata or {}, error

        # Merge metadata
        full_metadata = metadata or {}
        if quality:
            full_metadata["quality_metrics"] = quality
        if tokens:
            full_metadata["token_usage"] = tokens

        return content, full_metadata, None

    def health_check(self) -> Dict[str, Any]:
        """Check health of both services"""
        return {
            "router": "healthy",
            "unified_service": "healthy" if self.unified_service else "not_initialized",
            "legacy_service": "healthy" if self.legacy_service else "not_initialized",
            "feature_flags": self.feature_flags.get_all_flags(),
        }


# Factory function
def get_service_router(settings: Optional[Settings] = None) -> ServiceRouter:
    """Get or create service router instance"""
    if not settings:
        settings = Settings()
    return ServiceRouter(settings)
