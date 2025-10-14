"""Filesystem tools for file operations."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def read_file(file_path: str) -> str:
    """Read contents of a file.

    Args:
        file_path: Path to the file to read

    Returns:
        File contents as string
    """
    try:
        path = Path(file_path).expanduser()
        if not path.exists():
            return f"Error: File not found: {file_path}"

        if not path.is_file():
            return f"Error: Path is not a file: {file_path}"

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return content

    except PermissionError:
        return f"Error: Permission denied: {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(file_path: str, content: str) -> str:
    """Write content to a file.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file

    Returns:
        Success or error message
    """
    try:
        path = Path(file_path).expanduser()

        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully wrote {len(content)} characters to {file_path}"

    except PermissionError:
        return f"Error: Permission denied: {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def list_directory(directory: str = ".", pattern: str = "*") -> str:
    """List contents of a directory.

    Args:
        directory: Directory path to list (default: current directory)
        pattern: Glob pattern to filter files (default: *)

    Returns:
        Formatted list of directory contents
    """
    try:
        path = Path(directory).expanduser()

        if not path.exists():
            return f"Error: Directory not found: {directory}"

        if not path.is_dir():
            return f"Error: Path is not a directory: {directory}"

        # Get matching items
        items = sorted(path.glob(pattern))

        if not items:
            return f"No items matching pattern '{pattern}' in {directory}"

        # Format output
        result = f"Contents of {directory} (pattern: {pattern}):\n\n"

        dirs = [item for item in items if item.is_dir()]
        files = [item for item in items if item.is_file()]

        if dirs:
            result += "Directories:\n"
            for d in dirs:
                result += f"  📁 {d.name}/\n"
            result += "\n"

        if files:
            result += "Files:\n"
            for f in files:
                size = f.stat().st_size
                size_str = _format_size(size)
                result += f"  📄 {f.name} ({size_str})\n"

        return result.strip()

    except PermissionError:
        return f"Error: Permission denied: {directory}"
    except Exception as e:
        return f"Error listing directory: {str(e)}"


def file_exists(file_path: str) -> str:
    """Check if a file exists.

    Args:
        file_path: Path to check

    Returns:
        Existence status message
    """
    try:
        path = Path(file_path).expanduser()

        if path.exists():
            if path.is_file():
                size = path.stat().st_size
                return f"File exists: {file_path} ({_format_size(size)})"
            elif path.is_dir():
                return f"Path exists but is a directory: {file_path}"
            else:
                return f"Path exists but is neither file nor directory: {file_path}"
        else:
            return f"File does not exist: {file_path}"

    except Exception as e:
        return f"Error checking file: {str(e)}"


def _format_size(size: int) -> str:
    """Format file size in human-readable format.

    Args:
        size: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


class FileSystemTool:
    """Collection of filesystem tools for agents."""

    @staticmethod
    def read(file_path: str) -> str:
        """Read a file.

        Args:
            file_path: Path to file

        Returns:
            File contents
        """
        return read_file(file_path)

    @staticmethod
    def write(file_path: str, content: str) -> str:
        """Write to a file.

        Args:
            file_path: Path to file
            content: Content to write

        Returns:
            Success message
        """
        return write_file(file_path, content)

    @staticmethod
    def list(directory: str = ".", pattern: str = "*") -> str:
        """List directory contents.

        Args:
            directory: Directory path
            pattern: Glob pattern

        Returns:
            Directory listing
        """
        return list_directory(directory, pattern)

    @staticmethod
    def exists(file_path: str) -> str:
        """Check if file exists.

        Args:
            file_path: Path to check

        Returns:
            Existence status
        """
        return file_exists(file_path)
