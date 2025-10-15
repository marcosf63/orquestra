"""Unit tests for built-in tools."""

import pytest

from orquestra.tools import MissingDependencyError, calculate, convert_units, python_eval
from orquestra.tools import file_exists, list_directory, read_file, write_file


class TestComputationTools:
    """Tests for computation tools."""

    def test_calculate_basic(self):
        """Test basic calculation."""
        result = calculate("2 + 2")
        assert "= 4" in result

    def test_calculate_complex(self):
        """Test complex calculation."""
        result = calculate("(10 + 5) * 2 - 3")
        assert "= 27" in result

    def test_calculate_multiplication(self):
        """Test multiplication."""
        result = calculate("7 * 6")
        assert "= 42" in result

    def test_calculate_division(self):
        """Test division."""
        result = calculate("15 / 3")
        assert "= 5" in result

    def test_calculate_power(self):
        """Test exponentiation."""
        result = calculate("2 ** 8")
        assert "= 256" in result

    def test_calculate_invalid_expression(self):
        """Test that invalid expression returns error message."""
        result = calculate("invalid expression")
        assert "error" in result.lower()

    def test_python_eval_simple(self):
        """Test simple Python evaluation."""
        result = python_eval("len([1, 2, 3, 4])")
        assert result == "4"

    def test_python_eval_string_operations(self):
        """Test string operations."""
        result = python_eval("'hello'.upper()")
        assert result == "HELLO"

    def test_convert_units_temperature(self):
        """Test temperature conversion."""
        # Temperature conversion not supported - should return error
        result = convert_units(0, "celsius", "fahrenheit")
        assert "Error" in result or "Unsupported" in result

    def test_convert_units_length(self):
        """Test length conversion."""
        # Length conversion not supported - should return error
        result = convert_units(1, "meter", "centimeter")
        assert "Error" in result or "Unsupported" in result

    def test_calculate_with_math_functions(self):
        """Test calculations with mathematical functions."""
        result = calculate("sqrt(16)")
        assert "= 4" in result

        result = calculate("abs(-5)")
        assert "= 5" in result

        result = calculate("round(3.7)")
        assert "= 4" in result

    def test_calculate_with_constants(self):
        """Test calculations with mathematical constants."""
        result = calculate("pi")
        assert "3.14" in result

        result = calculate("e")
        assert "2.7" in result

    def test_calculate_min_max(self):
        """Test min and max functions."""
        result = calculate("min(5, 3, 8)")
        assert "= 3" in result

        result = calculate("max(5, 3, 8)")
        assert "= 8" in result

    def test_calculate_modulo(self):
        """Test modulo operation."""
        result = calculate("10 % 3")
        assert "= 1" in result

    def test_calculate_floor_division(self):
        """Test floor division."""
        result = calculate("10 // 3")
        assert "= 3" in result

    def test_python_eval_list_operations(self):
        """Test Python eval with list operations."""
        # List comprehensions
        result = python_eval("[x * 2 for x in [1, 2, 3]]")
        assert "[2, 4, 6]" in result

        # len() is allowed
        result = python_eval("len([3, 1, 4, 1, 5])")
        assert "5" in result

    def test_python_eval_dict_operations(self):
        """Test Python eval with dictionary operations."""
        result = python_eval("{'a': 1, 'b': 2}['a']")
        assert result == "1"

    def test_python_eval_error_handling(self):
        """Test that dangerous operations are blocked."""
        # Should return error message for dangerous operations
        result = python_eval("__import__('os').system('ls')")
        assert "error" in result.lower()

    def test_convert_units_weight(self):
        """Test weight conversion - not implemented."""
        result = convert_units(1, "kilogram", "gram")
        assert "Error" in result or "Unsupported" in result

    def test_convert_units_invalid_unit(self):
        """Test conversion with invalid units."""
        result = convert_units(1, "invalid_unit", "meter")
        assert "Error" in result or "Unsupported" in result

        result = convert_units(1, "meter", "invalid_unit")
        assert "Error" in result or "Unsupported" in result

    def test_convert_units_incompatible_types(self):
        """Test conversion between incompatible unit types."""
        result = convert_units(1, "meter", "kilogram")
        assert "Error" in result or "Unsupported" in result


class TestFilesystemTools:
    """Tests for filesystem tools."""

    def test_read_file(self, temp_file):
        """Test reading a file."""
        content = read_file(temp_file)
        assert content == "Test content"

    def test_read_file_not_found(self):
        """Test reading non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            read_file("/path/that/does/not/exist.txt")

    def test_read_file_is_directory(self, temp_dir):
        """Test reading a directory raises error."""
        with pytest.raises(ValueError, match="not a file"):
            read_file(temp_dir)

    def test_write_file(self, tmp_path):
        """Test writing to a file."""
        file_path = tmp_path / "new_file.txt"

        result = write_file(str(file_path), "New content")

        assert "Successfully wrote" in result
        assert file_path.exists()
        assert file_path.read_text() == "New content"

    def test_write_file_creates_directories(self, tmp_path):
        """Test that write_file creates parent directories."""
        file_path = tmp_path / "nested" / "dirs" / "file.txt"

        result = write_file(str(file_path), "Content")

        assert file_path.exists()
        assert file_path.read_text() == "Content"

    def test_list_directory(self, temp_dir):
        """Test listing directory contents."""
        result = list_directory(temp_dir)

        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "subdir" in result

    def test_list_directory_not_found(self):
        """Test listing non-existent directory raises error."""
        with pytest.raises(FileNotFoundError):
            list_directory("/path/that/does/not/exist")

    def test_list_directory_is_file(self, temp_file):
        """Test listing a file (not directory) raises error."""
        with pytest.raises(ValueError, match="not a directory"):
            list_directory(temp_file)

    def test_list_directory_with_pattern(self, temp_dir):
        """Test listing directory with glob pattern."""
        result = list_directory(temp_dir, pattern="*.txt")

        assert "file1.txt" in result
        assert "file2.txt" in result

    def test_file_exists_true(self, temp_file):
        """Test file_exists returns correct message for existing file."""
        result = file_exists(temp_file)

        assert "File exists" in result
        assert temp_file in result

    def test_file_exists_false(self):
        """Test file_exists for non-existent file."""
        result = file_exists("/nonexistent/path/file.txt")

        assert "does not exist" in result

    def test_file_exists_is_directory(self, temp_dir):
        """Test file_exists for directory."""
        result = file_exists(temp_dir)

        assert "directory" in result


class TestSearchTools:
    """Tests for search tools."""

    def test_web_search_missing_dependency(self, monkeypatch):
        """Test that web_search raises MissingDependencyError when ddgs not installed."""
        import sys

        # Remove ddgs from sys.modules if it exists
        if "ddgs" in sys.modules:
            monkeypatch.delitem(sys.modules, "ddgs")

        # Mock import to raise ImportError
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "ddgs":
                raise ImportError("No module named 'ddgs'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        # Now test
        from orquestra.tools import web_search

        with pytest.raises(MissingDependencyError) as exc_info:
            web_search("test query")

        assert "ddgs" in str(exc_info.value)
        assert "uv add orquestra --optional search" in str(exc_info.value)

    def test_web_search_with_ddgs_installed(self):
        """Test web_search when ddgs is installed (integration test)."""
        pytest.importorskip("ddgs", minversion=None)

        from orquestra.tools import web_search

        # This would actually call the API - skip in unit tests
        # Just verify it doesn't raise MissingDependencyError
        pytest.skip("Skipping actual web search in unit tests")


class TestToolExceptions:
    """Tests for tool exception handling."""

    def test_missing_dependency_error_attributes(self):
        """Test MissingDependencyError has correct attributes."""
        error = MissingDependencyError(
            "test-package",
            "pip install test-package"
        )

        assert error.dependency == "test-package"
        assert error.install_command == "pip install test-package"
        assert "test-package" in str(error)
        assert "pip install test-package" in str(error)

    def test_missing_dependency_error_message(self):
        """Test MissingDependencyError message format."""
        error = MissingDependencyError("ddgs", "uv add orquestra --optional search")

        message = str(error)
        assert "ddgs" in message
        assert "not installed" in message
        assert "uv add orquestra --optional search" in message
