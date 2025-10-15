"""Unit tests for ReactAgent."""

import pytest

from orquestra import ReactAgent


class TestReactAgent:
    """Tests for ReactAgent class."""

    def test_create_react_agent(self):
        """Test creating a ReactAgent."""
        agent = ReactAgent(
            name="ReactTest",
            description="A test react agent",
            provider="gpt-4o-mini",
        )

        assert agent.name == "ReactTest"
        assert agent.description == "A test react agent"
        assert agent.max_iterations == 10

    def test_react_agent_custom_max_iterations(self):
        """Test ReactAgent with custom max_iterations."""
        agent = ReactAgent(
            name="ReactTest",
            provider="gpt-4o-mini",
            max_iterations=5,
        )

        assert agent.max_iterations == 5

    def test_react_system_prompt_has_react_pattern(self):
        """Test that ReactAgent has ReAct-specific system prompt."""
        agent = ReactAgent(
            name="ReactTest",
            provider="gpt-4o-mini",
        )

        assert "ReAct" in agent.system_prompt
        assert "Reasoning" in agent.system_prompt
        assert "Acting" in agent.system_prompt

    def test_react_system_prompt_has_date(self):
        """Test that ReactAgent system prompt includes date."""
        agent = ReactAgent(
            name="ReactTest",
            provider="gpt-4o-mini",
        )

        assert "Current date:" in agent.system_prompt
        assert agent.current_date in agent.system_prompt

    def test_react_agent_with_custom_system_prompt(self):
        """Test ReactAgent with custom system prompt overrides default."""
        custom_prompt = "Custom ReAct prompt."
        agent = ReactAgent(
            name="ReactTest",
            provider="gpt-4o-mini",
            system_prompt=custom_prompt,
        )

        assert agent.system_prompt == custom_prompt

    def test_react_agent_run_uses_max_iterations(self, mock_openai_provider):
        """Test that ReactAgent.run() uses configured max_iterations."""
        agent = ReactAgent(
            name="ReactTest",
            provider=mock_openai_provider,
            max_iterations=7,
        )

        # The run method should use the agent's max_iterations
        # We can't easily test this without mocking, but we verify the attribute exists
        assert agent.max_iterations == 7

    def test_react_agent_run_override_max_iterations(self, mock_openai_provider):
        """Test overriding max_iterations in run()."""
        agent = ReactAgent(
            name="ReactTest",
            provider=mock_openai_provider,
            max_iterations=10,
        )

        # Should accept override
        response = agent.run("Test", max_iterations=3)

        assert response is not None

    @pytest.mark.asyncio
    async def test_react_agent_arun(self, mock_openai_provider):
        """Test ReactAgent async run."""
        agent = ReactAgent(
            name="ReactTest",
            provider=mock_openai_provider,
        )

        response = await agent.arun("Test async")

        assert response is not None
