"""Unit tests for the tool system."""

import pytest

from orquestra.core.tool import Tool, ToolParameter, ToolRegistry


class TestToolParameter:
    """Tests for ToolParameter class."""

    def test_create_tool_parameter(self):
        """Test creating a tool parameter."""
        param = ToolParameter(
            name="test_param",
            type=str,
            description="A test parameter",
            required=True,
        )

        assert param.name == "test_param"
        assert param.type == str
        assert param.description == "A test parameter"
        assert param.required is True

    def test_tool_parameter_with_default(self):
        """Test tool parameter with default value."""
        param = ToolParameter(
            name="optional_param",
            type=int,
            description="Optional parameter",
            required=False,
            default=42,
        )

        assert param.required is False
        assert param.default == 42


class TestTool:
    """Tests for Tool class."""

    def test_tool_from_function(self, sample_tool_function):
        """Test creating a Tool from a function."""
        tool = Tool.from_function(sample_tool_function)

        assert tool.name == "add_numbers"
        assert "Add two numbers together" in tool.description
        assert len(tool.parameters) == 2

        # Check parameters
        params = {p.name: p for p in tool.parameters}
        assert "a" in params
        assert "b" in params
        assert params["a"].type == int
        assert params["b"].type == int
        assert params["a"].required is True
        assert params["b"].required is True

    def test_tool_from_function_with_optional_param(self, sample_tool_function_with_optional):
        """Test creating tool with optional parameters."""
        tool = Tool.from_function(sample_tool_function_with_optional)

        assert tool.name == "greet"
        assert len(tool.parameters) == 2

        params = {p.name: p for p in tool.parameters}
        assert params["name"].required is True
        assert params["greeting"].required is False
        assert params["greeting"].default == "Hello"

    def test_tool_from_function_with_custom_name(self, sample_tool_function):
        """Test creating tool with custom name."""
        tool = Tool.from_function(sample_tool_function, name="custom_add")

        assert tool.name == "custom_add"
        assert "Add two numbers together" in tool.description

    def test_tool_call(self, sample_tool_function):
        """Test calling a tool."""
        tool = Tool.from_function(sample_tool_function)

        result = tool(a=5, b=3)
        assert result == 8

    def test_tool_to_openai_format(self, sample_tool_function):
        """Test converting tool to OpenAI function format."""
        tool = Tool.from_function(sample_tool_function)

        openai_format = tool.to_openai_format()

        assert openai_format["type"] == "function"
        assert openai_format["function"]["name"] == "add_numbers"
        assert "description" in openai_format["function"]
        assert "parameters" in openai_format["function"]

        params = openai_format["function"]["parameters"]
        assert params["type"] == "object"
        assert "a" in params["properties"]
        assert "b" in params["properties"]
        assert params["properties"]["a"]["type"] == "integer"
        assert params["properties"]["b"]["type"] == "integer"
        assert set(params["required"]) == {"a", "b"}

    def test_tool_to_anthropic_format(self, sample_tool_function):
        """Test converting tool to Anthropic format."""
        tool = Tool.from_function(sample_tool_function)

        anthropic_format = tool.to_anthropic_format()

        assert anthropic_format["name"] == "add_numbers"
        assert "description" in anthropic_format
        assert "input_schema" in anthropic_format

        schema = anthropic_format["input_schema"]
        assert schema["type"] == "object"
        assert "a" in schema["properties"]
        assert "b" in schema["properties"]
        assert set(schema["required"]) == {"a", "b"}

    def test_python_type_to_json_type_conversions(self):
        """Test type conversion from Python to JSON types."""
        tool = Tool(
            name="test",
            description="Test tool",
            parameters=[],
            function=lambda: None,
        )

        assert tool._python_type_to_json_type(str) == "string"
        assert tool._python_type_to_json_type(int) == "integer"
        assert tool._python_type_to_json_type(float) == "number"
        assert tool._python_type_to_json_type(bool) == "boolean"
        assert tool._python_type_to_json_type(list) == "array"
        assert tool._python_type_to_json_type(dict) == "object"


class TestToolRegistry:
    """Tests for ToolRegistry class."""

    def test_create_empty_registry(self):
        """Test creating an empty tool registry."""
        registry = ToolRegistry()

        assert len(registry) == 0
        assert registry.get_all() == []

    def test_register_function(self, sample_tool_function):
        """Test registering a function as a tool."""
        registry = ToolRegistry()

        tool = registry.register_function(sample_tool_function)

        assert tool.name == "add_numbers"
        assert len(registry) == 1
        assert registry.get("add_numbers") == tool

    def test_register_function_with_custom_name(self, sample_tool_function):
        """Test registering a function with custom name."""
        registry = ToolRegistry()

        tool = registry.register_function(sample_tool_function, name="my_add")

        assert tool.name == "my_add"
        assert registry.get("my_add") == tool
        assert registry.get("add_numbers") is None

    def test_register_multiple_tools(self, sample_tool_function, sample_tool_function_with_optional):
        """Test registering multiple tools."""
        registry = ToolRegistry()

        tool1 = registry.register_function(sample_tool_function)
        tool2 = registry.register_function(sample_tool_function_with_optional)

        assert len(registry) == 2
        assert registry.get("add_numbers") == tool1
        assert registry.get("greet") == tool2

    def test_get_nonexistent_tool(self):
        """Test getting a tool that doesn't exist."""
        registry = ToolRegistry()

        assert registry.get("nonexistent") is None

    def test_get_all_tools(self, sample_tool_function, sample_tool_function_with_optional):
        """Test getting all tools from registry."""
        registry = ToolRegistry()

        registry.register_function(sample_tool_function)
        registry.register_function(sample_tool_function_with_optional)

        all_tools = registry.get_all()
        assert len(all_tools) == 2
        tool_names = {t.name for t in all_tools}
        assert tool_names == {"add_numbers", "greet"}

    def test_remove_tool(self, sample_tool_function):
        """Test removing a tool from registry."""
        registry = ToolRegistry()

        registry.register_function(sample_tool_function)
        assert len(registry) == 1

        registry.remove("add_numbers")
        assert len(registry) == 0
        assert registry.get("add_numbers") is None

    def test_remove_nonexistent_tool(self):
        """Test removing a tool that doesn't exist (should not error)."""
        registry = ToolRegistry()

        # Should not raise error
        registry.remove("nonexistent")
        assert len(registry) == 0

    def test_clear_registry(self, sample_tool_function, sample_tool_function_with_optional):
        """Test clearing all tools from registry."""
        registry = ToolRegistry()

        registry.register_function(sample_tool_function)
        registry.register_function(sample_tool_function_with_optional)
        assert len(registry) == 2

        registry.clear()
        assert len(registry) == 0
        assert registry.get_all() == []

    def test_tool_overwrite(self, sample_tool_function):
        """Test that registering a tool with same name overwrites it."""
        registry = ToolRegistry()

        tool1 = registry.register_function(sample_tool_function)

        # Register again with same name
        def different_add(x: int, y: int) -> int:
            """Different add function."""
            return x + y + 1

        tool2 = registry.register_function(different_add, name="add_numbers")

        assert len(registry) == 1
        assert registry.get("add_numbers") == tool2
        assert registry.get("add_numbers") != tool1
