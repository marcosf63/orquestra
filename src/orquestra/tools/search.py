"""Web search tool using DuckDuckGo (ddgs package)."""

from __future__ import annotations

from typing import Any

from orquestra.tools.exceptions import MissingDependencyError


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)

    Returns:
        Formatted search results as a string

    Raises:
        MissingDependencyError: If ddgs is not installed
    """
    try:
        from ddgs import DDGS
    except ImportError as e:
        raise MissingDependencyError(
            "ddgs",
            "uv add orquestra --optional search"
        ) from e

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return f"No results found for: {query}"

        # Format results
        formatted = f"Search results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            body = result.get("body", "No description")
            link = result.get("href", "")

            formatted += f"{i}. {title}\n"
            formatted += f"   {body}\n"
            if link:
                formatted += f"   URL: {link}\n"
            formatted += "\n"

        return formatted.strip()

    except Exception as e:
        return f"Search error: {str(e)}"


def news_search(query: str, max_results: int = 5) -> str:
    """Search for news articles.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)

    Returns:
        Formatted news results as a string

    Raises:
        MissingDependencyError: If ddgs is not installed
    """
    try:
        from ddgs import DDGS
    except ImportError as e:
        raise MissingDependencyError(
            "ddgs",
            "uv add orquestra --optional search"
        ) from e

    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=max_results))

        if not results:
            return f"No news found for: {query}"

        # Format results
        formatted = f"News results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            body = result.get("body", "No description")
            source = result.get("source", "Unknown")
            date = result.get("date", "")
            link = result.get("url", "")

            formatted += f"{i}. {title}\n"
            formatted += f"   Source: {source}"
            if date:
                formatted += f" | {date}"
            formatted += "\n"
            formatted += f"   {body}\n"
            if link:
                formatted += f"   URL: {link}\n"
            formatted += "\n"

        return formatted.strip()

    except Exception as e:
        return f"News search error: {str(e)}"


class SearchTool:
    """Collection of search tools for agents."""

    @staticmethod
    def web(query: str, max_results: int = 5) -> str:
        """Search the web.

        Args:
            query: Search query
            max_results: Maximum results

        Returns:
            Search results
        """
        return web_search(query, max_results)

    @staticmethod
    def news(query: str, max_results: int = 5) -> str:
        """Search news.

        Args:
            query: Search query
            max_results: Maximum results

        Returns:
            News results
        """
        return news_search(query, max_results)
