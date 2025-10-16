"""ChromaDB vector store implementation."""

from __future__ import annotations

import uuid
from typing import Any

from ..embeddings.base import EmbeddingProvider
from .base import Document, SearchResult, VectorStore

try:
    import chromadb
    from chromadb.config import Settings

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


class ChromaVectorStore(VectorStore):
    """ChromaDB vector store implementation.

    ChromaDB is a simple, easy-to-use vector database that's perfect
    for getting started with vector search and RAG applications.

    Example:
        ```python
        from orquestra.embeddings import OpenAIEmbeddings
        from orquestra.vectorstores import ChromaVectorStore

        # Create embeddings provider
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        # Create vector store
        store = ChromaVectorStore(
            collection_name="my_documents",
            embedding_provider=embeddings,
        )

        # Add documents
        store.add(["Document 1", "Document 2", "Document 3"])

        # Search
        results = store.search("query text", limit=5)
        ```
    """

    def __init__(
        self,
        collection_name: str = "orquestra",
        embedding_provider: EmbeddingProvider | None = None,
        persist_directory: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ChromaDB vector store.

        Args:
            collection_name: Name of the Chroma collection
            embedding_provider: Embedding provider for generating vectors
            persist_directory: Directory to persist data (None for in-memory)
            **kwargs: Additional ChromaDB configuration
        """
        if not CHROMA_AVAILABLE:
            raise ImportError(
                "ChromaDB not installed. "
                "Install it with: uv add chromadb or pip install chromadb"
            )

        self.embedding_provider = embedding_provider
        self.collection_name = collection_name

        # Create Chroma client
        if persist_directory:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(**kwargs),
            )
        else:
            self.client = chromadb.Client(settings=Settings(**kwargs))

        # Get or create collection
        # If we have an embedding provider, use custom embedding function
        if embedding_provider:
            # ChromaDB expects an embedding function - we'll wrap our provider
            embedding_fn = self._create_embedding_function()
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=embedding_fn,
            )
        else:
            # Use Chroma's default embedding function
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
            )

    def _create_embedding_function(self):
        """Create ChromaDB-compatible embedding function."""
        from chromadb.api.types import EmbeddingFunction

        provider = self.embedding_provider

        class CustomEmbeddingFunction(EmbeddingFunction):
            def __call__(self, input: list[str]) -> list[list[float]]:
                return provider.embed_batch(input)

        return CustomEmbeddingFunction()

    def add(
        self,
        documents: list[Document] | list[str],
        embeddings: list[list[float]] | None = None,
    ) -> list[str]:
        """Add documents to ChromaDB.

        Args:
            documents: List of documents or strings
            embeddings: Pre-computed embeddings (optional)

        Returns:
            List of document IDs
        """
        # Convert strings to Documents
        docs = []
        for doc in documents:
            if isinstance(doc, str):
                docs.append(Document(content=doc))
            else:
                docs.append(doc)

        # Generate IDs if not provided
        ids = []
        for doc in docs:
            if doc.id:
                ids.append(doc.id)
            else:
                doc.id = str(uuid.uuid4())
                ids.append(doc.id)

        # Extract content and metadata
        contents = [doc.content for doc in docs]
        metadatas = [doc.metadata for doc in docs]

        # Add to collection
        if embeddings:
            self.collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas,
                embeddings=embeddings,
            )
        else:
            self.collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas,
            )

        return ids

    async def aadd(
        self,
        documents: list[Document] | list[str],
        embeddings: list[list[float]] | None = None,
    ) -> list[str]:
        """Async add documents (ChromaDB is synchronous, so this just wraps add).

        Args:
            documents: List of documents or strings
            embeddings: Pre-computed embeddings (optional)

        Returns:
            List of document IDs
        """
        return self.add(documents, embeddings)

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
            List of search results
        """
        # Query ChromaDB
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=filter,
        )

        # Convert to SearchResult objects
        search_results = []
        if results and results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                doc = Document(
                    content=results["documents"][0][i],
                    metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                    id=results["ids"][0][i],
                )
                score = 1.0 - results["distances"][0][i] if results["distances"] else 0.0
                search_results.append(SearchResult(document=doc, score=score))

        return search_results

    async def asearch(
        self,
        query: str,
        limit: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Async search (ChromaDB is synchronous, so this just wraps search).

        Args:
            query: Query string
            limit: Maximum number of results
            filter: Optional metadata filter

        Returns:
            List of search results
        """
        return self.search(query, limit, filter)

    def delete(self, ids: list[str]) -> None:
        """Delete documents by ID.

        Args:
            ids: List of document IDs
        """
        self.collection.delete(ids=ids)

    async def adelete(self, ids: list[str]) -> None:
        """Async delete documents.

        Args:
            ids: List of document IDs
        """
        self.delete(ids)

    def clear(self) -> None:
        """Clear all documents from collection."""
        self.client.delete_collection(name=self.collection_name)
        # Recreate empty collection
        if self.embedding_provider:
            embedding_fn = self._create_embedding_function()
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embedding_fn,
            )
        else:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
            )

    async def aclear(self) -> None:
        """Async clear all documents."""
        self.clear()

    def count(self) -> int:
        """Get number of documents.

        Returns:
            Number of documents in collection
        """
        return self.collection.count()
