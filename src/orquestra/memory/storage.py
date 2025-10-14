"""Storage backends for memory persistence."""

from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from typing import Any

from ..core.provider import Message


class StorageBackend(ABC):
    """Abstract base class for memory storage backends."""

    @abstractmethod
    def save_message(
        self, session_id: str, role: str, content: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """Save a message to storage.

        Args:
            session_id: Session identifier
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata
        """
        pass

    @abstractmethod
    def load_messages(
        self, session_id: str, limit: int | None = None, offset: int = 0
    ) -> list[Message]:
        """Load messages from storage.

        Args:
            session_id: Session identifier
            limit: Maximum number of messages to load
            offset: Number of messages to skip

        Returns:
            List of messages
        """
        pass

    @abstractmethod
    def delete_messages(self, session_id: str) -> None:
        """Delete all messages for a session.

        Args:
            session_id: Session identifier
        """
        pass

    @abstractmethod
    def list_sessions(self) -> list[str]:
        """List all session IDs.

        Returns:
            List of session identifiers
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the storage connection."""
        pass


class SQLiteStorage(StorageBackend):
    """SQLite storage backend for chat memory."""

    def __init__(self, db_path: str = "orquestra_memory.db") -> None:
        """Initialize SQLite storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self) -> None:
        """Create necessary database tables."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id
            ON messages(session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at
            ON messages(created_at)
        """)
        self.conn.commit()

    def save_message(
        self, session_id: str, role: str, content: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """Save a message to SQLite.

        Args:
            session_id: Session identifier
            role: Message role
            content: Message content
            metadata: Optional metadata
        """
        cursor = self.conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute(
            """
            INSERT INTO messages (session_id, role, content, metadata)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, role, content, metadata_json),
        )
        self.conn.commit()

    def load_messages(
        self, session_id: str, limit: int | None = None, offset: int = 0
    ) -> list[Message]:
        """Load messages from SQLite.

        Args:
            session_id: Session identifier
            limit: Maximum messages to load
            offset: Number of messages to skip

        Returns:
            List of messages
        """
        cursor = self.conn.cursor()

        query = """
            SELECT role, content FROM messages
            WHERE session_id = ?
            ORDER BY created_at ASC
        """
        params: list[Any] = [session_id]

        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [Message(role=row[0], content=row[1]) for row in rows]

    def delete_messages(self, session_id: str) -> None:
        """Delete all messages for a session.

        Args:
            session_id: Session identifier
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        self.conn.commit()

    def list_sessions(self) -> list[str]:
        """List all session IDs.

        Returns:
            List of session identifiers
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT session_id FROM messages ORDER BY session_id")
        return [row[0] for row in cursor.fetchall()]

    def close(self) -> None:
        """Close SQLite connection."""
        self.conn.close()

    def __del__(self) -> None:
        """Cleanup on deletion."""
        try:
            self.conn.close()
        except:
            pass


class PostgreSQLStorage(StorageBackend):
    """PostgreSQL storage backend for chat memory."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "orquestra",
        user: str = "postgres",
        password: str | None = None,
        connection_string: str | None = None,
    ) -> None:
        """Initialize PostgreSQL storage.

        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
            connection_string: Full connection string (overrides other params)
        """
        try:
            import psycopg
        except ImportError:
            raise ImportError(
                "PostgreSQL support requires psycopg. "
                "Install with: uv add orquestra --optional postgresql"
            )

        if connection_string:
            self.conn = psycopg.connect(connection_string)
        else:
            self.conn = psycopg.connect(
                host=host,
                port=port,
                dbname=database,
                user=user,
                password=password or "",
            )

        self._create_tables()

    def _create_tables(self) -> None:
        """Create necessary database tables."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_id
                ON messages(session_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at
                ON messages(created_at)
            """)
            self.conn.commit()

    def save_message(
        self, session_id: str, role: str, content: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """Save a message to PostgreSQL.

        Args:
            session_id: Session identifier
            role: Message role
            content: Message content
            metadata: Optional metadata
        """
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO messages (session_id, role, content, metadata)
                VALUES (%s, %s, %s, %s)
                """,
                (session_id, role, content, json.dumps(metadata) if metadata else None),
            )
            self.conn.commit()

    def load_messages(
        self, session_id: str, limit: int | None = None, offset: int = 0
    ) -> list[Message]:
        """Load messages from PostgreSQL.

        Args:
            session_id: Session identifier
            limit: Maximum messages to load
            offset: Number of messages to skip

        Returns:
            List of messages
        """
        with self.conn.cursor() as cursor:
            query = """
                SELECT role, content FROM messages
                WHERE session_id = %s
                ORDER BY created_at ASC
            """
            params: list[Any] = [session_id]

            if limit is not None:
                query += " LIMIT %s OFFSET %s"
                params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [Message(role=row[0], content=row[1]) for row in rows]

    def delete_messages(self, session_id: str) -> None:
        """Delete all messages for a session.

        Args:
            session_id: Session identifier
        """
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM messages WHERE session_id = %s", (session_id,))
            self.conn.commit()

    def list_sessions(self) -> list[str]:
        """List all session IDs.

        Returns:
            List of session identifiers
        """
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT session_id FROM messages ORDER BY session_id")
            return [row[0] for row in cursor.fetchall()]

    def close(self) -> None:
        """Close PostgreSQL connection."""
        self.conn.close()

    def __del__(self) -> None:
        """Cleanup on deletion."""
        try:
            self.conn.close()
        except:
            pass
