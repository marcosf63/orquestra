"""Google Gemini provider implementation."""

from __future__ import annotations

import os
from typing import Any

from ..core.provider import Message, Provider, ProviderResponse, ToolCall

try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiProvider(Provider):
    """Google Gemini provider."""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize Gemini provider.

        Args:
            model: Model name (e.g., "gemini-pro", "gemini-1.5-flash")
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            base_url: Custom base URL (not used for Gemini)
            **kwargs: Additional generation configuration
        """
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "Google GenerativeAI package not installed. "
                "Install it with: uv add google-generativeai or pip install google-generativeai"
            )

        super().__init__(model, api_key, base_url, **kwargs)

        # Get API key from env if not provided
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API key not found. "
                "Set GOOGLE_API_KEY environment variable or pass api_key parameter"
            )

        # Configure genai
        genai.configure(api_key=self.api_key)

        # Initialize model
        self.genai_model = genai.GenerativeModel(model)

    def complete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Generate completion using Gemini.

        Args:
            messages: Conversation messages
            tools: Optional tools (Gemini function declarations)
            **kwargs: Additional generation parameters

        Returns:
            Standardized provider response
        """
        # Convert messages to Gemini format
        # Gemini uses a different chat format
        gemini_messages = []
        system_instruction = None

        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            elif msg.role == "user":
                gemini_messages.append({"role": "user", "parts": [msg.content]})
            elif msg.role == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg.content]})

        # Start chat session
        chat = self.genai_model.start_chat(history=gemini_messages[:-1] if gemini_messages else [])

        # Prepare generation config
        generation_config = kwargs.copy()

        # Send message
        if gemini_messages:
            last_message = gemini_messages[-1]["parts"][0]
        else:
            last_message = ""

        try:
            response = chat.send_message(
                last_message,
                generation_config=generation_config if generation_config else None,
            )

            # Gemini doesn't support function calling in the same way
            # This is a simplified implementation
            content = response.text if hasattr(response, "text") else None

            return ProviderResponse(
                content=content,
                tool_calls=[],
                finish_reason=None,
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

    async def acomplete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Async completion using Gemini.

        Note: Google's genai library doesn't have full async support yet.
        This is a wrapper around the sync method.

        Args:
            messages: Conversation messages
            tools: Optional tools
            **kwargs: Additional generation parameters

        Returns:
            Standardized provider response
        """
        # For now, just call sync version
        # In production, consider using asyncio.to_thread
        return self.complete(messages, tools, **kwargs)

    def supports_tools(self) -> bool:
        """Gemini has limited tool support.

        Returns:
            False for now (can be extended in future)
        """
        return False
