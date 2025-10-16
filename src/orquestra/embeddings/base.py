"""Base embedding provider abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    def __init__(self, model: str, **kwargs) -> None:
        """Initialize the embedding provider.

        Args:
            model: Model identifier
            **kwargs: Additional provider-specific configuration
        """
        self.model = model
        self.config = kwargs

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        pass

    @abstractmethod
    async def aembed(self, text: str) -> list[float]:
        """Async generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        pass

    @abstractmethod
    async def aembed_batch(self, texts: list[str]) -> list[list[float]]:
        """Async generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        pass

    def dimension(self) -> int:
        """Get the dimension of embeddings produced by this provider.

        Returns:
            Embedding dimension (e.g., 1536 for text-embedding-3-small)
        """
        # Default implementation - subclasses should override with actual dimension
        return 1536
