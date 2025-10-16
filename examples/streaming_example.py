"""Example demonstrating streaming responses from agents.

This example shows how to use streaming to get real-time responses
from AI agents, similar to ChatGPT-style interfaces.

Requirements:
    - OpenAI or Anthropic API key set in environment
    - Run: export OPENAI_API_KEY="your-key" or export ANTHROPIC_API_KEY="your-key"

Usage:
    uv run python examples/streaming_example.py
"""

import sys
from orquestra import ReactAgent


def basic_streaming_example():
    """Basic streaming example with GPT-4."""
    print("=" * 60)
    print("Basic Streaming Example")
    print("=" * 60)

    # Create an agent
    agent = ReactAgent(
        name="StreamingAssistant",
        description="A helpful AI assistant with streaming responses",
        provider="gpt-4o-mini",
    )

    # Stream a simple response
    prompt = "Write a short poem about AI and humanity in 4 lines."
    print(f"\nUser: {prompt}\n")
    print("Assistant: ", end="", flush=True)

    for chunk in agent.stream(prompt):
        print(chunk, end="", flush=True)

    print("\n")


def storytelling_streaming():
    """Example of streaming a longer story."""
    print("=" * 60)
    print("Storytelling with Streaming")
    print("=" * 60)

    agent = ReactAgent(
        name="Storyteller",
        description="A creative storyteller",
        provider="gpt-4o-mini",
    )

    prompt = "Tell me a very short sci-fi story about a robot discovering emotions (max 3 paragraphs)."
    print(f"\nUser: {prompt}\n")
    print("Assistant:\n")

    for chunk in agent.stream(prompt):
        print(chunk, end="", flush=True)
        sys.stdout.flush()

    print("\n")


def async_streaming_example():
    """Async streaming example."""
    import asyncio

    async def run_async():
        print("=" * 60)
        print("Async Streaming Example")
        print("=" * 60)

        agent = ReactAgent(
            name="AsyncAssistant",
            description="An async streaming assistant",
            provider="gpt-4o-mini",
        )

        prompt = "Explain quantum computing in 2 simple sentences."
        print(f"\nUser: {prompt}\n")
        print("Assistant: ", end="", flush=True)

        async for chunk in agent.astream(prompt):
            print(chunk, end="", flush=True)
            await asyncio.sleep(0.01)  # Small delay for visual effect

        print("\n")

    asyncio.run(run_async())


def claude_streaming_example():
    """Streaming with Claude (Anthropic)."""
    try:
        print("=" * 60)
        print("Claude Streaming Example")
        print("=" * 60)

        agent = ReactAgent(
            name="ClaudeAssistant",
            description="A helpful Claude assistant",
            provider="claude-3-5-sonnet-20241022",
        )

        prompt = "What are the three most important principles of good software design? Be concise."
        print(f"\nUser: {prompt}\n")
        print("Assistant: ", end="", flush=True)

        for chunk in agent.stream(prompt):
            print(chunk, end="", flush=True)

        print("\n")

    except Exception as e:
        print(f"Claude example skipped: {e}")
        print("Make sure ANTHROPIC_API_KEY is set to run this example.\n")


def main():
    """Run all streaming examples."""
    print("\n🌊 ORQUESTRA STREAMING EXAMPLES 🌊\n")

    try:
        # Run basic examples
        basic_streaming_example()
        storytelling_streaming()

        # Run async example
        async_streaming_example()

        # Try Claude if available
        claude_streaming_example()

        print("=" * 60)
        print("✓ All streaming examples completed!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nStopped by user.")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure you have set your API key:")
        print("  export OPENAI_API_KEY='your-key'")
        print("  or")
        print("  export ANTHROPIC_API_KEY='your-key'")


if __name__ == "__main__":
    main()
