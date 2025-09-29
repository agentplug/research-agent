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
        # Enhance query for better search results if it's about current information
        from datetime import date

        current_year = date.today().year

        enhanced_query = query
        if (
            "current" in query.lower()
            or "now" in query.lower()
            or "today" in query.lower()
        ):
            # Automatically add temporal context when user asks about "current" status
            enhanced_query = f'{query} {current_year} OR "as of {current_year}" OR "in {current_year}"'

        # Build system prompt with tool context
        system_prompt = self._build_tool_aware_system_prompt(
            query, mode, intention_paragraph
        )

        # Add temporal context to the input for better tool call generation
        input_with_context = query
        if (
            "current" in query.lower()
            or "now" in query.lower()
            or "today" in query.lower()
        ):
            input_with_context = f"{query}\n\nNote: When searching for 'current' information, include temporal context like '{current_year}' or 'as of {current_year}' to get the most recent and relevant results."

        # Generate response
        content = self.llm_service.generate(
            input_data=input_with_context,
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
            enhanced_content = self._enhance_content_with_tools(
                content, tool_results, query
            )
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

    def execute_followup_round(
        self,
        original_query: str,
        previous_results: List[Dict[str, Any]],
        mode: str,
        intention_paragraph: str = "",
    ) -> Optional[Dict[str, Any]]:
        """
        Execute follow-up round with tool integration.

        Args:
            original_query: Original research query
            previous_results: Results from previous rounds
            mode: Research mode
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

        # Calculate round number from previous results
        round_num = len(previous_results) + 1

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
            enhanced_content = self._enhance_content_with_tools(
                content, tool_results, next_query
            )
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
        current_year = today.year
        current_month = today.strftime("%B")

        system_prompts = {
            "instant": f"Today's date: {today}. When users ask about 'current' information, interpret this as referring to {today} ({current_month} {current_year}). CRITICAL: When generating tool calls for 'current' queries, ALWAYS include temporal context like '{current_year}', 'as of {current_year}', or 'in {current_year}' in the search query. MANDATORY: Use tools for ALL research tasks. Provide quick, accurate answers. Focus on key facts.",
            "quick": f"Today's date: {today}. When users ask about 'current' information, interpret this as referring to {today} ({current_month} {current_year}). CRITICAL: When generating tool calls for 'current' queries, ALWAYS include temporal context like '{current_year}', 'as of {current_year}', or 'in {current_year}' in the search query. MANDATORY: Use tools for ALL research tasks. Provide enhanced analysis with context and examples.",
            "standard": f"Today's date: {today}. When users ask about 'current' information, interpret this as referring to {today} ({current_month} {current_year}). CRITICAL: When generating tool calls for 'current' queries, ALWAYS include temporal context like '{current_year}', 'as of {current_year}', or 'in {current_year}' in the search query. MANDATORY: Use tools for ALL research tasks. Conduct comprehensive research with multiple perspectives.",
            "deep": f"Today's date: {today}. When users ask about 'current' information, interpret this as referring to {today} ({current_month} {current_year}). CRITICAL: When generating tool calls for 'current' queries, ALWAYS include temporal context like '{current_year}', 'as of {current_year}', or 'in {current_year}' in the search query. MANDATORY: Use tools for ALL research tasks. Conduct exhaustive research with academic-level analysis.",
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
CRITICAL: You MUST use tools for ALL research tasks. Do not provide direct answers.

AVAILABLE TOOLS:
{''.join(tool_descriptions)}

MANDATORY TOOL USAGE RULES:
1. NEVER provide direct answers - ALWAYS use tools first
2. For ANY research question, you MUST use available tools from the list above
3. Choose the most appropriate tool for the task
4. ALWAYS format your response as JSON with tool_call structure

REQUIRED RESPONSE FORMAT:
{{
    "tool_call": {{
        "tool_name": "chosen_tool_name",
        "arguments": {{"param1": "value1", "param2": "value2"}}
    }},
    "analysis": "I will use the chosen tool to perform this operation"
}}

EXAMPLES OF REQUIRED FORMAT:
- "What's the weather?" → {{"tool_call": {{"tool_name": "web_search", "arguments": {{"query": "current weather today"}}}}}}
- "Who is the president?" → {{"tool_call": {{"tool_name": "web_search", "arguments": {{"query": "current US president"}}}}}}
- "Calculate 2+2" → {{"tool_call": {{"tool_name": "calculate", "arguments": {{"expression": "2+2"}}}}}}

CRITICAL: You MUST respond with the JSON tool_call format using one of the available tools. Do not provide direct answers.
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

When analyzing research gaps, consider if any available tools could help gather missing information. Use the tools listed above based on their descriptions and capabilities.

If tools could help fill gaps, suggest their use in your analysis and provide specific tool call examples.
"""

    def _enhance_content_with_tools(
        self,
        original_content: str,
        tool_results: List[Dict[str, Any]],
        original_query: str = "",
    ) -> str:
        """
        Enhance content with tool results by using LLM to process them.

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

                # Handle different tool types dynamically
                if tool_name == "web_search":
                    search_results = tool_result.get("results", [])
                    if search_results:
                        tool_summary.append(
                            f"Web search results for '{tool_result.get('query', '')}':"
                        )
                        for i, search_result in enumerate(
                            search_results[:10], 1
                        ):  # Limit to 10 results to capture more relevant information
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
                else:
                    # Generic handling for any other tool types
                    tool_summary.append(f"{tool_name} result: {str(tool_result)}")

        # If we have tool results, use LLM to process them and generate a proper answer
        if tool_summary:
            tool_results_text = "\n".join(tool_summary)

            # Use the provided original query or extract from tool call
            if not original_query:
                original_query = "the research question"
                if tool_results and tool_results[0].get("tool_name") == "web_search":
                    original_query = (
                        tool_results[0]
                        .get("result", {})
                        .get("query", "the research question")
                    )
        else:
            # No tool results available, return a message indicating this
            return f"The tool search was attempted but no results were returned. Original query: {original_query}"

        # Use LLM to process tool results and generate final answer
        from datetime import date

        today = date.today()
        current_year = today.year
        current_month = today.strftime("%B")

        system_prompt = f"""You are a research assistant. You have been provided with tool results that contain information relevant to a research question.

CRITICAL: Today's date is {today} ({current_month} {current_year}). You MUST use the information from the tool results below to answer the research question.

MANDATORY INSTRUCTIONS:
1. **Use the information from the tool results provided below to answer the research question**
2. **Always cite specific sources from the tool results**
3. **Pay special attention to dates and temporal context - prioritize information that reflects the current status as of {today} ({current_month} {current_year})**
4. **If the tool results contain relevant information, use it to provide a comprehensive answer**
5. **If the tool results don't contain enough information, say so but still use what information is available**

Tool Results:
{tool_results_text}

Research Question: {original_query}

CRITICAL: Answer the research question using the information from the tool results above. Always cite the specific sources you're using from the tool results. If the tool results contain conflicting information, mention the conflict and explain which source you're prioritizing and why."""

        # Generate final answer using LLM
        final_answer = self.llm_service.generate(
            input_data=f"Research question: {original_query}\n\nTool results:\n{tool_results_text}",
            system_prompt=system_prompt,
            temperature=0.0,
        )

        return final_answer

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
