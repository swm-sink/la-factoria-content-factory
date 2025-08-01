"""
Base exporter class and export format definitions.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from app.models.pydantic.content import GeneratedContent

logger = logging.getLogger(__name__)


class ExportFormat(str, Enum):
    """Supported export formats."""

    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class ExportOptions(dict):
    """Export options container with type hints."""

    def __init__(
        self,
        include_metadata: bool = True,
        include_quality_metrics: bool = True,
        include_version_info: bool = True,
        template_name: Optional[str] = None,
        custom_styles: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(
            include_metadata=include_metadata,
            include_quality_metrics=include_quality_metrics,
            include_version_info=include_version_info,
            template_name=template_name,
            custom_styles=custom_styles or {},
            **kwargs,
        )


class BaseExporter(ABC):
    """Abstract base class for content exporters."""

    def __init__(self, format_type: ExportFormat):
        """
        Initialize the base exporter.

        Args:
            format_type: The export format type
        """
        self.format_type = format_type
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    async def export_single(self, content: GeneratedContent, options: Optional[ExportOptions] = None) -> bytes:
        """
        Export a single content item.

        Args:
            content: The content to export
            options: Export options

        Returns:
            The exported content as bytes
        """
        pass

    @abstractmethod
    async def export_batch(self, contents: List[GeneratedContent], options: Optional[ExportOptions] = None) -> bytes:
        """
        Export multiple content items.

        Args:
            contents: List of contents to export
            options: Export options

        Returns:
            The exported content as bytes
        """
        pass

    @abstractmethod
    def get_content_type(self) -> str:
        """
        Get the MIME content type for this exporter.

        Returns:
            MIME content type string
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """
        Get the file extension for this exporter.

        Returns:
            File extension without the dot
        """
        pass

    def _prepare_content_data(
        self, content: GeneratedContent, options: Optional[ExportOptions] = None
    ) -> Dict[str, Any]:
        """
        Prepare content data for export.

        Args:
            content: The content to prepare
            options: Export options

        Returns:
            Dictionary with prepared content data
        """
        options = options or ExportOptions()

        # Base content data
        data = {
            "title": content.content_outline.title,
            "overview": content.content_outline.overview,
            "learning_objectives": content.content_outline.learning_objectives,
            "sections": [
                {
                    "section_number": section.section_number,
                    "title": section.title,
                    "description": section.description,
                    "key_points": section.key_points,
                    "estimated_duration_minutes": section.estimated_duration_minutes,
                }
                for section in content.content_outline.sections
            ],
            "estimated_total_duration": content.content_outline.estimated_total_duration,
            "target_audience": content.content_outline.target_audience,
            "difficulty_level": content.content_outline.difficulty_level,
        }

        # Add optional content types if present
        if content.podcast_script:
            data["podcast_script"] = {
                "title": content.podcast_script.title,
                "introduction": content.podcast_script.introduction,
                "main_content": content.podcast_script.main_content,
                "conclusion": content.podcast_script.conclusion,
                "speaker_notes": content.podcast_script.speaker_notes or [],
                "estimated_duration_minutes": content.podcast_script.estimated_duration_minutes,
            }

        if content.study_guide:
            data["study_guide"] = {
                "title": content.study_guide.title,
                "overview": content.study_guide.overview,
                "key_concepts": content.study_guide.key_concepts,
                "detailed_content": content.study_guide.detailed_content,
                "summary": content.study_guide.summary,
                "recommended_reading": content.study_guide.recommended_reading or [],
            }

        if content.one_pager_summary:
            data["one_pager_summary"] = {
                "title": content.one_pager_summary.title,
                "executive_summary": content.one_pager_summary.executive_summary,
                "key_takeaways": content.one_pager_summary.key_takeaways,
                "main_content": content.one_pager_summary.main_content,
            }

        if content.detailed_reading_material:
            data["detailed_reading_material"] = {
                "title": content.detailed_reading_material.title,
                "introduction": content.detailed_reading_material.introduction,
                "sections": content.detailed_reading_material.sections,
                "conclusion": content.detailed_reading_material.conclusion,
                "references": content.detailed_reading_material.references or [],
            }

        if content.faqs:
            data["faqs"] = {
                "title": content.faqs.title,
                "items": [
                    {"question": item.question, "answer": item.answer, "category": item.category}
                    for item in content.faqs.items
                ],
            }

        if content.flashcards:
            data["flashcards"] = {
                "title": content.flashcards.title,
                "items": [
                    {
                        "term": item.term,
                        "definition": item.definition,
                        "category": item.category,
                        "difficulty": item.difficulty,
                    }
                    for item in content.flashcards.items
                ],
            }

        if content.reading_guide_questions:
            data["reading_guide_questions"] = {
                "title": content.reading_guide_questions.title,
                "questions": content.reading_guide_questions.questions,
            }

        # Add export metadata
        data["export_metadata"] = {"exported_at": datetime.utcnow().isoformat(), "format": self.format_type.value}

        return data

    def _flatten_content_for_csv(self, content: GeneratedContent) -> List[Dict[str, Union[str, int, float]]]:
        """
        Flatten content structure for CSV export.

        Args:
            content: The content to flatten

        Returns:
            List of flat dictionaries suitable for CSV export
        """
        rows = []

        # Main content info
        base_info = {
            "content_type": "outline",
            "title": content.content_outline.title,
            "overview": content.content_outline.overview,
            "target_audience": content.content_outline.target_audience or "",
            "difficulty_level": content.content_outline.difficulty_level or "",
            "estimated_duration": content.content_outline.estimated_total_duration or 0,
        }

        # Learning objectives
        for idx, objective in enumerate(content.content_outline.learning_objectives):
            rows.append(
                {**base_info, "item_type": "learning_objective", "item_number": idx + 1, "item_content": objective}
            )

        # Sections
        for section in content.content_outline.sections:
            rows.append(
                {
                    **base_info,
                    "item_type": "section",
                    "item_number": section.section_number,
                    "item_title": section.title,
                    "item_content": section.description,
                    "section_duration": section.estimated_duration_minutes or 0,
                }
            )

            # Section key points
            for idx, point in enumerate(section.key_points):
                rows.append(
                    {
                        **base_info,
                        "item_type": "key_point",
                        "section_number": section.section_number,
                        "item_number": idx + 1,
                        "item_content": point,
                    }
                )

        # FAQs
        if content.faqs:
            for idx, item in enumerate(content.faqs.items):
                rows.append(
                    {
                        **base_info,
                        "item_type": "faq",
                        "item_number": idx + 1,
                        "question": item.question,
                        "answer": item.answer,
                        "category": item.category or "",
                    }
                )

        # Flashcards
        if content.flashcards:
            for idx, item in enumerate(content.flashcards.items):
                rows.append(
                    {
                        **base_info,
                        "item_type": "flashcard",
                        "item_number": idx + 1,
                        "term": item.term,
                        "definition": item.definition,
                        "category": item.category or "",
                        "difficulty": item.difficulty or "",
                    }
                )

        # Reading guide questions
        if content.reading_guide_questions:
            for idx, question in enumerate(content.reading_guide_questions.questions):
                rows.append(
                    {**base_info, "item_type": "reading_question", "item_number": idx + 1, "item_content": question}
                )

        return rows
