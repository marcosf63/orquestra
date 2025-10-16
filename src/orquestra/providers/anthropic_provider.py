"""Anthropic provider implementation."""

from __future__ import annotations

import os
from typing import Any, AsyncGenerator, Generator

from ..core.provider import Message, Provider, ProviderResponse, StreamChunk, ToolCall

try:
    from anthropic import Anthropic, AsyncAnthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicProvider(Provider):
    """Anthropic provider for Claude models."""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize Anthropic provider.

        Args:
            model: Model name (e.g., "claude-3-5-sonnet-20241022", "claude-3-opus")
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            base_url: Custom base URL for API
            **kwargs: Additional Anthropic client configuration
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic package not installed. "
                "Install it with: uv add anthropic or pip install anthropic"
            )

        super().__init__(model, api_key, base_url, **kwargs)

        # Get API key from env if not provided
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not found. "
                "Set ANTHROPIC_API_KEY environment variable or pass api_key parameter"
            )

        # Initialize clients
        client_kwargs = {"api_key": self.api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self.client = Anthropic(**client_kwargs)
        self.async_client = AsyncAnthropic(**client_kwargs)

    def complete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Generate completion using Anthropic.

        Args:
            messages: Conversation messages
            tools: Optional tools in Anthropic format
            **kwargs: Additional generation parameters

        Returns:
            Standardized provider response
        """
        # Separate system message from conversation
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                conversation_messages.append({"role": msg.role, "content": msg.content})

        # Prepare completion kwargs
        completion_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": conversation_messages,
            "max_tokens": kwargs.pop("max_tokens", 4096),
            **kwargs,
        }

        if system_message:
            completion_kwargs["system"] = system_message

        if tools:
            completion_kwargs["tools"] = tools

        # Call Anthropic API
        response = self.client.messages.create(**completion_kwargs)

        # Parse response
        content = None
        tool_calls: list[ToolCall] = []

        for block in response.content:
            if block.type == "text":
                content = block.text
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input,
                    )
                )

        return ProviderResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=response.stop_reason,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            raw_response=response,
        )

    async def acomplete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Async completion using Anthropic.

        Args:
            messages: Conversation messages
            tools: Optional tools in Anthropic format
            **kwargs: Additional generation parameters

        Returns:
            Standardized provider response
        """
        # Separate system message from conversation
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                conversation_messages.append({"role": msg.role, "content": msg.content})

        # Prepare completion kwargs
        completion_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": conversation_messages,
            "max_tokens": kwargs.pop("max_tokens", 4096),
            **kwargs,
        }

        if system_message:
            completion_kwargs["system"] = system_message

        if tools:
            completion_kwargs["tools"] = tools

        # Call Anthropic API
        response = await self.async_client.messages.create(**completion_kwargs)

        # Parse response
        content = None
        tool_calls: list[ToolCall] = []

        for block in response.content:
            if block.type == "text":
                content = block.text
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input,
                    )
                )

        return ProviderResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=response.stop_reason,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            raw_response=response,
        )

    def supports_tools(self) -> bool:
        """Anthropic supports tool calling.

        Returns:
            True
        """
        return True

    def supports_streaming(self) -> bool:
        """Anthropic supports streaming responses.

        Returns:
            True
        """
        return True

    def stream(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> Generator[StreamChunk, None, None]:
        """Stream completion using Anthropic.

        Args:
            messages: Conversation messages
            tools: Optional tools in Anthropic format
            **kwargs: Additional generation parameters

        Yields:
            StreamChunk objects with incremental content
        """
        # Separate system message from conversation
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                conversation_messages.append({"role": msg.role, "content": msg.content})

        # Prepare completion kwargs
        completion_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": conversation_messages,
            "max_tokens": kwargs.pop("max_tokens", 4096),
            "stream": True,
            **kwargs,
        }

        if system_message:
            completion_kwargs["system"] = system_message

        if tools:
            completion_kwargs["tools"] = tools

        # Call Anthropic streaming API
        with self.client.messages.stream(**completion_kwargs) as stream:
            tool_call_accumulator: dict[str, dict[str, Any]] = {}

            for event in stream:
                # Handle text deltas
                if hasattr(event, 'type'):
                    if event.type == "content_block_delta":
                        if hasattr(event.delta, 'text'):
                            yield StreamChunk(content=event.delta.text)

                        # Handle tool use deltas
                        elif hasattr(event.delta, 'partial_json'):
                            # Anthropic sends partial JSON for tool inputs
                            pass

                    elif event.type == "content_block_start":
                        if hasattr(event.content_block, 'type'):
                            if event.content_block.type == "tool_use":
                                tool_id = event.content_block.id
                                tool_call_accumulator[tool_id] = {
                                    "id": tool_id,
                                    "name": event.content_block.name,
                                    "input": "",
                                }

                    elif event.type == "message_delta":
                        # Message finished
                        if tool_call_accumulator:
                            tool_calls = []
                            for data in tool_call_accumulator.values():
                                tool_calls.append(
                                    ToolCall(
                                        id=data["id"],
                                        name=data["name"],
                                        arguments=data.get("input", {}),
                                    )
                                )
                            if tool_calls:
                                yield StreamChunk(
                                    content="",
                                    tool_calls=tool_calls,
                                    finish_reason=event.delta.stop_reason if hasattr(event.delta, 'stop_reason') else None,
                                )

    async def astream(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[StreamChunk, None]:
        """Async stream completion using Anthropic.

        Args:
            messages: Conversation messages
            tools: Optional tools in Anthropic format
            **kwargs: Additional generation parameters

        Yields:
            StreamChunk objects with incremental content
        """
        # Separate system message from conversation
        system_message = None
        conversation_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                conversation_messages.append({"role": msg.role, "content": msg.content})

        # Prepare completion kwargs
        completion_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": conversation_messages,
            "max_tokens": kwargs.pop("max_tokens", 4096),
            "stream": True,
            **kwargs,
        }

        if system_message:
            completion_kwargs["system"] = system_message

        if tools:
            completion_kwargs["tools"] = tools

        # Call Anthropic streaming API
        async with self.async_client.messages.stream(**completion_kwargs) as stream:
            tool_call_accumulator: dict[str, dict[str, Any]] = {}

            async for event in stream:
                # Handle text deltas
                if hasattr(event, 'type'):
                    if event.type == "content_block_delta":
                        if hasattr(event.delta, 'text'):
                            yield StreamChunk(content=event.delta.text)

                        # Handle tool use deltas
                        elif hasattr(event.delta, 'partial_json'):
                            # Anthropic sends partial JSON for tool inputs
                            pass

                    elif event.type == "content_block_start":
                        if hasattr(event.content_block, 'type'):
                            if event.content_block.type == "tool_use":
                                tool_id = event.content_block.id
                                tool_call_accumulator[tool_id] = {
                                    "id": tool_id,
                                    "name": event.content_block.name,
                                    "input": "",
                                }

                    elif event.type == "message_delta":
                        # Message finished
                        if tool_call_accumulator:
                            tool_calls = []
                            for data in tool_call_accumulator.values():
                                tool_calls.append(
                                    ToolCall(
                                        id=data["id"],
                                        name=data["name"],
                                        arguments=data.get("input", {}),
                                    )
                                )
                            if tool_calls:
                                yield StreamChunk(
                                    content="",
                                    tool_calls=tool_calls,
                                    finish_reason=event.delta.stop_reason if hasattr(event.delta, 'stop_reason') else None,
                                )
