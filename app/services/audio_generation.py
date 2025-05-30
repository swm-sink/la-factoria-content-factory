"""
Audio generation service for converting text to speech using ElevenLabs.
"""

import logging
import os
from typing import Dict, Any, Tuple
from elevenlabs import generate, set_api_key
from prometheus_client import Counter, Histogram
from google.cloud import storage
import uuid

from app.core.config.settings import get_settings

# Prometheus metrics
ELEVENLABS_API_CALLS = Counter(
    "elevenlabs_api_calls_total", "Total number of ElevenLabs API calls"
)
ELEVENLABS_API_DURATION = Histogram(
    "elevenlabs_api_duration_seconds", "Time spent in ElevenLabs API calls"
)


class AudioGenerationService:
    """Service for generating audio content using ElevenLabs."""

    def __init__(self):
        """Initialize the audio generation service."""
        self.settings = get_settings()
        set_api_key(self.settings.elevenlabs_api_key)
        try:
            self.gcs_client = storage.Client(project=self.settings.gcp_project_id)
            self.gcs_bucket_name = self.settings.storage_bucket
            if not self.gcs_bucket_name:
                logging.error("GCS_STORAGE_BUCKET_NAME not configured. Audio upload will fail.")
                self.gcs_client = None # Disable GCS if bucket name missing
        except Exception as e:
            logging.error(f"Failed to initialize Google Cloud Storage client: {e}", exc_info=True)
            self.gcs_client = None

    def generate_audio(self, text: str) -> Tuple[Dict[str, Any], int]:
        """Generates audio from text using ElevenLabs.

        Args:
            text: The text to convert to audio.

        Returns:
            Tuple[Dict[str, Any], int]: A dictionary containing the path to the
                generated audio file (currently a temporary local server path)
                and status, along with the HTTP status code.
        """
        if not self.settings.elevenlabs_api_key:
            logging.error("ElevenLabs API key not configured. Cannot generate audio.")
            return {
                "error": "Audio generation service not configured.",
                "status": "error",
            }, 500

        try:
            logging.info(
                f"Calling ElevenLabs for audio generation using voice ID: {self.settings.elevenlabs_voice_id}."
            )

            character_count = len(text)

            # Make the API call with timing
            ELEVENLABS_API_CALLS.inc()
            with ELEVENLABS_API_DURATION.time():
                audio = generate(
                    text=text,
                    voice=self.settings.elevenlabs_voice_id,
                    model="eleven_multilingual_v2",
                )

            # Save the audio file
            temp_audio_path = "/tmp/podcast_audio.mp3"
            with open(temp_audio_path, "wb") as f:
                f.write(audio)

            logging.info(f"Audio temporarily saved to {temp_audio_path}")

            # Upload to GCS
            audio_url_for_response = temp_audio_path # Default to local path if GCS fails
            if self.gcs_client and self.gcs_bucket_name:
                try:
                    bucket = self.gcs_client.bucket(self.gcs_bucket_name)
                    # Create a unique blob name
                    blob_name = f"audio_outputs/{uuid.uuid4()}.mp3"
                    blob = bucket.blob(blob_name)
                    
                    blob.upload_from_filename(temp_audio_path)
                    # Make the blob publicly readable for simplicity in MVP
                    # For production, consider signed URLs or more robust ACLs
                    blob.make_public()
                    audio_url_for_response = blob.public_url
                    logging.info(f"Audio uploaded to GCS: {audio_url_for_response}")
                    
                    # Clean up local temp file after successful upload
                    if os.path.exists(temp_audio_path):
                        os.remove(temp_audio_path)
                        logging.info(f"Cleaned up temporary audio file: {temp_audio_path}")

                except Exception as e:
                    logging.error(f"Failed to upload audio to GCS: {e}", exc_info=True)
                    # Fallback to local path if GCS upload fails, but this won't work in Cloud Run
                    logging.warning("GCS upload failed. Audio URL will be local path, which is not suitable for Cloud Run.")
            else:
                logging.warning("GCS client or bucket not configured. Audio URL will be local path, not suitable for Cloud Run.")

            # Log character count and estimated cost if enabled
            if self.settings.enable_cost_tracking:
                # Cost is per 1000 characters
                estimated_cost = (
                    character_count / 1000
                ) * self.settings.elevenlabs_tts_pricing_per_1k_chars

                log_payload = {
                    "message": "ElevenLabs API call for audio generation successful.",
                    "service_name": "ElevenLabs-TTS",
                    "voice_id": self.settings.elevenlabs_voice_id,
                    "model_name": "eleven_multilingual_v2",  # Or other model if configurable
                    "input_characters": character_count,
                    "estimated_cost_usd": round(estimated_cost, 6),
                }
                # Use json.dumps for structured logging if preferred, or direct logging
                logging.info(f"ElevenLabs API call details: {log_payload}")

            return {"audio_url": audio_url_for_response, "status": "success"}, 200

        except Exception as e:
            logging.error(f"Error generating audio: {e}", exc_info=True)
            return {
                "error": f"Failed to generate audio: {str(e)}",
                "status": "error",
            }, 503

    def cleanup_audio(self) -> None:
        """Cleans up temporary audio files."""
        try:
            temp_audio_path = "/tmp/podcast_audio.mp3"
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
                logging.info(f"Cleaned up temporary audio file: {temp_audio_path}")
        except Exception as e:
            logging.error(f"Error cleaning up audio file: {e}", exc_info=True)
