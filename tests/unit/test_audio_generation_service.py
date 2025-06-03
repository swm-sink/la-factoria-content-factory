from unittest.mock import MagicMock, mock_open, patch

import pytest

from app.core.config.settings import Settings
from app.services.audio_generation import AudioGenerationService

# --- Fixtures ---


@pytest.fixture
def mock_settings_audio():
    return Settings(
        elevenlabs_api_key="fake_elevenlabs_key",
        elevenlabs_voice_id="fake_voice_id",
        gcp_project_id="fake-gcp-project",
        storage_bucket="fake-gcs-bucket",
        enable_cost_tracking=True,
        elevenlabs_tts_pricing_per_1k_chars=0.30,
    )


@pytest.fixture
def audio_service(mock_settings_audio):
    with patch(
        "app.services.audio_generation.get_settings", return_value=mock_settings_audio
    ):
        # Mock elevenlabs.set_api_key as it's called on init
        with patch("app.services.audio_generation.set_api_key") as mock_set_key:
            # Mock storage.Client
            with patch(
                "app.services.audio_generation.storage.Client"
            ) as MockStorageClient:
                mock_gcs_client_instance = MagicMock()
                MockStorageClient.return_value = mock_gcs_client_instance

                mock_bucket_instance = MagicMock()
                mock_gcs_client_instance.bucket.return_value = mock_bucket_instance

                mock_blob_instance = MagicMock()
                mock_blob_instance.public_url = mock_audio_config["mock_gcs_url"]
                mock_bucket_instance.blob.return_value = mock_blob_instance

                service = AudioGenerationService()
                # Attach mocks for easier access in tests
                service._mock_gcs_client = mock_gcs_client_instance
                service._mock_gcs_bucket = mock_bucket_instance
                service._mock_gcs_blob = mock_blob_instance
                yield service


@pytest.fixture
def mock_audio_config():
    """Configuration for audio generation tests"""
    return {
        "mock_gcs_url": "http://fake-gcs.test.com/audio.mp3",
        "mock_blob_name": "test_audio.mp3",
        "mock_bucket_name": "test-audio-bucket",
    }


# --- Test Cases ---


@patch("app.services.audio_generation.generate")
@patch("builtins.open", new_callable=mock_open)
@patch("os.path.exists", return_value=True)  # Assume temp file exists for cleanup
@patch("os.remove")
def test_generate_audio_success_with_gcs_upload(
    mock_os_remove,
    mock_os_exists,
    mock_file_open,
    mock_elevenlabs_generate,
    audio_service: AudioGenerationService,
):
    mock_elevenlabs_generate.return_value = b"fake_audio_bytes"
    text_to_generate = "Hello world, this is a test audio."

    result, status_code = audio_service.generate_audio(text_to_generate)

    assert status_code == 200
    assert result["status"] == "success"
    assert result["audio_url"] == mock_audio_config["mock_gcs_url"]

    mock_elevenlabs_generate.assert_called_once_with(
        text=text_to_generate,
        voice=audio_service.settings.elevenlabs_voice_id,
        model="eleven_multilingual_v2",
    )
    mock_file_open.assert_called_once_with("/tmp/podcast_audio.mp3", "wb")
    mock_file_open().write.assert_called_once_with(b"fake_audio_bytes")

    audio_service._mock_gcs_client.bucket.assert_called_once_with(
        audio_service.gcs_bucket_name
    )
    audio_service._mock_gcs_bucket.blob.assert_called_once()  # Check it's called with a UUID-based name
    blob_arg_name = audio_service._mock_gcs_bucket.blob.call_args[0][0]
    assert "audio_outputs/" in blob_arg_name
    assert ".mp3" in blob_arg_name

    audio_service._mock_gcs_blob.upload_from_filename.assert_called_once_with(
        "/tmp/podcast_audio.mp3"
    )
    audio_service._mock_gcs_blob.make_public.assert_called_once()
    mock_os_remove.assert_called_once_with("/tmp/podcast_audio.mp3")


@patch("app.services.audio_generation.generate")
@patch("builtins.open", new_callable=mock_open)
def test_generate_audio_no_elevenlabs_key(
    mock_file_open,
    mock_elevenlabs_generate,
    audio_service: AudioGenerationService,
    mock_settings_audio,
):
    mock_settings_audio.elevenlabs_api_key = None  # Simulate missing key
    # Re-initialize service with modified settings for this test
    with patch(
        "app.services.audio_generation.get_settings", return_value=mock_settings_audio
    ):
        with patch(
            "app.services.audio_generation.set_api_key"
        ):  # Mock set_api_key again
            service_no_key = AudioGenerationService()

    result, status_code = service_no_key.generate_audio("Test text")

    assert status_code == 500
    assert result["status"] == "error"
    assert "Audio generation service not configured" in result["error"]
    mock_elevenlabs_generate.assert_not_called()


@patch("app.services.audio_generation.generate")
@patch("builtins.open", new_callable=mock_open)
def test_generate_audio_gcs_client_not_configured(
    mock_file_open,
    mock_elevenlabs_generate,
    audio_service: AudioGenerationService,
    mock_settings_audio,
):
    mock_elevenlabs_generate.return_value = b"fake_audio_bytes"
    mock_settings_audio.storage_bucket = None  # Simulate GCS not configured

    with patch(
        "app.services.audio_generation.get_settings", return_value=mock_settings_audio
    ):
        with patch("app.services.audio_generation.set_api_key"):
            # For this test, we need to ensure GCS client is None in the service instance
            with patch(
                "app.services.audio_generation.storage.Client", return_value=None
            ) as MockStorageClientNone:
                service_no_gcs = AudioGenerationService()
                service_no_gcs.gcs_client = None  # Explicitly set to None

    result, status_code = service_no_gcs.generate_audio("Test text")

    assert status_code == 200
    assert result["status"] == "success"
    assert result["audio_url"] == "/tmp/podcast_audio.mp3"  # Should be local path

    mock_elevenlabs_generate.assert_called_once()
    # GCS methods should not be called
    if (
        hasattr(service_no_gcs, "_mock_gcs_client") and service_no_gcs._mock_gcs_client
    ):  # Check if mock was even attached
        service_no_gcs._mock_gcs_client.bucket.assert_not_called()


@patch(
    "app.services.audio_generation.generate",
    side_effect=Exception("ElevenLabs API Error"),
)
def test_generate_audio_elevenlabs_api_error(
    mock_elevenlabs_generate_error, audio_service: AudioGenerationService
):
    result, status_code = audio_service.generate_audio("Test text")

    assert status_code == 503
    assert result["status"] == "error"
    assert "Failed to generate audio: ElevenLabs API Error" in result["error"]
    mock_elevenlabs_generate_error.assert_called_once()


@patch("app.services.audio_generation.generate")
@patch("builtins.open", new_callable=mock_open)
def test_generate_audio_gcs_upload_error(
    mock_file_open, mock_elevenlabs_generate, audio_service: AudioGenerationService
):
    mock_elevenlabs_generate.return_value = b"fake_audio_bytes"
    audio_service._mock_gcs_blob.upload_from_filename.side_effect = Exception(
        "GCS Upload Failed"
    )

    result, status_code = audio_service.generate_audio("Test text")

    assert status_code == 200  # Still returns 200 but with local path
    assert result["status"] == "success"
    assert result["audio_url"] == "/tmp/podcast_audio.mp3"  # Fallback to local path
    audio_service._mock_gcs_blob.upload_from_filename.assert_called_once()


@patch("app.services.audio_generation.generate")
@patch("builtins.open", new_callable=mock_open)
@patch("logging.Logger.info")  # To capture log messages
def test_generate_audio_cost_tracking(
    mock_logger_info,
    mock_file_open,
    mock_elevenlabs_generate,
    audio_service: AudioGenerationService,
    mock_settings_audio,
):
    mock_elevenlabs_generate.return_value = b"fake_audio_bytes"
    text = "This is a test text with exactly 50 characters."  # Length 50
    character_count = len(text)
    expected_cost = (
        character_count / 1000
    ) * mock_settings_audio.elevenlabs_tts_pricing_per_1k_chars

    # Ensure cost tracking is enabled
    mock_settings_audio.enable_cost_tracking = True
    with patch(
        "app.services.audio_generation.get_settings", return_value=mock_settings_audio
    ):
        # Re-init service or ensure setting is picked up if service was already created
        # For simplicity, assume audio_service uses the updated mock_settings_audio if it's passed around
        # or re-initialize if necessary. Here, audio_service fixture already uses it.
        audio_service.settings = (
            mock_settings_audio  # Ensure it uses the modified settings
        )

    audio_service.generate_audio(text)

    found_log = False
    for call_args in mock_logger_info.call_args_list:
        log_message = call_args[0][0]
        if (
            isinstance(log_message, str)
            and "ElevenLabs API call details" in log_message
        ):
            # Example: "ElevenLabs API call details: {'message': ..., 'estimated_cost_usd': 0.015}"
            assert f"'input_characters': {character_count}" in log_message
            assert (
                f"'estimated_cost_usd': {expected_cost:.6f}" in log_message
            )  # Check for rounded cost
            found_log = True
            break
    assert found_log, "Cost tracking log message not found or incorrect."


def test_cleanup_audio_file_exists(audio_service: AudioGenerationService):
    with patch("os.path.exists", return_value=True) as mock_exists:
        with patch("os.remove") as mock_remove:
            audio_service.cleanup_audio()
            mock_exists.assert_called_once_with("/tmp/podcast_audio.mp3")
            mock_remove.assert_called_once_with("/tmp/podcast_audio.mp3")


def test_cleanup_audio_file_not_exists(audio_service: AudioGenerationService):
    with patch("os.path.exists", return_value=False) as mock_exists:
        with patch("os.remove") as mock_remove:
            audio_service.cleanup_audio()
            mock_exists.assert_called_once_with("/tmp/podcast_audio.mp3")
            mock_remove.assert_not_called()
