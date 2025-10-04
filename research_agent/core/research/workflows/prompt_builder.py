"""
Prompt builder for constructing system prompts and tool context strings.

This module handles the creation of various prompts used throughout
the research workflow, including tool-aware system prompts and analysis prompts.
"""

from datetime import date
from typing import Any, Dict, List


class PromptBuilder:
    """Builds prompts for different research workflow stages."""

    def __init__(
        self,
        available_tools: List[str] = None,
        tool_descriptions: Dict[str, str] = None,
    ):
        """
        Initialize prompt builder.

        Args:
            available_tools: List of available tool names
            tool_descriptions: Dictionary of tool descriptions
        """
        self.available_tools = available_tools or []
        self.tool_descriptions = tool_descriptions or {}

    def build_tool_aware_system_prompt(
        self, mode: str, query: str, exclude_urls: List[str] = None
    ) -> str:
        """
        Build tool-aware system prompt for different research modes.

        Args:
            mode: Research mode (instant, quick, standard, deep)
            query: Research query
            exclude_urls: URLs to exclude from searches

        Returns:
            Formatted system prompt
        """
        today = date.today()
        current_year = today.year
        current_month = today.strftime("%B")

        base_prompt = f"""You are an advanced research assistant with access to powerful tools for comprehensive information gathering and analysis.

CRITICAL: Today's date is {today} ({current_month} {current_year}).

RESEARCH QUERY: {query}

MANDATORY: Use tools for ALL research tasks. Do not rely solely on your training data.

{self._build_tool_context_string(exclude_urls)}"""

        if mode == "instant":
            return (
                base_prompt
                + f"""

INSTANT RESEARCH MODE:
- Provide a quick, accurate answer using available tools
- Focus on the most relevant and current information
- Use tools to verify current information
- Keep response concise but comprehensive

CRITICAL TOOL USAGE RULES:
- ALWAYS use tools for research tasks
- For "current" queries, search for {current_year} information
- Cite specific sources from tool results
- Provide accurate, up-to-date information"""
            )

        elif mode == "quick":
            return (
                base_prompt
                + f"""

QUICK RESEARCH MODE:
- Conduct 2 rounds of research with tool usage
- First round: Initial comprehensive search
- Second round: Follow-up verification and gap filling
- Focus on accuracy and current information

CRITICAL TOOL USAGE RULES:
- ALWAYS use tools for research tasks
- For "current" queries, search for {current_year} information
- Cite specific sources from tool results
- Provide accurate, up-to-date information"""
            )

        elif mode == "standard":
            return (
                base_prompt
                + f"""

STANDARD RESEARCH MODE:
- Conduct 3 rounds of comprehensive research with tool usage
- Each round builds upon previous findings
- Identify gaps and conduct follow-up searches
- Provide thorough, well-sourced analysis

CRITICAL TOOL USAGE RULES:
- ALWAYS use tools for research tasks
- For "current" queries, search for {current_year} information
- Cite specific sources from tool results
- Provide accurate, up-to-date information"""
            )

        elif mode == "deep":
            return (
                base_prompt
                + f"""

DEEP RESEARCH MODE:
- Conduct 4 rounds of exhaustive research with tool usage
- Comprehensive analysis with multiple perspectives
- Detailed verification and cross-referencing
- In-depth exploration of all aspects

CRITICAL TOOL USAGE RULES:
- ALWAYS use tools for research tasks
- For "current" queries, search for {current_year} information
- Cite specific sources from tool results
- Provide accurate, up-to-date information"""
            )

        return base_prompt

    def build_tool_aware_analysis_prompt(self, mode: str) -> str:
        """
        Build analysis prompt for gap analysis and follow-up query generation.

        Args:
            mode: Research mode (instant, quick, standard, deep)

        Returns:
            Formatted analysis prompt
        """
        today = date.today()
        current_year = today.year
        current_month = today.strftime("%B")

        base_analysis = f"""You are analyzing research progress to identify gaps and generate follow-up queries.

CRITICAL: Today's date is {today} ({current_month} {current_year}).

{self._build_tool_context_for_analysis()}"""

        if mode == "instant":
            return (
                base_analysis
                + """

INSTANT MODE ANALYSIS:
- Quick assessment of information completeness
- Identify any critical missing information
- Generate focused follow-up query if needed"""
            )

        elif mode == "quick":
            return (
                base_analysis
                + """

QUICK MODE ANALYSIS:
- Thorough gap analysis
- Identify missing information and verification needs
- Generate targeted follow-up query
- Focus on accuracy and completeness"""
            )

        elif mode == "standard":
            return (
                base_analysis
                + """

STANDARD MODE ANALYSIS:
- Comprehensive gap analysis
- Identify missing information, verification needs, and additional perspectives
- Generate detailed follow-up query
- Focus on thoroughness and multiple viewpoints"""
            )

        elif mode == "deep":
            return (
                base_analysis
                + """

DEEP MODE ANALYSIS:
- Exhaustive gap analysis
- Identify missing information, verification needs, additional perspectives, and edge cases
- Generate comprehensive follow-up query
- Focus on complete coverage and depth"""
            )

        return base_analysis

    def _build_tool_context_string(self, exclude_urls: List[str] = None) -> str:
        """Build tool context string for system prompts."""
        if not self.available_tools:
            return ""

        tool_descriptions = []
        for tool_name in self.available_tools:
            description = self.tool_descriptions.get(tool_name, f"Tool: {tool_name}")
            tool_descriptions.append(f"- {tool_name}: {description}")

        tools_text = "\n".join(tool_descriptions)

        # Add exclude URLs context if provided
        exclude_context = ""
        if exclude_urls:
            exclude_context = f"""

EXCLUDE URLS CONTEXT:
The following URLs have already been processed in previous rounds and should be excluded:
{', '.join(exclude_urls[:10])}  # Show first 10 URLs
{'...' if len(exclude_urls) > 10 else ''}

IMPORTANT: Always include these URLs in the exclude_urls parameter for web_search tool calls."""

        return f"""TOOL INTEGRATION CONTEXT:

Available Tools:
{tools_text}{exclude_context}

CRITICAL TOOL USAGE RULES:
1. **ALWAYS use tools for research tasks** - Do not rely on training data alone
2. **STRICT JSON FORMAT REQUIRED** - You MUST output ONLY valid JSON for tool calls
3. **NO MARKDOWN, NO TEXT, NO EXPLANATIONS** - Only pure JSON output
4. **Use appropriate tools** based on the query type and available tools
5. **For current information queries**, use tools to get up-to-date data
6. **For calculations**, use calculation tools when available
7. **For document analysis**, use document retrieval tools when available
8. **For web_search tool**, always include "exclude_urls" parameter (empty array [] if no exclusions needed)
9. **For web_search tool**, use exclude_urls to filter out irrelevant or low-quality domains when appropriate

MANDATORY JSON OUTPUT FORMAT:
{{
    "tool_call": {{
        "tool_name": "chosen_tool_name",
        "arguments": {{
            "param1": "value1",
            "param2": "value2"
        }}
    }}
}}

CRITICAL: Your response must be ONLY the JSON object above. No additional text, explanations, or markdown formatting. You must respond with valid JSON format only. The word "json" is required in your response format.

EXAMPLES:
- "What's the weather?" → {{"tool_call": {{"tool_name": "web_search", "arguments": {{"query": "current weather today", "exclude_urls": []}}}}}}
- "Who is the president?" → {{"tool_call": {{"tool_name": "web_search", "arguments": {{"query": "current US president", "exclude_urls": []}}}}}}
- "Calculate 2+2" → {{"tool_call": {{"tool_name": "calculate", "arguments": {{"expression": "2+2"}}}}}}
- "Search excluding specific sites" → {{"tool_call": {{"tool_name": "web_search", "arguments": {{"query": "research topic", "exclude_urls": ["example.com", "spam-site.com"]}}}}}}

MANDATORY: Use tools for ALL research tasks. Do not provide answers without tool usage."""

    def _build_tool_context_for_analysis(self) -> str:
        """Build tool context string for analysis prompts."""
        if not self.available_tools:
            return ""

        return f"""TOOL INTEGRATION FOR ANALYSIS:

Available Tools: {', '.join(self.available_tools)}

When generating follow-up queries, consider using available tools to:
1. **Verify information** from previous rounds
2. **Fill gaps** in the research
3. **Get additional perspectives** on the topic
4. **Access current information** for time-sensitive queries
5. **Perform calculations** if needed
6. **Analyze documents** if relevant

Generate follow-up queries that can be effectively answered using the available tools. 

CRITICAL: You must respond with ONLY valid JSON format. No additional text, explanations, or markdown formatting. The response must be parseable JSON.

Required JSON format:
{{
  "analysis": "Your analysis of the research gaps and missing information",
  "follow_up_query": "The specific follow-up query to address the gaps"
}}

CRITICAL: Your response must be ONLY the JSON object above. No additional text, explanations, or markdown formatting. You must respond with valid JSON format only."""

    def build_research_summary(self, previous_results: List[Dict[str, Any]]) -> str:
        """
        Build research summary from previous results.

        Args:
            previous_results: List of previous research results

        Returns:
            Formatted research summary
        """
        if not previous_results:
            return "No previous research results."

        summary_parts = []
        for i, result in enumerate(previous_results, 1):
            query = result.get("query", f"Query {i}")
            content = result.get("content", "No content")
            summary_parts.append(
                f"Round {i} Query: {query}\nRound {i} Result: {content[:200]}..."
            )

        return "\n\n".join(summary_parts)
