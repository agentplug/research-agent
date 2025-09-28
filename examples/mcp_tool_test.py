#!/usr/bin/env python3
"""
MCP Tool Integration Test

Tests real tool execution via MCP server.
"""

import json
import subprocess
import sys
from typing import Any, Dict

# Define available tools and their descriptions for the test context
TEST_TOOL_CONTEXT = {
    "available_tools": ["web_search", "calculate"],
    "tool_descriptions": {
        "web_search": "Search the web for current information",
        "calculate": "Perform mathematical calculations",
    },
}


def execute_agent_call(
    method: str, parameters: Dict[str, Any], tool_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Executes an agent call via subprocess and returns the parsed JSON result."""
    input_data = {
        "method": method,
        "parameters": parameters,
        "tool_context": tool_context,
    }

    try:
        command = ["python", "agent.py", json.dumps(input_data)]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,  # Increased timeout for MCP calls
        )

        if result.returncode == 0:
            response = json.loads(result.stdout)
            return response.get("result", response)
        else:
            print(f"Agent stderr: {result.stderr}", file=sys.stderr)
            return {
                "success": False,
                "data": {"error": f"Agent execution failed: {result.stderr}"},
            }

    except subprocess.TimeoutExpired:
        return {"success": False, "data": {"error": "Agent execution timed out"}}
    except json.JSONDecodeError as e:
        print(f"Failed to parse agent response: {result.stdout}", file=sys.stderr)
        return {
            "success": False,
            "data": {"error": f"Failed to parse agent response: {str(e)}"},
        }
    except Exception as e:
        return {
            "success": False,
            "data": {"error": f"Unexpected error during agent call: {str(e)}"},
        }


def run_test(name: str, test_func) -> bool:
    """Runs a single test function and prints results."""
    print(f"🔍 Testing {name}...")
    success, message = test_func()
    if success:
        print(f"✅ {name} Test PASSED")
        if message:
            print(f"   {message}")
    else:
        print(f"❌ {name} Test FAILED")
        if message:
            print(f"   Error: {message}")
    return success


def test_mcp_web_search() -> (bool, str):
    """Tests if the web_search tool uses MCP for real search."""
    query = "What is the current weather in New York?"
    result = execute_agent_call("instant_research", {"query": query}, TEST_TOOL_CONTEXT)

    if result.get("success"):
        content = result["data"].get("content", "")

        # Check for MCP indicators (real results vs simulation)
        if "tool_call" in content and "web_search" in content:
            if "simulated" in content.lower() or "example.com" in content:
                return False, "Still using simulation instead of MCP"
            elif "--- TOOL RESULTS ---" in content:
                return True, "MCP web search executed successfully"
            else:
                return False, f"Tool used but unclear if MCP: {content[:200]}..."
        else:
            return False, f"No tool call detected: {content[:200]}..."
    return False, result.get("data", {}).get("error", "Unknown error")


def test_mcp_calculation() -> (bool, str):
    """Tests if the calculate tool works with MCP."""
    query = "Calculate 25% of 480"
    result = execute_agent_call("instant_research", {"query": query}, TEST_TOOL_CONTEXT)

    if result.get("success"):
        content = result["data"].get("content", "")
        if "tool_call" in content and "calculate" in content and "120" in content:
            return True, "MCP calculation executed successfully"
        else:
            return False, f"Tool not used or incorrect result: {content[:200]}..."
    return False, result.get("data", {}).get("error", "Unknown error")


def test_mcp_status() -> (bool, str):
    """Tests if agent status shows MCP integration."""
    result = execute_agent_call("get_agent_status", {}, TEST_TOOL_CONTEXT)

    if result.get("success"):
        tool_integration = result["data"].get("tool_integration", {})
        if tool_integration.get("has_tools"):
            return (
                True,
                f"MCP tools detected: {tool_integration.get('available_tools')}",
            )
        else:
            return False, f"No tools detected: {tool_integration}"
    return False, result.get("data", {}).get("error", "Unknown error")


def test_mcp_tool_stats() -> (bool, str):
    """Tests if tool usage stats show MCP execution."""
    result = execute_agent_call("get_tool_usage_stats", {}, TEST_TOOL_CONTEXT)

    if result.get("success"):
        stats = result["data"]
        if stats.get("has_tools") and stats.get("total_executions", 0) > 0:
            return (
                True,
                f"MCP tool stats available: {stats.get('total_executions')} executions",
            )
        else:
            return False, f"No tool execution stats: {stats}"
    return False, result.get("data", {}).get("error", "Unknown error")


def test_mcp_integration_suite():
    """Runs all MCP integration tests."""
    print("🧪 MCP TOOL INTEGRATION TEST SUITE")
    print("=" * 50)
    print("🔗 Testing real tool execution via MCP server...")
    print()

    all_tests_passed = True

    if not run_test("MCP Web Search", test_mcp_web_search):
        all_tests_passed = False

    if not run_test("MCP Calculation", test_mcp_calculation):
        all_tests_passed = False

    if not run_test("MCP Status Detection", test_mcp_status):
        all_tests_passed = False

    if not run_test("MCP Tool Stats", test_mcp_tool_stats):
        all_tests_passed = False

    print("\n📋 MCP TEST SUMMARY")
    print("=" * 50)
    if all_tests_passed:
        print("🎉 ALL MCP TESTS PASSED! Real tool integration is working.")
        print("✅ Research Agent is now using MCP for real tool execution!")
    else:
        print("❌ SOME MCP TESTS FAILED. Check the output above for details.")
        print("⚠️  Make sure MCP server is running on http://127.0.0.1:8000")


if __name__ == "__main__":
    test_mcp_integration_suite()
