"""
Educational Content Generation Service for La Factoria
Main service orchestrating AI generation with educational quality assessment
Following patterns from la-factoria-prompt-integration.md lines 140-291
"""

import asyncio
import logging
import time
import json
import uuid
from typing import Dict, Any, Optional, List

from ..core.config import settings
from ..models.educational import LearningObjective, LaFactoriaContentType
from .prompt_loader import PromptTemplateLoader
from .ai_providers import AIProviderManager
from .quality_assessor import EducationalQualityAssessor

logger = logging.getLogger(__name__)

class EducationalContentService:
    """Educational content generation service using La Factoria prompts"""

    def __init__(self):
        self.prompt_loader = PromptTemplateLoader()
        self.ai_provider = AIProviderManager()
        self.quality_assessor = EducationalQualityAssessor()
        self._initialized = False

    async def initialize(self):
        """Initialize all service components"""
        if self._initialized:
            return

        try:
            await self.prompt_loader.initialize()
            logger.info("Educational content service initialized successfully")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize educational content service: {e}")
            raise

    async def generate_content(
        self,
        content_type: str,
        topic: str,
        age_group: str = "general",
        learning_objectives: Optional[List[LearningObjective]] = None,
        additional_requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate educational content using La Factoria prompts with quality assessment

        Args:
            content_type: One of the 8 supported La Factoria content types
            topic: Educational topic or subject
            age_group: Target learning level
            learning_objectives: Specific learning objectives to incorporate
            additional_requirements: Additional requirements or constraints

        Returns:
            Dictionary with generated content, quality metrics, and metadata
        """
        # Ensure service is initialized
        if not self._initialized:
            await self.initialize()

        start_time = time.time()

        # Validate content type
        supported_types = [ct.value for ct in LaFactoriaContentType]
        if content_type not in supported_types:
            raise ValueError(f"Unsupported content type: {content_type}")

        try:
            logger.info(f"Generating {content_type} for topic: '{topic}' (age_group: {age_group})")

            # Load the appropriate prompt template
            template = await self.prompt_loader.load_template(content_type)

            # Prepare variables for template compilation
            variables = {
                "topic": topic,
                "age_group": age_group,
                "syllabus_text": topic,  # For backward compatibility with existing prompts
                "additional_requirements": additional_requirements or "",
            }

            # Add learning objectives if provided
            if learning_objectives:
                variables["learning_objectives"] = [
                    {
                        "cognitive_level": obj.cognitive_level.value if hasattr(obj.cognitive_level, 'value') else obj.cognitive_level,
                        "subject_area": obj.subject_area,
                        "specific_skill": obj.specific_skill,
                        "measurable_outcome": obj.measurable_outcome,
                        "difficulty_level": obj.difficulty_level
                    }
                    for obj in learning_objectives
                ]

            # Compile the template with variables
            compiled_prompt = self.prompt_loader.compile_template(template, variables)

            # Generate content using AI provider with fallback
            ai_response = await self.ai_provider.generate_content(
                prompt=compiled_prompt,
                content_type=content_type,
                max_tokens=self._get_max_tokens_for_type(content_type)
            )

            # Parse the generated content (handles JSON extraction from markdown)
            parsed_content = self._parse_generated_content(ai_response.content, content_type)

            # Assess educational quality using learning science metrics
            quality_metrics = await self.quality_assessor.assess_content_quality(
                content=parsed_content,
                content_type=content_type,
                age_group=age_group,
                learning_objectives=learning_objectives
            )

            # Calculate generation metrics
            generation_time = (time.time() - start_time) * 1000  # milliseconds

            # Create comprehensive result with educational metadata
            result = {
                "id": str(uuid.uuid4()),
                "content_type": content_type,
                "topic": topic,
                "age_group": age_group,
                "generated_content": parsed_content,
                "quality_metrics": quality_metrics,
                "metadata": {
                    "generation_duration_ms": int(generation_time),
                    "tokens_used": ai_response.tokens_used,
                    "prompt_template": content_type,
                    "ai_provider": ai_response.provider,
                    "ai_model": ai_response.model,
                    "template_variables": variables,
                    "educational_effectiveness_score": quality_metrics.get("educational_effectiveness", 0),
                    "cognitive_load_metrics": quality_metrics.get("cognitive_load_metrics", {}),
                    "readability_score": quality_metrics.get("readability_score", 0),
                    "meets_quality_threshold": quality_metrics.get("meets_quality_threshold", False)
                }
            }

            # Log generation success
            logger.info(
                f"Content generated successfully: {content_type} for '{topic}' "
                f"(quality: {quality_metrics.get('overall_quality_score', 0):.2f}, "
                f"time: {generation_time:.0f}ms)"
            )

            return result

        except Exception as e:
            logger.error(f"Content generation failed for {content_type}: {e}")
            raise

    def _get_max_tokens_for_type(self, content_type: str) -> int:
        """Get appropriate token limits for each La Factoria content type"""
        token_limits = {
            "flashcards": 2000,
            "one_pager_summary": 1500,
            "faq_collection": 3000,
            "reading_guide_questions": 2000,
            "study_guide": 4000,
            "detailed_reading_material": 5000,
            "podcast_script": 4000,
            "master_content_outline": 3000
        }
        return token_limits.get(content_type, 3000)

    def _parse_generated_content(self, raw_content: str, content_type: str) -> Dict[str, Any]:
        """
        Parse AI-generated content based on expected structure

        La Factoria prompts are designed to return JSON, but we handle various formats
        """
        try:
            # Try to parse as JSON first (our prompts request JSON output)
            if raw_content.strip().startswith('{'):
                return json.loads(raw_content)

            # Extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            # Extract JSON from any code block
            code_block_match = re.search(r'```\s*(\{.*?\})\s*```', raw_content, re.DOTALL)
            if code_block_match:
                try:
                    return json.loads(code_block_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Look for JSON-like structure without code blocks
            json_like_match = re.search(r'(\{[^{}]*\{.*?\}[^{}]*\})', raw_content, re.DOTALL)
            if json_like_match:
                try:
                    return json.loads(json_like_match.group(1))
                except json.JSONDecodeError:
                    pass

            # Fallback: return as structured text based on content type
            logger.warning(f"Could not parse JSON for {content_type}, creating structured fallback")
            return self._create_structured_fallback(raw_content, content_type)

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed for {content_type}: {e}")
            return self._create_structured_fallback(raw_content, content_type)

    def _create_structured_fallback(self, raw_content: str, content_type: str) -> Dict[str, Any]:
        """Create structured content when JSON parsing fails"""

        # Basic structure based on content type
        base_structure = {
            "title": f"Generated {content_type.replace('_', ' ').title()}",
            "content": raw_content,
            "raw_output": True,
            "parsing_note": "Content was generated as text and structured automatically"
        }

        # Content type specific enhancements
        if content_type == "flashcards":
            # Try to extract Q&A pairs
            lines = raw_content.split('\n')
            cards = []
            current_card = {}

            for line in lines:
                line = line.strip()
                if line.startswith('Q:') or line.startswith('Question:'):
                    if current_card:
                        cards.append(current_card)
                    current_card = {"question": line.replace('Q:', '').replace('Question:', '').strip()}
                elif line.startswith('A:') or line.startswith('Answer:'):
                    if current_card:
                        current_card["answer"] = line.replace('A:', '').replace('Answer:', '').strip()

            if current_card:
                cards.append(current_card)

            if cards:
                base_structure["flashcards"] = cards

        elif content_type == "faq_collection":
            # Try to extract FAQ pairs
            import re
            faq_pattern = r'(?:Q|Question):\s*(.*?)\n(?:A|Answer):\s*(.*?)(?=\n(?:Q|Question):|$)'
            faqs = re.findall(faq_pattern, raw_content, re.DOTALL | re.IGNORECASE)

            if faqs:
                base_structure["faqs"] = [
                    {"question": q.strip(), "answer": a.strip()}
                    for q, a in faqs
                ]

        elif content_type in ["study_guide", "detailed_reading_material"]:
            # Try to extract sections
            sections = raw_content.split('\n\n')
            if len(sections) > 1:
                base_structure["sections"] = [
                    {"title": f"Section {i+1}", "content": section.strip()}
                    for i, section in enumerate(sections) if section.strip()
                ]

        return base_structure

    async def generate_multiple_content_types(
        self,
        topic: str,
        content_types: List[str],
        age_group: str = "general",
        learning_objectives: Optional[List[LearningObjective]] = None,
        additional_requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate multiple content types for the same topic concurrently

        Useful for creating comprehensive educational packages
        """
        if not content_types:
            raise ValueError("At least one content type must be specified")

        # Validate all content types
        supported_types = [ct.value for ct in LaFactoriaContentType]
        invalid_types = [ct for ct in content_types if ct not in supported_types]
        if invalid_types:
            raise ValueError(f"Unsupported content types: {invalid_types}")

        logger.info(f"Generating {len(content_types)} content types for topic: '{topic}'")

        # Generate all content types concurrently
        tasks = [
            self.generate_content(
                content_type=content_type,
                topic=topic,
                age_group=age_group,
                learning_objectives=learning_objectives,
                additional_requirements=additional_requirements
            )
            for content_type in content_types
        ]

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results and separate successes from failures
            generated_content = {}
            errors = {}

            for i, result in enumerate(results):
                content_type = content_types[i]

                if isinstance(result, Exception):
                    errors[content_type] = str(result)
                    logger.error(f"Failed to generate {content_type}: {result}")
                else:
                    generated_content[content_type] = result

            # Calculate overall metrics
            total_generation_time = sum(
                content.get("metadata", {}).get("generation_duration_ms", 0)
                for content in generated_content.values()
            )

            average_quality_score = sum(
                content.get("quality_metrics", {}).get("overall_quality_score", 0)
                for content in generated_content.values()
            ) / len(generated_content) if generated_content else 0

            return {
                "topic": topic,
                "age_group": age_group,
                "requested_types": content_types,
                "generated_content": generated_content,
                "errors": errors,
                "summary": {
                    "successful_generations": len(generated_content),
                    "failed_generations": len(errors),
                    "total_generation_time_ms": total_generation_time,
                    "average_quality_score": round(average_quality_score, 3)
                }
            }

        except Exception as e:
            logger.error(f"Batch content generation failed: {e}")
            raise

    async def get_content_type_info(self) -> Dict[str, Any]:
        """Get information about supported content types"""
        if not self._initialized:
            await self.initialize()

        return {
            "supported_types": self.prompt_loader.get_supported_content_types(),
            "template_stats": self.prompt_loader.get_template_stats(),
            "ai_provider_stats": self.ai_provider.get_provider_stats(),
            "quality_thresholds": {
                "overall_minimum": settings.QUALITY_THRESHOLD_OVERALL,
                "educational_minimum": settings.QUALITY_THRESHOLD_EDUCATIONAL,
                "factual_minimum": settings.QUALITY_THRESHOLD_FACTUAL
            }
        }

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for the educational content service"""
        health_status = {
            "service_initialized": self._initialized,
            "timestamp": time.time()
        }

        try:
            # Check prompt loader
            if self._initialized:
                health_status["prompt_loader"] = "healthy"
                health_status["template_stats"] = self.prompt_loader.get_template_stats()
            else:
                health_status["prompt_loader"] = "not_initialized"

            # Check AI providers
            health_status["ai_providers"] = await self.ai_provider.health_check()

            # Check quality assessor
            health_status["quality_assessor"] = "healthy"  # Placeholder

            # Overall status
            all_healthy = (
                health_status["prompt_loader"] == "healthy" and
                all(status == "healthy" for status in health_status["ai_providers"].values())
            )
            health_status["overall_status"] = "healthy" if all_healthy else "degraded"

        except Exception as e:
            health_status["overall_status"] = "unhealthy"
            health_status["error"] = str(e)

        return health_status
