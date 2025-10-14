"""Basic agent example with web search."""

from dotenv import load_dotenv

from orquestra import ReactAgent, web_search

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a basic agent with web search capability."""
    # Set your API key in .env file:
    # OPENAI_API_KEY=your-key-here

    # Create agent
    agent = ReactAgent(
        name="WebResearcher",
        description="A helpful research assistant with web access",
        provider="gpt-4o-mini",  # or "claude-3-5-sonnet-20241022", "gemini-pro", etc.
    )

    # Add web search tool
    agent.add_tool(web_search)

    # Ask a question
    print("🎼 Orquestra Agent Demo\n")
    print("Question: What are the latest developments in AI agents?\n")

    answer = agent.run(
        "What are the latest developments in AI agents? Provide a summary."
    )

    print("\n📝 Answer:")
    print(answer)


if __name__ == "__main__":
    main()
