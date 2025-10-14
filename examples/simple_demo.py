"""Simple demo without external dependencies."""

from dotenv import load_dotenv

from orquestra import ReactAgent

# Load environment variables from .env file
load_dotenv()


def main():
    """Run a simple agent demo with basic math tools."""
    print("🎼 Orquestra Simple Demo\n")

    # Create agent
    agent = ReactAgent(
        name="MathAssistant",
        description="A helpful math and calculation assistant",
        provider="gpt-4o-mini",
    )

    # Add custom tools using decorators
    @agent.tool()
    def add(a: float, b: float) -> float:
        """Add two numbers together.

        Args:
            a: First number
            b: Second number

        Returns:
            Sum of a and b
        """
        return a + b

    @agent.tool()
    def multiply(a: float, b: float) -> float:
        """Multiply two numbers.

        Args:
            a: First number
            b: Second number

        Returns:
            Product of a and b
        """
        return a * b

    @agent.tool()
    def power(base: float, exponent: float) -> float:
        """Raise a number to a power.

        Args:
            base: The base number
            exponent: The exponent

        Returns:
            base raised to the power of exponent
        """
        return base ** exponent

    # Test queries
    queries = [
        "What is 25 + 17?",
        "Calculate 12 times 8",
        "What is 2 to the power of 10?",
        "If I have 15 apples and buy 23 more, then multiply by 3, how many do I have?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print('='*60)

        try:
            answer = agent.run(query)
            print(f"\n✓ Answer: {answer}")
        except Exception as e:
            print(f"\n✗ Error: {e}")

        # Reset for next query
        agent.reset()
        print()


if __name__ == "__main__":
    main()
