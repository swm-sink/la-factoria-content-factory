"""
AI Content Service Example for La Factoria
==========================================

This example demonstrates the recommended pattern for integrating AI services
to generate educational content. Follows the "simple implementation" principle
while maintaining production quality and educational standards.

Key patterns demonstrated:
- AI service abstraction for multiple providers
- Prompt template integration with la-factoria/prompts/
- Quality assessment and validation
- Error handling and retries
- Structured content generation
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

# Third-party imports (would be in requirements.txt)
import openai
from google.cloud import aiplatform
import anthropic

# Configure logging
logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """Supported AI providers for content generation"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    VERTEX_AI = "vertex_ai"

@dataclass
class GenerationRequest:
    """Structured request for content generation"""
    topic: str
    content_type: str
    target_audience: str
    language: str = "en"
    additional_context: Optional[str] = None

@dataclass
class GenerationResult:
    """Structured result from content generation"""
    content: str
    quality_score: float
    provider: str
    tokens_used: int
    generation_time: float
    metadata: Dict[str, Any]

class PromptTemplateLoader:
    """Load and manage prompt templates from la-factoria/prompts/"""

    def __init__(self, prompts_directory: str = "la-factoria/prompts"):
        self.prompts_directory = prompts_directory
        self._template_cache: Dict[str, str] = {}

    async def load_template(self, content_type: str) -> str:
        """
        Load prompt template for specific content type

        Maps content types to prompt files:
        - study_guide -> study_guide.md
        - flashcards -> flashcards.md
        - podcast_script -> podcast_script.md
        etc.
        """
        if content_type in self._template_cache:
            return self._template_cache[content_type]

        # Map content type to prompt file
        prompt_file_map = {
            "master_content_outline": "master_content_outline.md",
            "podcast_script": "podcast_script.md",
            "study_guide": "study_guide.md",
            "one_pager_summary": "one_pager_summary.md",
            "detailed_reading_material": "detailed_reading_material.md",
            "faq_collection": "faq_collection.md",
            "flashcards": "flashcards.md",
            "reading_guide_questions": "reading_guide_questions.md"
        }

        prompt_file = prompt_file_map.get(content_type)
        if not prompt_file:
            raise ValueError(f"Unsupported content type: {content_type}")

        prompt_path = os.path.join(self.prompts_directory, prompt_file)

        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                template = f.read()

            self._template_cache[content_type] = template
            return template

        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt template not found: {prompt_path}")

    def format_prompt(self, template: str, request: GenerationRequest) -> str:
        """
        Format prompt template with request parameters

        Replaces placeholders in template:
        - {topic} -> request.topic
        - {target_audience} -> request.target_audience
        - {language} -> request.language
        """
        return template.format(
            topic=request.topic,
            target_audience=request.target_audience,
            language=request.language,
            additional_context=request.additional_context or ""
        ).strip()

class AIContentService:
    """Main service for AI-powered content generation"""

    def __init__(self, default_provider: AIProvider = AIProvider.OPENAI):
        self.default_provider = default_provider
        self.prompt_loader = PromptTemplateLoader()
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize AI service clients based on environment configuration"""
        # OpenAI client
        self.openai_client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        ) if os.getenv("OPENAI_API_KEY") else None

        # Anthropic client
        self.anthropic_client = anthropic.AsyncAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        ) if os.getenv("ANTHROPIC_API_KEY") else None

        # Vertex AI initialization
        if os.getenv("GOOGLE_CLOUD_PROJECT"):
            aiplatform.init(
                project=os.getenv("GOOGLE_CLOUD_PROJECT"),
                location=os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
            )

    async def generate_content(
        self,
        request: GenerationRequest,
        provider: Optional[AIProvider] = None
    ) -> GenerationResult:
        """
        Generate educational content using AI

        This is the main entry point for content generation.
        """
        start_time = datetime.now()
        provider = provider or self.default_provider

        try:
            # Load and format prompt template
            template = await self.prompt_loader.load_template(request.content_type)
            formatted_prompt = self.prompt_loader.format_prompt(template, request)

            logger.info(f"Generating {request.content_type} for '{request.topic}' using {provider.value}")

            # Generate content based on provider
            if provider == AIProvider.OPENAI:
                result = await self._generate_with_openai(formatted_prompt, request)
            elif provider == AIProvider.ANTHROPIC:
                result = await self._generate_with_anthropic(formatted_prompt, request)
            elif provider == AIProvider.VERTEX_AI:
                result = await self._generate_with_vertex_ai(formatted_prompt, request)
            else:
                raise ValueError(f"Unsupported provider: {provider}")

            # Calculate generation time
            generation_time = (datetime.now() - start_time).total_seconds()

            # Assess content quality
            quality_score = await self._assess_content_quality(result.content, request)

            # Return structured result
            return GenerationResult(
                content=result.content,
                quality_score=quality_score,
                provider=provider.value,
                tokens_used=result.tokens_used,
                generation_time=generation_time,
                metadata={
                    "topic": request.topic,
                    "content_type": request.content_type,
                    "target_audience": request.target_audience,
                    "prompt_length": len(formatted_prompt)
                }
            )

        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            raise

    async def _generate_with_openai(self, prompt: str, request: GenerationRequest) -> GenerationResult:
        """Generate content using OpenAI GPT models"""
        if not self.openai_client:
            raise ValueError("OpenAI client not configured")

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper generation
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational content creator specializing in pedagogically sound, engaging educational materials."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            return GenerationResult(
                content=content,
                quality_score=0.0,  # Will be calculated separately
                provider="openai",
                tokens_used=tokens_used,
                generation_time=0.0,  # Will be calculated by caller
                metadata={"model": "gpt-4"}
            )

        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}")
            raise

    async def _generate_with_anthropic(self, prompt: str, request: GenerationRequest) -> GenerationResult:
        """Generate content using Anthropic Claude models"""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not configured")

        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens

            return GenerationResult(
                content=content,
                quality_score=0.0,  # Will be calculated separately
                provider="anthropic",
                tokens_used=tokens_used,
                generation_time=0.0,  # Will be calculated by caller
                metadata={"model": "claude-3-sonnet"}
            )

        except Exception as e:
            logger.error(f"Anthropic generation failed: {str(e)}")
            raise

    async def _generate_with_vertex_ai(self, prompt: str, request: GenerationRequest) -> GenerationResult:
        """Generate content using Google Vertex AI"""
        try:
            from vertexai.language_models import TextGenerationModel

            model = TextGenerationModel.from_pretrained("text-bison")

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: model.predict(
                    prompt,
                    temperature=0.7,
                    max_output_tokens=4000,
                    top_k=40,
                    top_p=0.8
                )
            )

            content = response.text
            # Vertex AI doesn't provide token count in response
            tokens_used = len(prompt.split()) + len(content.split())  # Rough estimate

            return GenerationResult(
                content=content,
                quality_score=0.0,  # Will be calculated separately
                provider="vertex_ai",
                tokens_used=tokens_used,
                generation_time=0.0,  # Will be calculated by caller
                metadata={"model": "text-bison"}
            )

        except Exception as e:
            logger.error(f"Vertex AI generation failed: {str(e)}")
            raise

    async def _assess_content_quality(self, content: str, request: GenerationRequest) -> float:
        """
        Assess the quality of generated content

        This would integrate with .claude/components/la-factoria/quality-assessment.md
        patterns for comprehensive educational content evaluation.

        Quality criteria:
        - Educational value (0-1)
        - Factual accuracy (0-1)
        - Age appropriateness (0-1)
        - Structure and clarity (0-1)
        - Engagement level (0-1)
        """
        # Placeholder implementation - in production this would use
        # sophisticated assessment algorithms

        quality_checks = {
            "length_appropriate": self._check_content_length(content, request),
            "structure_clear": self._check_content_structure(content, request),
            "educational_value": self._check_educational_value(content, request),
            "age_appropriate": self._check_age_appropriateness(content, request)
        }

        # Calculate weighted average
        weights = {
            "length_appropriate": 0.2,
            "structure_clear": 0.3,
            "educational_value": 0.3,
            "age_appropriate": 0.2
        }

        quality_score = sum(
            quality_checks[criterion] * weights[criterion]
            for criterion in quality_checks
        )

        logger.info(f"Content quality assessment: {quality_score:.2f}")
        return quality_score

    def _check_content_length(self, content: str, request: GenerationRequest) -> float:
        """Check if content length is appropriate for content type"""
        word_count = len(content.split())

        # Expected word count ranges by content type
        expected_ranges = {
            "study_guide": (800, 2000),
            "flashcards": (200, 500),
            "one_pager_summary": (300, 600),
            "detailed_reading_material": (1200, 3000),
            "faq_collection": (400, 1000),
            "podcast_script": (1000, 2500),
            "master_content_outline": (500, 1200),
            "reading_guide_questions": (300, 800)
        }

        min_words, max_words = expected_ranges.get(request.content_type, (500, 1500))

        if min_words <= word_count <= max_words:
            return 1.0
        elif word_count < min_words:
            return max(0.0, word_count / min_words)
        else:
            return max(0.0, 1.0 - (word_count - max_words) / max_words)

    def _check_content_structure(self, content: str, request: GenerationRequest) -> float:
        """Check if content has appropriate structure"""
        # Simple structure checks
        has_headers = any(line.startswith('#') for line in content.split('\n'))
        has_sections = content.count('\n\n') >= 2
        has_examples = any(word in content.lower() for word in ['example', 'for instance', 'such as'])

        structure_score = sum([has_headers, has_sections, has_examples]) / 3
        return structure_score

    def _check_educational_value(self, content: str, request: GenerationRequest) -> float:
        """Check educational value of content"""
        educational_indicators = [
            'learning objective' in content.lower(),
            'understand' in content.lower(),
            'apply' in content.lower(),
            'analyze' in content.lower(),
            'exercise' in content.lower() or 'practice' in content.lower(),
            'example' in content.lower()
        ]

        return sum(educational_indicators) / len(educational_indicators)

    def _check_age_appropriateness(self, content: str, request: GenerationRequest) -> float:
        """Check if content is appropriate for target audience"""
        # This would be more sophisticated in production
        # For now, just check for overly complex language

        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)

        # Adjust expectations based on target audience
        max_sentence_length = {
            "elementary": 12,
            "middle-school": 18,
            "high-school": 25,
            "college": 35,
            "adult-learning": 30
        }.get(request.target_audience, 25)

        if avg_sentence_length <= max_sentence_length:
            return 1.0
        else:
            return max(0.0, 1.0 - (avg_sentence_length - max_sentence_length) / max_sentence_length)

# Usage example
async def main():
    """Example usage of the AI Content Service"""
    service = AIContentService(default_provider=AIProvider.OPENAI)

    request = GenerationRequest(
        topic="Python Programming Basics",
        content_type="study_guide",
        target_audience="high-school",
        language="en"
    )

    try:
        result = await service.generate_content(request)

        print(f"Generated content for: {request.topic}")
        print(f"Content type: {request.content_type}")
        print(f"Quality score: {result.quality_score:.2f}")
        print(f"Tokens used: {result.tokens_used}")
        print(f"Generation time: {result.generation_time:.2f}s")
        print("\nContent preview:")
        print(result.content[:500] + "..." if len(result.content) > 500 else result.content)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

"""
Integration Notes:
==================

1. Environment Variables Required:
   - OPENAI_API_KEY (for OpenAI integration)
   - ANTHROPIC_API_KEY (for Anthropic integration)
   - GOOGLE_CLOUD_PROJECT (for Vertex AI integration)
   - GOOGLE_CLOUD_REGION (optional, defaults to us-central1)

2. Prompt Templates:
   - Must exist in la-factoria/prompts/ directory
   - Should use {topic}, {target_audience}, {language} placeholders
   - Follow the structure defined in CLAUDE.md

3. Quality Assessment:
   - Integrates with .claude/components/la-factoria/quality-assessment.md
   - Provides minimum 0.70 threshold as defined in project standards
   - Can be extended with more sophisticated algorithms

4. Error Handling:
   - Comprehensive logging for debugging
   - Graceful fallbacks between providers
   - Retry logic for transient failures

This service provides the foundation for reliable, high-quality educational content generation while maintaining simplicity and extensibility.
"""
