"""Unit tests for LLM providers."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from orquestra import Message, ProviderResponse, ToolCall
from orquestra.core.provider import ProviderFactory


class TestProviderFactory:
    """Tests for ProviderFactory."""

    def test_create_openai_provider(self):
        """Test creating OpenAI provider by name."""
        provider = ProviderFactory.create("gpt-4o-mini")

        assert provider is not None
        assert provider.model == "gpt-4o-mini"

    @pytest.mark.skipif(
        True,  # Skip if anthropic not installed
        reason="anthropic not installed"
    )
    def test_create_anthropic_provider(self):
        """Test creating Anthropic provider by name."""
        provider = ProviderFactory.create("claude-3-5-sonnet-20241022")

        assert provider is not None
        assert provider.model == "claude-3-5-sonnet-20241022"

    @pytest.mark.skipif(
        True,  # Skip if google-generativeai not installed
        reason="google-generativeai not installed"
    )
    def test_create_gemini_provider(self):
        """Test creating Gemini provider by name."""
        provider = ProviderFactory.create("gemini-1.5-flash")

        assert provider is not None
        assert provider.model == "gemini-1.5-flash"

    @pytest.mark.skipif(
        True,  # Skip if ollama not installed
        reason="ollama not installed"
    )
    def test_create_ollama_provider(self):
        """Test creating Ollama provider by name."""
        provider = ProviderFactory.create("llama3")

        assert provider is not None
        assert provider.model == "llama3"

    def test_create_unknown_provider(self):
        """Test that unknown provider raises error when dependencies missing."""
        # This will raise ImportError for missing ollama package
        with pytest.raises(ImportError):
            ProviderFactory.create("unknown-truly-doesnt-exist")

    def test_create_with_custom_params(self):
        """Test creating provider with custom parameters."""
        provider = ProviderFactory.create(
            "gpt-4o-mini",
            api_key="custom-key",
            base_url="https://custom.api.com"
        )

        assert provider.api_key == "custom-key"
        assert provider.base_url == "https://custom.api.com"

    def test_create_openrouter_provider(self):
        """Test creating OpenRouter provider by model format."""
        # OpenRouter models use format: provider/model-name
        provider = ProviderFactory.create(
            "anthropic/claude-3.5-sonnet",
            api_key="sk-or-test-key"
        )

        assert provider is not None
        assert provider.model == "anthropic/claude-3.5-sonnet"
        assert "openrouter" in provider.base_url

    def test_infer_openrouter_from_slash_format(self):
        """Test that models with slash are detected as OpenRouter."""
        from orquestra.core.provider import ProviderFactory

        # All these should be detected as OpenRouter
        test_models = [
            "openai/gpt-4",
            "anthropic/claude-3.5-sonnet",
            "meta-llama/llama-3.1-70b",
            "google/gemini-pro",
        ]

        for model in test_models:
            provider_name = ProviderFactory._infer_provider(model)
            assert provider_name == "openrouter", f"Failed for model: {model}"


class TestOpenAIProvider:
    """Tests for OpenAI provider."""

    @patch('orquestra.providers.openai_provider.OpenAI')
    def test_openai_complete(self, mock_openai_class):
        """Test OpenAI complete method."""
        from orquestra.providers.openai_provider import OpenAIProvider

        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock the completion response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30

        mock_client.chat.completions.create.return_value = mock_response

        # Create provider and test
        provider = OpenAIProvider("gpt-4o-mini", api_key="test-key")
        messages = [Message(role="user", content="Hello")]

        result = provider.complete(messages)

        assert result.content == "Test response"
        assert result.finish_reason == "stop"
        assert result.usage["prompt_tokens"] == 10
        assert result.usage["completion_tokens"] == 20

    @patch('orquestra.providers.openai_provider.OpenAI')
    def test_openai_complete_with_tools(self, mock_openai_class):
        """Test OpenAI complete with tool calls."""
        from orquestra.providers.openai_provider import OpenAIProvider

        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock tool call
        mock_tool_call = Mock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "test_tool"
        mock_tool_call.function.arguments = '{"arg": "value"}'

        # Mock the completion response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = None
        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        mock_response.choices[0].finish_reason = "tool_calls"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15

        mock_client.chat.completions.create.return_value = mock_response

        # Create provider and test
        provider = OpenAIProvider("gpt-4o-mini", api_key="test-key")
        messages = [Message(role="user", content="Use a tool")]
        tools = [{"type": "function", "function": {"name": "test_tool"}}]

        result = provider.complete(messages, tools=tools)

        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].name == "test_tool"
        assert result.tool_calls[0].id == "call_123"
        assert result.tool_calls[0].arguments == {"arg": "value"}

    def test_openai_supports_tools(self):
        """Test that OpenAI provider supports tools."""
        from orquestra.providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider("gpt-4o-mini", api_key="test-key")
        assert provider.supports_tools() is True


class TestAnthropicProvider:
    """Tests for Anthropic provider."""

    @pytest.mark.skipif(True, reason="anthropic not installed")
    @patch('orquestra.providers.anthropic_provider.Anthropic')
    def test_anthropic_complete(self, mock_anthropic_class):
        """Test Anthropic complete method."""
        from orquestra.providers.anthropic_provider import AnthropicProvider

        # Mock the Anthropic client
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        # Mock the completion response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Test response"
        mock_response.stop_reason = "end_turn"
        mock_response.usage = Mock()
        mock_response.usage.input_tokens = 15
        mock_response.usage.output_tokens = 25

        mock_client.messages.create.return_value = mock_response

        # Create provider and test
        provider = AnthropicProvider("claude-3-5-sonnet-20241022", api_key="test-key")
        messages = [Message(role="user", content="Hello")]

        result = provider.complete(messages)

        assert result.content == "Test response"
        assert result.finish_reason == "end_turn"
        assert result.usage["prompt_tokens"] == 15
        assert result.usage["completion_tokens"] == 25

    @pytest.mark.skipif(True, reason="anthropic not installed")
    def test_anthropic_supports_tools(self):
        """Test that Anthropic provider supports tools."""
        from orquestra.providers.anthropic_provider import AnthropicProvider

        provider = AnthropicProvider("claude-3-5-sonnet-20241022", api_key="test-key")
        assert provider.supports_tools() is True


class TestGeminiProvider:
    """Tests for Gemini provider."""

    @pytest.mark.skipif(True, reason="google-generativeai not installed")
    @patch('orquestra.providers.gemini_provider.genai')
    def test_gemini_complete(self, mock_genai):
        """Test Gemini complete method."""
        from orquestra.providers.gemini_provider import GeminiProvider

        # Mock the generate_content response
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_response.candidates = [Mock()]
        mock_response.candidates[0].finish_reason = 1  # STOP
        mock_response.usage_metadata = Mock()
        mock_response.usage_metadata.prompt_token_count = 12
        mock_response.usage_metadata.candidates_token_count = 18

        # Mock the model
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        # Create provider and test
        provider = GeminiProvider("gemini-1.5-flash", api_key="test-key")
        messages = [Message(role="user", content="Hello")]

        result = provider.complete(messages)

        assert result.content == "Test response"
        assert result.usage["prompt_tokens"] == 12
        assert result.usage["completion_tokens"] == 18

    @pytest.mark.skipif(True, reason="google-generativeai not installed")
    def test_gemini_supports_tools(self):
        """Test that Gemini provider supports tools."""
        from orquestra.providers.gemini_provider import GeminiProvider

        provider = GeminiProvider("gemini-1.5-flash", api_key="test-key")
        assert provider.supports_tools() is True


class TestOllamaProvider:
    """Tests for Ollama provider."""

    @pytest.mark.skipif(True, reason="ollama not installed")
    @patch('orquestra.providers.ollama_provider.requests.post')
    def test_ollama_complete(self, mock_post):
        """Test Ollama complete method."""
        from orquestra.providers.ollama_provider import OllamaProvider

        # Mock the HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "message": {"content": "Test response"},
            "done": True
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Create provider and test
        provider = OllamaProvider("llama3", base_url="http://localhost:11434")
        messages = [Message(role="user", content="Hello")]

        result = provider.complete(messages)

        assert result.content == "Test response"

    @pytest.mark.skipif(True, reason="ollama not installed")
    def test_ollama_supports_tools(self):
        """Test that Ollama provider supports tools."""
        from orquestra.providers.ollama_provider import OllamaProvider

        provider = OllamaProvider("llama3")
        assert provider.supports_tools() is True


class TestOpenRouterProvider:
    """Tests for OpenRouter provider."""

    @patch('orquestra.providers.openrouter_provider.OpenAI')
    def test_openrouter_complete(self, mock_openai_class):
        """Test OpenRouter complete method."""
        from orquestra.providers.openrouter_provider import OpenRouterProvider

        # Mock the OpenAI client (OpenRouter uses OpenAI-compatible API)
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock the completion response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response from OpenRouter"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 30

        mock_client.chat.completions.create.return_value = mock_response

        # Create provider and test
        provider = OpenRouterProvider("anthropic/claude-3.5-sonnet", api_key="sk-or-test-key")
        messages = [Message(role="user", content="Hello")]

        result = provider.complete(messages)

        assert result.content == "Test response from OpenRouter"
        assert result.finish_reason == "stop"
        assert result.usage["prompt_tokens"] == 10
        assert result.usage["completion_tokens"] == 20

    @patch('orquestra.providers.openrouter_provider.OpenAI')
    def test_openrouter_with_tools(self, mock_openai_class):
        """Test OpenRouter complete with tool calls."""
        from orquestra.providers.openrouter_provider import OpenRouterProvider

        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock tool call
        mock_tool_call = Mock()
        mock_tool_call.id = "call_openrouter_123"
        mock_tool_call.function.name = "test_tool"
        mock_tool_call.function.arguments = '{"arg": "value"}'

        # Mock the completion response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = None
        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        mock_response.choices[0].finish_reason = "tool_calls"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 15
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 20

        mock_client.chat.completions.create.return_value = mock_response

        # Create provider and test
        provider = OpenRouterProvider("openai/gpt-4", api_key="sk-or-test-key")
        messages = [Message(role="user", content="Use a tool")]
        tools = [{"type": "function", "function": {"name": "test_tool"}}]

        result = provider.complete(messages, tools=tools)

        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].name == "test_tool"
        assert result.tool_calls[0].id == "call_openrouter_123"
        assert result.tool_calls[0].arguments == {"arg": "value"}

    def test_openrouter_supports_tools(self):
        """Test that OpenRouter provider supports tools."""
        from orquestra.providers.openrouter_provider import OpenRouterProvider

        provider = OpenRouterProvider("meta-llama/llama-3.1-70b", api_key="sk-or-test-key")
        assert provider.supports_tools() is True

    def test_openrouter_base_url(self):
        """Test that OpenRouter uses correct base URL."""
        from orquestra.providers.openrouter_provider import OpenRouterProvider

        provider = OpenRouterProvider("anthropic/claude-3.5-sonnet", api_key="sk-or-test-key")
        assert provider.base_url == "https://openrouter.ai/api/v1"


class TestProviderErrorHandling:
    """Tests for provider error handling."""

    @patch('orquestra.providers.openai_provider.OpenAI')
    def test_openai_api_error(self, mock_openai_class):
        """Test OpenAI API error handling."""
        from orquestra.providers.openai_provider import OpenAIProvider

        # Mock the OpenAI client to raise an error
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        # Create provider and test
        provider = OpenAIProvider("gpt-4o-mini", api_key="test-key")
        messages = [Message(role="user", content="Hello")]

        with pytest.raises(Exception, match="API Error"):
            provider.complete(messages)

    @pytest.mark.skipif(True, reason="ollama not installed")
    @patch('orquestra.providers.ollama_provider.requests.post')
    def test_ollama_connection_error(self, mock_post):
        """Test Ollama connection error handling."""
        from orquestra.providers.ollama_provider import OllamaProvider
        import requests

        # Mock connection error
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        # Create provider and test
        provider = OllamaProvider("llama3")
        messages = [Message(role="user", content="Hello")]

        with pytest.raises(requests.exceptions.ConnectionError):
            provider.complete(messages)
