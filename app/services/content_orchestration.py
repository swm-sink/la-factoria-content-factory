"""
Content Orchestration Service for coordinating multi-step content generation.
Handles the workflow of generating outline and derivative content types.
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Tuple, Type

from pydantic import BaseModel

from app.core.config.settings import Settings
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
from app.services.llm_client import LLMClientService
from app.services.parallel_processor import ParallelProcessor
from app.services.prompt_optimizer import PromptContext
from app.services.prompts import PromptService
from app.utils.content_validation import sanitize_html_content
from app.utils.text_cleanup import correct_grammar_and_style


class ContentOrchestrationService:
    """Service for orchestrating the multi-step content generation process."""

    def __init__(
        self,
        settings: Settings,
        llm_client: LLMClientService,
        prompt_service: Optional[PromptService] = None,
        parallel_processor: Optional[ParallelProcessor] = None,
    ):
        """Initialize the orchestration service."""
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.llm_client = llm_client
        self.prompt_service = prompt_service or PromptService()
        self.parallel_processor = parallel_processor or ParallelProcessor(max_workers=4)

    def analyze_input_complexity(self, syllabus_text: str) -> PromptContext:
        """Analyze the complexity of the input to create appropriate prompt context."""
        word_count = len(syllabus_text.split())

        # Determine complexity level
        if word_count < 100:
            complexity = "simple"
            technical_level = "beginner"
        elif word_count < 500:
            complexity = "moderate"
            technical_level = "intermediate"
        else:
            complexity = "complex"
            technical_level = "advanced"

        # Extract key topics (simplified)
        lines = syllabus_text.split("\n")
        topics = [
            line.strip() for line in lines if line.strip() and len(line.strip()) > 10
        ][:5]

        return PromptContext(
            topic=" ".join(topics[:2]) if topics else "Educational Content",
            audience_level=technical_level,
            content_type="educational",
            key_topics=topics,
            constraints={
                "complexity": complexity,
                "word_count": word_count,
                "estimated_duration": word_count / 150,  # rough estimate
            },
        )

    def generate_master_content_outline(
        self,
        syllabus_text: str,
        prompt_context: PromptContext,
        quality_validator: Optional[callable] = None,
    ) -> Tuple[Optional[ContentOutline], Dict[str, int]]:
        """Generate the master ContentOutline from syllabus text."""
        self.logger.info("Generating Master Content Outline...")

        prompt = self.prompt_service.get_prompt(
            "master_content_outline", syllabus_text=syllabus_text
        )

        master_outline, token_usage = self.llm_client.call_generative_model(
            prompt_str=prompt,
            pydantic_model_cls=ContentOutline,
            content_type_name="Master Content Outline",
            prompt_context=prompt_context,
            quality_validator=quality_validator,
        )

        if master_outline:
            self.logger.info("Master Content Outline generated successfully.")
            # Apply content sanitization
            self._sanitize_content_outline(master_outline)
            self.logger.info("Applied sanitization to Master Content Outline.")
        else:
            self.logger.error("Failed to generate Master Content Outline.")

        return master_outline, token_usage

    def _sanitize_content_outline(self, outline: ContentOutline) -> None:
        """Apply sanitization to content outline."""
        if outline.overview:
            outline.overview = sanitize_html_content(
                correct_grammar_and_style(outline.overview)
            )

        for section in outline.sections:
            if section.description:
                section.description = sanitize_html_content(
                    correct_grammar_and_style(section.description)
                )
            if section.title:
                section.title = sanitize_html_content(section.title)
            if section.key_points:
                section.key_points = [
                    sanitize_html_content(correct_grammar_and_style(kp))
                    for kp in section.key_points
                ]

    def orchestrate_derivative_content_generation(
        self,
        master_outline_json: str,
        prompt_context: PromptContext,
        use_parallel: bool,
        generated_content_data: GeneratedContent,
        initial_token_usage: Dict[str, int],
        quality_validator: Optional[callable] = None,
    ) -> Tuple[GeneratedContent, Dict[str, int]]:
        """Orchestrate the generation of all derivative content types."""
        self.logger.info("Starting orchestration of derivative content generation...")
        current_total_token_usage = initial_token_usage.copy()

        content_types_config = {
            "podcast_script": ("podcast_script", PodcastScript, "Podcast Script"),
            "study_guide": ("study_guide", StudyGuide, "Study Guide"),
            "one_pager_summary": (
                "one_pager_summary",
                OnePagerSummary,
                "One-Pager Summary",
            ),
            "detailed_reading_material": (
                "detailed_reading_material",
                DetailedReadingMaterial,
                "Detailed Reading Material",
            ),
            "faqs": ("faq_collection", FAQCollection, "FAQs"),
            "flashcards": ("flashcards", FlashcardCollection, "Flashcards"),
            "reading_guide_questions": (
                "reading_guide_questions",
                ReadingGuideQuestions,
                "Reading Guide Questions",
            ),
        }

        if use_parallel:
            self.logger.info("Generating derivative content in parallel.")

            def generate_task_wrapper(args_tuple):
                attr_name, prompt_key, model_cls, name = args_tuple
                return attr_name, self._generate_specific_content_type(
                    master_outline_json,
                    prompt_key,
                    model_cls,
                    name,
                    prompt_context,
                    quality_validator,
                )

            task_args_list = [
                (k, v[0], v[1], v[2]) for k, v in content_types_config.items()
            ]
            results = self.parallel_processor.execute_tasks(
                generate_task_wrapper, task_args_list
            )

            for attr_name, result_tuple in results:
                if result_tuple and not isinstance(result_tuple, Exception):
                    content_obj, task_tokens = result_tuple
                    if content_obj:
                        setattr(generated_content_data, attr_name, content_obj)
                    current_total_token_usage["input_tokens"] += task_tokens.get(
                        "input_tokens", 0
                    )
                    current_total_token_usage["output_tokens"] += task_tokens.get(
                        "output_tokens", 0
                    )
                else:
                    self.logger.warning(
                        f"Failed to generate {attr_name} in parallel: {result_tuple}"
                    )
        else:
            self.logger.info("Generating derivative content sequentially.")
            for attr_name, (
                prompt_key,
                model_cls,
                name,
            ) in content_types_config.items():
                content_obj, task_tokens = self._generate_specific_content_type(
                    master_outline_json,
                    prompt_key,
                    model_cls,
                    name,
                    prompt_context,
                    quality_validator,
                )
                if content_obj:
                    setattr(generated_content_data, attr_name, content_obj)
                current_total_token_usage["input_tokens"] += task_tokens.get(
                    "input_tokens", 0
                )
                current_total_token_usage["output_tokens"] += task_tokens.get(
                    "output_tokens", 0
                )

        self.logger.info("Finished orchestration of derivative content generation.")
        return generated_content_data, current_total_token_usage

    def _generate_specific_content_type(
        self,
        master_outline_json: str,
        prompt_name_key: str,
        model_cls: Type[BaseModel],
        content_type_name: str,
        prompt_context: PromptContext,
        quality_validator: Optional[callable] = None,
    ) -> Tuple[Optional[BaseModel], Dict[str, int]]:
        """Generate a specific derivative content type based on the master outline."""
        self.logger.info(f"Generating {content_type_name} based on master outline...")

        # Create content-specific context
        content_context = PromptContext(
            topic=prompt_context.topic,
            audience_level=prompt_context.audience_level,
            content_type=prompt_name_key,
            key_topics=prompt_context.key_topics,
            constraints={
                **prompt_context.constraints,
                "content_type": prompt_name_key,
                "base_outline": "provided",
            },
        )

        prompt = self.prompt_service.get_prompt(
            prompt_name_key, outline_json=master_outline_json
        )

        content_object, token_usage = self.llm_client.call_generative_model(
            prompt_str=prompt,
            pydantic_model_cls=model_cls,
            content_type_name=content_type_name,
            prompt_context=content_context,
            quality_validator=quality_validator,
        )

        if content_object:
            self.logger.info(f"{content_type_name} generated successfully.")
            # Apply content sanitization
            self._apply_content_sanitization(content_object)
        else:
            self.logger.warning(f"Failed to generate {content_type_name}.")

        return content_object, token_usage

    def _apply_content_sanitization(self, content_object: BaseModel) -> None:
        """Apply sanitization and grammar correction to content object."""
        if hasattr(content_object, "title") and getattr(content_object, "title"):
            setattr(
                content_object,
                "title",
                sanitize_html_content(getattr(content_object, "title")),
            )

        if isinstance(content_object, PodcastScript):
            if content_object.introduction:
                content_object.introduction = sanitize_html_content(
                    correct_grammar_and_style(content_object.introduction)
                )
            if content_object.main_content:
                content_object.main_content = sanitize_html_content(
                    correct_grammar_and_style(content_object.main_content)
                )
            if content_object.conclusion:
                content_object.conclusion = sanitize_html_content(
                    correct_grammar_and_style(content_object.conclusion)
                )
        elif isinstance(content_object, StudyGuide):
            if content_object.overview:
                content_object.overview = sanitize_html_content(
                    correct_grammar_and_style(content_object.overview)
                )
            if content_object.detailed_content:
                content_object.detailed_content = sanitize_html_content(
                    correct_grammar_and_style(content_object.detailed_content)
                )
            if content_object.summary:
                content_object.summary = sanitize_html_content(
                    correct_grammar_and_style(content_object.summary)
                )
            if content_object.key_concepts:
                content_object.key_concepts = [
                    sanitize_html_content(kc) for kc in content_object.key_concepts
                ]
        elif isinstance(content_object, OnePagerSummary):
            if content_object.executive_summary:
                content_object.executive_summary = sanitize_html_content(
                    correct_grammar_and_style(content_object.executive_summary)
                )
            if content_object.main_content:
                content_object.main_content = sanitize_html_content(
                    correct_grammar_and_style(content_object.main_content)
                )
            if content_object.key_takeaways:
                content_object.key_takeaways = [
                    sanitize_html_content(kt) for kt in content_object.key_takeaways
                ]
        elif isinstance(content_object, DetailedReadingMaterial):
            if content_object.introduction:
                content_object.introduction = sanitize_html_content(
                    correct_grammar_and_style(content_object.introduction)
                )
            for section_item in content_object.sections:
                if section_item.get("title"):
                    section_item["title"] = sanitize_html_content(section_item["title"])
                if section_item.get("content"):
                    section_item["content"] = sanitize_html_content(
                        correct_grammar_and_style(section_item["content"])
                    )
            if content_object.conclusion:
                content_object.conclusion = sanitize_html_content(
                    correct_grammar_and_style(content_object.conclusion)
                )
        elif isinstance(content_object, FAQCollection):
            for item in content_object.items:
                if item.question:
                    item.question = sanitize_html_content(item.question)
                if item.answer:
                    item.answer = sanitize_html_content(
                        correct_grammar_and_style(item.answer)
                    )
        elif isinstance(content_object, FlashcardCollection):
            for item in content_object.items:
                if item.term:
                    item.term = sanitize_html_content(item.term)
                if item.definition:
                    item.definition = sanitize_html_content(
                        correct_grammar_and_style(item.definition)
                    )
        elif isinstance(content_object, ReadingGuideQuestions):
            if content_object.questions:
                content_object.questions = [
                    sanitize_html_content(q) for q in content_object.questions
                ]

    def calculate_and_log_cost_summary(
        self,
        total_token_usage: Dict[str, int],
        content_type: str = "full_content_generation",
        start_time: Optional[datetime] = None,
    ) -> Optional[float]:
        """
        Calculate total estimated cost and log cost tracking summary.

        Args:
            total_token_usage: Dictionary with 'input_tokens' and 'output_tokens'
            content_type: Type of content generated for logging context
            start_time: Start time to calculate total duration

        Returns:
            Estimated cost in USD, or None if cost tracking disabled
        """
        if not self.settings.enable_cost_tracking:
            return None

        input_tokens = total_token_usage.get("input_tokens", 0)
        output_tokens = total_token_usage.get("output_tokens", 0)
        total_tokens = input_tokens + output_tokens

        # Calculate estimated cost using pricing from settings
        pricing = getattr(self.settings, "gemini_1_5_flash_pricing", {})
        input_cost_per_1k = pricing.get(
            "input_per_1k_tokens", 0.000075
        )  # Default Gemini 1.5 Flash pricing
        output_cost_per_1k = pricing.get("output_per_1k_tokens", 0.0003)

        input_cost = (input_tokens / 1000) * input_cost_per_1k
        output_cost = (output_tokens / 1000) * output_cost_per_1k
        total_estimated_cost = input_cost + output_cost

        # Calculate duration if start_time provided
        duration_seconds = None
        if start_time:
            duration_seconds = (datetime.utcnow() - start_time).total_seconds()

        # Check cost thresholds and warn if approaching limits
        cost_per_request_limit = getattr(
            self.settings, "max_cost_per_request", 0.50
        )  # Default $0.50

        if total_estimated_cost > cost_per_request_limit * 0.8:  # 80% threshold
            self.logger.warning(
                f"Cost approaching limit for {content_type}: "
                f"${total_estimated_cost:.4f} (limit: ${cost_per_request_limit})"
            )

        if total_estimated_cost > cost_per_request_limit:
            self.logger.error(
                f"Cost exceeded limit for {content_type}: "
                f"${total_estimated_cost:.4f} > ${cost_per_request_limit}"
            )

        # Log comprehensive cost summary
        cost_summary = {
            "message": f"Cost summary for {content_type}",
            "content_type": content_type,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_estimated_cost_usd": round(total_estimated_cost, 6),
            "cost_per_token": round(total_estimated_cost / total_tokens, 8)
            if total_tokens > 0
            else 0,
        }

        if duration_seconds:
            cost_summary["duration_seconds"] = round(duration_seconds, 2)
            cost_summary["cost_per_second"] = (
                round(total_estimated_cost / duration_seconds, 6)
                if duration_seconds > 0
                else 0
            )

        self.logger.info("Content generation cost tracking", extra=cost_summary)

        return total_estimated_cost
