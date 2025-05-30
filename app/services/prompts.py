"""
Service for managing and loading AI prompt templates from external files.

This service provides a centralized way to access versioned prompt templates,
which are stored as Markdown files. It includes caching for loaded prompts.
"""

import os
import logging
from functools import lru_cache
from typing import Dict

# Configure logging
logger = logging.getLogger(__name__)


class PromptService:
    """
    Manages loading and accessing AI prompt templates from external files.
    """

    _prompt_cache: Dict[str, str] = {}
    _base_prompt_path: str = "app/core/prompts/v1"

    PROMPT_MAP: Dict[str, str] = {
        "master_content_outline": "master_content_outline.md",
        "podcast_script": "podcast_script.md",
        "study_guide": "study_guide.md",
        "one_pager_summary": "one_pager_summary.md",
        "detailed_reading_material": "detailed_reading_material.md",
        "faq_collection": "faq_collection.md",
        "flashcards": "flashcards.md",
        "reading_guide_questions": "reading_guide_questions.md",
    }

    def __init__(self, base_path: str = None):
        """
        Initializes the PromptService.

        Args:
            base_path (str, optional): The base directory path for prompt files.
                                       Defaults to "app/core/prompts/v1".
        """
        if base_path:
            self._base_prompt_path = base_path

        # Pre-warm cache if desired, or let it load on demand
        # self._warm_cache()

    @lru_cache(maxsize=32)  # Cache results of this method
    def _load_prompt_from_file(self, file_path: str) -> str:
        """
        Loads a single prompt template from a file.

        Args:
            file_path (str): The full path to the prompt file.

        Returns:
            str: The content of the prompt file.

        Raises:
            FileNotFoundError: If the prompt file cannot be found.
            IOError: If there is an error reading the file.
        """
        try:
            # Ensure the path is absolute or correctly relative to the project root
            # For this project, paths are relative to the root where Cline operates.
            full_path = os.path.join(os.getcwd(), file_path)

            if not os.path.exists(full_path):
                logger.error(f"Prompt file not found at path: {full_path}")
                raise FileNotFoundError(f"Prompt file not found: {file_path}")

            with open(full_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()
            logger.info(f"Successfully loaded prompt from: {file_path}")
            return prompt_content
        except FileNotFoundError:
            # Already logged, re-raise
            raise
        except IOError as e:
            logger.error(f"IOError reading prompt file {file_path}: {e}")
            raise IOError(f"Could not read prompt file {file_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading prompt file {file_path}: {e}")
            raise Exception(f"Unexpected error loading prompt {file_path}: {e}")

    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        Retrieves a prompt template by its logical name and formats it with provided arguments.

        Args:
            prompt_name (str): The logical name of the prompt (e.g., "master_content_outline").
            **kwargs: Keyword arguments to format the prompt template.

        Returns:
            str: The formatted prompt content.

        Raises:
            ValueError: If the prompt_name is not recognized.
            FileNotFoundError: If the prompt file cannot be found.
            IOError: If there is an error reading the file.
        """
        if prompt_name not in self.PROMPT_MAP:
            logger.error(f"Unknown prompt name: {prompt_name}")
            raise ValueError(
                f"Prompt name '{prompt_name}' is not defined in PROMPT_MAP."
            )

        file_name = self.PROMPT_MAP[prompt_name]
        file_path = os.path.join(self._base_prompt_path, file_name)

        try:
            # Use the internal cached method to load from file
            prompt_template = self._load_prompt_from_file(file_path)

            if kwargs:
                return prompt_template.format(**kwargs)
            return prompt_template
        except KeyError as e:  # Should not happen if PROMPT_MAP is correct
            logger.error(
                f"Formatting error for prompt '{prompt_name}': Missing key {e}"
            )
            raise ValueError(
                f"Formatting error for prompt '{prompt_name}': Missing key {e}"
            )
        # FileNotFoundError and IOError are propagated from _load_prompt_from_file

    def _warm_cache(self):
        """
        Pre-loads all defined prompts into the cache.
        This is optional and can be called during initialization if desired.
        """
        logger.info("Warming prompt cache...")
        for prompt_name in self.PROMPT_MAP.keys():
            try:
                self.get_prompt(prompt_name)  # This will load and cache it
            except Exception as e:
                logger.error(f"Failed to pre-load prompt '{prompt_name}': {e}")
        logger.info("Prompt cache warming complete.")


# Example usage (for testing or direct script use):
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    prompt_service = PromptService()

    # Test loading a prompt
    try:
        outline_prompt_template = prompt_service.get_prompt("master_content_outline")
        # print("Outline Prompt Template:\n", outline_prompt_template)

        # Test formatting
        formatted_outline_prompt = prompt_service.get_prompt(
            "master_content_outline",
            syllabus_text="This is a sample syllabus about Python programming.",
        )
        print("\nFormatted Outline Prompt:\n", formatted_outline_prompt)

        podcast_prompt = prompt_service.get_prompt(
            "podcast_script",
            outline_json='{"title": "Test Podcast Outline", "sections": []}',
        )
        print("\nFormatted Podcast Prompt:\n", podcast_prompt)

    except Exception as e:
        print(f"An error occurred: {e}")
