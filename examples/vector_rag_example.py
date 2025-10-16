"""Example of RAG (Retrieval-Augmented Generation) using vector databases.

This example shows how to build a knowledge base with vector search
and use it to answer questions with context.

Requirements:
    - Install: uv add chromadb
    - OpenAI API key: export OPENAI_API_KEY="your-key"

Usage:
    uv run python examples/vector_rag_example.py
"""

from orquestra import ReactAgent
from orquestra.embeddings import OpenAIEmbeddings
from orquestra.vectorstores import ChromaVectorStore, Document


def simple_rag_example():
    """Simple RAG example with ChromaDB."""
    print("=" * 60)
    print("Simple RAG Example")
    print("=" * 60)

    # Create embeddings provider
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Create vector store
    store = ChromaVectorStore(
        collection_name="orquestra_docs",
        embedding_provider=embeddings,
    )

    # Add some knowledge to the vector store
    documents = [
        Document(
            content="Orquestra is a modern AI agent framework with multi-provider support.",
            metadata={"source": "overview"},
        ),
        Document(
            content="Orquestra supports OpenAI, Anthropic Claude, Google Gemini, and Ollama.",
            metadata={"source": "providers"},
        ),
        Document(
            content="You can register tools using decorators with @agent.tool().",
            metadata={"source": "tools"},
        ),
        Document(
            content="Orquestra has built-in memory systems with SQLite and PostgreSQL persistence.",
            metadata={"source": "memory"},
        ),
        Document(
            content="The framework supports streaming responses from AI models.",
            metadata={"source": "features"},
        ),
    ]

    print("\nAdding documents to vector store...")
    store.add(documents)
    print(f"✓ Added {store.count()} documents")

    # Create an agent with a RAG tool
    agent = ReactAgent(
        name="RAG Assistant",
        description="An assistant with access to Orquestra documentation",
        provider="gpt-4o-mini",
    )

    # Add a search tool that uses the vector store
    @agent.tool()
    def search_knowledge(query: str) -> str:
        """Search the Orquestra documentation knowledge base."""
        results = store.search(query, limit=3)
        if not results:
            return "No relevant information found."

        context = "\n\n".join([
            f"- {r.document.content} (relevance: {r.score:.2f})"
            for r in results
        ])
        return f"Relevant information:\n{context}"

    # Ask questions
    questions = [
        "What providers does Orquestra support?",
        "How do I add tools to an agent?",
        "Does Orquestra support streaming?",
    ]

    for question in questions:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}")

        answer = agent.run(question)
        print(f"\nAnswer: {answer}\n")


def main():
    """Run RAG example."""
    try:
        simple_rag_example()
    except ImportError as e:
        if "chromadb" in str(e):
            print("ChromaDB not installed.")
            print("Install it with: uv add chromadb")
        else:
            raise
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure OPENAI_API_KEY is set:")
        print("  export OPENAI_API_KEY='your-key'")


if __name__ == "__main__":
    main()
