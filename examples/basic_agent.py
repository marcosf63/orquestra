"""Basic agent example with web search."""

from dotenv import load_dotenv

from orquestra import ReactAgent, web_search
from orquestra.tools import MissingDependencyError

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a basic agent with web search capability."""
    # Set your API key in .env file:
    # OPENAI_API_KEY=your-key-here

    print("🎼 Orquestra Agent Demo\n")

    # Create agent
    agent = ReactAgent(
        name="WebResearcher",
        description="A helpful research assistant with web access",
        provider="gpt-4o-mini",  # or "claude-3-5-sonnet-20241022", "gemini-pro", etc.
    )

    # Add web search tool
    agent.add_tool(web_search)

    # Ask a question about current events
    print("Question: What are the latest news about AI and technology today?\n")

    try:
        answer = agent.run(
            "What are the latest news about AI and technology today? Search the web and provide a summary."
        )

        print("\n📝 Answer:")
        print(answer)
    except MissingDependencyError as e:
        print(f"\n❌ {e}\n")
        print("For a simpler example without dependencies, try:")
        print("  python examples/simple_demo.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you have set OPENAI_API_KEY in your .env file")
        print("2. Check your internet connection")
        print("\nFor a simpler example without web search, try:")
        print("  python examples/simple_demo.py")


if __name__ == "__main__":
    main()
