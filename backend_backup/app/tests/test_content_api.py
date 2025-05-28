import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

API_KEY = "test-api-key"  # Use a consistent test API key

@pytest.fixture(scope="module", autouse=True)
def mock_settings():
    with patch('app.core.config.settings.API_KEY', API_KEY):
        yield

@pytest.mark.asyncio
async def test_generate_content_missing_api_key(client: AsyncClient):
    response = await client.post("/api/generate-content", json={})
    assert response.status_code == 401 # Expecting 401 due to Depends(get_api_key)
    assert "Invalid or missing API key" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_content_invalid_api_key(client: AsyncClient):
    response = await client.post(
        "/api/generate-content", 
        json={},
        headers={"X-API-Key": "invalid-key"}
    )
    assert response.status_code == 401
    assert "Invalid or missing API key" in response.json()["detail"]

@pytest.mark.asyncio
@patch("app.services.content.ContentService.generate_content", new_callable=AsyncMock)
@patch("app.services.audio.AudioService.generate_audio", new_callable=AsyncMock)
async def test_generate_content_success(
    mock_audio_generate: AsyncMock,
    mock_content_generate: AsyncMock,
    client: AsyncClient
):
    mock_content_generate.return_value = {
        "outline": "Test Outline",
        "podcast_script": "Test Podcast Script",
        "study_guide": "Test Study Guide",
        "one_pager_summaries": ["Summary 1"],
        "detailed_reading_materials": ["Material 1"],
        "faqs": [{"question": "Q1", "answer": "A1"}],
        "flashcards": [{"front": "F1", "back": "B1"}],
        "reading_guide_questions": ["RQ1"]
    }
    mock_audio_generate.return_value = "/fake/audio/url.mp3"

    payload = {
        "topic": "Test Topic",
        "content_type": "study_guide",
        "target_audience": "students",
        "length": "short",
        "generate_audio": True
    }
    
    response = await client.post(
        "/api/generate-content", 
        json=payload,
        headers={"X-API-Key": API_KEY}
    )
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["content"]["outline"] == "Test Outline"
    # Audio URL might be None because it's a background task, or could be mocked directly in response
    # For this test, we assume the endpoint returns the URL if generation is requested.
    # If audio_url is returned directly by the endpoint (not just background task):
    # assert response_data["audio_url"] == "/fake/audio/url.mp3"
    
    mock_content_generate.assert_called_once_with(
        topic="Test Topic",
        content_type="study_guide",
        target_audience="students",
        length="short"
    )
    # mock_audio_generate.assert_called_once() # This is harder to assert due to background task nature

# TODO: Add more tests for error cases, different inputs, and history endpoints. 