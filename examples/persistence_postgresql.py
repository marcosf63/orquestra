"""Example demonstrating ChatMemory persistence with PostgreSQL."""

import os

from dotenv import load_dotenv

from orquestra import ChatMemory, PostgreSQLStorage

# Load environment variables from .env file
load_dotenv()


def main():
    """Demonstrate persistent chat memory with PostgreSQL."""
    print("🎼 Orquestra Persistent Memory Demo (PostgreSQL)\n")

    # Create PostgreSQL storage
    # Option 1: Using individual parameters (from .env)
    storage = PostgreSQLStorage(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "orquestra"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
    )

    # Option 2: Using connection string from .env (alternative)
    # storage = PostgreSQLStorage(
    #     connection_string=os.getenv("POSTGRES_CONNECTION_STRING")
    # )

    # Create a chat memory with persistence
    session_id = "demo-session-pg-001"
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

    # Add new messages with metadata
    print("Adding new messages...\n")

    memory.add_message(
        "user",
        "Hello! Tell me about PostgreSQL.",
        metadata={"source": "web", "priority": "high"},
    )
    memory.add_message(
        "assistant",
        "PostgreSQL is a powerful, open-source relational database system "
        "with over 35 years of active development.",
        metadata={"model": "gpt-4"},
    )
    memory.add_message(
        "user", "What are some key features?", metadata={"source": "web"}
    )
    memory.add_message(
        "assistant",
        "PostgreSQL supports advanced data types, full-text search, JSONB, "
        "and has excellent support for concurrent transactions.",
        metadata={"model": "gpt-4"},
    )

    print("✅ Messages saved to PostgreSQL\n")

    # Display current conversation
    print(f"Current conversation ({len(memory)} messages):\n")
    for msg in memory.get_messages():
        emoji = "👤" if msg.role == "user" else "🤖"
        print(f"{emoji} {msg.role}: {msg.content}")

    print(f"\n📊 Session ID: {session_id}")
    print(f"💾 Database: PostgreSQL at localhost:5432/orquestra")

    # List all sessions
    sessions = memory.list_sessions()
    print(f"\n🗂️  Available sessions: {', '.join(sessions)}")

    # Close storage
    storage.close()

    print("\n💡 Tip: Run this example again to see messages persist!")
    print("📝 Note: Make sure PostgreSQL is running and credentials are correct")


if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("❌ PostgreSQL support not installed.")
        print("Install with: uv add orquestra --optional postgresql")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'orquestra' exists")
        print("  3. Credentials are correct")
