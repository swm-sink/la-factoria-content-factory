#!/usr/bin/env python3
"""
Test script to verify Vertex AI connection and configuration
Run this before deploying to ensure everything is working correctly
"""

import json
import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 AI Content Factory - Vertex AI Setup Verification")
print("=" * 50)

# Check required environment variables
required_vars = {
    "GCP_PROJECT_ID": os.getenv("GCP_PROJECT_ID"),
    "GCP_LOCATION": os.getenv("GCP_LOCATION", "us-central1"),
    "GEMINI_MODEL_NAME": os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash"),
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    print("❌ Missing required environment variables:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\nPlease set these in your .env file or environment")
    sys.exit(1)

print("✅ Environment variables loaded:")
for var, value in required_vars.items():
    print(f"   {var}: {value}")

# Check for authentication
print("\n🔐 Checking authentication...")
google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if google_creds:
    print(f"   Using service account: {google_creds}")
    if not os.path.exists(google_creds):
        print(f"   ❌ Service account file not found: {google_creds}")
        sys.exit(1)
else:
    print("   Using Application Default Credentials (gcloud auth)")

# Test Vertex AI connection
print("\n🚀 Testing Vertex AI connection...")
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel

    # Initialize Vertex AI
    vertexai.init(
        project=required_vars["GCP_PROJECT_ID"], location=required_vars["GCP_LOCATION"]
    )
    print("   ✅ Vertex AI initialized successfully")

    # Test model instantiation
    model_name = required_vars["GEMINI_MODEL_NAME"]
    if model_name.startswith("models/"):
        model_name = model_name.replace("models/", "")

    model = GenerativeModel(model_name)
    print(f"   ✅ Model '{model_name}' loaded successfully")

    # Test generation
    print("\n📝 Testing content generation...")
    test_prompt = "Generate a JSON object with a single field 'greeting' containing a friendly hello message."

    response = model.generate_content(test_prompt)
    print("   ✅ Generation successful!")
    print(f"   Response preview: {response.text[:100]}...")

    # Test JSON parsing (important for the app)
    try:
        # Clean potential markdown
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        json_data = json.loads(text.strip())
        print("   ✅ JSON parsing successful")
        print(f"   Parsed data: {json_data}")
    except json.JSONDecodeError as e:
        print(f"   ⚠️  JSON parsing failed: {e}")
        print(
            "   Note: The app expects JSON responses, ensure prompts request JSON format"
        )

except ImportError:
    print("   ❌ vertexai package not installed")
    print("   Run: pip install google-cloud-aiplatform vertexai")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {type(e).__name__}: {e}")
    print("\n   Troubleshooting tips:")
    print("   1. Run: gcloud auth application-default login")
    print("   2. Ensure Vertex AI API is enabled in your project")
    print("   3. Check project permissions")
    sys.exit(1)

# Test the actual app's LLM client
print("\n🔧 Testing app's SimpleLLMClient...")
try:
    from app.core.config.settings import Settings
    from app.services.simple_llm_client import SimpleLLMClient

    settings = Settings()
    client = SimpleLLMClient(settings)

    if client.is_available():
        print("   ✅ SimpleLLMClient initialized successfully")
        print("   ℹ️  Full app testing requires running in async context")
        print("   Run 'docker compose up' to test the complete application")
    else:
        print("   ❌ SimpleLLMClient not available")

except ImportError as e:
    print(f"   ⚠️  Could not import app modules: {e}")
    print("   This is normal if running outside the app context")
except Exception as e:
    print(f"   ❌ Error testing SimpleLLMClient: {e}")

# Summary
print("\n" + "=" * 50)
print("📊 SETUP VERIFICATION SUMMARY")
print("=" * 50)

if not missing_vars:
    print("✅ Vertex AI is properly configured and working!")
    print("\nNext steps:")
    print("1. Test the app locally: docker compose up")
    print("2. Test content generation with curl (see VERTEX_AI_SETUP_GUIDE.md)")
    print("3. Deploy to Cloud Run when ready")
else:
    print("❌ Setup incomplete. Please fix the issues above.")

print("\n� Tip: Check docs/VERTEX_AI_SETUP_GUIDE.md for detailed setup instructions")
