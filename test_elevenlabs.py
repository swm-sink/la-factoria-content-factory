"""Test script to verify ElevenLabs API key and voice ID (v2 client, handling generator output)."""

from elevenlabs.client import ElevenLabs


def test_elevenlabs():
    """Test ElevenLabs API key and voice ID."""
    # Set API key
    api_key = "sk_f9f15293edb761661313e56a0fb7840cc383acf4bddefaf3"
    voice_id = "j9jfwdrw7BRfcR43Qohk"

    client = ElevenLabs(api_key=api_key)

    # Test text
    test_text = "Hello! This is a test of the ElevenLabs API integration."

    try:
        # Generate audio
        audio_stream = client.text_to_speech.convert(
            text=test_text, voice_id=voice_id, model_id="eleven_multilingual_v2"
        )

        # Handle the generator output by iterating and writing chunks
        with open("test_audio.mp3", "wb") as f:
            for chunk in audio_stream:
                if chunk:
                    f.write(chunk)

        print("✅ ElevenLabs test successful!")
        print(f"✅ API Key: {api_key[:8]}...{api_key[-4:]}")
        print(f"✅ Voice ID: {voice_id}")
        print("✅ Test audio saved as 'test_audio.mp3'")

    except Exception as e:
        print("❌ ElevenLabs test failed!")
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    test_elevenlabs()
