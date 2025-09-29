#!/usr/bin/env python3
"""
Tool Execution Framework for Research Agent

Handles tool calls, execution, and result processing.
Supports both MCP (real) and simulation modes.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# Import MCP executor for real tool calls
try:
    from .agenthub_mcp_client import AgentHubMCPClient

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


class ToolExecutor:
    """Handles tool execution and result processing."""

    def __init__(
        self,
        available_tools: List[str],
        tool_descriptions: Dict[str, str] = None,
        mcp_server_url: str = "http://127.0.0.1:8000",
        use_mcp: bool = True,
    ):
        """
        Initialize tool executor.

        Args:
            available_tools: List of available tool names
            tool_descriptions: Dictionary of tool descriptions
            mcp_server_url: URL of MCP tool server
            use_mcp: Whether to use MCP for real tool execution
        """
        self.available_tools = available_tools or []
        self.tool_descriptions = tool_descriptions or {}
        self.logger = logging.getLogger(__name__)

        # Tool execution results cache
        self.execution_history: List[Dict[str, Any]] = []

        # MCP integration
        self.use_mcp = use_mcp and MCP_AVAILABLE
        self.mcp_executor = None

        if self.use_mcp:
            try:
                self.mcp_executor = AgentHubMCPClient(mcp_server_url)
                # Test MCP connection
                connection_test = self.mcp_executor.test_connection()
                if connection_test["success"]:
                    self.logger.info(
                        "✅ AgentHub MCP tool server connected successfully"
                    )
                else:
                    self.logger.warning(
                        f"⚠️ MCP connection failed: {connection_test.get('error')}"
                    )
                    self.logger.info("🔄 Falling back to simulation mode")
                    self.use_mcp = False
            except Exception as e:
                self.logger.warning(f"⚠️ MCP initialization failed: {str(e)}")
                self.logger.info("🔄 Falling back to simulation mode")
                self.use_mcp = False

        if not self.use_mcp:
            self.logger.info("🔄 Using simulation mode for tool execution")

    def extract_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract tool calls from LLM response content.

        Args:
            content: LLM response content

        Returns:
            List of tool call dictionaries
        """
        tool_calls = []

        try:
            # Try to parse as JSON first
            if content.strip().startswith("{") and content.strip().endswith("}"):
                parsed_content = json.loads(content)
                if "tool_call" in parsed_content:
                    tool_calls.append(parsed_content["tool_call"])
                elif isinstance(parsed_content, list):
                    tool_calls.extend(parsed_content)

            # Look for tool_call patterns in text
            elif "tool_call" in content:
                # Extract JSON objects containing tool_call
                import re

                json_pattern = r'\{[^{}]*"tool_call"[^{}]*\}'
                matches = re.findall(json_pattern, content)

                for match in matches:
                    try:
                        tool_call = json.loads(match)
                        if "tool_call" in tool_call:
                            tool_calls.append(tool_call["tool_call"])
                    except json.JSONDecodeError:
                        continue

        except json.JSONDecodeError:
            self.logger.warning(
                f"Failed to parse tool calls from content: {content[:100]}..."
            )

        return tool_calls

    def validate_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a tool call.

        Args:
            tool_call: Tool call dictionary

        Returns:
            Validation result with success status and details
        """
        if not isinstance(tool_call, dict):
            return {
                "valid": False,
                "error": "Tool call must be a dictionary",
                "tool_call": tool_call,
            }

        tool_name = tool_call.get("tool_name")
        if not tool_name:
            return {
                "valid": False,
                "error": "Missing tool_name in tool call",
                "tool_call": tool_call,
            }

        if tool_name not in self.available_tools:
            return {
                "valid": False,
                "error": f"Tool '{tool_name}' not available. Available tools: {self.available_tools}",
                "tool_call": tool_call,
            }

        arguments = tool_call.get("arguments", {})
        if not isinstance(arguments, dict):
            return {
                "valid": False,
                "error": "Tool arguments must be a dictionary",
                "tool_call": tool_call,
            }

        return {
            "valid": True,
            "tool_name": tool_name,
            "arguments": arguments,
            "tool_call": tool_call,
        }

    def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single tool call.

        Args:
            tool_call: Tool call dictionary

        Returns:
            Tool execution result
        """
        validation = self.validate_tool_call(tool_call)

        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"],
                "tool_call": tool_call,
                "timestamp": datetime.now().isoformat(),
            }

        tool_name = validation["tool_name"]
        arguments = validation["arguments"]

        try:
            # Use MCP for real tool execution if available
            if self.use_mcp and self.mcp_executor:
                result = self.mcp_executor.execute_tool(tool_call)
                self.execution_history.append(result)
                return result
            else:
                # Fallback to simulation
                result = self._simulate_tool_execution(tool_name, arguments)

                # Log execution
                execution_record = {
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "mode": "simulation",
                }
                self.execution_history.append(execution_record)

                return {
                    "success": True,
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                    "mode": "simulation",
                }

        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {str(e)}")

            execution_record = {
                "tool_name": tool_name,
                "arguments": arguments,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "success": False,
            }
            self.execution_history.append(execution_record)

            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name,
                "arguments": arguments,
                "timestamp": datetime.now().isoformat(),
            }

    def execute_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls.

        Args:
            tool_calls: List of tool call dictionaries

        Returns:
            List of tool execution results
        """
        results = []

        for tool_call in tool_calls:
            result = self.execute_tool(tool_call)
            results.append(result)

        return results

    def _simulate_tool_execution(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Any:
        """
        Simulate tool execution for testing purposes.

        Args:
            tool_name: Name of the tool
            arguments: Tool arguments

        Returns:
            Simulated tool result
        """
        # This is a simulation - in real implementation, tools would be called via APIs

        if tool_name == "web_search":
            query = arguments.get("query", "")
            return {
                "type": "web_search_result",
                "query": query,
                "results": [
                    {
                        "title": f"Search result for: {query}",
                        "url": f"https://example.com/search?q={query}",
                        "snippet": f"This is a simulated search result for '{query}'. In a real implementation, this would contain actual web search results.",
                    }
                ],
                "total_results": 1,
            }

        elif tool_name == "calculate":
            expression = arguments.get("expression", "")
            try:
                # Safe evaluation for simple math expressions
                result = eval(expression)
                return {
                    "type": "calculation_result",
                    "expression": expression,
                    "result": result,
                }
            except Exception as e:
                return {
                    "type": "calculation_error",
                    "expression": expression,
                    "error": str(e),
                }

        elif tool_name == "document_retrieval":
            file_path = arguments.get("file_path", "")
            extract_type = arguments.get("extract_type", "full_text")
            return {
                "type": "document_result",
                "file_path": file_path,
                "extract_type": extract_type,
                "content": f"This is simulated content extracted from {file_path} using {extract_type} method.",
                "metadata": {
                    "file_size": "1.2MB",
                    "pages": 10,
                    "extraction_method": extract_type,
                },
            }

        else:
            return {
                "type": "unknown_tool",
                "tool_name": tool_name,
                "arguments": arguments,
                "message": f"Tool '{tool_name}' is not implemented in simulation mode",
            }

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        Get tool execution history.

        Returns:
            List of execution records
        """
        return self.execution_history.copy()

    def clear_execution_history(self) -> None:
        """Clear tool execution history."""
        self.execution_history.clear()

    def get_tool_usage_stats(self) -> Dict[str, Any]:
        """
        Get tool usage statistics.

        Returns:
            Dictionary with usage statistics
        """
        if not self.execution_history:
            return {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "tool_usage": {},
                "average_execution_time": 0,
            }

        total_executions = len(self.execution_history)
        successful_executions = sum(
            1 for record in self.execution_history if record.get("success", False)
        )
        failed_executions = total_executions - successful_executions

        tool_usage = {}
        for record in self.execution_history:
            tool_name = record.get("tool_name", "unknown")
            tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1

        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "tool_usage": tool_usage,
            "success_rate": successful_executions / total_executions
            if total_executions > 0
            else 0,
        }

    def get_mcp_status(self) -> Dict[str, Any]:
        """
        Get MCP server status and connection info.

        Returns:
            Dictionary with MCP status information
        """
        status = {
            "mcp_available": MCP_AVAILABLE,
            "mcp_enabled": self.use_mcp,
            "mcp_executor_initialized": self.mcp_executor is not None,
            "execution_mode": "mcp" if self.use_mcp else "simulation",
        }

        if self.mcp_executor:
            try:
                # Test connection
                connection_test = self.mcp_executor.test_connection()
                status["connection_status"] = (
                    "connected" if connection_test["success"] else "failed"
                )
                status["connection_error"] = connection_test.get("error")

                # Get available tools from MCP server
                available_tools = self.mcp_executor.get_available_tools()
                status["mcp_available_tools"] = available_tools

            except Exception as e:
                status["connection_status"] = "error"
                status["connection_error"] = str(e)

        return status
