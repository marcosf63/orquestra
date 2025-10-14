"""Example showing custom tool creation with decorators."""

from dotenv import load_dotenv

from orquestra import ReactAgent

# Load environment variables from .env file
load_dotenv()


def main():
    """Demonstrate custom tools with FastAPI-style decorators."""
    # Set your API key in .env file:
    # OPENAI_API_KEY=your-key-here

    # Create agent
    agent = ReactAgent(
        name="MathAssistant",
        description="An assistant that helps with math problems",
        provider="gpt-4o-mini",
    )

    # Add custom tools using decorators
    @agent.tool()
    def fibonacci(n: int) -> int:
        """Calculate the nth Fibonacci number.

        Args:
            n: Position in Fibonacci sequence (must be positive)

        Returns:
            The nth Fibonacci number
        """
        if n <= 0:
            return 0
        elif n == 1:
            return 1

        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    @agent.tool()
    def is_prime(n: int) -> bool:
        """Check if a number is prime.

        Args:
            n: Number to check

        Returns:
            True if prime, False otherwise
        """
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    @agent.tool()
    def factorial(n: int) -> int:
        """Calculate factorial of a number.

        Args:
            n: Number to calculate factorial (must be non-negative)

        Returns:
            n! (factorial of n)
        """
        if n < 0:
            raise ValueError("Factorial not defined for negative numbers")
        if n == 0 or n == 1:
            return 1

        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    # Ask questions
    print("🎼 Orquestra Custom Tools Demo\n")

    questions = [
        "What is the 10th Fibonacci number?",
        "Is 17 a prime number?",
        "Calculate the factorial of 5",
    ]

    for question in questions:
        print(f"\n❓ Question: {question}")
        answer = agent.run(question)
        print(f"📝 Answer: {answer}")

        # Reset agent for next question
        agent.reset()


if __name__ == "__main__":
    main()
