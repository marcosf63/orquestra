"""OpenAI provider implementation."""

from __future__ import annotations

import os
from typing import Any

from ..core.provider import Message, Provider, ProviderResponse, ToolCall

try:
    from openai import AsyncOpenAI, OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIProvider(Provider):
    """OpenAI provider for GPT models."""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize OpenAI provider.

        Args:
            model: Model name (e.g., "gpt-4o-mini", "gpt-4")
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            base_url: Custom base URL for API
            **kwargs: Additional OpenAI client configuration
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package not installed. "
                "Install it with: uv add openai or pip install openai"
            )

        super().__init__(model, api_key, base_url, **kwargs)

        # Get API key from env if not provided
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter"
            )

        # Initialize clients
        client_kwargs = {"api_key": self.api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self.client = OpenAI(**client_kwargs)
        self.async_client = AsyncOpenAI(**client_kwargs)

    def complete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Generate completion using OpenAI.

        Args:
            messages: Conversation messages
            tools: Optional tools in OpenAI format
            **kwargs: Additional generation parameters

        Returns:
            Standardized provider response
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

        # Call OpenAI API
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
        """Async completion using OpenAI.

        Args:
            messages: Conversation messages
            tools: Optional tools in OpenAI format
            **kwargs: Additional generation parameters

        Returns:
            Standardized provider response
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

        # Call OpenAI API
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
        """OpenAI supports function calling.

        Returns:
            True
        """
        return True
