from elevenlabs import generate, set_api_key
from elevenlabs.api import Voice
import os
from typing import Optional
import uuid

from ..core.config import settings

class AudioService:
    def __init__(self):
        set_api_key(settings.ELEVENLABS_API_KEY)
        self.voice = Voice(
            voice_id="21m00Tcm4TlvDq8ikWAM",  # Default voice ID
            name="Rachel",
            category="premade",
            settings={
                "stability": 0.5,
                "similarity_boost": 0.75,
            }
        )

    async def generate_audio(self, text: str, filename: str) -> Optional[str]:
        """
        Generate audio from text using ElevenLabs.
        """
        try:
            # Generate audio
            audio = generate(
                text=text,
                voice=self.voice,
                model="eleven_monolingual_v1"
            )

            # Save to file
            filepath = os.path.join("storage", "audio", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, "wb") as f:
                f.write(audio)

            # Return the URL
            return f"/storage/audio/{filename}"
        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            return None

    async def get_audio(self, filename: str) -> Optional[bytes]:
        """
        Retrieve audio file.
        """
        try:
            filepath = os.path.join("storage", "audio", filename)
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, "rb") as f:
                return f.read()
        except Exception as e:
            print(f"Error retrieving audio: {str(e)}")
            return None

    # TODO: Add methods for audio synthesis, upload to GCS
    pass 