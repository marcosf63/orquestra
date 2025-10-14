"""Ollama provider implementation for local models."""

from __future__ import annotations

from typing import Any

from ..core.provider import Message, Provider, ProviderResponse, ToolCall

try:
    import ollama

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class OllamaProvider(Provider):
    """Ollama provider for local models."""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize Ollama provider.

        Args:
            model: Model name (e.g., "llama3", "mistral", "codellama")
            api_key: Not used for Ollama (local)
            base_url: Ollama server URL (defaults to http://localhost:11434)
            **kwargs: Additional Ollama configuration
        """
        if not OLLAMA_AVAILABLE:
            raise ImportError(
                "Ollama package not installed. "
                "Install it with: uv add ollama or pip install ollama"
            )

        super().__init__(model, api_key, base_url, **kwargs)

        # Ollama client configuration
        self.host = base_url or "http://localhost:11434"

        # Initialize client
        self.client = ollama.Client(host=self.host)
        self.async_client = ollama.AsyncClient(host=self.host)

    def complete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Generate completion using Ollama.

        Args:
            messages: Conversation messages
            tools: Optional tools (limited support in Ollama)
            **kwargs: Additional generation parameters

        Returns:
            Standardized provider response
        """
        # Convert messages to Ollama format
        ollama_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        # Prepare chat kwargs
        chat_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": ollama_messages,
            **kwargs,
        }

        # Add tools if provided (note: not all Ollama models support this)
        if tools:
            chat_kwargs["tools"] = tools

        try:
            # Call Ollama API
            response = self.client.chat(**chat_kwargs)

            # Parse response
            content = response.get("message", {}).get("content", "")
            tool_calls: list[ToolCall] = []

            # Check for tool calls (if supported by model)
            if "tool_calls" in response.get("message", {}):
                for tc in response["message"]["tool_calls"]:
                    tool_calls.append(
                        ToolCall(
                            id=tc.get("id", ""),
                            name=tc.get("name", ""),
                            arguments=tc.get("arguments", {}),
                        )
                    )

            return ProviderResponse(
                content=content,
                tool_calls=tool_calls,
                finish_reason=response.get("done_reason"),
                usage={},  # Ollama doesn't provide token counts by default
                raw_response=response,
            )

        except Exception as e:
            return ProviderResponse(
                content=f"Error: {str(e)}",
                tool_calls=[],
                finish_reason="error",
                usage={},
                raw_response=None,
            )

    async def acomplete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Async completion using Ollama.

        Args:
            messages: Conversation messages
            tools: Optional tools
            **kwargs: Additional generation parameters

        Returns:
            Standardized provider response
        """
        # Convert messages to Ollama format
        ollama_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        # Prepare chat kwargs
        chat_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": ollama_messages,
            **kwargs,
        }

        if tools:
            chat_kwargs["tools"] = tools

        try:
            # Call Ollama API
            response = await self.async_client.chat(**chat_kwargs)

            # Parse response
            content = response.get("message", {}).get("content", "")
            tool_calls: list[ToolCall] = []

            if "tool_calls" in response.get("message", {}):
                for tc in response["message"]["tool_calls"]:
                    tool_calls.append(
                        ToolCall(
                            id=tc.get("id", ""),
                            name=tc.get("name", ""),
                            arguments=tc.get("arguments", {}),
                        )
                    )

            return ProviderResponse(
                content=content,
                tool_calls=tool_calls,
                finish_reason=response.get("done_reason"),
                usage={},
                raw_response=response,
            )

        except Exception as e:
            return ProviderResponse(
                content=f"Error: {str(e)}",
                tool_calls=[],
                finish_reason="error",
                usage={},
                raw_response=None,
            )

    def supports_tools(self) -> bool:
        """Ollama has limited tool support depending on model.

        Returns:
            False by default (can be overridden for specific models)
        """
        # Some Ollama models support tools, but it's not universal
        # For safety, default to False
        return False
