"""
Simplified LLM Client - Clean interface for Vertex AI interactions
"""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Any, Dict, Optional, Tuple, Type

import vertexai
from pydantic import BaseModel
from vertexai.generative_models import GenerativeModel

from app.core.config.settings import Settings
from app.core.exceptions.custom_exceptions import ExternalServiceError
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
from app.services.prompts import PromptService


class SimpleLLMClient:
    """
    Simplified LLM client with single responsibility: Call Vertex AI.
    No complex retry logic, no quality refinement, just clean API calls.
    """

    # Map content types to their Pydantic models
    CONTENT_TYPE_MODELS = {
        "podcast_script": PodcastScript,
        "study_guide": StudyGuide,
        "one_pager_summary": OnePagerSummary,
        "detailed_reading": DetailedReadingMaterial,
        "faqs": FAQCollection,
        "flashcards": FlashcardCollection,
        "reading_questions": ReadingGuideQuestions,
    }

    # Map to prompt template names
    CONTENT_TYPE_PROMPTS = {
        "podcast_script": "podcast_script",
        "study_guide": "study_guide",
        "one_pager_summary": "one_pager_summary",
        "detailed_reading": "detailed_reading_material",
        "faqs": "faq_collection",
        "flashcards": "flashcards",
        "reading_questions": "reading_guide_questions",
    }

    def __init__(self, settings: Settings):
        """Initialize with minimal dependencies"""
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.prompt_service = PromptService()
        self.model = None
        
        # Set timeout with default of 120 seconds (2 minutes)
        self.timeout_seconds = getattr(settings, 'llm_timeout_seconds', 120)
        
        # Thread pool for timeout handling
        self.executor = ThreadPoolExecutor(max_workers=1)

        # Initialize Vertex AI
        self._initialize_vertex_ai()

    def _initialize_vertex_ai(self) -> None:
        """Initialize Vertex AI model"""
        try:
            vertexai.init(
                project=self.settings.gcp_project_id,
                location=self.settings.gcp_location,
            )

            if self.settings.gemini_model_name:
                self.model = GenerativeModel(self.settings.gemini_model_name)
                self.logger.info(
                    f"Initialized Gemini model: {self.settings.gemini_model_name}"
                )
            else:
                raise ValueError("No Gemini model name configured")

        except Exception as e:
            self.logger.error(f"Failed to initialize Vertex AI: {e}")
            raise ExternalServiceError(f"LLM initialization failed: {e}")

    async def generate_outline(
        self, syllabus_text: str, debug: bool = False
    ) -> Tuple[Optional[ContentOutline], Dict[str, int]]:
        """Generate content outline from syllabus"""
        prompt = self.prompt_service.get_prompt(
            "master_content_outline", syllabus_text=syllabus_text
        )

        content, token_usage = await self._call_llm(
            prompt=prompt,
            model_cls=ContentOutline,
            content_type="content_outline",
            debug=debug,
        )
        return content, token_usage

    async def generate_content_type(
        self, content_type: str, outline: ContentOutline, debug: bool = False
    ) -> Tuple[Optional[BaseModel], Dict[str, int]]:
        """Generate specific content type from outline"""
        if content_type not in self.CONTENT_TYPE_MODELS:
            raise ValueError(f"Unknown content type: {content_type}")

        # Get appropriate prompt template
        prompt_name = self.CONTENT_TYPE_PROMPTS[content_type]
        model_cls = self.CONTENT_TYPE_MODELS[content_type]

        # Generate prompt with outline
        prompt = self.prompt_service.get_prompt(
            prompt_name, outline_json=outline.model_dump_json()
        )

        content, token_usage = await self._call_llm(
            prompt=prompt, model_cls=model_cls, content_type=content_type, debug=debug
        )
        return content, token_usage

    async def _call_llm(
        self,
        prompt: str,
        model_cls: Type[BaseModel],
        content_type: str,
        debug: bool = False,
    ) -> Tuple[Optional[BaseModel], Dict[str, int]]:
        """
        Make a single LLM call with basic retry logic.

        Returns:
            Tuple of (parsed_content, token_usage)
        """
        if not self.model:
            raise ExternalServiceError("LLM model not initialized")

        token_usage = {"input_tokens": 0, "output_tokens": 0}
        max_retries = 2  # Simple retry for transient errors

        for attempt in range(max_retries + 1):
            try:
                # Log prompt in debug mode
                if debug:
                    self.logger.debug(f"Prompt for {content_type}:\n{prompt[:500]}...")

                # Make API call
                start_time = time.time()
                
                # Call LLM with timeout handling
                try:
                    future = self.executor.submit(self.model.generate_content, prompt)
                    response = future.result(timeout=self.timeout_seconds)
                except FutureTimeoutError:
                    self.logger.error(
                        f"LLM call timed out after {self.timeout_seconds}s for {content_type} "
                        f"(attempt {attempt + 1}/{max_retries + 1})"
                    )
                    
                    if attempt < max_retries:
                        self.logger.info(f"Retrying after timeout...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raise ExternalServiceError(
                            f"LLM call timed out after {self.timeout_seconds}s for {content_type}"
                        )
                
                duration = time.time() - start_time

                # Extract token usage
                if hasattr(response, "usage_metadata"):
                    token_usage["input_tokens"] = getattr(
                        response.usage_metadata, "prompt_token_count", 0
                    )
                    token_usage["output_tokens"] = getattr(
                        response.usage_metadata, "candidates_token_count", 0
                    )

                # Log response in debug mode
                if debug:
                    self.logger.debug(
                        f"Response for {content_type}:\n{response.text[:500]}..."
                    )

                # Parse response
                content = self._parse_response(response.text, model_cls, content_type)

                if content:
                    self.logger.info(
                        f"Generated {content_type} in {duration:.2f}s "
                        f"(tokens: {sum(token_usage.values())})"
                    )
                    return content, token_usage

            except json.JSONDecodeError as e:
                self.logger.warning(
                    f"JSON parse error for {content_type} (attempt {attempt + 1}): {e}"
                )
                if attempt == max_retries:
                    return None, token_usage

            except Exception as e:
                self.logger.error(
                    f"LLM call failed for {content_type} (attempt {attempt + 1}): {e}"
                )
                if attempt == max_retries:
                    raise ExternalServiceError(
                        f"Failed to generate {content_type}: {e}"
                    )

            # Simple backoff
            if attempt < max_retries:
                time.sleep(2**attempt)

        return None, token_usage

    def _parse_response(
        self, response_text: str, model_cls: Type[BaseModel], content_type: str
    ) -> Optional[BaseModel]:
        """Parse and validate LLM response"""
        try:
            # Clean JSON response
            cleaned_text = self._clean_json_response(response_text)

            # Parse JSON
            data = json.loads(cleaned_text)

            # Validate with Pydantic
            return model_cls(**data)

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON for {content_type}: {e}")
            raise

        except Exception as e:
            self.logger.error(f"Failed to validate {content_type}: {e}")
            return None

    def _clean_json_response(self, text: str) -> str:
        """Remove markdown code blocks and clean JSON"""
        cleaned = text.strip()

        # Remove markdown code blocks
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        return cleaned.strip()

    def is_available(self) -> bool:
        """Check if LLM client is ready"""
        return self.model is not None
