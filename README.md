# Orquestra

**Orchestrate agents and tools in perfect harmony.**

A modern AI agent framework with multi-provider support, built-in tools, and a FastAPI-style declarative API.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Multi-Provider Support** - OpenAI, Anthropic Claude, Google Gemini, and Ollama
- **Built-in Tools** - Search, filesystem, computation, and more
- **Memory Systems** - Chat memory with SQLite/PostgreSQL persistence
- **MCP Integration** - Model Context Protocol support (coming soon)
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
```

## Examples

See the [examples/](examples/) directory for complete examples:

- `basic_agent.py` - Simple agent with web search
- `custom_tools.py` - Creating custom tools with decorators
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

## Roadmap

- [x] Core agent framework
- [x] Multi-provider support (OpenAI, Anthropic, Gemini, Ollama)
- [x] Tool system with decorators
- [x] Memory systems with persistence (SQLite/PostgreSQL)
- [x] Built-in tools (search, filesystem, computation)
- [ ] MCP (Model Context Protocol) integration
- [ ] Vector database integration for knowledge
- [ ] Streaming responses
- [ ] Agent orchestration and chaining

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

- GitHub: [@marcosf63](https://github.com/marcosf63)
- Issues: [GitHub Issues](https://github.com/marcosf63/orquestra/issues)

---

**Orquestra** - Orchestrate agents and tools in perfect harmony
