"""Memory systems for agent conversation and knowledge management."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from ..core.provider import Message


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
    """Simple chat history memory.

    Stores conversation messages in chronological order with optional
    window size limiting.
    """

    def __init__(self, max_messages: int | None = None) -> None:
        """Initialize chat memory.

        Args:
            max_messages: Maximum number of messages to keep (None for unlimited)
        """
        self.max_messages = max_messages
        self._messages: list[Message] = []

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

    def add_message(self, role: str, content: str) -> None:
        """Add a message directly.

        Args:
            role: Message role (user, assistant, system)
            content: Message content
        """
        self._messages.append(Message(role=role, content=content))

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


class HybridMemory:
    """Combines chat and knowledge memory.

    Separates conversational context (chat) from long-term knowledge
    for better performance and retrieval.
    """

    def __init__(
        self,
        max_chat_messages: int | None = None,
    ) -> None:
        """Initialize hybrid memory.

        Args:
            max_chat_messages: Maximum chat history messages
        """
        self.chat = ChatMemory(max_messages=max_chat_messages)
        self.knowledge = KnowledgeMemory()

    def add_message(self, role: str, content: str) -> None:
        """Add to chat memory.

        Args:
            role: Message role
            content: Message content
        """
        self.chat.add_message(role, content)

    def add_knowledge(self, content: str, metadata: dict[str, Any] | None = None) -> None:
        """Add to knowledge memory.

        Args:
            content: Knowledge content
            metadata: Optional metadata
        """
        entry = MemoryEntry(content=content, metadata=metadata or {})
        self.knowledge.add(entry)

    def search_knowledge(self, query: str, limit: int = 5) -> list[MemoryEntry]:
        """Search knowledge base.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of relevant knowledge entries
        """
        return self.knowledge.search(query, limit)

    def get_context(
        self, include_knowledge: bool = False, knowledge_query: str | None = None
    ) -> list[Message]:
        """Get conversation context.

        Args:
            include_knowledge: Whether to include relevant knowledge
            knowledge_query: Query for knowledge search (uses last message if None)

        Returns:
            List of messages for context
        """
        messages = self.chat.get_messages()

        if include_knowledge:
            query = knowledge_query
            if query is None and messages:
                # Use last user message as query
                for msg in reversed(messages):
                    if msg.role == "user":
                        query = msg.content
                        break

            if query:
                knowledge_entries = self.search_knowledge(query)
                if knowledge_entries:
                    # Insert knowledge as system message
                    knowledge_content = "Relevant knowledge:\n" + "\n".join(
                        f"- {entry.content}" for entry in knowledge_entries
                    )
                    messages.insert(
                        0 if not messages or messages[0].role != "system" else 1,
                        Message(role="system", content=knowledge_content),
                    )

        return messages

    def clear_chat(self) -> None:
        """Clear chat history only."""
        self.chat.clear()

    def clear_knowledge(self) -> None:
        """Clear knowledge base only."""
        self.knowledge.clear()

    def clear_all(self) -> None:
        """Clear both chat and knowledge."""
        self.chat.clear()
        self.knowledge.clear()
