#!/usr/bin/env python3
"""
Tool-Aware Research Workflows

Enhanced research workflows that integrate tool execution for comprehensive research.
"""

from typing import Any, Dict, List, Optional

from ...utils.utils import format_response, get_current_timestamp
from ..research.workflows_enhanced import ResearchWorkflows
from ..tools.tool_executor import ToolExecutor


class ToolAwareResearchWorkflows(ResearchWorkflows):
    """Research workflows with tool integration."""

    def __init__(
        self,
        llm_service,
        analysis_engine,
        clarification_engine,
        intention_generator,
        available_tools: List[str] = None,
        tool_descriptions: Dict[str, str] = None,
    ):
        """
        Initialize tool-aware research workflows.

        Args:
            llm_service: LLM service instance
            analysis_engine: Analysis engine instance
            clarification_engine: Clarification engine instance
            intention_generator: Intention generator instance
            available_tools: List of available tool names
            tool_descriptions: Dictionary of tool descriptions
        """
        super().__init__(
            llm_service, analysis_engine, clarification_engine, intention_generator
        )
        self.available_tools = available_tools or []
        self.tool_descriptions = tool_descriptions or {}
        self.tool_executor = (
            ToolExecutor(available_tools, tool_descriptions)
            if available_tools
            else None
        )

    def execute_first_round(
        self, query: str, mode: str, intention_paragraph: str = ""
    ) -> Dict[str, Any]:
        """
        Execute first round with tool integration.

        Args:
            query: Research query
            mode: Research mode
            intention_paragraph: Intention paragraph for deep research

        Returns:
            First round result with tool integration
        """
        # Build system prompt with tool context
        system_prompt = self._build_tool_aware_system_prompt(
            query, mode, intention_paragraph
        )

        # Generate response
        content = self.llm_service.generate(
            input_data=query,
            system_prompt=system_prompt,
            temperature=0.0,
        )

        # Check for tool calls in response
        tool_calls = (
            self.tool_executor.extract_tool_calls(content) if self.tool_executor else []
        )
        tools_used = []

        if tool_calls and self.tool_executor:
            # Execute tools and enhance content
            tool_results = self.tool_executor.execute_tools(tool_calls)
            tools_used = [
                result.get("tool_name")
                for result in tool_results
                if result.get("success")
            ]

            # Enhance content with tool results
            enhanced_content = self._enhance_content_with_tools(content, tool_results)
            content = enhanced_content

        return {
            "round": 1,
            "query": query,
            "content": content,
            "tools_used": tools_used,
            "tool_calls": tool_calls,
            "tool_results": tool_results if tool_calls else [],
            "timestamp": get_current_timestamp(),
        }

    def execute_follow_up_round(
        self,
        original_query: str,
        previous_results: List[Dict[str, Any]],
        mode: str,
        round_num: int,
        intention_paragraph: str = "",
    ) -> Dict[str, Any]:
        """
        Execute follow-up round with tool integration.

        Args:
            original_query: Original research query
            previous_results: Results from previous rounds
            mode: Research mode
            round_num: Current round number
            intention_paragraph: Intention paragraph for deep research

        Returns:
            Follow-up round result with tool integration
        """
        # Build analysis prompt with tool context
        analysis_prompt = self._build_tool_aware_analysis_prompt(
            original_query, previous_results, mode
        )

        # Perform analysis
        analysis_result = self.llm_service.generate(
            input_data=analysis_prompt,
            system_prompt="You are a research analysis expert. Analyze the research progress and determine next steps.",
            temperature=0.0,
        )

        # Parse analysis result
        try:
            import json

            analysis_data = json.loads(analysis_result)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            analysis_data = {
                "goal_reached": False,
                "identified_gaps": ["Analysis parsing failed"],
                "next_query": f"Continue research on: {original_query}",
                "reasoning": "Could not parse analysis result",
            }

        # Check if goal is reached
        if analysis_data.get("goal_reached", False):
            return {
                "round": round_num,
                "query": "Goal reached",
                "content": "Research goal has been achieved",
                "tools_used": [],
                "tool_calls": [],
                "tool_results": [],
                "goal_reached": True,
                "timestamp": get_current_timestamp(),
            }

        # Generate next query
        next_query = analysis_data.get(
            "next_query", f"Continue research on: {original_query}"
        )

        # Execute next query with tool integration
        system_prompt = self._build_tool_aware_system_prompt(
            next_query, mode, intention_paragraph
        )

        content = self.llm_service.generate(
            input_data=next_query,
            system_prompt=system_prompt,
            temperature=0.0,
        )

        # Check for tool calls in response
        tool_calls = (
            self.tool_executor.extract_tool_calls(content) if self.tool_executor else []
        )
        tools_used = []

        if tool_calls and self.tool_executor:
            # Execute tools and enhance content
            tool_results = self.tool_executor.execute_tools(tool_calls)
            tools_used = [
                result.get("tool_name")
                for result in tool_results
                if result.get("success")
            ]

            # Enhance content with tool results
            enhanced_content = self._enhance_content_with_tools(content, tool_results)
            content = enhanced_content

        return {
            "round": round_num,
            "query": next_query,
            "content": content,
            "tools_used": tools_used,
            "tool_calls": tool_calls,
            "tool_results": tool_results if tool_calls else [],
            "goal_reached": False,
            "timestamp": get_current_timestamp(),
        }

    def _build_tool_aware_system_prompt(
        self, query: str, mode: str, intention_paragraph: str = ""
    ) -> str:
        """
        Build system prompt with tool context.

        Args:
            query: Research query
            mode: Research mode
            intention_paragraph: Intention paragraph for deep research

        Returns:
            Enhanced system prompt with tool context
        """
        # Get base system prompt from parent class
        from datetime import date

        today = date.today()
        system_prompts = {
            "instant": f"Today's date: {today}. When users ask about 'current' information, interpret this as referring to {today} (September 2025). Always include relevant temporal context in search queries. Provide quick, accurate answers. Focus on key facts.",
            "quick": f"Today's date: {today}. When users ask about 'current' information, interpret this as referring to {today} (September 2025). Always include relevant temporal context in search queries. Provide enhanced analysis with context and examples.",
            "standard": f"Today's date: {today}. When users ask about 'current' information, interpret this as referring to {today} (September 2025). Always include relevant temporal context in search queries. Conduct comprehensive research with multiple perspectives.",
            "deep": f"Today's date: {today}. When users ask about 'current' information, interpret this as referring to {today} (September 2025). Always include relevant temporal context in search queries. Conduct exhaustive research with academic-level analysis.",
        }

        base_prompt = system_prompts.get(mode, "You are a helpful research assistant.")

        # Add intention paragraph for deep research
        if mode == "deep" and intention_paragraph:
            base_prompt = f"{base_prompt}\n\n{intention_paragraph}\n\nEnsure all research aligns with this intention and addresses the specific focus areas mentioned."

        if self.available_tools:
            tool_context = self._build_tool_context_string()
            return f"{base_prompt}\n\n{tool_context}"

        return base_prompt

    def _build_tool_aware_analysis_prompt(
        self, original_query: str, previous_results: List[Dict[str, Any]], mode: str
    ) -> str:
        """
        Build analysis prompt with tool context.

        Args:
            original_query: Original research query
            previous_results: Results from previous rounds
            mode: Research mode

        Returns:
            Enhanced analysis prompt with tool context
        """
        # Build research summary from previous results
        research_summary = self._build_research_summary(previous_results)

        # Get base analysis prompt from analysis engine
        base_prompt = self.analysis_engine.build_analysis_prompt(
            original_query, research_summary, mode
        )

        if self.available_tools:
            tool_context = self._build_tool_context_for_analysis()
            return f"{base_prompt}\n\n{tool_context}"

        return base_prompt

    def _build_research_summary(self, previous_results: List[Dict[str, Any]]) -> str:
        """Build research summary from previous results."""
        if not previous_results:
            return ""

        summary_parts = []
        for i, result in enumerate(previous_results, 1):
            query = result.get("query", f"Round {i}")
            content = result.get("content", "")
            tools_used = result.get("tools_used", [])

            summary_parts.append(f"Round {i}: {query}")
            if tools_used:
                summary_parts.append(f"Tools used: {', '.join(tools_used)}")
            summary_parts.append(f"Content: {content[:200]}...")
            summary_parts.append("")

        return "\n".join(summary_parts)

    def _build_tool_context_string(self) -> str:
        """
        Build tool context string for system prompts.

        Returns:
            Tool context string
        """
        if not self.available_tools:
            return ""

        tool_descriptions = []
        for tool_name in self.available_tools:
            description = self.tool_descriptions.get(tool_name, f"Tool: {tool_name}")
            tool_descriptions.append(
                f"""
Tool: {tool_name}
Description: {description}
"""
            )

        return f"""
TOOL INTEGRATION CONTEXT:
You have access to the following tools. Use them when appropriate for the research task.

{''.join(tool_descriptions)}

TOOL USAGE RULES:
1. Use tools when they can provide better, more current, or more specific information
2. For web searches, use web_search tool instead of relying on training data
3. For calculations, use math tools instead of manual computation
4. For document analysis, use document_retrieval tool
5. Always format tool calls as JSON with "tool_call" structure

TOOL CALL FORMAT:
{{
    "tool_call": {{
        "tool_name": "tool_name",
        "arguments": {{"param1": "value1", "param2": "value2"}}
    }},
    "analysis": "I will use the tool to perform this operation"
}}

EXAMPLES:
- "What's the latest news about AI?" → {{"tool_call": {{"tool_name": "web_search", "arguments": {{"query": "latest AI news 2024"}}}}}}
- "Calculate 15% of 250" → {{"tool_call": {{"tool_name": "calculate", "arguments": {{"expression": "250 * 0.15"}}}}}}
- "Extract key points from this document" → {{"tool_call": {{"tool_name": "document_retrieval", "arguments": {{"file_path": "document.pdf", "extract_type": "key_points"}}}}}}

IMPORTANT: Use tools when they can provide better information than your training data. Always format responses as JSON with "tool_call" structure.
"""

    def _build_tool_context_for_analysis(self) -> str:
        """
        Build tool context specifically for analysis.

        Returns:
            Tool context string for analysis
        """
        if not self.available_tools:
            return ""

        return f"""
TOOL INTEGRATION FOR ANALYSIS:
You have access to these tools: {', '.join(self.available_tools)}

When analyzing research gaps, consider if any tools could help gather missing information:
- web_search: For current information, news, recent developments
- document_retrieval: For extracting information from documents
- data_analysis: For statistical analysis and calculations
- calculate: For mathematical computations

If tools could help fill gaps, suggest their use in your analysis and provide specific tool call examples.
"""

    def _enhance_content_with_tools(
        self, original_content: str, tool_results: List[Dict[str, Any]]
    ) -> str:
        """
        Enhance content with tool results.

        Args:
            original_content: Original LLM content
            tool_results: Results from tool executions

        Returns:
            Enhanced content with tool results integrated
        """
        if not tool_results:
            return original_content

        # Create tool results summary
        tool_summary = []
        for result in tool_results:
            if result.get("success", False):
                tool_name = result.get("tool_name", "unknown")
                tool_result = result.get("result", {})

                if tool_name == "web_search":
                    search_results = tool_result.get("results", [])
                    if search_results:
                        tool_summary.append(
                            f"Web search results for '{tool_result.get('query', '')}':"
                        )
                        for i, search_result in enumerate(
                            search_results[:3], 1
                        ):  # Limit to 3 results
                            tool_summary.append(
                                f"{i}. {search_result.get('title', 'No title')}"
                            )
                            tool_summary.append(
                                f"   {search_result.get('snippet', 'No snippet')}"
                            )
                            tool_summary.append(
                                f"   URL: {search_result.get('url', 'No URL')}"
                            )
                        tool_summary.append("")

                elif tool_name == "calculate":
                    expression = tool_result.get("expression", "")
                    calc_result = tool_result.get("result", "Error")
                    tool_summary.append(f"Calculation: {expression} = {calc_result}")

                elif tool_name == "document_retrieval":
                    content = tool_result.get("content", "")
                    tool_summary.append(f"Document content: {content}")

        # Combine original content with tool results
        if tool_summary:
            enhanced_content = f"{original_content}\n\n--- TOOL RESULTS ---\n{chr(10).join(tool_summary)}"
            return enhanced_content

        return original_content

    def get_tool_usage_stats(self) -> Dict[str, Any]:
        """
        Get tool usage statistics.

        Returns:
            Dictionary with tool usage statistics
        """
        if not self.tool_executor:
            return {
                "has_tools": False,
                "available_tools": self.available_tools,
                "tool_count": len(self.available_tools),
            }

        stats = self.tool_executor.get_tool_usage_stats()
        stats["has_tools"] = len(self.available_tools) > 0
        stats["available_tools"] = self.available_tools
        stats["tool_count"] = len(self.available_tools)

        return stats
