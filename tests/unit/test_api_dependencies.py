from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException, status
from jose import JWTError

from app.api.deps import get_api_key, get_current_active_user, get_current_user
from app.core.config.settings import Settings
from app.models.pydantic.user import TokenData
from app.models.pydantic.user import User as UserResponse

# --- Fixtures ---


@pytest.fixture
def mock_settings_for_deps():
    return Settings(
        api_key="test_key",
        jwt_secret_key="test_jwt_secret_that_is_32_chars_long_minimum_for_validation_purposes",
        jwt_algorithm="HS256",
        # Add other necessary settings
        gcp_project_id="test-project",
        gcp_location="us-central1",
        gemini_model_name="models/gemini-2.5-flash-preview-05-20",
    )


# --- Tests for get_api_key ---


@pytest.mark.asyncio
async def test_get_api_key_valid(test_settings):
    with patch("app.api.deps.get_settings", return_value=test_settings):
        # Simulate FastAPI calling the dependency with the header value
        validated_key = await get_api_key(api_key="test_key")
        assert validated_key == "test_key"


@pytest.mark.asyncio
async def test_get_api_key_invalid(test_settings):
    with patch("app.api.deps.get_settings", return_value=test_settings):
        with pytest.raises(HTTPException) as exc_info:
            await get_api_key(api_key="invalid_key")
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid or missing API key" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_api_key_missing(test_settings):
    with patch("app.api.deps.get_settings", return_value=test_settings):
        with pytest.raises(HTTPException) as exc_info:
            await get_api_key(api_key=None)  # Simulate missing header
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid or missing API key" in exc_info.value.detail


# --- Tests for get_current_user ---


@pytest.mark.asyncio
async def test_get_current_user_valid_token(test_settings):
    test_username = "testuser@example.com"
    token_payload = {"sub": test_username}
    # This token is not actually signed with the key, but decode is mocked
    mock_token = "mock_jwt_token"

    with patch("app.api.deps.get_settings", return_value=test_settings):
        with patch(
            "app.api.deps.jwt.decode", return_value=token_payload
        ) as mock_jwt_decode:
            token_data = await get_current_user(token=mock_token)
            assert token_data.username == test_username
            mock_jwt_decode.assert_called_once_with(
                mock_token,
                test_settings.jwt_secret_key,
                algorithms=[test_settings.jwt_algorithm],
            )


@pytest.mark.asyncio
async def test_get_current_user_invalid_token_jwt_error(test_settings):
    mock_token = "invalid_jwt_token"
    with patch("app.api.deps.get_settings", return_value=test_settings):
        with patch(
            "app.api.deps.jwt.decode", side_effect=JWTError("Invalid token")
        ) as mock_jwt_decode:
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token=mock_token)
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Could not validate credentials" in exc_info.value.detail
            mock_jwt_decode.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_user_missing_username_in_payload(test_settings):
    token_payload_no_sub = {"id": "123"}  # Missing 'sub'
    mock_token = "mock_jwt_token_no_sub"
    with patch("app.api.deps.get_settings", return_value=test_settings):
        with patch("app.api.deps.jwt.decode", return_value=token_payload_no_sub):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token=mock_token)
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Could not validate credentials" in exc_info.value.detail


# --- Tests for get_current_active_user ---


@pytest.mark.asyncio
async def test_get_current_active_user_success(test_settings):
    test_username = "activeuser@example.com"
    mock_token_data = TokenData(username=test_username)

    # Firestore document for the user
    mock_user_doc = {
        "email": test_username,
        "full_name": "Active User",
        "is_active": True,
        "hashed_password": "mock_hashed_password_for_test",  # Required by model validation
    }

    # Mock get_current_user to return our TokenData
    mock_get_current_user_dep = AsyncMock(return_value=mock_token_data)

    with patch("app.api.deps.get_settings", return_value=test_settings):
        with patch(
            "app.api.deps.get_document_from_firestore",
            AsyncMock(return_value=mock_user_doc),
        ) as mock_get_doc:
            # We need to provide the dependency result directly to get_current_active_user
            active_user = await get_current_active_user(
                current_user_token_data=mock_token_data
            )

            assert isinstance(active_user, UserResponse)
            assert active_user.email == test_username
            assert active_user.full_name == "Active User"
            # If UserResponse has an 'id' field and it's mapped from email:
            assert active_user.id == test_username

            mock_get_doc.assert_called_once_with(test_username, collection_name="users")


@pytest.mark.asyncio
async def test_get_current_active_user_not_found(test_settings):
    test_username = "nonexistentuser@example.com"
    mock_token_data = TokenData(username=test_username)

    with patch("app.api.deps.get_settings", return_value=test_settings):
        with patch(
            "app.api.deps.get_document_from_firestore", AsyncMock(return_value=None)
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_active_user(current_user_token_data=mock_token_data)
            assert exc_info.value.status_code == 404
            assert "User not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_active_user_pydantic_error(test_settings):
    test_username = "malformeduser@example.com"
    mock_token_data = TokenData(username=test_username)

    # Firestore document missing a required field for UserResponse (e.g., email)
    mock_user_doc_malformed = {
        "full_name": "Malformed User",
        # "email": test_username, # Missing email
    }

    with patch("app.api.deps.get_settings", return_value=test_settings):
        with patch(
            "app.api.deps.get_document_from_firestore",
            AsyncMock(return_value=mock_user_doc_malformed),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_active_user(current_user_token_data=mock_token_data)
            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Error processing user data" in exc_info.value.detail


# Example of how to test a dependency that itself has dependencies,
# though get_current_active_user takes its dependency as an argument.
# If it were a sub-dependency called via Depends(), you'd mock it like this:
# @patch('app.api.deps.get_current_user', new_callable=AsyncMock)
# async def test_get_current_active_user_with_mocked_sub_dependency(mock_get_current_user_dep, ...):
#     mock_get_current_user_dep.return_value = TokenData(username="test@example.com")
#     # ... rest of the test for get_current_active_user
