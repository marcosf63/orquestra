"""Example: Using MCP Server Tools in an Orquestra Agent.

This example demonstrates how to connect an Orquestra agent to an external
MCP server and use its tools seamlessly.

Prerequisites:
- Node.js installed (for npx)
- Or any MCP server available

Try with official MCP servers:
- Filesystem: npx -y @modelcontextprotocol/server-filesystem <directory>
- GitHub: npx -y @modelcontextprotocol/server-github
- Brave Search: npx -y @modelcontextprotocol/server-brave-search
"""

from orquestra import ReactAgent

def main():
    """Run the MCP tools example."""
    # Create an Orquestra agent
    agent = ReactAgent(
        name="MCPAssistant",
        description="An AI assistant with access to MCP server tools",
        provider="gpt-4o-mini",  # Requires OPENAI_API_KEY
        verbose=True,  # Show tool calls
    )

    # Example 1: Connect to filesystem MCP server
    print("=" * 60)
    print("Example 1: Filesystem MCP Server")
    print("=" * 60)
    print()

    try:
        # Add filesystem MCP server (exposes file operations)
        agent.add_mcp_server(
            name="filesystem",
            command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        )

        # Now the agent can use filesystem tools
        response = agent.run("List the files in the directory")
        print("\nAgent response:")
        print(response)
        print()

    except Exception as e:
        print(f"Error with filesystem server: {e}")
        print("Make sure Node.js is installed and /tmp directory exists")
        print()

    # Example 2: Using custom Python MCP server
    print("=" * 60)
    print("Example 2: Custom Python MCP Server")
    print("=" * 60)
    print()

    # To use a custom Python MCP server:
    # 1. Create your server (see mcp_server_example.py)
    # 2. Connect to it:
    #
    # agent.add_mcp_server(
    #     name="custom",
    #     command=["python", "examples/mcp_server_example.py"]
    # )
    #
    # response = agent.run("Use the custom tool")

    print("To use custom MCP servers:")
    print("1. Create an MCP server (any language)")
    print("2. Use agent.add_mcp_server(name='...', command=['...'])")
    print("3. Agent automatically discovers and uses the tools")
    print()

    # Example 3: Multiple MCP servers
    print("=" * 60)
    print("Example 3: Multiple MCP Servers")
    print("=" * 60)
    print()

    print("You can connect to multiple MCP servers:")
    print()
    print("  agent.add_mcp_server('filesystem', [...])")
    print("  agent.add_mcp_server('github', [...])")
    print("  agent.add_mcp_server('custom', [...])")
    print()
    print("All tools from all servers become available to the agent!")
    print()


if __name__ == "__main__":
    main()
