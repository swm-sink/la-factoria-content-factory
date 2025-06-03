"""
Text cleanup and grammar correction utilities.
"""

import logging
import re

# Configure logging
logger = logging.getLogger(__name__)


def correct_grammar_and_style(text: str) -> str:
    """
    Apply grammar and style corrections to text.

    Args:
        text: Text to correct

    Returns:
        Corrected text
    """
    # Common grammar fixes
    fixes = [
        (r"\s+", " "),  # Multiple spaces
        (r"([.!?])\s*([A-Z])", r"\1 \2"),  # Space after punctuation
        (r"([a-z])([A-Z])", r"\1 \2"),  # Space between words
        (r"([a-z])([0-9])", r"\1 \2"),  # Space between word and number
        (r"([0-9])([a-z])", r"\1 \2"),  # Space between number and word
    ]

    # Apply fixes
    for pattern, replacement in fixes:
        text = re.sub(pattern, replacement, text)

    return text.strip()
