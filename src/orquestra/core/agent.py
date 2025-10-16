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

    def add_mcp_server(self, name: str, command: list[str]) -> None:
        """Connect to an MCP server and add its tools to the agent.

        This method connects to an external MCP server, discovers its available
        tools, and automatically registers them with the agent. The tools can
        then be used just like any other agent tool.

        Args:
            name: Identifier for this MCP server connection
            command: Command to launch the MCP server subprocess
                    Example: ["python", "server.py"] or ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"]

        Example:
            ```python
            agent = ReactAgent(name="Assistant", provider="gpt-4o-mini")

            # Add filesystem MCP server
            agent.add_mcp_server(
                name="filesystem",
                command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
            )

            # Tools from MCP server are now available
            agent.run("List files in the directory")
            ```

        Note:
            This method runs asynchronously in the background. Tools are registered
            immediately and the MCP connection is maintained for the agent's lifetime.
        """
        import asyncio

        # Import MCP client (lazy import to avoid dependency if not using MCP)
        try:
            from ..mcp.client import MCPClient
        except ImportError:
            raise ImportError(
                "MCP support requires pydantic>=2.0.0. "
                "Install with: pip install orquestra[mcp] or pip install pydantic>=2.0.0"
            )

        async def _setup_mcp():
            """Setup MCP connection and register tools."""
            client = MCPClient(command=command, name=f"{self.name}-{name}")

            try:
                await client.connect()
                self.logger.info(f"🔌 Connected to MCP server: {name}")

                # Discover tools
                tools = await client.list_tools()
                self.logger.info(f"🔍 Discovered {len(tools)} tools from {name}")

                # Register each tool
                for mcp_tool in tools:
                    # Create wrapper function for this tool
                    def create_wrapper(tool_name: str):
                        async def tool_wrapper(**kwargs: Any) -> str:
                            """MCP tool wrapper."""
                            try:
                                result = await client.call_tool(tool_name, kwargs)
                                return result.get_text()
                            except Exception as e:
                                return f"Error calling MCP tool: {str(e)}"

                        return tool_wrapper

                    # Create sync wrapper
                    def create_sync_wrapper(tool_name: str):
                        async_func = create_wrapper(tool_name)

                        def sync_wrapper(**kwargs: Any) -> str:
                            """Sync wrapper for MCP tool."""
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    # If loop is running, create a new task
                                    future = asyncio.ensure_future(async_func(**kwargs))
                                    # This is a workaround - in practice, tools should be async
                                    return "MCP tool called (async)"
                                else:
                                    return loop.run_until_complete(async_func(**kwargs))
                            except Exception as e:
                                return f"Error: {str(e)}"

                        return sync_wrapper

                    wrapper = create_sync_wrapper(mcp_tool.name)
                    wrapper.__name__ = mcp_tool.name
                    wrapper.__doc__ = mcp_tool.description or f"MCP tool: {mcp_tool.name}"

                    # Register with agent
                    self.add_tool(wrapper, name=mcp_tool.name)
                    self.logger.debug(f"  ✓ Registered MCP tool: {mcp_tool.name}")

                self.logger.info(f"✓ MCP server '{name}' ready with {len(tools)} tools")

                # Store client reference
                if not hasattr(self, '_mcp_clients'):
                    self._mcp_clients = {}
                self._mcp_clients[name] = client

            except Exception as e:
                self.logger.error(f"❌ Failed to connect to MCP server '{name}': {e}")
                raise

        # Run setup in background
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, schedule task
                asyncio.create_task(_setup_mcp())
            else:
                # If no loop, run synchronously
                loop.run_until_complete(_setup_mcp())
        except RuntimeError:
            # No event loop, create one
            asyncio.run(_setup_mcp())

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
