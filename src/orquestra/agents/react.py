"""ReAct (Reasoning + Acting) Agent implementation."""

from __future__ import annotations

from typing import Any

from ..core.agent import Agent


class ReactAgent(Agent):
    """ReAct agent with reasoning and acting capabilities.

    The ReAct pattern interleaves reasoning traces and task-specific
    actions to solve problems.

    Example:
        ```python
        agent = ReactAgent(
            name="Assistant",
            description="A helpful AI assistant",
            provider="gpt-4o-mini"
        )

        @agent.tool()
        def search(query: str) -> str:
            '''Search the internet for information'''
            return search_results

        answer = agent.run("What is the capital of France?")
        ```
    """

    def __init__(
        self,
        name: str,
        description: str | None = None,
        provider: str | None = None,
        system_prompt: str | None = None,
        max_iterations: int = 10,
        **provider_kwargs: Any,
    ) -> None:
        """Initialize ReAct agent.

        Args:
            name: Agent name
            description: Agent description
            provider: Provider instance or model name
            system_prompt: Custom system prompt
            max_iterations: Maximum reasoning iterations
            **provider_kwargs: Additional provider configuration
        """
        # Use custom system prompt for ReAct if not provided
        if system_prompt is None:
            system_prompt = self._create_react_prompt(name, description)

        super().__init__(
            name=name,
            description=description,
            provider=provider,
            system_prompt=system_prompt,
            **provider_kwargs,
        )

        self.max_iterations = max_iterations

    def _create_react_prompt(self, name: str, description: str | None) -> str:
        """Create ReAct-specific system prompt.

        Args:
            name: Agent name
            description: Agent description

        Returns:
            System prompt with ReAct instructions
        """
        prompt = f"You are {name}"
        if description:
            prompt += f", {description}"
        prompt += ".\n\n"

        prompt += """You solve problems using the ReAct (Reasoning + Acting) pattern:

1. **Thought**: First, think about what you need to do to answer the question
2. **Action**: Use available tools to gather information or perform actions
3. **Observation**: Analyze the results from your actions
4. **Repeat**: Continue this cycle until you have enough information
5. **Answer**: Provide the final answer

When using tools:
- Always explain your reasoning before calling a tool
- Use tools when you need external information
- Analyze the tool results carefully
- Combine multiple tool results if needed

Be concise but thorough in your reasoning."""

        return prompt

    def run(
        self,
        prompt: str,
        max_iterations: int | None = None,
        **generation_kwargs: Any,
    ) -> str:
        """Run the ReAct agent with a prompt.

        Args:
            prompt: User prompt/question
            max_iterations: Override default max iterations
            **generation_kwargs: Additional generation parameters

        Returns:
            Agent's final response
        """
        iterations = max_iterations or self.max_iterations
        return super().run(prompt, max_iterations=iterations, **generation_kwargs)

    async def arun(
        self,
        prompt: str,
        max_iterations: int | None = None,
        **generation_kwargs: Any,
    ) -> str:
        """Async run the ReAct agent.

        Args:
            prompt: User prompt/question
            max_iterations: Override default max iterations
            **generation_kwargs: Additional generation parameters

        Returns:
            Agent's final response
        """
        iterations = max_iterations or self.max_iterations
        return await super().arun(prompt, max_iterations=iterations, **generation_kwargs)
