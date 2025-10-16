"""Workflow system for agent orchestration and chaining."""

from __future__ import annotations

from typing import Any, Callable

from ..core.agent import Agent


class Workflow:
    """Simple workflow for chaining agents and tasks.

    Example:
        ```python
        from orquestra import ReactAgent
        from orquestra.orchestration import Workflow

        # Create agents
        researcher = ReactAgent(name="Researcher", provider="gpt-4o-mini")
        writer = ReactAgent(name="Writer", provider="gpt-4o-mini")

        # Create workflow
        workflow = Workflow()
        workflow.add_step("research", researcher.run)
        workflow.add_step("write", writer.run)

        # Run workflow
        result = workflow.run("Write about AI")
        ```
    """

    def __init__(self, name: str = "Workflow") -> None:
        """Initialize workflow.

        Args:
            name: Workflow name
        """
        self.name = name
        self.steps: list[tuple[str, Callable]] = []

    def add_step(
        self,
        name: str,
        func: Callable,
        pass_previous: bool = True,
    ) -> Workflow:
        """Add a step to the workflow.

        Args:
            name: Step name
            func: Function or agent method to execute
            pass_previous: Whether to pass previous result to this step

        Returns:
            Self for chaining
        """
        self.steps.append((name, func, pass_previous))
        return self

    def run(self, initial_input: str, **kwargs: Any) -> str:
        """Execute the workflow.

        Args:
            initial_input: Initial input for the workflow
            **kwargs: Additional arguments passed to each step

        Returns:
            Final result
        """
        result = initial_input

        for step_name, func, pass_previous in self.steps:
            print(f"\n▶ Running step: {step_name}")

            if pass_previous:
                result = func(result, **kwargs)
            else:
                result = func(**kwargs)

        return result


class SequentialWorkflow(Workflow):
    """Sequential workflow that passes results between agents.

    Each agent receives the output from the previous agent as input.

    Example:
        ```python
        workflow = SequentialWorkflow()
        workflow.add_agent(research_agent)
        workflow.add_agent(summary_agent)
        workflow.add_agent(writer_agent)

        result = workflow.run("Research quantum computing")
        ```
    """

    def add_agent(self, agent: Agent) -> SequentialWorkflow:
        """Add an agent to the workflow.

        Args:
            agent: Agent to add

        Returns:
            Self for chaining
        """
        self.add_step(agent.name, agent.run, pass_previous=True)
        return self  # type: ignore


# Placeholder for future ParallelWorkflow
class ParallelWorkflow:
    """Parallel workflow for running multiple agents concurrently.

    Note: This is a placeholder for future implementation.
    Requires async support and result aggregation.
    """

    def __init__(self, name: str = "ParallelWorkflow") -> None:
        self.name = name
        raise NotImplementedError(
            "ParallelWorkflow is not yet implemented. "
            "Use SequentialWorkflow for now."
        )
