"""Tests for LLM timeout handling fix."""

import asyncio
import time
from unittest.mock import MagicMock, Mock, patch

import pytest
from vertexai.generative_models import GenerativeModel

from app.core.config.settings import Settings
from app.core.exceptions.custom_exceptions import ExternalServiceError
from app.services.llm_client import LLMClientService
from app.services.simple_llm_client import SimpleLLMClient


class TestLLMTimeoutHandling:
    """Test timeout handling in LLM clients."""

    @pytest.fixture
    def settings(self):
        """Create test settings."""
        settings = MagicMock(spec=Settings)
        settings.gcp_project_id = "test-project"
        settings.gcp_location = "us-central1"
        settings.gemini_model_name = "gemini-1.5-flash"
        settings.max_retries = 2
        settings.retry_delay = 0.1
        settings.enable_cost_tracking = False
        settings.llm_timeout_seconds = 30  # 30 second timeout
        return settings

    @pytest.fixture
    def mock_vertexai_init(self):
        """Mock vertexai initialization."""
        with patch("app.services.llm_client.vertexai.init") as mock:
            yield mock

    @pytest.fixture
    def mock_generative_model(self):
        """Mock GenerativeModel."""
        with patch("app.services.llm_client.GenerativeModel") as mock:
            yield mock

    def test_llm_client_timeout_handling(self, settings, mock_vertexai_init, mock_generative_model):
        """Test that LLMClientService handles timeouts properly."""
        # Create mock model that simulates timeout
        mock_model = MagicMock()
        
        def slow_generate_content(*args, **kwargs):
            """Simulate a slow API call that would timeout."""
            time.sleep(2)  # Sleep for 2 seconds
            response = MagicMock()
            response.text = '{"test": "data"}'
            response.usage_metadata = MagicMock(
                prompt_token_count=10,
                candidates_token_count=20
            )
            return response
        
        mock_model.generate_content = slow_generate_content
        mock_generative_model.return_value = mock_model
        
        # Initialize client with short timeout
        settings.llm_timeout_seconds = 1  # 1 second timeout
        client = LLMClientService(settings)
        
        # Mock the model class for validation
        mock_model_cls = MagicMock()
        mock_model_cls.__name__ = "TestModel"
        
        # Should timeout and return None
        with patch("app.services.llm_client.time.time", side_effect=time.time):
            result, tokens = client.call_generative_model(
                prompt_str="Test prompt",
                pydantic_model_cls=mock_model_cls,
                content_type_name="test_content",
                max_retries=0  # No retries for this test
            )
        
        # Verify timeout handling
        assert result is None
        assert tokens["input_tokens"] == 0
        assert tokens["output_tokens"] == 0

    def test_llm_client_successful_within_timeout(self, settings, mock_vertexai_init, mock_generative_model):
        """Test successful completion within timeout."""
        # Create mock model that responds quickly
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"test": "data"}'
        mock_response.usage_metadata = MagicMock(
            prompt_token_count=10,
            candidates_token_count=20
        )
        mock_model.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model
        
        # Initialize client
        client = LLMClientService(settings)
        
        # Mock the model class for validation
        mock_model_cls = MagicMock()
        mock_model_cls.__name__ = "TestModel"
        mock_instance = MagicMock()
        mock_model_cls.return_value = mock_instance
        
        # Should complete successfully
        result, tokens = client.call_generative_model(
            prompt_str="Test prompt",
            pydantic_model_cls=mock_model_cls,
            content_type_name="test_content",
            max_retries=0
        )
        
        # Verify successful completion
        assert result == mock_instance
        assert tokens["input_tokens"] == 10
        assert tokens["output_tokens"] == 20

    def test_llm_client_retry_on_timeout(self, settings, mock_vertexai_init, mock_generative_model):
        """Test that client retries on timeout."""
        # Create mock model that times out first, then succeeds
        mock_model = MagicMock()
        call_count = 0
        
        def generate_with_timeout_then_success(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call times out
                time.sleep(2)
            # Second call succeeds
            response = MagicMock()
            response.text = '{"test": "data"}'
            response.usage_metadata = MagicMock(
                prompt_token_count=10,
                candidates_token_count=20
            )
            return response
        
        mock_model.generate_content = generate_with_timeout_then_success
        mock_generative_model.return_value = mock_model
        
        # Initialize client with short timeout
        settings.llm_timeout_seconds = 1
        client = LLMClientService(settings)
        
        # Mock the model class
        mock_model_cls = MagicMock()
        mock_model_cls.__name__ = "TestModel"
        mock_instance = MagicMock()
        mock_model_cls.return_value = mock_instance
        
        # Should retry and succeed
        result, tokens = client.call_generative_model(
            prompt_str="Test prompt",
            pydantic_model_cls=mock_model_cls,
            content_type_name="test_content",
            max_retries=1  # Allow one retry
        )
        
        # Verify retry succeeded
        assert result == mock_instance
        assert call_count == 2  # First timeout, second success

    @pytest.mark.asyncio
    async def test_simple_llm_client_timeout(self, settings):
        """Test SimpleLLMClient timeout handling."""
        with patch("app.services.simple_llm_client.vertexai.init"):
            with patch("app.services.simple_llm_client.GenerativeModel") as mock_model_cls:
                # Create mock model
                mock_model = MagicMock()
                
                async def slow_generate(*args, **kwargs):
                    """Simulate slow async operation."""
                    await asyncio.sleep(2)
                    response = MagicMock()
                    response.text = '{"test": "data"}'
                    response.usage_metadata = MagicMock(
                        prompt_token_count=10,
                        candidates_token_count=20
                    )
                    return response
                
                mock_model.generate_content = slow_generate
                mock_model_cls.return_value = mock_model
                
                # Initialize client with short timeout
                settings.llm_timeout_seconds = 1
                client = SimpleLLMClient(settings)
                
                # Should timeout and raise exception
                with pytest.raises(ExternalServiceError, match="timeout"):
                    await client._call_llm(
                        prompt="Test prompt",
                        model_cls=MagicMock,
                        content_type="test_content",
                        max_retries=0
                    )

    def test_timeout_configuration(self, settings, mock_vertexai_init, mock_generative_model):
        """Test that timeout is configurable."""
        mock_model = MagicMock()
        mock_generative_model.return_value = mock_model
        
        # Test default timeout
        client = LLMClientService(settings)
        assert hasattr(client, 'timeout_seconds')
        assert client.timeout_seconds == 30
        
        # Test custom timeout
        settings.llm_timeout_seconds = 60
        client = LLMClientService(settings)
        assert client.timeout_seconds == 60
        
        # Test missing timeout setting defaults to reasonable value
        delattr(settings, 'llm_timeout_seconds')
        client = LLMClientService(settings)
        assert client.timeout_seconds == 120  # Default 2 minutes

    def test_timeout_logging(self, settings, mock_vertexai_init, mock_generative_model, caplog):
        """Test that timeouts are properly logged."""
        # Create mock model that times out
        mock_model = MagicMock()
        
        def timeout_generate(*args, **kwargs):
            time.sleep(2)
            
        mock_model.generate_content = timeout_generate
        mock_generative_model.return_value = mock_model
        
        # Initialize client
        settings.llm_timeout_seconds = 1
        client = LLMClientService(settings)
        
        # Call with timeout
        result, _ = client.call_generative_model(
            prompt_str="Test prompt",
            pydantic_model_cls=MagicMock,
            content_type_name="test_content",
            max_retries=0
        )
        
        # Check logs
        assert "timeout" in caplog.text.lower()
        assert "test_content" in caplog.text
        assert result is None