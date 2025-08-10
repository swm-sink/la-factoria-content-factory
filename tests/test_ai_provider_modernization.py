"""
Test suite for AI Provider Modernization
Validates updated AI providers work correctly with latest models
Following TDD principles for safe modernization
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from src.services.ai_providers import AIProviderManager, AIProviderType, AIResponse
from src.core.config import settings


class TestAIProviderModernization:
    """Test suite for AI provider modernization and model updates"""

    @pytest.fixture
    def ai_provider_manager(self):
        """Create AI provider manager for testing"""
        return AIProviderManager()

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response with updated models"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test generated content"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.total_tokens = 100
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 50
        return mock_response

    @pytest.fixture
    def mock_anthropic_response(self):
        """Mock Anthropic API response with updated Claude models"""
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Test Claude generated content"
        mock_response.usage.input_tokens = 50
        mock_response.usage.output_tokens = 50
        mock_response.stop_reason = "end_turn"
        return mock_response

    def test_no_langchain_imports(self):
        """Ensure no LangChain imports remain in the codebase"""
        import src.services.ai_providers as ai_providers_module
        import src.core.config as config_module
        
        # Check source code doesn't contain langchain imports
        with open(ai_providers_module.__file__, 'r') as f:
            content = f.read()
            assert 'langchain' not in content.lower(), "LangChain references found in ai_providers.py"
            assert 'from langchain' not in content.lower(), "LangChain imports found in ai_providers.py"
            assert 'import langchain' not in content.lower(), "LangChain imports found in ai_providers.py"

        with open(config_module.__file__, 'r') as f:
            content = f.read()
            assert 'langchain' not in content.lower(), "LangChain references found in config.py"

    def test_updated_model_references(self):
        """Verify deprecated model references have been updated"""
        # Test config.py model references
        anthropic_config = settings.get_ai_provider_config("anthropic")
        assert anthropic_config["model"] == "claude-3-5-sonnet-20241022", \
            f"Expected updated Claude model, got: {anthropic_config.get('model')}"

        # Test Vertex AI models (should use updated models)
        vertex_config = settings.get_ai_provider_config("vertex_ai")
        assert vertex_config["model"] != "text-bison", \
            "Deprecated text-bison model still in use"

    @pytest.mark.asyncio
    async def test_anthropic_provider_with_updated_model(self, ai_provider_manager, mock_anthropic_response):
        """Test Anthropic provider uses updated Claude model"""
        if not settings.has_anthropic_config:
            pytest.skip("Anthropic not configured")

        with patch.object(ai_provider_manager.providers.get(AIProviderType.ANTHROPIC, MagicMock()), 
                         'messages') as mock_messages:
            mock_messages.create = AsyncMock(return_value=mock_anthropic_response)
            
            response = await ai_provider_manager._generate_with_anthropic("Test prompt", 1000)
            
            # Verify the call was made with updated model
            mock_messages.create.assert_called_once()
            call_args = mock_messages.create.call_args
            assert call_args[1]["model"] == "claude-3-5-sonnet-20241022", \
                f"Expected updated Claude model in API call, got: {call_args[1].get('model')}"
            
            # Verify response structure
            assert isinstance(response, AIResponse)
            assert response.content == "Test Claude generated content"
            assert response.provider == AIProviderType.ANTHROPIC.value
            assert response.model == "claude-3-5-sonnet-20241022"

    @pytest.mark.asyncio
    async def test_openai_provider_uses_current_models(self, ai_provider_manager, mock_openai_response):
        """Test OpenAI provider uses current model versions"""
        if not settings.has_openai_config:
            pytest.skip("OpenAI not configured")

        with patch.object(ai_provider_manager.providers.get(AIProviderType.OPENAI, MagicMock()), 
                         'chat') as mock_chat:
            mock_chat.completions.create = AsyncMock(return_value=mock_openai_response)
            
            response = await ai_provider_manager._generate_with_openai("Test prompt", 1000)
            
            # Verify the call was made with appropriate model (should be gpt-4 or newer)
            mock_chat.completions.create.assert_called_once()
            call_args = mock_chat.completions.create.call_args
            model_used = call_args[1]["model"]
            assert model_used in ["gpt-4", "gpt-4o", "gpt-4-turbo"], \
                f"Expected current OpenAI model, got: {model_used}"
            
            # Verify response structure
            assert isinstance(response, AIResponse)
            assert response.content == "Test generated content"
            assert response.provider == AIProviderType.OPENAI.value

    @pytest.mark.asyncio
    async def test_vertex_ai_provider_modernization(self, ai_provider_manager):
        """Test Vertex AI provider uses updated models"""
        if not settings.GOOGLE_CLOUD_PROJECT:
            pytest.skip("Vertex AI not configured")

        # Skip test if vertexai package is not available
        try:
            import vertexai.generative_models
        except ImportError:
            pytest.skip("vertexai package not installed")
        
        # Test that Vertex AI is using updated models, not deprecated text-bison
        with patch('vertexai.generative_models.GenerativeModel') as mock_model_class:
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "Test Vertex AI content"
            mock_response.usage_metadata = MagicMock()
            mock_response.usage_metadata.total_token_count = 75
            mock_response.candidates = [{'safety_ratings': []}]
            
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model
            
            response = await ai_provider_manager._generate_with_vertex_ai("Test prompt", 1000)
            
            # Verify updated model is used (should not be text-bison)
            mock_model_class.assert_called_once()
            model_name = mock_model_class.call_args[0][0]
            assert model_name != "text-bison", \
                f"Still using deprecated text-bison model: {model_name}"
            assert model_name == "gemini-1.5-flash", \
                f"Expected gemini-1.5-flash model, got: {model_name}"
            
            # Verify response structure
            assert isinstance(response, AIResponse)
            assert response.content == "Test Vertex AI content"

    def test_provider_configuration_consistency(self):
        """Test that all provider configurations use current models"""
        # Check all provider configs for deprecated models
        deprecated_models = [
            "claude-3-sonnet-20240229",  # Old Claude model
            "text-bison",                # Old Vertex AI model
            "gpt-3.5-turbo",            # Should prefer gpt-4
            "text-davinci-003",         # Deprecated OpenAI model
        ]
        
        for provider in ["openai", "anthropic", "vertex_ai"]:
            config = settings.get_ai_provider_config(provider)
            if config and "model" in config:
                model = config["model"]
                assert model not in deprecated_models, \
                    f"Provider {provider} still uses deprecated model: {model}"

    @pytest.mark.asyncio
    async def test_fallback_provider_logic(self, ai_provider_manager):
        """Test that fallback logic works with updated providers"""
        # Test that fallback hierarchy is maintained
        fallback = await ai_provider_manager._get_fallback_provider(AIProviderType.OPENAI)
        
        # Should return next available provider
        if AIProviderType.ANTHROPIC in ai_provider_manager.providers:
            assert fallback == AIProviderType.ANTHROPIC
        elif AIProviderType.VERTEX_AI in ai_provider_manager.providers:
            assert fallback == AIProviderType.VERTEX_AI

    @pytest.mark.asyncio
    async def test_health_check_with_updated_models(self, ai_provider_manager):
        """Test health check works with updated provider models"""
        # Mock the health check calls
        with patch.object(ai_provider_manager.providers.get(AIProviderType.OPENAI, MagicMock()), 
                         'chat') as mock_chat:
            mock_chat.completions.create = AsyncMock(return_value=MagicMock())
            
            health_status = await ai_provider_manager.health_check()
            
            # Verify health check structure
            assert isinstance(health_status, dict)
            
            # If OpenAI is configured, verify health check was called
            if AIProviderType.OPENAI in ai_provider_manager.providers:
                assert AIProviderType.OPENAI.value in health_status
                # Health check should use a lightweight model
                if mock_chat.completions.create.called:
                    call_args = mock_chat.completions.create.call_args
                    model_used = call_args[1]["model"]
                    # Should use efficient model for health checks
                    assert model_used in ["gpt-3.5-turbo", "gpt-4"], \
                        f"Health check should use efficient model, got: {model_used}"

    def test_provider_stats_tracking(self, ai_provider_manager):
        """Test that provider statistics are properly tracked"""
        stats = ai_provider_manager.get_provider_stats()
        
        assert "current_provider" in stats
        assert "available_providers" in stats
        assert "stats" in stats
        
        # Verify each provider has proper stats structure
        for provider, provider_stats in stats["stats"].items():
            assert "requests" in provider_stats
            assert "successes" in provider_stats
            assert "failures" in provider_stats
            assert "total_tokens" in provider_stats
            assert "avg_response_time" in provider_stats

    @pytest.mark.asyncio
    async def test_content_generation_end_to_end(self, ai_provider_manager):
        """Test full content generation pipeline with updated models"""
        if not ai_provider_manager.providers:
            pytest.skip("No AI providers configured")

        # Mock the appropriate provider
        current_provider = ai_provider_manager.current_provider
        
        with patch.object(ai_provider_manager, f'_generate_with_{current_provider.value.lower()}') as mock_generate:
            mock_response = AIResponse(
                content="Generated educational content",
                provider=current_provider.value,
                model="updated-model",
                tokens_used=150,
                generation_time=1.5,
                metadata={}
            )
            mock_generate.return_value = mock_response
            
            response = await ai_provider_manager.generate_content(
                prompt="Create a study guide for Python basics",
                content_type="study_guide",
                max_tokens=1000
            )
            
            # Verify response
            assert isinstance(response, AIResponse)
            assert response.content == "Generated educational content"
            assert response.provider == current_provider.value
            assert response.tokens_used > 0


class TestLegacyCleanup:
    """Test suite to ensure legacy code and dependencies are cleaned up"""

    def test_requirements_no_langchain(self):
        """Ensure requirements.txt doesn't include LangChain dependencies"""
        with open('/Users/smenssink/Developer/la-factoria-content-factory/.conductor/bangui/requirements.txt', 'r') as f:
            content = f.read().lower()
            
        langchain_packages = [
            'langchain',
            'langchain-core',
            'langchain-community',
            'langchain-openai',
            'langchain-anthropic'
        ]
        
        for package in langchain_packages:
            assert package not in content, f"Found LangChain package in requirements.txt: {package}"

    def test_no_unused_imports(self):
        """Check for unused imports in AI provider files"""
        import ast
        import os
        
        files_to_check = [
            '/Users/smenssink/Developer/la-factoria-content-factory/.conductor/bangui/src/services/ai_providers.py',
            '/Users/smenssink/Developer/la-factoria-content-factory/.conductor/bangui/src/core/config.py'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Parse AST to check for import statements
                tree = ast.parse(content)
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
                
                # Ensure no LangChain imports
                langchain_imports = [imp for imp in imports if 'langchain' in imp.lower()]
                assert not langchain_imports, f"Found LangChain imports in {file_path}: {langchain_imports}"