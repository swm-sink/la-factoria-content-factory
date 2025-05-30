"""
Content quality metrics service for evaluating generated content.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from textstat import (
    flesch_reading_ease,
    flesch_kincaid_grade,
    automated_readability_index,
)
from prometheus_client import Histogram, Counter

# Prometheus metrics
QUALITY_EVALUATION_TIME = Histogram(
    "quality_evaluation_duration_seconds", "Time spent on quality evaluation"
)
QUALITY_SCORES = Histogram(
    "content_quality_scores",
    "Distribution of content quality scores",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)


@dataclass
class ReadabilityMetrics:
    """Readability metrics for content."""

    flesch_reading_ease: float
    flesch_kincaid_grade: float
    automated_readability_index: float
    avg_sentence_length: float
    avg_word_length: float

    def get_readability_score(self) -> float:
        """Calculate overall readability score (0-1)."""
        # Normalize Flesch Reading Ease (0-100 to 0-1)
        flesch_normalized = max(0, min(100, self.flesch_reading_ease)) / 100

        # Penalize very high grade levels (target: 8-12th grade)
        grade_penalty = 0
        if self.flesch_kincaid_grade > 12:
            grade_penalty = min(0.3, (self.flesch_kincaid_grade - 12) * 0.05)
        elif self.flesch_kincaid_grade < 8:
            grade_penalty = min(0.2, (8 - self.flesch_kincaid_grade) * 0.03)

        return max(0, flesch_normalized - grade_penalty)


@dataclass
class ContentStructureMetrics:
    """Structural metrics for content."""

    has_introduction: bool
    has_conclusion: bool
    section_count: int
    paragraph_count: int
    avg_paragraph_length: float
    has_transitions: bool
    logical_flow_score: float

    def get_structure_score(self) -> float:
        """Calculate overall structure score (0-1)."""
        score = 0.0

        # Basic structure elements
        if self.has_introduction:
            score += 0.2
        if self.has_conclusion:
            score += 0.2
        if self.has_transitions:
            score += 0.2

        # Section organization
        if 3 <= self.section_count <= 8:
            score += 0.2
        elif self.section_count > 0:
            score += 0.1

        # Paragraph structure
        if 50 <= self.avg_paragraph_length <= 150:
            score += 0.1
        elif self.avg_paragraph_length > 0:
            score += 0.05

        # Logical flow
        score += self.logical_flow_score * 0.1

        return min(1.0, score)


@dataclass
class ContentRelevanceMetrics:
    """Relevance metrics for content."""

    keyword_coverage: float
    topic_coherence: float
    factual_accuracy_score: float
    completeness_score: float

    def get_relevance_score(self) -> float:
        """Calculate overall relevance score (0-1)."""
        weights = {
            "keyword_coverage": 0.25,
            "topic_coherence": 0.25,
            "factual_accuracy": 0.25,
            "completeness": 0.25,
        }

        return (
            self.keyword_coverage * weights["keyword_coverage"]
            + self.topic_coherence * weights["topic_coherence"]
            + self.factual_accuracy_score * weights["factual_accuracy"]
            + self.completeness_score * weights["completeness"]
        )


@dataclass
class QualityMetrics:
    """Overall quality metrics for content."""

    readability: ReadabilityMetrics
    structure: ContentStructureMetrics
    relevance: ContentRelevanceMetrics
    engagement_score: float
    format_compliance_score: float
    overall_score: float = 0.0

    def calculate_overall_score(self) -> float:
        """Calculate the overall quality score."""
        weights = {
            "readability": 0.25,
            "structure": 0.25,
            "relevance": 0.3,
            "engagement": 0.1,
            "format_compliance": 0.1,
        }

        self.overall_score = (
            self.readability.get_readability_score() * weights["readability"]
            + self.structure.get_structure_score() * weights["structure"]
            + self.relevance.get_relevance_score() * weights["relevance"]
            + self.engagement_score * weights["engagement"]
            + self.format_compliance_score * weights["format_compliance"]
        )

        return self.overall_score


class QualityMetricsService:
    """Service for evaluating content quality."""

    def __init__(self):
        """Initialize the quality metrics service."""
        self.logger = logging.getLogger(__name__)

    def evaluate_content(
        self,
        content: str,
        syllabus_text: str,
        target_format: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> QualityMetrics:
        """
        Evaluate the quality of generated content.

        Args:
            content: The generated content to evaluate
            syllabus_text: The original syllabus text
            target_format: The target format (podcast, guide, etc.)
            metadata: Additional metadata about the content

        Returns:
            QualityMetrics object with detailed scores
        """
        with QUALITY_EVALUATION_TIME.time():
            # Calculate readability metrics
            readability = self._calculate_readability_metrics(content)

            # Calculate structure metrics
            structure = self._calculate_structure_metrics(content, target_format)

            # Calculate relevance metrics
            relevance = self._calculate_relevance_metrics(content, syllabus_text)

            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(content, target_format)

            # Calculate format compliance score
            format_compliance_score = self._calculate_format_compliance_score(
                content, target_format, metadata
            )

            # Create quality metrics object
            quality_metrics = QualityMetrics(
                readability=readability,
                structure=structure,
                relevance=relevance,
                engagement_score=engagement_score,
                format_compliance_score=format_compliance_score,
            )

            # Calculate overall score
            overall_score = quality_metrics.calculate_overall_score()
            QUALITY_SCORES.observe(overall_score)

            self.logger.info(f"Content quality evaluated: {overall_score:.3f}")

            return quality_metrics

    def _calculate_readability_metrics(self, content: str) -> ReadabilityMetrics:
        """Calculate readability metrics for content."""
        try:
            # Calculate readability scores
            flesch_ease = flesch_reading_ease(content)
            flesch_grade = flesch_kincaid_grade(content)
            ari = automated_readability_index(content)

            # Calculate sentence and word metrics
            sentences = re.split(r"[.!?]+", content)
            sentences = [s.strip() for s in sentences if s.strip()]

            words = content.split()

            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            avg_word_length = (
                sum(len(word) for word in words) / len(words) if words else 0
            )

            return ReadabilityMetrics(
                flesch_reading_ease=flesch_ease,
                flesch_kincaid_grade=flesch_grade,
                automated_readability_index=ari,
                avg_sentence_length=avg_sentence_length,
                avg_word_length=avg_word_length,
            )

        except Exception as e:
            self.logger.warning(f"Error calculating readability metrics: {str(e)}")
            return ReadabilityMetrics(
                flesch_reading_ease=50.0,
                flesch_kincaid_grade=10.0,
                automated_readability_index=10.0,
                avg_sentence_length=15.0,
                avg_word_length=5.0,
            )

    def _calculate_structure_metrics(
        self, content: str, target_format: str
    ) -> ContentStructureMetrics:
        """Calculate structure metrics for content."""
        # Check for introduction and conclusion
        content_lower = content.lower()
        has_introduction = any(
            keyword in content_lower[:200]
            for keyword in ["introduction", "welcome", "today we", "let's begin"]
        )
        has_conclusion = any(
            keyword in content_lower[-200:]
            for keyword in [
                "conclusion",
                "summary",
                "in summary",
                "to wrap up",
                "finally",
            ]
        )

        # Count sections and paragraphs
        sections = re.split(r"\n\s*#{1,3}\s+", content)
        section_count = len(sections) - 1  # Subtract 1 for content before first header

        paragraphs = re.split(r"\n\s*\n", content)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        paragraph_count = len(paragraphs)

        avg_paragraph_length = (
            sum(len(p.split()) for p in paragraphs) / paragraph_count
            if paragraph_count > 0
            else 0
        )

        # Check for transitions
        transition_words = [
            "however",
            "furthermore",
            "moreover",
            "additionally",
            "meanwhile",
            "consequently",
            "therefore",
            "thus",
            "next",
            "first",
            "second",
            "finally",
            "in addition",
            "on the other hand",
        ]
        has_transitions = any(word in content_lower for word in transition_words)

        # Simple logical flow score (based on transition presence and structure)
        logical_flow_score = 0.5
        if has_transitions:
            logical_flow_score += 0.3
        if section_count > 0:
            logical_flow_score += 0.2

        return ContentStructureMetrics(
            has_introduction=has_introduction,
            has_conclusion=has_conclusion,
            section_count=section_count,
            paragraph_count=paragraph_count,
            avg_paragraph_length=avg_paragraph_length,
            has_transitions=has_transitions,
            logical_flow_score=min(1.0, logical_flow_score),
        )

    def _calculate_relevance_metrics(
        self, content: str, syllabus_text: str
    ) -> ContentRelevanceMetrics:
        """Calculate relevance metrics for content."""
        # Extract keywords from syllabus
        syllabus_words = set(
            word.lower()
            for word in re.findall(r"\b\w+\b", syllabus_text)
            if len(word) > 3
        )

        content_words = set(
            word.lower() for word in re.findall(r"\b\w+\b", content) if len(word) > 3
        )

        # Calculate keyword coverage
        if syllabus_words:
            keyword_coverage = len(syllabus_words.intersection(content_words)) / len(
                syllabus_words
            )
        else:
            keyword_coverage = 0.0

        # Simple topic coherence (based on keyword repetition and density)
        topic_coherence = min(1.0, keyword_coverage * 1.5)

        # Placeholder scores (would need more sophisticated analysis)
        factual_accuracy_score = 0.8  # Would need fact-checking
        completeness_score = min(
            1.0, len(content.split()) / 500
        )  # Based on content length

        return ContentRelevanceMetrics(
            keyword_coverage=keyword_coverage,
            topic_coherence=topic_coherence,
            factual_accuracy_score=factual_accuracy_score,
            completeness_score=completeness_score,
        )

    def _calculate_engagement_score(self, content: str, target_format: str) -> float:
        """Calculate engagement score based on format-specific criteria."""
        engagement_score = 0.5  # Base score

        content_lower = content.lower()

        # Format-specific engagement factors
        if target_format == "podcast":
            # Check for conversational elements
            if any(
                phrase in content_lower
                for phrase in ["you might", "let's", "imagine", "think about"]
            ):
                engagement_score += 0.2

            # Check for questions
            question_count = content.count("?")
            engagement_score += min(0.2, question_count * 0.05)

        elif target_format == "guide":
            # Check for actionable language
            if any(
                phrase in content_lower
                for phrase in ["step", "how to", "you can", "try"]
            ):
                engagement_score += 0.2

            # Check for examples
            if any(
                phrase in content_lower
                for phrase in ["example", "for instance", "such as"]
            ):
                engagement_score += 0.1

        # General engagement factors
        if any(
            phrase in content_lower
            for phrase in ["interesting", "important", "key", "crucial"]
        ):
            engagement_score += 0.1

        return min(1.0, engagement_score)

    def _calculate_format_compliance_score(
        self,
        content: str,
        target_format: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Calculate format compliance score."""
        compliance_score = 0.5  # Base score

        word_count = len(content.split())

        # Format-specific compliance checks
        if target_format == "podcast":
            # Check for speaker notes or timing cues
            if "[" in content and "]" in content:
                compliance_score += 0.2

            # Check for appropriate length (aim for 150-200 words per minute)
            if metadata and "target_duration" in metadata:
                target_duration = metadata["target_duration"]
                expected_words = target_duration * 175  # 175 words per minute
                length_ratio = word_count / expected_words if expected_words > 0 else 0
                if 0.8 <= length_ratio <= 1.2:
                    compliance_score += 0.3
                elif 0.6 <= length_ratio <= 1.4:
                    compliance_score += 0.1

        elif target_format == "guide":
            # Check for structured sections
            if "#" in content or re.search(r"\d+\.", content):
                compliance_score += 0.2

            # Check for appropriate length
            if metadata and "target_pages" in metadata:
                target_pages = metadata["target_pages"]
                expected_words = target_pages * 250  # 250 words per page
                length_ratio = word_count / expected_words if expected_words > 0 else 0
                if 0.8 <= length_ratio <= 1.2:
                    compliance_score += 0.3
                elif 0.6 <= length_ratio <= 1.4:
                    compliance_score += 0.1

        elif target_format == "one_pager":
            # Check for concise format
            if 400 <= word_count <= 600:
                compliance_score += 0.3
            elif 300 <= word_count <= 700:
                compliance_score += 0.1

        return min(1.0, compliance_score)
