"""Unit tests for memory systems."""

import pytest

from orquestra import ChatMemory, KnowledgeMemory, Message, MemoryEntry


class TestMemoryEntry:
    """Tests for MemoryEntry class."""

    def test_create_memory_entry(self):
        """Test creating a memory entry."""
        entry = MemoryEntry(content="Test content")

        assert entry.content == "Test content"
        assert entry.metadata == {}
        assert entry.timestamp is None

    def test_memory_entry_with_metadata(self):
        """Test creating memory entry with metadata."""
        entry = MemoryEntry(
            content="Test content",
            metadata={"source": "test", "priority": 1},
            timestamp=1234567890.0,
        )

        assert entry.content == "Test content"
        assert entry.metadata == {"source": "test", "priority": 1}
        assert entry.timestamp == 1234567890.0


class TestChatMemory:
    """Tests for ChatMemory class."""

    def test_create_chat_memory(self):
        """Test creating a chat memory instance."""
        memory = ChatMemory()

        assert memory.max_messages is None
        assert memory.storage is None
        assert memory.session_id is not None
        assert isinstance(memory.session_id, str)

    def test_chat_memory_with_max_messages(self):
        """Test creating chat memory with max messages limit."""
        memory = ChatMemory(max_messages=10)

        assert memory.max_messages == 10

    def test_add_message(self):
        """Test adding a message to chat memory."""
        memory = ChatMemory()

        memory.add_message("user", "Hello")
        messages = memory.get_messages()

        assert len(messages) == 1
        assert messages[0].role == "user"
        assert messages[0].content == "Hello"

    def test_add_multiple_messages(self):
        """Test adding multiple messages."""
        memory = ChatMemory()

        memory.add_message("user", "Hello")
        memory.add_message("assistant", "Hi there!")
        memory.add_message("user", "How are you?")

        messages = memory.get_messages()
        assert len(messages) == 3
        assert messages[0].content == "Hello"
        assert messages[1].content == "Hi there!"
        assert messages[2].content == "How are you?"

    def test_max_messages_limiting(self):
        """Test that max_messages limit is enforced (sliding window)."""
        memory = ChatMemory(max_messages=3)

        memory.add_message("user", "msg1")
        memory.add_message("assistant", "msg2")
        memory.add_message("user", "msg3")
        memory.add_message("assistant", "msg4")  # Should remove msg1
        memory.add_message("user", "msg5")  # Should remove msg2

        messages = memory.get_messages()
        assert len(messages) == 3
        assert messages[0].content == "msg3"
        assert messages[1].content == "msg4"
        assert messages[2].content == "msg5"

    def test_get_messages_empty(self):
        """Test getting messages from empty memory."""
        memory = ChatMemory()

        messages = memory.get_messages()
        assert messages == []

    def test_clear_memory(self):
        """Test clearing chat memory."""
        memory = ChatMemory()

        memory.add_message("user", "Hello")
        memory.add_message("assistant", "Hi!")
        assert len(memory.get_messages()) == 2

        memory.clear()
        assert len(memory.get_messages()) == 0

    def test_add_entry(self):
        """Test adding a MemoryEntry."""
        memory = ChatMemory()

        entry = MemoryEntry(content="Test entry")
        memory.add(entry)

        # ChatMemory should convert MemoryEntry to Message
        messages = memory.get_messages()
        assert len(messages) == 1

    def test_add_string_entry(self):
        """Test adding a string as entry."""
        memory = ChatMemory()

        memory.add("Simple string entry")

        messages = memory.get_messages()
        assert len(messages) == 1

    def test_search_chat_memory(self):
        """Test searching chat memory."""
        memory = ChatMemory()

        memory.add_message("user", "I love Python programming")
        memory.add_message("assistant", "Python is great!")
        memory.add_message("user", "Tell me about JavaScript")

        # Search for messages containing "Python"
        results = memory.search("Python", limit=2)

        assert len(results) <= 2
        assert all(isinstance(entry, MemoryEntry) for entry in results)
        assert len(results) == 2  # Should find both messages with "Python"
        assert "Python" in results[0].content or "python" in results[0].content.lower()


class TestKnowledgeMemory:
    """Tests for KnowledgeMemory class."""

    def test_create_knowledge_memory(self):
        """Test creating a knowledge memory instance."""
        memory = KnowledgeMemory()

        assert memory is not None

    def test_add_knowledge(self):
        """Test adding knowledge entries."""
        memory = KnowledgeMemory()

        memory.add("Python is a programming language")
        memory.add("JavaScript is used for web development")

        # Basic test - just ensure no errors
        assert True

    def test_search_knowledge(self):
        """Test searching knowledge memory."""
        memory = KnowledgeMemory()

        memory.add("Python is a programming language")
        memory.add("JavaScript is used for web development")
        memory.add("Rust is a systems programming language")

        # Search for "programming"
        results = memory.search("programming language", limit=2)

        assert len(results) <= 2
        assert all(isinstance(entry, MemoryEntry) for entry in results)

    def test_clear_knowledge_memory(self):
        """Test clearing knowledge memory."""
        memory = KnowledgeMemory()

        memory.add("Entry 1")
        memory.add("Entry 2")

        memory.clear()

        # After clearing, search should return empty
        results = memory.search("Entry", limit=10)
        assert len(results) == 0


class TestChatMemoryWithStorage:
    """Tests for ChatMemory with storage backend."""

    def test_chat_memory_with_storage_initialization(self, temp_db):
        """Test that ChatMemory can be initialized with storage."""
        from orquestra import SQLiteStorage

        storage = SQLiteStorage(temp_db)
        memory = ChatMemory(storage=storage, session_id="test_session")

        assert memory.storage == storage
        assert memory.session_id == "test_session"

    def test_messages_persist_across_instances(self, temp_db):
        """Test that messages persist when using storage."""
        from orquestra import SQLiteStorage

        session_id = "persistent_session"

        # First instance - add messages
        storage1 = SQLiteStorage(temp_db)
        memory1 = ChatMemory(storage=storage1, session_id=session_id)
        memory1.add_message("user", "Hello")
        memory1.add_message("assistant", "Hi there!")

        # Second instance - should load existing messages
        storage2 = SQLiteStorage(temp_db)
        memory2 = ChatMemory(storage=storage2, session_id=session_id)

        messages = memory2.get_messages()
        assert len(messages) == 2
        assert messages[0].content == "Hello"
        assert messages[1].content == "Hi there!"

    def test_different_sessions_dont_mix(self, temp_db):
        """Test that different sessions have separate message histories."""
        from orquestra import SQLiteStorage

        storage = SQLiteStorage(temp_db)

        # Session 1
        memory1 = ChatMemory(storage=storage, session_id="session1")
        memory1.add_message("user", "Session 1 message")

        # Session 2
        memory2 = ChatMemory(storage=storage, session_id="session2")
        memory2.add_message("user", "Session 2 message")

        # Verify separation
        assert len(memory1.get_messages()) == 1
        assert len(memory2.get_messages()) == 1
        assert memory1.get_messages()[0].content == "Session 1 message"
        assert memory2.get_messages()[0].content == "Session 2 message"
