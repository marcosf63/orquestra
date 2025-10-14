# Orquestra Examples

This directory contains example scripts demonstrating various features of the Orquestra framework.

## Running Examples

Before running the examples, make sure you have:

1. Installed Orquestra with the required providers:
```bash
uv add orquestra --optional openai --optional search
```

2. Configure your API keys using a `.env` file:
```bash
# Copy the example file
cp ../.env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=sk-your-key-here
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# GOOGLE_API_KEY=your-key-here
```

All examples automatically load environment variables from `.env` file using `python-dotenv`.

## Available Examples

### 1. Simple Demo (`simple_demo.py`) - **START HERE!**

Simple demonstration with basic math tools (no external dependencies required).

```bash
uv run python examples/simple_demo.py
```

**Features:**
- Creating a ReactAgent
- Adding custom tools with decorators
- Multiple tool interactions
- **No external dependencies needed**

### 2. Basic Agent (`basic_agent.py`)

Demonstrates creating an agent with web search capability.

```bash
# Requires search dependency
uv add orquestra --optional search

uv run python examples/basic_agent.py
```

**Features:**
- Creating a ReactAgent
- Adding built-in web search tool
- Real-world web queries
- Exception handling for missing dependencies
- **Requires:** ddgs dependency

### 3. Custom Tools (`custom_tools.py`)

Shows how to create custom tools using decorators (FastAPI style).

```bash
python examples/custom_tools.py
```

**Features:**
- Tool creation with `@agent.tool()` decorator
- Type hints for tool parameters
- Docstring-based tool descriptions
- Multiple tools per agent

### 4. SQLite Persistence (`persistence_sqlite.py`)

Demonstrates persistent chat memory using SQLite.

```bash
python examples/persistence_sqlite.py
```

**Features:**
- ChatMemory with SQLite persistence
- Session management
- Message persistence across runs
- Listing available sessions

### 5. PostgreSQL Persistence (`persistence_postgresql.py`)

Demonstrates persistent chat memory using PostgreSQL.

```bash
# Requires PostgreSQL optional dependency
uv add orquestra --optional postgresql

python examples/persistence_postgresql.py
```

**Features:**
- ChatMemory with PostgreSQL persistence
- Message metadata support
- Production-ready database backend
- Connection string or parameter-based configuration

## Next Steps

After exploring these examples, check out:

- [Main README](../README.md) for full documentation
- [API Reference](../docs/api.md) (coming soon)
- [Advanced Examples](../docs/examples.md) (coming soon)

## Need Help?

- Open an issue: [GitHub Issues](https://github.com/marcosf63/orquestra/issues)
- Read the docs: [Documentation](https://github.com/marcosf63/orquestra#readme)
