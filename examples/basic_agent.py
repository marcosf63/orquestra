"""Basic agent example with web search."""

import os

from orquestra import ReactAgent, web_search


def main():
    """Run a basic agent with web search capability."""
    # Set your API key in environment or .env file
    # export OPENAI_API_KEY="your-key"

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
