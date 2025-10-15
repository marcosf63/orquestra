"""OpenRouter provider implementation."""

from __future__ import annotations

import os
from typing import Any

from ..core.provider import Message, Provider, ProviderResponse, ToolCall

try:
    from openai import AsyncOpenAI, OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenRouterProvider(Provider):
    """OpenRouter provider for accessing 100+ models through a unified API.

    OpenRouter provides access to models from OpenAI, Anthropic, Google, Meta,
    and many other providers through a single API compatible with OpenAI's format.

    Examples:
        >>> # Create agent with OpenRouter
        >>> agent = ReactAgent(
        ...     name="Assistant",
        ...     provider="anthropic/claude-3.5-sonnet",  # Auto-detects OpenRouter
        ...     api_key="sk-or-v1-..."  # or set OPENROUTER_API_KEY env var
        ... )

        >>> # Or specify provider explicitly
        >>> from orquestra.providers import OpenRouterProvider
        >>> provider = OpenRouterProvider(
        ...     model="openai/gpt-4",
        ...     api_key="sk-or-v1-..."
        ... )
    """

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        **kwargs: Any,
    ) -> None:
        """Initialize OpenRouter provider.

        Args:
            model: Model name in format "provider/model"
                  (e.g., "openai/gpt-4", "anthropic/claude-3.5-sonnet")
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
            base_url: OpenRouter API base URL (default: https://openrouter.ai/api/v1)
            **kwargs: Additional OpenAI client configuration

        Raises:
            ImportError: If openai package is not installed
            ValueError: If API key is not provided or found in environment
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package not installed (required for OpenRouter). "
                "Install it with: uv add openai or pip install openai"
            )

        super().__init__(model, api_key, base_url, **kwargs)

        # Get API key from env if not provided
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. "
                "Set OPENROUTER_API_KEY environment variable or pass api_key parameter. "
                "Get your key at: https://openrouter.ai/keys"
            )

        self.base_url = base_url

        # Initialize OpenAI-compatible clients with OpenRouter base URL
        client_kwargs = {
            "api_key": self.api_key,
            "base_url": self.base_url,
        }

        self.client = OpenAI(**client_kwargs)
        self.async_client = AsyncOpenAI(**client_kwargs)

    def complete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Generate completion using OpenRouter.

        Args:
            messages: Conversation messages
            tools: Optional tools in OpenAI format
            **kwargs: Additional generation parameters (temperature, max_tokens, etc.)

        Returns:
            Standardized provider response

        Examples:
            >>> provider = OpenRouterProvider("anthropic/claude-3.5-sonnet")
            >>> messages = [Message(role="user", content="Hello!")]
            >>> response = provider.complete(messages)
            >>> print(response.content)
        """
        # Convert messages to OpenAI format
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        # Prepare completion kwargs
        completion_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": openai_messages,
            **kwargs,
        }

        if tools:
            completion_kwargs["tools"] = tools
            # Enable parallel tool calls by default
            completion_kwargs.setdefault("parallel_tool_calls", True)

        # Call OpenRouter API (OpenAI-compatible)
        response = self.client.chat.completions.create(**completion_kwargs)

        # Extract first choice
        choice = response.choices[0]

        # Parse tool calls if present
        tool_calls: list[ToolCall] = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                import json

                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                    )
                )

        return ProviderResponse(
            content=choice.message.content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            raw_response=response,
        )

    async def acomplete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Async completion using OpenRouter.

        Args:
            messages: Conversation messages
            tools: Optional tools in OpenAI format
            **kwargs: Additional generation parameters

        Returns:
            Standardized provider response

        Examples:
            >>> provider = OpenRouterProvider("openai/gpt-4")
            >>> messages = [Message(role="user", content="Hello!")]
            >>> response = await provider.acomplete(messages)
        """
        # Convert messages to OpenAI format
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        # Prepare completion kwargs
        completion_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": openai_messages,
            **kwargs,
        }

        if tools:
            completion_kwargs["tools"] = tools
            completion_kwargs.setdefault("parallel_tool_calls", True)

        # Call OpenRouter API (OpenAI-compatible)
        response = await self.async_client.chat.completions.create(**completion_kwargs)

        # Extract first choice
        choice = response.choices[0]

        # Parse tool calls if present
        tool_calls: list[ToolCall] = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                import json

                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                    )
                )

        return ProviderResponse(
            content=choice.message.content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            raw_response=response,
        )

    def supports_tools(self) -> bool:
        """OpenRouter supports function calling for compatible models.

        Returns:
            True (most modern models on OpenRouter support tools)
        """
        return True
