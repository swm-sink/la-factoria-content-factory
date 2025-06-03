"""
Simplified Content Generation Service - Phase 2 Refactored Version.
Main service for generating educational content using decomposed architecture.
"""

import logging
import time
from typing import Dict, Optional, Tuple

from prometheus_client import REGISTRY, Counter, Histogram

from app.core.config.settings import Settings, get_settings
from app.models.pydantic.content import (
    ContentMetadata,
    GeneratedContent,
    QualityMetrics,
)
from app.services.comprehensive_content_validator import (
    ComprehensiveContentValidator,
    ComprehensiveValidationReport,
)
from app.services.content_cache import ContentCacheService
from app.services.content_orchestration import ContentOrchestrationService
from app.services.enhanced_content_validator import EnhancedContentValidator
from app.services.llm_client import LLMClientService
from app.services.parallel_processor import ParallelProcessor
from app.services.prompt_optimizer import PromptOptimizer
from app.services.prompts import PromptService
from app.services.quality_metrics import QualityMetricsService

# Prometheus metrics - handle duplicate registration properly
try:
    CONTENT_GENERATION_CALLS = REGISTRY._names_to_collectors[
        "content_generation_calls_total"
    ]
except KeyError:
    CONTENT_GENERATION_CALLS = Counter(
        "content_generation_calls_total", "Total number of content generation calls"
    )

try:
    CONTENT_GENERATION_DURATION = REGISTRY._names_to_collectors[
        "content_generation_duration_seconds"
    ]
except KeyError:
    CONTENT_GENERATION_DURATION = Histogram(
        "content_generation_duration_seconds", "Time spent on content generation"
    )

try:
    CACHE_HITS = REGISTRY._names_to_collectors["content_cache_hits_total"]
except KeyError:
    CACHE_HITS = Counter(
        "content_cache_hits_total", "Total number of cache hits in content generation"
    )

try:
    CACHE_MISSES = REGISTRY._names_to_collectors["content_cache_misses_total"]
except KeyError:
    CACHE_MISSES = Counter(
        "content_cache_misses_total",
        "Total number of cache misses in content generation",
    )


class ContentGenerationService:
    """
    Simplified main content generation service using decomposed architecture.
    Coordinates LLM client, orchestration, validation, and caching services.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the service with all required components."""
        self.settings = settings or get_settings()
        self.logger = logging.getLogger(__name__)

        # Initialize core services
        self.prompt_optimizer = PromptOptimizer()
        self.llm_client = LLMClientService(self.settings, self.prompt_optimizer)
        self.prompt_service = PromptService()
        self.parallel_processor = ParallelProcessor(max_workers=4)

        # Initialize orchestration service
        self.orchestration_service = ContentOrchestrationService(
            settings=self.settings,
            llm_client=self.llm_client,
            prompt_service=self.prompt_service,
            parallel_processor=self.parallel_processor,
        )

        # Initialize validation services
        self.content_validator = EnhancedContentValidator()
        self.comprehensive_validator = ComprehensiveContentValidator()
        self.quality_service = QualityMetricsService()

        # Initialize cache service with error handling
        try:
            self.cache = ContentCacheService()
        except Exception as e:
            self.logger.warning(
                f"Failed to initialize cache service: {e}. Operating without cache."
            )
            self.cache = None

    def generate_educational_content(
        self,
        job_id: str,
        syllabus_text: str,
        target_format: str = "comprehensive",
        target_duration: Optional[float] = None,
        target_pages: Optional[int] = None,
        use_cache: bool = True,
        use_parallel: bool = False,  # MVP: Default to sequential for stability
        quality_threshold: float = 0.70,  # MVP: Lowered threshold for faster delivery
    ) -> Tuple[
        Optional[GeneratedContent],
        Optional[ContentMetadata],
        Optional[QualityMetrics],
        Dict[str, int],
        Optional[Dict[str, str]],
    ]:
        """
        Generate educational content using the decomposed architecture.

        Returns:
            GeneratedContent, ContentMetadata, QualityMetrics, total_token_usage, error_info (if any)
        """
        CONTENT_GENERATION_CALLS.inc()
        start_time = time.time()
        self.logger.info(
            f"Job {job_id}: Starting content generation with quality threshold {quality_threshold}."
        )

        total_token_usage = {"input_tokens": 0, "output_tokens": 0}
        error_info: Optional[Dict[str, str]] = None

        # Cache version for this refactored service
        CACHE_VERSION = "content_gen_service_v1"

        # Step 1: Check cache if enabled
        if use_cache and self.cache is not None:
            cached_result = self._check_cache(
                syllabus_text,
                target_format,
                target_duration,
                target_pages,
                CACHE_VERSION,
                job_id,
            )
            if cached_result:
                return cached_result

        try:
            # Step 2: Pre-validate input
            input_validation = self.content_validator.pre_validate_input(syllabus_text)
            if input_validation.quality_score < 0.3:
                error_info = {
                    "code": "INPUT_VALIDATION_FAILED",
                    "message": f"Input quality too low ({input_validation.quality_score:.2f}). "
                    f"Suggestions: {', '.join(input_validation.enhancement_suggestions[:2])}",
                }
                self.logger.error(f"Job {job_id}: {error_info['message']}")
                return None, None, None, total_token_usage, error_info

            # Step 3: Analyze input complexity
            prompt_context = self.orchestration_service.analyze_input_complexity(
                syllabus_text
            )

            # Create quality validator function for LLM client
            def quality_validator(content, content_type):
                return self.content_validator.validate_content(content, content_type)

            # Step 4: Generate master outline
            (
                master_outline,
                outline_tokens,
            ) = self.orchestration_service.generate_master_content_outline(
                syllabus_text, prompt_context, quality_validator
            )
            total_token_usage["input_tokens"] += outline_tokens.get("input_tokens", 0)
            total_token_usage["output_tokens"] += outline_tokens.get("output_tokens", 0)

            if not master_outline:
                error_info = {
                    "code": "OUTLINE_GENERATION_FAILED",
                    "message": "Failed to generate master content outline",
                }
                self.logger.error(f"Job {job_id}: Outline generation failed.")
                return None, None, None, total_token_usage, error_info

            # Step 5: Initialize GeneratedContent with outline
            generated_content_data = GeneratedContent(content_outline=master_outline)
            master_outline_json = master_outline.model_dump_json()

            # Step 6: Orchestrate derivative content generation
            (
                generated_content_data,
                total_token_usage,
            ) = self.orchestration_service.orchestrate_derivative_content_generation(
                master_outline_json=master_outline_json,
                prompt_context=prompt_context,
                use_parallel=use_parallel,
                generated_content_data=generated_content_data,
                initial_token_usage=total_token_usage,
                quality_validator=quality_validator,
            )

            # Step 7: Comprehensive validation
            comprehensive_report = self._perform_comprehensive_validation(
                generated_content_data,
                syllabus_text,
                target_format,
                job_id,
                quality_threshold,
            )

            # Step 8: Create quality metrics and metadata
            (
                quality_metrics_obj,
                content_metadata_obj,
            ) = self._create_metrics_and_metadata(
                comprehensive_report,
                syllabus_text,
                target_format,
                target_duration,
                target_pages,
                total_token_usage,
            )

            # Step 9: Cache results if enabled
            if use_cache and self.cache is not None:
                self._cache_results(
                    syllabus_text,
                    target_format,
                    target_duration,
                    target_pages,
                    generated_content_data,
                    content_metadata_obj,
                    quality_metrics_obj,
                    CACHE_VERSION,
                    job_id,
                )

            # Step 10: Record final metrics
            elapsed_time = time.time() - start_time
            CONTENT_GENERATION_DURATION.observe(elapsed_time)
            self.logger.info(
                f"Job {job_id}: Content generation completed in {elapsed_time:.2f}s. "
                f"Quality score: {quality_metrics_obj.overall_score:.2f}"
            )

            return (
                generated_content_data,
                content_metadata_obj,
                quality_metrics_obj,
                total_token_usage,
                None,
            )

        except Exception as e:
            self.logger.error(f"Job {job_id}: Unexpected error: {e}", exc_info=True)
            error_info = {
                "code": "GENERATION_ERROR",
                "message": f"Content generation failed: {str(e)}",
            }
            return None, None, None, total_token_usage, error_info

    def _check_cache(
        self,
        syllabus_text: str,
        target_format: str,
        target_duration: Optional[float],
        target_pages: Optional[int],
        cache_version: str,
        job_id: str,
    ) -> Optional[Tuple]:
        """Check cache for existing results."""
        cached_result = self.cache.get(
            syllabus_text,
            target_format,
            target_duration,
            target_pages,
            version=cache_version,
        )

        if cached_result:
            cached_content_payload, cached_qm_dict = cached_result
            if (
                isinstance(cached_content_payload, tuple)
                and len(cached_content_payload) == 3
            ):
                gc_cached, cm_cached, qm_cached_obj = cached_content_payload

                if (
                    isinstance(gc_cached, GeneratedContent)
                    and isinstance(cm_cached, ContentMetadata)
                    and isinstance(qm_cached_obj, QualityMetrics)
                ):
                    self.logger.info(
                        f"Job {job_id}: Cache hit (Version: {cache_version}, "
                        f"Score: {qm_cached_obj.overall_score:.2f})."
                    )
                    CACHE_HITS.inc()
                    return (
                        gc_cached,
                        cm_cached,
                        qm_cached_obj,
                        {"input_tokens": 0, "output_tokens": 0},
                        None,
                    )
                else:
                    self.logger.warning(
                        f"Job {job_id}: Cache data malformed for version {cache_version}."
                    )
            else:
                self.logger.info(
                    f"Job {job_id}: Cache miss for version {cache_version}."
                )
        else:
            self.logger.info(f"Job {job_id}: Cache miss for version {cache_version}.")

        CACHE_MISSES.inc()
        return None

    def _perform_comprehensive_validation(
        self,
        generated_content_data: GeneratedContent,
        syllabus_text: str,
        target_format: str,
        job_id: str,
        quality_threshold: float,
    ) -> ComprehensiveValidationReport:
        """Perform comprehensive validation of generated content."""
        comprehensive_report = self.comprehensive_validator.validate_content_pipeline(
            generated_content=generated_content_data,
            original_syllabus_text=syllabus_text,
            target_format=target_format,
        )

        self.logger.info(
            f"Job {job_id}: Comprehensive validation complete. "
            f"Overall score: {comprehensive_report.overall_score:.2f}, "
            f"Passed: {comprehensive_report.overall_passed}"
        )

        # MVP: Log quality status but proceed with content even if below threshold
        if (
            not comprehensive_report.overall_passed
            or comprehensive_report.overall_score < quality_threshold
        ):
            self.logger.warning(
                f"Job {job_id}: Content quality below threshold but proceeding for MVP. "
                f"Score: {comprehensive_report.overall_score:.2f}, Target: {quality_threshold}"
            )

        return comprehensive_report

    def _create_metrics_and_metadata(
        self,
        comprehensive_report: ComprehensiveValidationReport,
        syllabus_text: str,
        target_format: str,
        target_duration: Optional[float],
        target_pages: Optional[int],
        total_token_usage: Dict[str, int],
    ) -> Tuple[QualityMetrics, ContentMetadata]:
        """Create quality metrics and content metadata objects."""
        # Extract scores from comprehensive report
        structural_score = next(
            (
                s.score
                for s in comprehensive_report.stage_results
                if s.stage_name == "Structural Validation" and s.score is not None
            ),
            comprehensive_report.overall_score,
        )
        coherence_score = next(
            (
                s.score
                for s in comprehensive_report.stage_results
                if "Coherence" in s.stage_name and s.score is not None
            ),
            comprehensive_report.overall_score,
        )
        educational_score = next(
            (
                s.score
                for s in comprehensive_report.stage_results
                if "Educational Value" in s.stage_name and s.score is not None
            ),
            0.75,
        )

        quality_metrics_obj = QualityMetrics(
            overall_score=comprehensive_report.overall_score,
            readability_score=educational_score,
            structure_score=structural_score,
            relevance_score=coherence_score,
            engagement_score=educational_score * 0.9,
            format_compliance_score=structural_score,
        )

        content_metadata_obj = ContentMetadata(
            source_syllabus_length=len(syllabus_text),
            source_format=target_format or "comprehensive",
            target_duration_minutes=target_duration,
            target_pages_count=target_pages,
            ai_model_used=self.settings.gemini_model_name,
            tokens_consumed=total_token_usage["input_tokens"]
            + total_token_usage["output_tokens"],
            quality_score=quality_metrics_obj.overall_score,
        )

        return quality_metrics_obj, content_metadata_obj

    def _cache_results(
        self,
        syllabus_text: str,
        target_format: str,
        target_duration: Optional[float],
        target_pages: Optional[int],
        generated_content_data: GeneratedContent,
        content_metadata_obj: ContentMetadata,
        quality_metrics_obj: QualityMetrics,
        cache_version: str,
        job_id: str,
    ) -> None:
        """Cache the generated results."""
        self.logger.info(f"Job {job_id}: Caching generated content.")
        content_to_cache = (
            generated_content_data,
            content_metadata_obj,
            quality_metrics_obj,
        )
        self.cache.set(
            syllabus_text=syllabus_text,
            target_format=target_format,
            content=content_to_cache,
            target_duration=target_duration,
            target_pages=target_pages,
            quality_metrics_obj=quality_metrics_obj,
            version=cache_version,
        )

    def is_healthy(self) -> bool:
        """Check if the service is healthy and ready to generate content."""
        return self.llm_client.is_available()


# Dependency provider for the new service
_content_generation_service_instance: Optional[ContentGenerationService] = None


def get_content_generation_service() -> ContentGenerationService:
    """
    Dependency provider for ContentGenerationService.
    Ensures a single instance is created and reused.
    """
    global _content_generation_service_instance
    if _content_generation_service_instance is None:
        try:
            _content_generation_service_instance = ContentGenerationService()
        except Exception as e:
            import logging

            logging.getLogger(__name__).critical(
                f"Failed to instantiate ContentGenerationService: {e}", exc_info=True
            )
            raise
    return _content_generation_service_instance
