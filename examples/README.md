# Orquestra Examples

This directory contains example scripts demonstrating various features of the Orquestra framework.

## Running Examples

Before running the examples, make sure you have:

1. Installed Orquestra with the required providers:
```bash
uv add orquestra --optional openai --optional search
```

2. Set your API keys:
```bash
export OPENAI_API_KEY="your-key"
# or use a .env file
```

## Available Examples

### 1. Basic Agent (`basic_agent.py`)

Demonstrates creating a simple agent with web search capability.

```bash
python examples/basic_agent.py
```

**Features:**
- Creating a ReactAgent
- Adding built-in tools
- Running queries

### 2. Custom Tools (`custom_tools.py`)

Shows how to create custom tools using decorators (FastAPI style).

```bash
python examples/custom_tools.py
```

**Features:**
- Tool creation with `@agent.tool()` decorator
- Type hints for tool parameters
- Docstring-based tool descriptions
- Multiple tools per agent

### 3. SQLite Persistence (`persistence_sqlite.py`)

Demonstrates persistent chat memory using SQLite.

```bash
python examples/persistence_sqlite.py
```

**Features:**
- ChatMemory with SQLite persistence
- Session management
- Message persistence across runs
- Listing available sessions

### 4. PostgreSQL Persistence (`persistence_postgresql.py`)

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
