"""Base Agent class with FastAPI-style decorators for tool registration."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Generator, TypeVar

from .provider import Message, Provider, ProviderFactory, StreamChunk
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

    def stream(
        self,
        prompt: str,
        max_iterations: int = 10,
        **generation_kwargs: Any,
    ) -> Generator[str, None, None]:
        """Stream the agent's response with a prompt.

        Args:
            prompt: User prompt/question
            max_iterations: Maximum number of tool calling iterations
            **generation_kwargs: Additional generation parameters

        Yields:
            String chunks of the response

        Note:
            Streaming with tool calling may not stream tool execution.
            For best streaming experience, use without tools or with simple queries.
        """
        import time
        start_time = time.time()

        self.logger.info(f"▶ Starting streaming agent execution")
        self.logger.debug(f"📝 User prompt: {prompt}")

        # Check if provider supports streaming
        if not self.provider.supports_streaming():
            self.logger.warning("⚠️ Provider doesn't support streaming, falling back to regular run()")
            result = self.run(prompt, max_iterations, **generation_kwargs)
            yield result
            return

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

        # Iterative execution loop with streaming
        iteration = 0
        full_response = ""

        while iteration < max_iterations:
            self.logger.info(f"🔄 Iteration {iteration + 1}/{max_iterations}")

            # Stream response from provider
            tool_calls_list = []
            chunk_content = ""

            for chunk in self.provider.stream(
                messages=self.messages,
                tools=tools_list,
                **generation_kwargs,
            ):
                if chunk.content:
                    chunk_content += chunk.content
                    full_response += chunk.content
                    yield chunk.content

                # Collect tool calls if present
                if chunk.tool_calls:
                    tool_calls_list.extend(chunk.tool_calls)

            # If no tool calls, we're done
            if not tool_calls_list:
                if chunk_content:
                    self.logger.info(f"✓ Streaming completed in {time.time() - start_time:.2f}s")
                    self.messages.append(
                        Message(role="assistant", content=full_response)
                    )
                    return
                else:
                    self.logger.warning("⚠️ No response generated")
                    return

            # Handle tool calls (non-streaming)
            self.logger.debug(f"🧠 Processing {len(tool_calls_list)} tool calls")
            self.messages.append(
                Message(
                    role="assistant",
                    content=chunk_content or "Using tools...",
                )
            )

            for tool_call in tool_calls_list:
                tool = self.tools.get(tool_call.name)
                if tool is None:
                    self.logger.error(f"❌ Tool not found: {tool_call.name}")
                    tool_result = f"Error: Tool '{tool_call.name}' not found"
                else:
                    args_str = ", ".join(f"{k}={repr(v)[:50]}" for k, v in tool_call.arguments.items())
                    self.logger.info(f"🔧 Tool call: {tool_call.name}({args_str})")

                    try:
                        tool_result = tool(**tool_call.arguments)
                        self.logger.info(f"✅ Tool result: {len(str(tool_result))} characters")
                    except Exception as e:
                        self.logger.error(f"⚠️ Tool error: {type(e).__name__}: {str(e)}")
                        tool_result = f"Error executing tool: {str(e)}"

                # Add tool result to messages
                self.messages.append(
                    Message(
                        role="user",
                        content=f"Tool '{tool_call.name}' result: {tool_result}",
                    )
                )

            iteration += 1

        self.logger.warning(f"⚠️ Max iterations ({max_iterations}) reached")

    async def astream(
        self,
        prompt: str,
        max_iterations: int = 10,
        **generation_kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Async stream the agent's response with a prompt.

        Args:
            prompt: User prompt/question
            max_iterations: Maximum number of tool calling iterations
            **generation_kwargs: Additional generation parameters

        Yields:
            String chunks of the response
        """
        import time
        start_time = time.time()

        self.logger.info(f"▶ Starting async streaming agent execution")
        self.logger.debug(f"📝 User prompt: {prompt}")

        # Check if provider supports streaming
        if not self.provider.supports_streaming():
            self.logger.warning("⚠️ Provider doesn't support streaming, falling back to regular arun()")
            result = await self.arun(prompt, max_iterations, **generation_kwargs)
            yield result
            return

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

        # Iterative execution loop with streaming
        iteration = 0
        full_response = ""

        while iteration < max_iterations:
            self.logger.info(f"🔄 Iteration {iteration + 1}/{max_iterations}")

            # Stream response from provider
            tool_calls_list = []
            chunk_content = ""

            async for chunk in self.provider.astream(
                messages=self.messages,
                tools=tools_list,
                **generation_kwargs,
            ):
                if chunk.content:
                    chunk_content += chunk.content
                    full_response += chunk.content
                    yield chunk.content

                # Collect tool calls if present
                if chunk.tool_calls:
                    tool_calls_list.extend(chunk.tool_calls)

            # If no tool calls, we're done
            if not tool_calls_list:
                if chunk_content:
                    self.logger.info(f"✓ Async streaming completed in {time.time() - start_time:.2f}s")
                    self.messages.append(
                        Message(role="assistant", content=full_response)
                    )
                    return
                else:
                    self.logger.warning("⚠️ No response generated")
                    return

            # Handle tool calls (non-streaming)
            self.logger.debug(f"🧠 Processing {len(tool_calls_list)} tool calls")
            self.messages.append(
                Message(
                    role="assistant",
                    content=chunk_content or "Using tools...",
                )
            )

            for tool_call in tool_calls_list:
                tool = self.tools.get(tool_call.name)
                if tool is None:
                    self.logger.error(f"❌ Tool not found: {tool_call.name}")
                    tool_result = f"Error: Tool '{tool_call.name}' not found"
                else:
                    args_str = ", ".join(f"{k}={repr(v)[:50]}" for k, v in tool_call.arguments.items())
                    self.logger.info(f"🔧 Tool call: {tool_call.name}({args_str})")

                    try:
                        tool_result = tool(**tool_call.arguments)
                        self.logger.info(f"✅ Tool result: {len(str(tool_result))} characters")
                    except Exception as e:
                        self.logger.error(f"⚠️ Tool error: {type(e).__name__}: {str(e)}")
                        tool_result = f"Error executing tool: {str(e)}"

                # Add tool result to messages
                self.messages.append(
                    Message(
                        role="user",
                        content=f"Tool '{tool_call.name}' result: {tool_result}",
                    )
                )

            iteration += 1

        self.logger.warning(f"⚠️ Max iterations ({max_iterations}) reached")

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
                    # Extract parameters from input schema
                    input_schema = mcp_tool.input_schema
                    properties = input_schema.get("properties", {})
                    required = input_schema.get("required", [])

                    # Create wrapper function with proper signature
                    def create_wrapper(tool_name: str, tool_schema: dict):
                        async def tool_wrapper(**kwargs: Any) -> str:
                            """MCP tool wrapper."""
                            try:
                                result = await client.call_tool(tool_name, kwargs)
                                return result.get_text()
                            except Exception as e:
                                return f"Error calling MCP tool: {str(e)}"

                        return tool_wrapper

                    # Create sync wrapper with dynamic parameters
                    def create_sync_wrapper(tool_name: str, params: dict, req_params: list):
                        async_func = create_wrapper(tool_name, params)

                        # Build function signature dynamically
                        import inspect

                        # Create parameter list with defaults
                        sig_params = []
                        for param_name, param_def in params.items():
                            if param_name in req_params:
                                # Required parameter
                                sig_params.append(
                                    inspect.Parameter(
                                        param_name,
                                        inspect.Parameter.KEYWORD_ONLY,
                                        annotation=str,  # Default to str
                                    )
                                )
                            else:
                                # Optional parameter with None default
                                sig_params.append(
                                    inspect.Parameter(
                                        param_name,
                                        inspect.Parameter.KEYWORD_ONLY,
                                        default=None,
                                        annotation=str,
                                    )
                                )

                        def sync_wrapper(**kwargs: Any) -> str:
                            """Sync wrapper for MCP tool."""
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    # Create new event loop for nested async call
                                    import threading
                                    result_container = []

                                    def run_async():
                                        new_loop = asyncio.new_event_loop()
                                        asyncio.set_event_loop(new_loop)
                                        try:
                                            result = new_loop.run_until_complete(async_func(**kwargs))
                                            result_container.append(result)
                                        finally:
                                            new_loop.close()

                                    thread = threading.Thread(target=run_async)
                                    thread.start()
                                    thread.join(timeout=30)

                                    if result_container:
                                        return result_container[0]
                                    return "MCP tool timeout"
                                else:
                                    return loop.run_until_complete(async_func(**kwargs))
                            except Exception as e:
                                return f"Error: {str(e)}"

                        # Set proper signature
                        sync_wrapper.__signature__ = inspect.Signature(sig_params)  # type: ignore
                        return sync_wrapper

                    wrapper = create_sync_wrapper(mcp_tool.name, properties, required)
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
