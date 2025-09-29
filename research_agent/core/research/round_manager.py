"""Round management for research workflows."""

from typing import Any, Dict, List

from ...utils.utils import get_current_timestamp


class RoundManager:
    """Manages research rounds and result building."""

    @staticmethod
    def build_research_summary(previous_results: List[Dict[str, Any]]) -> str:
        """Build a summary of previous research results."""
        return "\n".join(
            [
                f"Round {r['round']}:\nTried Query: {r['query']}\nReceived Answer: {r['content']}"
                for r in previous_results
            ]
        )

    @staticmethod
    def build_round_result(
        analysis: Dict[str, Any],
        followup_content: str,
        previous_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build the result dictionary for a follow-up round."""
        return {
            "round": len(previous_results) + 1,
            "query": analysis.get("next_query"),
            "content": followup_content,
            "timestamp": get_current_timestamp(),
            "analysis": analysis.get("analysis", ""),
            "gaps_targeted": analysis.get("gaps_identified", []),
        }

    @staticmethod
    def build_first_round_result(query: str, content: str) -> Dict[str, Any]:
        """Build the result dictionary for the first round."""
        return {
            "round": 1,
            "query": query,
            "content": content,
            "timestamp": get_current_timestamp(),
        }
