# <¼ Orquestra

**Orchestrate agents and tools in perfect harmony.**

A modern AI agent framework with multi-provider support, built-in tools, and a FastAPI-style declarative API.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ( Features

- > **Multi-Provider Support** - OpenAI, Anthropic Claude, Google Gemini, and Ollama
- =à **Built-in Tools** - Search, filesystem, computation, and more
- >à **Memory Systems** - Separate chat and knowledge memory for better performance
- = **MCP Integration** - Model Context Protocol support (coming soon)
- <¨ **FastAPI-Style API** - Elegant and intuitive agent creation with decorators

## =æ Installation

```bash
# Basic installation
uv add orquestra

# With specific providers
uv add orquestra --optional openai
uv add orquestra --optional anthropic
uv add orquestra --optional gemini
uv add orquestra --optional ollama

# With all providers
uv add orquestra --optional all

# With search capabilities
uv add orquestra --optional search
```

## =€ Quick Start

```python
from orquestra import ReactAgent

# Create an agent
agent = ReactAgent(
    name="Assistant",
    description="A helpful AI assistant",
    provider="gpt-4o-mini"  # or "claude-3-5-sonnet-20241022", "gemini-pro", etc.
)

# Add tools with decorators (FastAPI style!)
@agent.tool()
def search(query: str) -> str:
    """Search the internet for information"""
    # Your search implementation
    return results

@agent.tool()
def calculate(expression: str) -> float:
    """Perform mathematical calculations"""
    return eval(expression)

# Run the agent
answer = agent.run("What is the capital of France?")
print(answer)
```

## <¯ Core Concepts

### Agents

Agents are the main orchestrators. Create them with a simple declarative API:

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

Tools are functions that agents can use. Register them with decorators:

```python
@agent.tool()
def read_csv(filepath: str) -> str:
    """Read a CSV file and return its contents"""
    with open(filepath) as f:
        return f.read()

# Or register programmatically
def write_file(path: str, content: str) -> str:
    """Write content to a file"""
    with open(path, 'w') as f:
        f.write(content)
    return f"Wrote {len(content)} bytes to {path}"

agent.add_tool(write_file)
```

### Built-in Tools

Orquestra comes with ready-to-use tools:

```python
from orquestra import web_search, calculate, read_file

# Use directly
results = web_search("Python async programming")

# Or register with agent
agent.add_tool(web_search)
agent.add_tool(calculate)
agent.add_tool(read_file)
```

### Memory Systems

Separate chat history from long-term knowledge:

```python
from orquestra import HybridMemory

# Create memory with chat history limit
memory = HybridMemory(max_chat_messages=100)

# Add to chat history
memory.add_message("user", "Hello!")
memory.add_message("assistant", "Hi there!")

# Add to knowledge base
memory.add_knowledge(
    "Python 3.13 was released in October 2024",
    metadata={"topic": "python", "type": "release"}
)

# Search knowledge
results = memory.search_knowledge("Python 3.13")
```

### Multi-Provider Support

Switch between providers seamlessly:

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

## =Ú Examples

### Web Research Agent

```python
from orquestra import ReactAgent, web_search, calculate

agent = ReactAgent(
    name="Researcher",
    description="Research assistant with web access",
    provider="gpt-4o-mini"
)

agent.add_tool(web_search)
agent.add_tool(calculate)

# Ask a research question
answer = agent.run(
    "What is the current population of Tokyo and how does it compare to New York?"
)
print(answer)
```

### File Analysis Agent

```python
from orquestra import ReactAgent
from orquestra.tools import FileSystemTool

agent = ReactAgent(
    name="FileAnalyzer",
    description="Analyzes and processes files",
    provider="claude-3-5-sonnet-20241022"
)

# Add filesystem tools
agent.add_tool(FileSystemTool.read)
agent.add_tool(FileSystemTool.list)
agent.add_tool(FileSystemTool.write)

# Analyze files
result = agent.run(
    "Read all Python files in the current directory and create a summary"
)
print(result)
```

### Data Processing Agent

```python
from orquestra import ReactAgent, calculate

agent = ReactAgent(
    name="DataProcessor",
    description="Processes and analyzes numerical data",
    provider="gpt-4o"
)

@agent.tool()
def load_data(filename: str) -> list[float]:
    """Load numerical data from a file"""
    with open(filename) as f:
        return [float(line.strip()) for line in f]

@agent.tool()
def stats(numbers: list[float]) -> dict:
    """Calculate statistics for a list of numbers"""
    return {
        "mean": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
    }

agent.add_tool(calculate)

result = agent.run("Load data.txt and calculate the mean, min, and max values")
```

## =' Configuration

### Environment Variables

Set API keys via environment variables:

```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
# Ollama runs locally, no key needed
```

Or use a `.env` file:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...
```

### Custom Providers

You can also pass API keys directly:

```python
from orquestra import ReactAgent

agent = ReactAgent(
    name="Agent",
    provider="gpt-4o-mini",
    api_key="your-api-key"
)
```

## >ê Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=orquestra

# Type checking
mypy src/orquestra

# Linting
ruff check src/orquestra

# Formatting
black src/orquestra
```

## =ú Roadmap

- [x] Core agent framework
- [x] Multi-provider support (OpenAI, Anthropic, Gemini, Ollama)
- [x] Tool system with decorators
- [x] Memory systems (chat + knowledge)
- [x] Built-in tools (search, filesystem, computation)
- [ ] MCP (Model Context Protocol) integration
- [ ] Vector database integration for knowledge
- [ ] Streaming responses
- [ ] Agent orchestration and chaining
- [ ] Plugin system
- [ ] Web UI for agent monitoring

## =Ä License

MIT License - see [LICENSE](LICENSE) file for details.

## > Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## =î Contact

- GitHub: [@marcosf63](https://github.com/marcosf63)
- Issues: [GitHub Issues](https://github.com/marcosf63/orquestra/issues)

---

**Orquestra** - Orchestrate agents and tools in perfect harmony <¼
