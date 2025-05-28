"""Content generation service for the AI Content Factory.

DEPRECATED: This service is deprecated and will be removed in a future version. 
Please use EnhancedMultiStepContentGenerationService from 
app.services.multi_step_content_generation instead.

This module handles the generation of various types of educational content using
the Gemini model and manages the content generation process.
"""

import logging
import json
import warnings
from typing import Dict, Any, Tuple, Optional
from google.cloud import aiplatform
from prometheus_client import Counter, Histogram

from app.core.config.settings import get_settings
from app.core.prompts.v1.content_generation import ContentGenerationPrompts

# Prometheus metrics
GEMINI_API_CALLS = Counter('gemini_api_calls_total', 'Total number of Gemini API calls')
GEMINI_API_DURATION = Histogram('gemini_api_duration_seconds', 'Time spent in Gemini API calls')

class ContentGenerationService:
    """DEPRECATED: Service for generating educational content using Gemini. 
    Use EnhancedMultiStepContentGenerationService instead."""
    
    def __init__(self):
        """Initialize the content generation service."""
        warnings.warn(
            "ContentGenerationService is deprecated and will be removed in a future version. "
            "Use EnhancedMultiStepContentGenerationService instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.settings = get_settings()
        self.prompts = ContentGenerationPrompts()
        
    def generate_content(self, syllabus_text: str) -> Tuple[Dict[str, Any], int]:
        """Generates comprehensive educational content from syllabus text.
        
        Args:
            syllabus_text: The text of the syllabus.
            
        Returns:
            Tuple[Dict[str, Any], int]: Generated content and status code.
        """
        try:
            # Initialize Vertex AI
            aiplatform.init(
                project=self.settings.gcp_project_id,
                location=self.settings.gcp_location
            )
            model = aiplatform.GenerativeModel(self.settings.gemini_model_name)
            
            # Generate the prompt
            generation_prompt = self.prompts.get_main_prompt(syllabus_text)
            
            # Log the API call
            logging.info(
                f"Calling Gemini model: {self.settings.gemini_model_name} "
                f"with prompt length {len(generation_prompt)} characters."
            )
            
            # Make the API call with timing
            GEMINI_API_CALLS.inc()
            with GEMINI_API_DURATION.time():
                response = model.generate_content(
                    generation_prompt,
                    generation_config={"response_mime_type": "application/json"},
                )
            
            # Parse and validate the response
            content_response = self._parse_gemini_response(response.text)
            logging.info("Content generated successfully.")
            
            return content_response, 200
            
        except Exception as e:
            logging.error(f"Error generating content: {e}", exc_info=True)
            return self._create_error_response(str(e)), 503
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parses and validates the Gemini response.
        
        Args:
            response_text: The raw response text from Gemini.
            
        Returns:
            Dict[str, Any]: Parsed and validated content.
            
        Raises:
            ValueError: If the response is invalid.
        """
        try:
            content = json.loads(response_text)
            is_valid, error_message = self._validate_content_structure(content)
            if not is_valid:
                raise ValueError(error_message)
            return content
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")
    
    def _validate_content_structure(self, content: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates the structure of generated content.
        
        Args:
            content: The content dictionary to validate.
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        required_fields = {
            'content_outline': str,
            'podcast_script': str,
            'study_guide': str,
            'one_pager_summary': str,
            'detailed_reading_material': str,
            'faqs': list,
            'flashcards': list,
            'reading_guide_questions': list
        }
        
        for field, expected_type in required_fields.items():
            if field not in content:
                return False, f"Missing required field: {field}"
            if not isinstance(content[field], expected_type):
                return False, f"Invalid type for {field}: expected {expected_type.__name__}, got {type(content[field]).__name__}"
        
        # Validate array contents
        if not all(isinstance(faq, dict) and 'question' in faq and 'answer' in faq for faq in content['faqs']):
            return False, "Invalid FAQ structure: each FAQ must have 'question' and 'answer' fields"
        
        if not all(isinstance(flashcard, dict) and 'term' in flashcard and 'definition' in flashcard for flashcard in content['flashcards']):
            return False, "Invalid flashcard structure: each flashcard must have 'term' and 'definition' fields"
        
        if not all(isinstance(q, str) for q in content['reading_guide_questions']):
            return False, "Invalid reading guide questions: all questions must be strings"
        
        return True, ""
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Creates a standardized error response.
        
        Args:
            error_message: The error message to include.
            
        Returns:
            Dict[str, Any]: A dictionary with error messages for all content types.
        """
        return {
            "content_outline": f"Error: {error_message}",
            "podcast_script": f"Error: {error_message}",
            "study_guide": f"Error: {error_message}",
            "one_pager_summary": f"Error: {error_message}",
            "detailed_reading_material": f"Error: {error_message}",
            "faqs": [],
            "flashcards": [],
            "reading_guide_questions": []
        } 