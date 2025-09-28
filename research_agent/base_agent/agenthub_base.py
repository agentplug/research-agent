#!/usr/bin/env python3
"""
AgentHub BaseAgent for Research Agent

Provides tool integration capabilities following AgentHub standards.
"""

import json
from typing import Any, Dict, List, Optional


class AgentHubBaseAgent:
    """Base class for AgentHub agents with tool integration."""

    def __init__(self, tool_context: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.

        Args:
            tool_context: Dictionary containing tool metadata and context information
        """
        self.tool_context = tool_context or {}
        self.available_tools = self.tool_context.get("available_tools", [])
        self.tool_descriptions = self.tool_context.get("tool_descriptions", {})
        self.tool_usage_examples = self.tool_context.get("tool_usage_examples", {})
        self.tool_parameters = self.tool_context.get("tool_parameters", {})
        self.tool_return_types = self.tool_context.get("tool_return_types", {})

    def validate_tool_context(self) -> bool:
        """
        Validate tool context structure.

        Returns:
            True if tool context is valid, False otherwise
        """
        if not isinstance(self.tool_context, dict):
            return False

        # Check required fields
        required_fields = ["available_tools", "tool_descriptions"]
        for field in required_fields:
            if field not in self.tool_context:
                return False

        # Check if available_tools is a list
        if not isinstance(self.tool_context["available_tools"], list):
            return False

        # Check if tool_descriptions is a dict
        if not isinstance(self.tool_context["tool_descriptions"], dict):
            return False

        return True

    def build_tool_context_string(self) -> str:
        """
        Build tool context string for AI system prompt.

        Returns:
            Formatted tool context string
        """
        if not self.available_tools:
            return ""

        tool_descriptions = []
        for tool_name in self.available_tools:
            description = self.tool_descriptions.get(tool_name, f"Tool: {tool_name}")
            examples = self.tool_usage_examples.get(tool_name, [])
            parameters = self.tool_parameters.get(tool_name, {})
            return_type = self.tool_return_types.get(tool_name, "unknown")

            tool_descriptions.append(
                f"""
Tool: {tool_name}
Description: {description}
Parameters: {json.dumps(parameters) if parameters else "None"}
Return Type: {return_type}
Examples: {', '.join(examples) if examples else "None"}
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

    def get_tool_info(self) -> Dict[str, Any]:
        """
        Get information about available tools.

        Returns:
            Dictionary with tool information
        """
        return {
            "available_tools": self.available_tools,
            "tool_descriptions": self.tool_descriptions,
            "tool_usage_examples": self.tool_usage_examples,
            "tool_parameters": self.tool_parameters,
            "tool_return_types": self.tool_return_types,
            "tool_count": len(self.available_tools),
            "has_tools": len(self.available_tools) > 0,
        }

    def has_tool(self, tool_name: str) -> bool:
        """
        Check if a specific tool is available.

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if tool is available, False otherwise
        """
        return tool_name in self.available_tools

    def get_tool_description(self, tool_name: str) -> str:
        """
        Get description for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool description or empty string if not found
        """
        return self.tool_descriptions.get(tool_name, "")

    def log_execution_step(self, step: str, details: str = "") -> None:
        """
        Log execution step for debugging and transparency.

        Args:
            step: Step description
            details: Additional details
        """
        print(f"🔍 AGENT STEP: {step}")
        if details:
            print(f"   📝 Details: {details}")
