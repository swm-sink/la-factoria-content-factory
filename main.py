"""AI Content Factory MVP - Main Flask Application.

This module defines the core Flask application for the AI Content Factory MVP,
handling web requests and routing.
"""

import logging
import os  # Keep os for environment variables
import json  # Keep json for parsing Gemini's output
import time
from typing import Dict, List, Tuple, Any, Optional
from flask import Flask, request, jsonify
import vertexai  # Add Vertex AI import
from vertexai.generative_models import (
    GenerativeModel,
)  # Remove Part as it's not directly used in this snippet
from elevenlabs.client import ElevenLabs
from prometheus_client import Counter, Histogram, start_http_server

# Configure basic logging for visibility in development and Cloud Run
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Prometheus metrics
GEMINI_API_CALLS = Counter('gemini_api_calls_total', 'Total number of Gemini API calls')
GEMINI_API_DURATION = Histogram('gemini_api_duration_seconds', 'Time spent in Gemini API calls')
ELEVENLABS_API_CALLS = Counter('elevenlabs_api_calls_total', 'Total number of ElevenLabs API calls')
ELEVENLABS_API_DURATION = Histogram('elevenlabs_api_duration_seconds', 'Time spent in ElevenLabs API calls')

# Type definitions for better code clarity
ContentResponse = Dict[str, Any]
AudioStatus = str
StatusCode = int
GenerationResult = Tuple[ContentResponse, AudioStatus, StatusCode]
TokenUsage = Dict[str, int]

def log_token_usage(response: Any) -> Optional[TokenUsage]:
    """Logs token usage from Gemini API response if available.
    
    Args:
        response: The Gemini API response object.
        
    Returns:
        Optional[TokenUsage]: Dictionary with token usage if available, None otherwise.
    """
    if not hasattr(response, 'usage_metadata'):
        return None
        
    usage = {
        'input_tokens': response.usage_metadata.prompt_token_count,
        'output_tokens': response.usage_metadata.candidates_token_count,
        'total_tokens': response.usage_metadata.total_token_count
    }
    
    # Log token usage with estimated cost (assuming $0.00025 per 1K tokens)
    estimated_cost = (usage['total_tokens'] / 1000) * 0.00025
    logging.info(
        f"Gemini API Usage - Input: {usage['input_tokens']}, "
        f"Output: {usage['output_tokens']}, Total: {usage['total_tokens']}, "
        f"Estimated Cost: ${estimated_cost:.6f}"
    )
    
    return usage

def validate_content_structure(content: Dict[str, Any]) -> Tuple[bool, str]:
    """Validates the structure of generated content.
    
    Args:
        content: The content dictionary to validate.
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    required_fields = {
        'content_outline': str,
        'podcast_script': str,
        'study_guide': str,
        'one_pager_summary': str,
        'detailed_reading_material': str,
        'faqs': list,
        'flashcards': list,
        'reading_guide_questions': list
    }
    
    for field, expected_type in required_fields.items():
        if field not in content:
            return False, f"Missing required field: {field}"
        if not isinstance(content[field], expected_type):
            return False, f"Invalid type for {field}: expected {expected_type.__name__}, got {type(content[field]).__name__}"
            
    # Validate array contents
    if not all(isinstance(faq, dict) and 'question' in faq and 'answer' in faq for faq in content['faqs']):
        return False, "Invalid FAQ structure: each FAQ must have 'question' and 'answer' fields"
        
    if not all(isinstance(flashcard, dict) and 'term' in flashcard and 'definition' in flashcard for flashcard in content['flashcards']):
        return False, "Invalid flashcard structure: each flashcard must have 'term' and 'definition' fields"
        
    if not all(isinstance(q, str) for q in content['reading_guide_questions']):
        return False, "Invalid reading guide questions: all questions must be strings"
        
    return True, ""

def generate_gemini_prompt(syllabus_text: str) -> str:
    """Generates the prompt for Gemini to create comprehensive educational content.
    
    Args:
        syllabus_text: The input syllabus or topic text.
        
    Returns:
        str: A detailed prompt instructing Gemini to generate all required content types.
    """
    return f"""
    You are an expert content creator and instructional designer. Your task is to transform the provided 'syllabus_text' into comprehensive educational content, following a structured approach.

    ---
    Syllabus Text:
    {syllabus_text}
    ---

    **Output Format:** Your response MUST be a single JSON object with the following top-level keys:
    - "content_outline": A structured outline of the main topics and subtopics
    - "podcast_script": A conversational script for a 5-7 minute podcast
    - "study_guide": A concise, actionable study guide
    - "one_pager_summary": A single-page summary of key points
    - "detailed_reading_material": In-depth explanation of concepts
    - "faqs": Array of objects with "question" and "answer" fields
    - "flashcards": Array of objects with "term" and "definition" fields
    - "reading_guide_questions": Array of critical thinking questions

    **Content Requirements:**
    1. content_outline:
       - Create a clear, hierarchical structure
       - Include main topics and key subtopics
       - Ensure logical flow and progression

    2. podcast_script:
       - Engaging, conversational tone
       - Clear introduction, main content, and conclusion
       - Approximately 500-700 words
       - Include natural transitions

    3. study_guide:
       - Concise bullet points of key concepts
       - Include 3-5 assessment questions
       - Approximately 300-400 words
       - Focus on actionable learning points

    4. one_pager_summary:
       - Single-page format
       - Highlight key takeaways
       - Use clear headings and subheadings
       - Include essential definitions

    5. detailed_reading_material:
       - Comprehensive explanation of concepts
       - Include examples and applications
       - Use clear, academic language
       - Approximately 800-1000 words

    6. faqs:
       - 5-7 common questions
       - Clear, detailed answers
       - Cover key concepts and potential misconceptions

    7. flashcards:
       - 8-10 key terms/concepts
       - Clear, concise definitions
       - Include context where helpful

    8. reading_guide_questions:
       - 5-7 critical thinking questions
       - Encourage deeper understanding
       - Include application-based questions

    Ensure all content is directly relevant to the syllabus_text and maintains consistency across all formats.
    """

def parse_gemini_response(response_text: str) -> ContentResponse:
    """Parses and validates the Gemini response, providing default values for missing content.
    
    Args:
        response_text: The raw text response from Gemini.
        
    Returns:
        ContentResponse: A dictionary containing all content types with default values for missing fields.
    """
    try:
        content = json.loads(response_text)
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse Gemini response as JSON: {e}")
        return create_error_response("Failed to parse JSON response")

    # Validate content structure
    is_valid, error_message = validate_content_structure(content)
    if not is_valid:
        logging.error(f"Invalid content structure: {error_message}")
        return create_error_response(f"Invalid content structure: {error_message}")

    return content

def create_error_response(error_message: str) -> ContentResponse:
    """Creates a standardized error response.
    
    Args:
        error_message: The error message to include.
        
    Returns:
        ContentResponse: A dictionary with error messages for all content types.
    """
    return {
        "content_outline": f"Error: {error_message}",
        "podcast_script": f"Error: {error_message}",
        "study_guide": f"Error: {error_message}",
        "one_pager_summary": f"Error: {error_message}",
        "detailed_reading_material": f"Error: {error_message}",
        "faqs": [],
        "flashcards": [],
        "reading_guide_questions": []
    }

def generate_content_with_gemini(
    syllabus_text: str,
    gcp_project_id: str,
    gemini_model_name: str,
) -> Tuple[ContentResponse, StatusCode]:
    """Generates content using Gemini API.
    
    Args:
        syllabus_text: The text of the syllabus.
        gcp_project_id: The Google Cloud Project ID.
        gemini_model_name: The name of the Gemini model to use.
        
    Returns:
        Tuple[ContentResponse, StatusCode]: Generated content and status code.
    """
    content_response = create_error_response("Not generated")
    status_code = 200

    try:
        # Initialize Vertex AI
        vertexai.init(project=gcp_project_id, location="us-central1")
        model = GenerativeModel(gemini_model_name)

        # Generate the prompt
        generation_prompt = generate_gemini_prompt(syllabus_text)

        # Log the API call with enhanced details
        logging.info(
            f"Calling Gemini model: {gemini_model_name} (Project: {gcp_project_id}) "
            f"with prompt length {len(generation_prompt)} characters."
        )

        # Make the API call with timing
        GEMINI_API_CALLS.inc()
        with GEMINI_API_DURATION.time():
            response = model.generate_content(
                generation_prompt,
                generation_config={"response_mime_type": "application/json"},
            )

        # Log token usage and cost if available
        token_usage = log_token_usage(response)

        # Parse and validate the response
        content_response = parse_gemini_response(response.text)
        logging.info("Gemini content generated successfully.")

    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}", exc_info=True)
        status_code = 503  # Service Unavailable
        for key in content_response:
            if isinstance(content_response[key], list):
                content_response[key] = []
            else:
                content_response[key] = f"Error: Failed to generate {key.replace('_', ' ')}."

    return content_response, status_code

def generate_audio_with_elevenlabs(
    podcast_script: str,
    elevenlabs_api_key: str,
    elevenlabs_voice_id: str,
) -> Tuple[AudioStatus, StatusCode]:
    """Generates audio using ElevenLabs API.
    
    Args:
        podcast_script: The podcast script to convert to audio.
        elevenlabs_api_key: The ElevenLabs API key.
        elevenlabs_voice_id: The ElevenLabs voice ID.
        
    Returns:
        Tuple[AudioStatus, StatusCode]: Audio generation status and status code.
    """
    audio_status = "Not attempted."
    status_code = 200

    try:
        elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

        logging.info(
            f"Calling ElevenLabs for audio generation using voice ID: {elevenlabs_voice_id}."
        )
        
        # Make the API call with timing
        ELEVENLABS_API_CALLS.inc()
        with ELEVENLABS_API_DURATION.time():
            audio_stream = elevenlabs_client.text_to_speech.convert(
                text=podcast_script,
                voice_id=elevenlabs_voice_id,
                model_id="eleven_multilingual_v2",
            )

        temp_audio_path = "/tmp/podcast_audio.mp3"
        with open(temp_audio_path, "wb") as f:
            for chunk in audio_stream:
                if chunk:
                    f.write(chunk)

        logging.info(f"Audio saved to {temp_audio_path}")
        audio_status = "Audio generated successfully and saved temporarily."

    except Exception as e:
        logging.error(f"Error calling ElevenLabs API: {e}", exc_info=True)
        audio_status = "Failed to generate audio."
        status_code = 503  # Service Unavailable

    return audio_status, status_code

def generate_content_and_audio(
    syllabus_text: str,
    gcp_project_id: str,
    gemini_model_name: str,
    elevenlabs_api_key: str,
    elevenlabs_voice_id: str,
) -> GenerationResult:
    """Generates comprehensive educational content and audio from syllabus text using AI APIs.

    Args:
        syllabus_text: The text of the syllabus.
        gcp_project_id: The Google Cloud Project ID.
        gemini_model_name: The name of the Gemini model to use.
        elevenlabs_api_key: The ElevenLabs API key.
        elevenlabs_voice_id: The ElevenLabs voice ID.

    Returns:
        GenerationResult: A tuple containing:
            - ContentResponse: Dictionary with all generated content types
            - AudioStatus: Status of audio generation
            - StatusCode: HTTP status code
    """
    # Generate content using Gemini
    content_response, status_code = generate_content_with_gemini(
        syllabus_text, gcp_project_id, gemini_model_name
    )

    # Only attempt audio generation if podcast script was successfully generated
    if content_response["podcast_script"] and not content_response["podcast_script"].startswith("Error:"):
        audio_status, audio_status_code = generate_audio_with_elevenlabs(
            content_response["podcast_script"],
            elevenlabs_api_key,
            elevenlabs_voice_id,
        )
        # Use the more severe status code
        status_code = max(status_code, audio_status_code)
    else:
        logging.warning(
            "Skipping ElevenLabs audio generation as podcast script was not generated or was empty/had an error."
        )
        audio_status = "Audio generation skipped: no valid podcast script."

    return content_response, audio_status, status_code

app = Flask(__name__)

# Start Prometheus metrics server
start_http_server(8000)

@app.route("/", methods=["GET"])
def hello_world() -> str:
    """Handles the root URL '/' and returns a greeting.

    Returns:
        str: A simple greeting message.
    """
    logging.info("Received request for / route.")
    return "Hello, Cloud Run! This is AI Content Factory MVP."

@app.route("/generate-content", methods=["POST"])
def generate_content() -> tuple:
    """Receives syllabus text, generates comprehensive content & audio via AI, and returns results.

    Expects a JSON payload with 'syllabus_text'.

    Returns:
        tuple: JSON response with all generated content types and audio status, or error, and HTTP status code.
    """
    logging.info("Received request for /generate-content endpoint.")
    data = request.get_json()

    # --- Input Validation (Section E.2) ---
    if (
        not data
        or "syllabus_text" not in data
        or not isinstance(data["syllabus_text"], str)
        or not data["syllabus_text"].strip()
    ):
        logging.warning("Validation failed: 'syllabus_text' is missing or empty.")
        return (
            jsonify({"error": "syllabus_text is required and cannot be empty."}),
            400,  # Bad Request
        )

    syllabus_text = data["syllabus_text"].strip()
    if not (50 <= len(syllabus_text) <= 5000):
        logging.warning(
            f"Validation failed: syllabus_text length {len(syllabus_text)} is out of bounds."
        )
        return (
            jsonify({"error": "syllabus_text must be between 50 and 5000 characters."}),
            400,  # Bad Request
        )

    # Retrieve credentials/config (using env vars for MVP - Section E.1)
    # TODO: Post-MVP - Implement retrieval from Google Secret Manager (Section E.1 project.mdc)
    # Example placeholder for Secret Manager client initialization:
    # from google.cloud import secretmanager
    # client = secretmanager.SecretManagerServiceClient()
    # ELEVENLABS_API_KEY_SECRET_NAME = "projects/your-gcp-project-id/secrets/ELEVENLABS_API_KEY/versions/latest"
    # response = client.access_secret_version(name=ELEVENLABS_API_KEY_SECRET_NAME)
    # elevenlabs_api_key = response.payload.data.decode("UTF-8")
    # Similarly for other secrets.

    gcp_project_id = os.environ.get("GCP_PROJECT_ID")
    # Using gemini-2.5-flash-preview-05-20 for better content generation quality
    gemini_model_name = os.environ.get("GEMINI_MODEL_NAME", "gemini-2.5-flash-preview-05-20")
    # TODO: Move to Secret Manager in post-MVP
    elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")  # MVP: from env var
    elevenlabs_voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

    # Check for missing environment variables before calling the AI function
    # Post-MVP: This check will need to be adapted if secrets are fetched from Secret Manager
    if not gcp_project_id or not elevenlabs_api_key:
        error_message = "Missing required environment variables: GCP_PROJECT_ID and/or ELEVENLABS_API_KEY."
        logging.error(error_message)
        return jsonify({"error": error_message}), 500

    # Generate content and audio
    content_response, audio_status, status_code = generate_content_and_audio(
        syllabus_text,
        gcp_project_id,
        gemini_model_name,
        elevenlabs_api_key,
        elevenlabs_voice_id,
    )

    # Prepare the final response
    response_data = {
        **content_response,  # Include all content types
        "audio_status": audio_status
    }

    # Handle error cases
    if status_code != 200:
        if any(value.startswith("Error:") for value in content_response.values() if isinstance(value, str)):
            error_detail = next(
                (f"Gemini Error: {value}" for value in content_response.values() 
                 if isinstance(value, str) and value.startswith("Error:")),
                "Unknown error in content generation."
            )
            return (
                jsonify({
                    "error": "Failed to generate content from AI.",
                    "error_detail": error_detail,
                    **content_response,  # Include any successfully generated content
                    "audio_status": audio_status
                }),
                status_code,
            )
        elif audio_status.startswith("Failed to generate audio"):
            return (
                jsonify({
                    **content_response,  # Include all generated content
                    "audio_status": audio_status,
                    "error": "Audio generation failed.",
                    "error_detail": f"ElevenLabs Error: {audio_status}"
                }),
                status_code,
            )

    # Success case
    return jsonify(response_data), status_code

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
