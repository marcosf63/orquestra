"""Exceptions for built-in tools."""

from __future__ import annotations


class MissingDependencyError(ImportError):
    """Raised when a required dependency for a tool is not installed.

    Attributes:
        dependency: Name of the missing dependency package
        install_command: Command to install the dependency
    """

    def __init__(self, dependency: str, install_command: str) -> None:
        """Initialize the exception.

        Args:
            dependency: Name of the missing package
            install_command: Command to install it (e.g., "uv add orquestra --optional search")
        """
        self.dependency = dependency
        self.install_command = install_command
        message = (
            f"Required dependency '{dependency}' is not installed.\n"
            f"Install it with: {install_command}"
        )
        super().__init__(message)
