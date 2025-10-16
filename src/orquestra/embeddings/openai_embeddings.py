"""OpenAI embeddings implementation."""

from __future__ import annotations

import os

from .base import EmbeddingProvider

try:
    from openai import AsyncOpenAI, OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIEmbeddings(EmbeddingProvider):
    """OpenAI embeddings provider.

    Supports models:
    - text-embedding-3-small (1536 dimensions, faster, cheaper)
    - text-embedding-3-large (3072 dimensions, better quality)
    - text-embedding-ada-002 (legacy, 1536 dimensions)
    """

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: str | None = None,
        **kwargs,
    ) -> None:
        """Initialize OpenAI embeddings.

        Args:
            model: OpenAI embedding model name
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            **kwargs: Additional OpenAI client configuration
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package not installed. "
                "Install it with: uv add openai or pip install openai"
            )

        super().__init__(model, **kwargs)

        # Get API key from env if not provided
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter"
            )

        # Initialize clients
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

    def embed(self, text: str) -> list[float]:
        """Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    async def aembed(self, text: str) -> list[float]:
        """Async generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        response = await self.async_client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        # Sort by index to ensure correct order
        embeddings = sorted(response.data, key=lambda x: x.index)
        return [e.embedding for e in embeddings]

    async def aembed_batch(self, texts: list[str]) -> list[list[float]]:
        """Async generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        response = await self.async_client.embeddings.create(
            model=self.model,
            input=texts,
        )
        # Sort by index to ensure correct order
        embeddings = sorted(response.data, key=lambda x: x.index)
        return [e.embedding for e in embeddings]

    def dimension(self) -> int:
        """Get embedding dimension.

        Returns:
            Embedding dimension
        """
        dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        return dimensions.get(self.model, 1536)
