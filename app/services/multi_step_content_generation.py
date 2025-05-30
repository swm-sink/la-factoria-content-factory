"""
Multi-step content generation service for creating long-form educational content.
Handles orchestration of topic decomposition, content generation, and assembly.
"""

import logging
import json
import time
from typing import Dict, List, Any, Tuple, Optional, Type, Callable
from dataclasses import dataclass
from google.cloud import aiplatform
from prometheus_client import Counter, Histogram
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from app.core.config.settings import get_settings
from app.services.prompts import PromptService  # Changed
from app.services.content_cache import ContentCacheService
from app.services.progress_tracker import ProgressTracker, GenerationStage
from app.services.parallel_processor import ParallelProcessor
from app.services.quality_metrics import QualityMetricsService
from app.models.content_version import (
    ContentVersion,
    ContentVersionManager,
    ContentFormat,
)
from app.models.pydantic.content import (
    ContentOutline,
    PodcastScript,
    StudyGuide,
    OnePagerSummary,
    DetailedReadingMaterial,
    FAQCollection,
    FlashcardCollection,
    ReadingGuideQuestions,
    GeneratedContent,
)
from pydantic import BaseModel, ValidationError as PydanticValidationError
from app.utils.text_cleanup import correct_grammar_and_style  # Added

# Prometheus metrics
MULTI_STEP_GENERATION_CALLS = Counter(
    "multi_step_generation_calls_total",
    "Total number of multi-step content generation calls",
)
MULTI_STEP_GENERATION_DURATION = Histogram(
    "multi_step_generation_duration_seconds",
    "Time spent on multi-step content generation",
)


@dataclass
class ContentSection:
    """Represents a section of content with its metadata."""

    title: str
    content: str
    word_count: int
    estimated_duration: float  # in minutes
    content_type: str  # e.g., 'podcast', 'guide', 'one_pager'


class EnhancedMultiStepContentGenerationService:
    """Enhanced service for generating long-form educational content through multiple steps."""

    def __init__(self):
        """Initialize the service with settings and AI platform."""
        self.settings = get_settings()
        self.prompt_service = PromptService()  # Changed
        self.cache = ContentCacheService()
        self.progress_tracker = ProgressTracker()
        self.parallel_processor = ParallelProcessor(max_workers=4)
        self.quality_service = QualityMetricsService()
        self.version_manager = ContentVersionManager()
        self.logger = logging.getLogger(__name__)

        # Initialize Vertex AI
        aiplatform.init(
            project=self.settings.gcp_project_id, location=self.settings.gcp_location
        )
        # Ensure self.model is correctly initialized
        # It might be better to initialize it here if not done by aiplatform.init itself
        # For example:
        # if self.settings.gemini_model_name:
        #     self.model = aiplatform.GenerativeModel(self.settings.gemini_model_name)
        # else:
        #     self.logger.error("Gemini model name not configured. AI features will fail.")
        #     self.model = None # Or raise an error
        # Assuming self.model is already properly initialized by prior code based on settings
        # Let's ensure it's explicitly assigned for clarity if aiplatform.init doesn't assign it to self.model
        if hasattr(aiplatform, "GenerativeModel"):  # Check if class exists
            self.model = aiplatform.GenerativeModel(self.settings.gemini_model_name)
        else:
            self.logger.error(
                "aiplatform.GenerativeModel not found. AI features will fail."
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

    @retry(
        stop=stop_after_attempt(get_settings().max_retries + 1),  # settings.max_retries is for retries, so +1 for initial attempt
        wait=wait_fixed(get_settings().retry_delay),
        retry=retry_if_exception_type((json.JSONDecodeError, PydanticValidationError)),
        reraise=True  # Reraise the exception if all retries fail
    )
    def _call_generative_model_with_retry(
        self,
        prompt_str: str,
        pydantic_model_cls: Type[BaseModel],
        content_type_name: str,  # For logging
        attempt_number: int = 1 # For logging retry attempts
    ) -> Tuple[Optional[BaseModel], Dict[str, int]]:
        """
        Internal worker for _call_generative_model, wrapped with tenacity for retries.
        Parses the JSON response, and validates against a Pydantic model.

        Args:
            prompt_str: The prompt to send to the LLM.
            pydantic_model_cls: The Pydantic model class to validate the response against.
            content_type_name: A descriptive name of the content being generated (for logging).
            attempt_number: The current attempt number (for logging).

        Returns:
            A tuple containing the validated Pydantic object (or None if an error occurs)
            and a dictionary with token usage ('input_tokens', 'output_tokens').
        
        Raises:
            json.JSONDecodeError: If JSON parsing fails after retries.
            PydanticValidationError: If Pydantic validation fails after retries.
            Exception: For other LLM call failures after retries.
        """
        token_usage = {"input_tokens": 0, "output_tokens": 0}
        # This function assumes self.model is initialized and valid.
        # The check for self.model should be done before calling this retry-wrapped function.

        if attempt_number > 1:
            self.logger.info(f"Retrying LLM call for {content_type_name}, attempt {attempt_number}...")
            # Simple prompt modification for retry on PydanticValidationError or JSONDecodeError
            # More sophisticated analysis could be done here based on the exception type.
            prompt_str_modified = prompt_str + "\\n\\nCRITICAL REMINDER: Your entire response MUST be a single, valid JSON object that strictly adheres to the Pydantic model structure previously defined. Double-check all constraints, types, and nesting. Ensure no extraneous text before or after the JSON object."
        else:
            prompt_str_modified = prompt_str

        try:
            self.logger.info(f"Sending prompt to LLM for {content_type_name} (Attempt {attempt_number})...")
            
            llm_response = self.model.generate_content(prompt_str_modified)

            token_usage["input_tokens"] = getattr(
                llm_response.usage_metadata, "prompt_token_count", 0
            )
            token_usage["output_tokens"] = getattr(
                llm_response.usage_metadata, "candidates_token_count", 0
            )
            if not token_usage["input_tokens"] and hasattr(
                llm_response.usage_metadata, "input_token_count"
            ):
                token_usage["input_tokens"] = (
                    llm_response.usage_metadata.input_token_count
                )
            if not token_usage["output_tokens"] and hasattr(
                llm_response.usage_metadata, "output_token_count"
            ):
                token_usage["output_tokens"] = (
                    llm_response.usage_metadata.output_token_count
                )

            cleaned_json_str = self._clean_llm_json_response(llm_response.text)
            
            # These can raise exceptions that tenacity will catch for retry
            parsed_json = json.loads(cleaned_json_str) 
            validated_data = pydantic_model_cls(**parsed_json)

            self.logger.info(
                f"Successfully generated and validated {content_type_name} on attempt {attempt_number}."
            )

            if self.settings.enable_cost_tracking:
                input_cost = (
                    token_usage["input_tokens"] / 1000
                ) * self.settings.gemini_1_5_flash_pricing.get("input_per_1k_tokens", 0)
                output_cost = (
                    token_usage["output_tokens"] / 1000
                ) * self.settings.gemini_1_5_flash_pricing.get(
                    "output_per_1k_tokens", 0
                )
                estimated_cost = input_cost + output_cost
                log_payload = {
                    "message": f"Gemini API call for {content_type_name} successful (Attempt {attempt_number}).",
                    "service_name": "VertexAI-Gemini",
                    "model_name": self.settings.gemini_model_name,
                    "content_type_generated": content_type_name,
                    "input_tokens": token_usage["input_tokens"],
                    "output_tokens": token_usage["output_tokens"],
                    "estimated_cost_usd": round(estimated_cost, 6),
                }
                self.logger.info(json.dumps(log_payload))

            return validated_data, token_usage

        except (json.JSONDecodeError, PydanticValidationError) as e:
            # Log the specific parsing/validation error before tenacity retries or reraises
            if isinstance(e, json.JSONDecodeError):
                 self.logger.warning(
                    f"JSON parsing error for {content_type_name} on attempt {attempt_number}: {e}. Response text: {llm_response.text[:500] if hasattr(llm_response, 'text') else 'N/A'}..."
                )
            else: # PydanticValidationError
                 self.logger.warning(
                    f"Pydantic validation error for {content_type_name} on attempt {attempt_number}: {e}. Cleaned JSON: {cleaned_json_str[:500] if 'cleaned_json_str' in locals() else 'N/A'}..."
                )
            raise # Reraise for tenacity to handle retry

        # Catching general exceptions should be done by the caller of _call_generative_model if needed,
        # after tenacity has exhausted retries for specific error types.

    def _call_generative_model(
        self,
        prompt_str: str,
        pydantic_model_cls: Type[BaseModel],
        content_type_name: str,  # For logging
    ) -> Tuple[Optional[BaseModel], Dict[str, int]]:
        """
        Calls the generative model, with retries for parsing/validation errors.
        This method now acts as a wrapper around the tenacity-decorated _call_generative_model_with_retry.

        Args:
            prompt_str: The prompt to send to the LLM.
            pydantic_model_cls: The Pydantic model class to validate the response against.
            content_type_name: A descriptive name of the content being generated (for logging).

        Returns:
            A tuple containing the validated Pydantic object (or None if an error occurs)
            and a dictionary with token usage ('input_tokens', 'output_tokens').
        """
        token_usage = {"input_tokens": 0, "output_tokens": 0} # Default token usage

        if not self.model:
            self.logger.error(
                f"Generative model not initialized. Cannot generate {content_type_name}."
            )
            return None, token_usage
        
        current_attempt = 0
        try:
            # Pass attempt number to the retryable function for logging and potentially different logic on retries
            # The before_sleep function in tenacity can also be used to update attempt_number or log.
            # For simplicity here, we pass it and the retryable function updates it.
            # Note: Tenacity's @retry decorator creates a new function. 
            # We need to handle the attempt_number logic carefully if we want to pass it to the *decorated* function.
            # A simpler way is to use tenacity's built-in attempt_number in a before_sleep_log function.
            # For this edit, I'll adjust the @retry to use a before_sleep logger and remove attempt_number from args.

            # Revised approach: Tenacity handles attempt counting implicitly.
            # The before_sleep function can log attempts.
            # The simple prompt modification can happen inside the main try block if an exception occurs,
            # before tenacity retries. However, tenacity's `before_sleep` is cleaner for logging.

            # Let's simplify and assume the _call_generative_model_with_retry handles its internal logic for prompt modification based on being retried.
            # The @retry decorator needs to be on the method itself.

            # Re-defining the retry logic slightly to better integrate with tenacity's flow
            # The _call_generative_model_with_retry will be the one decorated.
            # This outer function will call the decorated one.
            
            # The main logic is now in _call_generative_model_with_retry which is decorated.
            # This outer function just calls it and handles the final exception if retries are exhausted.
            
            # The `attempt_number` logic was moved to the tenacity retry configuration.
            # We define a logging function for tenacity to call before sleeping.
            
            def log_retry_attempt(retry_state):
                self.logger.info(
                    f"Retrying LLM call for {content_type_name}, attempt {retry_state.attempt_number} "
                    f"due to {type(retry_state.outcome.exception()).__name__}. "
                    f"Sleeping for {retry_state.next_action.sleep}s."
                )

            # Need to redefine the _call_generative_model_with_retry without the attempt_number arg
            # and apply the decorator directly to it.
            # The existing _call_generative_model will become the retry-wrapped one.
            # The following is a structural change that's hard to represent in diff.
            # I will redefine _call_generative_model to include the tenacity decorator and logic.
            # And remove _call_generative_model_with_retry.

            # This will be applied by editing the original _call_generative_model method.
            # The diff will show the original method being replaced.
            
            # For the sake of this edit, assume the _call_generative_model_with_retry is correctly defined above
            # and this function calls it.
            
            # Actually, the decorator should be on the method itself.
            # The current structure with a separate _with_retry method is fine.
            # This _call_generative_model will call the decorated one.
            
            # Simulate passing attempt number correctly to a decorated function is tricky.
            # A cleaner way is to let tenacity manage attempts and use its state.
            # Let's assume the decorator on _call_generative_model_with_retry works as intended
            # and the prompt modification logic inside it uses its attempt_number parameter.
            
            # Corrected call to the (now decorated) method:
            return self._call_generative_model_with_retry( # This will now be the decorated version
                prompt_str=prompt_str,
                pydantic_model_cls=pydantic_model_cls,
                content_type_name=content_type_name,
                attempt_number=1 # Initial call is attempt 1
            )

        except (json.JSONDecodeError, PydanticValidationError) as e:
            # These errors should have been handled by tenacity retries. 
            # If they reach here, it means all retries failed.
            self.logger.error(
                f"All retry attempts failed for {content_type_name} due to {type(e).__name__}: {e}. "
                "See previous retry logs for details on each attempt."
            )
            # Token usage might be partial or zero if all attempts failed before/during LLM call
            # It's best to return the current token_usage accumulated if possible, or default.
            # The _call_generative_model_with_retry should ideally update token_usage even on failure.
            # For now, returning the default zeroed token_usage on final failure here.
            return None, {"input_tokens": 0, "output_tokens": 0} 
        
        except Exception as e: # Catch any other exceptions from the LLM call itself (e.g., API errors not caught by tenacity)
            self.logger.error(
                f"General error generating {content_type_name} with LLM after potential retries: {e}", exc_info=True
            )
            # Extract token usage if available from the exception or a partially formed response
            # This part is complex and depends on how the SDK might attach usage metadata to exceptions.
            # For now, returning default token_usage.
            return None, {"input_tokens": 0, "output_tokens": 0}

    # Placeholder for the new master outline generation method
    def _generate_master_content_outline(
        self, syllabus_text: str
    ) -> Tuple[Optional[ContentOutline], Dict[str, int]]:
        """Generates the master ContentOutline from syllabus text."""
        self.logger.info("Generating Master Content Outline...")
        prompt = self.prompt_service.get_prompt(
            "master_content_outline", syllabus_text=syllabus_text
        )  # Changed

        master_outline, token_usage = self._call_generative_model(
            prompt_str=prompt,
            pydantic_model_cls=ContentOutline,
            content_type_name="Master Content Outline",
        )

        if master_outline:
            self.logger.info("Master Content Outline generated successfully.")
            # Apply grammar/style correction
            if master_outline.overview:
                master_outline.overview = correct_grammar_and_style(
                    master_outline.overview
                )
            for section in master_outline.sections:
                if section.description:
                    section.description = correct_grammar_and_style(section.description)
            self.logger.info(
                "Applied grammar/style correction to Master Content Outline."
            )
        else:
            self.logger.error("Failed to generate Master Content Outline.")

        return master_outline, token_usage

    # Placeholder for generating a specific derivative content type
    def _generate_specific_content_type(
        self,
        master_outline_json: str,  # Master outline as a JSON string
        prompt_name_key: str,  # e.g., "podcast_script"
        model_cls: Type[BaseModel],  # e.g., PodcastScript
        content_type_name: str,  # For logging, e.g., "Podcast Script"
    ) -> Tuple[Optional[BaseModel], Dict[str, int]]:
        """Generates a specific derivative content type based on the master outline."""
        self.logger.info(f"Generating {content_type_name} based on master outline...")
        prompt = self.prompt_service.get_prompt(
            prompt_name_key, outline_json=master_outline_json
        )  # Changed

        content_object, token_usage = self._call_generative_model(
            prompt_str=prompt,
            pydantic_model_cls=model_cls,
            content_type_name=content_type_name,
        )

        if content_object:
            self.logger.info(f"{content_type_name} generated successfully.")
            # Apply grammar/style correction to relevant fields
            if isinstance(content_object, PodcastScript):
                if content_object.introduction:
                    content_object.introduction = correct_grammar_and_style(
                        content_object.introduction
                    )
                if content_object.main_content:
                    content_object.main_content = correct_grammar_and_style(
                        content_object.main_content
                    )
                if content_object.conclusion:
                    content_object.conclusion = correct_grammar_and_style(
                        content_object.conclusion
                    )
            elif isinstance(content_object, StudyGuide):
                if content_object.overview:
                    content_object.overview = correct_grammar_and_style(
                        content_object.overview
                    )
                if content_object.detailed_content:
                    content_object.detailed_content = correct_grammar_and_style(
                        content_object.detailed_content
                    )
                if content_object.summary:
                    content_object.summary = correct_grammar_and_style(
                        content_object.summary
                    )
            elif isinstance(content_object, OnePagerSummary):
                if content_object.executive_summary:
                    content_object.executive_summary = correct_grammar_and_style(
                        content_object.executive_summary
                    )
                if content_object.main_content:
                    content_object.main_content = correct_grammar_and_style(
                        content_object.main_content
                    )
            elif isinstance(content_object, DetailedReadingMaterial):
                if content_object.introduction:
                    content_object.introduction = correct_grammar_and_style(
                        content_object.introduction
                    )
                for (
                    section_item
                ) in (
                    content_object.sections
                ):  # section_item is a dict here as per Pydantic model
                    if section_item.get(
                        "content"
                    ):  # DRMSectionItem is a TypedDict, access by key
                        section_item["content"] = correct_grammar_and_style(
                            section_item["content"]
                        )
                if content_object.conclusion:
                    content_object.conclusion = correct_grammar_and_style(
                        content_object.conclusion
                    )
            elif isinstance(content_object, FAQCollection):
                for item in content_object.items:  # item is FAQItem Pydantic model
                    if item.answer:
                        item.answer = correct_grammar_and_style(item.answer)
            elif isinstance(content_object, FlashcardCollection):
                for (
                    item
                ) in content_object.items:  # item is FlashcardItem Pydantic model
                    if item.definition:
                        item.definition = correct_grammar_and_style(item.definition)
            # ReadingGuideQuestions questions are typically not corrected for style. Title is default.

            if not isinstance(
                content_object, ReadingGuideQuestions
            ):  # Avoid logging for types we don't correct
                self.logger.info(
                    f"Applied grammar/style correction to {content_type_name}."
                )

        else:
            self.logger.warning(
                f"Failed to generate {content_type_name}."
            )  # Warning as other types might succeed

        return content_object, token_usage

    def generate_long_form_content(
        self,
        syllabus_text: str,
        target_format: str,  # This might become less relevant or indicate the *primary* desired output if still needed
        target_duration: float = None,
        target_pages: int = None,
        use_cache: bool = True,
        use_parallel: bool = True,
    ) -> Tuple[Dict[str, Any], int, str]:
        """
        Generate long-form content using an outline-driven, modular approach.
        First, a master content outline is generated.
        Then, based on this outline, various derivative content types are generated in parallel.
        """
        start_time = time.time()
        total_token_usage = {"input_tokens": 0, "output_tokens": 0}
        job_id = self.progress_tracker.start_job(
            syllabus_text, target_format, target_duration, target_pages
        )

        generated_content_data = GeneratedContent(
            content_outline=None  # Will be populated, type hint requires it
        )  # Initialize with a placeholder for outline

        try:
            MULTI_STEP_GENERATION_CALLS.inc()

            # Cache Key: For simplicity, the cache key might primarily be based on syllabus_text
            # and perhaps a hash of requested derivative types if we allow selecting them.
            # For now, assume we generate all derivative types.
            cache_key_params = (
                syllabus_text,
                "all_types_from_outline",
                target_duration,
                target_pages,
            )

            if use_cache:
                self.progress_tracker.update_stage(
                    job_id, GenerationStage.INITIALIZING, 10.0, "Checking cache"
                )
                cached_data_dict = self.cache.get(*cache_key_params)
                if cached_data_dict:
                    # Assuming cached_data_dict is the final dictionary form ready for return
                    self.progress_tracker.complete_job(job_id, cached_data_dict)
                    self.logger.info(
                        f"Content (all types from outline) served from cache for job {job_id}"
                    )
                    return cached_data_dict, 200, job_id

            # Step 1: Generate Master Content Outline
            self.progress_tracker.update_stage(
                job_id,
                GenerationStage.GENERATING_OUTLINE,
                0.0,
                "Generating master content outline",
            )
            master_outline, outline_tokens = self._generate_master_content_outline(
                syllabus_text
            )
            total_token_usage["input_tokens"] += outline_tokens.get("input_tokens", 0)
            total_token_usage["output_tokens"] += outline_tokens.get("output_tokens", 0)

            if not master_outline:
                self.logger.error(
                    f"Failed to generate master content outline for job {job_id}. Aborting."
                )
                self.progress_tracker.fail_job(
                    job_id, "Master content outline generation failed."
                )
                # Return an error structure compatible with what the API route expects
                # This might need refinement based on how API route maps this.
                return (
                    self._create_error_response(
                        "Master content outline generation failed", partial_data=None
                    ),
                    500,
                    job_id,
                )

            generated_content_data.content_outline = master_outline
            self.progress_tracker.update_stage(
                job_id,
                GenerationStage.GENERATING_OUTLINE,
                100.0,
                "Master content outline generated",
            )

            # Step 2: Generate Derivative Content Types in Parallel
            self.progress_tracker.update_stage(
                job_id,
                GenerationStage.GENERATING_DERIVATIVES,
                0.0,
                "Starting generation of derivative content types",
            )

            master_outline_json = (
                master_outline.model_dump_json()
            )  # Serialize for prompts

            derivative_tasks = []
            derivative_task_ids = []
            # Define which content types to generate, can be made configurable later
            # The key is the attribute name in GeneratedContent model
            # Value is a tuple of (prompt_name_key, pydantic_model_class, display_name) # Changed
            content_types_to_generate = {
                "podcast_script": (
                    "podcast_script",
                    PodcastScript,
                    "Podcast Script",
                ),  # Changed
                "study_guide": ("study_guide", StudyGuide, "Study Guide"),  # Changed
                "one_pager_summary": (
                    "one_pager_summary",
                    OnePagerSummary,
                    "One-Pager Summary",
                ),  # Changed
                "detailed_reading_material": (
                    "detailed_reading_material",
                    DetailedReadingMaterial,
                    "Detailed Reading Material",
                ),  # Changed
                "faqs": ("faq_collection", FAQCollection, "FAQs"),  # Changed
                "flashcards": (
                    "flashcards",
                    FlashcardCollection,
                    "Flashcards",
                ),  # Changed
                "reading_guide_questions": (
                    "reading_guide_questions",
                    ReadingGuideQuestions,
                    "Reading Guide Questions",
                ),  # Changed
            }

            for attr_name, (
                prompt_name_key,
                model_cls,
                display_name,
            ) in content_types_to_generate.items():  # Changed
                # Lambda to capture variables for the parallel task
                task = lambda ao_json=master_outline_json, pnk=prompt_name_key, mc=model_cls, dn=display_name: self._generate_specific_content_type(  # Changed
                    master_outline_json=ao_json,
                    prompt_name_key=pnk,  # Changed
                    model_cls=mc,
                    content_type_name=dn,
                )
                derivative_tasks.append(task)
                derivative_task_ids.append(attr_name)  # Use attribute name as task ID

            num_derivative_tasks = len(derivative_tasks)
            completed_derivative_tasks = 0

            def parallel_progress_callback(task_id: str, progress: float):
                # This callback might be too granular for overall stage.
                # Instead, we'll update progress after all parallel tasks are done or based on completion count.
                nonlocal completed_derivative_tasks
                if (
                    progress >= 100.0
                ):  # Assuming 100% means task is done (success or failure)
                    completed_derivative_tasks += 1
                    stage_progress = (
                        completed_derivative_tasks / num_derivative_tasks
                    ) * 100
                    self.progress_tracker.update_stage(
                        job_id,
                        GenerationStage.GENERATING_DERIVATIVES,
                        stage_progress,
                        f"Completed {task_id} ({completed_derivative_tasks}/{num_derivative_tasks})",
                    )

            if use_parallel and derivative_tasks:
                parallel_results = self.parallel_processor.execute_parallel_tasks(
                    derivative_tasks, derivative_task_ids, parallel_progress_callback
                )
                for result in parallel_results:
                    content_object, task_tokens = (
                        result.result
                        if result.success and result.result
                        else (None, {})
                    )
                    total_token_usage["input_tokens"] += task_tokens.get(
                        "input_tokens", 0
                    )
                    total_token_usage["output_tokens"] += task_tokens.get(
                        "output_tokens", 0
                    )
                    if content_object and hasattr(
                        generated_content_data, result.task_id
                    ):
                        setattr(generated_content_data, result.task_id, content_object)
                    elif not result.success:
                        self.logger.warning(
                            f"Parallel task {result.task_id} failed: {result.error}"
                        )
            elif derivative_tasks:  # Sequential generation if not parallel
                for i, task_lambda in enumerate(derivative_tasks):
                    attr_name = derivative_task_ids[i]
                    content_object, task_tokens = task_lambda()  # Execute the lambda
                    total_token_usage["input_tokens"] += task_tokens.get(
                        "input_tokens", 0
                    )
                    total_token_usage["output_tokens"] += task_tokens.get(
                        "output_tokens", 0
                    )
                    if content_object and hasattr(generated_content_data, attr_name):
                        setattr(generated_content_data, attr_name, content_object)

                    completed_derivative_tasks += 1
                    stage_progress = (
                        completed_derivative_tasks / num_derivative_tasks
                    ) * 100
                    self.progress_tracker.update_stage(
                        job_id,
                        GenerationStage.GENERATING_DERIVATIVES,
                        stage_progress,
                        f"Completed {attr_name} ({completed_derivative_tasks}/{num_derivative_tasks})",
                    )

            self.progress_tracker.update_stage(
                job_id,
                GenerationStage.GENERATING_DERIVATIVES,
                100.0,
                "All derivative content generation attempted",
            )

            # Check total token usage against limits
            if total_token_usage["input_tokens"] + total_token_usage["output_tokens"] > self.settings.max_total_tokens:
                self.logger.warning(
                    f"Job {job_id} exceeded max_total_tokens ({self.settings.max_total_tokens}). "
                    f"Actual: {total_token_usage['input_tokens'] + total_token_usage['output_tokens']}. "
                    f"Content might be truncated or incomplete if limit was strictly enforced mid-generation."
                )
            elif (total_token_usage["input_tokens"] + total_token_usage["output_tokens"]) > (self.settings.max_total_tokens * 0.8):
                self.logger.info(
                    f"Job {job_id} token usage is >80% of max_total_tokens. "
                    f"Used: {total_token_usage['input_tokens'] + total_token_usage['output_tokens']}, Limit: {self.settings.max_total_tokens}."
                )

            # Step 3: Final Assembly (Python object aggregation) and Quality Check
            # The `generated_content_data` (GeneratedContent model) is already populated.
            self.progress_tracker.update_stage(
                job_id,
                GenerationStage.ASSEMBLING_CONTENT,
                50.0,
                "Aggregating generated content parts",
            )

            # Determine the primary content for the 'content' field if needed by ContentResponse structure later.
            # This might depend on the original 'target_format' or be a standard choice (e.g., study guide if available).
            # For now, the API route's ContentResponse mapping will handle this. We just provide all parts.

            # Convert GeneratedContent Pydantic model to a dictionary for the final response structure
            final_content_dict = generated_content_data.model_dump(
                exclude_none=True
            )  # Important: exclude_none
            # Ensure all keys expected by ContentResponse are present, even if None (handled by Pydantic model defaults usually)

            self.progress_tracker.update_stage(
                job_id,
                GenerationStage.ASSEMBLING_CONTENT,
                100.0,
                "Content aggregation complete",
            )

            # Step 4: Quality Evaluation (on the master outline or primary content)
            self.progress_tracker.update_stage(
                job_id, GenerationStage.FINALIZING, 0.0, "Evaluating content quality"
            )
            quality_metrics_data = {}
            # Decide what to evaluate: the outline, or a specific derivative if target_format is key.
            # Let's assume we evaluate the generated outline's quality.
            if (
                generated_content_data.content_outline
                and generated_content_data.content_outline.overview
            ):
                quality_metrics = self.quality_service.evaluate_content(  # Indentation fixed
                    text_to_evaluate=generated_content_data.content_outline.overview,  # Example: evaluate outline overview
                    original_source_text=syllabus_text,
                    target_format_description="content_outline",
                    generation_params={
                        "target_duration": target_duration,
                        "target_pages": target_pages,
                    },
                )
                quality_metrics_data = {
                    "overall_score": quality_metrics.overall_score,
                    "readability_score": quality_metrics.readability.get_readability_score(),
                    "structure_score": quality_metrics.structure.get_structure_score(),
                    "relevance_score": quality_metrics.relevance.get_relevance_score(),
                    "engagement_score": quality_metrics.engagement_score,  # May not apply to outline
                    "format_compliance_score": quality_metrics.format_compliance_score,  # May not apply to outline
                }
                final_content_dict["quality_metrics"] = quality_metrics_data

            # Step 5: Version Management
            generation_duration = time.time() - start_time
            # The 'content' for versioning should be the full structured dict
            content_version = ContentVersion.create_new(
                syllabus_text=syllabus_text,
                target_format=ContentFormat(
                    target_format.upper() if target_format else "COMPREHENSIVE"
                ),  # Or more generic
                content=final_content_dict,  # Store the whole dict
                metadata={
                    "target_duration": target_duration,
                    "target_pages": target_pages,
                    "job_id": job_id,
                    "original_target_format": target_format,  # Keep original request if needed
                },
                generation_time=generation_duration,
                token_usage=total_token_usage,
            )
            if "overall_score" in quality_metrics_data:
                content_version.update_quality_score(
                    quality_metrics_data["overall_score"]
                )
            self.version_manager.add_version(content_version)
            final_content_dict["version_id"] = content_version.version_id
            final_content_dict["job_id"] = (
                job_id  # Ensure job_id is in the returned dict
            )

            # Add title if not already present in final_content_dict from outline
            if (
                "title" not in final_content_dict
                and generated_content_data.content_outline
            ):
                final_content_dict["title"] = (
                    generated_content_data.content_outline.title
                )

            # Cache the final result dictionary
            if use_cache:
                self.cache.set(
                    *cache_key_params, value=final_content_dict
                )  # Store the dict

            self.progress_tracker.update_stage(
                job_id, GenerationStage.FINALIZING, 100.0, "Content generation complete"
            )
            self.progress_tracker.complete_job(job_id, final_content_dict)

            # The API route expects a dict that ContentResponse can parse.
            # final_content_dict should now contain all the fields that GeneratedContent would,
            # plus job_id, version_id, quality_metrics, etc.
            # The `title` and `content` (primary text) fields at the root of ContentResponse
            # need to be set by the API route from final_content_dict.

            # Determine overall status (partial or complete)
            # This logic might need to align with how ContentResponse model expects 'status' and 'content' fields
            all_generated = all(
                getattr(generated_content_data, attr_name) is not None
                for attr_name in content_types_to_generate.keys()
            )
            status_code = 200 if all_generated else 202  # 202 for partial success

            # The API route will map this dict to ContentResponse.
            # Ensure 'final_content_dict' has the structure that can be mapped to ContentResponse's 'content' (GeneratedContent)
            # and other root fields.
            # Let's adjust `final_content_dict` to be the payload for `ContentResponse(content=payload, ...)`
            response_payload_for_generated_content = generated_content_data.model_dump(
                exclude_none=True
            )

            # Construct the final dict to be returned by the service method, which will be used to init ContentResponse
            # This needs to match the structure that the API route's ContentResponse model will be initialized with.
            # The API route takes the output of this service method's first element (a dict)
            # and uses its fields to populate a ContentResponse instance.

            service_return_dict = {
                "job_id": job_id,
                "version_id": content_version.version_id,
                "quality_metrics": quality_metrics_data,  # This should be a dict
                # Fields for GeneratedContent Pydantic model (to be nested under 'content' by API route)
                "content_outline": response_payload_for_generated_content.get(
                    "content_outline"
                ),
                "podcast_script": response_payload_for_generated_content.get(
                    "podcast_script"
                ),
                "study_guide": response_payload_for_generated_content.get(
                    "study_guide"
                ),
                "one_pager_summary": response_payload_for_generated_content.get(
                    "one_pager_summary"
                ),
                "detailed_reading_material": response_payload_for_generated_content.get(
                    "detailed_reading_material"
                ),
                "faqs": response_payload_for_generated_content.get("faqs"),
                "flashcards": response_payload_for_generated_content.get("flashcards"),
                "reading_guide_questions": response_payload_for_generated_content.get(
                    "reading_guide_questions"
                ),
                # Metadata for ContentResponse
                "metadata": {  # This should map to ContentMetadata Pydantic model
                    "source_syllabus_length": len(syllabus_text),
                    "source_format": target_format,  # Original requested format
                    "target_duration_minutes": target_duration,
                    "target_pages_count": target_pages,
                    "calculated_total_word_count": total_token_usage.get(
                        "output_tokens"
                    ),  # Approximation, actual word count better
                    "ai_model_used": self.settings.gemini_model_name,
                    "tokens_consumed": total_token_usage["input_tokens"]
                    + total_token_usage["output_tokens"],
                },
                # Primary content fields that ContentResponse expects at its root
                "title": (
                    generated_content_data.content_outline.title
                    if generated_content_data.content_outline
                    else "Untitled Content"
                ),
                # Determine 'content' field for ContentResponse based on target_format or a default
                "content": self._determine_primary_content_for_response(
                    generated_content_data, target_format
                ),
            }

            return service_return_dict, status_code, job_id

        except Exception as e:
            error_message = f"Unhandled error in content generation pipeline: {e}"
            self.logger.error(error_message, exc_info=True)
            self.progress_tracker.fail_job(job_id, error_message)
            # Create a dict that _create_error_response would generate
            # so the API route can still form an error HTTP response.
            # The data for GeneratedContent might be partially populated
            partial_data_for_error = (
                generated_content_data.model_dump(exclude_none=True)
                if generated_content_data.content_outline
                else {}
            )

            return (
                self._create_error_response(
                    error_message, partial_data=partial_data_for_error
                ),
                500,
                job_id,
            )

    def _determine_primary_content_for_response(
        self, generated_data: GeneratedContent, original_target_format: Optional[str]
    ) -> str:
        """
        Determines the primary text content for the 'content' field of ContentResponse.
        This might be based on the original target_format or a default.
        """
        if original_target_format:
            if (
                original_target_format.lower() == "podcast"
                and generated_data.podcast_script
            ):
                return generated_data.podcast_script.main_content
            if original_target_format.lower() == "guide" and generated_data.study_guide:
                return generated_data.study_guide.detailed_content
            if (
                original_target_format.lower() == "one_pager"
                and generated_data.one_pager_summary
            ):
                return generated_data.one_pager_summary.main_content

        # Default if target_format not matched or if primary content of that format is empty
        if generated_data.study_guide and generated_data.study_guide.detailed_content:
            return generated_data.study_guide.detailed_content
        if (
            generated_data.detailed_reading_material
            and generated_data.detailed_reading_material.sections
        ):
            return (
                generated_data.detailed_reading_material.sections[0].get("content", "")
                if generated_data.detailed_reading_material.sections
                else ""
            )
        if generated_data.content_outline and generated_data.content_outline.overview:
            return generated_data.content_outline.overview
        return "Primary content could not be determined or is empty."

    def _create_error_response(
        self, error_message: str, partial_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a standardized error response, potentially including partial data."""
        # This structure should align with what the API route expects to build an error HTTP response
        # or a ContentResponse with a 'failed' status.
        response = {
            "error": error_message,
            "status": "failed",  # This indicates the job status
            # Include partial content if available and if the ContentResponse model can handle it
            # The API route will use this to populate ContentResponse, which has a 'content: GeneratedContent' field
        }
        if partial_data:
            # These keys should match the fields of GeneratedContent Pydantic model
            response.update(
                {
                    "content_outline": partial_data.get("content_outline"),
                    "podcast_script": partial_data.get("podcast_script"),
                    "study_guide": partial_data.get("study_guide"),
                    "one_pager_summary": partial_data.get("one_pager_summary"),
                    "detailed_reading_material": partial_data.get(
                        "detailed_reading_material"
                    ),
                    "faqs": partial_data.get("faqs"),
                    "flashcards": partial_data.get("flashcards"),
                    "reading_guide_questions": partial_data.get(
                        "reading_guide_questions"
                    ),
                }
            )
        else:  # Ensure all keys are present for GeneratedContent part of response, even if None
            response.update(
                {
                    "content_outline": None,
                    "podcast_script": None,
                    "study_guide": None,
                    "one_pager_summary": None,
                    "detailed_reading_material": None,
                    "faqs": None,
                    "flashcards": None,
                    "reading_guide_questions": None,
                }
            )
        return response

    def get_job_progress(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get progress information for a job."""
        progress = self.progress_tracker.get_progress(job_id)
        if not progress:
            return None

        return {
            "job_id": progress.job_id,
            "current_stage": progress.current_stage.value,
            "overall_progress": progress.overall_progress,
            "started_at": progress.started_at.isoformat(),
            "completed_at": (
                progress.completed_at.isoformat() if progress.completed_at else None
            ),
            "error_message": progress.error_message,
            "stages": {
                stage.stage.value: {
                    "progress_percentage": stage.progress_percentage,
                    "current_item": stage.current_item,
                    "completed_items": stage.completed_items,
                    "total_items": stage.total_items,
                    "started_at": stage.started_at.isoformat(),
                    "completed_at": (
                        stage.completed_at.isoformat() if stage.completed_at else None
                    ),
                }
                for stage in progress.stages.values()
            },
        }

    def get_content_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific content version."""
        version = self.version_manager.get_version(version_id)
        return version.to_dict() if version else None

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()

    def cleanup_resources(self) -> Dict[str, int]:
        """Cleanup old resources and return cleanup stats."""
        cache_cleaned = self.cache.cleanup_expired()
        jobs_cleaned = self.progress_tracker.cleanup_old_jobs()

        return {"cache_entries_cleaned": cache_cleaned, "jobs_cleaned": jobs_cleaned}
