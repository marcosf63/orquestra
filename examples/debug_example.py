"""Example demonstrating debug mode for detailed troubleshooting."""

from dotenv import load_dotenv

from orquestra import ReactAgent

# Load environment variables from .env file
load_dotenv()


def main():
    """Run agent with debug logging enabled."""
    print("🎼 Orquestra - Debug Mode Demo")
    print("=" * 60)
    print("\nThis example shows debug logging for detailed troubleshooting.\n")

    # Create agent with debug=True
    agent = ReactAgent(
        name="MathHelper",
        description="A helpful assistant for mathematical calculations",
        provider="gpt-4o-mini",
        debug=True,  # Enable debug logging (includes verbose)
    )

    # Add custom calculation tool
    @agent.tool()
    def calculate(expression: str) -> float:
        """Evaluate a mathematical expression safely.

        Args:
            expression: Mathematical expression to evaluate (e.g., "2 + 2")

        Returns:
            Result of the calculation
        """
        import ast
        import operator

        # Safe operators
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
        }

        def eval_expr(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.BinOp):
                return operators[type(node.op)](
                    eval_expr(node.left), eval_expr(node.right)
                )
            elif isinstance(node, ast.UnaryOp):
                return operators[type(node.op)](eval_expr(node.operand))
            else:
                raise ValueError(f"Unsupported operation: {node}")

        try:
            tree = ast.parse(expression, mode="eval")
            return eval_expr(tree.body)
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")

    print("\n" + "=" * 60)
    print("DEBUG MODE - You'll see:")
    print("  All VERBOSE logs plus:")
    print("  📤 Messages sent to provider")
    print("  📥 Provider responses")
    print("  🧠 Assistant reasoning")
    print("  📊 Full tool arguments")
    print("  📝 Result previews")
    print("  🔍 Stack traces on errors")
    print("  ⏰ Timestamps for each log")
    print("=" * 60 + "\n")

    # Run query
    answer = agent.run(
        "Calculate the result of (15 + 27) * 3, then subtract 10. "
        "Show me the step-by-step process."
    )

    print("\n" + "=" * 60)
    print("📝 Final Answer:")
    print("=" * 60)
    print(answer)

    print("\n" + "=" * 60)
    print("Debug Info:")
    print(f"  Agent name: {agent.name}")
    print(f"  Current date: {agent.current_date}")
    print(f"  Current datetime: {agent.current_datetime}")
    print(f"  Total messages in history: {len(agent.messages)}")
    print(f"  Registered tools: {', '.join(t.name for t in agent.tools.get_all())}")
    print("=" * 60)


if __name__ == "__main__":
    main()
