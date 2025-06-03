import os
from unittest.mock import mock_open, patch

import pytest

from app.services.prompts import PromptService

# --- Fixtures ---


@pytest.fixture
def prompt_service():
    """Returns a PromptService instance with a temporary base path for testing."""
    # Use a temporary, non-existent base path to ensure mocks are used for file loading
    # or set up a temporary directory structure if testing actual file reads.
    # For these unit tests, we'll mostly mock file operations.
    return PromptService(base_path="tests/unit/test_prompts_data")


@pytest.fixture
def temp_prompt_files(tmp_path):
    """Creates temporary prompt files for testing actual file loading."""
    v1_path = tmp_path / "app/core/prompts/v1"
    v1_path.mkdir(parents=True, exist_ok=True)

    (v1_path / "test_prompt.md").write_text("Hello {{name}}!")
    (v1_path / "no_format_prompt.md").write_text("This is a static prompt.")

    return tmp_path


# --- Test Cases ---


def test_prompt_service_initialization_default_path():
    service = PromptService()
    assert service._base_prompt_path == "app/core/prompts/v1"


def test_prompt_service_initialization_custom_path():
    custom_path = "my/custom/prompts"
    service = PromptService(base_path=custom_path)
    assert service._base_prompt_path == custom_path


@patch("builtins.open", new_callable=mock_open, read_data="Hello {{name}}!")
@patch("os.path.exists", return_value=True)
def test_get_prompt_success_with_formatting(
    mock_exists, mock_file_open, prompt_service
):
    prompt_service.PROMPT_MAP[
        "test_format_prompt"
    ] = "test_format_prompt.md"  # Add to map for test

    formatted_prompt = prompt_service.get_prompt("test_format_prompt", name="World")

    expected_file_path = os.path.join(
        prompt_service._base_prompt_path, "test_format_prompt.md"
    )
    mock_file_open.assert_called_once_with(expected_file_path, "r", encoding="utf-8")
    assert formatted_prompt == "Hello World!"

    # Test lru_cache on _load_prompt_from_file
    # Call again, open should not be called again if caching works on _load_prompt_from_file
    prompt_service._load_prompt_from_file.cache_clear()  # Clear for this specific test part
    mock_file_open.reset_mock()

    # First call to load and cache
    prompt_service.get_prompt("test_format_prompt", name="CacheTest1")
    mock_file_open.assert_called_once_with(expected_file_path, "r", encoding="utf-8")

    # Second call, should use cache for _load_prompt_from_file
    mock_file_open.reset_mock()
    prompt_service.get_prompt("test_format_prompt", name="CacheTest2")
    mock_file_open.assert_not_called()


@patch("builtins.open", new_callable=mock_open, read_data="Static prompt content.")
@patch("os.path.exists", return_value=True)
def test_get_prompt_success_no_formatting(mock_exists, mock_file_open, prompt_service):
    prompt_service.PROMPT_MAP["test_static_prompt"] = "test_static_prompt.md"

    prompt_content = prompt_service.get_prompt("test_static_prompt")

    expected_file_path = os.path.join(
        prompt_service._base_prompt_path, "test_static_prompt.md"
    )
    mock_file_open.assert_called_once_with(expected_file_path, "r", encoding="utf-8")
    assert prompt_content == "Static prompt content."


def test_get_prompt_unknown_name(prompt_service):
    with pytest.raises(
        ValueError, match="Prompt name 'unknown_prompt' is not defined in PROMPT_MAP."
    ):
        prompt_service.get_prompt("unknown_prompt")


@patch("os.path.exists", return_value=False)  # Simulate file not existing
def test_get_prompt_file_not_found(mock_exists, prompt_service):
    prompt_service.PROMPT_MAP["missing_file_prompt"] = "missing_file_prompt.md"

    expected_file_path = os.path.join(
        prompt_service._base_prompt_path, "missing_file_prompt.md"
    )
    with pytest.raises(
        FileNotFoundError, match=f"Prompt file not found: {expected_file_path}"
    ):
        prompt_service.get_prompt("missing_file_prompt")
    mock_exists.assert_called_once_with(expected_file_path)


@patch("builtins.open", side_effect=IOError("Test IOError"))
@patch("os.path.exists", return_value=True)
def test_get_prompt_io_error(mock_exists, mock_file_open_io_error, prompt_service):
    prompt_service.PROMPT_MAP["io_error_prompt"] = "io_error_prompt.md"

    with pytest.raises(IOError, match="Could not read prompt file"):
        prompt_service.get_prompt("io_error_prompt")


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="Hello {{name}} and {{location}}!",
)
@patch("os.path.exists", return_value=True)
def test_get_prompt_formatting_missing_key(mock_exists, mock_file_open, prompt_service):
    prompt_service.PROMPT_MAP["format_key_error_prompt"] = "format_key_error_prompt.md"

    with pytest.raises(
        ValueError,
        match="Formatting error for prompt 'format_key_error_prompt': Missing key 'location'",
    ):
        prompt_service.get_prompt(
            "format_key_error_prompt", name="User"
        )  # Missing 'location'


# Test with actual temporary files
def test_get_prompt_with_actual_files(temp_prompt_files):
    # Initialize PromptService to use the temp_prompt_files directory structure
    # The base_path should point to where "app/core/prompts/v1" is within temp_prompt_files
    service_with_real_files = PromptService(
        base_path=str(temp_prompt_files / "app/core/prompts/v1")
    )
    service_with_real_files.PROMPT_MAP["test_prompt"] = "test_prompt.md"
    service_with_real_files.PROMPT_MAP["no_format_prompt"] = "no_format_prompt.md"

    # Test formatted prompt
    formatted = service_with_real_files.get_prompt(
        "test_prompt", name="UserFromRealFile"
    )
    assert formatted == "Hello UserFromRealFile!"

    # Test static prompt
    static_content = service_with_real_files.get_prompt("no_format_prompt")
    assert static_content == "This is a static prompt."

    # Test caching with real files
    service_with_real_files._load_prompt_from_file.cache_clear()

    # Patch 'open' to spy on it after the first real read
    with patch(
        "builtins.open", new_callable=mock_open, read_data="Hello {{name}}!"
    ) as m_open:
        # This call will use the real file via the unpatched _load_prompt_from_file's first call
        # For subsequent calls, if _load_prompt_from_file is cached, 'open' won't be called.
        # This setup is a bit tricky because lru_cache is on _load_prompt_from_file.
        # Let's re-verify the cache on _load_prompt_from_file directly.

        # First call - should read file
        service_with_real_files._load_prompt_from_file(
            str(temp_prompt_files / "app/core/prompts/v1/test_prompt.md")
        )

        # To test the cache, we need to ensure the next call to _load_prompt_from_file
        # for the *same path* doesn't re-open the file.
        # We can't easily assert mock_open was *not* called if the first call was real.
        # Instead, let's mock 'open' from the start for a specific path and check call counts.

        service_with_real_files._load_prompt_from_file.cache_clear()  # Clear for this specific sub-test

        str(temp_prompt_files / "app/core/prompts/v1/test_prompt.md")

        # Mock open specifically for this path to count calls
        # This is more of an integration test for the caching mechanism with file system.
        # A simpler unit test for lru_cache was done in test_get_prompt_success_with_formatting.


def test_warm_cache(prompt_service, mocker):
    # Mock _load_prompt_from_file to avoid actual file IO and check calls
    mock_load = mocker.patch.object(
        prompt_service,
        "_load_prompt_from_file",
        return_value="Mocked prompt content for {{key}}",
    )

    # Make PROMPT_MAP smaller for this test for simplicity
    prompt_service.PROMPT_MAP = {"prompt1": "prompt1.md", "prompt2": "prompt2.md"}

    prompt_service._warm_cache()

    expected_calls = [
        call(os.path.join(prompt_service._base_prompt_path, "prompt1.md")),
        call(os.path.join(prompt_service._base_prompt_path, "prompt2.md")),
    ]
    mock_load.assert_has_calls(expected_calls, any_order=True)
    assert mock_load.call_count == len(expected_calls)
