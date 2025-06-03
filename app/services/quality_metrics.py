"""
Quality metrics service for content evaluation.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from textstat import (
    automated_readability_index,
    flesch_kincaid_grade,
    flesch_reading_ease,
)

logger = logging.getLogger(__name__)


@dataclass
class ReadabilityMetrics:
    """Readability metrics for content."""

    flesch_reading_ease: float
    flesch_kincaid_grade: float
    automated_readability_index: float


@dataclass
class ContentStructureMetrics:
    """Structure metrics for content."""

    has_introduction: bool
    has_conclusion: bool
    has_sections: bool
    section_count: int
    avg_section_length: float
    logical_flow_score: float


@dataclass
class ContentRelevanceMetrics:
    """Relevance metrics for content."""

    keyword_coverage: float
    topic_coherence: float
    content_relevance: float


@dataclass
class QualityMetrics:
    """Quality metrics for content."""

    readability_score: float
    complexity_score: float
    engagement_score: float
    overall_score: float
    metadata: Dict[str, Any]


class QualityMetricsService:
    """Service for evaluating content quality."""

    def __init__(self):
        """Initialize the service."""
        self.logger = logging.getLogger(__name__)

    def evaluate_content(
        self,
        content: str,
        syllabus_text: str,
        target_format: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QualityMetrics:
        """
        Evaluate content quality.

        Args:
            content: Content to evaluate
            syllabus_text: Syllabus text for relevance comparison
            target_format: Target format for structure validation
            metadata: Additional metadata

        Returns:
            QualityMetrics object with detailed scores
        """
        # Calculate readability metrics
        readability = self._calculate_readability_metrics(content)

        # Calculate structure metrics
        structure = self._calculate_structure_metrics(content, target_format)

        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(content)

        # Calculate overall score
        overall_score = self._calculate_overall_score(
            readability_score=readability.flesch_reading_ease / 100.0,
            complexity_score=structure.logical_flow_score,
            engagement_score=engagement_score,
        )

        self.logger.info(f"Content quality evaluated: {overall_score:.3f}")

        return QualityMetrics(
            readability_score=readability.flesch_reading_ease / 100.0,
            complexity_score=structure.logical_flow_score,
            engagement_score=engagement_score,
            overall_score=overall_score,
            metadata=metadata or {},
        )

    def _calculate_readability_metrics(self, content: str) -> ReadabilityMetrics:
        """Calculate readability metrics for content."""
        try:
            flesch_ease = flesch_reading_ease(content)
            flesch_grade = flesch_kincaid_grade(content)
            ari = automated_readability_index(content)

            return ReadabilityMetrics(
                flesch_reading_ease=flesch_ease,
                flesch_kincaid_grade=flesch_grade,
                automated_readability_index=ari,
            )
        except Exception as e:
            self.logger.warning(f"Error calculating readability metrics: {str(e)}")
            return ReadabilityMetrics(
                flesch_reading_ease=50.0,
                flesch_kincaid_grade=10.0,
                automated_readability_index=10.0,
            )

    def _calculate_structure_metrics(
        self, content: str, target_format: str
    ) -> ContentStructureMetrics:
        """Calculate structure metrics for content."""
        # Check for introduction and conclusion
        has_introduction = "introduction" in content.lower()[:500]
        has_conclusion = "conclusion" in content.lower()[-500:]

        # Split into sections
        sections = content.split("\n\n")
        has_sections = len(sections) > 1
        section_count = len(sections)

        # Calculate average section length
        avg_section_length = (
            sum(len(s) for s in sections) / len(sections) if sections else 0
        )

        # Calculate logical flow score
        logical_flow_score = 0.0

        # Check for transition words
        transition_words = [
            "first",
            "second",
            "third",
            "finally",
            "however",
            "moreover",
            "furthermore",
            "in addition",
            "on the other hand",
            "consequently",
            "therefore",
            "thus",
        ]

        for word in transition_words:
            if word in content.lower():
                logical_flow_score += 0.1

        # Check for section headers
        if has_sections:
            logical_flow_score += 0.2

        # Check for introduction and conclusion
        if has_introduction:
            logical_flow_score += 0.2
        if has_conclusion:
            logical_flow_score += 0.2

        return ContentStructureMetrics(
            has_introduction=has_introduction,
            has_conclusion=has_conclusion,
            has_sections=has_sections,
            section_count=section_count,
            avg_section_length=avg_section_length,
            logical_flow_score=min(1.0, logical_flow_score),
        )

    def _calculate_engagement_score(self, content: str) -> float:
        """Calculate engagement score for content."""
        # Simple engagement score based on content length and structure
        base_score = min(1.0, len(content) / 5000.0)  # Based on content length

        # Add points for interactive elements
        if "?" in content:  # Questions
            base_score += 0.1
        if "!" in content:  # Exclamations
            base_score += 0.1
        if ":" in content:  # Lists
            base_score += 0.1

        return min(1.0, base_score)

    def _calculate_overall_score(
        self, readability_score: float, complexity_score: float, engagement_score: float
    ) -> float:
        """Calculate overall quality score."""
        weights = {"readability": 0.4, "complexity": 0.3, "engagement": 0.3}

        return (
            readability_score * weights["readability"]
            + complexity_score * weights["complexity"]
            + engagement_score * weights["engagement"]
        )
