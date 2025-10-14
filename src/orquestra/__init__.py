"""Orquestra - Orchestrate agents and tools in perfect harmony.

A modern AI agent framework with multi-provider support, built-in tools,
and FastAPI-style declarative API.
"""

__version__ = "0.2.4"

# Core components
from .core import (
    Agent,
    Message,
    Provider,
    ProviderFactory,
    ProviderResponse,
    Tool,
    ToolCall,
    ToolParameter,
    ToolRegistry,
)

# Agent types
from .agents import ReactAgent

# Memory systems
from .memory import (
    ChatMemory,
    KnowledgeMemory,
    Memory,
    MemoryEntry,
    PostgreSQLStorage,
    SQLiteStorage,
    StorageBackend,
)

# Built-in tools
from .tools import (
    ComputationTool,
    FileSystemTool,
    SearchTool,
    calculate,
    convert_units,
    list_directory,
    news_search,
    python_eval,
    read_file,
    web_search,
    write_file,
)

# Import providers to trigger registration
from . import providers

__all__ = [
    # Version
    "__version__",
    # Core
    "Agent",
    "Tool",
    "ToolParameter",
    "ToolRegistry",
    "Provider",
    "ProviderFactory",
    "Message",
    "ProviderResponse",
    "ToolCall",
    # Agents
    "ReactAgent",
    # Memory
    "Memory",
    "MemoryEntry",
    "ChatMemory",
    "KnowledgeMemory",
    "StorageBackend",
    "SQLiteStorage",
    "PostgreSQLStorage",
    # Tools - Classes
    "SearchTool",
    "FileSystemTool",
    "ComputationTool",
    # Tools - Functions
    "web_search",
    "news_search",
    "read_file",
    "write_file",
    "list_directory",
    "calculate",
    "python_eval",
    "convert_units",
]
