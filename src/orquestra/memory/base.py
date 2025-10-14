"""Memory systems for agent conversation and knowledge management."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from ..core.provider import Message
from .storage import StorageBackend


class MemoryEntry(BaseModel):
    """Represents a memory entry."""

    content: str
    metadata: dict[str, Any] = {}
    timestamp: float | None = None


class Memory(ABC):
    """Abstract base class for memory systems."""

    @abstractmethod
    def add(self, entry: MemoryEntry | str) -> None:
        """Add an entry to memory.

        Args:
            entry: Memory entry or string content
        """
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[MemoryEntry]:
        """Search memory for relevant entries.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of relevant memory entries
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all memory entries."""
        pass


class ChatMemory(Memory):
    """Chat history memory with optional persistence.

    Stores conversation messages in chronological order with optional
    window size limiting and database persistence support.
    """

    def __init__(
        self,
        max_messages: int | None = None,
        storage: StorageBackend | None = None,
        session_id: str | None = None,
    ) -> None:
        """Initialize chat memory.

        Args:
            max_messages: Maximum number of messages to keep (None for unlimited)
            storage: Optional storage backend for persistence
            session_id: Session identifier for storage (auto-generated if not provided)
        """
        self.max_messages = max_messages
        self.storage = storage
        self.session_id = session_id or str(uuid.uuid4())
        self._messages: list[Message] = []

        # Load messages from storage if available
        if self.storage:
            self._messages = self.storage.load_messages(self.session_id, limit=max_messages)

    def add(self, entry: MemoryEntry | str | Message) -> None:
        """Add a message to chat history.

        Args:
            entry: Message to add
        """
        if isinstance(entry, Message):
            self._messages.append(entry)
        elif isinstance(entry, str):
            self._messages.append(Message(role="user", content=entry))
        elif isinstance(entry, MemoryEntry):
            self._messages.append(Message(role="user", content=entry.content))

        # Maintain window size
        if self.max_messages and len(self._messages) > self.max_messages:
            # Keep system message if present
            if self._messages[0].role == "system":
                self._messages = [self._messages[0]] + self._messages[-(self.max_messages - 1):]
            else:
                self._messages = self._messages[-self.max_messages:]

    def add_message(self, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Add a message directly.

        Args:
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata for the message
        """
        message = Message(role=role, content=content)
        self._messages.append(message)

        # Save to storage if available
        if self.storage:
            self.storage.save_message(self.session_id, role, content, metadata)

        # Maintain window size
        if self.max_messages and len(self._messages) > self.max_messages:
            if self._messages[0].role == "system":
                self._messages = [self._messages[0]] + self._messages[-(self.max_messages - 1):]
            else:
                self._messages = self._messages[-self.max_messages:]

    def get_messages(self) -> list[Message]:
        """Get all messages in chronological order.

        Returns:
            List of messages
        """
        return self._messages.copy()

    def search(self, query: str, limit: int = 5) -> list[MemoryEntry]:
        """Search chat history (simple keyword matching).

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching memory entries
        """
        query_lower = query.lower()
        matches: list[MemoryEntry] = []

        for msg in self._messages:
            if query_lower in msg.content.lower():
                matches.append(
                    MemoryEntry(
                        content=msg.content,
                        metadata={"role": msg.role},
                    )
                )
                if len(matches) >= limit:
                    break

        return matches

    def clear(self) -> None:
        """Clear all chat history."""
        self._messages.clear()

        # Clear from storage if available
        if self.storage:
            self.storage.delete_messages(self.session_id)

    def load_from_storage(self, limit: int | None = None) -> None:
        """Reload messages from storage.

        Args:
            limit: Maximum number of messages to load
        """
        if not self.storage:
            raise ValueError("No storage backend configured")

        self._messages = self.storage.load_messages(
            self.session_id, limit=limit or self.max_messages
        )

    def list_sessions(self) -> list[str]:
        """List all available session IDs from storage.

        Returns:
            List of session IDs

        Raises:
            ValueError: If no storage backend configured
        """
        if not self.storage:
            raise ValueError("No storage backend configured")

        return self.storage.list_sessions()

    def __len__(self) -> int:
        """Get number of messages in history."""
        return len(self._messages)


class KnowledgeMemory(Memory):
    """Vector-based knowledge memory for semantic search.

    This is a simple in-memory implementation. For production use,
    consider integrating with vector databases like ChromaDB, Pinecone, etc.
    """

    def __init__(self) -> None:
        """Initialize knowledge memory."""
        self._entries: list[MemoryEntry] = []

    def add(self, entry: MemoryEntry | str) -> None:
        """Add knowledge entry.

        Args:
            entry: Knowledge entry or string
        """
        if isinstance(entry, str):
            entry = MemoryEntry(content=entry)

        self._entries.append(entry)

    def search(self, query: str, limit: int = 5) -> list[MemoryEntry]:
        """Search knowledge base (simple keyword matching).

        Note: This is a basic implementation using keyword matching.
        For production, integrate with vector embeddings and similarity search.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of relevant knowledge entries
        """
        query_lower = query.lower()
        scored_entries: list[tuple[int, MemoryEntry]] = []

        for entry in self._entries:
            # Simple scoring: count matching words
            score = sum(
                1 for word in query_lower.split() if word in entry.content.lower()
            )
            if score > 0:
                scored_entries.append((score, entry))

        # Sort by score descending and return top results
        scored_entries.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored_entries[:limit]]

    def clear(self) -> None:
        """Clear all knowledge entries."""
        self._entries.clear()

    def __len__(self) -> int:
        """Get number of knowledge entries."""
        return len(self._entries)


