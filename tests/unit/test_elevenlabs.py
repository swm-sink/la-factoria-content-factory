"""Test script to verify ElevenLabs API key and voice ID (v0.2.27 API)."""

import os

from elevenlabs import set_api_key
from elevenlabs.api import generate
from elevenlabs.exceptions import APIError


def test_elevenlabs():
    """Test ElevenLabs API key and voice ID."""
    # Set API key
    api_key = "sk_f9f15293edb761661313e56a0fb7840cc383acf4bddefaf3"
    voice_id = "j9jfwdrw7BRfcR43Qohk"

    # Set API key for the session
    set_api_key(api_key)

    # Test text
    test_text = "Hello! This is a test of the ElevenLabs API integration."

    try:
        # Generate audio using the simple function API
        audio = generate(text=test_text, voice=voice_id, model="eleven_multilingual_v2")

        # Save the audio file
        with open("test_audio.mp3", "wb") as f:
            f.write(audio)

        print("✅ ElevenLabs test successful!")
        print(f"✅ API Key: {api_key[:8]}...{api_key[-4:]}")
        print(f"✅ Voice ID: {voice_id}")
        print("✅ Test audio saved as 'test_audio.mp3'")

        # Cleanup test file
        if os.path.exists("test_audio.mp3"):
            os.remove("test_audio.mp3")
            print("✅ Test audio file cleaned up")

    except APIError as e:
        print("❌ ElevenLabs API error!")
        print(f"API Error: {str(e)}")
    except Exception as e:
        print("❌ ElevenLabs test failed!")
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    test_elevenlabs()
