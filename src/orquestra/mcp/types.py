"""Minimal MCP types for client integration."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Tool(BaseModel):
    """MCP Tool definition."""

    name: str
    description: str | None = None
    input_schema: dict[str, Any] = Field(alias="inputSchema")

    class Config:
        populate_by_name = True


class ToolCallResult(BaseModel):
    """Result from calling an MCP tool."""

    content: list[dict[str, Any]]
    is_error: bool | None = Field(None, alias="isError")

    class Config:
        populate_by_name = True

    def get_text(self) -> str:
        """Extract text content from result."""
        if not self.content:
            return ""
        for item in self.content:
            if item.get("type") == "text":
                return item.get("text", "")
        return ""


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 Request."""

    jsonrpc: Literal["2.0"] = "2.0"
    id: int | str
    method: str
    params: dict[str, Any] | None = None


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 Response."""

    jsonrpc: Literal["2.0"] = "2.0"
    id: int | str
    result: Any | None = None
    error: dict[str, Any] | None = None
