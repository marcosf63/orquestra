"""Simple MCP client for connecting to external MCP servers."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from .types import JSONRPCRequest, JSONRPCResponse, Tool, ToolCallResult

logger = logging.getLogger(__name__)


class MCPClient:
    """Minimal MCP client for connecting to external servers.

    This client connects to MCP servers via stdio subprocess and allows
    discovering and calling their tools.

    Example:
        ```python
        async with MCPClient(
            command=["python", "server.py"]
        ) as client:
            tools = await client.list_tools()
            result = await client.call_tool("search", {"query": "python"})
        ```
    """

    def __init__(self, command: list[str], name: str | None = None) -> None:
        """Initialize MCP client.

        Args:
            command: Command to launch MCP server subprocess
            name: Optional client name for identification
        """
        self.command = command
        self.name = name or "orquestra-client"
        self._process: asyncio.subprocess.Process | None = None
        self._request_id = 0
        self._pending: dict[int, asyncio.Future] = {}
        self._receive_task: asyncio.Task | None = None
        self._initialized = False

    async def __aenter__(self) -> MCPClient:
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def connect(self) -> None:
        """Connect to the MCP server."""
        # Start subprocess
        self._process = await asyncio.create_subprocess_exec(
            *self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        if not self._process.stdout or not self._process.stdin:
            raise RuntimeError("Failed to create subprocess pipes")

        # Start receiving messages
        self._receive_task = asyncio.create_task(self._receive_loop())

        # Initialize connection
        await self._initialize()

    async def close(self) -> None:
        """Close connection to server."""
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        if self._process:
            try:
                self._process.terminate()
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self._process.kill()
                await self._process.wait()

    async def _initialize(self) -> None:
        """Initialize the MCP connection."""
        result = await self._send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": self.name, "version": "1.0.0"},
            },
        )

        # Send initialized notification
        await self._send_notification("notifications/initialized")
        self._initialized = True
        logger.debug(f"Connected to MCP server: {result.get('serverInfo', {}).get('name')}")

    async def list_tools(self) -> list[Tool]:
        """List available tools from the server.

        Returns:
            List of Tool definitions
        """
        result = await self._send_request("tools/list")
        tools_data = result.get("tools", [])
        return [Tool(**tool) for tool in tools_data]

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> ToolCallResult:
        """Call a tool on the server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result
        """
        result = await self._send_request(
            "tools/call", {"name": name, "arguments": arguments or {}}
        )
        return ToolCallResult(**result)

    async def _send_request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send JSON-RPC request and wait for response."""
        if not self._process or not self._process.stdin:
            raise RuntimeError("Not connected to server")

        self._request_id += 1
        request_id = self._request_id

        request = JSONRPCRequest(id=request_id, method=method, params=params)

        # Create future for response
        future: asyncio.Future[dict[str, Any]] = asyncio.Future()
        self._pending[request_id] = future

        try:
            # Send request
            line = request.model_dump_json(by_alias=True, exclude_none=True) + "\n"
            self._process.stdin.write(line.encode("utf-8"))
            await self._process.stdin.drain()

            # Wait for response
            result = await future
            return result

        finally:
            self._pending.pop(request_id, None)

    async def _send_notification(self, method: str, params: dict[str, Any] | None = None) -> None:
        """Send JSON-RPC notification (no response expected)."""
        if not self._process or not self._process.stdin:
            raise RuntimeError("Not connected to server")

        notification = {"jsonrpc": "2.0", "method": method}
        if params:
            notification["params"] = params

        line = json.dumps(notification) + "\n"
        self._process.stdin.write(line.encode("utf-8"))
        await self._process.stdin.drain()

    async def _receive_loop(self) -> None:
        """Background task to receive messages from server."""
        if not self._process or not self._process.stdout:
            return

        try:
            while True:
                line = await self._process.stdout.readline()
                if not line:
                    break

                try:
                    message = json.loads(line.decode("utf-8").strip())
                    await self._handle_message(message)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {e}")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in receive loop: {e}")

    async def _handle_message(self, message: dict[str, Any]) -> None:
        """Handle received message from server."""
        if "id" in message and message["id"] in self._pending:
            request_id = message["id"]
            future = self._pending[request_id]

            if "error" in message:
                error = message["error"]
                future.set_exception(
                    RuntimeError(f"MCP Error: {error.get('message', 'Unknown error')}")
                )
            elif "result" in message:
                future.set_result(message["result"])
            else:
                future.set_exception(RuntimeError("Invalid response"))
