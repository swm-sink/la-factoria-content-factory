"""Content validation service for AI-generated content.

This service orchestrates the validation workflow including:
- Pre-validation content checks
- Pydantic model validation
- Quality assessment
- Content sanitization
- Error handling and reporting
"""

import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime

from app.models.pydantic.content import (
    ContentResponse,
    GeneratedContent,
    QualityMetrics,
    ContentMetadata,
    APIErrorResponse,
)
from app.utils.content_validation import (
    validate_and_parse_content_response,
    validate_ai_content_dict,
    sanitize_content_dict,
    calculate_readability_score,
    estimate_reading_time,
    extract_text_from_content,
)
from app.core.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ContentValidationService:
    """Service for validating and processing AI-generated content."""

    def __init__(self):
        self.settings = settings
        self.validation_stats = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "average_quality_score": 0.0,
        }

    def validate_raw_ai_output(
        self,
        raw_content: Dict[str, Any],
        job_id: Optional[str] = None,
        ai_model: Optional[str] = None,
        tokens_used: Optional[int] = None,
    ) -> Tuple[bool, Union[ContentResponse, APIErrorResponse]]:
        """Validate raw AI output and return structured response.

        Args:
            raw_content: Raw dictionary from AI model
            job_id: Optional job identifier
            ai_model: AI model used for generation
            tokens_used: Number of tokens consumed

        Returns:
            Tuple of (success, ContentResponse_or_APIErrorResponse)
        """
        self.validation_stats["total_validations"] += 1

        try:
            logger.info(f"Validating AI output for job {job_id}")

            # Pre-validation checks
            if not raw_content:
                error_response = self._create_error_response(
                    "Empty content received from AI model", "EMPTY_CONTENT", job_id
                )
                return False, error_response

            # Validate and parse content
            success, result = validate_and_parse_content_response(raw_content)

            if success:
                content_response = result

                # Enhance metadata
                if not content_response.metadata:
                    content_response.metadata = ContentMetadata()

                content_response.job_id = job_id
                content_response.metadata.ai_model_used = ai_model
                content_response.metadata.tokens_consumed = tokens_used
                content_response.metadata.generation_timestamp = datetime.utcnow()

                # Calculate additional metrics
                self._enhance_quality_metrics(content_response)

                # Update statistics
                self.validation_stats["successful_validations"] += 1
                if content_response.quality_metrics:
                    current_avg = self.validation_stats["average_quality_score"]
                    new_score = content_response.quality_metrics.overall_score or 0
                    total_successful = self.validation_stats["successful_validations"]
                    self.validation_stats["average_quality_score"] = (
                        current_avg * (total_successful - 1) + new_score
                    ) / total_successful

                logger.info(f"Successfully validated content for job {job_id}")
                return True, content_response

            else:
                # Validation failed
                error_messages = result
                self.validation_stats["failed_validations"] += 1

                error_response = self._create_error_response(
                    "Content validation failed",
                    "VALIDATION_FAILED",
                    job_id,
                    details=error_messages,
                )

                logger.warning(
                    f"Content validation failed for job {job_id}: {error_messages}"
                )
                return False, error_response

        except Exception as e:
            self.validation_stats["failed_validations"] += 1
            logger.error(
                f"Unexpected error during content validation for job {job_id}: {e}",
                exc_info=True,
            )

            error_response = self._create_error_response(
                "Internal validation error", "INTERNAL_ERROR", job_id, details=str(e)
            )
            return False, error_response

    def _enhance_quality_metrics(self, content_response: ContentResponse) -> None:
        """Enhance quality metrics with additional calculations.

        Args:
            content_response: ContentResponse to enhance
        """
        try:
            if not content_response.quality_metrics:
                content_response.quality_metrics = QualityMetrics()

            metrics = content_response.quality_metrics
            content = content_response.content

            # Calculate content-specific metrics
            if content.podcast_script:
                script_text = (
                    content.podcast_script.introduction
                    + " "
                    + content.podcast_script.main_content
                    + " "
                    + content.podcast_script.conclusion
                )
                metrics.engagement_score = self._calculate_engagement_score(script_text)

                # Estimate duration
                estimated_duration = estimate_reading_time(
                    script_text, wpm=150
                )  # Speaking pace
                content.podcast_script.estimated_duration_minutes = estimated_duration
                content_response.metadata.calculated_total_duration = estimated_duration

            if content.study_guide:
                guide_text = content.study_guide.detailed_content
                metrics.relevance_score = self._calculate_relevance_score(
                    guide_text, content.content_outline.overview
                )

            # Calculate format compliance
            metrics.format_compliance_score = self._calculate_format_compliance(content)

            # Update overall score with new metrics
            scores = [
                metrics.readability_score or 0,
                metrics.structure_score or 0,
                metrics.engagement_score or 0,
                metrics.relevance_score or 0,
                metrics.format_compliance_score or 0,
            ]
            valid_scores = [s for s in scores if s > 0]
            if valid_scores:
                metrics.overall_score = sum(valid_scores) / len(valid_scores)

        except Exception as e:
            logger.warning(f"Failed to enhance quality metrics: {e}")

    def _calculate_engagement_score(self, text: str) -> float:
        """Calculate engagement score based on text characteristics.

        Args:
            text: Text to analyze

        Returns:
            Engagement score between 0 and 1
        """
        if not text:
            return 0.0

        score = 0.5  # Base score

        # Check for engaging elements
        engaging_words = [
            "you",
            "your",
            "imagine",
            "discover",
            "learn",
            "understand",
            "explore",
            "consider",
            "think",
            "question",
            "example",
        ]

        word_count = len(text.split())
        if word_count > 0:
            engaging_count = sum(
                1 for word in text.lower().split() if word in engaging_words
            )
            engagement_ratio = engaging_count / word_count

            # Bonus for questions
            question_count = text.count("?")
            question_ratio = question_count / max(1, text.count("."))

            # Calculate final score
            score = min(1.0, 0.3 + engagement_ratio * 0.5 + question_ratio * 0.2)

        return score

    def _calculate_relevance_score(self, content: str, reference: str) -> float:
        """Calculate relevance score by comparing content to reference.

        Args:
            content: Content to score
            reference: Reference text (e.g., outline overview)

        Returns:
            Relevance score between 0 and 1
        """
        if not content or not reference:
            return 0.0

        # Simple keyword overlap approach
        content_words = set(content.lower().split())
        reference_words = set(reference.lower().split())

        # Filter out common words
        common_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }
        content_words -= common_words
        reference_words -= common_words

        if not reference_words:
            return 0.5

        overlap = len(content_words & reference_words)
        relevance_score = overlap / len(reference_words)

        return min(1.0, relevance_score)

    def _calculate_format_compliance(self, content: GeneratedContent) -> float:
        """Calculate format compliance score.

        Args:
            content: Generated content to evaluate

        Returns:
            Format compliance score between 0 and 1
        """
        compliance_score = 0.0
        total_checks = 0

        # Check outline compliance
        if content.content_outline:
            total_checks += 1
            if (
                len(content.content_outline.sections) >= 3
                and len(content.content_outline.learning_objectives) >= 3
            ):
                compliance_score += 1

        # Check podcast script compliance
        if content.podcast_script:
            total_checks += 1
            script = content.podcast_script
            if (
                script.introduction
                and script.main_content
                and script.conclusion
                and len(script.introduction) >= 100
                and len(script.main_content) >= 800
            ):
                compliance_score += 1

        # Check study guide compliance
        if content.study_guide:
            total_checks += 1
            guide = content.study_guide
            if (
                guide.overview
                and guide.detailed_content
                and guide.summary
                and len(guide.key_concepts) >= 5
            ):
                compliance_score += 1

        # Check FAQ compliance
        if content.faqs:
            total_checks += 1
            if 5 <= len(content.faqs.items) <= 15:
                compliance_score += 1

        # Check flashcards compliance
        if content.flashcards:
            total_checks += 1
            if 10 <= len(content.flashcards.items) <= 25:
                compliance_score += 1

        return compliance_score / max(1, total_checks)

    def _create_error_response(
        self,
        error_message: str,
        error_code: str,
        job_id: Optional[str] = None,
        details: Optional[Any] = None,
    ) -> APIErrorResponse:
        """Create standardized error response.

        Args:
            error_message: Human-readable error message
            error_code: Machine-readable error code
            job_id: Optional job identifier
            details: Optional error details

        Returns:
            APIErrorResponse object
        """
        return APIErrorResponse(
            error=error_message,
            code=error_code,
            details=details,
            content_status={
                "job_id": job_id,
                "validation_status": "failed",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics.

        Returns:
            Dictionary with validation statistics
        """
        return {
            **self.validation_stats,
            "success_rate": (
                self.validation_stats["successful_validations"]
                / max(1, self.validation_stats["total_validations"])
            ),
        }

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on validation service.

        Returns:
            Health check results
        """
        try:
            # Test basic validation functionality
            test_content = {
                "content_outline": {
                    "title": "Test Content",
                    "overview": "This is a test overview for health checking the validation service functionality.",
                    "learning_objectives": [
                        "Learn testing",
                        "Understand validation",
                        "Apply health checks",
                    ],
                    "sections": [
                        {
                            "section_number": 1,
                            "title": "Introduction",
                            "description": "Introduction section for testing purposes.",
                            "key_points": ["Point 1", "Point 2"],
                        }
                    ],
                }
            }

            success, _ = validate_and_parse_content_response(test_content)

            return {
                "status": "healthy" if success else "degraded",
                "validation_test": "passed" if success else "failed",
                "statistics": self.get_validation_statistics(),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Global service instance
_validation_service: Optional[ContentValidationService] = None


def get_content_validation_service() -> ContentValidationService:
    """Get or create the global content validation service instance.

    Returns:
        ContentValidationService instance
    """
    global _validation_service
    if _validation_service is None:
        _validation_service = ContentValidationService()
    return _validation_service
