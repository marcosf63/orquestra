"""Base provider abstraction for LLM integration."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class Message(BaseModel):
    """Represents a chat message."""

    role: str  # "user", "assistant", "system"
    content: str


class ToolCall(BaseModel):
    """Represents a tool call from the LLM."""

    id: str
    name: str
    arguments: dict[str, Any]


class ProviderResponse(BaseModel):
    """Standardized response from any LLM provider."""

    content: str | None = None
    tool_calls: list[ToolCall] = []
    finish_reason: str | None = None
    usage: dict[str, int] = {}
    raw_response: Any = None

    class Config:
        arbitrary_types_allowed = True


class Provider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the provider.

        Args:
            model: Model identifier (e.g., "gpt-4o-mini", "claude-3-5-sonnet")
            api_key: API key for the provider (defaults to env variable)
            base_url: Custom base URL for the API
            **kwargs: Additional provider-specific configuration
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.config = kwargs

    @abstractmethod
    def complete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Generate a completion from the LLM.

        Args:
            messages: List of conversation messages
            tools: Optional list of available tools in provider format
            **kwargs: Additional generation parameters (temperature, max_tokens, etc.)

        Returns:
            Standardized provider response
        """
        pass

    @abstractmethod
    async def acomplete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Async version of complete.

        Args:
            messages: List of conversation messages
            tools: Optional list of available tools in provider format
            **kwargs: Additional generation parameters

        Returns:
            Standardized provider response
        """
        pass

    @abstractmethod
    def supports_tools(self) -> bool:
        """Check if this provider supports tool/function calling.

        Returns:
            True if provider supports tools, False otherwise
        """
        pass

    def format_tools(self, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Format tools for this specific provider.

        Override this method if the provider needs special tool formatting.

        Args:
            tools: Tools in standard format

        Returns:
            Tools formatted for this provider
        """
        return tools


class ProviderFactory:
    """Factory for creating provider instances."""

    _providers: dict[str, type[Provider]] = {}

    @classmethod
    def register(cls, name: str, provider_class: type[Provider]) -> None:
        """Register a provider class.

        Args:
            name: Provider name (e.g., "openai", "anthropic")
            provider_class: The provider class
        """
        cls._providers[name] = provider_class

    @classmethod
    def create(cls, model: str, **kwargs: Any) -> Provider:
        """Create a provider instance based on model name.

        Args:
            model: Model identifier (e.g., "gpt-4o-mini", "claude-3-5-sonnet")
            **kwargs: Additional provider configuration

        Returns:
            Provider instance

        Raises:
            ValueError: If provider cannot be determined from model name
        """
        # Determine provider from model name
        provider_name = cls._infer_provider(model)

        if provider_name not in cls._providers:
            raise ValueError(
                f"Unknown provider for model '{model}'. "
                f"Available providers: {list(cls._providers.keys())}"
            )

        provider_class = cls._providers[provider_name]
        return provider_class(model=model, **kwargs)

    @classmethod
    def _infer_provider(cls, model: str) -> str:
        """Infer provider from model name.

        Args:
            model: Model identifier

        Returns:
            Provider name

        Raises:
            ValueError: If provider cannot be inferred
        """
        model_lower = model.lower()

        # OpenAI models
        if any(
            x in model_lower for x in ["gpt-", "o1-", "o3-", "davinci", "curie", "babbage"]
        ):
            return "openai"

        # Anthropic models
        if "claude" in model_lower:
            return "anthropic"

        # Google Gemini models
        if "gemini" in model_lower or "palm" in model_lower:
            return "gemini"

        # Ollama (local models) - default for unknown
        # Ollama can run any model name, so it's our fallback
        return "ollama"

    @classmethod
    def list_providers(cls) -> list[str]:
        """Get list of registered providers.

        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
