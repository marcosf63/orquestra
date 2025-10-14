"""Example demonstrating memory systems."""

from orquestra import HybridMemory, ReactAgent


def main():
    """Demonstrate hybrid memory with chat and knowledge."""
    # Create memory system
    memory = HybridMemory(max_chat_messages=10)

    # Add knowledge to the knowledge base
    print("🎼 Orquestra Memory System Demo\n")
    print("📚 Adding knowledge to the knowledge base...\n")

    knowledge_items = [
        "Python 3.13 was released in October 2024",
        "FastAPI is a modern web framework for building APIs with Python",
        "Pydantic v2 provides data validation using type hints",
        "Async/await enables concurrent programming in Python",
        "Type hints improve code quality and IDE support",
    ]

    for item in knowledge_items:
        memory.add_knowledge(item, metadata={"topic": "python"})
        print(f"  ✓ {item}")

    # Simulate conversation
    print("\n💬 Simulating conversation...\n")

    conversation = [
        ("user", "Hello! I'd like to learn about Python."),
        ("assistant", "Hello! I'd be happy to help you learn about Python."),
        ("user", "What's new in Python 3.13?"),
        (
            "assistant",
            "Python 3.13 was released in October 2024 with several improvements.",
        ),
        ("user", "Tell me about FastAPI"),
        (
            "assistant",
            "FastAPI is a modern, fast web framework for building APIs with Python.",
        ),
    ]

    for role, content in conversation:
        memory.add_message(role, content)
        emoji = "👤" if role == "user" else "🤖"
        print(f"{emoji} {role}: {content}")

    # Search knowledge
    print("\n🔍 Searching knowledge base...\n")

    queries = ["Python 3.13", "web framework", "type hints"]

    for query in queries:
        print(f"Query: '{query}'")
        results = memory.search_knowledge(query, limit=2)
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.content}")
        print()

    # Get context with knowledge
    print("📖 Getting conversation context with knowledge...\n")
    context = memory.get_context(include_knowledge=True, knowledge_query="Python")

    print(f"Context includes {len(context)} messages:")
    for msg in context:
        if msg.role == "system":
            print(f"  [SYSTEM] Knowledge injected")
        else:
            print(f"  [{msg.role.upper()}] {msg.content[:50]}...")


if __name__ == "__main__":
    main()
