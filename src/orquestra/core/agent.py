"""Base Agent class with FastAPI-style decorators for tool registration."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Callable, TypeVar

from .provider import Message, Provider, ProviderFactory
from .tool import Tool, ToolRegistry

F = TypeVar("F", bound=Callable[..., Any])


class Agent:
    """Base agent class with decorator-based tool registration.

    Example:
        ```python
        agent = Agent(
            name="Assistant",
            description="A helpful AI assistant",
            provider="gpt-4o-mini"
        )

        @agent.tool()
        def search(query: str) -> str:
            '''Search the internet'''
            return results

        response = agent.run("What is the capital of France?")
        ```
    """

    def __init__(
        self,
        name: str,
        description: str | None = None,
        provider: str | Provider | None = None,
        system_prompt: str | None = None,
        current_date: str | None = None,
        current_datetime: str | None = None,
        verbose: bool = False,
        debug: bool = False,
        **provider_kwargs: Any,
    ) -> None:
        """Initialize the agent.

        Args:
            name: Agent name
            description: Agent description
            provider: Provider instance or model name (e.g., "gpt-4o-mini")
            system_prompt: Custom system prompt for the agent
            current_date: Current date (YYYY-MM-DD). Defaults to today's date.
            current_datetime: Current datetime (YYYY-MM-DD HH:MM:SS). Defaults to now.
            verbose: Enable verbose logging (INFO level)
            debug: Enable debug logging (DEBUG level, implies verbose=True)
            **provider_kwargs: Additional provider configuration
        """
        self.name = name
        self.description = description

        # Set current date and datetime
        now = datetime.now()
        self.current_date = current_date or now.strftime("%Y-%m-%d")
        self.current_datetime = current_datetime or now.strftime("%Y-%m-%d %H:%M:%S")

        # Configure logging
        self.verbose = verbose
        self.debug = debug
        if debug:
            self.verbose = True  # debug implies verbose

        # Setup logger
        self.logger = logging.getLogger(f"orquestra.agent.{name}")
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
        elif self.verbose:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.WARNING)

        # Add console handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            if self.debug:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S'
                )
            else:
                formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.system_prompt = system_prompt or self._default_system_prompt()

        # Initialize provider
        if isinstance(provider, Provider):
            self.provider = provider
        elif isinstance(provider, str):
            self.provider = ProviderFactory.create(provider, **provider_kwargs)
        else:
            raise ValueError("provider must be a Provider instance or model name string")

        # Initialize tool registry
        self.tools = ToolRegistry()

        # Message history
        self.messages: list[Message] = []

    def _default_system_prompt(self) -> str:
        """Generate default system prompt.

        Returns:
            Default system prompt string
        """
        prompt = f"You are {self.name}"
        if self.description:
            prompt += f", {self.description}"
        prompt += ".\n\n"

        # Add date context
        prompt += f"Current date: {self.current_date}\n"
        prompt += f"Current date and time: {self.current_datetime}\n"

        return prompt

    def tool(
        self, name: str | None = None
    ) -> Callable[[F], F]:
        """Decorator to register a function as a tool.

        Args:
            name: Optional custom name for the tool

        Returns:
            Decorator function

        Example:
            ```python
            @agent.tool()
            def search(query: str) -> str:
                '''Search for information'''
                return results
            ```
        """

        def decorator(func: F) -> F:
            self.tools.register_function(func, name)
            return func

        return decorator

    def add_tool(self, func: Callable[..., Any], name: str | None = None) -> Tool:
        """Programmatically add a tool to the agent.

        Args:
            func: Function to add as a tool
            name: Optional custom name for the tool

        Returns:
            The created Tool instance

        Example:
            ```python
            def my_function(x: int) -> int:
                return x * 2

            agent.add_tool(my_function)
            ```
        """
        return self.tools.register_function(func, name)

    def run(
        self,
        prompt: str,
        max_iterations: int = 10,
        **generation_kwargs: Any,
    ) -> str:
        """Run the agent with a prompt.

        Args:
            prompt: User prompt/question
            max_iterations: Maximum number of tool calling iterations
            **generation_kwargs: Additional generation parameters (temperature, etc.)

        Returns:
            Agent's final response
        """
        import time
        start_time = time.time()

        self.logger.info(f"▶ Starting agent execution")
        self.logger.debug(f"📝 User prompt: {prompt}")

        # Add user message
        self.messages.append(Message(role="user", content=prompt))

        # Add system message if this is the first interaction
        if len(self.messages) == 1:
            self.messages.insert(0, Message(role="system", content=self.system_prompt))
            self.logger.debug(f"📋 System prompt: {self.system_prompt[:200]}...")

        # Prepare tools for provider
        tools_list = None
        if self.provider.supports_tools() and len(self.tools) > 0:
            tools_list = self._format_tools_for_provider()
            tool_names = [t.name for t in self.tools.get_all()]
            self.logger.info(f"🔧 Available tools: {', '.join(tool_names)}")
            self.logger.debug(f"📊 Tools config: {len(tools_list)} tools registered")

        # Iterative execution loop
        iteration = 0
        while iteration < max_iterations:
            self.logger.info(f"🔄 Iteration {iteration + 1}/{max_iterations}")
            # Get completion from provider
            self.logger.debug(f"📤 Sending {len(self.messages)} messages to provider")
            response = self.provider.complete(
                messages=self.messages,
                tools=tools_list,
                **generation_kwargs,
            )
            self.logger.debug(f"📥 Provider response received")

            # If no tool calls, we're done
            if not response.tool_calls:
                if response.content:
                    self.logger.info(f"✓ Execution completed in {time.time() - start_time:.2f}s")
                    self.logger.debug(f"💬 Final response: {response.content[:200]}...")
                    self.messages.append(
                        Message(role="assistant", content=response.content)
                    )
                    return response.content
                else:
                    # No content and no tool calls - something went wrong
                    self.logger.warning("⚠️ No response generated")
                    return "No response generated"

            # Handle tool calls
            self.logger.debug(f"🧠 Assistant reasoning: {response.content}")
            self.messages.append(
                Message(
                    role="assistant",
                    content=response.content or "Using tools...",
                )
            )

            for tool_call in response.tool_calls:
                tool = self.tools.get(tool_call.name)
                if tool is None:
                    self.logger.error(f"❌ Tool not found: {tool_call.name}")
                    tool_result = f"Error: Tool '{tool_call.name}' not found"
                else:
                    # Log tool call
                    args_str = ", ".join(f"{k}={repr(v)[:50]}" for k, v in tool_call.arguments.items())
                    self.logger.info(f"🔧 Tool call: {tool_call.name}({args_str})")
                    self.logger.debug(f"📊 Full arguments: {tool_call.arguments}")

                    try:
                        tool_result = tool(**tool_call.arguments)
                        result_preview = str(tool_result)[:100]
                        self.logger.info(f"✅ Tool result: {len(str(tool_result))} characters")
                        self.logger.debug(f"📝 Result preview: {result_preview}...")
                    except Exception as e:
                        self.logger.error(f"⚠️ Tool error: {type(e).__name__}: {str(e)}")
                        if self.debug:
                            import traceback
                            self.logger.debug(f"🔍 Stack trace:\n{traceback.format_exc()}")
                        tool_result = f"Error executing tool: {str(e)}"

                # Add tool result to messages
                self.messages.append(
                    Message(
                        role="user",
                        content=f"Tool '{tool_call.name}' result: {tool_result}",
                    )
                )

            iteration += 1

        self.logger.warning(f"⚠️ Max iterations ({max_iterations}) reached without final answer")
        return "Max iterations reached without final answer"

    async def arun(
        self,
        prompt: str,
        max_iterations: int = 10,
        **generation_kwargs: Any,
    ) -> str:
        """Async version of run.

        Args:
            prompt: User prompt/question
            max_iterations: Maximum number of tool calling iterations
            **generation_kwargs: Additional generation parameters

        Returns:
            Agent's final response
        """
        import time
        start_time = time.time()

        self.logger.info(f"▶ Starting async agent execution")
        self.logger.debug(f"📝 User prompt: {prompt}")

        # Add user message
        self.messages.append(Message(role="user", content=prompt))

        # Add system message if this is the first interaction
        if len(self.messages) == 1:
            self.messages.insert(0, Message(role="system", content=self.system_prompt))
            self.logger.debug(f"📋 System prompt: {self.system_prompt[:200]}...")

        # Prepare tools for provider
        tools_list = None
        if self.provider.supports_tools() and len(self.tools) > 0:
            tools_list = self._format_tools_for_provider()
            tool_names = [t.name for t in self.tools.get_all()]
            self.logger.info(f"🔧 Available tools: {', '.join(tool_names)}")
            self.logger.debug(f"📊 Tools config: {len(tools_list)} tools registered")

        # Iterative execution loop
        iteration = 0
        while iteration < max_iterations:
            self.logger.info(f"🔄 Iteration {iteration + 1}/{max_iterations}")
            # Get completion from provider
            self.logger.debug(f"📤 Sending {len(self.messages)} messages to provider")
            response = await self.provider.acomplete(
                messages=self.messages,
                tools=tools_list,
                **generation_kwargs,
            )
            self.logger.debug(f"📥 Provider response received")

            # If no tool calls, we're done
            if not response.tool_calls:
                if response.content:
                    self.logger.info(f"✓ Async execution completed in {time.time() - start_time:.2f}s")
                    self.logger.debug(f"💬 Final response: {response.content[:200]}...")
                    self.messages.append(
                        Message(role="assistant", content=response.content)
                    )
                    return response.content
                else:
                    self.logger.warning("⚠️ No response generated")
                    return "No response generated"

            # Handle tool calls
            self.logger.debug(f"🧠 Assistant reasoning: {response.content}")
            self.messages.append(
                Message(
                    role="assistant",
                    content=response.content or "Using tools...",
                )
            )

            for tool_call in response.tool_calls:
                tool = self.tools.get(tool_call.name)
                if tool is None:
                    self.logger.error(f"❌ Tool not found: {tool_call.name}")
                    tool_result = f"Error: Tool '{tool_call.name}' not found"
                else:
                    # Log tool call
                    args_str = ", ".join(f"{k}={repr(v)[:50]}" for k, v in tool_call.arguments.items())
                    self.logger.info(f"🔧 Tool call: {tool_call.name}({args_str})")
                    self.logger.debug(f"📊 Full arguments: {tool_call.arguments}")

                    try:
                        tool_result = tool(**tool_call.arguments)
                        result_preview = str(tool_result)[:100]
                        self.logger.info(f"✅ Tool result: {len(str(tool_result))} characters")
                        self.logger.debug(f"📝 Result preview: {result_preview}...")
                    except Exception as e:
                        self.logger.error(f"⚠️ Tool error: {type(e).__name__}: {str(e)}")
                        if self.debug:
                            import traceback
                            self.logger.debug(f"🔍 Stack trace:\n{traceback.format_exc()}")
                        tool_result = f"Error executing tool: {str(e)}"

                # Add tool result to messages
                self.messages.append(
                    Message(
                        role="user",
                        content=f"Tool '{tool_call.name}' result: {tool_result}",
                    )
                )

            iteration += 1

        self.logger.warning(f"⚠️ Max iterations ({max_iterations}) reached without final answer")
        return "Max iterations reached without final answer"

    def reset(self) -> None:
        """Reset the agent's conversation history."""
        self.messages.clear()

    def _format_tools_for_provider(self) -> list[dict[str, Any]]:
        """Format tools for the current provider.

        Returns:
            List of tools in provider-specific format
        """
        all_tools = self.tools.get_all()

        # Determine format based on provider type
        provider_type = type(self.provider).__name__.lower()

        if "anthropic" in provider_type:
            return [tool.to_anthropic_format() for tool in all_tools]
        else:
            # Default to OpenAI format (most common)
            return [tool.to_openai_format() for tool in all_tools]
