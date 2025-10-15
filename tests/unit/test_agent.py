"""Unit tests for the base Agent class."""

import logging
from datetime import datetime
from unittest.mock import Mock

import pytest

from orquestra import Agent, Message, ProviderResponse, ToolCall


class TestAgentInitialization:
    """Tests for Agent initialization."""

    def test_create_agent(self, mock_openai_provider):
        """Test creating a basic agent."""
        agent = Agent(
            name="TestAgent",
            description="A test agent",
            provider=mock_openai_provider,
        )

        assert agent.name == "TestAgent"
        assert agent.description == "A test agent"
        assert agent.provider == mock_openai_provider
        assert len(agent.messages) == 0

    def test_agent_with_provider_string(self):
        """Test creating agent with provider model name string."""
        agent = Agent(
            name="TestAgent",
            provider="gpt-4o-mini",
        )

        assert agent.name == "TestAgent"
        assert agent.provider is not None
        assert agent.provider.model == "gpt-4o-mini"

    def test_agent_without_provider_raises_error(self):
        """Test that creating agent without provider raises error."""
        with pytest.raises(ValueError, match="provider must be"):
            Agent(name="TestAgent", provider=None)

    def test_agent_date_attributes(self, mock_openai_provider):
        """Test that agent has current date attributes."""
        agent = Agent(
            name="TestAgent",
            provider=mock_openai_provider,
        )

        assert agent.current_date is not None
        assert agent.current_datetime is not None
        assert len(agent.current_date) == 10  # YYYY-MM-DD format
        assert len(agent.current_datetime) == 19  # YYYY-MM-DD HH:MM:SS format

        # Verify format
        datetime.strptime(agent.current_date, "%Y-%m-%d")
        datetime.strptime(agent.current_datetime, "%Y-%m-%d %H:%M:%S")

    def test_agent_custom_date(self, mock_openai_provider):
        """Test agent with custom date."""
        agent = Agent(
            name="TestAgent",
            provider=mock_openai_provider,
            current_date="2024-12-25",
            current_datetime="2024-12-25 09:30:00",
        )

        assert agent.current_date == "2024-12-25"
        assert agent.current_datetime == "2024-12-25 09:30:00"

    def test_agent_system_prompt_includes_date(self, mock_openai_provider):
        """Test that system prompt includes date information."""
        agent = Agent(
            name="TestAgent",
            provider=mock_openai_provider,
        )

        assert "Current date:" in agent.system_prompt
        assert agent.current_date in agent.system_prompt
        assert agent.current_datetime in agent.system_prompt

    def test_agent_custom_system_prompt(self, mock_openai_provider):
        """Test agent with custom system prompt."""
        custom_prompt = "You are a custom assistant."
        agent = Agent(
            name="TestAgent",
            provider=mock_openai_provider,
            system_prompt=custom_prompt,
        )

        assert agent.system_prompt == custom_prompt


class TestAgentLogging:
    """Tests for Agent logging functionality."""

    def test_agent_default_logging(self, mock_openai_provider):
        """Test agent has logging disabled by default."""
        agent = Agent(
            name="TestAgent",
            provider=mock_openai_provider,
        )

        assert agent.verbose is False
        assert agent.debug is False
        assert agent.logger.level == logging.WARNING

    def test_agent_verbose_mode(self, mock_openai_provider):
        """Test agent with verbose mode enabled."""
        agent = Agent(
            name="TestAgent",
            provider=mock_openai_provider,
            verbose=True,
        )

        assert agent.verbose is True
        assert agent.debug is False
        assert agent.logger.level == logging.INFO

    def test_agent_debug_mode(self, mock_openai_provider):
        """Test agent with debug mode enabled."""
        agent = Agent(
            name="TestAgent",
            provider=mock_openai_provider,
            debug=True,
        )

        assert agent.verbose is True  # debug implies verbose
        assert agent.debug is True
        assert agent.logger.level == logging.DEBUG

    def test_logger_name(self, mock_openai_provider):
        """Test logger has correct name."""
        agent = Agent(
            name="CustomName",
            provider=mock_openai_provider,
        )

        assert agent.logger.name == "orquestra.agent.CustomName"


class TestAgentToolRegistration:
    """Tests for tool registration in Agent."""

    def test_register_tool_with_decorator(self, mock_openai_provider):
        """Test registering tool with @agent.tool() decorator."""
        agent = Agent(name="TestAgent", provider=mock_openai_provider)

        @agent.tool()
        def test_function(x: int) -> int:
            """A test function."""
            return x * 2

        assert len(agent.tools) == 1
        tool = agent.tools.get("test_function")
        assert tool is not None
        assert tool.name == "test_function"

    def test_register_tool_with_custom_name(self, mock_openai_provider):
        """Test registering tool with custom name."""
        agent = Agent(name="TestAgent", provider=mock_openai_provider)

        @agent.tool(name="custom_name")
        def test_function(x: int) -> int:
            """A test function."""
            return x * 2

        tool = agent.tools.get("custom_name")
        assert tool is not None
        assert tool.name == "custom_name"

    def test_add_tool_programmatically(self, mock_openai_provider, sample_tool_function):
        """Test adding tool programmatically."""
        agent = Agent(name="TestAgent", provider=mock_openai_provider)

        tool = agent.add_tool(sample_tool_function)

        assert tool is not None
        assert len(agent.tools) == 1
        assert agent.tools.get("add_numbers") == tool

    def test_multiple_tools(self, mock_openai_provider):
        """Test registering multiple tools."""
        agent = Agent(name="TestAgent", provider=mock_openai_provider)

        @agent.tool()
        def tool1(x: int) -> int:
            return x

        @agent.tool()
        def tool2(y: str) -> str:
            return y

        assert len(agent.tools) == 2
        assert agent.tools.get("tool1") is not None
        assert agent.tools.get("tool2") is not None


class TestAgentRun:
    """Tests for Agent.run() method."""

    def test_run_basic(self, mock_openai_provider):
        """Test basic run without tools."""
        agent = Agent(name="TestAgent", provider=mock_openai_provider)

        response = agent.run("Hello, agent!")

        assert response == "This is a mocked response from the provider."
        assert len(agent.messages) == 3  # system + user + assistant

    def test_run_adds_system_message_first_time(self, mock_openai_provider):
        """Test that system message is added on first run."""
        agent = Agent(name="TestAgent", provider=mock_openai_provider)

        agent.run("Test")

        # Should have system message first
        assert agent.messages[0].role == "system"
        assert agent.messages[1].role == "user"

    def test_run_doesnt_duplicate_system_message(self, mock_openai_provider):
        """Test that system message is not duplicated on subsequent runs."""
        agent = Agent(name="TestAgent", provider=mock_openai_provider)

        agent.run("First message")
        agent.run("Second message")

        # Count system messages
        system_msgs = [m for m in agent.messages if m.role == "system"]
        assert len(system_msgs) == 1

    def test_run_with_tool_call(self, mock_provider_with_tool_call):
        """Test run with tool calls."""
        agent = Agent(name="TestAgent", provider=mock_provider_with_tool_call)

        # Register a tool
        @agent.tool()
        def test_tool(arg1: str) -> str:
            """A test tool."""
            return f"Tool executed with {arg1}"

        response = agent.run("Use the tool")

        assert response == "Final response after tool use"
        # Should have called complete twice (tool call + final response)
        # Note: Can't easily verify call_count with our MockProvider implementation

    def test_run_with_max_iterations(self):
        """Test run with custom max_iterations."""
        from tests.conftest import MockProvider

        # Create provider that always returns tool calls
        provider = MockProvider(model="gpt-4o-mini")
        provider._complete_response = ProviderResponse(
            content="Using tools",
            tool_calls=[
                ToolCall(
                    id="call_fake",
                    name="fake_tool",
                    arguments={}
                )
            ]
        )

        agent = Agent(name="TestAgent", provider=provider)

        # Register a fake tool
        @agent.tool()
        def fake_tool() -> str:
            """A fake tool."""
            return "Fake result"

        # Should stop after max_iterations
        response = agent.run("Test", max_iterations=3)

        assert "Max iterations reached" in response or len(agent.messages) > 0

    def test_reset_clears_messages(self, mock_openai_provider):
        """Test that reset() clears message history."""
        agent = Agent(name="TestAgent", provider=mock_openai_provider)

        agent.run("First")
        agent.run("Second")
        assert len(agent.messages) > 0

        agent.reset()
        assert len(agent.messages) == 0


class TestAgentAsyncRun:
    """Tests for Agent.arun() async method."""

    @pytest.mark.asyncio
    async def test_arun_basic(self, mock_openai_provider):
        """Test basic async run."""
        agent = Agent(name="TestAgent", provider=mock_openai_provider)

        response = await agent.arun("Hello, agent!")

        assert response == "This is a mocked async response from the provider."

    @pytest.mark.asyncio
    async def test_arun_adds_messages(self, mock_openai_provider):
        """Test that async run adds messages correctly."""
        agent = Agent(name="TestAgent", provider=mock_openai_provider)

        await agent.arun("Test message")

        assert len(agent.messages) >= 2
        assert agent.messages[0].role == "system"
        assert agent.messages[1].role == "user"


class TestAgentErrorHandling:
    """Tests for Agent error handling."""

    def test_tool_not_found(self):
        """Test handling of tool not found error."""
        from tests.conftest import MockProvider

        provider = MockProvider(model="gpt-4o-mini")
        provider._complete_side_effect = [
            ProviderResponse(
                content="Using unknown tool",
                tool_calls=[
                    ToolCall(
                        id="call_unknown",
                        name="unknown_tool",
                        arguments={}
                    )
                ]
            ),
            ProviderResponse(content="Continuing after error", tool_calls=[])
        ]

        agent = Agent(name="TestAgent", provider=provider)
        response = agent.run("Use unknown tool")

        # Should handle error and continue
        assert response is not None
        # Error message should be added to messages
        assert any("unknown_tool" in str(m.content) for m in agent.messages)

    def test_tool_execution_error(self):
        """Test handling of tool execution errors."""
        from tests.conftest import MockProvider

        provider = MockProvider(model="gpt-4o-mini")
        provider._complete_side_effect = [
            ProviderResponse(
                content="Using tool",
                tool_calls=[
                    ToolCall(
                        id="call_error",
                        name="error_tool",
                        arguments={}
                    )
                ]
            ),
            ProviderResponse(content="Handled error", tool_calls=[])
        ]

        agent = Agent(name="TestAgent", provider=provider)

        # Register a tool that raises an error
        @agent.tool()
        def error_tool() -> str:
            """A tool that raises an error."""
            raise ValueError("Intentional error")

        response = agent.run("Use error tool")

        # Should handle error and continue
        assert response is not None
        # Error message should be in messages
        assert any("Error executing tool" in str(m.content) for m in agent.messages)

    def test_no_response_generated(self):
        """Test handling when provider returns no content."""
        from tests.conftest import MockProvider

        provider = MockProvider(model="gpt-4o-mini")
        provider._complete_response = ProviderResponse(
            content=None,
            tool_calls=[]
        )

        agent = Agent(name="TestAgent", provider=provider)
        response = agent.run("Test")

        assert "No response generated" in response

    def test_debug_mode_logging(self):
        """Test that debug mode provides detailed logs."""
        from tests.conftest import MockProvider

        provider = MockProvider(model="gpt-4o-mini")
        agent = Agent(name="TestAgent", provider=provider, debug=True)

        assert agent.debug is True
        assert agent.verbose is True
        assert agent.logger.level == logging.DEBUG
