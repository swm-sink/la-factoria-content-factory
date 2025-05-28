"""
Automates the generation of the AI context dump file (ai_context_dump.md).

This script collects content from specified project files and compiles them
into a single Markdown file, which can be used to provide context to
AI models like Gemini or ChatGPT.

It supports selective section inclusion via command-line arguments.
Enhanced logging and error handling are implemented as per project guidelines.
"""

import argparse
import logging
from datetime import datetime, timezone
import os
from typing import Dict, List, Optional, Tuple, TypedDict

# Configure enhanced logging
LOG_FORMAT = '''%(asctime)s - %(levelname)s - %(name)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'''
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class SectionDetail(TypedDict):
    """Typed dictionary for section details."""
    display_name: str
    file_path_relative_to_root: str
    markdown_language_hint: str
    required: bool

# Define a dictionary mapping short section identifiers to their details.
# These are the files that will be included in the AI context dump.
SECTION_DEFINITIONS: Dict[str, SectionDetail] = {
    "project_mdc": {
        "display_name": "Project Directives and Rules (.cursor/rules/project.mdc)",
        "file_path_relative_to_root": ".cursor/rules/project.mdc",
        "markdown_language_hint": "markdown",
        "required": True,
    },
    "main_py": {
        "display_name": "Main Application (app/main.py)",
        "file_path_relative_to_root": "app/main.py",
        "markdown_language_hint": "python",
        "required": True,
    },
    "test_app_py": {
        "display_name": "Unit Tests (tests/unit/test_app.py)",
        "file_path_relative_to_root": "tests/unit/test_app.py", # Updated path
        "markdown_language_hint": "python",
        "required": False, # Set to False as per user prompt example
    },
    "requirements_txt": {
        "display_name": "Application Dependencies (requirements.txt)",
        "file_path_relative_to_root": "requirements.txt",
        "markdown_language_hint": "text",
        "required": True,
    },
    "dockerfile": {
        "display_name": "Dockerfile (Dockerfile)",
        "file_path_relative_to_root": "Dockerfile",
        "markdown_language_hint": "dockerfile",
        "required": True,
    },
    "tasks_md": {
        "display_name": "Project Tasks (tasks.md)",
        "file_path_relative_to_root": "tasks.md",
        "markdown_language_hint": "markdown",
        "required": True,
    },
    "changelog_md": {
        "display_name": "Changelog (CHANGELOG.md)",
        "file_path_relative_to_root": "CHANGELOG.md",
        "markdown_language_hint": "markdown",
        "required": False,
    },
    "readme_md": {
        "display_name": "README (README.md)",
        "file_path_relative_to_root": "README.md",
        "markdown_language_hint": "markdown",
        "required": True,
    },
    "script_itself": {
        "display_name": "Context Dump Script (generate_ai_context_dump.py)",
        "file_path_relative_to_root": "generate_ai_context_dump.py",
        "markdown_language_hint": "python",
        "required": True,
    },
}

def _get_cest_time() -> str:
    """Returns the current time in CEST if possible, otherwise UTC with offset."""
    try:
        # This part requires `pytz` or Python 3.9+ `zoneinfo`
        # For simplicity without adding new deps for now, using UTC with offset
        # from datetime import timezone as dt_timezone
        # from zoneinfo import ZoneInfo # Python 3.9+
        # cest = ZoneInfo("Europe/Berlin")
        # dt_cest = datetime.now(cest)
        # return dt_cest.strftime("%Y-%m-%d %H:%M:%S (%Z)")
        dt_utc = datetime.now(timezone.utc)
        # Simulate CEST as UTC+2 for example purposes if ZoneInfo not available
        # In a real scenario, ensure pytz or zoneinfo is used for accurate timezone.
        dt_sim_cest = dt_utc.astimezone(timezone(datetime.strptime("2000-01-01T00:00:00+0200", "%Y-%m-%dT%H:%M:%S%z").tzinfo))
        return dt_sim_cest.strftime("%Y-%m-%d %H:%M:%S (Simulated CEST %z)")

    except ImportError:
        logger.warning("zoneinfo module not found for precise CEST. Using UTC.")
        dt_utc = datetime.now(timezone.utc)
        return dt_utc.strftime("%Y-%m-%d %H:%M:%S (UTC%z)")
    except Exception as e:
        logger.error(f"Error getting CEST time: {e}. Using UTC.")
        dt_utc = datetime.now(timezone.utc)
        return dt_utc.strftime("%Y-%m-%d %H:%M:%S (UTC%z)")


def _read_and_format_file(
    file_path: str, display_name: str, markdown_language_hint: str, section_number: int
) -> str:
    """
    Reads a file and formats its content as a Markdown section.

    Args:
        file_path: The absolute path to the file.
        display_name: The display name for the section header.
        markdown_language_hint: The language hint for the Markdown code block.
        section_number: The number for the section heading.

    Returns:
        A string containing the formatted Markdown section.
    """
    logger.info(f"Processing section {section_number}: {display_name} from {file_path}")
    content_parts = [f"## {section_number}. {display_name}\n"]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        content_parts.append(f"```{markdown_language_hint}\n")
        content_parts.append(file_content)
        content_parts.append("\n```\n\n")
        logger.debug(f"Successfully read and formatted {file_path}")
    except FileNotFoundError:
        not_found_msg = f"File not found: {file_path}"
        logger.error(not_found_msg)
        content_parts.append(f"```text\n{not_found_msg}\n```\n\n")
    except Exception as e:
        error_msg = f"Error reading file {file_path}: {e}"
        logger.exception(error_msg, exc_info=True) # Log full traceback
        content_parts.append(f"```text\n{error_msg}\n```\n\n")
    return "".join(content_parts)


def generate_dump(output_file: str, sections_to_include: Optional[List[str]] = None) -> bool:
    """
    Generates the AI context dump Markdown file.

    Args:
        output_file: The path to the output Markdown file.
        sections_to_include: A list of short section identifiers to include.
                             If None or empty, all defined sections are included.

    Returns:
        True if the dump was generated successfully, False otherwise.
    """
    logger.info(f"Starting AI context dump generation. Output to: {output_file}")
    if sections_to_include:
        logger.info(f"Including specified sections: {sections_to_include}")
    else:
        logger.info("Including all defined sections.")

    project_root = os.path.dirname(os.path.abspath(__file__))
    logger.debug(f"Project root determined as: {project_root}")

    markdown_content = [
        "# AI Content Factory Project Context Dump\n",
        f"Generated: {_get_cest_time()}\n\n",
        "This document contains a snapshot of key project files to provide context for AI interactions.\n\n",
    ]

    section_counter = 1
    
    definitions_to_process = SECTION_DEFINITIONS
    if sections_to_include:
        # Filter definitions ensuring specified sections are valid
        valid_requested_sections = {
            key: SECTION_DEFINITIONS[key]
            for key in sections_to_include
            if key in SECTION_DEFINITIONS
        }
        # Add any missing required sections if a specific list is provided
        for key, detail in SECTION_DEFINITIONS.items():
            if detail["required"] and key not in valid_requested_sections:
                logger.warning(f"Required section '{key}' was not specified but will be included.")
                valid_requested_sections[key] = detail
        
        if not valid_requested_sections:
            logger.error("No valid sections specified or found. Aborting.")
            return False
        definitions_to_process = valid_requested_sections
        logger.info(f"Final sections to process: {list(definitions_to_process.keys())}")


    for section_key, section_detail in definitions_to_process.items():
        file_path_abs = os.path.join(project_root, section_detail["file_path_relative_to_root"])
        logger.debug(f"Absolute path for {section_key}: {file_path_abs}")
        
        formatted_section = _read_and_format_file(
            file_path_abs,
            section_detail["display_name"],
            section_detail["markdown_language_hint"],
            section_counter
        )
        markdown_content.append(formatted_section)
        section_counter += 1

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("".join(markdown_content))
        logger.info(f"Successfully wrote AI context dump to {output_file}")
        return True
    except IOError as e:
        logger.error(f"Failed to write output file {output_file}: {e}", exc_info=True)
        return False
    except Exception as e: # Catch any other unexpected error during write
        logger.error(f"An unexpected error occurred while writing {output_file}: {e}", exc_info=True)
        return False


def main():
    """Main function to parse arguments and orchestrate dump generation."""
    parser = argparse.ArgumentParser(
        description="Generate an AI context dump from specified project files.",
        formatter_class=argparse.RawTextHelpFormatter # To allow multi-line help
    )
    parser.add_argument(
        "--output",
        default="ai_context_dump.md",
        help="Specifies the output Markdown filename (default: ai_context_dump.md)",
    )
    parser.add_argument(
        "--sections",
        nargs="*",
        choices=list(SECTION_DEFINITIONS.keys()), # Restrict choices to defined sections
        help=(
            "A list of short section identifiers to include. "
            "If omitted, all defined sections are included.\nAvailable sections:\n" + 
            "\n".join([f"  - {key}: {details['display_name']}" for key, details in SECTION_DEFINITIONS.items()])
        ),
        metavar="SECTION_ID"
    )

    args = parser.parse_args()
    
    logger.info("Script execution started with arguments: %s", args)

    if generate_dump(args.output, args.sections):
        logger.info("AI context dump generation completed successfully.")
    else:
        logger.error("AI context dump generation failed.")
        # Consider exiting with a non-zero status code for CI/CD integration
        # import sys
        # sys.exit(1)

if __name__ == "__main__":
    main() 