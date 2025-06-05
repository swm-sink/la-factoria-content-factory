#!/usr/bin/env python3
import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing Vertex AI connection...")

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel

    project_id = os.getenv("GCP_PROJECT_ID", "ai-content-factory-460918")
    location = os.getenv("GCP_LOCATION", "us-central1")
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash-preview-05-20")

    print(f"Project ID: {project_id}")
    print(f"Location: {location}")
    print(f"Model: {model_name}")

    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)

    # Remove 'models/' prefix if present
    if model_name.startswith("models/"):
        model_name = model_name.replace("models/", "")

    # Create model instance
    model = GenerativeModel(model_name)

    # Test generation
    prompt = "Say hello in JSON format with a field called 'greeting'"
    response = model.generate_content(prompt)

    print(f"\nSuccess! Response: {response.text}")

except Exception as e:
    print(f"\nError: {type(e).__name__}: {e}")
    sys.exit(1)
