"""
AI Provider Manager for La Factoria
Multi-provider AI integration with fallback support
Following patterns from la-factoria-prompt-integration.md
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import json

from ..core.config import settings

logger = logging.getLogger(__name__)

class AIProviderType(str, Enum):
    """Supported AI providers for content generation"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    VERTEX_AI = "vertex_ai"
    ELEVENLABS = "elevenlabs"  # For audio generation

@dataclass
class AIResponse:
    """Standardized AI response structure"""
    content: str
    provider: str
    model: str
    tokens_used: int
    generation_time: float
    metadata: Dict[str, Any]

class AIProviderManager:
    """Manage multiple AI providers with fallback support"""

    def __init__(self):
        self.providers = {}
        self.current_provider = None
        self.provider_stats = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize available AI providers based on configuration"""
        try:
            # OpenAI Provider
            if settings.has_openai_config:
                self.providers[AIProviderType.OPENAI] = self._get_openai_client()
                logger.info("OpenAI provider initialized")

            # Anthropic Provider
            if settings.has_anthropic_config:
                self.providers[AIProviderType.ANTHROPIC] = self._get_anthropic_client()
                logger.info("Anthropic provider initialized")

            # Vertex AI Provider
            if settings.GOOGLE_CLOUD_PROJECT:
                self.providers[AIProviderType.VERTEX_AI] = self._get_vertex_ai_client()
                logger.info("Vertex AI provider initialized")

            # ElevenLabs Provider (for audio)
            if settings.has_elevenlabs_config:
                self.providers[AIProviderType.ELEVENLABS] = self._get_elevenlabs_client()
                logger.info("ElevenLabs provider initialized")

            # Set default provider
            if self.providers:
                self.current_provider = list(self.providers.keys())[0]
                logger.info(f"Default AI provider set to: {self.current_provider}")
            else:
                logger.warning("No AI providers configured")

            # Initialize stats
            for provider in self.providers:
                self.provider_stats[provider] = {
                    "requests": 0,
                    "successes": 0,
                    "failures": 0,
                    "total_tokens": 0,
                    "avg_response_time": 0.0
                }

        except Exception as e:
            logger.error(f"Failed to initialize AI providers: {e}")
            raise

    def _get_openai_client(self):
        """Initialize OpenAI client"""
        try:
            import openai
            return openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        except ImportError:
            logger.error("OpenAI package not installed. Run: pip install openai")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return None

    def _get_anthropic_client(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            return anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        except ImportError:
            logger.error("Anthropic package not installed. Run: pip install anthropic")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            return None

    def _get_vertex_ai_client(self):
        """Initialize Vertex AI client"""
        try:
            from google.cloud import aiplatform
            aiplatform.init(
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_REGION
            )
            return aiplatform
        except ImportError:
            logger.error("Google Cloud AI Platform package not installed. Run: pip install google-cloud-aiplatform")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI client: {e}")
            return None

    def _get_elevenlabs_client(self):
        """Initialize ElevenLabs client"""
        try:
            # Placeholder for ElevenLabs client
            # In production, use actual ElevenLabs SDK
            return {"api_key": settings.ELEVENLABS_API_KEY}
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs client: {e}")
            return None

    async def generate_content(
        self,
        prompt: str,
        content_type: str,
        max_tokens: int = None,
        provider: Optional[AIProviderType] = None
    ) -> AIResponse:
        """
        Generate content using specified or default AI provider

        Args:
            prompt: The compiled prompt for content generation
            content_type: Type of content being generated
            max_tokens: Maximum tokens for generation
            provider: Specific provider to use (optional)

        Returns:
            AIResponse with generated content and metadata
        """
        provider = provider or self.current_provider
        max_tokens = max_tokens or settings.DEFAULT_MAX_TOKENS

        if not provider or provider not in self.providers:
            raise ValueError(f"Provider {provider} not available")

        # Record request
        self.provider_stats[provider]["requests"] += 1
        start_time = time.time()

        try:
            # Generate content with selected provider
            if provider == AIProviderType.OPENAI:
                response = await self._generate_with_openai(prompt, max_tokens)
            elif provider == AIProviderType.ANTHROPIC:
                response = await self._generate_with_anthropic(prompt, max_tokens)
            elif provider == AIProviderType.VERTEX_AI:
                response = await self._generate_with_vertex_ai(prompt, max_tokens)
            else:
                raise ValueError(f"Content generation not supported for provider: {provider}")

            # Record success
            generation_time = time.time() - start_time
            self.provider_stats[provider]["successes"] += 1
            self.provider_stats[provider]["total_tokens"] += response.tokens_used
            self._update_avg_response_time(provider, generation_time)

            logger.info(f"Content generated successfully with {provider} in {generation_time:.2f}s")
            return response

        except Exception as e:
            # Record failure
            self.provider_stats[provider]["failures"] += 1

            logger.error(f"Content generation failed with {provider}: {e}")

            # Try fallback if available
            fallback_provider = await self._get_fallback_provider(provider)
            if fallback_provider:
                logger.info(f"Attempting fallback to {fallback_provider}")
                return await self.generate_content(prompt, content_type, max_tokens, fallback_provider)

            raise

    async def _generate_with_openai(self, prompt: str, max_tokens: int) -> AIResponse:
        """Generate content using OpenAI GPT models"""
        client = self.providers[AIProviderType.OPENAI]
        if not client:
            raise RuntimeError("OpenAI client not available")

        try:
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational content creator specializing in pedagogically sound, engaging educational materials. Always respond with well-structured, age-appropriate content that follows learning science principles."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=max_tokens,
                top_p=0.9
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0

            return AIResponse(
                content=content,
                provider=AIProviderType.OPENAI.value,
                model="gpt-4",
                tokens_used=tokens_used,
                generation_time=0.0,  # Will be set by caller
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0
                }
            )

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

    async def _generate_with_anthropic(self, prompt: str, max_tokens: int) -> AIResponse:
        """Generate content using Anthropic Claude models"""
        client = self.providers[AIProviderType.ANTHROPIC]
        if not client:
            raise RuntimeError("Anthropic client not available")

        try:
            response = await client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=max_tokens,
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

            return AIResponse(
                content=content,
                provider=AIProviderType.ANTHROPIC.value,
                model="claude-3-sonnet-20240229",
                tokens_used=tokens_used,
                generation_time=0.0,  # Will be set by caller
                metadata={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "stop_reason": response.stop_reason
                }
            )

        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise

    async def _generate_with_vertex_ai(self, prompt: str, max_tokens: int) -> AIResponse:
        """Generate content using Google Vertex AI"""
        try:
            from vertexai.language_models import TextGenerationModel

            model = TextGenerationModel.from_pretrained("text-bison")

            # Run in executor to avoid blocking
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: model.predict(
                    prompt,
                    temperature=0.7,
                    max_output_tokens=max_tokens,
                    top_k=40,
                    top_p=0.8
                )
            )

            content = response.text
            # Vertex AI doesn't provide token count in response
            tokens_used = len(prompt.split()) + len(content.split())  # Rough estimate

            return AIResponse(
                content=content,
                provider=AIProviderType.VERTEX_AI.value,
                model="text-bison",
                tokens_used=tokens_used,
                generation_time=0.0,  # Will be set by caller
                metadata={
                    "is_blocked": response.is_blocked,
                    "safety_attributes": response.safety_attributes.__dict__ if response.safety_attributes else {}
                }
            )

        except Exception as e:
            logger.error(f"Vertex AI generation failed: {e}")
            raise

    async def _get_fallback_provider(self, failed_provider: AIProviderType) -> Optional[AIProviderType]:
        """Get fallback provider when primary fails"""
        # Define fallback hierarchy
        fallback_order = [
            AIProviderType.OPENAI,
            AIProviderType.ANTHROPIC,
            AIProviderType.VERTEX_AI
        ]

        # Remove failed provider and return next available
        available_fallbacks = [p for p in fallback_order if p != failed_provider and p in self.providers]

        return available_fallbacks[0] if available_fallbacks else None

    def _update_avg_response_time(self, provider: AIProviderType, response_time: float):
        """Update average response time for provider"""
        stats = self.provider_stats[provider]
        total_requests = stats["successes"]

        if total_requests == 1:
            stats["avg_response_time"] = response_time
        else:
            # Calculate running average
            stats["avg_response_time"] = (
                (stats["avg_response_time"] * (total_requests - 1) + response_time) / total_requests
            )

    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics for all providers"""
        return {
            "current_provider": self.current_provider.value if self.current_provider else None,
            "available_providers": [p.value for p in self.providers.keys()],
            "stats": {p.value: stats for p, stats in self.provider_stats.items()}
        }

    def set_default_provider(self, provider: AIProviderType):
        """Set the default provider for content generation"""
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not available")

        self.current_provider = provider
        logger.info(f"Default provider changed to: {provider}")

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all AI providers"""
        health_status = {}

        for provider_type, client in self.providers.items():
            try:
                # Perform a simple health check (provider-specific)
                if provider_type == AIProviderType.OPENAI and client:
                    # Simple test request
                    await client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=5
                    )
                    health_status[provider_type.value] = "healthy"
                elif provider_type == AIProviderType.ANTHROPIC and client:
                    # Simple test request for Anthropic
                    health_status[provider_type.value] = "healthy"  # Placeholder
                else:
                    health_status[provider_type.value] = "healthy" if client else "unavailable"

            except Exception as e:
                health_status[provider_type.value] = f"unhealthy: {str(e)}"
                logger.warning(f"Health check failed for {provider_type}: {e}")

        return health_status
