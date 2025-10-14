"""Example demonstrating ChatMemory persistence with SQLite."""

from orquestra import ChatMemory, SQLiteStorage


def main():
    """Demonstrate persistent chat memory with SQLite."""
    print("🎼 Orquestra Persistent Memory Demo (SQLite)\n")

    # Create SQLite storage
    storage = SQLiteStorage(db_path="chat_history.db")

    # Create a chat memory with persistence
    session_id = "demo-session-001"
    memory = ChatMemory(
        max_messages=100,
        storage=storage,
        session_id=session_id,
    )

    # Check if we have previous messages
    if len(memory) > 0:
        print(f"📚 Found {len(memory)} existing messages in session '{session_id}'\n")
        print("Previous conversation:")
        for msg in memory.get_messages():
            print(f"  [{msg.role.upper()}] {msg.content}")
        print()
    else:
        print(f"📝 Starting new session: '{session_id}'\n")

    # Add new messages
    print("Adding new messages...\n")

    memory.add_message("user", "Hello! Can you help me with Python?")
    memory.add_message("assistant", "Of course! I'd be happy to help you with Python.")
    memory.add_message("user", "What is a decorator?")
    memory.add_message(
        "assistant",
        "A decorator in Python is a design pattern that allows you to modify "
        "the behavior of a function or class without changing its source code.",
    )

    print("✅ Messages saved to database\n")

    # Display current conversation
    print(f"Current conversation ({len(memory)} messages):\n")
    for msg in memory.get_messages():
        emoji = "👤" if msg.role == "user" else "🤖"
        print(f"{emoji} {msg.role}: {msg.content}")

    print(f"\n📊 Session ID: {session_id}")
    print(f"💾 Database: {storage.db_path}")

    # List all sessions
    sessions = memory.list_sessions()
    print(f"\n🗂️  Available sessions: {', '.join(sessions)}")

    # Close storage
    storage.close()

    print("\n💡 Tip: Run this example again to see messages persist!")


if __name__ == "__main__":
    main()
