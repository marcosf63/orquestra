"""Base vector store abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class Document(BaseModel):
    """Document with content and metadata."""

    content: str
    metadata: dict[str, Any] = {}
    id: str | None = None


class SearchResult(BaseModel):
    """Search result from vector store."""

    document: Document
    score: float
    """Similarity score (higher is more similar)."""


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    def add(
        self,
        documents: list[Document] | list[str],
        embeddings: list[list[float]] | None = None,
    ) -> list[str]:
        """Add documents to the vector store.

        Args:
            documents: List of documents or strings to add
            embeddings: Pre-computed embeddings (optional, will compute if not provided)

        Returns:
            List of document IDs
        """
        pass

    @abstractmethod
    async def aadd(
        self,
        documents: list[Document] | list[str],
        embeddings: list[list[float]] | None = None,
    ) -> list[str]:
        """Async add documents to the vector store.

        Args:
            documents: List of documents or strings to add
            embeddings: Pre-computed embeddings (optional)

        Returns:
            List of document IDs
        """
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Search for similar documents.

        Args:
            query: Query string
            limit: Maximum number of results
            filter: Optional metadata filter

        Returns:
            List of search results ordered by similarity
        """
        pass

    @abstractmethod
    async def asearch(
        self,
        query: str,
        limit: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Async search for similar documents.

        Args:
            query: Query string
            limit: Maximum number of results
            filter: Optional metadata filter

        Returns:
            List of search results ordered by similarity
        """
        pass

    @abstractmethod
    def delete(self, ids: list[str]) -> None:
        """Delete documents by ID.

        Args:
            ids: List of document IDs to delete
        """
        pass

    @abstractmethod
    async def adelete(self, ids: list[str]) -> None:
        """Async delete documents by ID.

        Args:
            ids: List of document IDs to delete
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all documents from the store."""
        pass

    @abstractmethod
    async def aclear(self) -> None:
        """Async clear all documents from the store."""
        pass

    def count(self) -> int:
        """Get number of documents in the store.

        Returns:
            Number of documents
        """
        raise NotImplementedError("count() not implemented")
