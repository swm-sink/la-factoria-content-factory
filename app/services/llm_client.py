"""
LLM Client Service for handling all Vertex AI Gemini interactions.
Centralized service for AI model calls, prompt refinement, and cost tracking.
"""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Dict, Optional, Tuple, Type

import vertexai
from prometheus_client import REGISTRY, Counter, Histogram
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from vertexai.generative_models import GenerativeModel

from app.core.config.settings import Settings
from app.core.exceptions.custom_exceptions import ExternalServiceError, JobErrorCode
from app.services.prompt_optimizer import PromptContext, PromptOptimizer

# Prometheus metrics for LLM client
try:
    LLM_CALLS_TOTAL = REGISTRY._names_to_collectors["llm_calls_total"]
except KeyError:
    LLM_CALLS_TOTAL = Counter(
        "llm_calls_total", "Total number of LLM API calls", ["content_type", "status"]
    )

try:
    LLM_CALL_DURATION = REGISTRY._names_to_collectors["llm_call_duration_seconds"]
except KeyError:
    LLM_CALL_DURATION = Histogram(
        "llm_call_duration_seconds",
        "Time spent on individual LLM calls",
        ["content_type"],
    )

try:
    LLM_PROMPT_REFINEMENTS = REGISTRY._names_to_collectors[
        "llm_prompt_refinements_total"
    ]
except KeyError:
    LLM_PROMPT_REFINEMENTS = Counter(
        "llm_prompt_refinements_total",
        "Total number of prompt refinements",
        ["refinement_type"],
    )

try:
    LLM_TIMEOUTS = REGISTRY._names_to_collectors["llm_timeouts_total"]
except KeyError:
    LLM_TIMEOUTS = Counter(
        "llm_timeouts_total",
        "Total number of LLM call timeouts",
        ["content_type"],
    )


class LLMClientService:
    """Service for handling all LLM interactions with Vertex AI Gemini."""

    def __init__(
        self, settings: Settings, prompt_optimizer: Optional[PromptOptimizer] = None
    ):
        """Initialize the LLM client with Vertex AI."""
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.prompt_optimizer = prompt_optimizer or PromptOptimizer()
        self.model = None
        
        # Set timeout with default of 120 seconds (2 minutes)
        self.timeout_seconds = getattr(settings, 'llm_timeout_seconds', 120)
        
        # Thread pool for timeout handling
        self.executor = ThreadPoolExecutor(max_workers=1)

        # Initialize Vertex AI with error handling
        self._initialize_vertex_ai()

    def _initialize_vertex_ai(self) -> None:
        """Initialize Vertex AI with proper error handling."""
        try:
            vertexai.init(
                project=self.settings.gcp_project_id,
                location=self.settings.gcp_location,
            )

            if self.settings.gemini_model_name:
                self.model = GenerativeModel(self.settings.gemini_model_name)
                self.logger.info(
                    f"Vertex AI initialized successfully with model {self.settings.gemini_model_name}"
                )
            else:
                self.logger.error(
                    "Gemini model name not configured. AI features will be unavailable."
                )
                self.model = None

        except Exception as e:
            self.logger.error(
                f"CRITICAL: Failed to initialize Vertex AI. AI features will be unavailable. Error: {e}",
                exc_info=True,
            )
            self.model = None
            # For MVP, we'll log the error but not raise immediately
            # The service will handle None model in call_generative_model

    def clean_llm_json_response(self, llm_response_text: str) -> str:
        """Clean the LLM JSON response text, removing markdown and leading/trailing whitespace."""
        cleaned_text = llm_response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        return cleaned_text.strip()

    def refine_prompt_for_quality(
        self, prompt: str, quality_issues: list, previous_mods: list
    ) -> str:
        """Refine prompt based on quality issues."""
        refinements = []

        if any("generic_content" in str(issue) for issue in quality_issues):
            refinements.append(
                "IMPORTANT: Generate specific, detailed content relevant to the topic. "
                "Avoid generic placeholder text or examples. Be concrete and informative."
            )

        if any("insufficient_sections" in str(issue) for issue in quality_issues):
            refinements.append(
                "REQUIREMENT: Include at least 3-5 well-developed sections with substantial content in each."
            )

        if any("insufficient_key_points" in str(issue) for issue in quality_issues):
            refinements.append(
                "REQUIREMENT: Include at least 5 specific key points or takeaways."
            )

        if any("content_too_short" in str(issue) for issue in quality_issues):
            refinements.append(
                "REQUIREMENT: Provide comprehensive, detailed content. Each section should be well-developed."
            )

        # Add refinements to prompt
        if refinements:
            refinement_text = "\n\n".join(refinements)
            prompt = prompt + "\n\n===QUALITY REQUIREMENTS===\n" + refinement_text
            LLM_PROMPT_REFINEMENTS.labels(refinement_type="quality_issues").inc()

        return prompt

    def refine_prompt_for_json_error(self, prompt: str, error_msg: str) -> str:
        """Refine prompt to address JSON parsing errors."""
        json_reminder = (
            "\n\nCRITICAL: Your response MUST be valid JSON only. Do not include any text before or after the JSON. "
            "Do not wrap the JSON in markdown code blocks (```json). "
            "Ensure all strings are properly quoted and escaped. "
            'Example format: {"field": "value", "field2": ["item1", "item2"]}'
        )
        LLM_PROMPT_REFINEMENTS.labels(refinement_type="json_structure").inc()
        return prompt + json_reminder

    def refine_prompt_for_validation_error(
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

        LLM_PROMPT_REFINEMENTS.labels(refinement_type="pydantic_validation").inc()
        return prompt + schema_reminder

    def estimate_token_count(self, text: str) -> int:
        """
        Estimate token count for input text.

        This is a rough estimation using character count / 4 for English text.
        For more accuracy, this could use the actual tokenizer if available.
        """
        # Rough estimation: ~4 characters per token for English
        estimated_tokens = len(text) / 4
        return int(estimated_tokens)

    def check_token_limits(self, prompt: str, content_type: str) -> bool:
        """
        Check if the prompt is within token limits before making API call.

        Returns True if within limits, False if exceeding limits.
        Logs warnings at 80% of limit as per Rule J.11.
        """
        estimated_tokens = self.estimate_token_count(prompt)

        # Check against per-content-type limit if configured
        max_tokens_per_type = getattr(
            self.settings, "max_tokens_per_content_type", None
        )
        if max_tokens_per_type and estimated_tokens > max_tokens_per_type:
            self.logger.error(
                f"Prompt for {content_type} exceeds per-content-type token limit: "
                f"{estimated_tokens} > {max_tokens_per_type}"
            )
            return False

        # Check against total token budget if configured
        max_total_tokens = getattr(self.settings, "max_total_tokens", None)
        if max_total_tokens:
            # Use a portion of the total budget for individual requests
            individual_limit = max_total_tokens * 0.5  # 50% of total budget per request
            if estimated_tokens > individual_limit:
                self.logger.error(
                    f"Prompt for {content_type} exceeds individual token budget: "
                    f"{estimated_tokens} > {individual_limit} (50% of total budget)"
                )
                return False

            # Warning at 80% threshold
            warning_threshold = individual_limit * 0.8
            if estimated_tokens > warning_threshold:
                self.logger.warning(
                    f"Prompt for {content_type} approaching token limit: "
                    f"{estimated_tokens} tokens (>{warning_threshold:.0f}, 80% of budget)"
                )

        self.logger.info(
            f"Token estimation for {content_type}: {estimated_tokens} tokens (within limits)"
        )
        return True

    def log_cost_tracking(self, token_usage: Dict[str, int], content_type: str) -> None:
        """Log cost tracking information."""
        if not self.settings.enable_cost_tracking:
            return

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

    def call_generative_model(
        self,
        prompt_str: str,
        pydantic_model_cls: Type[BaseModel],
        content_type_name: str,
        max_retries: Optional[int] = None,
        enable_quality_check: bool = True,
        use_optimizer: bool = True,
        prompt_context: Optional[PromptContext] = None,
        quality_validator: Optional[callable] = None,
    ) -> Tuple[Optional[BaseModel], Dict[str, int]]:
        """
        Call the generative model with retry logic, quality checks, and prompt refinement.

        Args:
            prompt_str: The prompt to send to the model
            pydantic_model_cls: The Pydantic model class for validation
            content_type_name: Human-readable name for the content type
            max_retries: Maximum number of retries (defaults to settings.max_retries)
            enable_quality_check: Whether to perform quality validation
            use_optimizer: Whether to use prompt optimization
            prompt_context: Context for prompt optimization
            quality_validator: Optional quality validation function

        Returns:
            Tuple of (validated_model_instance, token_usage_dict)
        """
        start_time = time.time()

        if max_retries is None:
            max_retries = self.settings.max_retries

        cumulative_tokens = {"input_tokens": 0, "output_tokens": 0}

        # Check if model is available
        if not self.model:
            self.logger.error(
                f"Generative model not initialized. Cannot generate {content_type_name}."
            )
            LLM_CALLS_TOTAL.labels(
                content_type=content_type_name, status="model_unavailable"
            ).inc()
            return None, cumulative_tokens

        # Optimize prompt if enabled
        if use_optimizer and prompt_context:
            try:
                prompt_str = self.prompt_optimizer.optimize_prompt(
                    prompt_str, prompt_context
                )
                self.logger.info(f"Optimized prompt for {content_type_name}")
            except Exception as e:
                self.logger.warning(
                    f"Prompt optimization failed for {content_type_name}: {e}"
                )

        # Check token limits before proceeding
        if not self.check_token_limits(prompt_str, content_type_name):
            self.logger.error(
                f"Token limit exceeded for {content_type_name}. Aborting LLM call."
            )
            LLM_CALLS_TOTAL.labels(
                content_type=content_type_name, status="token_limit_exceeded"
            ).inc()
            return None, cumulative_tokens

        # Keep track of prompt modifications
        current_prompt = prompt_str
        prompt_modifications = []

        # Retry loop with prompt refinement
        for attempt in range(max_retries + 1):
            try:
                self.logger.info(
                    f"Sending prompt to LLM for {content_type_name} (attempt {attempt + 1}/{max_retries + 1})..."
                )

                # Call LLM with timeout handling
                try:
                    future = self.executor.submit(self.model.generate_content, current_prompt)
                    llm_response = future.result(timeout=self.timeout_seconds)
                except FutureTimeoutError:
                    self.logger.error(
                        f"LLM call timed out after {self.timeout_seconds}s for {content_type_name} "
                        f"(attempt {attempt + 1}/{max_retries + 1})"
                    )
                    LLM_TIMEOUTS.labels(content_type=content_type_name).inc()
                    
                    if attempt < max_retries:
                        self.logger.info(f"Retrying after timeout...")
                        time.sleep(self.settings.retry_delay)
                        continue
                    else:
                        LLM_CALLS_TOTAL.labels(
                            content_type=content_type_name, status="timeout"
                        ).inc()
                        return None, cumulative_tokens

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
                cleaned_json_str = self.clean_llm_json_response(llm_response.text)
                parsed_json = json.loads(cleaned_json_str)
                validated_data = pydantic_model_cls(**parsed_json)

                # Quality check if enabled and validator provided
                if enable_quality_check and quality_validator and attempt < max_retries:
                    try:
                        quality_result = quality_validator(
                            validated_data, content_type_name.lower().replace(" ", "_")
                        )

                        if not quality_result.get("is_valid", True):
                            quality_issues = quality_result.get("validation_errors", [])
                            self.logger.warning(
                                f"Quality issues detected for {content_type_name}: {quality_issues}. "
                                f"Refining prompt and retrying..."
                            )
                            # Refine prompt based on quality issues
                            current_prompt = self.refine_prompt_for_quality(
                                current_prompt, quality_issues, prompt_modifications
                            )
                            prompt_modifications.extend(
                                [str(issue) for issue in quality_issues]
                            )
                            continue

                        # Log quality score if available
                        quality_score = quality_result.get("overall_score")
                        if quality_score is not None:
                            self.logger.info(
                                f"Quality score for {content_type_name}: {quality_score:.2f}"
                            )

                    except Exception as e:
                        self.logger.warning(
                            f"Quality validation failed for {content_type_name}: {e}"
                        )

                self.logger.info(
                    f"Successfully generated and validated {content_type_name} after {attempt + 1} attempt(s)."
                )

                # Log cost tracking
                self.log_cost_tracking(cumulative_tokens, content_type_name)

                # Record metrics
                LLM_CALLS_TOTAL.labels(
                    content_type=content_type_name, status="success"
                ).inc()
                LLM_CALL_DURATION.labels(content_type=content_type_name).observe(
                    time.time() - start_time
                )

                return validated_data, cumulative_tokens

            except (json.JSONDecodeError, PydanticValidationError) as e:
                error_type = type(e).__name__
                self.logger.warning(
                    f"Attempt {attempt + 1} failed for {content_type_name} with {error_type}: {str(e)[:200]}"
                )

                if attempt < max_retries:
                    # Refine prompt for better JSON structure
                    if isinstance(e, json.JSONDecodeError):
                        current_prompt = self.refine_prompt_for_json_error(
                            current_prompt, str(e)
                        )
                        prompt_modifications.append("json_structure_reminder")
                    else:  # PydanticValidationError
                        current_prompt = self.refine_prompt_for_validation_error(
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
                    LLM_CALLS_TOTAL.labels(
                        content_type=content_type_name, status="validation_failed"
                    ).inc()
                    return None, cumulative_tokens

            except Exception as e:
                self.logger.error(
                    f"Unexpected error generating {content_type_name}: {e}",
                    exc_info=True,
                )
                LLM_CALLS_TOTAL.labels(
                    content_type=content_type_name, status="error"
                ).inc()
                return None, cumulative_tokens

        # Should not reach here
        LLM_CALLS_TOTAL.labels(
            content_type=content_type_name, status="max_retries_exceeded"
        ).inc()
        return None, cumulative_tokens

    def is_available(self) -> bool:
        """Check if the LLM client is available and ready to use."""
        return self.model is not None
