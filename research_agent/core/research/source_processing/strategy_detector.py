"""
Strategy detector for determining processing approach based on tool result structure.

This module analyzes tool results and determines the appropriate processing strategy
without hardcoding specific tool names.
"""

from typing import Any, Dict


class StrategyDetector:
    """Detects processing strategy based on tool result structure."""

    @staticmethod
    def determine_processing_strategy(
        tool_name: str, tool_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine the processing strategy for a tool based on its result structure.
        This allows for dynamic tool handling without hardcoding tool names.

        Args:
            tool_name: Name of the tool
            tool_result: Result from the tool execution

        Returns:
            Dictionary containing processing strategy information
        """
        # Check if the tool result contains multiple items (like web_search with "results" array)
        if "results" in tool_result and isinstance(tool_result["results"], list):
            return {
                "type": "multi_result",
                "results": tool_result["results"],
                "content_field": "content",  # Field containing the main content
                "title_field": "title",  # Field containing the title
                "url_field": "url",  # Field containing the URL
                "snippet_field": "snippet",  # Field containing snippet (fallback)
            }

        # Check if the tool result has structured content (like document_retrieval)
        elif "content" in tool_result or "text" in tool_result or "data" in tool_result:
            return {
                "type": "single_result",
                "content_field": "content"
                if "content" in tool_result
                else ("text" if "text" in tool_result else "data"),
                "title_field": "title" if "title" in tool_result else "name",
                "url_field": "url" if "url" in tool_result else "source",
                "snippet_field": "snippet" if "snippet" in tool_result else "summary",
            }

        # Default strategy for simple tools (like calculate)
        else:
            return {
                "type": "single_result",
                "content_field": "result",
                "title_field": "operation",
                "url_field": "source",
                "snippet_field": "summary",
            }

    @staticmethod
    def is_multi_result_strategy(strategy: Dict[str, Any]) -> bool:
        """Check if strategy is for multi-result processing."""
        return strategy.get("type") == "multi_result"

    @staticmethod
    def get_content_field(strategy: Dict[str, Any]) -> str:
        """Get the content field name from strategy."""
        return strategy.get("content_field", "content")

    @staticmethod
    def get_title_field(strategy: Dict[str, Any]) -> str:
        """Get the title field name from strategy."""
        return strategy.get("title_field", "title")

    @staticmethod
    def get_url_field(strategy: Dict[str, Any]) -> str:
        """Get the URL field name from strategy."""
        return strategy.get("url_field", "url")

    @staticmethod
    def get_snippet_field(strategy: Dict[str, Any]) -> str:
        """Get the snippet field name from strategy."""
        return strategy.get("snippet_field", "snippet")
