"""Tool system with registry for agent capabilities."""

from __future__ import annotations

import inspect
from typing import Any, Callable, TypeVar, get_type_hints

from pydantic import BaseModel, create_model

F = TypeVar("F", bound=Callable[..., Any])


class ToolParameter(BaseModel):
    """Represents a tool parameter with type and description."""

    name: str
    type: type
    description: str | None = None
    required: bool = True
    default: Any = None


class Tool(BaseModel):
    """Represents a callable tool that an agent can use."""

    name: str
    description: str | None = None
    parameters: list[ToolParameter] = []
    function: Callable[..., Any]

    class Config:
        arbitrary_types_allowed = True

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the tool function."""
        return self.function(*args, **kwargs)

    @classmethod
    def from_function(cls, func: Callable[..., Any], name: str | None = None) -> Tool:
        """Create a Tool from a function with type hints and docstring.

        Args:
            func: The function to convert to a tool
            name: Optional custom name for the tool

        Returns:
            Tool instance wrapping the function
        """
        tool_name = name or func.__name__
        description = inspect.getdoc(func) or f"Tool: {tool_name}"

        # Extract type hints
        type_hints = get_type_hints(func)
        sig = inspect.signature(func)

        # Build parameters list
        parameters: list[ToolParameter] = []
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_type = type_hints.get(param_name, Any)
            required = param.default == inspect.Parameter.empty
            default = None if required else param.default

            # Try to extract parameter description from docstring
            param_description = None
            if func.__doc__:
                # Simple extraction - can be improved with docstring parser
                for line in func.__doc__.split("\n"):
                    if param_name in line and ":" in line:
                        param_description = line.split(":", 1)[1].strip()
                        break

            parameters.append(
                ToolParameter(
                    name=param_name,
                    type=param_type,
                    description=param_description,
                    required=required,
                    default=default,
                )
            )

        return cls(
            name=tool_name,
            description=description,
            parameters=parameters,
            function=func,
        )

    def to_openai_format(self) -> dict[str, Any]:
        """Convert tool to OpenAI function calling format."""
        properties = {}
        required = []

        for param in self.parameters:
            param_schema = {"type": self._python_type_to_json_type(param.type)}
            if param.description:
                param_schema["description"] = param.description

            properties[param.name] = param_schema
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description or "",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def to_anthropic_format(self) -> dict[str, Any]:
        """Convert tool to Anthropic tool format."""
        input_schema = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        for param in self.parameters:
            input_schema["properties"][param.name] = {
                "type": self._python_type_to_json_type(param.type),
                "description": param.description or "",
            }
            if param.required:
                input_schema["required"].append(param.name)

        return {
            "name": self.name,
            "description": self.description or "",
            "input_schema": input_schema,
        }

    @staticmethod
    def _python_type_to_json_type(python_type: type) -> str:
        """Convert Python type to JSON Schema type."""
        type_mapping = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }
        return type_mapping.get(python_type, "string")


class ToolRegistry:
    """Registry for managing agent tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool in the registry.

        Args:
            tool: The tool to register
        """
        self._tools[tool.name] = tool

    def register_function(
        self, func: Callable[..., Any], name: str | None = None
    ) -> Tool:
        """Register a function as a tool.

        Args:
            func: The function to register
            name: Optional custom name for the tool

        Returns:
            The created Tool instance
        """
        tool = Tool.from_function(func, name)
        self.register(tool)
        return tool

    def get(self, name: str) -> Tool | None:
        """Get a tool by name.

        Args:
            name: The tool name

        Returns:
            The tool if found, None otherwise
        """
        return self._tools.get(name)

    def get_all(self) -> list[Tool]:
        """Get all registered tools.

        Returns:
            List of all registered tools
        """
        return list(self._tools.values())

    def remove(self, name: str) -> None:
        """Remove a tool from the registry.

        Args:
            name: The tool name to remove
        """
        self._tools.pop(name, None)

    def clear(self) -> None:
        """Clear all tools from the registry."""
        self._tools.clear()

    def __len__(self) -> int:
        """Return the number of registered tools."""
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools
