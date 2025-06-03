"""
Comprehensive content validator for ensuring content quality and consistency.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel

from app.models.pydantic.content import (
    ContentOutline,
    DetailedReadingMaterial,
    FAQCollection,
    FlashcardCollection,
    GeneratedContent,
    OnePagerSummary,
    PodcastScript,
    ReadingGuideQuestions,
    StudyGuide,
)
from app.services.enhanced_content_validator import (  # For structural/basic checks
    EnhancedContentValidator,
)

# Placeholder for educational quality specific validator
# from app.services.educational_quality_validator import EducationalQualityValidator

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of content validation."""

    is_valid: bool
    issues: List[str]
    metadata: Dict[str, Any]


@dataclass
class ValidationStageResult:
    """Result of a single validation stage."""

    passed: bool
    stage_name: str
    score: float
    issues_found: List[str]
    improvement_suggestion: Optional[str] = None


@dataclass
class ComprehensiveValidationReport:
    """Complete validation report with all stages."""

    overall_passed: bool
    overall_score: float
    stage_results: List[ValidationStageResult]
    actionable_feedback: List[str]
    refinement_prompts: List[str]


class ComprehensiveContentValidator:
    """Validator for ensuring content quality and consistency."""

    def __init__(self):
        self.structural_validator = EnhancedContentValidator()
        # TODO: Define thresholds and weights for scoring
        self.quality_thresholds = {
            "default": 0.7,
            "ContentOutline": 0.8,
            "PodcastScript": 0.75,
        }
        self.score_weights = {
            "structural": 0.3,
            "completeness": 0.2,
            "coherence": 0.3,
            "educational_value": 0.2,
        }

    def validate_content(self, content: BaseModel) -> tuple[bool, list[str]]:
        """Validate content against quality standards."""
        logger.debug(
            f"Running completeness validation for {content.__class__.__name__}..."
        )
        issues = []

        # Example for ContentOutline (adapt for others)
        if isinstance(content, ContentOutline):
            if not (10 <= len(content.title) <= 200):
                issues.append("Title length invalid.")
            if not (50 <= len(content.overview) <= 1000):
                issues.append("Overview length invalid.")
            if not (3 <= len(content.learning_objectives) <= 10):
                issues.append("Incorrect number of learning objectives.")
            for lo in content.learning_objectives:
                if len(lo) < 15:
                    issues.append(f"Learning objective too short: '{lo[:20]}...'")
            if not (3 <= len(content.sections) <= 15):
                issues.append("Incorrect number of sections.")
            for sec in content.sections:
                if not (5 <= len(sec.title) <= 200):
                    issues.append(
                        f"Section title '{sec.title[:20]}...' length invalid."
                    )
                if not (20 <= len(sec.description) <= 1000):
                    issues.append(
                        f"Section description for '{sec.title[:20]}...' length invalid."
                    )
                for kp in sec.key_points:
                    if len(kp.strip()) < 10:
                        issues.append(
                            f"Key point '{kp[:20]}...' in section '{sec.title[:20]}' is too short."
                        )
                if len(sec.key_points) > 10:
                    issues.append(
                        f"Too many key points in section '{sec.title[:20]}'. Max 10."
                    )

        elif isinstance(content, PodcastScript):
            if not (10 <= len(content.title) <= 200):
                issues.append("PodcastScript title length invalid.")
            if not (100 <= len(content.introduction) <= 2000):
                issues.append("PodcastScript introduction length invalid.")
            if not (800 <= len(content.main_content) <= 10000):
                issues.append("PodcastScript main_content length invalid.")
            if not (100 <= len(content.conclusion) <= 1000):
                issues.append("PodcastScript conclusion length invalid.")
            total_len = (
                len(content.introduction)
                + len(content.main_content)
                + len(content.conclusion)
            )
            if not (1000 <= total_len <= 12000):
                issues.append(
                    f"PodcastScript total content length ({total_len}) out of range 1000-12000."
                )

        elif isinstance(content, StudyGuide):
            if not (10 <= len(content.title) <= 200):
                issues.append("StudyGuide title length invalid.")
            if not (100 <= len(content.overview) <= 1000):
                issues.append("StudyGuide overview length invalid.")
            if not (5 <= len(content.key_concepts) <= 20):
                issues.append("StudyGuide incorrect number of key concepts.")
            if not (500 <= len(content.detailed_content) <= 8000):
                issues.append("StudyGuide detailed_content length invalid.")
            if not (100 <= len(content.summary) <= 1000):
                issues.append("StudyGuide summary length invalid.")

        elif isinstance(content, OnePagerSummary):
            if not (10 <= len(content.title) <= 200):
                issues.append("OnePagerSummary title length invalid.")
            if not (100 <= len(content.executive_summary) <= 500):
                issues.append("OnePagerSummary executive_summary length invalid.")
            if not (3 <= len(content.key_takeaways) <= 7):
                issues.append("OnePagerSummary incorrect number of key takeaways.")
            for kt in content.key_takeaways:
                if len(kt.strip()) < 20:
                    issues.append(f"Key takeaway '{kt[:20]}...' too short.")
            if not (200 <= len(content.main_content) <= 1500):
                issues.append("OnePagerSummary main_content length invalid.")

        elif isinstance(content, DetailedReadingMaterial):
            if not (10 <= len(content.title) <= 200):
                issues.append("DetailedReadingMaterial title length invalid.")
            if not (200 <= len(content.introduction) <= 1000):
                issues.append("DetailedReadingMaterial introduction length invalid.")
            if not (3 <= len(content.sections) <= 10):
                issues.append("DetailedReadingMaterial incorrect number of sections.")
            for sec in content.sections:
                if not sec.get("title") or len(sec["title"]) < 10:
                    issues.append(
                        f"DRM Section title '{sec.get('title', '')[:20]}...' length invalid."
                    )
                if not sec.get("content") or len(sec["content"]) < 200:
                    issues.append(
                        f"DRM Section content for '{sec.get('title', '')[:20]}...' length invalid."
                    )
            if not (200 <= len(content.conclusion) <= 1000):
                issues.append("DetailedReadingMaterial conclusion length invalid.")

        elif isinstance(content, FAQCollection):
            if not (5 <= len(content.items) <= 15):
                issues.append("FAQCollection incorrect number of items.")
            for item in content.items:
                if not (10 <= len(item.question) <= 300) or not item.question.endswith(
                    "?"
                ):
                    issues.append(f"FAQ question '{item.question[:30]}...' invalid.")
                if not (20 <= len(item.answer) <= 1000):
                    issues.append(
                        f"FAQ answer for '{item.question[:30]}...' length invalid."
                    )

        elif isinstance(content, FlashcardCollection):
            if not (10 <= len(content.items) <= 25):
                issues.append("FlashcardCollection incorrect number of items.")
            for item in content.items:
                if not (2 <= len(item.term) <= 100):
                    issues.append(
                        f"Flashcard term '{item.term[:30]}...' length invalid."
                    )
                if not (10 <= len(item.definition) <= 500):
                    issues.append(
                        f"Flashcard definition for '{item.term[:30]}...' length invalid."
                    )
                if item.difficulty and item.difficulty not in [
                    "easy",
                    "medium",
                    "hard",
                ]:
                    issues.append(f"Flashcard difficulty '{item.difficulty}' invalid.")

        elif isinstance(content, ReadingGuideQuestions):
            if not (5 <= len(content.questions) <= 15):
                issues.append("ReadingGuideQuestions incorrect number of questions.")
            for q_text in content.questions:
                if len(q_text.strip()) < 15 or not q_text.strip().endswith("?"):
                    issues.append(f"Reading guide question '{q_text[:30]}...' invalid.")

        passed = not issues
        return passed, issues

    def _validate_structure(
        self, content: BaseModel, content_type_name: str
    ) -> ValidationStageResult:
        """Validates Pydantic model structure and basic field constraints."""
        logger.debug(f"Running structural validation for {content_type_name}...")
        # EnhancedContentValidator's validate_content returns a dict
        # We need to adapt it or use its methods more directly.
        # For now, let's assume a simplified pass/fail based on Pydantic validation.
        try:
            # Re-validate to be sure, or trust it's already validated if coming from _call_generative_model
            # content.model_validate(content.model_dump()) # This re-validates
            # For this stage, we assume the object `content` is already a parsed Pydantic model.
            # The main check is if it *exists* and is of the right type.
            # More detailed field checks (length, count) are part of completeness.

            # Let's use the existing validator's logic if possible
            validation_dict = self.structural_validator.validate_content(
                content, content_type_name.lower().replace(" ", "_")
            )
            passed = validation_dict.get("is_valid", False)
            score = validation_dict.get(
                "overall_score", 0.0 if not passed else 1.0
            )  # structural_validator score
            issues = validation_dict.get("validation_errors", [])

            return ValidationStageResult(
                passed=passed,
                stage_name="Structural Validation",
                score=score,
                issues_found=[str(issue) for issue in issues],
                improvement_suggestion="Ensure the content strictly adheres to the defined JSON schema and all field constraints (type, format)."
                if not passed
                else None,
            )
        except Exception as e:
            logger.error(
                f"Error during structural validation of {content_type_name}: {e}"
            )
            return ValidationStageResult(
                passed=False,
                stage_name="Structural Validation",
                score=0.0,
                issues_found=[f"Critical structural error: {str(e)}"],
                improvement_suggestion="The content has critical structural errors preventing basic parsing. Regenerate strictly following the schema.",
            )

    def _validate_completeness(
        self, content: BaseModel, content_type_name: str
    ) -> ValidationStageResult:
        """Validates if all required fields are present and meet basic quantitative criteria (length, count)."""
        logger.debug(f"Running completeness validation for {content_type_name}...")
        issues = []

        # Example for ContentOutline (adapt for others)
        if isinstance(content, ContentOutline):
            if not (10 <= len(content.title) <= 200):
                issues.append("Title length invalid.")
            if not (50 <= len(content.overview) <= 1000):
                issues.append("Overview length invalid.")
            if not (3 <= len(content.learning_objectives) <= 10):
                issues.append("Incorrect number of learning objectives.")
            for lo in content.learning_objectives:
                if len(lo) < 15:
                    issues.append(f"Learning objective too short: '{lo[:20]}...'")
            if not (3 <= len(content.sections) <= 15):
                issues.append("Incorrect number of sections.")
            for sec in content.sections:
                if not (5 <= len(sec.title) <= 200):
                    issues.append(
                        f"Section title '{sec.title[:20]}...' length invalid."
                    )
                if not (20 <= len(sec.description) <= 1000):
                    issues.append(
                        f"Section description for '{sec.title[:20]}...' length invalid."
                    )
                for kp in sec.key_points:
                    if len(kp.strip()) < 10:
                        issues.append(
                            f"Key point '{kp[:20]}...' in section '{sec.title[:20]}' is too short."
                        )
                if len(sec.key_points) > 10:
                    issues.append(
                        f"Too many key points in section '{sec.title[:20]}'. Max 10."
                    )

        elif isinstance(content, PodcastScript):
            if not (10 <= len(content.title) <= 200):
                issues.append("PodcastScript title length invalid.")
            if not (100 <= len(content.introduction) <= 2000):
                issues.append("PodcastScript introduction length invalid.")
            if not (800 <= len(content.main_content) <= 10000):
                issues.append("PodcastScript main_content length invalid.")
            if not (100 <= len(content.conclusion) <= 1000):
                issues.append("PodcastScript conclusion length invalid.")
            total_len = (
                len(content.introduction)
                + len(content.main_content)
                + len(content.conclusion)
            )
            if not (1000 <= total_len <= 12000):
                issues.append(
                    f"PodcastScript total content length ({total_len}) out of range 1000-12000."
                )

        elif isinstance(content, StudyGuide):
            if not (10 <= len(content.title) <= 200):
                issues.append("StudyGuide title length invalid.")
            if not (100 <= len(content.overview) <= 1000):
                issues.append("StudyGuide overview length invalid.")
            if not (5 <= len(content.key_concepts) <= 20):
                issues.append("StudyGuide incorrect number of key concepts.")
            if not (500 <= len(content.detailed_content) <= 8000):
                issues.append("StudyGuide detailed_content length invalid.")
            if not (100 <= len(content.summary) <= 1000):
                issues.append("StudyGuide summary length invalid.")

        elif isinstance(content, OnePagerSummary):
            if not (10 <= len(content.title) <= 200):
                issues.append("OnePagerSummary title length invalid.")
            if not (100 <= len(content.executive_summary) <= 500):
                issues.append("OnePagerSummary executive_summary length invalid.")
            if not (3 <= len(content.key_takeaways) <= 7):
                issues.append("OnePagerSummary incorrect number of key takeaways.")
            for kt in content.key_takeaways:
                if len(kt.strip()) < 20:
                    issues.append(f"Key takeaway '{kt[:20]}...' too short.")
            if not (200 <= len(content.main_content) <= 1500):
                issues.append("OnePagerSummary main_content length invalid.")

        elif isinstance(content, DetailedReadingMaterial):
            if not (10 <= len(content.title) <= 200):
                issues.append("DetailedReadingMaterial title length invalid.")
            if not (200 <= len(content.introduction) <= 1000):
                issues.append("DetailedReadingMaterial introduction length invalid.")
            if not (3 <= len(content.sections) <= 10):
                issues.append("DetailedReadingMaterial incorrect number of sections.")
            for sec in content.sections:
                if not sec.get("title") or len(sec["title"]) < 10:
                    issues.append(
                        f"DRM Section title '{sec.get('title', '')[:20]}...' length invalid."
                    )
                if not sec.get("content") or len(sec["content"]) < 200:
                    issues.append(
                        f"DRM Section content for '{sec.get('title', '')[:20]}...' length invalid."
                    )
            if not (200 <= len(content.conclusion) <= 1000):
                issues.append("DetailedReadingMaterial conclusion length invalid.")

        elif isinstance(content, FAQCollection):
            if not (5 <= len(content.items) <= 15):
                issues.append("FAQCollection incorrect number of items.")
            for item in content.items:
                if not (10 <= len(item.question) <= 300) or not item.question.endswith(
                    "?"
                ):
                    issues.append(f"FAQ question '{item.question[:30]}...' invalid.")
                if not (20 <= len(item.answer) <= 1000):
                    issues.append(
                        f"FAQ answer for '{item.question[:30]}...' length invalid."
                    )

        elif isinstance(content, FlashcardCollection):
            if not (10 <= len(content.items) <= 25):
                issues.append("FlashcardCollection incorrect number of items.")
            for item in content.items:
                if not (2 <= len(item.term) <= 100):
                    issues.append(
                        f"Flashcard term '{item.term[:30]}...' length invalid."
                    )
                if not (10 <= len(item.definition) <= 500):
                    issues.append(
                        f"Flashcard definition for '{item.term[:30]}...' length invalid."
                    )
                if item.difficulty and item.difficulty not in [
                    "easy",
                    "medium",
                    "hard",
                ]:
                    issues.append(f"Flashcard difficulty '{item.difficulty}' invalid.")

        elif isinstance(content, ReadingGuideQuestions):
            if not (5 <= len(content.questions) <= 15):
                issues.append("ReadingGuideQuestions incorrect number of questions.")
            for q_text in content.questions:
                if len(q_text.strip()) < 15 or not q_text.strip().endswith("?"):
                    issues.append(f"Reading guide question '{q_text[:30]}...' invalid.")

        passed = not issues
        # Simple scoring: 1.0 if no issues, 0.5 if issues exist but object is usable, 0.0 if critical.
        current_score = 1.0 if passed else 0.5

        return ValidationStageResult(
            passed=passed,
            stage_name="Completeness Validation",
            score=current_score,  # More nuanced scoring can be added
            issues_found=issues,
            improvement_suggestion="Ensure all fields are populated according to specified length and count constraints. Review missing or incomplete sections."
            if not passed
            else None,
        )

    def _validate_coherence(
        self, content: GeneratedContent, content_type_name: str
    ) -> ValidationStageResult:
        """Validates semantic consistency and relevance to the outline/syllabus."""
        logger.debug(f"Running coherence validation for {content_type_name}...")

        if not content.content_outline:
            return ValidationStageResult(
                passed=False,
                stage_name="Coherence Validation",
                score=0.0,
                issues_found=["Master outline missing, cannot assess coherence."],
            )

        # Extract key topics and concepts from outline
        outline_topics = self._extract_outline_topics(content.content_outline)
        outline_text = self._outline_to_text(content.content_outline)

        # Validate each content type
        validation_results = {}
        total_score = 0.0
        total_items = 0
        all_issues = []

        # Validate each content type against the outline
        for content_type, content_instance in [
            ("podcast_script", content.podcast_script),
            ("study_guide", content.study_guide),
            ("one_pager_summary", content.one_pager_summary),
            ("detailed_reading_material", content.detailed_reading_material),
            ("faqs", content.faqs),
            ("flashcards", content.flashcards),
            ("reading_guide_questions", content.reading_guide_questions),
        ]:
            if content_instance:
                score, issues = self._validate_content_against_outline(
                    content_instance, outline_topics, outline_text, content_type
                )
                validation_results[content_type] = {"score": score, "issues": issues}
                total_score += score
                total_items += 1
                all_issues.extend(issues)

        # Calculate overall coherence score
        overall_score = total_score / total_items if total_items > 0 else 0.0
        passed = overall_score >= self.quality_thresholds.get("default", 0.7)

        return ValidationStageResult(
            passed=passed,
            stage_name="Coherence and Relevance Validation",
            score=overall_score,
            issues_found=all_issues,
            improvement_suggestion="Improve relevance to the master outline. Ensure all generated parts directly address the outline's topics and maintain logical flow."
            if not passed
            else None,
        )

    def _extract_outline_topics(self, outline: ContentOutline) -> List[str]:
        """Extract key topics from the content outline."""
        topics = []

        # Extract main topics from outline
        if outline.main_topics:
            topics.extend([topic.title for topic in outline.main_topics])

        # Extract subtopics
        for topic in outline.main_topics or []:
            if topic.subtopics:
                topics.extend([subtopic.title for subtopic in topic.subtopics])

        return topics

    def _outline_to_text(self, outline: ContentOutline) -> str:
        """Convert outline to text for semantic comparison."""
        text_parts = []

        if outline.title:
            text_parts.append(outline.title)

        if outline.description:
            text_parts.append(outline.description)

        if outline.main_topics:
            for topic in outline.main_topics:
                text_parts.append(topic.title)
                if topic.description:
                    text_parts.append(topic.description)

                if topic.subtopics:
                    for subtopic in topic.subtopics:
                        text_parts.append(subtopic.title)
                        if subtopic.description:
                            text_parts.append(subtopic.description)

        return " ".join(text_parts)

    def _validate_content_against_outline(
        self,
        content: Any,
        outline_topics: List[str],
        outline_text: str,
        content_type: str,
    ) -> Tuple[float, List[str]]:
        """Validate a content piece against the outline."""
        issues = []
        score = 0.0

        # Extract content text based on type
        content_text = self._extract_content_text(content, content_type)
        if not content_text:
            return 0.0, ["No content text found"]

        # Check topic coverage
        topic_coverage = self._calculate_topic_coverage(content_text, outline_topics)
        score += topic_coverage * 0.6  # 60% weight for topic coverage

        # Check semantic similarity
        semantic_similarity = self._calculate_semantic_similarity(
            content_text, outline_text
        )
        score += semantic_similarity * 0.4  # 40% weight for semantic similarity

        # Generate issues if score is low
        if topic_coverage < 0.6:
            issues.append(f"Low topic coverage in {content_type}")
        if semantic_similarity < 0.6:
            issues.append(f"Low semantic alignment in {content_type}")

        return score, issues

    def _extract_content_text(self, content: Any, content_type: str) -> str:
        """Extract text content based on content type."""
        if content_type == "podcast_script":
            return content.script if hasattr(content, "script") else ""
        elif content_type == "study_guide":
            return content.content if hasattr(content, "content") else ""
        elif content_type == "one_pager_summary":
            return content.summary if hasattr(content, "summary") else ""
        elif content_type == "detailed_reading_material":
            return content.content if hasattr(content, "content") else ""
        elif content_type == "faqs":
            return (
                " ".join([f"{q.question} {q.answer}" for q in content.questions])
                if hasattr(content, "questions")
                else ""
            )
        elif content_type == "flashcards":
            return (
                " ".join([f"{c.front} {c.back}" for c in content.cards])
                if hasattr(content, "cards")
                else ""
            )
        elif content_type == "reading_guide_questions":
            return (
                " ".join([q.question for q in content.questions])
                if hasattr(content, "questions")
                else ""
            )
        return ""

    def _calculate_topic_coverage(self, content_text: str, topics: List[str]) -> float:
        """Calculate how well the content covers the outline topics."""
        if not topics:
            return 0.0

        covered_topics = 0
        for topic in topics:
            if topic.lower() in content_text.lower():
                covered_topics += 1

        return covered_topics / len(topics)

    def _calculate_semantic_similarity(
        self, content_text: str, outline_text: str
    ) -> float:
        """Calculate semantic similarity between content and outline."""
        # Simple implementation using word overlap
        # TODO: Implement more sophisticated semantic similarity using embeddings
        content_words = set(content_text.lower().split())
        outline_words = set(outline_text.lower().split())

        if not content_words or not outline_words:
            return 0.0

        overlap = len(content_words.intersection(outline_words))
        total = len(content_words.union(outline_words))

        return overlap / total if total > 0 else 0.0

    def _validate_educational_value(
        self, content: BaseModel, content_type_name: str
    ) -> ValidationStageResult:
        """Placeholder for validating educational quality, accuracy, engagement."""
        logger.debug(
            f"Running educational value validation for {content_type_name} (Placeholder)..."
        )
        # TODO: Implement actual educational quality checks.
        # This could involve:
        # - Checking for clarity of explanations.
        # - Presence of examples (if applicable).
        # - Appropriateness of terminology for target audience.
        # - Factual accuracy checks (potentially with another LLM call or knowledge base).
        # - Engagement factors (e.g., for podcast scripts, study guides).
        score = 0.75  # Placeholder score
        passed = score >= 0.6  # Placeholder threshold
        issues = (
            []
            if passed
            else ["Content may lack depth or engagement. Examples could be improved."]
        )
        return ValidationStageResult(
            passed=passed,
            stage_name="Educational Value Validation",
            score=score,  # Placeholder
            issues_found=issues,
            improvement_suggestion="Enhance educational impact: provide clearer explanations, more relevant examples, and ensure factual accuracy. Consider engagement strategies."
            if not passed
            else None,
        )

    def _calculate_composite_score(
        self, stage_results: List[ValidationStageResult]
    ) -> float:
        """Calculates a weighted composite score from individual stage scores."""
        total_score = 0.0
        total_weight = 0.0

        name_to_weight_key = {
            "Structural Validation": "structural",
            "Completeness Validation": "completeness",
            "Coherence and Relevance Validation": "coherence",
            "Educational Value Validation": "educational_value",
        }

        for result in stage_results:
            weight_key = name_to_weight_key.get(result.stage_name)
            if weight_key and result.score is not None:
                weight = self.score_weights.get(
                    weight_key, 0.1
                )  # Default weight if not specified
                total_score += result.score * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def _generate_refinement_prompts(self, actionable_feedback: List[str]) -> List[str]:
        """Generates high-level prompts for LLM-based refinement based on feedback."""
        # This is a simplified version. A more advanced one would tailor prompts per issue.
        if not actionable_feedback:
            return []

        combined_feedback = " ".join(actionable_feedback)
        refinement_prompt = (
            f"The previously generated content has issues: {combined_feedback}. "
            "Please regenerate the content, specifically addressing these points. "
            "Focus on improving accuracy, completeness, adherence to schema, and relevance to the original request. "
            "Ensure all constraints and quality checks mentioned in the original prompt are met."
        )
        return [refinement_prompt]

    def validate_content_pipeline(
        self,
        generated_content: GeneratedContent,  # The whole collection of generated parts
        original_syllabus_text: Optional[str] = None,  # For context if needed
        target_format: Optional[str] = None,  # For context if needed
    ) -> ComprehensiveValidationReport:
        """
        Runs the full validation pipeline on the GeneratedContent object.
        """
        logger.info(
            f"Starting comprehensive validation pipeline for content based on outline: {generated_content.content_outline.title if generated_content.content_outline else 'N/A'}"
        )

        all_stage_results: List[ValidationStageResult] = []
        actionable_feedback: List[str] = []

        # --- Stage 1: Validate the Master Content Outline itself ---
        if generated_content.content_outline:
            outline_stages = [
                self._validate_structure(
                    generated_content.content_outline, "ContentOutline"
                ),
                self._validate_completeness(
                    generated_content.content_outline, "ContentOutline"
                ),
                # Educational value for outline might be about its structure and coverage
                self._validate_educational_value(
                    generated_content.content_outline,
                    "ContentOutline_EducationalStructure",
                ),
            ]
            all_stage_results.extend(outline_stages)
            for res in outline_stages:
                if not res.passed and res.improvement_suggestion:
                    actionable_feedback.append(f"Outline: {res.improvement_suggestion}")
        else:
            critical_issue = ValidationStageResult(
                passed=False,
                stage_name="ContentOutline Presence",
                score=0.0,
                issues_found=["Master Content Outline is missing."],
            )
            all_stage_results.append(critical_issue)
            actionable_feedback.append(
                "Critical: Master Content Outline is missing. Cannot proceed with further validation."
            )
            # Early exit if outline is missing as it's fundamental
            overall_score = self._calculate_composite_score(all_stage_results)
            return ComprehensiveValidationReport(
                overall_passed=False,
                overall_score=overall_score,
                stage_results=all_stage_results,
                actionable_feedback=actionable_feedback,
                refinement_prompts=self._generate_refinement_prompts(
                    actionable_feedback
                ),
            )

        # --- Stage 2: Validate Derivative Content Types (if outline passed basic checks) ---
        # We assume derivative content types are attributes of GeneratedContent
        derivative_content_types = {
            "PodcastScript": generated_content.podcast_script,
            "StudyGuide": generated_content.study_guide,
            "OnePagerSummary": generated_content.one_pager_summary,
            "DetailedReadingMaterial": generated_content.detailed_reading_material,
            "FAQCollection": generated_content.faqs,
            "FlashcardCollection": generated_content.flashcards,
            "ReadingGuideQuestions": generated_content.reading_guide_questions,
        }

        for content_type_name, content_instance in derivative_content_types.items():
            if content_instance:  # If this content type was generated
                logger.debug(f"Validating derivative: {content_type_name}")
                item_stages = [
                    self._validate_structure(content_instance, content_type_name),
                    self._validate_completeness(content_instance, content_type_name),
                    # Coherence for derivatives is against the master outline (passed via GeneratedContent)
                    # self._validate_coherence(generated_content, content_type_name), # This needs GeneratedContent
                    self._validate_educational_value(
                        content_instance, content_type_name
                    ),
                ]
                all_stage_results.extend(item_stages)
                for res in item_stages:
                    if not res.passed and res.improvement_suggestion:
                        actionable_feedback.append(
                            f"{content_type_name}: {res.improvement_suggestion}"
                        )

        # --- Stage 3: Overall Coherence (Semantic check across all generated parts) ---
        # This needs the full GeneratedContent object
        coherence_stage_result = self._validate_coherence(
            generated_content, "GeneratedContent_Overall"
        )
        all_stage_results.append(coherence_stage_result)
        if (
            not coherence_stage_result.passed
            and coherence_stage_result.improvement_suggestion
        ):
            actionable_feedback.append(
                f"Overall Coherence: {coherence_stage_result.improvement_suggestion}"
            )

        # --- Calculate final scores and pass/fail ---
        overall_score = self._calculate_composite_score(all_stage_results)

        # Determine overall_passed based on critical stages or overall score
        # For example, if structural validation of outline failed, overall_passed is False
        critical_stages_passed = all(
            s.passed
            for s in all_stage_results
            if s.stage_name
            in [
                "Structural Validation",
                "ContentOutline Presence",
            ]  # Add more critical stages
        )
        overall_passed = critical_stages_passed and (
            overall_score >= self.quality_thresholds.get("default", 0.7)
        )

        logger.info(
            f"Comprehensive validation finished. Overall Score: {overall_score:.2f}, Passed: {overall_passed}"
        )

        return ComprehensiveValidationReport(
            overall_passed=overall_passed,
            overall_score=overall_score,
            stage_results=all_stage_results,
            actionable_feedback=list(set(actionable_feedback)),  # Unique feedback
            refinement_prompts=self._generate_refinement_prompts(actionable_feedback),
        )


# Example Usage (conceptual)
if __name__ == "__main__":
    # This is for illustration; real usage would be within the generation service
    validator = ComprehensiveContentValidator()

    # Create dummy GeneratedContent object
    mock_outline = ContentOutline(
        title="Mock Course Outline",
        overview="This is a mock overview for the comprehensive course on AI.",
        learning_objectives=[
            "Understand AI basics",
            "Learn ML algorithms",
            "Apply deep learning",
        ],
        sections=[
            {
                "section_number": 1,
                "title": "AI Fundamentals",
                "description": "Covering the core concepts of AI.",
                "key_points": ["Definition of AI", "History of AI"],
            },
            {
                "section_number": 2,
                "title": "Machine Learning",
                "description": "Exploring various ML techniques.",
                "key_points": ["Supervised Learning", "Unsupervised Learning"],
            },
        ],
    )
    mock_podcast = PodcastScript(
        title="AI Podcast",
        introduction="Welcome to AI.",
        main_content="Today we discuss AI...",
        conclusion="Thanks for listening.",
    )

    generated_data = GeneratedContent(
        content_outline=mock_outline,
        podcast_script=mock_podcast
        # ... other content types would be populated
    )

    report = validator.validate_content_pipeline(generated_data)

    print(f"Overall Validation Passed: {report.overall_passed}")
    print(f"Overall Score: {report.overall_score:.2f}")
    print("\nStage Results:")
    for stage_res in report.stage_results:
        print(
            f"  Stage: {stage_res.stage_name}, Passed: {stage_res.passed}, Score: {stage_res.score:.2f if stage_res.score is not None else 'N/A'}"
        )
        if stage_res.issues_found:
            print(f"    Issues: {'; '.join(stage_res.issues_found)}")

    if report.actionable_feedback:
        print("\nActionable Feedback:")
        for feedback_item in report.actionable_feedback:
            print(f"- {feedback_item}")

    if report.refinement_prompts:
        print("\nSuggested Refinement Prompts:")
        for prompt_item in report.refinement_prompts:
            print(f"- {prompt_item}")
