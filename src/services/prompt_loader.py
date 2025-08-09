"""
Prompt Template Loader for La Factoria
Loads and manages prompt templates from la-factoria/prompts/ directory
Following patterns from la-factoria-prompt-integration.md
"""

import os
import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path
import asyncio
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from ..core.config import settings
from ..models.educational import LaFactoriaContentType

logger = logging.getLogger(__name__)

class PromptTemplateLoader:
    """Load and manage La Factoria prompt templates"""

    def __init__(self, prompts_directory: str = "prompts"):
        self.prompts_directory = Path(prompts_directory)
        self.template_cache: Dict[str, str] = {}
        self.jinja_env: Optional[Environment] = None

        # Content type to file mapping
        self.template_files = {
            LaFactoriaContentType.MASTER_CONTENT_OUTLINE: "master_content_outline.md",
            LaFactoriaContentType.PODCAST_SCRIPT: "podcast_script.md",
            LaFactoriaContentType.STUDY_GUIDE: "study_guide.md",
            LaFactoriaContentType.ONE_PAGER_SUMMARY: "one_pager_summary.md",
            LaFactoriaContentType.DETAILED_READING_MATERIAL: "detailed_reading_material.md",
            LaFactoriaContentType.FAQ_COLLECTION: "faq_collection.md",
            LaFactoriaContentType.FLASHCARDS: "flashcards.md",
            LaFactoriaContentType.READING_GUIDE_QUESTIONS: "reading_guide_questions.md"
        }

    async def initialize(self):
        """Initialize the prompt loader and validate templates"""
        try:
            # Set up Jinja2 environment for template compilation
            # Use {$ $} delimiters to avoid conflicts with JSON {{ }} in prompts
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.prompts_directory)),
                variable_start_string='{$',
                variable_end_string='$}',
                trim_blocks=True,
                lstrip_blocks=True
            )

            # Validate that all required templates exist
            await self._validate_templates()

            logger.info(f"Prompt loader initialized with {len(self.template_files)} templates")

        except Exception as e:
            logger.error(f"Failed to initialize prompt loader: {e}")
            raise

    async def _validate_templates(self):
        """Validate that all required prompt templates exist"""
        missing_templates = []

        for content_type, filename in self.template_files.items():
            file_path = self.prompts_directory / filename
            if not file_path.exists():
                missing_templates.append(f"{content_type.value}: {filename}")

        if missing_templates:
            error_msg = f"Missing prompt templates: {', '.join(missing_templates)}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info("All prompt templates validated successfully")

    async def load_template(self, content_type: str) -> str:
        """
        Load prompt template for specific content type

        Args:
            content_type: One of the 8 supported La Factoria content types

        Returns:
            Raw template content as string
        """
        # Convert string to enum if needed
        if isinstance(content_type, str):
            try:
                content_type_enum = LaFactoriaContentType(content_type)
            except ValueError:
                raise ValueError(f"Unsupported content type: {content_type}")
        else:
            content_type_enum = content_type

        # Check cache first
        cache_key = content_type_enum.value
        if cache_key in self.template_cache:
            logger.debug(f"Template cache hit for {cache_key}")
            return self.template_cache[cache_key]

        # Get template filename
        template_file = self.template_files.get(content_type_enum)
        if not template_file:
            raise ValueError(f"No template file mapping for content type: {content_type_enum.value}")

        # Load template from file
        template_path = self.prompts_directory / template_file

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # Cache the template
            self.template_cache[cache_key] = template_content

            logger.info(f"Loaded template for {content_type_enum.value} from {template_file}")
            return template_content

        except FileNotFoundError:
            error_msg = f"Template file not found: {template_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        except Exception as e:
            error_msg = f"Failed to load template {template_file}: {e}"
            logger.error(error_msg)
            raise

    def compile_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """
        Compile template with provided variables using Jinja2

        Args:
            template_content: Raw template content
            variables: Dictionary of variables to substitute

        Returns:
            Compiled template with variables substituted
        """
        if not self.jinja_env:
            raise RuntimeError("Prompt loader not initialized. Call initialize() first.")

        try:
            # Create template from string
            template = self.jinja_env.from_string(template_content)

            # Render with variables
            compiled_content = template.render(**variables)

            logger.debug(f"Template compiled with variables: {list(variables.keys())}")
            return compiled_content.strip()

        except Exception as e:
            logger.error(f"Template compilation failed: {e}")
            logger.debug(f"Variables provided: {variables}")
            raise ValueError(f"Template compilation failed: {e}")

    async def get_template_metadata(self, content_type: str) -> Dict[str, Any]:
        """
        Get metadata about a template (variables, description, etc.)

        This would parse the template to extract metadata comments
        For now, returns basic information
        """
        template_content = await self.load_template(content_type)

        # Extract metadata from template comments (basic implementation)
        metadata = {
            "content_type": content_type,
            "length": len(template_content),
            "variables_detected": self._extract_template_variables(template_content),
            "estimated_tokens": len(template_content.split()) * 1.3  # Rough estimate
        }

        return metadata

    def _extract_template_variables(self, template_content: str) -> list:
        """Extract Jinja2 variables from template content"""
        import re

        # Find all {$variable$} patterns (using our custom delimiters)
        variable_pattern = r'\{\$\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\$\}'
        variables = re.findall(variable_pattern, template_content)

        # Remove duplicates and sort
        return sorted(list(set(variables)))

    async def reload_template(self, content_type: str):
        """Reload a specific template from disk (clear cache)"""
        cache_key = content_type if isinstance(content_type, str) else content_type.value

        # Remove from cache
        if cache_key in self.template_cache:
            del self.template_cache[cache_key]

        # Reload template
        await self.load_template(content_type)
        logger.info(f"Template reloaded: {cache_key}")

    async def reload_all_templates(self):
        """Reload all templates from disk (clear all cache)"""
        self.template_cache.clear()

        # Preload all templates
        for content_type in self.template_files.keys():
            await self.load_template(content_type)

        logger.info("All templates reloaded")

    def get_supported_content_types(self) -> list:
        """Get list of supported content types"""
        return [ct.value for ct in self.template_files.keys()]

    def get_template_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded templates"""
        return {
            "total_templates": len(self.template_files),
            "cached_templates": len(self.template_cache),
            "supported_types": self.get_supported_content_types(),
            "prompts_directory": str(self.prompts_directory),
            "cache_hit_ratio": len(self.template_cache) / len(self.template_files) if self.template_files else 0
        }
