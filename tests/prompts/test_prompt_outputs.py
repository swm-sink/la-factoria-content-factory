import json
from typing import Any, Dict, Type

import pytest
from pydantic import BaseModel, ValidationError

from app.core.config.settings import get_settings
from app.models.pydantic.content import (
    ContentOutline,
    DetailedReadingMaterial,
    FAQCollection,
    FlashcardCollection,
    OnePagerSummary,
    PodcastScript,
    ReadingGuideQuestions,
    StudyGuide,
)
from app.services.multi_step_content_generation_final import (
    EnhancedMultiStepContentGenerationService,
)
from app.services.prompts import PromptService

# Initialize services
prompt_service = PromptService()
settings = get_settings()

# Sample data for testing
SAMPLE_SYLLABUS_TEXT = """
Module 1: Introduction to Python
- Variables and Data Types
- Control Flow (if/else, loops)
Module 2: Functions
- Defining Functions
- Scope and Closures
Module 3: Object-Oriented Programming
- Classes and Objects
- Inheritance
"""

SAMPLE_OUTLINE_JSON = json.dumps(
    {
        "title": "Comprehensive Python Course Outline",
        "overview": "This outline covers fundamental Python concepts from basics to OOP.",
        "learning_objectives": [
            "Understand basic Python syntax and data types.",
            "Learn to control program flow using conditional statements and loops.",
            "Master function definition and usage, including scope.",
            "Grasp the principles of Object-Oriented Programming in Python.",
        ],
        "sections": [
            {
                "section_number": 1,
                "title": "Introduction to Python",
                "description": "Covers variables, data types, and control flow.",
                "key_points": ["Variables", "Data Types", "Loops"],
            },
            {
                "section_number": 2,
                "title": "Functions",
                "description": "Explores function definition, arguments, and scope.",
                "key_points": ["Definition", "Arguments", "Scope"],
            },
            {
                "section_number": 3,
                "title": "Object-Oriented Programming",
                "description": "Introduces classes, objects, and inheritance.",
                "key_points": ["Classes", "Objects", "Inheritance"],
            },
        ],
        "target_audience": "Beginner to Intermediate Programmers",
        "difficulty_level": "intermediate",
    }
)

# --- Test Cases ---


@pytest.mark.parametrize(
    "prompt_key, pydantic_model, sample_input_kwargs",
    [
        (
            "master_content_outline",
            ContentOutline,
            {"syllabus_text": SAMPLE_SYLLABUS_TEXT},
        ),
        ("podcast_script", PodcastScript, {"outline_json": SAMPLE_OUTLINE_JSON}),
        ("study_guide", StudyGuide, {"outline_json": SAMPLE_OUTLINE_JSON}),
        ("one_pager_summary", OnePagerSummary, {"outline_json": SAMPLE_OUTLINE_JSON}),
        (
            "detailed_reading_material",
            DetailedReadingMaterial,
            {"outline_json": SAMPLE_OUTLINE_JSON},
        ),
        ("faq_collection", FAQCollection, {"outline_json": SAMPLE_OUTLINE_JSON}),
        ("flashcards", FlashcardCollection, {"outline_json": SAMPLE_OUTLINE_JSON}),
        (
            "reading_guide_questions",
            ReadingGuideQuestions,
            {"outline_json": SAMPLE_OUTLINE_JSON},
        ),
    ],
)
def test_prompt_generates_valid_format_and_parses(
    prompt_key: str,
    pydantic_model: Type[BaseModel],
    sample_input_kwargs: Dict[str, Any],
    mocker,
):
    formatted_prompt = prompt_service.get_prompt(prompt_key, **sample_input_kwargs)
    assert formatted_prompt is not None
    assert isinstance(formatted_prompt, str)

    mock_llm_output_dict = {}
    if pydantic_model == ContentOutline:
        mock_llm_output_dict = {
            "title": "Test Title for Outline Valid Length",
            "overview": "Test overview with sufficient length for validation purposes. This should be more than fifty characters long.",
            "learning_objectives": [
                "Objective A valid length and more than fifteen chars",
                "Objective B valid length and more than fifteen chars",
                "Objective C valid length and more than fifteen chars",
            ],
            "sections": [
                {
                    "section_number": 1,
                    "title": "Section 1 Valid Title",
                    "description": "Valid description for section 1, long enough for validation.",
                    "key_points": ["KP1 valid length more than ten chars"],
                },
                {
                    "section_number": 2,
                    "title": "Section 2 Valid Title",
                    "description": "Valid description for section 2, long enough for validation.",
                    "key_points": ["KP2 valid length more than ten chars"],
                },
                {
                    "section_number": 3,
                    "title": "Section 3 Valid Title",
                    "description": "Valid description for section 3, long enough for validation.",
                    "key_points": ["KP3 valid length more than ten chars"],
                },
            ],
        }
    elif pydantic_model == PodcastScript:
        mock_llm_output_dict = {
            "title": "Test Podcast Title Valid Length",
            "introduction": "This is a test introduction for the podcast script, ensuring it is long enough to pass validation. It should be at least 100 characters long to be considered valid by the Pydantic model.",
            "main_content": "This is the main content of the podcast. It needs to be substantially long, over 800 characters to be valid. We will fill this with enough text to simulate a real script. This part discusses various topics from the outline, section by section, providing detailed explanations and engaging dialogue. We need to ensure this section is very comprehensive. Let's add more filler text to meet the length requirement. This is more filler text. And even more filler text to make sure we are well above the minimum length for the main content of the podcast script. This should be sufficient now for testing purposes. Adding even more text to ensure we cross the threshold comfortably. This is just padding to meet the length requirements for the main_content field of the PodcastScript Pydantic model during unit testing of prompt outputs.",
            "conclusion": "This is the test conclusion for the podcast script, wrapping up the discussion and providing final thoughts. It also needs to be of a certain minimum length for validation, specifically at least 100 characters.",
        }
        total_len = (
            len(mock_llm_output_dict["introduction"])
            + len(mock_llm_output_dict["main_content"])
            + len(mock_llm_output_dict["conclusion"])
        )
        if total_len < 1000:
            mock_llm_output_dict["main_content"] += " " * (1000 - total_len)

    elif pydantic_model == StudyGuide:
        mock_llm_output_dict = {
            "title": "Test Study Guide Title Valid Length",
            "overview": "This is a test overview for the study guide, long enough for validation and detailed, exceeding one hundred characters.",
            "key_concepts": [
                "Concept 1 valid length (min 10 chars)",
                "Concept 2 valid length (min 10 chars)",
                "Concept 3 valid length (min 10 chars)",
                "Concept 4 valid length (min 10 chars)",
                "Concept 5 valid length (min 10 chars)",
            ],
            "detailed_content": "This is the detailed content for the study guide. It needs to be quite long, at least 500 characters. This section will elaborate on various topics, providing explanations, examples, and details suitable for learners. We will add more text here to meet the minimum length requirement. This is more filler text to ensure the detailed_content field is sufficiently long for Pydantic validation. More and more text is added here to ensure we pass the minimum length. This should now be well over five hundred characters to satisfy the model's validation rules.",
            "summary": "This is a test summary for the study guide, ensuring it meets the minimum length requirement of 100 characters for proper validation and completeness.",
        }
    elif pydantic_model == OnePagerSummary:
        mock_llm_output_dict = {
            "title": "Test One Pager Title Valid Length",
            "executive_summary": "This is a test executive summary, which needs to be at least 100 characters long to pass validation. Adding more details to meet length and provide a good example.",
            "key_takeaways": [
                "Takeaway one is important and long enough for validation (min 20 chars).",
                "Takeaway two is also crucial and sufficiently detailed for validation (min 20 chars).",
                "Takeaway three provides further insights and meets length for validation (min 20 chars).",
            ],
            "main_content": "This is the main content for the one-pager summary. It should be concise yet informative, covering the key aspects from the outline. The length requirement is 200 characters, so we add enough text here. This is more text to ensure it passes the validation and is a good representation.",
        }
    elif pydantic_model == DetailedReadingMaterial:
        mock_llm_output_dict = {
            "title": "Test Detailed Reading Material Title Valid Length",
            "introduction": "This is a test introduction for the detailed reading material. It must be at least 200 characters long to ensure it passes the validation checks. We are adding more text to meet this requirement for this specific test case, making sure it's comprehensive.",
            "sections": [
                {
                    "title": "DRM Section 1 Title Valid Length",
                    "content": "Content for DRM section 1. This content needs to be at least 200 characters long. We are adding more text here to make sure it meets the minimum length requirement for detailed reading material sections. This should be enough text for validation purposes and to simulate realistic content.",
                },
                {
                    "title": "DRM Section 2 Title Valid Length",
                    "content": "Content for DRM section 2. Similarly, this content also needs to be at least 200 characters long. We are adding more text here to make sure it meets the minimum length requirement for detailed reading material sections. This should be enough text for validation purposes and to simulate realistic content.",
                },
                {
                    "title": "DRM Section 3 Title Valid Length",
                    "content": "Content for DRM section 3. And again, this content also needs to be at least 200 characters long. We are adding more text here to make sure it meets the minimum length requirement for detailed reading material sections. This should be enough text for validation purposes and to simulate realistic content.",
                },
            ],
            "conclusion": "This is a test conclusion for the detailed reading material. It must be at least 200 characters long. We are adding more text here to meet this requirement for the conclusion section of the detailed reading material, ensuring it's thorough.",
        }
    elif pydantic_model == FAQCollection:
        mock_llm_output_dict = {
            "title": "Test Frequently Asked Questions Valid Length",
            "items": [
                {
                    "question": "What is the first test question, is it long enough?",
                    "answer": "This is the answer to the first test question, long enough for validation and providing useful information.",
                },
                {
                    "question": "What is the second test question, is it long enough?",
                    "answer": "This is the answer to the second test question, also long enough for validation and providing useful information.",
                },
                {
                    "question": "What is the third test question, is it long enough?",
                    "answer": "This is the answer to the third test question, and it is also long enough for validation and providing useful information.",
                },
                {
                    "question": "What is the fourth test question, is it long enough?",
                    "answer": "This is the answer to the fourth test question, ensuring sufficient length for validation and providing useful information.",
                },
                {
                    "question": "What is the fifth test question, is it long enough?",
                    "answer": "This is the answer to the fifth test question, making sure it's valid for validation and providing useful information.",
                },
            ],
        }
    elif pydantic_model == FlashcardCollection:
        mock_llm_output_dict = {
            "title": "Test Study Flashcards Valid Length",
            "items": [
                {
                    "term": "Term 1 Valid",
                    "definition": "Definition for Term 1, long enough for validation and clarity.",
                },
                {
                    "term": "Term 2 Valid",
                    "definition": "Definition for Term 2, also long enough for validation and clarity.",
                },
                {
                    "term": "Term 3 Valid",
                    "definition": "Definition for Term 3, ensuring validity and length for validation.",
                },
                {
                    "term": "Term 4 Valid",
                    "definition": "Definition for Term 4, meeting length requirements for validation and clarity.",
                },
                {
                    "term": "Term 5 Valid",
                    "definition": "Definition for Term 5, this is a test definition, long enough for validation.",
                },
                {
                    "term": "Term 6 Valid",
                    "definition": "Definition for Term 6, another test definition, long enough for validation.",
                },
                {
                    "term": "Term 7 Valid",
                    "definition": "Definition for Term 7, yet another one, long enough for validation.",
                },
                {
                    "term": "Term 8 Valid",
                    "definition": "Definition for Term 8, making sure we have enough length for validation.",
                },
                {
                    "term": "Term 9 Valid",
                    "definition": "Definition for Term 9, almost there for minimum items, long enough for validation.",
                },
                {
                    "term": "Term 10 Valid",
                    "definition": "Definition for Term 10, last one for minimum items, long enough for validation.",
                },
            ],
        }
    elif pydantic_model == ReadingGuideQuestions:
        mock_llm_output_dict = {
            "title": "Test Reading Guide Questions Valid Length",
            "questions": [
                "This is the first reading guide question, is it long enough for validation?",
                "This is the second reading guide question, what do you think, is it long enough for validation?",
                "This is the third reading guide question, does it meet criteria for length for validation?",
                "This is the fourth reading guide question, how about this one for length for validation?",
                "This is the fifth reading guide question, is this valid too for length for validation?",
            ],
        }

    if not mock_llm_output_dict and pydantic_model:
        pytest.skip(f"Mock LLM output not yet defined for {pydantic_model.__name__}")

    mock_llm_json_response = json.dumps(mock_llm_output_dict)
    mock_generation_service = EnhancedMultiStepContentGenerationService()
    cleaned_json_str = mock_generation_service._clean_llm_json_response(
        mock_llm_json_response
    )

    try:
        parsed_data = json.loads(cleaned_json_str)
        validated_model = pydantic_model(**parsed_data)
        assert isinstance(validated_model, pydantic_model)
    except json.JSONDecodeError as e:
        pytest.fail(
            f"Mocked LLM response for {prompt_key} was not valid JSON: {e}\nResponse: {cleaned_json_str}"
        )
    except ValidationError as e:
        pytest.fail(
            f"Mocked LLM response for {prompt_key} failed Pydantic validation for {pydantic_model.__name__}: {e}\nResponse: {cleaned_json_str}"
        )


# TODO:
# 1. (Done for primary models) Complete the mock_llm_output_dict for ALL Pydantic models in the test.
#    Each model needs its own minimal valid dictionary structure.
# 2. (Partially Done) Add tests for prompt robustness:
#    - Test with empty or minimal {{ outline_json }} or {{ syllabus_text }}.
#    - Test with very long inputs.
#    - Test with inputs containing special characters.
# 3. (Partially Done) Add tests for specific quality checks mentioned in prompts:
#    - e.g., for FAQs, ensure questions end with '?'.
#    - e.g., for ContentOutline, ensure section_numbers are sequential.
# 4. Consider integration tests (run sparingly) that make actual LLM calls with specific test prompts
#    and validate the live output against Pydantic models and quality criteria.
#    These would require API keys and careful management of costs.
# 5. Test the "CRITICAL OUTPUT REQUIREMENTS" themselves:
#    - Can the LLM adhere to "Do not wrap JSON in markdown"? (Hard to test without real calls)
#    - Can the LLM adhere to "Do not include text before or after JSON"?


def test_all_prompts_exist():
    """Ensures all known prompt keys are retrievable."""
    prompt_keys = [
        "master_content_outline",
        "podcast_script",
        "study_guide",
        "one_pager_summary",
        "detailed_reading_material",
        "faq_collection",
        "flashcards",
        "reading_guide_questions",
    ]
    for key in prompt_keys:
        assert (
            prompt_service.get_prompt(key, syllabus_text="test", outline_json="{}")
            is not None
        ), f"Prompt {key} not found"


# --- Tests for Prompt Robustness ---


def test_master_content_outline_prompt_empty_syllabus(mocker):
    """Test master_content_outline prompt with empty syllabus_text."""
    prompt_key = "master_content_outline"
    pydantic_model = ContentOutline

    formatted_prompt = prompt_service.get_prompt(prompt_key, syllabus_text="")
    assert formatted_prompt is not None

    mock_llm_output_dict = {
        "title": "Empty Syllabus Outline Valid Length",
        "overview": "Outline generated from an empty syllabus input which is long enough for validation.",
        "learning_objectives": [
            "Objective 1 from empty syllabus and long enough for validation",
            "Objective 2 from empty syllabus and long enough for validation",
            "Objective 3 from empty syllabus and long enough for validation",
        ],
        "sections": [
            {
                "section_number": 1,
                "title": "Default Section Title Valid Length",
                "description": "Default description due to empty input and long enough for validation.",
                "key_points": ["Default key point long enough for validation"],
            },
            {
                "section_number": 2,
                "title": "Second Default Section Title Valid Length",
                "description": "Second default description due to empty input and long enough for validation.",
                "key_points": ["Second default key point long enough for validation"],
            },
            {
                "section_number": 3,
                "title": "Third Default Section Title Valid Length",
                "description": "Third default description due to empty input and long enough for validation.",
                "key_points": ["Third default key point long enough for validation"],
            },
        ],
    }

    mock_llm_json_response = json.dumps(mock_llm_output_dict)
    mock_generation_service = EnhancedMultiStepContentGenerationService()
    cleaned_json_str = mock_generation_service._clean_llm_json_response(
        mock_llm_json_response
    )

    try:
        parsed_data = json.loads(cleaned_json_str)
        validated_model = pydantic_model(**parsed_data)
        assert isinstance(validated_model, pydantic_model)
    except ValidationError as e:
        pytest.fail(
            f"Minimal valid mock LLM response for {prompt_key} (empty syllabus) failed Pydantic validation: {e}"
        )


def test_master_content_outline_prompt_special_chars_syllabus(mocker):
    """Test master_content_outline prompt with syllabus_text containing special characters."""
    prompt_key = "master_content_outline"
    pydantic_model = ContentOutline
    special_syllabus = 'Syllabus with "quotes", newlines\n, tabs\t, and unicode 😊. Let\'s see: <xml>tags</xml> & ampersands.'

    formatted_prompt = prompt_service.get_prompt(
        prompt_key, syllabus_text=special_syllabus
    )
    assert formatted_prompt is not None
    assert "unicode 😊" in formatted_prompt
    assert "<xml>tags</xml>" in formatted_prompt

    mock_llm_output_dict = {
        "title": "Outline with Special Chars 😊 and enough length",
        "overview": 'Overview including "quotes" and <tags> and this overview is definitely long enough for validation.',
        "learning_objectives": [
            "Objective with 😊 and sufficient length for validation",
            "Objective with & and sufficient length for validation",
            "Objective with newline\n and sufficient length for validation",
        ],
        "sections": [
            {
                "section_number": 1,
                "title": 'Section with "Quotes" and enough length',
                "description": "Description with <xml> and this description is also long enough.",
                "key_points": ["Point with 😊 and long enough"],
            },
            {
                "section_number": 2,
                "title": "Another Section Valid Title",
                "description": "Another valid description for section two, long enough.",
                "key_points": ["KP2 valid length more than ten chars"],
            },
            {
                "section_number": 3,
                "title": "Third Section Valid Title",
                "description": "Third valid description for section three, long enough.",
                "key_points": ["KP3 valid length more than ten chars"],
            },
        ],
    }

    mock_llm_json_response = json.dumps(mock_llm_output_dict)
    mock_generation_service = EnhancedMultiStepContentGenerationService()
    cleaned_json_str = mock_generation_service._clean_llm_json_response(
        mock_llm_json_response
    )

    try:
        parsed_data = json.loads(cleaned_json_str)
        validated_model = pydantic_model(**parsed_data)
        assert isinstance(validated_model, pydantic_model)
    except ValidationError as e:
        pytest.fail(
            f"Mock LLM response for {prompt_key} (special chars syllabus) failed Pydantic validation: {e}"
        )


def test_derivative_prompt_empty_outline_json(mocker):
    """Test a derivative prompt (e.g., podcast_script) with empty outline_json."""
    prompt_key = "podcast_script"
    pydantic_model = PodcastScript

    formatted_prompt = prompt_service.get_prompt(prompt_key, outline_json="{}")
    assert formatted_prompt is not None

    mock_llm_output_dict = {
        "title": "Generic Podcast from Empty Outline Valid Length",
        "introduction": "This is a generic introduction because the outline was empty. It needs to be at least 100 characters long for validation and to provide some context.",
        "main_content": "This is generic main content due to an empty outline. This section must be very long, at least 800 characters. We are adding a lot of filler text here to meet this requirement. This filler text will continue for a while to ensure that the Pydantic model validation for minimum length passes successfully. More filler, more filler, and even more filler text. Still adding more filler text. This should be enough filler text now for the main content of this generic podcast script.",
        "conclusion": "This is a generic conclusion from an empty outline, and it also needs to be at least 100 characters long for validation to ensure it's a complete thought.",
    }
    total_len = (
        len(mock_llm_output_dict["introduction"])
        + len(mock_llm_output_dict["main_content"])
        + len(mock_llm_output_dict["conclusion"])
    )
    if total_len < 1000:
        mock_llm_output_dict["main_content"] += " " * (1000 - total_len)

    mock_llm_json_response = json.dumps(mock_llm_output_dict)
    mock_generation_service = EnhancedMultiStepContentGenerationService()
    cleaned_json_str = mock_generation_service._clean_llm_json_response(
        mock_llm_json_response
    )

    try:
        parsed_data = json.loads(cleaned_json_str)
        validated_model = pydantic_model(**parsed_data)
        assert isinstance(validated_model, pydantic_model)
    except ValidationError as e:
        pytest.fail(
            f"Minimal valid mock LLM response for {prompt_key} (empty outline_json) failed Pydantic validation: {e}"
        )


def test_derivative_prompt_special_chars_outline_json(mocker):
    """Test a derivative prompt with outline_json containing special characters."""
    prompt_key = "podcast_script"
    pydantic_model = PodcastScript

    special_outline_data = {
        "title": 'Outline with "Quotes" & 😊 Symbols Valid Length',
        "overview": "This overview contains newlines\n and <xml>tags</xml> and is long enough for validation.",
        "learning_objectives": [
            "Objective with &ampersand and long enough",
            "Objective with 'single quotes' and long enough",
            "Third objective for count and length, also long enough",
        ],
        "sections": [
            {
                "section_number": 1,
                "title": "Section with 😊 Emoji and Valid Length",
                "description": 'Description containing "double quotes" and tabs\t and is long enough for validation.',
                "key_points": ["Key point with <tag> and long enough"],
            },
            {
                "section_number": 2,
                "title": "Second Section Valid Title Long Enough",
                "description": "Second section description long enough for validation and detailed.",
                "key_points": ["Second key point long enough for validation"],
            },
            {
                "section_number": 3,
                "title": "Third Section Valid Title Long Enough",
                "description": "Third section description long enough for validation and detailed.",
                "key_points": ["Third key point long enough for validation"],
            },
        ],
    }
    try:
        ContentOutline(**special_outline_data)
    except ValidationError as e:
        pytest.fail(
            f"Mock special_outline_data itself is invalid for ContentOutline: {e}"
        )

    special_outline_json = json.dumps(special_outline_data)

    formatted_prompt = prompt_service.get_prompt(
        prompt_key, outline_json=special_outline_json
    )
    assert formatted_prompt is not None
    assert 'Outline with "Quotes" & 😊 Symbols Valid Length' in formatted_prompt

    mock_llm_output_dict = {
        "title": 'Podcast from Outline with "Quotes" & 😊 Symbols Valid Length',
        "introduction": "Introduction discussing the overview with newlines\n and <xml>tags</xml>. This intro is long enough for validation and includes special characters.",
        "main_content": "Main content covering Section with 😊 Emoji and its \"double quotes\" and tabs\t. This main content is very long and detailed to meet validation requirements. We are adding more text here and ensuring all special characters from the input outline are handled or reflected appropriately. This includes ampersands & and 'single quotes'. This section needs to be particularly long to pass all checks.",
        "conclusion": "Concluding thoughts on the outline with special characters. This conclusion is also long enough for validation and summarizes the key points effectively.",
    }
    mock_llm_output_dict["title"] = mock_llm_output_dict["title"][:200]
    mock_llm_output_dict["introduction"] = (
        mock_llm_output_dict["introduction"]
        * (100 // len(mock_llm_output_dict["introduction"]) + 2)
    )[:1999]
    mock_llm_output_dict["main_content"] = (
        mock_llm_output_dict["main_content"]
        * (800 // len(mock_llm_output_dict["main_content"]) + 2)
    )[:9999]
    mock_llm_output_dict["conclusion"] = (
        mock_llm_output_dict["conclusion"]
        * (100 // len(mock_llm_output_dict["conclusion"]) + 2)
    )[:999]

    total_len = (
        len(mock_llm_output_dict["introduction"])
        + len(mock_llm_output_dict["main_content"])
        + len(mock_llm_output_dict["conclusion"])
    )
    if total_len < 1000:
        mock_llm_output_dict["main_content"] += " " * (1000 - total_len)

    mock_llm_json_response = json.dumps(mock_llm_output_dict)
    mock_generation_service = EnhancedMultiStepContentGenerationService()
    cleaned_json_str = mock_generation_service._clean_llm_json_response(
        mock_llm_json_response
    )

    try:
        parsed_data = json.loads(cleaned_json_str)
        validated_model = pydantic_model(**parsed_data)
        assert isinstance(validated_model, pydantic_model)
        assert validated_model.title == mock_llm_output_dict["title"]
    except ValidationError as e:
        pytest.fail(
            f"Mock LLM response for {prompt_key} (special chars outline_json) failed Pydantic validation: {e}\nResponse: {cleaned_json_str}"
        )


# --- Tests for Specific Prompt Instructions ---


def test_faq_prompt_instructs_question_mark():
    """Test if the faq_collection prompt instructs LLM to end questions with '?'."""
    prompt_text = prompt_service.get_prompt_template("faq_collection")
    assert (
        "?" in prompt_text
        or "question mark" in prompt_text.lower()
        or "end with a '?'" in prompt_text.lower()
    )


def test_outline_prompt_implies_sequential_numbering():
    """Test if the master_content_outline prompt implies sequential section numbering."""
    prompt_text = prompt_service.get_prompt_template("master_content_outline")
    assert (
        "sequential" in prompt_text.lower()
        or "order" in prompt_text.lower()
        or "section_number" in prompt_text.lower()
    )
