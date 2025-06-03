"""
Pydantic models for content generation requests, responses, and various content types.

This module defines the data structures used throughout the application for
handling AI-generated content, including request parameters, metadata,
quality metrics, and the specific structures for different educational content formats.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class TargetFormat(str, Enum):
    """Enumeration of allowed target formats for content generation."""

    PODCAST = "podcast"
    GUIDE = "guide"
    ONE_PAGER = "one_pager"
    COMPREHENSIVE = "comprehensive"


class ContentRequest(BaseModel):
    """Request model for generating content."""

    syllabus_text: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        description="The main input text/syllabus for content generation (50-5000 characters).",
    )
    target_format: TargetFormat = Field(
        default=TargetFormat.GUIDE,
        description="Target format for the content.",
    )
    target_duration: Optional[float] = Field(
        default=None,
        ge=0,
        description="Target duration in minutes (for time-based content like podcasts).",
    )
    target_pages: Optional[int] = Field(
        default=None,
        ge=1,
        description="Target number of pages (for document-based content like guides).",
    )
    use_parallel: bool = Field(
        default=True,
        description="Whether to use parallel processing for section generation.",
    )
    use_cache: bool = Field(
        default=True, description="Whether to use caching for generated content."
    )

    # Note: target_format validation now handled by TargetFormat enum


class ContentMetadata(BaseModel):
    """Metadata associated with the generated content."""

    source_syllabus_length: Optional[int] = None
    source_format: Optional[str] = None
    target_duration_minutes: Optional[float] = None
    target_pages_count: Optional[int] = None
    calculated_total_word_count: Optional[int] = None
    calculated_total_duration: Optional[float] = None
    generation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    ai_model_used: Optional[str] = None
    tokens_consumed: Optional[int] = None
    estimated_cost: Optional[float] = None


class QualityMetrics(BaseModel):
    """Quality metrics for the generated content."""

    overall_score: Optional[float] = Field(default=None, ge=0, le=1)
    readability_score: Optional[float] = Field(default=None, ge=0)
    structure_score: Optional[float] = Field(default=None, ge=0, le=1)
    relevance_score: Optional[float] = Field(default=None, ge=0, le=1)
    engagement_score: Optional[float] = Field(default=None, ge=0, le=1)
    format_compliance_score: Optional[float] = Field(default=None, ge=0, le=1)
    content_length_compliance: Optional[bool] = None
    validation_errors: List[str] = Field(default_factory=list)


# ====================================
# SPECIFIC CONTENT TYPE MODELS
# ====================================


class OutlineSection(BaseModel):
    """Individual section within a content outline."""

    section_number: int = Field(..., ge=1)
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=1000)
    estimated_duration_minutes: Optional[float] = Field(default=None, ge=0)
    key_points: List[str] = Field(default_factory=list, max_length=10)

    @field_validator("key_points")
    @classmethod
    def validate_key_points(cls, v: List[str]) -> List[str]:
        if len(v) > 10:
            raise ValueError("Maximum 10 key points per section")
        for point in v:
            if len(point.strip()) < 10:
                raise ValueError("Each key point must be at least 10 characters")
        return v


class ContentOutline(BaseModel):
    """Structured content outline - the foundation for all other content."""

    title: str = Field(..., min_length=10, max_length=200)
    overview: str = Field(..., min_length=50, max_length=1000)
    learning_objectives: List[str] = Field(..., min_length=3, max_length=10)
    sections: List[OutlineSection] = Field(..., min_length=3, max_length=15)
    estimated_total_duration: Optional[float] = Field(default=None, ge=0)
    target_audience: Optional[str] = None
    difficulty_level: Optional[str] = Field(default="intermediate")

    @field_validator("learning_objectives")
    @classmethod
    def validate_learning_objectives(cls, v: List[str]) -> List[str]:
        if not (3 <= len(v) <= 10):
            raise ValueError("Must have 3-10 learning objectives")
        for obj in v:
            if len(obj.strip()) < 15:
                raise ValueError(
                    "Each learning objective must be at least 15 characters"
                )
        return v

    @field_validator("difficulty_level")
    @classmethod
    def validate_difficulty(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ["beginner", "intermediate", "advanced"]:
            raise ValueError(
                "Difficulty must be 'beginner', 'intermediate', or 'advanced'"
            )
        return v


class PodcastScript(BaseModel):
    """Podcast script with structured content."""

    title: str = Field(..., min_length=10, max_length=200)
    introduction: str = Field(..., min_length=100, max_length=2000)
    main_content: str = Field(..., min_length=800, max_length=10000)
    conclusion: str = Field(..., min_length=100, max_length=1000)
    speaker_notes: Optional[List[str]] = Field(default_factory=list)
    estimated_duration_minutes: Optional[float] = None

    @model_validator(mode="after")
    def validate_content_length(self):
        total_length = (
            len(self.introduction) + len(self.main_content) + len(self.conclusion)
        )
        if not (1000 <= total_length <= 12000):
            raise ValueError("Total script content must be 1000-12000 characters")
        return self


class StudyGuide(BaseModel):
    """Comprehensive study guide."""

    title: str = Field(..., min_length=10, max_length=200)
    overview: str = Field(..., min_length=100, max_length=1000)
    key_concepts: List[str] = Field(..., min_length=5, max_length=20)
    detailed_content: str = Field(..., min_length=500, max_length=8000)
    summary: str = Field(..., min_length=100, max_length=1000)
    recommended_reading: Optional[List[str]] = Field(default_factory=list)

    @field_validator("key_concepts")
    @classmethod
    def validate_key_concepts(cls, v: List[str]) -> List[str]:
        if not (5 <= len(v) <= 20):
            raise ValueError("Must have 5-20 key concepts")
        return v


class OnePagerSummary(BaseModel):
    """Concise one-page summary."""

    title: str = Field(..., min_length=10, max_length=200)
    executive_summary: str = Field(..., min_length=100, max_length=500)
    key_takeaways: List[str] = Field(..., min_length=3, max_length=7)
    main_content: str = Field(..., min_length=200, max_length=1500)

    @field_validator("key_takeaways")
    @classmethod
    def validate_takeaways(cls, v: List[str]) -> List[str]:
        if not (3 <= len(v) <= 7):
            raise ValueError("Must have 3-7 key takeaways")
        for takeaway in v:
            if len(takeaway.strip()) < 20:
                raise ValueError("Each takeaway must be at least 20 characters")
        return v


class DetailedReadingMaterial(BaseModel):
    """Comprehensive reading material."""

    title: str = Field(..., min_length=10, max_length=200)
    introduction: str = Field(..., min_length=200, max_length=1000)
    sections: List[Dict[str, str]] = Field(..., min_length=3, max_length=10)
    conclusion: str = Field(..., min_length=200, max_length=1000)
    references: Optional[List[str]] = Field(default_factory=list)

    @field_validator("sections")
    @classmethod
    def validate_sections(cls, v: List[Dict[str, str]]) -> List[Dict[str, str]]:
        for section in v:
            if "title" not in section or "content" not in section:
                raise ValueError("Each section must have 'title' and 'content' keys")
            if len(section["title"]) < 10:
                raise ValueError("Section titles must be at least 10 characters")
            if len(section["content"]) < 200:
                raise ValueError("Section content must be at least 200 characters")
        return v


class FAQItem(BaseModel):
    """Individual FAQ item."""

    question: str = Field(..., min_length=10, max_length=300)
    answer: str = Field(..., min_length=20, max_length=1000)
    category: Optional[str] = None

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        if not v.strip().endswith("?"):
            raise ValueError("Questions must end with a question mark")
        return v.strip()


class FAQCollection(BaseModel):
    """Collection of FAQ items."""

    title: str = Field(default="Frequently Asked Questions")
    items: List[FAQItem] = Field(..., min_length=5, max_length=15)

    @field_validator("items")
    @classmethod
    def validate_faq_count(cls, v: List[FAQItem]) -> List[FAQItem]:
        if not (5 <= len(v) <= 15):
            raise ValueError("Must have 5-15 FAQ items")
        return v


class FlashcardItem(BaseModel):
    """Individual flashcard."""

    term: str = Field(..., min_length=2, max_length=100)
    definition: str = Field(..., min_length=10, max_length=500)
    category: Optional[str] = None
    difficulty: Optional[str] = Field(default="medium")

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ["easy", "medium", "hard"]:
            raise ValueError("Difficulty must be 'easy', 'medium', or 'hard'")
        return v


class FlashcardCollection(BaseModel):
    """Collection of flashcards."""

    title: str = Field(default="Study Flashcards")
    items: List[FlashcardItem] = Field(..., min_length=10, max_length=25)

    @field_validator("items")
    @classmethod
    def validate_flashcard_count(cls, v: List[FlashcardItem]) -> List[FlashcardItem]:
        if not (10 <= len(v) <= 25):
            raise ValueError("Must have 10-25 flashcard items")
        return v


class ReadingGuideQuestions(BaseModel):
    """Reading guide questions."""

    title: str = Field(default="Reading Guide Questions")
    questions: List[str] = Field(..., min_length=5, max_length=15)

    @field_validator("questions")
    @classmethod
    def validate_questions(cls, v: List[str]) -> List[str]:
        if not (5 <= len(v) <= 15):
            raise ValueError("Must have 5-15 reading guide questions")
        for question in v:
            if len(question.strip()) < 15:
                raise ValueError("Each question must be at least 15 characters")
            if not question.strip().endswith("?"):
                raise ValueError("All items must be questions (end with ?)")
        return v


# ====================================
# COMPREHENSIVE CONTENT RESPONSE
# ====================================


class GeneratedContent(BaseModel):
    """Complete generated content with all components."""

    content_outline: ContentOutline
    podcast_script: Optional[PodcastScript] = None
    study_guide: Optional[StudyGuide] = None
    one_pager_summary: Optional[OnePagerSummary] = None
    detailed_reading_material: Optional[DetailedReadingMaterial] = None
    faqs: Optional[FAQCollection] = None
    flashcards: Optional[FlashcardCollection] = None
    reading_guide_questions: Optional[ReadingGuideQuestions] = None

    @model_validator(mode="after")
    def validate_content_consistency(self):
        """Ensure all content is consistent with the outline title."""
        if not self.content_outline or not self.content_outline.title:
            # This case should ideally be caught by outline being mandatory
            # or a separate validator if outline can be None initially.
            return self

        outline_title = self.content_outline.title

        content_types_to_check = {
            "podcast_script": self.podcast_script,
            "study_guide": self.study_guide,
            "one_pager_summary": self.one_pager_summary,
            "detailed_reading_material": self.detailed_reading_material,
            "faqs": self.faqs,  # FAQCollection might use a default title
            "flashcards": self.flashcards,  # FlashcardCollection might use a default title
            "reading_guide_questions": self.reading_guide_questions,  # ReadingGuideQuestions might use a default title
        }

        for field_name, content_item in content_types_to_check.items():
            if content_item and hasattr(content_item, "title") and content_item.title:
                # Allow default titles for collections if they are not outline-derived
                if field_name in [
                    "faqs",
                    "flashcards",
                    "reading_guide_questions",
                ] and content_item.title in [
                    "Frequently Asked Questions",
                    "Study Flashcards",
                    "Reading Guide Questions",
                ]:
                    continue  # Skip check for default titles of these specific collections
                if content_item.title != outline_title:
                    raise ValueError(
                        f"{field_name.replace('_', ' ').title()} title '{content_item.title}' "
                        f"must match content outline title '{outline_title}'."
                    )
        return self


class ContentResponse(BaseModel):
    """Complete response for content generation."""

    job_id: Optional[str] = None
    content: GeneratedContent
    metadata: ContentMetadata
    quality_metrics: Optional[QualityMetrics] = None
    version_id: Optional[str] = None
    status: str = Field(default="completed")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed_statuses = {"completed", "partial", "failed"}
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


# ====================================
# ERROR HANDLING MODELS
# ====================================


class ErrorDetail(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    detail: List[ErrorDetail]


class APIErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    code: Optional[str] = None
    details: Optional[Any] = None
    content_status: Optional[Dict[str, str]] = None  # For partial generation status
