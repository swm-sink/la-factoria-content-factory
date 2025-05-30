"""Content validation utilities for AI-generated content.

This module provides functions for:
- Content sanitization (XSS prevention)
- Quality validation
- Structure compliance checks
- Length validation
- Content consistency verification
"""

import re
import html
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from pydantic import ValidationError

from app.models.pydantic.content import (
    ContentResponse,
    GeneratedContent,
    ContentOutline,
    PodcastScript,
    StudyGuide,
    OnePagerSummary,
    DetailedReadingMaterial,
    FAQCollection,
    FlashcardCollection,
    ReadingGuideQuestions,
    QualityMetrics,
)

logger = logging.getLogger(__name__)

# ====================================
# CONTENT SANITIZATION
# ====================================


def sanitize_html_content(content: str) -> str:
    """Remove or escape potentially dangerous HTML content.

    Args:
        content: Raw content string that may contain HTML

    Returns:
        Sanitized content string
    """
    if not content:
        return ""

    # Escape HTML entities
    sanitized = html.escape(content)

    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r"<script.*?</script>",
        r"<iframe.*?</iframe>",
        r"javascript:",
        r"on\w+\s*=",  # Event handlers like onclick=
        r"<object.*?</object>",
        r"<embed.*?</embed>",
    ]

    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)

    return sanitized.strip()


def sanitize_content_dict(content_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sanitize all string values in a content dictionary.

    Args:
        content_dict: Dictionary containing content to sanitize

    Returns:
        Dictionary with sanitized string values
    """
    if not isinstance(content_dict, dict):
        return content_dict

    sanitized = {}
    for key, value in content_dict.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_html_content(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_content_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [
                (
                    sanitize_html_content(item)
                    if isinstance(item, str)
                    else sanitize_content_dict(item) if isinstance(item, dict) else item
                )
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


# ====================================
# QUALITY VALIDATION
# ====================================


def calculate_readability_score(text: str) -> float:
    """Calculate a simple readability score based on sentence and word length.

    Args:
        text: Text to analyze

    Returns:
        Readability score between 0 and 1 (higher is better)
    """
    if not text or len(text.strip()) < 10:
        return 0.0

    # Simple metrics
    sentences = re.split(r"[.!?]+", text)
    words = text.split()

    if not sentences or not words:
        return 0.0

    avg_sentence_length = len(words) / len(sentences)
    avg_word_length = sum(len(word) for word in words) / len(words)

    # Ideal ranges: 15-20 words per sentence, 4-6 characters per word
    sentence_score = max(0, 1 - abs(avg_sentence_length - 17.5) / 17.5)
    word_score = max(0, 1 - abs(avg_word_length - 5) / 5)

    return (sentence_score + word_score) / 2


def check_content_structure(content: str, content_type: str) -> Tuple[float, List[str]]:
    """Check if content follows expected structural patterns.

    Args:
        content: Content to analyze
        content_type: Type of content (e.g., 'podcast_script', 'study_guide')

    Returns:
        Tuple of (structure_score, list_of_issues)
    """
    issues = []
    score = 1.0

    if not content or len(content.strip()) < 50:
        issues.append("Content is too short")
        return 0.0, issues

    # Check for basic structure elements
    if content_type == "podcast_script":
        required_elements = ["introduction", "main", "conclusion"]
        for element in required_elements:
            if element.lower() not in content.lower():
                issues.append(f"Missing {element} section")
                score -= 0.2

    elif content_type == "study_guide":
        required_elements = ["overview", "key", "summary"]
        for element in required_elements:
            if element.lower() not in content.lower():
                issues.append(f"Missing {element} section")
                score -= 0.2

    # Check for excessive repetition
    words = content.lower().split()
    if len(words) > 10:
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Only check longer words
                word_freq[word] = word_freq.get(word, 0) + 1

        max_freq = max(word_freq.values()) if word_freq else 0
        if max_freq > len(words) * 0.05:  # More than 5% repetition
            issues.append("Excessive word repetition detected")
            score -= 0.1

    return max(0.0, score), issues


def validate_content_length_requirements(
    content_dict: Dict[str, Any],
) -> Tuple[bool, List[str]]:
    """Validate that content meets minimum length requirements.

    Args:
        content_dict: Dictionary containing content to validate

    Returns:
        Tuple of (is_compliant, list_of_violations)
    """
    violations = []

    # Define minimum length requirements (in characters)
    length_requirements = {
        "content_outline": 200,
        "podcast_script": 1000,
        "study_guide": 800,
        "one_pager_summary": 300,
        "detailed_reading_material": 1500,
    }

    for content_type, min_length in length_requirements.items():
        if content_type in content_dict:
            content = content_dict[content_type]

            # Extract text content based on structure
            if isinstance(content, dict):
                if content_type == "content_outline":
                    text_length = len(str(content.get("overview", "")))
                elif content_type == "podcast_script":
                    intro = content.get("introduction", "")
                    main = content.get("main_content", "")
                    conclusion = content.get("conclusion", "")
                    text_length = len(intro) + len(main) + len(conclusion)
                else:
                    # For other types, sum up major text fields
                    text_length = sum(
                        len(str(v))
                        for k, v in content.items()
                        if isinstance(v, str)
                        and k in ["overview", "detailed_content", "main_content"]
                    )
            else:
                text_length = len(str(content))

            if text_length < min_length:
                violations.append(
                    f"{content_type} is {text_length} characters, minimum is {min_length}"
                )

    return len(violations) == 0, violations


# ====================================
# CONTENT VALIDATION SERVICE
# ====================================


def validate_ai_content_dict(
    content_dict: Dict[str, Any],
) -> Tuple[bool, QualityMetrics, Dict[str, Any]]:
    """Validate AI-generated content dictionary before Pydantic parsing.

    Args:
        content_dict: Raw dictionary from AI model

    Returns:
        Tuple of (is_valid, quality_metrics, sanitized_content_dict)
    """
    logger.info("Starting AI content validation")

    # First, sanitize the content
    sanitized_dict = sanitize_content_dict(content_dict)

    # Initialize quality metrics
    quality_metrics = QualityMetrics()
    validation_errors = []

    # Check content length compliance
    length_compliant, length_violations = validate_content_length_requirements(
        sanitized_dict
    )
    quality_metrics.content_length_compliance = length_compliant
    validation_errors.extend(length_violations)

    # Calculate overall readability and structure scores
    total_readability = 0.0
    total_structure = 0.0
    content_count = 0

    for content_type, content in sanitized_dict.items():
        if content and content_type in [
            "podcast_script",
            "study_guide",
            "detailed_reading_material",
        ]:
            # Extract text for analysis
            if isinstance(content, dict):
                text_parts = []
                for key, value in content.items():
                    if isinstance(value, str) and len(value) > 20:
                        text_parts.append(value)
                text = " ".join(text_parts)
            else:
                text = str(content)

            if text:
                readability = calculate_readability_score(text)
                structure_score, structure_issues = check_content_structure(
                    text, content_type
                )

                total_readability += readability
                total_structure += structure_score
                content_count += 1

                validation_errors.extend(
                    [f"{content_type}: {issue}" for issue in structure_issues]
                )

    # Calculate average scores
    if content_count > 0:
        quality_metrics.readability_score = total_readability / content_count
        quality_metrics.structure_score = total_structure / content_count

    # Calculate overall score
    scores = [
        quality_metrics.readability_score or 0,
        quality_metrics.structure_score or 0,
        1.0 if quality_metrics.content_length_compliance else 0.5,
    ]
    quality_metrics.overall_score = sum(scores) / len(scores)
    quality_metrics.validation_errors = validation_errors

    # Determine if content is valid
    is_valid = (
        quality_metrics.overall_score >= 0.6  # Minimum overall quality
        and quality_metrics.content_length_compliance  # Must meet length requirements
        and len(validation_errors) < 5  # Maximum allowed issues
    )

    logger.info(
        f"Content validation complete. Valid: {is_valid}, Score: {quality_metrics.overall_score:.2f}"
    )

    return is_valid, quality_metrics, sanitized_dict


def validate_and_parse_content_response(
    raw_content: Dict[str, Any],
) -> Tuple[bool, Union[ContentResponse, List[str]]]:
    """Validate and parse raw AI output into ContentResponse model.

    Args:
        raw_content: Raw dictionary from AI model

    Returns:
        Tuple of (success, ContentResponse_or_error_list)
    """
    try:
        logger.info("Validating and parsing AI content response")

        # First validate the content quality
        is_valid, quality_metrics, sanitized_content = validate_ai_content_dict(
            raw_content
        )

        if not is_valid:
            error_msg = "Content quality validation failed"
            logger.warning(f"{error_msg}: {quality_metrics.validation_errors}")
            return False, quality_metrics.validation_errors

        # Try to parse with Pydantic
        try:
            # Ensure we have the required structure for ContentResponse
            if "content" not in sanitized_content:
                sanitized_content = {"content": sanitized_content}

            if "metadata" not in sanitized_content:
                sanitized_content["metadata"] = {}

            # Add quality metrics
            sanitized_content["quality_metrics"] = quality_metrics.model_dump()

            content_response = ContentResponse(**sanitized_content)
            logger.info("Successfully parsed content response")
            return True, content_response

        except ValidationError as e:
            error_messages = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
            logger.error(f"Pydantic validation failed: {error_messages}")
            return False, error_messages

    except Exception as e:
        logger.error(f"Unexpected error during content validation: {e}", exc_info=True)
        return False, [f"Validation error: {str(e)}"]


# ====================================
# UTILITY FUNCTIONS
# ====================================


def extract_text_from_content(content: Any) -> str:
    """Extract readable text from any content structure.

    Args:
        content: Content in any format (str, dict, list)

    Returns:
        Extracted text string
    """
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        text_parts = []
        for value in content.values():
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, (list, dict)):
                text_parts.append(extract_text_from_content(value))
        return " ".join(text_parts)
    elif isinstance(content, list):
        text_parts = []
        for item in content:
            text_parts.append(extract_text_from_content(item))
        return " ".join(text_parts)
    else:
        return str(content)


def estimate_reading_time(text: str, wpm: int = 200) -> float:
    """Estimate reading time for text content.

    Args:
        text: Text to analyze
        wpm: Words per minute reading speed

    Returns:
        Estimated reading time in minutes
    """
    if not text:
        return 0.0

    word_count = len(text.split())
    return word_count / wpm
