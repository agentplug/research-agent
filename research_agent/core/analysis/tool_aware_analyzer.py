#!/usr/bin/env python3
"""
Tool-Aware Analysis Engine

Enhanced analysis engine that integrates tool context for better research analysis.
"""

from typing import Any, Dict, List, Optional

from .analyzer import AnalysisEngine


class ToolAwareAnalysisEngine(AnalysisEngine):
    """Analysis engine with tool integration capabilities."""

    def __init__(
        self,
        llm_service,
        available_tools: List[str] = None,
        tool_descriptions: Dict[str, str] = None,
    ):
        """
        Initialize tool-aware analysis engine.

        Args:
            llm_service: LLM service instance
            available_tools: List of available tool names
            tool_descriptions: Dictionary of tool descriptions
        """
        super().__init__(llm_service)
        self.available_tools = available_tools or []
        self.tool_descriptions = tool_descriptions or {}

    def build_analysis_prompt(
        self, original_query: str, research_summary: str, mode: str
    ) -> str:
        """
        Build analysis prompt with tool context.

        Args:
            original_query: Original research query
            research_summary: Summary of research conducted so far
            mode: Research mode (instant, quick, standard, deep)

        Returns:
            Enhanced analysis prompt with tool context
        """
        base_prompt = super().build_analysis_prompt(
            original_query, research_summary, mode
        )

        if self.available_tools:
            tool_context = self._build_tool_context_for_analysis()
            return f"{base_prompt}\n\n{tool_context}"

        return base_prompt

    def _build_tool_context_for_analysis(self) -> str:
        """
        Build tool context specifically for analysis.

        Returns:
            Tool context string for analysis
        """
        if not self.available_tools:
            return ""

        tool_descriptions = []
        for tool_name in self.available_tools:
            description = self.tool_descriptions.get(tool_name, f"Tool: {tool_name}")
            tool_descriptions.append(f"- {tool_name}: {description}")

        return f"""
TOOL INTEGRATION CONTEXT:
You have access to these tools: {', '.join(self.available_tools)}

Tool Descriptions:
{chr(10).join(tool_descriptions)}

When analyzing research gaps, consider if any tools could help gather missing information:
- web_search: For current information, news, recent developments, real-time data
- document_retrieval: For extracting information from documents, PDFs, reports
- data_analysis: For statistical analysis, calculations, data processing
- calculate: For mathematical calculations and computations

TOOL USAGE GUIDELINES:
1. If the research needs current information (news, recent developments) → suggest web_search
2. If the research needs document analysis → suggest document_retrieval
3. If the research needs calculations or data analysis → suggest calculate or data_analysis
4. If tools could help fill gaps, suggest their use in your analysis
5. Always consider tool capabilities when evaluating research completeness

IMPORTANT: When suggesting tool usage, provide specific arguments and explain how the tool would help fill identified gaps.
"""

    def analyze_with_tool_suggestions(
        self, original_query: str, research_summary: str, mode: str
    ) -> Dict[str, Any]:
        """
        Perform analysis with tool suggestions.

        Args:
            original_query: Original research query
            research_summary: Summary of research conducted so far
            mode: Research mode

        Returns:
            Analysis result with tool suggestions
        """
        # Get base analysis
        analysis_result = self.analyze_research_gaps(
            original_query, research_summary, mode
        )

        # Add tool suggestions if tools are available
        if self.available_tools and analysis_result.get("success", False):
            tool_suggestions = self._generate_tool_suggestions(
                original_query, research_summary, analysis_result.get("data", {})
            )
            analysis_result["tool_suggestions"] = tool_suggestions

        return analysis_result

    def _generate_tool_suggestions(
        self, original_query: str, research_summary: str, analysis_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate tool suggestions based on analysis.

        Args:
            original_query: Original research query
            research_summary: Research summary
            analysis_data: Analysis data

        Returns:
            List of tool suggestions
        """
        suggestions = []

        # Check if we need current information
        if self._needs_current_information(original_query, research_summary):
            suggestions.append(
                {
                    "tool_name": "web_search",
                    "reason": "Research requires current information or recent developments",
                    "arguments": {
                        "query": f"{original_query} recent developments 2024"
                    },
                    "priority": "high",
                }
            )

        # Check if we need calculations
        if self._needs_calculations(original_query, research_summary):
            suggestions.append(
                {
                    "tool_name": "calculate",
                    "reason": "Research involves mathematical calculations",
                    "arguments": {"expression": "TBD - specific calculation needed"},
                    "priority": "medium",
                }
            )

        # Check if we need document analysis
        if self._needs_document_analysis(original_query, research_summary):
            suggestions.append(
                {
                    "tool_name": "document_retrieval",
                    "reason": "Research requires document analysis or extraction",
                    "arguments": {
                        "file_path": "TBD - specific document needed",
                        "extract_type": "key_points",
                    },
                    "priority": "medium",
                }
            )

        return suggestions

    def _needs_current_information(self, query: str, summary: str) -> bool:
        """Check if research needs current information."""
        current_keywords = [
            "latest",
            "recent",
            "current",
            "new",
            "today",
            "now",
            "2024",
            "2025",
            "breaking",
            "update",
            "news",
            "trends",
            "developments",
        ]

        query_lower = query.lower()
        summary_lower = summary.lower()

        return any(
            keyword in query_lower or keyword in summary_lower
            for keyword in current_keywords
        )

    def _needs_calculations(self, query: str, summary: str) -> bool:
        """Check if research needs calculations."""
        calc_keywords = [
            "calculate",
            "compute",
            "math",
            "statistics",
            "percentage",
            "ratio",
            "formula",
            "equation",
            "sum",
            "average",
            "total",
            "rate",
        ]

        query_lower = query.lower()
        summary_lower = summary.lower()

        return any(
            keyword in query_lower or keyword in summary_lower
            for keyword in calc_keywords
        )

    def _needs_document_analysis(self, query: str, summary: str) -> bool:
        """Check if research needs document analysis."""
        doc_keywords = [
            "document",
            "pdf",
            "report",
            "paper",
            "file",
            "extract",
            "analyze",
            "summarize",
            "review",
            "study",
            "research paper",
            "publication",
        ]

        query_lower = query.lower()
        summary_lower = summary.lower()

        return any(
            keyword in query_lower or keyword in summary_lower
            for keyword in doc_keywords
        )

    def enhance_analysis_with_tools(
        self, analysis_result: Dict[str, Any], tool_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Enhance analysis result with tool execution results.

        Args:
            analysis_result: Original analysis result
            tool_results: Results from tool executions

        Returns:
            Enhanced analysis result
        """
        if not tool_results:
            return analysis_result

        # Add tool results to analysis
        analysis_result["tool_results"] = tool_results

        # Update analysis based on tool results
        if analysis_result.get("success", False):
            data = analysis_result.get("data", {})

            # Check if tools filled the gaps
            if tool_results:
                data["tools_used"] = [
                    result.get("tool_name")
                    for result in tool_results
                    if result.get("success")
                ]
                data["tool_success"] = all(
                    result.get("success", False) for result in tool_results
                )

                # If tools were successful, mark goal as potentially reached
                if data.get("tool_success", False):
                    data["goal_reached"] = True
                    data["next_query"] = None
                    data["reasoning"] = "Research goal reached with tool assistance"

        return analysis_result
