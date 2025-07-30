#!/usr/bin/env python3
"""Validate that LLM timeout handling is working correctly."""

import asyncio
import sys
import time
from unittest.mock import MagicMock, patch

from app.core.config.settings import Settings
from app.services.llm_client import LLMClientService
from app.services.simple_llm_client import SimpleLLMClient


def test_llm_client_timeout():
    """Test LLMClientService timeout handling."""
    print("Testing LLMClientService timeout handling...")
    
    # Create mock settings
    settings = MagicMock(spec=Settings)
    settings.gcp_project_id = "test-project"
    settings.gcp_location = "us-central1"
    settings.gemini_model_name = "gemini-1.5-flash"
    settings.max_retries = 1
    settings.retry_delay = 0.1
    settings.enable_cost_tracking = False
    settings.llm_timeout_seconds = 2  # 2 second timeout
    
    # Mock vertexai initialization
    with patch("app.services.llm_client.vertexai.init"):
        with patch("app.services.llm_client.GenerativeModel") as mock_model_cls:
            # Create mock model that simulates a slow response
            mock_model = MagicMock()
            
            def slow_generate_content(prompt):
                """Simulate slow API call."""
                print(f"  - Simulating slow API call (will sleep for 5 seconds)...")
                time.sleep(5)  # Sleep longer than timeout
                return MagicMock(text='{"test": "data"}')
            
            mock_model.generate_content = slow_generate_content
            mock_model_cls.return_value = mock_model
            
            # Initialize client
            client = LLMClientService(settings)
            
            # Verify timeout is set
            assert hasattr(client, 'timeout_seconds'), "Client missing timeout_seconds attribute"
            assert client.timeout_seconds == 2, f"Expected timeout=2, got {client.timeout_seconds}"
            print(f"  ✓ Timeout correctly set to {client.timeout_seconds} seconds")
            
            # Test timeout handling
            print("  - Calling LLM with timeout...")
            start_time = time.time()
            
            mock_model_cls_for_validation = MagicMock()
            mock_model_cls_for_validation.__name__ = "TestModel"
            
            result, tokens = client.call_generative_model(
                prompt_str="Test prompt",
                pydantic_model_cls=mock_model_cls_for_validation,
                content_type_name="test_content",
                max_retries=0  # No retries for this test
            )
            
            elapsed = time.time() - start_time
            
            # Verify timeout occurred
            assert result is None, "Expected None result due to timeout"
            assert elapsed < 3, f"Call should timeout in ~2s, took {elapsed:.1f}s"
            print(f"  ✓ Timeout handled correctly (elapsed: {elapsed:.1f}s)")
            
    print("✅ LLMClientService timeout handling: PASSED\n")
    return True


def test_simple_llm_client_timeout():
    """Test SimpleLLMClient timeout handling."""
    print("Testing SimpleLLMClient timeout handling...")
    
    # Create mock settings
    settings = MagicMock(spec=Settings)
    settings.gcp_project_id = "test-project"
    settings.gcp_location = "us-central1"
    settings.gemini_model_name = "gemini-1.5-flash"
    settings.llm_timeout_seconds = 2  # 2 second timeout
    
    # Mock vertexai initialization
    with patch("app.services.simple_llm_client.vertexai.init"):
        with patch("app.services.simple_llm_client.GenerativeModel") as mock_model_cls:
            # Create mock model
            mock_model = MagicMock()
            
            def slow_generate_content(prompt):
                """Simulate slow API call."""
                print(f"  - Simulating slow API call (will sleep for 5 seconds)...")
                time.sleep(5)  # Sleep longer than timeout
                return MagicMock(text='{"test": "data"}')
            
            mock_model.generate_content = slow_generate_content
            mock_model_cls.return_value = mock_model
            
            # Initialize client
            client = SimpleLLMClient(settings)
            
            # Verify timeout is set
            assert hasattr(client, 'timeout_seconds'), "Client missing timeout_seconds attribute"
            assert client.timeout_seconds == 2, f"Expected timeout=2, got {client.timeout_seconds}"
            print(f"  ✓ Timeout correctly set to {client.timeout_seconds} seconds")
            
    print("✅ SimpleLLMClient timeout handling: PASSED\n")
    return True


def test_timeout_configuration():
    """Test that timeout configuration works correctly."""
    print("Testing timeout configuration...")
    
    # Test with explicit timeout
    settings = MagicMock(spec=Settings)
    settings.llm_timeout_seconds = 60
    settings.gcp_project_id = "test"
    settings.gcp_location = "us"
    settings.gemini_model_name = "test-model"
    
    with patch("app.services.llm_client.vertexai.init"):
        with patch("app.services.llm_client.GenerativeModel"):
            client = LLMClientService(settings)
            assert client.timeout_seconds == 60
            print("  ✓ Custom timeout (60s) configured correctly")
    
    # Test with missing timeout (should use default)
    settings2 = MagicMock(spec=Settings)
    settings2.gcp_project_id = "test"
    settings2.gcp_location = "us"
    settings2.gemini_model_name = "test-model"
    # Don't set llm_timeout_seconds
    
    with patch("app.services.llm_client.vertexai.init"):
        with patch("app.services.llm_client.GenerativeModel"):
            client2 = LLMClientService(settings2)
            assert client2.timeout_seconds == 120  # Default
            print("  ✓ Default timeout (120s) used when not configured")
    
    print("✅ Timeout configuration: PASSED\n")
    return True


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("LLM Timeout Fix Validation")
    print("=" * 60)
    print()
    
    tests = [
        test_timeout_configuration,
        test_llm_client_timeout,
        test_simple_llm_client_timeout,
    ]
    
    all_passed = True
    for test_func in tests:
        try:
            passed = test_func()
            all_passed = all_passed and passed
        except Exception as e:
            print(f"❌ {test_func.__name__} FAILED: {e}")
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Timeout handling is working correctly!")
        print("\nNext steps:")
        print("1. Deploy to staging and test with real Gemini API")
        print("2. Monitor timeout metrics in production")
        print("3. Adjust timeout values based on actual response times")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Please fix the issues above")
        return 1


if __name__ == "__main__":
    sys.exit(main())