import importlib
import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

# Import the settings module itself to allow reloading/re-importing for cache tests
from app.core.config import settings as settings_module
from app.core.config.settings import (
    GSM_API_KEY_NAME,
    GSM_ELEVENLABS_API_KEY_NAME,
    GSM_JWT_SECRET_KEY_NAME,
    GSM_SENTRY_DSN_NAME,
    Settings,
)

# Helper to reset relevant environment variables
RELEVANT_ENV_VARS = [
    "GCP_PROJECT_ID",
    "API_KEY",
    "ELEVENLABS_API_KEY",
    "JWT_SECRET_KEY",
    "SENTRY_DSN",
    "APP_PORT",
    "CORS_ORIGINS",
    "GEMINI_MODEL_NAME",
    "REDIS_HOST",
    "REDIS_PORT",
    "DATABASE_URL"
    # Add any other env vars that might affect default settings tests
]


@pytest.fixture(autouse=True)
def clear_settings_cache_and_env():
    """Clears the lru_cache for get_settings and temporarily unsets relevant env vars."""
    # Store original env vars
    original_env_values = {var: os.environ.get(var) for var in RELEVANT_ENV_VARS}

    # Unset for the duration of the test
    for var in RELEVANT_ENV_VARS:
        if var in os.environ:
            del os.environ[var]

    # Clear lru_cache
    settings_module.get_settings.cache_clear()
    # Ensure SecretManagerClient is reset for tests that mock it
    settings_module.Settings._secrets_client = None

    yield  # Test runs here

    # Restore original env vars
    for var, value in original_env_values.items():
        if value is not None:
            os.environ[var] = value
        elif var in os.environ:  # If it was set to None but existed
            del os.environ[var]

    # Clear cache again for next test
    settings_module.get_settings.cache_clear()
    settings_module.Settings._secrets_client = None


def test_settings_default_values(test_settings):
    """Test that settings have correct default values."""
    assert test_settings.api_key == "test_key"
    assert test_settings.gcp_project_id == "test-project"
    assert test_settings.gcp_location == "us-central1"
    assert test_settings.gemini_model_name == "models/gemini-2.5-flash-preview-05-20"
    assert test_settings.cache_max_size == 100
    assert test_settings.cache_ttl_seconds == 3600
    assert test_settings.max_refinement_iterations == 1
    assert test_settings.cache_min_quality_retrieval == 0.6


def test_settings_from_env(monkeypatch, test_settings):
    """Test that settings can be overridden from environment variables."""
    # Override some settings
    monkeypatch.setenv("API_KEY", "env_test_key")
    monkeypatch.setenv("GCP_PROJECT_ID", "env_test_project")
    monkeypatch.setenv("GEMINI_MODEL_NAME", "models/gemini-1.0-pro-001")

    settings = Settings()

    # Check that environment variables take precedence
    assert settings.api_key == "env_test_key"
    assert settings.gcp_project_id == "env_test_project"
    assert settings.gemini_model_name == "models/gemini-1.0-pro-001"

    # Check that other settings remain at defaults
    assert settings.gcp_location == test_settings.gcp_location
    assert settings.cache_max_size == test_settings.cache_max_size
    assert settings.cache_ttl_seconds == test_settings.cache_ttl_seconds
    assert settings.max_refinement_iterations == test_settings.max_refinement_iterations
    assert (
        settings.cache_min_quality_retrieval
        == test_settings.cache_min_quality_retrieval
    )


def test_settings_validation():
    """Test that settings validation works correctly."""
    # Test valid settings
    valid_settings = Settings(
        api_key="test_key",
        gcp_project_id="test-project",
        gcp_location="us-central1",
        gemini_model_name="models/gemini-2.5-flash-preview-05-20",
        cache_max_size=100,
        cache_ttl_seconds=3600,
        max_refinement_iterations=1,
        cache_min_quality_retrieval=0.6,
    )
    assert valid_settings is not None

    # Test invalid settings
    with pytest.raises(ValueError):
        Settings(api_key="")  # Empty API key

    with pytest.raises(ValueError):
        Settings(gcp_project_id="")  # Empty project ID

    with pytest.raises(ValueError):
        Settings(gemini_model_name="invalid-model")  # Invalid model name

    with pytest.raises(ValueError):
        Settings(cache_max_size=-1)  # Negative cache size

    with pytest.raises(ValueError):
        Settings(cache_ttl_seconds=-1)  # Negative TTL

    with pytest.raises(ValueError):
        Settings(max_refinement_iterations=0)  # Zero iterations

    with pytest.raises(ValueError):
        Settings(cache_min_quality_retrieval=1.5)  # Quality > 1.0


def test_settings_model_name_validation():
    """Test that model name validation works correctly."""
    # Test valid model names
    valid_names = [
        "models/gemini-1.0-pro",
        "models/gemini-1.0-pro-001",
        "models/gemini-1.5-pro",
        "models/gemini-1.5-pro-001",
        "models/gemini-1.5-flash",
        "models/gemini-1.5-flash-001",
        "models/gemini-2.5-flash-preview-05-20",
    ]

    for name in valid_names:
        settings = Settings(gemini_model_name=name)
        assert settings.gemini_model_name == name

    # Test invalid model names
    invalid_names = [
        "gemini-1.0-pro",  # Missing models/ prefix
        "models/invalid-model",
        "models/gemini-1.0-pro-invalid",
        "models/gemini-1.5-invalid",
        "models/gemini-2.0-pro",  # Invalid version
    ]

    for name in invalid_names:
        with pytest.raises(ValueError):
            Settings(gemini_model_name=name)


def test_settings_from_env_validation(monkeypatch):
    """Test that environment variable validation works correctly."""
    # Test valid environment variables
    monkeypatch.setenv("GEMINI_MODEL_NAME", "models/gemini-1.0-pro-001")
    settings = Settings()
    assert settings.gemini_model_name == "models/gemini-1.0-pro-001"

    # Test invalid environment variables
    monkeypatch.setenv("GEMINI_MODEL_NAME", "invalid-model")
    with pytest.raises(ValueError):
        Settings()


def test_settings_load_from_env(monkeypatch):
    """Test that Settings correctly load values from environment variables."""
    monkeypatch.setenv("APP_PORT", "9090")
    monkeypatch.setenv("GCP_LOCATION", "europe-west1")
    monkeypatch.setenv("API_KEY", "env_api_key_123")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "env_eleven_key_456")
    monkeypatch.setenv(
        "JWT_SECRET_KEY", "env_jwt_secret_key_minimum_length_is_32_chars"
    )
    monkeypatch.setenv("SENTRY_DSN", "http://public@example.com/1")
    monkeypatch.setenv("CORS_ORIGINS", "http://test.com,https://another.org")
    monkeypatch.setenv("GEMINI_MODEL_NAME", "models/gemini-1.0-pro-001")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:port/db")

    # GCP_PROJECT_ID is not set, so GSM loading should be skipped.

    importlib.reload(
        settings_module
    )  # Reload to apply monkeypatched env vars before Settings class definition
    settings = settings_module.Settings()

    assert settings.app_port == 9090
    assert settings.gcp_location == "europe-west1"
    assert settings.api_key == "env_api_key_123"
    assert settings.elevenlabs_api_key == "env_eleven_key_456"
    assert settings.jwt_secret_key == "env_jwt_secret_key_minimum_length_is_32_chars"
    assert settings.sentry_dsn == "http://public@example.com/1"
    assert settings.cors_origins == ["http://test.com", "https://another.org"]
    assert settings.gemini_model_name == "models/gemini-1.0-pro-001"
    assert settings.database_url == "postgresql://user:pass@host:port/db"


def test_settings_cors_origins_processing(monkeypatch):
    """Test CORS_ORIGINS_ENV processing."""
    # Provide required keys via env for this test
    monkeypatch.setenv("API_KEY", "test_cors_api_key")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "test_cors_eleven_key")
    monkeypatch.setenv("JWT_SECRET_KEY", "test_cors_jwt_secret_key_min_length_32_chars")

    # Test with env var
    monkeypatch.setenv("CORS_ORIGINS", "http://a.com, http://b.com")
    importlib.reload(settings_module)
    settings_env = settings_module.Settings()
    assert settings_env.cors_origins == ["http://a.com", "http://b.com"]

    # Test default when env var is not set
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    importlib.reload(settings_module)
    settings_default = settings_module.Settings()
    assert "http://localhost:3000" in settings_default.cors_origins


def test_settings_invalid_gemini_model_name(monkeypatch):
    monkeypatch.setenv("API_KEY", "testkey_invalid_gemini")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "testkey_invalid_gemini_eleven")
    monkeypatch.setenv(
        "JWT_SECRET_KEY", "testkey_invalid_gemini_jwt_min_length_32_chars"
    )
    monkeypatch.setenv("GEMINI_MODEL_NAME", "invalid-model-name")

    importlib.reload(settings_module)
    with pytest.raises(ValidationError):
        settings_module.Settings()


@patch("app.core.config.settings.SecretManagerClient")
def test_settings_load_from_gsm_success(MockSecretManagerClient, monkeypatch):
    monkeypatch.setenv("GCP_PROJECT_ID", "fake-project-id-gsm-success")

    mock_gsm_client_instance = MockSecretManagerClient.return_value
    mock_gsm_client_instance.client = True

    secrets_map = {
        GSM_API_KEY_NAME: "gsm_api_key_789",
        GSM_ELEVENLABS_API_KEY_NAME: "gsm_eleven_key_101",
        GSM_JWT_SECRET_KEY_NAME: "gsm_jwt_secret_key_that_is_very_long_and_secure",
        GSM_SENTRY_DSN_NAME: "http://gsm_sentry@example.com/2",
    }
    mock_gsm_client_instance.get_secret.side_effect = (
        lambda secret_name: secrets_map.get(secret_name)
    )

    importlib.reload(settings_module)
    settings_module.get_settings.cache_clear()  # Ensure get_settings re-runs Settings()
    settings = settings_module.get_settings()

    assert settings.api_key == "gsm_api_key_789"
    assert settings.elevenlabs_api_key == "gsm_eleven_key_101"
    assert settings.jwt_secret_key == "gsm_jwt_secret_key_that_is_very_long_and_secure"
    assert settings.sentry_dsn == "http://gsm_sentry@example.com/2"
    mock_gsm_client_instance.get_secret.assert_any_call(GSM_API_KEY_NAME)


@patch("app.core.config.settings.SecretManagerClient")
def test_settings_gsm_fallback_to_env(MockSecretManagerClient, monkeypatch):
    monkeypatch.setenv("GCP_PROJECT_ID", "fake-project-id-gsm-fallback")

    mock_gsm_client_instance = MockSecretManagerClient.return_value
    mock_gsm_client_instance.client = True
    mock_gsm_client_instance.get_secret.side_effect = (
        lambda secret_name: None
        if secret_name == GSM_API_KEY_NAME
        else "gsm_other_value_for_elevenlabs_or_jwt"
    )

    monkeypatch.setenv("API_KEY", "env_fallback_api_key")
    # Ensure other required keys are set if GSM doesn't provide them for this test case
    monkeypatch.setenv("ELEVENLABS_API_KEY", "env_eleven_key_for_fallback_test")
    monkeypatch.setenv(
        "JWT_SECRET_KEY", "env_jwt_secret_for_fallback_test_min_length_32"
    )

    importlib.reload(settings_module)
    settings_module.get_settings.cache_clear()
    settings = settings_module.get_settings()

    assert settings.api_key == "env_fallback_api_key"


@patch("app.core.config.settings.SecretManagerClient")
def test_settings_gsm_client_init_failure(MockSecretManagerClient, monkeypatch):
    monkeypatch.setenv("GCP_PROJECT_ID", "fake-project-id-gsm-fail")

    mock_gsm_client_instance = MockSecretManagerClient.return_value
    mock_gsm_client_instance.client = None

    monkeypatch.setenv("API_KEY", "env_api_key_no_gsm")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "env_eleven_key_no_gsm")
    monkeypatch.setenv("JWT_SECRET_KEY", "env_jwt_secret_key_no_gsm_min_length_32")

    importlib.reload(settings_module)
    settings_module.get_settings.cache_clear()
    settings = settings_module.get_settings()

    assert settings.api_key == "env_api_key_no_gsm"
    mock_gsm_client_instance.get_secret.assert_not_called()


def test_settings_missing_required_secrets_raises_error(monkeypatch):
    # GCP_PROJECT_ID is cleared by autouse fixture
    # API_KEY, ELEVENLABS_API_KEY, JWT_SECRET_KEY are also cleared.
    importlib.reload(settings_module)
    settings_module.get_settings.cache_clear()
    with pytest.raises(ValueError, match="Failed to load application settings"):
        settings_module.get_settings()


def test_get_settings_lru_cache(monkeypatch):
    # Set required env vars to avoid validation errors during Settings instantiation
    monkeypatch.setenv("API_KEY", "testkey1_lru")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "testkey2_lru")
    monkeypatch.setenv("JWT_SECRET_KEY", "testkey3_lru_testkey3_lru_testkey3_lru")

    importlib.reload(settings_module)  # Reload to ensure clean state for Settings class
    settings_module.get_settings.cache_clear()  # Clear cache before first call

    # Patch the Settings class itself to count instantiations
    with patch.object(
        settings_module, "Settings", wraps=settings_module.Settings
    ) as mock_settings_class:
        settings1 = settings_module.get_settings()
        settings2 = settings_module.get_settings()

        assert settings1 is settings2
        mock_settings_class.assert_called_once()  # Settings() should only be called once

        # Verify that changing env var doesn't affect cached settings
        monkeypatch.setenv("API_KEY", "newkey_after_cache_lru")
        settings3 = settings_module.get_settings()
        assert settings3.api_key == "testkey1_lru"  # Still old value from cache

        # Clear cache and get again
        settings_module.get_settings.cache_clear()
        # Need to reload the module if Settings class itself caches _secrets_client or similar
        # or if Pydantic's BaseSettings does internal caching related to env var reads.
        # For pydantic-settings, it reads env vars upon instantiation.
        # The lru_cache on get_settings() prevents re-instantiation.
        # To test re-reading env vars, we must clear the lru_cache.

        # Reset call count for the new instantiation after cache clear
        mock_settings_class.reset_mock()
        settings4 = settings_module.get_settings()
        assert settings4.api_key == "newkey_after_cache_lru"
        mock_settings_class.assert_called_once()  # Called again after cache clear


def test_default_settings(settings):
    """Test default settings values."""
    assert settings.gemini_model_name == "models/gemini-2.5-flash-preview-05-20"


def test_environment_override(monkeypatch):
    """Test environment variable override."""
    monkeypatch.setenv("GEMINI_MODEL_NAME", "models/gemini-1.0-pro-001")
    settings = settings_module.Settings()
    assert settings.gemini_model_name == "models/gemini-1.0-pro-001"
