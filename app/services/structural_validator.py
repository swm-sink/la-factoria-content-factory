"""
Structural Validator - Simple validation focused on structure, not quality
"""

import logging
from dataclasses import dataclass
from typing import Any, List, Optional

from pydantic import BaseModel, ValidationError

from app.models.pydantic.content import (
    ContentOutline,
    DetailedReadingMaterial,
    FAQCollection,
    FlashcardCollection,
    OnePagerSummary,
    PodcastScript,
    ReadingGuideQuestions,
    StudyGuide,
)


@dataclass
class ValidationResult:
    """Result of validation check"""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class StructuralValidator:
    """
    Simple validator that only checks structure and basic requirements.
    No complex semantic validation - quality issues become warnings, not errors.
    """

    # Minimum length requirements (simplified)
    MIN_LENGTHS = {
        "content_outline": 100,
        "podcast_script": 500,
        "study_guide": 400,
        "one_pager_summary": 200,
        "detailed_reading": 800,
        "faqs": 100,  # At least a few questions
        "flashcards": 100,  # At least a few cards
        "reading_questions": 100,  # At least a few questions
    }

    # Content type to model mapping
    CONTENT_MODELS = {
        "content_outline": ContentOutline,
        "podcast_script": PodcastScript,
        "study_guide": StudyGuide,
        "one_pager_summary": OnePagerSummary,
        "detailed_reading": DetailedReadingMaterial,
        "faqs": FAQCollection,
        "flashcards": FlashcardCollection,
        "reading_questions": ReadingGuideQuestions,
    }

    def __init__(self):
        """Initialize validator"""
        self.logger = logging.getLogger(__name__)

    def validate_input(self, syllabus_text: str) -> ValidationResult:
        """Validate input syllabus text"""
        errors = []
        warnings = []

        # Basic validation
        if not syllabus_text:
            errors.append("Syllabus text is empty")
        elif len(syllabus_text.strip()) < 10:
            errors.append("Syllabus text is too short (min 10 characters)")
        elif len(syllabus_text) > 50000:
            warnings.append(
                "Syllabus text is very long (>50k chars), may affect quality"
            )

        # Check for basic content
        if syllabus_text and not any(c.isalnum() for c in syllabus_text):
            errors.append("Syllabus text contains no alphanumeric characters")

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    def validate_content(self, content: Any, content_type: str) -> ValidationResult:
        """
        Validate content structure for a specific type.
        Focus on structure, not quality.
        """
        errors = []
        warnings = []

        # Check if content exists
        if content is None:
            errors.append(f"{content_type} content is None")
            return ValidationResult(is_valid=False, errors=errors)

        # Validate it's the right type
        expected_model = self.CONTENT_MODELS.get(content_type)
        if expected_model and not isinstance(content, expected_model):
            try:
                # Try to convert if it's a dict
                if isinstance(content, dict):
                    content = expected_model(**content)
                else:
                    errors.append(
                        f"{content_type} is not the expected type "
                        f"({type(content).__name__} vs {expected_model.__name__})"
                    )
            except ValidationError as e:
                errors.append(f"Pydantic validation failed: {str(e)}")

        # Check minimum content requirements
        content_text = self._extract_text_content(content, content_type)
        min_length = self.MIN_LENGTHS.get(content_type, 100)

        if len(content_text) < min_length:
            warnings.append(
                f"{content_type} seems short ({len(content_text)} chars, "
                f"recommended min: {min_length})"
            )

        # Type-specific structural checks
        if content_type == "content_outline":
            self._validate_outline_structure(content, warnings)
        elif content_type == "podcast_script":
            self._validate_podcast_structure(content, warnings)
        elif content_type == "faqs":
            self._validate_faq_structure(content, warnings)
        elif content_type == "flashcards":
            self._validate_flashcard_structure(content, warnings)

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    def _extract_text_content(self, content: Any, content_type: str) -> str:
        """Extract text from content for length checking"""
        try:
            # Try to get a text representation
            if hasattr(content, "model_dump_json"):
                return content.model_dump_json()
            elif hasattr(content, "dict"):
                return str(content.dict())
            else:
                return str(content)
        except Exception:
            return ""

    def _validate_outline_structure(
        self, outline: ContentOutline, warnings: List[str]
    ) -> None:
        """Check outline has basic structure"""
        if not hasattr(outline, "sections") or not outline.sections:
            warnings.append("Outline has no sections")
        elif len(outline.sections) < 2:
            warnings.append("Outline has fewer than 2 sections")

        # Check if sections have subsections
        empty_sections = 0
        for section in getattr(outline, "sections", []):
            if not hasattr(section, "subsections") or not section.subsections:
                empty_sections += 1

        if empty_sections > len(getattr(outline, "sections", [])) / 2:
            warnings.append("Many outline sections lack subsections")

    def _validate_podcast_structure(
        self, script: PodcastScript, warnings: List[str]
    ) -> None:
        """Check podcast script has basic structure"""
        if not hasattr(script, "segments") or not script.segments:
            warnings.append("Podcast script has no segments")
        elif len(script.segments) < 3:
            warnings.append(
                "Podcast script has fewer than 3 segments (intro/body/outro)"
            )

        # Check for speaker diversity
        speakers = set()
        for segment in getattr(script, "segments", []):
            if hasattr(segment, "speaker"):
                speakers.add(segment.speaker)

        if len(speakers) < 2:
            warnings.append("Podcast script uses fewer than 2 speakers")

    def _validate_faq_structure(self, faqs: FAQCollection, warnings: List[str]) -> None:
        """Check FAQ collection has questions"""
        if not hasattr(faqs, "questions") or not faqs.questions:
            warnings.append("FAQ collection has no questions")
        elif len(faqs.questions) < 3:
            warnings.append("FAQ collection has fewer than 3 questions")

    def _validate_flashcard_structure(
        self, flashcards: FlashcardCollection, warnings: List[str]
    ) -> None:
        """Check flashcard collection has cards"""
        if not hasattr(flashcards, "cards") or not flashcards.cards:
            warnings.append("Flashcard collection has no cards")
        elif len(flashcards.cards) < 5:
            warnings.append("Flashcard collection has fewer than 5 cards")

        # Check for empty cards
        empty_cards = 0
        for card in getattr(flashcards, "cards", []):
            if not getattr(card, "front", "") or not getattr(card, "back", ""):
                empty_cards += 1

        if empty_cards > 0:
            warnings.append(f"{empty_cards} flashcards have empty front or back")
