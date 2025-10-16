# Orquestra

**Orchestrate agents and tools in perfect harmony.**

A modern AI agent framework with multi-provider support, built-in tools, and a FastAPI-style declarative API.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Multi-Provider Support** - OpenAI, Anthropic Claude, Google Gemini, Ollama, and OpenRouter (100+ models)
- **Streaming Responses** - Real-time streaming of agent responses like ChatGPT
- **Vector Database Integration** - ChromaDB and Qdrant support for semantic search and RAG
- **Agent Orchestration** - Chain and coordinate multiple agents with workflows
- **Built-in Tools** - Search, filesystem, computation, and more
- **Memory Systems** - Chat memory with SQLite/PostgreSQL persistence
- **Date-Aware Agents** - Automatic current date/time context for accurate responses
- **Verbose & Debug Modes** - Built-in logging for troubleshooting and monitoring
- **MCP Integration** - Use external MCP server tools with one line of code
- **FastAPI-Style API** - Elegant and intuitive agent creation with decorators

## Installation

```bash
# Basic installation
uv add orquestra

# With specific providers
uv add orquestra --optional openai
uv add orquestra --optional anthropic
uv add orquestra --optional gemini
uv add orquestra --optional ollama

# With search capabilities
uv add orquestra --optional search

# With PostgreSQL persistence
uv add orquestra --optional postgresql

# With vector database support (ChromaDB)
uv add orquestra --optional vectordb

# With Qdrant vector database
uv add orquestra --optional qdrant
```

## Quick Start

```python
from orquestra import ReactAgent

# Create an agent
agent = ReactAgent(
    name="Assistant",
    description="A helpful AI assistant",
    provider="gpt-4o-mini"
)

# Add tools with decorators (FastAPI style!)
@agent.tool()
def search(query: str) -> str:
    """Search the internet for information"""
    return results

# Run the agent
answer = agent.run("What is the capital of France?")
print(answer)
```

## Core Concepts

### Agents

Create agents with a simple declarative API:

```python
from orquestra import ReactAgent

agent = ReactAgent(
    name="DataAnalyst",
    description="Analyzes data and provides insights",
    provider="gpt-4o-mini",
    max_iterations=10
)
```

### Tools

Register tools with decorators:

```python
@agent.tool()
def read_csv(filepath: str) -> str:
    """Read a CSV file"""
    with open(filepath) as f:
        return f.read()
```

### Built-in Tools

```python
from orquestra import web_search, calculate, read_file

agent.add_tool(web_search)
agent.add_tool(calculate)
```

### Memory with Persistence

#### SQLite (Built-in)

```python
from orquestra import ChatMemory, SQLiteStorage

storage = SQLiteStorage("chat_history.db")
memory = ChatMemory(storage=storage, session_id="user-123")

memory.add_message("user", "Hello!")
memory.add_message("assistant", "Hi there!")

# Messages are automatically saved to database
# Load them later with the same session_id
```

#### PostgreSQL (Optional)

```bash
uv add orquestra --optional postgresql
```

```python
from orquestra import ChatMemory, PostgreSQLStorage

storage = PostgreSQLStorage(
    host="localhost",
    database="orquestra",
    user="postgres",
    password="your-password"
)

memory = ChatMemory(storage=storage, session_id="user-123")
```

### Multi-Provider Support

```python
# OpenAI
agent = ReactAgent(name="GPT Agent", provider="gpt-4o-mini")

# Anthropic Claude
agent = ReactAgent(name="Claude Agent", provider="claude-3-5-sonnet-20241022")

# Google Gemini
agent = ReactAgent(name="Gemini Agent", provider="gemini-pro")

# Ollama (local)
agent = ReactAgent(name="Local Agent", provider="llama3")

# OpenRouter - Access 100+ models with one API key!
# Get your key at: https://openrouter.ai/keys
agent = ReactAgent(name="Claude via OpenRouter", provider="anthropic/claude-3.5-sonnet")
agent = ReactAgent(name="GPT via OpenRouter", provider="openai/gpt-4")
agent = ReactAgent(name="Llama via OpenRouter", provider="meta-llama/llama-3.1-70b")
```

### OpenRouter - Unified Access to 100+ Models

OpenRouter provides a single API to access models from OpenAI, Anthropic, Google, Meta, and many others:

```python
from orquestra import ReactAgent

# Set your OpenRouter API key (get it at https://openrouter.ai/keys)
# export OPENROUTER_API_KEY="sk-or-v1-..."

# Use any model with provider/model format
agent = ReactAgent(
    name="Assistant",
    provider="anthropic/claude-3.5-sonnet",  # Auto-detects OpenRouter
)

# Or specify explicitly
from orquestra.providers import OpenRouterProvider

provider = OpenRouterProvider(
    model="openai/gpt-4",
    api_key="sk-or-v1-..."  # Optional if OPENROUTER_API_KEY is set
)

agent = ReactAgent(name="Assistant", provider=provider)
```

**Available Models:** OpenAI GPT-4/GPT-3.5, Anthropic Claude, Google Gemini/PaLM, Meta Llama, Mistral, and 100+ more!

**Benefits:**
- Single API key for all providers
- Pay-per-use pricing
- No provider-specific setup needed
- Same interface as native providers

See `examples/openrouter_example.py` for more examples.

### Date-Aware Agents

Agents automatically know the current date and time:

```python
agent = ReactAgent(
    name="NewsBot",
    provider="gpt-4o-mini"
)

# Agent automatically has access to current date/time
# No need to manually include it in prompts!
answer = agent.run("What's happening in tech today?")

# Custom date for testing or specific scenarios
agent = ReactAgent(
    name="HistoricalBot",
    provider="gpt-4o-mini",
    current_date="2024-01-01",  # Custom date
    current_datetime="2024-01-01 09:00:00"  # Custom datetime
)
```

### Logging and Debugging

Enable verbose or debug mode to track execution:

```python
# Verbose mode - track tool calls and iterations
agent = ReactAgent(
    name="Assistant",
    provider="gpt-4o-mini",
    verbose=True  # Shows execution flow
)

# Debug mode - detailed troubleshooting
agent = ReactAgent(
    name="Assistant",
    provider="gpt-4o-mini",
    debug=True  # Shows everything + timestamps
)

# Logs will show:
# ▶ Starting agent execution
# 🔄 Iteration 1/10
# 🔧 Tool call: web_search(query='latest news')
# ✅ Tool result: 1859 characters
# ✓ Execution completed in 2.34s
```

### Streaming Responses

Stream responses in real-time for better user experience:

```python
from orquestra import ReactAgent

agent = ReactAgent(
    name="StreamingAssistant",
    provider="gpt-4o-mini"
)

# Stream response chunks
for chunk in agent.stream("Tell me a short story"):
    print(chunk, end="", flush=True)

# Async streaming
async for chunk in agent.astream("Explain quantum computing"):
    print(chunk, end="", flush=True)
```

### Vector Databases and RAG

Build knowledge bases with semantic search:

```python
from orquestra import ReactAgent
from orquestra.embeddings import OpenAIEmbeddings
from orquestra.vectorstores import ChromaVectorStore, Document

# Create embeddings provider
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Create vector store
store = ChromaVectorStore(
    collection_name="knowledge",
    embedding_provider=embeddings
)

# Add documents
store.add([
    Document(content="Orquestra is an AI agent framework"),
    Document(content="It supports multiple LLM providers"),
])

# Create agent with RAG
agent = ReactAgent(name="RAG Agent", provider="gpt-4o-mini")

@agent.tool()
def search_knowledge(query: str) -> str:
    """Search the knowledge base"""
    results = store.search(query, limit=3)
    return "\n".join([r.document.content for r in results])

# Agent will use knowledge base automatically
answer = agent.run("What is Orquestra?")
```

### Agent Orchestration

Chain multiple agents together:

```python
from orquestra import ReactAgent
from orquestra.orchestration import SequentialWorkflow

# Create specialized agents
researcher = ReactAgent(name="Researcher", provider="gpt-4o-mini")
writer = ReactAgent(name="Writer", provider="gpt-4o-mini")
editor = ReactAgent(name="Editor", provider="gpt-4o-mini")

# Create workflow
workflow = SequentialWorkflow()
workflow.add_agent(researcher)
workflow.add_agent(writer)
workflow.add_agent(editor)

# Run workflow - each agent processes the previous agent's output
result = workflow.run("Write an article about AI safety")
```

## Examples

See the [examples/](examples/) directory for complete examples:

- `basic_agent.py` - Simple agent with web search
- `custom_tools.py` - Creating custom tools with decorators
- `streaming_example.py` - Real-time streaming responses
- `vector_rag_example.py` - RAG with vector databases
- `persistence_sqlite.py` - Chat memory with SQLite
- `persistence_postgresql.py` - Chat memory with PostgreSQL

## Configuration

Set API keys via environment variables:

```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
```

Or use a `.env` file.

## MCP Integration

Orquestra agents can use tools from external [Model Context Protocol](https://modelcontextprotocol.io) servers with a simple one-line integration.

### Using MCP Server Tools

```python
from orquestra import ReactAgent

agent = ReactAgent(name="Assistant", provider="gpt-4o-mini")

# Connect to any MCP server - tools become available automatically
agent.add_mcp_server(
    name="filesystem",
    command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
)

# Agent can now use filesystem tools
response = agent.run("List the files in the directory and read any README files")
```

### Examples with Official MCP Servers

```python
# Filesystem operations
agent.add_mcp_server(
    name="filesystem",
    command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "/home/user"]
)

# GitHub integration
agent.add_mcp_server(
    name="github",
    command=["npx", "-y", "@modelcontextprotocol/server-github"]
)

# Brave Search
agent.add_mcp_server(
    name="brave-search",
    command=["npx", "-y", "@modelcontextprotocol/server-brave-search"]
)
```

### How It Works

1. Agent connects to MCP server via stdio subprocess
2. Discovers available tools automatically
3. Registers tools in agent's tool registry
4. Tools work exactly like native Orquestra tools

See `examples/mcp_tools_example.py` for complete example.

## Roadmap

- [x] Core agent framework
- [x] Multi-provider support (OpenAI, Anthropic, Gemini, Ollama)
- [x] Tool system with decorators
- [x] Memory systems with persistence (SQLite/PostgreSQL)
- [x] Built-in tools (search, filesystem, computation)
- [x] MCP (Model Context Protocol) integration - use external MCP server tools
- [x] Vector database integration for knowledge (ChromaDB, Qdrant)
- [x] Streaming responses (OpenAI, Anthropic)
- [x] Agent orchestration and chaining (Sequential workflows)
- [ ] Parallel agent execution
- [ ] Advanced orchestration patterns (conditional, hierarchical)
- [ ] More vector database integrations (Pinecone, Weaviate)
- [ ] Streaming for all providers (Gemini, Ollama, OpenRouter)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

- GitHub: [@marcosf63](https://github.com/marcosf63)
- Issues: [GitHub Issues](https://github.com/marcosf63/orquestra/issues)

---

**Orquestra** - Orchestrate agents and tools in perfect harmony
