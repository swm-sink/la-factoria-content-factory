"""
Multi-step content generation service for creating long-form educational content.
Handles orchestration of topic decomposition, content generation, and assembly.
Now includes comprehensive quality validation and refinement.
"""

import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Type

import vertexai
from prometheus_client import REGISTRY, Counter, Histogram
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from vertexai.generative_models import GenerativeModel

from app.core.config.settings import get_settings
from app.models.content_version import ContentVersionManager
from app.models.pydantic.content import (
    ContentMetadata,
    ContentOutline,
    DetailedReadingMaterial,
    FAQCollection,
    FlashcardCollection,
    GeneratedContent,
    OnePagerSummary,
    PodcastScript,
    QualityMetrics,
    ReadingGuideQuestions,
    StudyGuide,
)
from app.services.comprehensive_content_validator import (
    ComprehensiveContentValidator,
    ComprehensiveValidationReport,
)
from app.services.content_cache import ContentCacheService
from app.services.enhanced_content_validator import EnhancedContentValidator
from app.services.parallel_processor import ParallelProcessor
from app.services.prompt_optimizer import PromptContext, PromptOptimizer
from app.services.prompts import PromptService
from app.services.quality_metrics import QualityMetricsService
from app.services.quality_refinement import QualityRefinementEngine
from app.utils.content_validation import sanitize_html_content
from app.utils.text_cleanup import correct_grammar_and_style

# Prometheus metrics - handle duplicate registration properly

# Get or create metrics by checking if they already exist
try:
    MULTI_STEP_GENERATION_CALLS = REGISTRY._names_to_collectors[
        "multi_step_generation_calls_total"
    ]
except KeyError:
    MULTI_STEP_GENERATION_CALLS = Counter(
        "multi_step_generation_calls_total",
        "Total number of multi-step content generation calls",
    )

try:
    MULTI_STEP_GENERATION_DURATION = REGISTRY._names_to_collectors[
        "multi_step_generation_duration_seconds"
    ]
except KeyError:
    MULTI_STEP_GENERATION_DURATION = Histogram(
        "multi_step_generation_duration_seconds",
        "Time spent on multi-step content generation",
    )

try:
    QUALITY_REFINEMENT_ATTEMPTS = REGISTRY._names_to_collectors[
        "quality_refinement_attempts_total"
    ]
except KeyError:
    QUALITY_REFINEMENT_ATTEMPTS = Counter(
        "quality_refinement_attempts_total",
        "Total number of quality refinement attempts",
        ["content_type", "refinement_reason"],
    )

try:
    QUALITY_SCORES = REGISTRY._names_to_collectors["content_quality_scores"]
except KeyError:
    QUALITY_SCORES = Histogram(
        "content_quality_scores",
        "Distribution of content quality scores",
        ["content_type"],
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


@dataclass
class ContentSection:
    """Represents a section of content with its metadata."""

    title: str
    content: str
    word_count: int
    estimated_duration: float  # in minutes
    content_type: str  # e.g., 'podcast', 'guide', 'one_pager'


class MultiStepContentService:
    """Enhanced service for generating long-form educational content through multiple steps with quality assurance."""

    def __init__(self):
        """Initialize the service with settings and AI platform."""
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        self.prompt_service = PromptService()
        try:
            self.cache = ContentCacheService()
        except Exception as e:
            self.logger.warning(
                f"Failed to initialize cache service: {e}. Operating without cache."
            )
            self.cache = None
        self.parallel_processor = ParallelProcessor(max_workers=4)
        self.quality_service = QualityMetricsService()
        self.version_manager = ContentVersionManager()

        # Initialize quality services
        self.prompt_optimizer = PromptOptimizer()
        self.content_validator = (
            EnhancedContentValidator()
        )  # Still needed for pre_validate_input
        # self.semantic_validator = SemanticConsistencyValidator() # Now part of ComprehensiveContentValidator
        self.quality_refiner = QualityRefinementEngine()
        self.comprehensive_validator = ComprehensiveContentValidator()  # New

        # Initialize Vertex AI
        vertexai.init(
            project=self.settings.gcp_project_id, location=self.settings.gcp_location
        )
        if self.settings.gemini_model_name:
            self.model = GenerativeModel(self.settings.gemini_model_name)
        else:
            self.logger.error(
                "Gemini model name not configured. AI features will fail."
            )
            self.model = None

    def _clean_llm_json_response(self, llm_response_text: str) -> str:
        """Cleans the LLM JSON response text, removing markdown and leading/trailing whitespace."""
        cleaned_text = llm_response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        return cleaned_text.strip()

    def _analyze_input_complexity(self, syllabus_text: str) -> PromptContext:
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

    def _call_generative_model(
        self,
        prompt_str: str,
        pydantic_model_cls: Type[BaseModel],
        content_type_name: str,
        max_retries: Optional[int] = None,
        enable_quality_check: bool = True,
        use_optimizer: bool = True,
        prompt_context: Optional[PromptContext] = None,
    ) -> Tuple[Optional[BaseModel], Dict[str, int]]:
        """
        Calls the generative model with retry logic, quality checks, and prompt refinement.
        """
        if max_retries is None:
            max_retries = self.settings.max_retries

        cumulative_tokens = {"input_tokens": 0, "output_tokens": 0}

        if not self.model:
            self.logger.error(
                f"Generative model not initialized. Cannot generate {content_type_name}."
            )
            return None, cumulative_tokens

        # Optimize prompt if enabled
        if use_optimizer and prompt_context:
            prompt_str = self.prompt_optimizer.optimize_prompt(
                prompt_str, prompt_context
            )
            self.logger.info(f"Optimized prompt for {content_type_name}")

        # Keep track of prompt modifications
        current_prompt = prompt_str
        prompt_modifications = []

        # Retry loop with prompt refinement
        for attempt in range(max_retries + 1):
            try:
                self.logger.info(
                    f"Sending prompt to LLM for {content_type_name} (attempt {attempt + 1}/{max_retries + 1})..."
                )

                llm_response = self.model.generate_content(current_prompt)

                # Extract token usage
                token_usage = {
                    "input_tokens": getattr(
                        llm_response.usage_metadata, "prompt_token_count", 0
                    ),
                    "output_tokens": getattr(
                        llm_response.usage_metadata, "candidates_token_count", 0
                    ),
                }

                # Add to cumulative tokens
                cumulative_tokens["input_tokens"] += token_usage["input_tokens"]
                cumulative_tokens["output_tokens"] += token_usage["output_tokens"]

                # Parse and validate
                cleaned_json_str = self._clean_llm_json_response(llm_response.text)
                parsed_json = json.loads(cleaned_json_str)
                validated_data = pydantic_model_cls(**parsed_json)

                # Quality check if enabled
                if enable_quality_check:
                    quality_result = self.content_validator.validate_content(
                        validated_data, content_type_name.lower().replace(" ", "_")
                    )

                    if not quality_result["is_valid"] and attempt < max_retries:
                        quality_issues = quality_result.get("validation_errors", [])
                        self.logger.warning(
                            f"Quality issues detected for {content_type_name}: {quality_issues}. "
                            f"Refining prompt and retrying..."
                        )
                        # Refine prompt based on quality issues
                        current_prompt = self._refine_prompt_for_quality(
                            current_prompt, quality_issues, prompt_modifications
                        )
                        prompt_modifications.extend(
                            [str(issue) for issue in quality_issues]
                        )
                        QUALITY_REFINEMENT_ATTEMPTS.labels(
                            content_type=content_type_name,
                            refinement_reason="quality_validation_failed",
                        ).inc()
                        continue

                    # Log quality score
                    quality_score = quality_result.get("overall_score", 0.0)
                    QUALITY_SCORES.labels(content_type=content_type_name).observe(
                        quality_score
                    )

                self.logger.info(
                    f"Successfully generated and validated {content_type_name} after {attempt + 1} attempt(s)."
                )

                # Log cost tracking if enabled
                if self.settings.enable_cost_tracking:
                    self._log_cost_tracking(cumulative_tokens, content_type_name)

                return validated_data, cumulative_tokens

            except (json.JSONDecodeError, PydanticValidationError) as e:
                error_type = type(e).__name__
                self.logger.warning(
                    f"Attempt {attempt + 1} failed for {content_type_name} with {error_type}: {str(e)[:200]}"
                )

                if attempt < max_retries:
                    # Refine prompt for better JSON structure
                    if isinstance(e, json.JSONDecodeError):
                        current_prompt = self._refine_prompt_for_json_error(
                            current_prompt, str(e)
                        )
                        prompt_modifications.append("json_structure_reminder")
                    else:  # PydanticValidationError
                        current_prompt = self._refine_prompt_for_validation_error(
                            current_prompt, e, pydantic_model_cls
                        )
                        prompt_modifications.append("pydantic_schema_clarification")

                    # Add delay between retries
                    time.sleep(self.settings.retry_delay)
                else:
                    # Final failure after all retries
                    self.logger.error(
                        f"All {max_retries + 1} attempts failed for {content_type_name}. "
                        f"Final error: {error_type}: {e}"
                    )
                    return None, cumulative_tokens

            except Exception as e:
                self.logger.error(
                    f"Unexpected error generating {content_type_name}: {e}",
                    exc_info=True,
                )
                return None, cumulative_tokens

        # Should not reach here
        return None, cumulative_tokens

    def _refine_prompt_for_quality(
        self, prompt: str, quality_issues: List[str], previous_mods: List[str]
    ) -> str:
        """Refine prompt based on quality issues."""
        refinements = []

        if any("generic_content" in issue for issue in quality_issues):
            refinements.append(
                "IMPORTANT: Generate specific, detailed content relevant to the topic. "
                "Avoid generic placeholder text or examples. Be concrete and informative."
            )

        if "insufficient_sections" in quality_issues:
            refinements.append(
                "REQUIREMENT: Include at least 3-5 well-developed sections with substantial content in each."
            )

        if "insufficient_key_points" in quality_issues:
            refinements.append(
                "REQUIREMENT: Include at least 5 specific key points or takeaways."
            )

        if "content_too_short" in quality_issues:
            refinements.append(
                "REQUIREMENT: Provide comprehensive, detailed content. Each section should be well-developed."
            )

        # Add refinements to prompt
        refinement_text = "\n\n".join(refinements)
        if refinement_text:
            prompt = prompt + "\n\n===QUALITY REQUIREMENTS===\n" + refinement_text

        return prompt

    def _refine_prompt_for_json_error(self, prompt: str, error_msg: str) -> str:
        """Refine prompt to address JSON parsing errors."""
        json_reminder = (
            "\n\nCRITICAL: Your response MUST be valid JSON only. Do not include any text before or after the JSON. "
            "Do not wrap the JSON in markdown code blocks (```json). "
            "Ensure all strings are properly quoted and escaped. "
            'Example format: {"field": "value", "field2": ["item1", "item2"]}'
        )
        return prompt + json_reminder

    def _refine_prompt_for_validation_error(
        self, prompt: str, error: PydanticValidationError, model_cls: Type[BaseModel]
    ) -> str:
        """Refine prompt to address Pydantic validation errors."""
        # Extract field requirements from error
        field_issues = []
        for err in error.errors():
            field = ".".join(str(loc) for loc in err["loc"])
            msg = err["msg"]
            field_issues.append(f"- {field}: {msg}")

        schema_reminder = (
            "\n\nVALIDATION REQUIREMENTS:\n"
            "The JSON must conform to these field requirements:\n"
            + "\n".join(field_issues[:5])  # Limit to first 5 issues
        )

        # Add model schema hint if helpful
        if hasattr(model_cls, "model_json_schema"):
            schema_reminder += f"\n\nExpected structure: {model_cls.__name__} with required fields as specified."

        return prompt + schema_reminder

    def _log_cost_tracking(
        self, token_usage: Dict[str, int], content_type: str
    ) -> None:
        """Log cost tracking information."""
        input_cost = (
            token_usage["input_tokens"] / 1000
        ) * self.settings.gemini_1_5_flash_pricing.get("input_per_1k_tokens", 0)
        output_cost = (
            token_usage["output_tokens"] / 1000
        ) * self.settings.gemini_1_5_flash_pricing.get("output_per_1k_tokens", 0)
        estimated_cost = input_cost + output_cost

        log_payload = {
            "message": f"Gemini API call for {content_type} completed.",
            "service_name": "VertexAI-Gemini",
            "model_name": self.settings.gemini_model_name,
            "content_type_generated": content_type,
            "input_tokens": token_usage["input_tokens"],
            "output_tokens": token_usage["output_tokens"],
            "estimated_cost_usd": round(estimated_cost, 6),
        }
        self.logger.info(json.dumps(log_payload))

    def _generate_master_content_outline(
        self, syllabus_text: str, prompt_context: PromptContext
    ) -> Tuple[Optional[ContentOutline], Dict[str, int]]:
        """Generates the master ContentOutline from syllabus text."""
        self.logger.info("Generating Master Content Outline...")
        prompt = self.prompt_service.get_prompt(
            "master_content_outline", syllabus_text=syllabus_text
        )

        master_outline, token_usage = self._call_generative_model(
            prompt_str=prompt,
            pydantic_model_cls=ContentOutline,
            content_type_name="Master Content Outline",
            prompt_context=prompt_context,
        )

        if master_outline:
            self.logger.info("Master Content Outline generated successfully.")
            # Apply grammar/style correction and sanitization
            if master_outline.overview:
                master_outline.overview = sanitize_html_content(
                    correct_grammar_and_style(master_outline.overview)
                )
            for section in master_outline.sections:
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
            self.logger.info(
                "Applied grammar/style correction to Master Content Outline."
            )
        else:
            self.logger.error("Failed to generate Master Content Outline.")

        return master_outline, token_usage

    def _orchestrate_derivative_content_generation(
        self,
        master_outline_json: str,
        prompt_context: PromptContext,
        use_parallel: bool,
        generated_content_data: GeneratedContent,  # Pass in the partially filled object
        initial_token_usage: Dict[str, int],
    ) -> Tuple[GeneratedContent, Dict[str, int]]:
        """Orchestrates the generation of all derivative content types."""
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
                # Ensure prompt_context is passed correctly
                return attr_name, self._generate_specific_content_type(
                    master_outline_json, prompt_key, model_cls, name, prompt_context
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
                    master_outline_json, prompt_key, model_cls, name, prompt_context
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
    ) -> Tuple[Optional[BaseModel], Dict[str, int]]:
        """Generates a specific derivative content type based on the master outline."""
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

        content_object, token_usage = self._call_generative_model(
            prompt_str=prompt,
            pydantic_model_cls=model_cls,
            content_type_name=content_type_name,
            prompt_context=content_context,
        )

        if content_object:
            self.logger.info(f"{content_type_name} generated successfully.")
            # Apply grammar/style correction and sanitization
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

    def _refine_if_needed(
        self,
        content: BaseModel,
        content_type: str,
        quality_score: float,
        refinement_threshold: float = 0.75,
    ) -> Tuple[BaseModel, bool]:
        """Refine content if quality score is below threshold."""
        if quality_score >= refinement_threshold:
            return content, False

        self.logger.info(
            f"Quality score {quality_score} below threshold {refinement_threshold} "
            f"for {content_type}. Attempting refinement..."
        )

        try:
            refined_content = self.quality_refiner.refine_content(
                content, content_type, {"quality_score": quality_score}
            )

            if refined_content and refined_content != content:
                QUALITY_REFINEMENT_ATTEMPTS.labels(
                    content_type=content_type, refinement_reason="low_quality_score"
                ).inc()
                self.logger.info(f"Successfully refined {content_type}")
                return refined_content, True
            else:
                self.logger.warning(f"Refinement did not improve {content_type}")
                return content, False

        except Exception as e:
            self.logger.error(f"Error refining {content_type}: {e}")
            return content, False

    def generate_long_form_content(
        self,
        job_id: str,
        syllabus_text: str,
        target_format: str,
        target_duration: float = None,
        target_pages: int = None,
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
        Generate long-form content using an outline-driven, modular approach with quality assurance.
        Returns: GeneratedContent, ContentMetadata, QualityMetrics, total_token_usage, error_info (if any)
        """
        MULTI_STEP_GENERATION_CALLS.inc()
        start_time = time.time()
        self.logger.info(
            f"Job {job_id}: Starting multi-step content generation with quality threshold {quality_threshold}."
        )

        total_token_usage = {"input_tokens": 0, "output_tokens": 0}
        generated_content_data: Optional[GeneratedContent] = None
        content_metadata_obj: Optional[ContentMetadata] = None
        quality_metrics_obj: Optional[QualityMetrics] = None
        error_info: Optional[Dict[str, str]] = None

        CACHE_VERSION = "long_form_v5_quality_aware"  # Updated cache version
        if use_cache and self.cache is not None:
            # Cache get now returns (content_payload, quality_metrics_dict)
            cached_result = self.cache.get(
                syllabus_text,
                target_format,
                target_duration,
                target_pages,
                version=CACHE_VERSION,
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
                        # MVP: Use cached content without quality checks for simplicity
                        self.logger.info(
                            f"Job {job_id}: Cache hit (Version: {CACHE_VERSION}, Score: {qm_cached_obj.overall_score:.2f})."
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
                            f"Job {job_id}: Cache data malformed for version {CACHE_VERSION}. Regenerating."
                        )
                        CACHE_MISSES.inc()
                else:
                    self.logger.info(
                        f"Job {job_id}: Cache miss for version {CACHE_VERSION}."
                    )
                    CACHE_MISSES.inc()
            else:
                self.logger.info(
                    f"Job {job_id}: Cache miss for version {CACHE_VERSION}."
                )
                CACHE_MISSES.inc()

        try:
            # Step 1: Pre-validate input
            input_validation = self.content_validator.pre_validate_input(syllabus_text)
            if input_validation.quality_score < 0.3:
                error_info = {
                    "code": "INPUT_VALIDATION_FAILED",
                    "message": f"Input quality too low ({input_validation.quality_score:.2f}). Suggestions: {', '.join(input_validation.enhancement_suggestions[:2])}",
                }
                self.logger.error(f"Job {job_id}: {error_info['message']}")
                return None, None, None, total_token_usage, error_info

            # Step 2: Analyze input complexity for prompt optimization
            prompt_context = self._analyze_input_complexity(syllabus_text)

            # Step 3: Generate master outline with quality checks
            master_outline, outline_tokens = self._generate_master_content_outline(
                syllabus_text, prompt_context
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

            # Initialize GeneratedContent with outline
            generated_content_data = GeneratedContent(content_outline=master_outline)
            master_outline_json = master_outline.model_dump_json()

            # Step 4: Orchestrate derivative content generation
            (
                generated_content_data,
                total_token_usage,
            ) = self._orchestrate_derivative_content_generation(
                master_outline_json=master_outline_json,
                prompt_context=prompt_context,
                use_parallel=use_parallel,
                generated_content_data=generated_content_data,
                initial_token_usage=total_token_usage,
            )

            # Step 5: Comprehensive validation using the new validator
            comprehensive_report: ComprehensiveValidationReport = (
                self.comprehensive_validator.validate_content_pipeline(
                    generated_content=generated_content_data,
                    original_syllabus_text=syllabus_text,
                    target_format=target_format,
                )
            )

            self.logger.info(
                f"Job {job_id}: Comprehensive validation complete. Overall score: {comprehensive_report.overall_score:.2f}, Passed: {comprehensive_report.overall_passed}"
            )

            # Step 6: MVP Simplified Validation - Single pass only
            self.logger.info(
                f"Job {job_id}: MVP Single-pass validation complete. "
                f"Score: {comprehensive_report.overall_score:.2f}, Passed: {comprehensive_report.overall_passed}"
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
                # For MVP: Don't fail on quality issues, just log them for improvement

            # Step 7: Create quality metrics from comprehensive report
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

            # Step 8: Create metadata
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

            # Step 9: Cache results (MVP: Simplified caching)
            if use_cache and self.cache is not None:
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
                    version=CACHE_VERSION,
                )

            # Record metrics
            elapsed_time = time.time() - start_time
            MULTI_STEP_GENERATION_DURATION.observe(elapsed_time)
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


# Dependency provider
_multi_step_content_service_instance: Optional[MultiStepContentService] = None


def get_enhanced_content_service() -> MultiStepContentService:
    """
    Dependency provider for MultiStepContentService.
    Ensures a single instance is created and reused.
    """
    global _multi_step_content_service_instance
    if _multi_step_content_service_instance is None:
        try:
            _multi_step_content_service_instance = MultiStepContentService()
        except Exception as e:
            import logging

            logging.getLogger(__name__).critical(
                f"Failed to instantiate MultiStepContentService: {e}", exc_info=True
            )
            raise
    return _multi_step_content_service_instance
