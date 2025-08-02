"""
Test Authentication System - TDD First!
Task: API-003 - Implement simple authentication
"""

import pytest
from fastapi.testclient import TestClient


def test_api_key_storage_exists():
    """Test that API key storage system exists."""
    from src.auth import ApiKeyStore

    store = ApiKeyStore()
    assert store is not None


def test_api_key_generation():
    """Test API key generation creates valid keys."""
    from src.auth import ApiKeyStore

    store = ApiKeyStore()

    # Generate a key
    key = store.generate_key(name="test-user")

    # Should be string, non-empty, reasonable length
    assert isinstance(key, str)
    assert len(key) >= 32  # At least 32 chars for security
    assert key.startswith("lf_")  # La Factoria prefix


def test_api_key_validation():
    """Test API key validation against stored keys."""
    from src.auth import ApiKeyStore

    store = ApiKeyStore()

    # Generate a valid key
    valid_key = store.generate_key(name="test-user")

    # Valid key should be accepted
    assert store.is_valid(valid_key) is True

    # Invalid key should be rejected
    assert store.is_valid("invalid-key") is False
    assert store.is_valid("lf_fakekeythatdoesnotexist") is False


def test_api_key_storage_persistence():
    """Test that API keys persist across store instances."""
    from src.auth import ApiKeyStore

    # Generate key in first store
    store1 = ApiKeyStore()
    key = store1.generate_key(name="persistent-user")
    assert store1.is_valid(key) is True

    # Create new store and verify key still works
    store2 = ApiKeyStore()
    assert store2.is_valid(key) is True


def test_api_key_info_retrieval():
    """Test retrieving information about an API key."""
    from src.auth import ApiKeyStore

    store = ApiKeyStore()
    key = store.generate_key(name="info-test-user")

    info = store.get_key_info(key)
    assert info is not None
    assert info["name"] == "info-test-user"
    assert "created_at" in info
    assert "last_used" in info


def test_api_key_usage_tracking():
    """Test that API key usage is tracked."""
    from src.auth import ApiKeyStore

    store = ApiKeyStore()
    key = store.generate_key(name="usage-test")

    # Initial usage should be None
    info = store.get_key_info(key)
    assert info["last_used"] is None

    # Record usage
    store.record_usage(key)

    # Usage should be updated
    info = store.get_key_info(key)
    assert info["last_used"] is not None


def test_api_key_deletion():
    """Test API key deletion/revocation."""
    from src.auth import ApiKeyStore

    store = ApiKeyStore()
    key = store.generate_key(name="delete-test")

    # Key should be valid initially
    assert store.is_valid(key) is True

    # Delete the key
    store.delete_key(key)

    # Key should no longer be valid
    assert store.is_valid(key) is False


def test_authentication_endpoint_with_new_system():
    """Test that main app uses new authentication system."""
    from src.main import app

    client = TestClient(app)

    # Invalid key should still be rejected
    response = client.post("/api/generate", json={"topic": "Test topic for auth"}, headers={"X-API-Key": "invalid-key"})
    assert response.status_code == 401

    # Old test keys should no longer work
    response = client.post(
        "/api/generate", json={"topic": "Test topic for auth"}, headers={"X-API-Key": "test-key-123"}
    )
    assert response.status_code == 401


def test_authentication_with_valid_generated_key():
    """Test that generated keys work with endpoints."""
    from src.auth import get_key_store
    from src.main import app

    # Use the global key store to ensure consistency
    store = get_key_store()
    valid_key = store.generate_key(name="endpoint-test")

    client = TestClient(app)

    # Should work with generated key
    response = client.post(
        "/api/generate", json={"topic": "Test topic with valid key"}, headers={"X-API-Key": valid_key}
    )
    assert response.status_code == 200


def test_multiple_keys_per_user():
    """Test that multiple keys can be generated for same user."""
    from src.auth import ApiKeyStore

    store = ApiKeyStore()

    key1 = store.generate_key(name="multi-key-user")
    key2 = store.generate_key(name="multi-key-user")

    # Keys should be different
    assert key1 != key2

    # Both should be valid
    assert store.is_valid(key1) is True
    assert store.is_valid(key2) is True


def test_list_keys_functionality():
    """Test listing all keys for management."""
    from src.auth import ApiKeyStore

    store = ApiKeyStore()

    # Start fresh
    initial_count = len(store.list_keys())

    # Generate some keys
    key1 = store.generate_key(name="list-test-1")
    key2 = store.generate_key(name="list-test-2")

    keys = store.list_keys()
    assert len(keys) == initial_count + 2

    # Should contain our keys
    key_ids = [k["key_id"] for k in keys]
    assert any(key1.split("_")[1] in k_id for k_id in key_ids)
    assert any(key2.split("_")[1] in k_id for k_id in key_ids)
