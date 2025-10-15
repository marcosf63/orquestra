"""Pytest configuration and shared fixtures."""

import os
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest

from orquestra import Message, ProviderResponse, ToolCall
from orquestra.core.provider import Provider


@pytest.fixture(autouse=True)
def set_test_api_keys(monkeypatch):
    """Set dummy API keys for all tests to avoid missing key errors."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-dummy-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")


class MockProvider(Provider):
    """Mock provider for testing that properly inherits from Provider."""

    def __init__(self, model: str = "gpt-4o-mini", **kwargs):
        super().__init__(model=model, **kwargs)
        self._complete_response = ProviderResponse(
            content="This is a mocked response from the provider.",
            tool_calls=[]
        )
        self._acomplete_response = ProviderResponse(
            content="This is a mocked async response from the provider.",
            tool_calls=[]
        )
        self._complete_side_effect = None

    def complete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Mock complete method."""
        if self._complete_side_effect:
            return self._complete_side_effect.pop(0)
        return self._complete_response

    async def acomplete(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Mock acomplete method."""
        return self._acomplete_response

    def supports_tools(self) -> bool:
        """Mock supports_tools method."""
        return True


@pytest.fixture
def mock_openai_provider():
    """Mock OpenAI provider for testing without API calls."""
    return MockProvider(model="gpt-4o-mini")


@pytest.fixture
def mock_provider_with_tool_call():
    """Mock provider that returns a tool call."""
    provider = MockProvider(model="gpt-4o-mini")

    # Set up side effect for multiple calls
    provider._complete_side_effect = [
        ProviderResponse(
            content="I need to use a tool",
            tool_calls=[
                ToolCall(
                    id="call_123",
                    name="test_tool",
                    arguments={"arg1": "value1"}
                )
            ]
        ),
        ProviderResponse(
            content="Final response after tool use",
            tool_calls=[]
        )
    ]

    return provider


@pytest.fixture
def sample_messages():
    """Sample messages for testing."""
    return [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Hello, how are you?"),
        Message(role="assistant", content="I'm doing well, thank you!"),
        Message(role="user", content="What's the weather?"),
    ]


@pytest.fixture
def temp_db(tmp_path):
    """Temporary database path for testing storage."""
    db_path = tmp_path / "test.db"
    return str(db_path)


@pytest.fixture
def temp_file(tmp_path):
    """Temporary file for testing filesystem operations."""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Test content")
    return str(file_path)


@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for testing."""
    test_dir = tmp_path / "test_directory"
    test_dir.mkdir()

    # Create some test files
    (test_dir / "file1.txt").write_text("Content 1")
    (test_dir / "file2.txt").write_text("Content 2")
    (test_dir / "subdir").mkdir()
    (test_dir / "subdir" / "file3.txt").write_text("Content 3")

    return str(test_dir)


@pytest.fixture
def sample_tool_function():
    """Sample function for tool creation testing."""
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together.

        Args:
            a: First number
            b: Second number

        Returns:
            Sum of a and b
        """
        return a + b

    return add_numbers


@pytest.fixture
def sample_tool_function_with_optional():
    """Sample function with optional parameters."""
    def greet(name: str, greeting: str = "Hello") -> str:
        """Greet someone.

        Args:
            name: Name of the person
            greeting: Greeting to use (default: Hello)

        Returns:
            Greeting message
        """
        return f"{greeting}, {name}!"

    return greet
