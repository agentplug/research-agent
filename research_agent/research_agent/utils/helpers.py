"""Helper functions for research agent."""

from typing import Any, Dict, List


class ResearchHelpers:
    """Helper functions for research operations."""

    @staticmethod
    def validate_mode(mode: str) -> bool:
        """Validate if mode is supported."""
        supported_modes = {"instant", "quick", "standard", "deep"}
        return mode in supported_modes

    @staticmethod
    def get_mode_description(mode: str) -> str:
        """Get description for a research mode."""
        descriptions = {
            "instant": "Single round quick answer",
            "quick": "2 rounds with gap analysis",
            "standard": "3 rounds with comprehensive analysis",
            "deep": "4 rounds with exhaustive analysis",
        }
        return descriptions.get(mode, "Unknown mode")

    @staticmethod
    def get_available_modes() -> List[str]:
        """Get list of available research modes."""
        return ["instant", "quick", "standard", "deep"]

    @staticmethod
    def format_research_history_entry(
        mode: str, query: str, result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format an entry for research history."""
        return {
            "mode": mode,
            "query": query,
            "result": result,
            "timestamp": result.get("data", {}).get("timestamp"),
        }
