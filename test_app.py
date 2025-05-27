"""Unit tests for the AI Content Factory MVP Flask application."""

import pytest
import os
import time
from unittest.mock import patch, MagicMock
from flask import Flask

# Apply module-level patches
patch_vertexai_init = patch("main.vertexai.init")
mocked_vertexai_init = patch_vertexai_init.start()

# Apply module-level patch for Flask.route BEFORE importing main
patch_flask_route = patch("flask.Flask.route", return_value=lambda f: f)
patch_flask_route.start()

from main import (
    app,
    ElevenLabs,
    GenerativeModel,
    generate_content_and_audio,
    generate_content_with_gemini,
    generate_audio_with_elevenlabs,
    ContentResponse,
    validate_content_structure,
    create_error_response,
    log_token_usage
)

# Stop the Flask.route patch after importing main
patch_flask_route.stop()

@pytest.fixture
def client():
    """Configures the Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_hello_world(client):
    """Tests the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Hello, Cloud Run! This is AI Content Factory MVP." in response.data.decode()

def test_generate_content_missing_syllabus(client):
    """Tests missing syllabus_text input."""
    response = client.post("/generate-content", json={})
    assert response.status_code == 400
    assert "syllabus_text is required" in response.get_json()["error"]

def test_generate_content_empty_syllabus(client):
    """Tests empty syllabus_text input."""
    response = client.post("/generate-content", json={"syllabus_text": ""})
    assert response.status_code == 400
    assert "syllabus_text is required" in response.get_json()["error"]

def test_generate_content_too_short_syllabus(client):
    """Tests syllabus_text that is too short."""
    response = client.post("/generate-content", json={"syllabus_text": "Too short"})
    assert response.status_code == 400
    assert (
        "syllabus_text must be between 50 and 5000 characters"
        in response.get_json()["error"]
    )

def create_mock_content_response() -> ContentResponse:
    """Creates a mock content response for testing."""
    return {
        "content_outline": "Mock content outline",
        "podcast_script": "Mock podcast script",
        "study_guide": "Mock study guide",
        "one_pager_summary": "Mock one-pager summary",
        "detailed_reading_material": "Mock detailed reading material",
        "faqs": [
            {"question": "Mock question 1", "answer": "Mock answer 1"},
            {"question": "Mock question 2", "answer": "Mock answer 2"}
        ],
        "flashcards": [
            {"term": "Mock term 1", "definition": "Mock definition 1"},
            {"term": "Mock term 2", "definition": "Mock definition 2"}
        ],
        "reading_guide_questions": [
            "Mock question 1?",
            "Mock question 2?"
        ]
    }

def test_validate_content_structure_valid():
    """Tests validation of valid content structure."""
    content = create_mock_content_response()
    is_valid, error_message = validate_content_structure(content)
    assert is_valid
    assert error_message == ""

def test_validate_content_structure_missing_field():
    """Tests validation of content with missing field."""
    content = create_mock_content_response()
    del content["content_outline"]
    is_valid, error_message = validate_content_structure(content)
    assert not is_valid
    assert "Missing required field: content_outline" in error_message

def test_validate_content_structure_invalid_type():
    """Tests validation of content with invalid field type."""
    content = create_mock_content_response()
    content["content_outline"] = 123  # Should be string
    is_valid, error_message = validate_content_structure(content)
    assert not is_valid
    assert "Invalid type for content_outline" in error_message

def test_validate_content_structure_invalid_faq():
    """Tests validation of content with invalid FAQ structure."""
    content = create_mock_content_response()
    content["faqs"] = [{"invalid": "structure"}]  # Missing question/answer
    is_valid, error_message = validate_content_structure(content)
    assert not is_valid
    assert "Invalid FAQ structure" in error_message

def test_validate_content_structure_invalid_flashcard():
    """Tests validation of content with invalid flashcard structure."""
    content = create_mock_content_response()
    content["flashcards"] = [{"invalid": "structure"}]  # Missing term/definition
    is_valid, error_message = validate_content_structure(content)
    assert not is_valid
    assert "Invalid flashcard structure" in error_message

def test_validate_content_structure_invalid_questions():
    """Tests validation of content with invalid reading guide questions."""
    content = create_mock_content_response()
    content["reading_guide_questions"] = [123]  # Should be string
    is_valid, error_message = validate_content_structure(content)
    assert not is_valid
    assert "Invalid reading guide questions" in error_message

def test_create_error_response():
    """Tests creation of standardized error response."""
    error_message = "Test error message"
    response = create_error_response(error_message)
    
    # Check all fields have error message
    for key in ["content_outline", "podcast_script", "study_guide", 
                "one_pager_summary", "detailed_reading_material"]:
        assert response[key] == f"Error: {error_message}"
    
    # Check arrays are empty
    assert response["faqs"] == []
    assert response["flashcards"] == []
    assert response["reading_guide_questions"] == []

def test_log_token_usage():
    """Tests token usage logging functionality."""
    # Create a mock response with usage metadata
    mock_response = MagicMock()
    mock_response.usage_metadata.prompt_token_count = 100
    mock_response.usage_metadata.candidates_token_count = 200
    mock_response.usage_metadata.total_token_count = 300

    # Test token usage logging
    usage = log_token_usage(mock_response)
    assert usage is not None
    assert usage["input_tokens"] == 100
    assert usage["output_tokens"] == 200
    assert usage["total_tokens"] == 300

def test_log_token_usage_no_metadata():
    """Tests token usage logging when metadata is not available."""
    # Create a mock response without usage metadata
    mock_response = MagicMock()
    delattr(mock_response, 'usage_metadata')

    # Test token usage logging
    usage = log_token_usage(mock_response)
    assert usage is None

@patch("main.generate_content_with_gemini")
def test_generate_content_success(mock_generate_content, client):
    """Tests successful content generation."""
    # Configure the mock to return successful results
    mock_content = create_mock_content_response()
    mock_generate_content.return_value = (mock_content, 200)

    # Patch os.environ for this specific test request
    with patch.dict(
        "os.environ",
        {
            "GCP_PROJECT_ID": "dummy-project-id",
            "ELEVENLABS_API_KEY": "dummy-elevenlabs-key",
        },
    ):
        response = client.post(
            "/generate-content",
            json={
                "syllabus_text": "A sample syllabus text for testing purposes. "
                * 10  # Ensure length > 50
            },
        )

    assert response.status_code == 200
    json_data = response.get_json()
    
    # Verify all content types are present and correct
    assert json_data["content_outline"] == "Mock content outline"
    assert json_data["podcast_script"] == "Mock podcast script"
    assert json_data["study_guide"] == "Mock study guide"
    assert json_data["one_pager_summary"] == "Mock one-pager summary"
    assert json_data["detailed_reading_material"] == "Mock detailed reading material"
    
    # Verify array content
    assert len(json_data["faqs"]) == 2
    assert json_data["faqs"][0]["question"] == "Mock question 1"
    assert json_data["faqs"][0]["answer"] == "Mock answer 1"
    
    assert len(json_data["flashcards"]) == 2
    assert json_data["flashcards"][0]["term"] == "Mock term 1"
    assert json_data["flashcards"][0]["definition"] == "Mock definition 1"
    
    assert len(json_data["reading_guide_questions"]) == 2
    assert json_data["reading_guide_questions"][0] == "Mock question 1?"
    
    mock_generate_content.assert_called_once()

@patch("main.generate_content_with_gemini")
def test_generate_content_gemini_error(mock_generate_content, client):
    """Tests Gemini API error handling."""
    # Configure the mock to return a Gemini error
    error_content = create_error_response("Failed to generate content from AI")
    mock_generate_content.return_value = (error_content, 503)

    # Patch os.environ for this specific test request
    with patch.dict(
        "os.environ",
        {
            "GCP_PROJECT_ID": "dummy-project-id",
            "ELEVENLABS_API_KEY": "dummy-elevenlabs-key",
        },
    ):
        response = client.post(
            "/generate-content",
            json={
                "syllabus_text": "A sample syllabus text for testing purposes. " * 10
            },
        )

    assert response.status_code == 503
    json_data = response.get_json()
    assert "Failed to generate content from AI." in json_data["error"]
    assert "Gemini Error:" in json_data["error_detail"]
    
    # Verify all content fields are present in error response
    for key in error_content:
        assert key in json_data
        if isinstance(error_content[key], list):
            assert isinstance(json_data[key], list)
            assert len(json_data[key]) == 0
        else:
            assert json_data[key].startswith("Error:")
    
    mock_generate_content.assert_called_once()

@patch("main.generate_content_with_gemini")
@patch("main.generate_audio_with_elevenlabs")
def test_generate_content_elevenlabs_error(mock_generate_audio, mock_generate_content, client):
    """Tests ElevenLabs API error handling."""
    # Configure the mocks to return successful content but ElevenLabs error
    mock_content = create_mock_content_response()
    mock_generate_content.return_value = (mock_content, 200)
    mock_generate_audio.return_value = ("Failed to generate audio.", 503)

    # Patch os.environ for this specific test request
    with patch.dict(
        "os.environ",
        {
            "GCP_PROJECT_ID": "dummy-project-id",
            "ELEVENLABS_API_KEY": "dummy-elevenlabs-key",
        },
    ):
        response = client.post(
            "/generate-content",
            json={
                "syllabus_text": "A sample syllabus text for testing purposes. " * 10
            },
        )

    assert response.status_code == 503
    json_data = response.get_json()
    assert "Audio generation failed." in json_data["error"]
    assert "ElevenLabs Error:" in json_data["error_detail"]
    
    # Verify content is still present despite audio error
    assert json_data["content_outline"] == "Mock content outline"
    assert json_data["podcast_script"] == "Mock podcast script"
    
    mock_generate_content.assert_called_once()
    mock_generate_audio.assert_called_once()

def test_generate_content_missing_env_vars(client):
    """Tests handling of missing environment variables."""
    # Patch os.environ to simulate missing variables
    with patch.dict("os.environ", {}, clear=True):
        response = client.post(
            "/generate-content",
            json={
                "syllabus_text": "A sample syllabus text for testing purposes. " * 10
            },
        )

    assert response.status_code == 500
    json_data = response.get_json()
    assert "Missing required environment variables" in json_data["error"]

def test_generate_content_large_input(client):
    """Tests handling of very large input."""
    # Create a very large syllabus text
    large_text = "A" * 5001  # Exceeds the 5000 character limit

    response = client.post(
        "/generate-content",
        json={"syllabus_text": large_text},
    )

    assert response.status_code == 400
    json_data = response.get_json()
    assert "syllabus_text must be between 50 and 5000 characters" in json_data["error"]

def test_generate_content_special_characters(client):
    """Tests handling of input with special characters."""
    special_text = "!@#$%^&*()_+{}|:<>?[]\\;',./~`" * 2  # Ensure length > 50

    with patch("main.generate_content_with_gemini") as mock_generate_content:
        mock_content = create_mock_content_response()
        mock_generate_content.return_value = (mock_content, 200)

        response = client.post(
            "/generate-content",
            json={"syllabus_text": special_text},
        )

    assert response.status_code == 200
    json_data = response.get_json()
    assert "content_outline" in json_data
    assert "podcast_script" in json_data

# Stop the module-level patch after the tests are done
patch_vertexai_init.stop()
