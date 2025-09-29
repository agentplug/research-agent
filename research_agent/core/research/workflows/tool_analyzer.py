"""
Tool-aware analyzer for processing tool results and enhancing content.

This module handles the analysis of tool results and enhancement of content
with tool-provided information.
"""

from typing import Any, Dict, List, Optional

from ..source_processing import SourceProcessor


class ToolAwareAnalyzer:
    """Analyzes tool results and enhances content with tool-provided information."""

    def __init__(self, llm_service, source_processor: SourceProcessor):
        """
        Initialize tool-aware analyzer.

        Args:
            llm_service: LLM service instance
            source_processor: Source processor instance
        """
        self.llm_service = llm_service
        self.source_processor = source_processor

    def enhance_content_with_tools(
        self,
        tool_results: List[Dict[str, Any]],
        original_query: str,
        follow_up_query: str = "",
    ) -> str:
        """
        Enhance content with tool results using per-source processing.

        Args:
            tool_results: Results from tool executions
            original_query: Original research query
            follow_up_query: Current follow-up query

        Returns:
            Enhanced content with tool information
        """
        if not tool_results:
            return "No tool results available for content enhancement."

        # Process sources individually for better analysis
        processed_sources = self.source_processor.process_sources(
            tool_results, original_query, follow_up_query
        )

        if not processed_sources:
            return "No relevant information found from tool results."

        # Synthesize processed sources into comprehensive answer
        synthesized_content = self.source_processor.synthesize_sources(
            processed_sources, original_query, follow_up_query
        )

        return synthesized_content

    def analyze_tool_results(
        self,
        tool_results: List[Dict[str, Any]],
        query: str,
    ) -> Dict[str, Any]:
        """
        Analyze tool results for relevance and quality.

        Args:
            tool_results: Results from tool executions
            query: Research query

        Returns:
            Analysis results dictionary
        """
        if not tool_results:
            return {
                "total_results": 0,
                "successful_results": 0,
                "success_rate": 0.0,
                "tool_types": {},
                "relevance_score": 0.0,
            }

        successful_results = [r for r in tool_results if r.get("success", False)]
        tool_types = {}
        total_relevance = 0.0
        relevant_sources = 0

        for result in successful_results:
            tool_name = result.get("tool_name", "unknown")
            tool_types[tool_name] = tool_types.get(tool_name, 0) + 1

            # Process sources to get relevance scores
            processed_sources = self.source_processor.process_sources(
                [result], query, ""
            )

            for source in processed_sources:
                relevance_score = source.get("relevance_score", 0.0)
                total_relevance += relevance_score
                if relevance_score > 0.0:
                    relevant_sources += 1

        avg_relevance = (
            total_relevance / len(processed_sources) if processed_sources else 0.0
        )

        return {
            "total_results": len(tool_results),
            "successful_results": len(successful_results),
            "success_rate": len(successful_results) / len(tool_results)
            if tool_results
            else 0.0,
            "tool_types": tool_types,
            "relevant_sources": relevant_sources,
            "avg_relevance_score": avg_relevance,
            "relevance_distribution": {
                "high_relevance": len(
                    [
                        s
                        for s in processed_sources
                        if s.get("relevance_score", 0.0) > 0.7
                    ]
                ),
                "medium_relevance": len(
                    [
                        s
                        for s in processed_sources
                        if 0.3 < s.get("relevance_score", 0.0) <= 0.7
                    ]
                ),
                "low_relevance": len(
                    [
                        s
                        for s in processed_sources
                        if s.get("relevance_score", 0.0) <= 0.3
                    ]
                ),
            },
        }

    def get_tool_usage_recommendations(
        self,
        query: str,
        available_tools: List[str],
    ) -> List[str]:
        """
        Get recommendations for which tools to use for a query.

        Args:
            query: Research query
            available_tools: List of available tools

        Returns:
            List of recommended tool names
        """
        recommendations = []

        query_lower = query.lower()

        # Web search recommendations
        if any(
            keyword in query_lower
            for keyword in ["current", "latest", "recent", "today", "now", "2025"]
        ):
            if "web_search" in available_tools:
                recommendations.append("web_search")

        # Calculation recommendations
        if any(
            keyword in query_lower
            for keyword in ["calculate", "compute", "math", "+", "-", "*", "/", "="]
        ):
            if "calculate" in available_tools:
                recommendations.append("calculate")

        # Document retrieval recommendations
        if any(
            keyword in query_lower
            for keyword in ["document", "file", "pdf", "text", "content"]
        ):
            if "document_retrieval" in available_tools:
                recommendations.append("document_retrieval")

        # Default to web search if no specific recommendations
        if not recommendations and "web_search" in available_tools:
            recommendations.append("web_search")

        return recommendations

    def validate_tool_results(
        self,
        tool_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Validate tool results for completeness and quality.

        Args:
            tool_results: Results from tool executions

        Returns:
            Validation results dictionary
        """
        validation_results = {
            "total_results": len(tool_results),
            "valid_results": 0,
            "invalid_results": 0,
            "validation_errors": [],
            "quality_metrics": {},
        }

        for i, result in enumerate(tool_results):
            try:
                # Check required fields
                if not isinstance(result, dict):
                    validation_results["validation_errors"].append(
                        f"Result {i}: Not a dictionary"
                    )
                    validation_results["invalid_results"] += 1
                    continue

                if "success" not in result:
                    validation_results["validation_errors"].append(
                        f"Result {i}: Missing 'success' field"
                    )
                    validation_results["invalid_results"] += 1
                    continue

                if "tool_name" not in result:
                    validation_results["validation_errors"].append(
                        f"Result {i}: Missing 'tool_name' field"
                    )
                    validation_results["invalid_results"] += 1
                    continue

                if "result" not in result:
                    validation_results["validation_errors"].append(
                        f"Result {i}: Missing 'result' field"
                    )
                    validation_results["invalid_results"] += 1
                    continue

                # Check result content
                tool_result = result.get("result", {})
                if not tool_result:
                    validation_results["validation_errors"].append(
                        f"Result {i}: Empty result content"
                    )
                    validation_results["invalid_results"] += 1
                    continue

                validation_results["valid_results"] += 1

            except Exception as e:
                validation_results["validation_errors"].append(
                    f"Result {i}: Validation error - {str(e)}"
                )
                validation_results["invalid_results"] += 1

        # Calculate quality metrics
        if validation_results["total_results"] > 0:
            validation_results["quality_metrics"] = {
                "validity_rate": validation_results["valid_results"]
                / validation_results["total_results"],
                "error_rate": validation_results["invalid_results"]
                / validation_results["total_results"],
            }

        return validation_results
