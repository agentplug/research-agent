"""
Response formatter for structuring research results.

This module handles the formatting of research results into different
output formats and structures.
"""

from typing import Any, Dict, List

from ....utils.utils import format_response, get_current_timestamp


class ResponseFormatter:
    """Formats research results into structured responses."""

    def __init__(self):
        """Initialize response formatter."""
        pass

    def build_multi_round_response(
        self,
        rounds: List[Dict[str, Any]],
        mode: str,
    ) -> Dict[str, Any]:
        """
        Build multi-round response structure.

        Args:
            rounds: List of round results
            mode: Research mode

        Returns:
            Formatted multi-round response
        """
        return {
            "research_summary": f"Research completed in {len(rounds)} rounds",
            "total_rounds": len(rounds),
            "mode": mode,
            "rounds": rounds,
            "timestamp": get_current_timestamp(),
        }

    def format_instant_response(self, content: str) -> str:
        """
        Format instant research response.

        Args:
            content: Research content

        Returns:
            Formatted instant response
        """
        return content

    def format_quick_response(self, rounds: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format quick research response.

        Args:
            rounds: List of round results

        Returns:
            Formatted quick response
        """
        return self.build_multi_round_response(rounds, "quick")

    def format_standard_response(self, rounds: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format standard research response.

        Args:
            rounds: List of round results

        Returns:
            Formatted standard response
        """
        return self.build_multi_round_response(rounds, "standard")

    def format_deep_response(self, rounds: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Format deep research response.

        Args:
            rounds: List of round results

        Returns:
            Formatted deep response
        """
        return self.build_multi_round_response(rounds, "deep")

    def format_error_response(
        self, error_message: str, mode: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Format error response.

        Args:
            error_message: Error message
            mode: Research mode

        Returns:
            Formatted error response
        """
        return {
            "error": True,
            "message": error_message,
            "mode": mode,
            "timestamp": get_current_timestamp(),
        }

    def format_clarification_response(self, questions: List[str]) -> Dict[str, Any]:
        """
        Format clarification response.

        Args:
            questions: List of clarification questions

        Returns:
            Formatted clarification response
        """
        return {
            "clarification_needed": True,
            "questions": questions,
            "timestamp": get_current_timestamp(),
        }

    def format_intention_response(self, intention: str) -> Dict[str, Any]:
        """
        Format intention response.

        Args:
            intention: User intention paragraph

        Returns:
            Formatted intention response
        """
        return {
            "intention_generated": True,
            "intention": intention,
            "timestamp": get_current_timestamp(),
        }

    def get_response_statistics(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about a response.

        Args:
            response: Response dictionary

        Returns:
            Response statistics
        """
        stats = {
            "has_error": response.get("error", False),
            "timestamp": response.get("timestamp"),
        }

        if "rounds" in response:
            stats["total_rounds"] = len(response["rounds"])
            stats["mode"] = response.get("mode", "unknown")

            # Calculate content statistics
            total_content_length = 0
            for round_data in response["rounds"]:
                content = round_data.get("content", "")
                total_content_length += len(content)

            stats["total_content_length"] = total_content_length
            stats["avg_content_length"] = (
                total_content_length / len(response["rounds"])
                if response["rounds"]
                else 0
            )

        return stats

    def validate_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate response structure.

        Args:
            response: Response dictionary

        Returns:
            Validation results
        """
        validation = {"is_valid": True, "errors": [], "warnings": []}

        # Check required fields
        if "timestamp" not in response:
            validation["errors"].append("Missing timestamp field")
            validation["is_valid"] = False

        # Check for error responses
        if response.get("error", False):
            if "message" not in response:
                validation["errors"].append("Error response missing message")
                validation["is_valid"] = False

        # Check for multi-round responses
        if "rounds" in response:
            rounds = response["rounds"]
            if not isinstance(rounds, list):
                validation["errors"].append("Rounds field must be a list")
                validation["is_valid"] = False
            else:
                for i, round_data in enumerate(rounds):
                    if not isinstance(round_data, dict):
                        validation["errors"].append(f"Round {i} must be a dictionary")
                        validation["is_valid"] = False
                    else:
                        required_fields = [
                            "round_number",
                            "query",
                            "content",
                            "timestamp",
                        ]
                        for field in required_fields:
                            if field not in round_data:
                                validation["errors"].append(
                                    f"Round {i} missing {field} field"
                                )
                                validation["is_valid"] = False

        return validation
