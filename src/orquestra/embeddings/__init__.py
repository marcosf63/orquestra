"""Embedding providers for vector representations of text."""

from .base import EmbeddingProvider

try:
    from .openai_embeddings import OpenAIEmbeddings
    OPENAI_EMBEDDINGS_AVAILABLE = True
except ImportError:
    OPENAI_EMBEDDINGS_AVAILABLE = False
    OpenAIEmbeddings = None  # type: ignore

__all__ = [
    "EmbeddingProvider",
    "OpenAIEmbeddings",
]
