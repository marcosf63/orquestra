"""MCP (Model Context Protocol) client integration.

This module provides minimal MCP client functionality to allow Orquestra
agents to use tools from external MCP servers.

Example:
    ```python
    from orquestra import ReactAgent

    agent = ReactAgent(name="Assistant", provider="gpt-4o-mini")

    # Add MCP server tools
    agent.add_mcp_server(
        name="filesystem",
        command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    )

    # Use MCP tools naturally
    agent.run("List files in the directory")
    ```
"""

from .client import MCPClient
from .types import JSONRPCRequest, JSONRPCResponse, Tool, ToolCallResult

__all__ = [
    "MCPClient",
    "Tool",
    "ToolCallResult",
    "JSONRPCRequest",
    "JSONRPCResponse",
]
