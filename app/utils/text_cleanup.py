"""
Text cleanup utilities, primarily for grammar and style correction.

This module uses language-tool-python to correct common grammatical errors
and improve the style of input text.
"""

import logging
import language_tool_python

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the language tool. This can take a moment on first run
# as it might download language data.
try:
    # Using a context manager for setup if available, or direct init
    # Depending on the library version, direct init might be standard.
    # tool = language_tool_python.LanguageTool('en-US')

    # Simpler initialization, often sufficient:
    tool = language_tool_python.LanguageTool("en-US")
    logger.info("LanguageTool initialized successfully for en-US.")
except Exception as e:
    logger.error(
        f"Failed to initialize LanguageTool: {e}. Grammar/style checking will be disabled.",
        exc_info=True,
    )
    tool = None


def correct_grammar_and_style(text: str) -> str:
    """
    Corrects common grammatical errors and improves style of the input text
    using language-tool-python.

    Args:
        text (str): The input text to be corrected.

    Returns:
        str: The corrected text, or the original text if correction fails or tool is unavailable.
    """
    if not tool:
        logger.warning(
            "LanguageTool is not available. Skipping grammar/style correction."
        )
        return text

    if not text or not isinstance(text, str):
        logger.warning("Input text is empty or not a string. Skipping correction.")
        return text

    try:
        logger.debug(
            f"Attempting grammar/style correction for text (first 100 chars): {text[:100]}"
        )
        # Correct the text
        corrected_text = tool.correct(text)

        # Log if changes were made (optional, for verbosity)
        if corrected_text != text:
            logger.info("Grammar/style corrections applied.")
            # For more detailed logging of changes, one might iterate through `tool.check(text)`
            # and log the specific matches/replacements, but `tool.correct` is simpler for direct use.
        else:
            logger.debug("No grammar/style corrections needed by LanguageTool.")

        return corrected_text
    except Exception as e:
        logger.error(
            f"Error during grammar/style correction: {e}. Returning original text.",
            exc_info=True,
        )
        return text


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for detailed tool logs

    sample_texts = [
        "This is an example sentence with some mistake.",
        "they enjoys playing football alot.",
        "Its a beautiful day, isnt it?",
        "Let's eat Grandma!",
        "Let's eat, Grandma!",  # Already correct
        "",  # Empty string
        None,  # Invalid input
        123,  # Invalid input
    ]

    for i, sample in enumerate(sample_texts):
        print(f"\n--- Sample {i+1} ---")
        print(f"Original: '{sample}'")
        if isinstance(sample, str) or sample is None:  # Allow None to test handling
            corrected = correct_grammar_and_style(sample)
            print(f"Corrected: '{corrected}'")
        else:
            print("Skipping correction for non-string input.")

    # Test with a longer paragraph
    long_text = """
    Thiss paragraph has severel issues it also have some stylistic problems that hopefully the tool can adress. 
    We wants to see how it perform on a larger block of text. for example, run on sentences might be a issue.
    Or perhaps, fragments. The tool should ideally make this text more readable and professional.
    """
    print("\n--- Long Sample ---")
    print(f"Original:\n{long_text}")
    corrected_long_text = correct_grammar_and_style(long_text)
    print(f"\nCorrected:\n{corrected_long_text}")
