# Orquestra

**Orchestrate agents and tools in perfect harmony.**

A modern AI agent framework with multi-provider support, built-in tools, and a FastAPI-style declarative API.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Multi-Provider Support** - OpenAI, Anthropic Claude, Google Gemini, Ollama, and OpenRouter (100+ models)
- **Built-in Tools** - Search, filesystem, computation, and more
- **Memory Systems** - Chat memory with SQLite/PostgreSQL persistence
- **Date-Aware Agents** - Automatic current date/time context for accurate responses
- **Verbose & Debug Modes** - Built-in logging for troubleshooting and monitoring
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
