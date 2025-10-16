"""Vector stores for semantic search and retrieval."""

from .base import Document, SearchResult, VectorStore

try:
    from .chroma import ChromaVectorStore
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    ChromaVectorStore = None  # type: ignore

__all__ = [
    "VectorStore",
    "Document",
    "SearchResult",
    "ChromaVectorStore",
]
