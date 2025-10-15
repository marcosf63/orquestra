"""Unit tests for storage backends."""

import pytest

from orquestra import Message, SQLiteStorage


class TestSQLiteStorage:
    """Tests for SQLiteStorage backend."""

    def test_create_sqlite_storage(self, temp_db):
        """Test creating SQLite storage."""
        storage = SQLiteStorage(temp_db)

        assert storage.db_path == temp_db
        assert storage is not None

    def test_save_and_load_message(self, temp_db):
        """Test saving and loading a single message."""
        storage = SQLiteStorage(temp_db)
        session_id = "test_session"

        # Save message
        storage.save_message(session_id, "user", "Hello, world!")

        # Load messages
        loaded = storage.load_messages(session_id)

        assert len(loaded) == 1
        assert loaded[0].role == "user"
        assert loaded[0].content == "Hello, world!"

    def test_save_multiple_messages(self, temp_db):
        """Test saving multiple messages."""
        storage = SQLiteStorage(temp_db)
        session_id = "multi_test"

        storage.save_message(session_id, "user", "Message 1")
        storage.save_message(session_id, "assistant", "Message 2")
        storage.save_message(session_id, "user", "Message 3")

        loaded = storage.load_messages(session_id)

        assert len(loaded) == 3
        assert [m.content for m in loaded] == ["Message 1", "Message 2", "Message 3"]
        assert [m.role for m in loaded] == ["user", "assistant", "user"]

    def test_load_empty_session(self, temp_db):
        """Test loading messages from empty session."""
        storage = SQLiteStorage(temp_db)

        loaded = storage.load_messages("nonexistent_session")

        assert loaded == []

    def test_list_sessions(self, temp_db):
        """Test listing all sessions."""
        storage = SQLiteStorage(temp_db)

        # Create messages in different sessions
        storage.save_message("session1", "user", "S1 msg")
        storage.save_message("session2", "user", "S2 msg")
        storage.save_message("session3", "user", "S3 msg")

        sessions = storage.list_sessions()

        assert len(sessions) == 3
        assert "session1" in sessions
        assert "session2" in sessions
        assert "session3" in sessions

    def test_list_sessions_empty(self, temp_db):
        """Test listing sessions when database is empty."""
        storage = SQLiteStorage(temp_db)

        sessions = storage.list_sessions()

        assert sessions == []

    def test_clear_session(self, temp_db):
        """Test clearing a specific session."""
        storage = SQLiteStorage(temp_db)

        # Add messages to two sessions
        storage.save_message("session1", "user", "S1 msg1")
        storage.save_message("session1", "user", "S1 msg2")
        storage.save_message("session2", "user", "S2 msg1")

        # Clear session1
        storage.delete_messages("session1")

        # Verify session1 is empty but session2 is not
        assert len(storage.load_messages("session1")) == 0
        assert len(storage.load_messages("session2")) == 1

    def test_clear_nonexistent_session(self, temp_db):
        """Test clearing a session that doesn't exist (should not error)."""
        storage = SQLiteStorage(temp_db)

        # Should not raise an error
        storage.delete_messages("nonexistent")

    def test_message_order_preserved(self, temp_db):
        """Test that message order is preserved."""
        storage = SQLiteStorage(temp_db)
        session_id = "order_test"

        # Add messages in specific order
        storage.save_message(session_id, "user", "First")
        storage.save_message(session_id, "assistant", "Second")
        storage.save_message(session_id, "user", "Third")
        storage.save_message(session_id, "assistant", "Fourth")

        loaded = storage.load_messages(session_id)

        assert len(loaded) == 4
        assert loaded[0].content == "First"
        assert loaded[1].content == "Second"
        assert loaded[2].content == "Third"
        assert loaded[3].content == "Fourth"

    def test_multiple_sessions_independent(self, temp_db):
        """Test that multiple sessions are independent."""
        storage = SQLiteStorage(temp_db)

        storage.save_message("session_a", "user", "A1")
        storage.save_message("session_a", "user", "A2")
        storage.save_message("session_b", "user", "B1")

        messages_a = storage.load_messages("session_a")
        messages_b = storage.load_messages("session_b")

        assert len(messages_a) == 2
        assert len(messages_b) == 1
        assert messages_a[0].content == "A1"
        assert messages_b[0].content == "B1"

    def test_persistence_across_instances(self, temp_db):
        """Test that data persists across storage instances."""
        session_id = "persistent"

        # Create first storage instance and save
        storage1 = SQLiteStorage(temp_db)
        storage1.save_message(session_id, "user", "Persistent message")

        # Create second storage instance and load
        storage2 = SQLiteStorage(temp_db)
        loaded = storage2.load_messages(session_id)

        assert len(loaded) == 1
        assert loaded[0].content == "Persistent message"


# PostgreSQL tests - optional, requires psycopg
@pytest.mark.integration
class TestPostgreSQLStorage:
    """Tests for PostgreSQLStorage backend."""

    @pytest.fixture
    def pg_storage(self):
        """Fixture for PostgreSQL storage (requires running PostgreSQL)."""
        pytest.importorskip("psycopg", minversion=None)
        pytest.skip("PostgreSQL integration tests require manual setup")
        # Example implementation:
        # from orquestra import PostgreSQLStorage
        # storage = PostgreSQLStorage(
        #     host="localhost",
        #     database="orquestra_test",
        #     user="test",
        #     password="test"
        # )
        # yield storage
        # # Cleanup

    def test_postgresql_save_load(self, pg_storage):
        """Test PostgreSQL save and load."""
        session_id = "pg_test"

        message = Message(role="user", content="PostgreSQL test")
        pg_storage.save_message(session_id, message)

        loaded = pg_storage.load_messages(session_id)

        assert len(loaded) == 1
        assert loaded[0].content == "PostgreSQL test"
