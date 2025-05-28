"""
Audio generation service for converting text to speech using ElevenLabs.
"""

import logging
import os
from typing import Dict, Any, Tuple
from elevenlabs import generate, set_api_key
from prometheus_client import Counter, Histogram

from app.core.config.settings import get_settings

# Prometheus metrics
ELEVENLABS_API_CALLS = Counter('elevenlabs_api_calls_total', 'Total number of ElevenLabs API calls')
ELEVENLABS_API_DURATION = Histogram('elevenlabs_api_duration_seconds', 'Time spent in ElevenLabs API calls')

class AudioGenerationService:
    """Service for generating audio content using ElevenLabs."""
    
    def __init__(self):
        """Initialize the audio generation service."""
        self.settings = get_settings()
        set_api_key(self.settings.elevenlabs_api_key)
        
    def generate_audio(self, text: str) -> Tuple[Dict[str, Any], int]:
        """Generates audio from text using ElevenLabs.
        
        Args:
            text: The text to convert to audio.
            
        Returns:
            Tuple[Dict[str, Any], int]: Audio generation result and status code.
        """
        try:
            logging.info(
                f"Calling ElevenLabs for audio generation using voice ID: {self.settings.elevenlabs_voice_id}."
            )
            
            # Make the API call with timing
            ELEVENLABS_API_CALLS.inc()
            with ELEVENLABS_API_DURATION.time():
                audio = generate(
                    text=text,
                    voice=self.settings.elevenlabs_voice_id,
                    model="eleven_multilingual_v2"
                )
            
            # Save the audio file
            temp_audio_path = "/tmp/podcast_audio.mp3"
            with open(temp_audio_path, "wb") as f:
                f.write(audio)
            
            logging.info(f"Audio saved to {temp_audio_path}")
            return {"audio_url": temp_audio_path, "status": "success"}, 200
            
        except Exception as e:
            logging.error(f"Error generating audio: {e}", exc_info=True)
            return {"error": f"Failed to generate audio: {str(e)}", "status": "error"}, 503
    
    def cleanup_audio(self) -> None:
        """Cleans up temporary audio files."""
        try:
            temp_audio_path = "/tmp/podcast_audio.mp3"
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
                logging.info(f"Cleaned up temporary audio file: {temp_audio_path}")
        except Exception as e:
            logging.error(f"Error cleaning up audio file: {e}", exc_info=True) 