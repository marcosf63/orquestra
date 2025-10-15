"""Example demonstrating verbose mode for tracking agent execution."""

from dotenv import load_dotenv

from orquestra import ReactAgent, web_search

# Load environment variables from .env file
load_dotenv()


def main():
    """Run agent with verbose logging enabled."""
    print("🎼 Orquestra - Verbose Mode Demo")
    print("=" * 60)
    print("\nThis example shows verbose logging to track agent execution.\n")

    # Create agent with verbose=True
    agent = ReactAgent(
        name="NewsResearcher",
        description="A research assistant that finds current news",
        provider="gpt-4o-mini",
        verbose=True,  # Enable verbose logging
    )

    # Add web search tool
    agent.add_tool(web_search)

    print("\n" + "=" * 60)
    print("VERBOSE MODE - You'll see:")
    print("  ▶ Execution start/end")
    print("  🔄 Iteration numbers")
    print("  🔧 Tool calls with arguments")
    print("  ✅ Tool results (character count)")
    print("=" * 60 + "\n")

    # Run query
    answer = agent.run("What's happening in technology today? Search for recent news.")

    print("\n" + "=" * 60)
    print("📝 Final Answer:")
    print("=" * 60)
    print(answer)


if __name__ == "__main__":
    main()
