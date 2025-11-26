#!/usr/bin/env python3
"""
MCP Tool Executor for Research Agent

Connects to MCP tool servers for real tool execution.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests


class MCPToolExecutor:
    """Handles real tool execution via MCP servers."""

    def __init__(self, mcp_server_url: str = None):
        """
        Initialize MCP tool executor.

        Args:
            mcp_server_url: URL of the MCP tool server. If not provided, will be constructed
                          from environment variables AGENTHUB_MCP_HOST and AGENTHUB_MCP_PORT.
        """
        if mcp_server_url is None:
            mcp_server_url = self._construct_server_url()
        
        self.mcp_server_url = mcp_server_url.rstrip("/")
        self.logger = logging.getLogger(__name__)

        # Tool execution results cache
        self.execution_history: List[Dict[str, Any]] = []

    def _construct_server_url(self) -> str:
        """
        Construct MCP server URL from environment variables.

        Returns:
            MCP server URL based on environment configuration
        """
        mcp_host = os.getenv("AGENTHUB_MCP_HOST", "localhost")
        
        if mcp_host == "localhost":
            # Use default localhost configuration
            return "http://127.0.0.1:8000"
        else:
            # Check if host already includes protocol
            if mcp_host.startswith("http://") or mcp_host.startswith("https://"):
                # Host already has protocol, use as-is (strip trailing slashes)
                return mcp_host.rstrip("/")
            else:
                # No protocol specified, construct URL
                # Check if port is specified in the host (e.g., "example.com:8080")
                if ":" in mcp_host:
                    # Port already in host, determine protocol from env or default to https
                    protocol = os.getenv("AGENTHUB_MCP_PROTOCOL", "https")
                    return f"{protocol}://{mcp_host}"
                else:
                    # No port in host, get from env or default
                    mcp_port = os.getenv("AGENTHUB_MCP_PORT")
                    protocol = os.getenv("AGENTHUB_MCP_PROTOCOL", "https")
                    
                    if mcp_port:
                        return f"{protocol}://{mcp_host}:{mcp_port}"
                    else:
                        # No port specified, use protocol default (443 for https, 80 for http)
                        return f"{protocol}://{mcp_host}"

    def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call via MCP server.

        Args:
            tool_call: Tool call dictionary

        Returns:
            Tool execution result
        """
        tool_name = tool_call.get("tool_name")
        arguments = tool_call.get("arguments", {})

        if not tool_name:
            return {
                "success": False,
                "error": "Missing tool_name in tool call",
                "tool_call": tool_call,
                "timestamp": datetime.now().isoformat(),
            }

        try:
            # Execute tool via MCP server
            result = self._call_mcp_tool(tool_name, arguments)

            # Log execution
            execution_record = {
                "tool_name": tool_name,
                "arguments": arguments,
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "success": True,
            }
            self.execution_history.append(execution_record)

            return {
                "success": True,
                "tool_name": tool_name,
                "arguments": arguments,
                "result": result,
                "timestamp": datetime.now().isoformat(),
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

    def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call MCP tool server for tool execution.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        # Try different endpoint patterns for MCP server
        endpoints_to_try = [
            f"{self.mcp_server_url}/tools/{tool_name}",
            f"{self.mcp_server_url}/{tool_name}",
            f"{self.mcp_server_url}/call",
            f"{self.mcp_server_url}/execute",
        ]

        # Prepare request payload
        payload = {"tool_name": tool_name, "arguments": arguments}

        last_error = None

        for endpoint in endpoints_to_try:
            try:
                # Make HTTP request to MCP server
                response = requests.post(
                    endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30,
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    # Try next endpoint
                    continue
                else:
                    last_error = f"HTTP {response.status_code}: {response.text}"

            except requests.exceptions.RequestException as e:
                last_error = f"Request error: {str(e)}"
                continue

        # If all endpoints failed, raise the last error
        raise Exception(f"MCP server error: {last_error}")

    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to MCP server.

        Returns:
            Connection test result
        """
        try:
            # Test with a simple web search
            test_result = self.execute_tool(
                {"tool_name": "web_search", "arguments": {"query": "test connection"}}
            )

            return {
                "success": True,
                "message": "MCP server connection successful",
                "test_result": test_result,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"MCP server connection failed: {str(e)}",
            }

    def get_available_tools(self) -> List[str]:
        """
        Get list of available tools from MCP server.

        Returns:
            List of available tool names
        """
        try:
            response = requests.get(f"{self.mcp_server_url}/tools", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("tools", [])
            else:
                return []
        except Exception:
            return []

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
                "success_rate": 0,
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
