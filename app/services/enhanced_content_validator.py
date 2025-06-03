"""
Enhanced content validation pipeline with multi-layer verification.
Provides comprehensive validation including structure, semantics, factual consistency,
and redundancy detection for high-quality content generation.
"""

import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

from prometheus_client import REGISTRY, Counter, Histogram

from app.models.pydantic.content import GeneratedContent

# Prometheus metrics
try:
    CONTENT_VALIDATION_DURATION = REGISTRY._names_to_collectors[
        "content_validation_duration_seconds"
    ]
except KeyError:
    CONTENT_VALIDATION_DURATION = Histogram(
        "content_validation_duration_seconds",
        "Time spent on content validation",
        ["validation_stage"],
    )
try:
    VALIDATION_ERRORS = REGISTRY._names_to_collectors["content_validation_errors_total"]
except KeyError:
    VALIDATION_ERRORS = Counter(
        "content_validation_errors_total",
        "Total validation errors by type",
        ["error_type", "severity"],
    )
try:
    INPUT_QUALITY_SCORES = REGISTRY._names_to_collectors["input_quality_scores"]
except KeyError:
    INPUT_QUALITY_SCORES = Histogram(
        "input_quality_scores",
        "Distribution of input quality scores",
        buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    )


@dataclass
class ValidationIssue:
    """Validation issue with severity and details."""

    severity: str
    issue_type: str
    description: str
    location: str
    suggested_fix: str


@dataclass
class InputValidation:
    """Input validation results."""

    quality_score: float
    readability_score: float
    completeness_score: float
    clarity_issues: List[str]
    enhancement_suggestions: List[str]
    word_count: int
    estimated_complexity: str


@dataclass
class StructureValidation:
    """Structure validation results."""

    has_required_sections: bool
    missing_sections: List[str]
    section_balance_score: float
    logical_flow_score: float
    hierarchy_issues: List[str]
    format_compliance: Dict[str, Any]


@dataclass
class FactualValidation:
    """Factual validation results."""

    consistency_score: float
    contradictions_found: List[str]
    unsupported_claims: List[str]
    fact_density_score: float
    citation_coverage: float


@dataclass
class RedundancyReport:
    """Redundancy analysis results."""

    redundancy_score: float
    repeated_sections: List[str]
    verbose_passages: List[str]
    consolidation_opportunities: List[str]


@dataclass
class ValidationResult:
    """Complete validation result with all checks."""

    is_valid: bool
    overall_score: float
    input_validation: Optional[InputValidation] = None
    structure_validation: Optional[StructureValidation] = None
    factual_validation: Optional[FactualValidation] = None
    redundancy_report: Optional[RedundancyReport] = None
    issues: List[ValidationIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EnhancedContentValidator:
    """Comprehensive content validation pipeline."""

    def __init__(self):
        """Initialize the enhanced validator."""
        self.logger = logging.getLogger(__name__)

        # Thresholds
        self.quality_thresholds = {
            "input_quality": 0.6,
            "structure_compliance": 0.7,
            "factual_consistency": 0.75,
            "redundancy_maximum": 0.3,
        }

        # Common academic/educational phrases
        self.educational_indicators = {
            "learning_objectives": [
                "learn",
                "understand",
                "analyze",
                "evaluate",
                "create",
                "apply",
            ],
            "educational_structure": [
                "introduction",
                "overview",
                "summary",
                "conclusion",
                "key points",
            ],
            "engagement_phrases": [
                "consider",
                "think about",
                "explore",
                "examine",
                "investigate",
            ],
        }

    def validate_complete_pipeline(
        self,
        content: GeneratedContent,
        syllabus_text: str,
        target_format: str,
        strict_mode: bool = False,
    ) -> ValidationResult:
        """
        Run complete validation pipeline on generated content.

        Args:
            content: Generated content to validate
            syllabus_text: Original input syllabus
            target_format: Target format for content
            strict_mode: If True, apply stricter validation criteria

        Returns:
            Comprehensive validation result
        """
        start_time = datetime.utcnow()
        all_issues = []
        all_recommendations = []

        # Stage 1: Input Validation
        with CONTENT_VALIDATION_DURATION.labels(validation_stage="input").time():
            input_validation = self.pre_validate_input(syllabus_text)
            if (
                input_validation.quality_score
                < self.quality_thresholds["input_quality"]
            ):
                all_issues.append(
                    ValidationIssue(
                        severity="major",
                        issue_type="low_input_quality",
                        description=f"Input quality score ({input_validation.quality_score:.2f}) below threshold",
                        location="input",
                        suggested_fix="Improve input clarity and completeness",
                    )
                )
                all_recommendations.extend(input_validation.enhancement_suggestions)

        # Stage 2: Structure Validation
        with CONTENT_VALIDATION_DURATION.labels(validation_stage="structure").time():
            structure_validation = self.validate_structure(content, target_format)
            if not structure_validation.has_required_sections:
                all_issues.append(
                    ValidationIssue(
                        severity="critical",
                        issue_type="missing_required_sections",
                        description=f"Missing required sections: {', '.join(structure_validation.missing_sections)}",
                        location="structure",
                        suggested_fix="Ensure all required sections are generated",
                    )
                )

        # Stage 3: Semantic Validation
        with CONTENT_VALIDATION_DURATION.labels(validation_stage="semantic").time():
            semantic_validation = self.validate_semantic_consistency(content)
            if (
                semantic_validation.consistency_score
                < self.quality_thresholds["factual_consistency"]
            ):
                all_issues.append(
                    ValidationIssue(
                        severity="major",
                        issue_type="low_semantic_alignment",
                        description=f"Semantic alignment score ({semantic_validation.consistency_score:.2f}) below threshold",
                        location="semantic",
                        suggested_fix="Improve content alignment with outline topics",
                    )
                )
                all_recommendations.extend(semantic_validation.recommendations)

        # Stage 4: Factual Consistency
        with CONTENT_VALIDATION_DURATION.labels(validation_stage="factual").time():
            factual_validation = self.validate_factual_consistency(content)
            if (
                factual_validation.consistency_score
                < self.quality_thresholds["factual_consistency"]
            ):
                all_issues.append(
                    ValidationIssue(
                        severity="critical",
                        issue_type="factual_inconsistency",
                        description=f"Factual consistency issues detected (score: {factual_validation.consistency_score:.2f})",
                        location="facts",
                        suggested_fix="Review and correct contradictory statements",
                    )
                )

        # Stage 5: Redundancy Detection
        with CONTENT_VALIDATION_DURATION.labels(validation_stage="redundancy").time():
            redundancy_report = self.detect_redundancy(content)
            if (
                redundancy_report.redundancy_score
                > self.quality_thresholds["redundancy_maximum"]
            ):
                all_issues.append(
                    ValidationIssue(
                        severity="major",
                        issue_type="high_redundancy",
                        description=f"High redundancy detected (score: {redundancy_report.redundancy_score:.2f})",
                        location="content",
                        suggested_fix="Consolidate repetitive content",
                    )
                )
                all_recommendations.extend(
                    redundancy_report.consolidation_opportunities[:3]
                )

        # Calculate overall score
        component_scores = [
            input_validation.quality_score,
            1.0 if structure_validation.has_required_sections else 0.5,
            semantic_validation.consistency_score,
            factual_validation.consistency_score,
            1.0 - redundancy_report.redundancy_score,
        ]

        # Weight the scores (factual is more important)
        weights = [0.1, 0.1, 0.3, 0.3, 0.2]
        overall_score = sum(
            score * weight for score, weight in zip(component_scores, weights)
        )

        # Apply strict mode penalties
        if strict_mode:
            critical_issues = [
                issue for issue in all_issues if issue.severity == "critical"
            ]
            if critical_issues:
                overall_score *= 0.7  # 30% penalty for critical issues

        # Determine if content is valid
        is_valid = overall_score >= 0.7 and not any(
            issue.severity == "critical" for issue in all_issues
        )

        # Log validation errors
        for issue in all_issues:
            VALIDATION_ERRORS.labels(
                error_type=issue.issue_type, severity=issue.severity
            ).inc()

        # Create comprehensive result
        validation_result = ValidationResult(
            is_valid=is_valid,
            overall_score=overall_score,
            input_validation=input_validation,
            structure_validation=structure_validation,
            factual_validation=factual_validation,
            redundancy_report=redundancy_report,
            issues=all_issues,
            recommendations=all_recommendations,
            metadata={
                "validation_duration": (datetime.utcnow() - start_time).total_seconds(),
                "strict_mode": strict_mode,
                "target_format": target_format,
            },
        )

        return validation_result

    def pre_validate_input(self, syllabus_text: str) -> InputValidation:
        """
        Validate input quality before generation.

        Args:
            syllabus_text: Input text to validate

        Returns:
            Input validation results
        """
        # Basic metrics
        word_count = len(syllabus_text.split())
        sentence_count = len(re.split(r"[.!?]+", syllabus_text))

        # Readability check
        avg_sentence_length = word_count / max(sentence_count, 1)
        readability_score = self._calculate_readability_score(
            syllabus_text, avg_sentence_length
        )

        # Completeness check
        completeness_score = self._assess_input_completeness(syllabus_text)

        # Clarity issues
        clarity_issues = self._identify_clarity_issues(syllabus_text)

        # Enhancement suggestions
        enhancement_suggestions = self._generate_input_suggestions(
            syllabus_text, clarity_issues, completeness_score
        )

        # Estimate complexity
        complexity = self._estimate_complexity(syllabus_text, word_count)

        # Calculate overall quality score
        quality_score = readability_score * 0.3 + completeness_score * 0.7

        INPUT_QUALITY_SCORES.observe(quality_score)

        return InputValidation(
            quality_score=quality_score,
            readability_score=readability_score,
            completeness_score=completeness_score,
            clarity_issues=clarity_issues,
            enhancement_suggestions=enhancement_suggestions,
            word_count=word_count,
            estimated_complexity=complexity,
        )

    def _calculate_readability_score(
        self, text: str, avg_sentence_length: float
    ) -> float:
        """Calculate readability score for input text."""
        # Simple readability heuristics
        score = 1.0

        # Penalize very long sentences
        if avg_sentence_length > 30:
            score -= 0.2
        elif avg_sentence_length > 25:
            score -= 0.1

        # Penalize very short sentences
        if avg_sentence_length < 10:
            score -= 0.15

        # Check for proper punctuation
        if not re.search(r"[.!?]", text):
            score -= 0.3

        # Check for paragraph structure
        if "\n" in text or len(text) > 500:
            score += 0.1

        return max(0.0, min(1.0, score))

    def _assess_input_completeness(self, text: str) -> float:
        """Assess how complete the input is for content generation."""
        score = 0.0
        text_lower = text.lower()

        # Check for educational indicators
        for category, terms in self.educational_indicators.items():
            if any(term in text_lower for term in terms):
                score += 0.2

        # Check for structure indicators
        structure_keywords = ["topic", "objective", "goal", "cover", "include", "focus"]
        structure_matches = sum(1 for kw in structure_keywords if kw in text_lower)
        score += min(0.3, structure_matches * 0.1)

        # Check for specific content indicators
        if re.search(r"\d+\.", text):  # Numbered items
            score += 0.1
        if re.search(r"[-•]", text):  # Bullet points
            score += 0.1

        # Length bonus
        word_count = len(text.split())
        if word_count >= 100:
            score += 0.2
        elif word_count >= 50:
            score += 0.1

        return min(1.0, score)

    def _identify_clarity_issues(self, text: str) -> List[str]:
        """Identify clarity issues in input text."""
        issues = []

        # Check for vague language
        vague_terms = ["thing", "stuff", "various", "some", "many", "etc", "and so on"]
        vague_found = [term for term in vague_terms if term in text.lower()]
        if vague_found:
            issues.append(f"Vague language detected: {', '.join(vague_found[:3])}")

        # Check for incomplete sentences
        sentences = re.split(r"[.!?]+", text)
        incomplete = [
            s.strip() for s in sentences if s.strip() and len(s.strip().split()) < 3
        ]
        if incomplete:
            issues.append(f"Possible incomplete sentences: {len(incomplete)} found")

        # Check for excessive abbreviations
        abbrev_pattern = r"\b[A-Z]{2,}\b"
        abbreviations = re.findall(abbrev_pattern, text)
        if len(set(abbreviations)) > 5:
            issues.append("Many abbreviations used - consider spelling out for clarity")

        # Check for missing context
        if not re.search(
            r"(course|class|training|workshop|lesson|module)", text.lower()
        ):
            issues.append("No clear educational context provided")

        return issues

    def _generate_input_suggestions(
        self, text: str, clarity_issues: List[str], completeness_score: float
    ) -> List[str]:
        """Generate suggestions to improve input quality."""
        suggestions = []

        if completeness_score < 0.5:
            suggestions.append(
                "Add more detail about the learning objectives and key topics to cover"
            )

        if "vague language" in " ".join(clarity_issues).lower():
            suggestions.append(
                "Replace vague terms with specific concepts and examples"
            )

        word_count = len(text.split())
        if word_count < 50:
            suggestions.append(
                "Expand the syllabus with more details about scope, audience, and desired outcomes"
            )

        if not re.search(
            r"(beginner|intermediate|advanced|introductory)", text.lower()
        ):
            suggestions.append(
                "Specify the difficulty level or target audience for better content calibration"
            )

        return suggestions

    def _estimate_complexity(self, text: str, word_count: int) -> str:
        """Estimate the complexity level of the topic."""
        text_lower = text.lower()

        # Advanced indicators
        advanced_terms = [
            "advanced",
            "complex",
            "sophisticated",
            "theoretical",
            "research",
            "analysis",
            "synthesis",
            "evaluation",
            "methodology",
            "framework",
        ]
        advanced_count = sum(1 for term in advanced_terms if term in text_lower)

        # Basic indicators
        basic_terms = [
            "introduction",
            "basic",
            "fundamental",
            "beginner",
            "overview",
            "simple",
            "elementary",
            "foundation",
            "primer",
            "basics",
        ]
        basic_count = sum(1 for term in basic_terms if term in text_lower)

        # Determine complexity
        if advanced_count >= 3 or (advanced_count > basic_count and word_count > 100):
            return "high"
        elif basic_count >= 2 or (basic_count > advanced_count):
            return "low"
        else:
            return "medium"

    def validate_structure(
        self, content: GeneratedContent, target_format: str
    ) -> StructureValidation:
        """
        Validate content structure and organization.

        Args:
            content: Generated content to validate
            target_format: Expected format

        Returns:
            Structure validation results
        """
        # Define required sections by format
        format_requirements = {
            "podcast": ["introduction", "main_content", "conclusion"],
            "guide": ["overview", "detailed_content", "summary"],
            "one_pager": ["executive_summary", "key_takeaways", "main_content"],
            "comprehensive": ["outline", "podcast_script", "study_guide"],
        }

        # Check required sections
        required_sections = format_requirements.get(target_format, [])
        missing_sections = []

        # Check specific content types
        if "podcast" in required_sections or target_format == "podcast":
            if not content.podcast_script:
                missing_sections.append("podcast_script")

        if "guide" in required_sections or target_format == "guide":
            if not content.study_guide:
                missing_sections.append("study_guide")

        has_required = len(missing_sections) == 0

        # Calculate section balance
        section_lengths = self._get_section_lengths(content)
        section_balance_score = self._calculate_balance_score(section_lengths)

        # Check logical flow
        logical_flow_score = self._assess_logical_flow(content)

        # Identify hierarchy issues
        hierarchy_issues = self._check_hierarchy_issues(content)

        # Check format compliance
        format_compliance = self._check_format_compliance(content, target_format)

        return StructureValidation(
            has_required_sections=has_required,
            missing_sections=missing_sections,
            section_balance_score=section_balance_score,
            logical_flow_score=logical_flow_score,
            hierarchy_issues=hierarchy_issues,
            format_compliance=format_compliance,
        )

    def _get_section_lengths(self, content: GeneratedContent) -> Dict[str, int]:
        """Get word counts for each content section."""
        lengths = {}

        if content.content_outline:
            outline_text = " ".join(
                [
                    content.content_outline.title,
                    content.content_outline.overview,
                    " ".join(content.content_outline.learning_objectives),
                ]
            )
            lengths["outline"] = len(outline_text.split())

        if content.podcast_script:
            script_text = " ".join(
                [
                    content.podcast_script.introduction,
                    content.podcast_script.main_content,
                    content.podcast_script.conclusion,
                ]
            )
            lengths["podcast"] = len(script_text.split())

        if content.study_guide:
            guide_text = " ".join(
                [
                    content.study_guide.overview,
                    content.study_guide.detailed_content,
                    content.study_guide.summary,
                ]
            )
            lengths["guide"] = len(guide_text.split())

        return lengths

    def _calculate_balance_score(self, section_lengths: Dict[str, int]) -> float:
        """Calculate how well-balanced the content sections are."""
        if len(section_lengths) < 2:
            return 1.0

        values = list(section_lengths.values())
        mean_length = sum(values) / len(values)

        # Calculate coefficient of variation
        variance = sum((x - mean_length) ** 2 for x in values) / len(values)
        std_dev = variance**0.5
        cv = std_dev / mean_length if mean_length > 0 else 1.0

        # Convert to score (lower CV = better balance)
        balance_score = max(0, 1 - cv)

        return balance_score

    def _assess_logical_flow(self, content: GeneratedContent) -> float:
        """Assess the logical flow of content."""
        score = 0.0

        # Check if outline sections are reflected in other content
        if content.content_outline and content.study_guide:
            outline_sections = {
                s.title.lower() for s in content.content_outline.sections
            }
            guide_text = content.study_guide.detailed_content.lower()

            sections_mentioned = sum(
                1 for section in outline_sections if section in guide_text
            )

            if outline_sections:
                score += (sections_mentioned / len(outline_sections)) * 0.5

        # Check for transition indicators
        if content.podcast_script:
            script_text = content.podcast_script.main_content.lower()
            transition_words = [
                "first",
                "second",
                "next",
                "then",
                "finally",
                "moreover",
                "however",
            ]
            transitions_found = sum(
                1 for word in transition_words if word in script_text
            )
            score += min(0.5, transitions_found * 0.1)

        return score

    def _check_hierarchy_issues(self, content: GeneratedContent) -> List[str]:
        """Check for issues in content hierarchy."""
        issues = []

        if content.content_outline:
            # Check section numbering
            expected_numbers = list(range(1, len(content.content_outline.sections) + 1))
            actual_numbers = [
                s.section_number for s in content.content_outline.sections
            ]

            if actual_numbers != expected_numbers:
                issues.append("Section numbering is not sequential")

            # Check for empty sections
            for section in content.content_outline.sections:
                if not section.key_points:
                    issues.append(f"Section '{section.title}' has no key points")

        return issues

    def _check_format_compliance(
        self, content: GeneratedContent, target_format: str
    ) -> Dict[str, bool]:
        """Check compliance with format-specific requirements."""
        compliance = {}

        if target_format == "podcast" and content.podcast_script:
            # Check podcast-specific requirements
            compliance["has_introduction"] = bool(content.podcast_script.introduction)
            compliance["has_conclusion"] = bool(content.podcast_script.conclusion)
            compliance["appropriate_length"] = (
                1000 <= len(content.podcast_script.main_content) <= 10000
            )

        elif target_format == "guide" and content.study_guide:
            # Check guide-specific requirements
            compliance["has_overview"] = bool(content.study_guide.overview)
            compliance["has_key_concepts"] = len(content.study_guide.key_concepts) >= 5
            compliance["has_summary"] = bool(content.study_guide.summary)

        return compliance

    def validate_factual_consistency(
        self, content: GeneratedContent
    ) -> FactualValidation:
        """
        Validate factual consistency across all content pieces.

        Args:
            content: Generated content to validate

        Returns:
            Factual validation results
        """
        contradictions = []
        unsupported_claims = []

        # Extract all factual statements
        fact_sources = self._extract_factual_statements(content)

        # Check for contradictions
        for source1, facts1 in fact_sources.items():
            for source2, facts2 in fact_sources.items():
                if source1 < source2:  # Avoid duplicate comparisons
                    found_contradictions = self._find_contradictions(
                        facts1, facts2, source1, source2
                    )
                    contradictions.extend(found_contradictions)

        # Check for unsupported claims
        if content.content_outline:
            outline_facts = set(fact_sources.get("outline", []))
            for source, facts in fact_sources.items():
                if source != "outline":
                    for fact in facts:
                        if not any(self._facts_match(fact, of) for of in outline_facts):
                            unsupported_claims.append(f"{source}: {fact}")

        # Calculate fact density
        total_words = sum(
            len(facts) * 5
            for facts in fact_sources.values()  # Estimate 5 words per fact
        )
        total_content_words = self._count_total_words(content)
        fact_density_score = min(1.0, total_words / max(total_content_words, 1) * 10)

        # Calculate consistency score
        consistency_score = 1.0
        if contradictions:
            consistency_score -= len(contradictions) * 0.1
        if unsupported_claims:
            consistency_score -= len(unsupported_claims) * 0.05
        consistency_score = max(0.0, consistency_score)

        # Citation coverage (simplified - checks for reference indicators)
        citation_coverage = self._calculate_citation_coverage(content)

        return FactualValidation(
            consistency_score=consistency_score,
            contradictions_found=contradictions,
            unsupported_claims=unsupported_claims[:10],  # Limit to top 10
            fact_density_score=fact_density_score,
            citation_coverage=citation_coverage,
        )

    def _extract_factual_statements(
        self, content: GeneratedContent
    ) -> Dict[str, List[str]]:
        """Extract factual statements from content."""
        facts = {}

        # Extract from outline
        if content.content_outline:
            outline_facts = []
            for section in content.content_outline.sections:
                outline_facts.extend(section.key_points)
            facts["outline"] = outline_facts

        # Extract from study guide
        if content.study_guide:
            facts["guide"] = content.study_guide.key_concepts

        # Extract from FAQs
        if content.faqs:
            faq_facts = []
            for item in content.faqs.items:
                # Extract key statements from answers
                sentences = re.split(r"[.!?]+", item.answer)
                faq_facts.extend([s.strip() for s in sentences if len(s.strip()) > 20])
            facts["faqs"] = faq_facts[:20]  # Limit to prevent overwhelming

        return facts

    def _find_contradictions(
        self, facts1: List[str], facts2: List[str], source1: str, source2: str
    ) -> List[str]:
        """Find contradictory statements between fact sets."""
        contradictions = []

        for fact1 in facts1:
            for fact2 in facts2:
                if self._are_contradictory(fact1, fact2):
                    contradictions.append(
                        f"{source1}: {fact1} contradicts {source2}: {fact2}"
                    )

        return contradictions

    def _are_contradictory(self, fact1: str, fact2: str) -> bool:
        """Check if two facts are contradictory."""
        # Simplified contradiction detection
        fact1_lower = fact1.lower()
        fact2_lower = fact2.lower()

        # Check for explicit negation
        negation_pairs = [
            ("is", "is not"),
            ("are", "are not"),
            ("can", "cannot"),
            ("will", "will not"),
            ("does", "does not"),
        ]

        for positive, negative in negation_pairs:
            if positive in fact1_lower and negative in fact2_lower:
                # Check if they're about the same subject
                similarity = SequenceMatcher(None, fact1_lower, fact2_lower).ratio()
                if similarity > 0.6:
                    return True

        # Check for conflicting numbers
        numbers1 = re.findall(r"\d+", fact1)
        numbers2 = re.findall(r"\d+", fact2)
        if numbers1 and numbers2 and numbers1 != numbers2:
            similarity = SequenceMatcher(
                None,
                re.sub(r"\d+", "NUM", fact1_lower),
                re.sub(r"\d+", "NUM", fact2_lower),
            ).ratio()
            if similarity > 0.8:
                return True

        return False

    def _facts_match(self, fact1: str, fact2: str) -> bool:
        """Check if two facts are essentially the same."""
        similarity = SequenceMatcher(None, fact1.lower(), fact2.lower()).ratio()
        return similarity > 0.7

    def _count_total_words(self, content: GeneratedContent) -> int:
        """Count total words in all content."""
        total = 0

        if content.content_outline:
            total += len(content.content_outline.overview.split())

        if content.podcast_script:
            total += len(content.podcast_script.main_content.split())

        if content.study_guide:
            total += len(content.study_guide.detailed_content.split())

        return total

    def _calculate_citation_coverage(self, content: GeneratedContent) -> float:
        """Calculate how well content is cited/referenced."""
        citation_indicators = [
            "according to",
            "research shows",
            "studies indicate",
            "as mentioned",
            "based on",
            "derived from",
        ]

        citation_count = 0
        content_pieces = 0

        if content.study_guide:
            guide_text = content.study_guide.detailed_content.lower()
            citation_count += sum(1 for ind in citation_indicators if ind in guide_text)
            content_pieces += 1

        if content.detailed_reading_material:
            reading_text = " ".join(
                [
                    content.detailed_reading_material.introduction,
                    content.detailed_reading_material.conclusion,
                ]
            ).lower()
            citation_count += sum(
                1 for ind in citation_indicators if ind in reading_text
            )
            content_pieces += 1

        # Calculate coverage score
        if content_pieces > 0:
            avg_citations = citation_count / content_pieces
            # Normalize to 0-1 scale (assume 3 citations per piece is good)
            return min(1.0, avg_citations / 3.0)
        return 0.0

    def detect_redundancy(self, content: GeneratedContent) -> RedundancyReport:
        """
        Detect redundant content and repetition.

        Args:
            content: Generated content to analyze

        Returns:
            Redundancy report with findings
        """
        repeated_sections = []
        verbose_passages = []
        consolidation_opportunities = []

        # Collect all text segments
        text_segments = self._collect_text_segments(content)

        # Find repeated content
        for i, (loc1, text1) in enumerate(text_segments):
            for j, (loc2, text2) in enumerate(text_segments[i + 1 :], i + 1):
                similarity = self._calculate_text_similarity(text1, text2)

                if similarity > 0.8 and len(text1.split()) > 20:
                    repeated_sections.append(f"{loc1}: {text1[:100]}...")

        # Detect verbose passages
        for location, text in text_segments:
            verbosity_score = self._calculate_verbosity(text)
            if verbosity_score > 0.7:
                verbose_passages.append(f"{location}: {text[:100]}...")

        # Identify consolidation opportunities
        topic_clusters = self._cluster_by_topic(text_segments)
        for topic, locations in topic_clusters.items():
            if len(locations) > 2:
                consolidation_opportunities.append(
                    f"Topic '{topic}' is discussed in {len(locations)} separate places. "
                    f"Consider consolidating in: {', '.join(locations[:3])}"
                )

        # Calculate overall redundancy score
        total_segments = len(text_segments)
        redundancy_score = 0.0

        if total_segments > 0:
            repetition_penalty = len(repeated_sections) / total_segments
            verbosity_penalty = len(verbose_passages) / total_segments
            consolidation_penalty = len(consolidation_opportunities) / max(
                len(topic_clusters), 1
            )

            redundancy_score = min(
                1.0,
                (
                    repetition_penalty * 0.5
                    + verbosity_penalty * 0.3
                    + consolidation_penalty * 0.2
                ),
            )

        return RedundancyReport(
            redundancy_score=redundancy_score,
            repeated_sections=repeated_sections[:5],  # Limit to top 5
            verbose_passages=verbose_passages[:5],
            consolidation_opportunities=consolidation_opportunities[:3],
        )

    def _collect_text_segments(
        self, content: GeneratedContent
    ) -> List[Tuple[str, str]]:
        """Collect all text segments with their locations."""
        segments = []

        if content.content_outline:
            for i, section in enumerate(content.content_outline.sections):
                segments.append((f"outline_section_{i+1}", section.description))

        if content.podcast_script:
            segments.extend(
                [
                    ("podcast_intro", content.podcast_script.introduction),
                    ("podcast_main", content.podcast_script.main_content),
                    ("podcast_conclusion", content.podcast_script.conclusion),
                ]
            )

        if content.study_guide:
            segments.extend(
                [
                    ("guide_overview", content.study_guide.overview),
                    ("guide_content", content.study_guide.detailed_content),
                    ("guide_summary", content.study_guide.summary),
                ]
            )

        if content.faqs:
            for i, item in enumerate(content.faqs.items[:5]):  # Limit to 5 FAQs
                segments.append((f"faq_{i+1}", f"{item.question} {item.answer}"))

        return segments

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text segments."""
        # Normalize texts
        text1_lower = text1.lower().strip()
        text2_lower = text2.lower().strip()

        # Quick check for identical texts
        if text1_lower == text2_lower:
            return 1.0

        # Use SequenceMatcher for similarity
        similarity = SequenceMatcher(None, text1_lower, text2_lower).ratio()

        # Boost similarity if key phrases match
        words1 = set(text1_lower.split())
        words2 = set(text2_lower.split())

        if len(words1) > 0 and len(words2) > 0:
            word_overlap = len(words1.intersection(words2)) / min(
                len(words1), len(words2)
            )
            similarity = (similarity + word_overlap) / 2

        return similarity

    def _calculate_verbosity(self, text: str) -> float:
        """Calculate verbosity score for text."""
        words = text.split()
        word_count = len(words)

        if word_count < 50:
            return 0.0

        # Check for filler words and phrases
        filler_words = [
            "very",
            "really",
            "actually",
            "basically",
            "essentially",
            "in fact",
            "as a matter of fact",
            "to be honest",
            "kind of",
            "sort of",
            "you know",
            "I mean",
        ]

        filler_count = sum(1 for word in words if word.lower() in filler_words)

        # Check for redundant phrases
        redundant_patterns = [
            r"\b(\w+)\s+\1\b",  # Repeated words
            r"in order to",  # Could be just "to"
            r"due to the fact that",  # Could be "because"
            r"at this point in time",  # Could be "now"
        ]

        redundancy_count = 0
        for pattern in redundant_patterns:
            redundancy_count += len(re.findall(pattern, text.lower()))

        # Calculate average sentence length
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        avg_sentence_length = word_count / max(len(sentences), 1)

        # Verbosity score based on multiple factors
        filler_ratio = filler_count / word_count
        redundancy_ratio = redundancy_count / word_count
        length_penalty = min(
            1.0, avg_sentence_length / 40
        )  # Penalize very long sentences

        verbosity_score = (
            filler_ratio * 0.4 + redundancy_ratio * 0.3 + length_penalty * 0.3
        )

        return min(1.0, verbosity_score)

    def _cluster_by_topic(
        self, text_segments: List[Tuple[str, str]]
    ) -> Dict[str, List[str]]:
        """Cluster text segments by topic."""
        topic_clusters = defaultdict(list)

        # Extract key terms from each segment
        segment_terms = {}
        for location, text in text_segments:
            # Simple term extraction - top nouns and noun phrases
            words = re.findall(r"\b[A-Za-z]{4,}\b", text.lower())

            # Filter common words
            stopwords = {
                "this",
                "that",
                "these",
                "those",
                "with",
                "from",
                "about",
                "into",
                "through",
                "during",
                "before",
                "after",
                "above",
                "below",
                "between",
                "under",
                "again",
                "further",
                "then",
                "once",
                "here",
                "there",
                "when",
                "where",
                "which",
                "while",
            }

            key_terms = [w for w in words if w not in stopwords]

            # Get most common terms
            term_counts = Counter(key_terms)
            top_terms = [term for term, count in term_counts.most_common(5)]

            segment_terms[location] = set(top_terms)

            # Assign to clusters based on shared terms
            for term in top_terms:
                if term_counts[term] >= 2:  # Term appears multiple times
                    topic_clusters[term].append(location)

        # Merge similar clusters
        merged_clusters = {}
        processed = set()

        for topic1, locations1 in topic_clusters.items():
            if topic1 in processed:
                continue

            merged_locations = set(locations1)

            for topic2, locations2 in topic_clusters.items():
                if topic2 != topic1 and topic2 not in processed:
                    # Check if topics are related
                    if any(loc in locations1 for loc in locations2):
                        merged_locations.update(locations2)
                        processed.add(topic2)

            if len(merged_locations) > 1:
                merged_clusters[topic1] = list(merged_locations)
            processed.add(topic1)

        return merged_clusters
