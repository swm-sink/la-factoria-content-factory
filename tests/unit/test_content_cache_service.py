import time
from datetime import datetime, timedelta
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from app.core.config.settings import Settings
from app.models.pydantic.content import (
    ContentMetadata,
    ContentOutline,
    GeneratedContent,
    QualityMetrics,
)
from app.services.content_cache import CacheEntry, ContentCacheService

# --- Fixtures ---


@pytest.fixture
def mock_settings(test_settings):
    return test_settings


@pytest.fixture
def mock_settings_for_cache(test_settings):
    """Cache-specific test settings based on shared settings"""
    return test_settings.model_copy(
        update={
            "cache_min_quality_retrieval": 0.7,
            "cache_min_quality_storage": 0.6,
            "cache_ttl_seconds": 3600,
            "cache_max_size": 3,
        }
    )


@pytest.fixture
def sample_content_outline() -> ContentOutline:
    return ContentOutline(
        title="Test Article",
        sections=[
            {"title": "Introduction", "content": "Test introduction"},
            {"title": "Main Section", "content": "Test main content"},
            {"title": "Conclusion", "content": "Test conclusion"},
        ],
        metadata={
            "target_audience": "Test audience",
            "tone": "Professional",
            "keywords": ["test", "article"],
        },
    )


@pytest.fixture
def sample_generated_content(test_settings) -> GeneratedContent:
    return GeneratedContent(
        content="Test generated content",
        metadata=ContentMetadata(
            ai_model_used=test_settings.gemini_model_name,
            generation_timestamp=datetime.utcnow(),
            processing_time_ms=100,
            token_count=50,
            quality_metrics=QualityMetrics(
                coherence_score=0.9, relevance_score=0.85, readability_score=0.8
            ),
        ),
    )


@pytest.fixture
def sample_content_metadata():
    return ContentMetadata(
        source_syllabus_length=100,
        target_format="comprehensive",
        duration_minutes=30,
        ai_model_used="test_model",
        total_tokens_consumed=500,
        generation_time_seconds=5.0,
        version="1.0",
    )


@pytest.fixture
def sample_quality_metrics_high():
    return QualityMetrics(
        overall_score=0.8,  # Above both storage and retrieval thresholds
        structure_score=0.8,
        coherence_score=0.8,
        relevance_score=0.8,
        educational_value_score=0.8,
        format_compliance_score=0.8,
        content_length_compliance=True,
        error_types_found=[],
        suggestions_for_improvement=[],
    )


@pytest.fixture
def sample_quality_metrics_medium():
    return QualityMetrics(
        overall_score=0.65,  # Below retrieval, above/equal storage
        structure_score=0.7,
        coherence_score=0.7,
        relevance_score=0.7,
        educational_value_score=0.7,
        format_compliance_score=0.7,
        content_length_compliance=True,
        error_types_found=[],
        suggestions_for_improvement=[],
    )


@pytest.fixture
def sample_quality_metrics_low():
    return QualityMetrics(
        overall_score=0.5,  # Below both storage and retrieval thresholds
        structure_score=0.5,
        coherence_score=0.5,
        relevance_score=0.5,
        educational_value_score=0.5,
        format_compliance_score=0.5,
        content_length_compliance=False,
        error_types_found=["Too short"],
        suggestions_for_improvement=["Make longer"],
    )


@pytest.fixture
def cache_service(mock_settings_for_cache):
    with patch(
        "app.services.content_cache.get_settings", return_value=mock_settings_for_cache
    ):
        service = ContentCacheService()
        service.clear()  # Ensure clean state for each test
        return service


# --- Test Cases ---


def test_generate_cache_key(cache_service: ContentCacheService):
    key1 = cache_service._generate_cache_key(
        "syllabus1", "format1", {"param": "value1"}
    )
    key2 = cache_service._generate_cache_key(
        "syllabus1", "format1", {"param": "value1"}
    )
    key3 = cache_service._generate_cache_key(
        "syllabus2", "format1", {"param": "value1"}
    )
    key4 = cache_service._generate_cache_key(
        "syllabus1", "format2", {"param": "value1"}
    )
    key5 = cache_service._generate_cache_key(
        "syllabus1", "format1", {"param": "value2"}
    )

    assert isinstance(key1, str)
    assert key1 == key2
    assert key1 != key3
    assert key1 != key4
    assert key1 != key5
    assert "syllabus1" in key1
    assert "format1" in key1
    assert "value1" in key1


def test_set_and_get_item_success(
    cache_service: ContentCacheService,
    sample_generated_content,
    sample_content_metadata,
    sample_quality_metrics_high,
):
    key_params = ("test_syllabus", "comprehensive", {"user_id": "user1"})
    cache_key = cache_service._generate_cache_key(*key_params)
    payload_to_set = (
        sample_generated_content,
        sample_content_metadata,
        sample_quality_metrics_high,
    )

    # Set item
    cache_service.set(cache_key, payload_to_set, sample_quality_metrics_high)

    # Get item
    retrieved_payload, retrieved_qm_dict = cache_service.get(cache_key)

    assert retrieved_payload is not None
    assert retrieved_qm_dict is not None
    assert retrieved_payload[0] == sample_generated_content
    assert retrieved_payload[1] == sample_content_metadata
    assert retrieved_payload[2] == sample_quality_metrics_high
    assert (
        retrieved_qm_dict["overall_score"] == sample_quality_metrics_high.overall_score
    )


def test_get_item_not_found(cache_service: ContentCacheService):
    cache_key = "non_existent_key"
    retrieved_data = cache_service.get(cache_key)
    assert retrieved_data is None


@patch("app.services.content_cache.time.time")
def test_get_item_expired(
    mock_time,
    cache_service: ContentCacheService,
    sample_generated_content,
    sample_content_metadata,
    sample_quality_metrics_high,
    mock_settings_for_cache,
):
    key_params = ("test_syllabus_expiry", "comprehensive", {})
    cache_key = cache_service._generate_cache_key(*key_params)
    payload_to_set = (
        sample_generated_content,
        sample_content_metadata,
        sample_quality_metrics_high,
    )

    # Set item at current time
    mock_time.return_value = 1000.0
    cache_service.set(cache_key, payload_to_set, sample_quality_metrics_high)

    # Try to get immediately - should be found
    retrieved_data, _ = cache_service.get(cache_key)
    assert retrieved_data is not None

    # Advance time past TTL
    mock_time.return_value = 1000.0 + mock_settings_for_cache.cache_ttl_seconds + 1

    # Try to get again - should be None (expired)
    retrieved_data_expired = cache_service.get(cache_key)
    assert retrieved_data_expired is None


def test_invalidate_item(
    cache_service: ContentCacheService,
    sample_generated_content,
    sample_content_metadata,
    sample_quality_metrics_high,
):
    key_params = ("test_syllabus_invalidate", "comprehensive", {})
    cache_key = cache_service._generate_cache_key(*key_params)
    payload_to_set = (
        sample_generated_content,
        sample_content_metadata,
        sample_quality_metrics_high,
    )

    cache_service.set(cache_key, payload_to_set, sample_quality_metrics_high)
    assert cache_service.get(cache_key) is not None  # Verify it's there

    cache_service.invalidate(cache_key)
    assert cache_service.get(cache_key) is None  # Verify it's gone


def test_clear_cache(
    cache_service: ContentCacheService,
    sample_generated_content,
    sample_content_metadata,
    sample_quality_metrics_high,
):
    key1_params = ("syllabus1", "format1", {})
    key1 = cache_service._generate_cache_key(*key1_params)
    payload1 = (
        sample_generated_content,
        sample_content_metadata,
        sample_quality_metrics_high,
    )

    key2_params = ("syllabus2", "format2", {})
    key2 = cache_service._generate_cache_key(*key2_params)
    # Create a slightly different QualityMetrics for the second item
    qm2 = sample_quality_metrics_high.model_copy(update={"overall_score": 0.85})
    payload2 = (sample_generated_content, sample_content_metadata, qm2)

    cache_service.set(key1, payload1, sample_quality_metrics_high)
    cache_service.set(key2, payload2, qm2)

    assert cache_service.get(key1) is not None
    assert cache_service.get(key2) is not None

    cache_service.clear()

    assert cache_service.get(key1) is None
    assert cache_service.get(key2) is None
    assert len(cache_service.cache) == 0


def test_lru_eviction(
    cache_service: ContentCacheService,
    sample_generated_content,
    sample_content_metadata,
    sample_quality_metrics_high,
):
    payload = (
        sample_generated_content,
        sample_content_metadata,
        sample_quality_metrics_high,
    )

    # Fill the cache (max_size = 3)
    key1 = cache_service._generate_cache_key("s1", "f1", {})
    cache_service.set(key1, payload, sample_quality_metrics_high)

    key2 = cache_service._generate_cache_key("s2", "f1", {})
    cache_service.set(key2, payload, sample_quality_metrics_high)

    key3 = cache_service._generate_cache_key("s3", "f1", {})
    cache_service.set(key3, payload, sample_quality_metrics_high)

    assert cache_service.get(key1) is not None
    assert cache_service.get(key2) is not None
    assert cache_service.get(key3) is not None
    assert len(cache_service.cache) == 3

    # Access key1 to make it most recently used
    cache_service.get(key1)

    # Add a 4th item - should evict key2 (least recently used after key1 access)
    key4 = cache_service._generate_cache_key("s4", "f1", {})
    cache_service.set(key4, payload, sample_quality_metrics_high)

    assert cache_service.get(key1) is not None  # Still there
    assert cache_service.get(key2) is None  # Evicted
    assert cache_service.get(key3) is not None  # Still there
    assert cache_service.get(key4) is not None  # Newly added


def test_quality_aware_storage_below_threshold(
    cache_service: ContentCacheService,
    sample_generated_content,
    sample_content_metadata,
    sample_quality_metrics_low,  # overall_score = 0.5
    mock_settings_for_cache,  # cache_min_quality_storage = 0.6
):
    key_params = ("test_syllabus_low_q_store", "comprehensive", {})
    cache_key = cache_service._generate_cache_key(*key_params)
    payload_to_set = (
        sample_generated_content,
        sample_content_metadata,
        sample_quality_metrics_low,
    )

    cache_service.set(cache_key, payload_to_set, sample_quality_metrics_low)

    # Item should NOT be stored
    assert cache_service.get(cache_key) is None
    assert len(cache_service.cache) == 0


def test_quality_aware_storage_above_threshold(
    cache_service: ContentCacheService,
    sample_generated_content,
    sample_content_metadata,
    sample_quality_metrics_medium,  # overall_score = 0.65
    mock_settings_for_cache,  # cache_min_quality_storage = 0.6
):
    key_params = ("test_syllabus_med_q_store", "comprehensive", {})
    cache_key = cache_service._generate_cache_key(*key_params)
    payload_to_set = (
        sample_generated_content,
        sample_content_metadata,
        sample_quality_metrics_medium,
    )

    cache_service.set(cache_key, payload_to_set, sample_quality_metrics_medium)

    # Item SHOULD be stored
    retrieved_payload, retrieved_qm_dict = cache_service.get(cache_key)
    assert retrieved_payload is not None
    assert (
        retrieved_qm_dict["overall_score"]
        == sample_quality_metrics_medium.overall_score
    )
    assert len(cache_service.cache) == 1


def test_quality_aware_retrieval_below_threshold(
    cache_service: ContentCacheService,
    sample_generated_content,
    sample_content_metadata,
    sample_quality_metrics_medium,  # overall_score = 0.65
    mock_settings_for_cache,  # cache_min_quality_retrieval = 0.7
):
    key_params = ("test_syllabus_med_q_retrieve", "comprehensive", {})
    cache_key = cache_service._generate_cache_key(*key_params)

    # Manually insert into cache bypassing the 'set' quality check for this test scenario
    # This simulates an item that was stored (e.g., storage threshold was lower)
    # but now retrieval threshold is higher.
    entry = CacheEntry(
        payload=(
            sample_generated_content,
            sample_content_metadata,
            sample_quality_metrics_medium,
        ),
        quality_metrics=sample_quality_metrics_medium.model_dump(),
        timestamp=time.time(),
        ttl=mock_settings_for_cache.cache_ttl_seconds,
    )
    cache_service.cache[cache_key] = entry
    assert len(cache_service.cache) == 1  # Ensure it's in the underlying cache

    # Attempt to get item
    retrieved_data = cache_service.get(cache_key)

    # Item should NOT be retrieved due to quality, even if not expired
    assert retrieved_data is None
    # The item should also be removed from cache upon failed quality retrieval
    assert cache_key not in cache_service.cache
    assert len(cache_service.cache) == 0


def test_quality_aware_retrieval_above_threshold(
    cache_service: ContentCacheService,
    sample_generated_content,
    sample_content_metadata,
    sample_quality_metrics_high,  # overall_score = 0.8
    mock_settings_for_cache,  # cache_min_quality_retrieval = 0.7
):
    key_params = ("test_syllabus_high_q_retrieve", "comprehensive", {})
    cache_key = cache_service._generate_cache_key(*key_params)
    payload_to_set = (
        sample_generated_content,
        sample_content_metadata,
        sample_quality_metrics_high,
    )

    cache_service.set(
        cache_key, payload_to_set, sample_quality_metrics_high
    )  # Stored as quality is high

    # Attempt to get item
    retrieved_payload, retrieved_qm_dict = cache_service.get(cache_key)

    # Item SHOULD be retrieved
    assert retrieved_payload is not None
    assert (
        retrieved_qm_dict["overall_score"] == sample_quality_metrics_high.overall_score
    )


@patch("app.services.content_cache.time.time")
def test_set_with_custom_ttl(
    mock_time,
    cache_service: ContentCacheService,
    sample_generated_content,
    sample_content_metadata,
    sample_quality_metrics_high,
    mock_settings_for_cache,
):
    key_params = ("test_syllabus_custom_ttl", "comprehensive", {})
    cache_key = cache_service._generate_cache_key(*key_params)
    payload_to_set = (
        sample_generated_content,
        sample_content_metadata,
        sample_quality_metrics_high,
    )
    custom_ttl = 10  # seconds

    # Set item at current time with custom TTL
    mock_time.return_value = 2000.0
    cache_service.set(
        cache_key, payload_to_set, sample_quality_metrics_high, ttl_seconds=custom_ttl
    )

    # Try to get immediately - should be found
    retrieved_data, _ = cache_service.get(cache_key)
    assert retrieved_data is not None

    # Advance time just before custom TTL expiry
    mock_time.return_value = 2000.0 + custom_ttl - 1
    retrieved_data, _ = cache_service.get(cache_key)
    assert retrieved_data is not None

    # Advance time past custom TTL
    mock_time.return_value = 2000.0 + custom_ttl + 1
    retrieved_data_expired = cache_service.get(cache_key)
    assert retrieved_data_expired is None

    # Verify it doesn't affect default TTL for other items
    key_default_ttl_params = ("test_syllabus_default_ttl", "comprehensive", {})
    key_default_ttl = cache_service._generate_cache_key(*key_default_ttl_params)

    mock_time.return_value = 2000.0  # Reset time for this set
    cache_service.set(
        key_default_ttl, payload_to_set, sample_quality_metrics_high
    )  # Uses default TTL

    # Advance time past custom_ttl but before default_ttl
    mock_time.return_value = 2000.0 + custom_ttl + 5
    assert mock_time.return_value < 2000.0 + mock_settings_for_cache.cache_ttl_seconds

    retrieved_default_ttl_data, _ = cache_service.get(key_default_ttl)
    assert retrieved_default_ttl_data is not None  # Should still be there


@pytest.mark.asyncio
async def test_cache_content_success(
    test_settings, sample_content_outline, sample_generated_content
):
    with patch(
        "app.services.content_cache_service.get_document_from_firestore",
        AsyncMock(return_value=None),
    ) as mock_get_doc:
        with patch(
            "app.services.content_cache_service.set_document_in_firestore", AsyncMock()
        ) as mock_set_doc:
            cache_service = ContentCacheService(settings=test_settings)
            await cache_service.cache_content(
                sample_content_outline, sample_generated_content
            )

            mock_get_doc.assert_called_once()
            mock_set_doc.assert_called_once()


@pytest.mark.asyncio
async def test_get_cached_content_success(
    test_settings, sample_content_outline, sample_generated_content
):
    cached_data = {
        "content": sample_generated_content.dict(),
        "timestamp": datetime.utcnow().isoformat(),
    }

    with patch(
        "app.services.content_cache_service.get_document_from_firestore",
        AsyncMock(return_value=cached_data),
    ) as mock_get_doc:
        cache_service = ContentCacheService(settings=test_settings)
        result = await cache_service.get_cached_content(sample_content_outline)

        assert result is not None
        assert isinstance(result, GeneratedContent)
        assert result.content == sample_generated_content.content
        mock_get_doc.assert_called_once()


@pytest.mark.asyncio
async def test_get_cached_content_not_found(test_settings, sample_content_outline):
    with patch(
        "app.services.content_cache_service.get_document_from_firestore",
        AsyncMock(return_value=None),
    ) as mock_get_doc:
        cache_service = ContentCacheService(settings=test_settings)
        result = await cache_service.get_cached_content(sample_content_outline)

        assert result is None
        mock_get_doc.assert_called_once()


@pytest.mark.asyncio
async def test_get_cached_content_expired(
    test_settings, sample_content_outline, sample_generated_content
):
    expired_timestamp = (datetime.utcnow() - timedelta(days=2)).isoformat()
    cached_data = {
        "content": sample_generated_content.dict(),
        "timestamp": expired_timestamp,
    }

    with patch(
        "app.services.content_cache_service.get_document_from_firestore",
        AsyncMock(return_value=cached_data),
    ) as mock_get_doc:
        cache_service = ContentCacheService(settings=test_settings)
        result = await cache_service.get_cached_content(sample_content_outline)

        assert result is None
        mock_get_doc.assert_called_once()


@pytest.mark.asyncio
async def test_clear_cache_success(test_settings):
    with patch(
        "app.services.content_cache_service.delete_document_from_firestore", AsyncMock()
    ) as mock_delete_doc:
        cache_service = ContentCacheService(settings=test_settings)
        await cache_service.clear_cache()

        mock_delete_doc.assert_called_once()


@pytest.mark.asyncio
async def test_cache_content_with_existing_content(
    test_settings, sample_content_outline, sample_generated_content
):
    existing_cached_data = {
        "content": sample_generated_content.dict(),
        "timestamp": datetime.utcnow().isoformat(),
    }

    with patch(
        "app.services.content_cache_service.get_document_from_firestore",
        AsyncMock(return_value=existing_cached_data),
    ) as mock_get_doc:
        with patch(
            "app.services.content_cache_service.set_document_in_firestore", AsyncMock()
        ) as mock_set_doc:
            cache_service = ContentCacheService(settings=test_settings)
            await cache_service.cache_content(
                sample_content_outline, sample_generated_content
            )

            mock_get_doc.assert_called_once()
            mock_set_doc.assert_called_once()
