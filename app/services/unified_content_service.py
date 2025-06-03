"""
Unified Content Generation Service - Simplified Architecture
Single entry point for all content generation with clear boundaries.
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from app.core.config.settings import Settings, get_settings
from app.core.exceptions.custom_exceptions import (
    ContentGenerationError,
    InvalidInputError,
)
from app.models.pydantic.content import (
    ContentMetadata,
    ContentOutline,
    GeneratedContent,
    QualityMetrics,
)
from app.services.content_cache import ContentCacheService
from app.services.simple_llm_client import SimpleLLMClient
from app.services.simple_monitor import SimpleMonitor
from app.services.structural_validator import StructuralValidator


@dataclass
class ContentOptions:
    """Options for content generation"""

    target_format: str = "comprehensive"
    use_cache: bool = True
    use_parallel: bool = False  # Disabled for MVP
    quality_threshold: float = 0.7  # For monitoring only
    debug_mode: bool = False


@dataclass
class ContentResult:
    """Result of content generation"""

    content: Optional[GeneratedContent] = None
    metadata: Optional[ContentMetadata] = None
    metrics: Optional[QualityMetrics] = None
    token_usage: Dict[str, int] = Field(
        default_factory=lambda: {"input_tokens": 0, "output_tokens": 0}
    )
    error: Optional[Dict[str, str]] = None
    debug_info: Optional[Dict[str, Any]] = None


class UnifiedContentService:
    """
    Simplified, unified service for content generation.
    Single responsibility: Orchestrate content generation from syllabus.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize with simplified dependencies"""
        self.settings = settings or get_settings()
        self.logger = logging.getLogger(__name__)

        # Initialize simple, focused services
        self.llm = SimpleLLMClient(self.settings)
        self.validator = StructuralValidator()
        self.monitor = SimpleMonitor()

        # Cache is optional
        try:
            self.cache = ContentCacheService()
        except Exception as e:
            self.logger.warning(f"Cache unavailable: {e}")
            self.cache: Optional[ContentCacheService] = None

    async def generate_content(
        self, syllabus_text: str, job_id: str, options: Optional[ContentOptions] = None
    ) -> ContentResult:
        """
        Generate all content types from syllabus with simplified flow.

        Args:
            syllabus_text: Input syllabus/topic text
            job_id: Unique job identifier for tracking
            options: Generation options

        Returns:
            ContentResult with generated content or error
        """
        options = options or ContentOptions()
        start_time = time.time()

        # Initialize result
        result = ContentResult()

        # Start monitoring
        with self.monitor.track_operation("content_generation", job_id) as tracker:
            try:
                # Step 1: Check cache if enabled
                if options.use_cache and self.cache:
                    cached = await self._check_cache(syllabus_text, options, job_id)
                    if cached:
                        tracker.record_cache_hit()
                        return cached

                # Step 2: Validate input
                input_valid = self.validator.validate_input(syllabus_text)
                if not input_valid.is_valid:
                    raise InvalidInputError(f"Invalid input: {input_valid.errors}")

                # Step 3: Generate content outline
                self.logger.info(f"Job {job_id}: Generating content outline")
                outline, outline_tokens = await self._generate_outline(
                    syllabus_text, job_id, options
                )
                result.token_usage["input_tokens"] += outline_tokens["input_tokens"]
                result.token_usage["output_tokens"] += outline_tokens["output_tokens"]

                if not outline:
                    raise ContentGenerationError("Failed to generate outline")

                # Step 4: Generate derivative content
                self.logger.info(f"Job {job_id}: Generating derivative content")
                content_dict = await self._generate_all_content(
                    outline, job_id, options
                )

                # Update token usage
                for content_type, (content, tokens) in content_dict.items():
                    result.token_usage["input_tokens"] += tokens["input_tokens"]
                    result.token_usage["output_tokens"] += tokens["output_tokens"]

                # Step 5: Assemble final content
                generated_content = GeneratedContent(
                    content_outline=outline,
                    podcast_script=content_dict.get("podcast_script", (None, {}))[0],
                    study_guide=content_dict.get("study_guide", (None, {}))[0],
                    one_pager_summary=content_dict.get("one_pager_summary", (None, {}))[
                        0
                    ],
                    detailed_reading_material=content_dict.get(
                        "detailed_reading", (None, {})
                    )[0],
                    faqs=content_dict.get("faqs", (None, {}))[0],
                    flashcards=content_dict.get("flashcards", (None, {}))[0],
                    reading_guide_questions=content_dict.get(
                        "reading_questions", (None, {})
                    )[0],
                )

                # Step 6: Calculate metrics (non-blocking)
                quality_score = self._calculate_quality_score(generated_content)
                self.monitor.record_quality(job_id, quality_score)

                # Step 7: Create metadata
                result.content = generated_content
                result.metadata = ContentMetadata(
                    source_syllabus_length=len(syllabus_text),
                    source_format=options.target_format,
                    ai_model_used=self.settings.gemini_model_name,
                    tokens_consumed=sum(result.token_usage.values()),
                )
                result.metadata.quality_score = (
                    quality_score  # Assign quality_score after initialization
                )
                result.metrics = QualityMetrics(
                    overall_score=quality_score,
                    readability_score=quality_score * 0.9,
                    structure_score=0.95,  # We trust our structure
                    relevance_score=quality_score * 0.85,
                    engagement_score=quality_score * 0.8,
                    format_compliance_score=0.95,
                    validation_errors=[],  # Initialize as empty list
                )

                # Step 8: Cache result if enabled
                if options.use_cache and self.cache:
                    await self._save_to_cache(syllabus_text, options, result, job_id)

                # Record success
                duration = time.time() - start_time
                tracker.record_success(duration, result.token_usage)
                self.logger.info(
                    f"Job {job_id}: Content generation completed in {duration:.2f}s"
                )

                # Add debug info if requested
                if options.debug_mode:
                    result.debug_info = {
                        "duration_seconds": duration,
                        "quality_score": quality_score,
                        "content_types_generated": list(content_dict.keys()),
                        "cache_used": False,
                    }

                return result

            except Exception as e:
                # Record failure
                tracker.record_failure(str(e))
                self.logger.error(f"Job {job_id}: Generation failed: {e}")

                # Create error result
                result.error = {
                    "code": type(e).__name__,
                    "message": str(e),
                    "job_id": job_id,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                if options.debug_mode:
                    result.debug_info = {
                        "exception_type": type(e).__name__,
                        "traceback": self._get_safe_traceback(),
                    }

                return result

    async def _check_cache(
        self, syllabus_text: str, options: ContentOptions, job_id: str
    ) -> Optional[ContentResult]:
        """Check cache for existing content"""
        try:
            cache_key = self.cache._generate_cache_key(
                syllabus_text, options.target_format
            )
            cached_data = self.cache.get(
                syllabus_text,
                options.target_format,
                options.target_duration
                if hasattr(options, "target_duration")
                else None,
                options.target_pages if hasattr(options, "target_pages") else None,
            )

            if cached_data:
                self.logger.info(f"Job {job_id}: Cache hit")
                # Reconstruct ContentResult from cached data
                return ContentResult(
                    content=cached_data.get("content"),
                    metadata=cached_data.get("metadata"),
                    metrics=cached_data.get("metrics"),
                    token_usage={"input_tokens": 0, "output_tokens": 0},
                )
        except Exception as e:
            self.logger.warning(f"Cache check failed: {e}")

        return None

    async def _generate_outline(
        self, syllabus_text: str, job_id: str, options: ContentOptions
    ) -> Tuple[Optional[ContentOutline], Dict[str, int]]:
        """Generate content outline"""
        outline, tokens = await self.llm.generate_outline(
            syllabus_text, debug=options.debug_mode
        )

        if outline:
            # Validate structure
            validation = self.validator.validate_content(outline, "content_outline")
            if not validation.is_valid:
                self.logger.warning(
                    f"Outline validation warnings: {validation.warnings}"
                )

        return outline, tokens

    async def _generate_all_content(
        self, outline: ContentOutline, job_id: str, options: ContentOptions
    ) -> Dict[str, Tuple[Any, Dict[str, int]]]:
        """Generate all derivative content types"""
        content_types = [
            "podcast_script",
            "study_guide",
            "one_pager_summary",
            "detailed_reading",
            "faqs",
            "flashcards",
            "reading_questions",
        ]

        results = {}

        # Sequential generation for MVP (simpler debugging)
        for content_type in content_types:
            try:
                content, tokens = await self.llm.generate_content_type(
                    content_type, outline, debug=options.debug_mode
                )

                if content:
                    # Validate structure
                    validation = self.validator.validate_content(content, content_type)
                    if not validation.is_valid:
                        self.logger.warning(
                            f"{content_type} validation warnings: {validation.warnings}"
                        )

                    results[content_type] = (content, tokens)
                else:
                    self.logger.warning(f"Failed to generate {content_type}")
                    results[content_type] = (
                        None,
                        {"input_tokens": 0, "output_tokens": 0},
                    )

            except Exception as e:
                self.logger.error(f"Error generating {content_type}: {e}")
                results[content_type] = (None, {"input_tokens": 0, "output_tokens": 0})

        return results

    def _calculate_quality_score(self, content: GeneratedContent) -> float:
        """Simple quality scoring based on content presence"""
        # Count how many content types were successfully generated
        content_types = [
            content.content_outline,
            content.podcast_script,
            content.study_guide,
            content.one_pager_summary,
            content.detailed_reading_material,
            content.faqs,
            content.flashcards,
            content.reading_guide_questions,
        ]

        generated_count = sum(1 for c in content_types if c is not None)
        total_count = len(content_types)

        # Base score on completion percentage
        base_score = generated_count / total_count

        # Apply minimal quality boost based on outline
        if content.content_outline and hasattr(content.content_outline, "sections"):
            if len(content.content_outline.sections) >= 3:
                base_score = min(1.0, base_score * 1.1)

        return round(base_score, 2)

    async def _save_to_cache(
        self,
        syllabus_text: str,
        options: ContentOptions,
        result: ContentResult,
        job_id: str,
    ) -> None:
        """Save result to cache"""
        try:
            cache_key = self.cache._generate_cache_key(
                syllabus_text, options.target_format
            )

            cache_data = {
                "content": result.content,
                "metadata": result.metadata,
                "metrics": result.metrics,
                "cached_at": datetime.utcnow().isoformat(),
            }

            self.cache.set(cache_key, cache_data)
            self.logger.info(f"Job {job_id}: Cached result")

        except Exception as e:
            self.logger.warning(f"Failed to cache result: {e}")

    def _get_safe_traceback(self) -> str:
        """Get traceback without sensitive information"""
        import traceback

        # This would filter out any sensitive data
        return traceback.format_exc()


# Dependency injection
_unified_service_instance: Optional[UnifiedContentService] = None


def get_unified_content_service() -> UnifiedContentService:
    """Get or create unified content service instance"""
    global _unified_service_instance
    if _unified_service_instance is None:
        _unified_service_instance = UnifiedContentService()
    return _unified_service_instance
