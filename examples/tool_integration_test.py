#!/usr/bin/env python3
"""
Comprehensive Tool Integration Test

Demonstrates all tool integration features of the Research Agent.
"""

import json
import subprocess
import sys
from typing import Any, Dict


def test_tool_integration():
    """Test comprehensive tool integration features."""

    print("🧪 COMPREHENSIVE TOOL INTEGRATION TEST")
    print("=" * 60)

    # Tool context for testing
    tool_context = {
        "available_tools": ["web_search", "calculate", "document_retrieval"],
        "tool_descriptions": {
            "web_search": "Search the web for current information",
            "calculate": "Perform mathematical calculations",
            "document_retrieval": "Extract and analyze documents",
        },
        "tool_usage_examples": {
            "web_search": ["Search for latest AI news", "Find current market trends"],
            "calculate": ["Calculate percentages", "Compute statistics"],
            "document_retrieval": [
                "Extract key points from PDF",
                "Summarize research paper",
            ],
        },
    }

    # Test cases
    test_cases = [
        {
            "name": "Web Search Tool",
            "method": "instant_research",
            "parameters": {
                "query": "What is the latest news about AI developments in 2024?"
            },
            "expected_tool": "web_search",
        },
        {
            "name": "Calculation Tool",
            "method": "instant_research",
            "parameters": {"query": "Calculate 25% of 480 and add 15% tax"},
            "expected_tool": "calculate",
        },
        {
            "name": "Multi-Tool Research",
            "method": "quick_research",
            "parameters": {
                "query": "What are the latest AI developments and calculate the market growth rate?"
            },
            "expected_tools": ["web_search", "calculate"],
        },
        {
            "name": "Deep Research with Tools",
            "method": "deep_research",
            "parameters": {
                "query": "Analyze AI market trends",
                "user_clarification": "Focus on 2024 data, include calculations",
            },
            "expected_tools": ["web_search", "calculate"],
        },
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print(f"Query: {test_case['parameters']['query']}")

        try:
            # Execute test
            result = execute_agent_call(
                test_case["method"], test_case["parameters"], tool_context
            )

            if result.get("success", False):
                print("✅ Test PASSED")

                # Check tool usage
                content = result.get("data", {}).get("content", "")
                tools_used = []

                if "web_search" in content:
                    tools_used.append("web_search")
                if "calculate" in content:
                    tools_used.append("calculate")
                if "document_retrieval" in content:
                    tools_used.append("document_retrieval")

                print(f"Tools used: {tools_used}")

                # Verify expected tools were used
                expected_tools = test_case.get(
                    "expected_tools", [test_case.get("expected_tool")]
                )
                if isinstance(expected_tools, str):
                    expected_tools = [expected_tools]

                tool_match = any(tool in tools_used for tool in expected_tools)
                if tool_match:
                    print("✅ Expected tools were used")
                else:
                    print(
                        f"⚠️ Expected tools {expected_tools} not found in {tools_used}"
                    )

                results.append(
                    {
                        "test": test_case["name"],
                        "status": "PASSED",
                        "tools_used": tools_used,
                        "expected_tools": expected_tools,
                        "tool_match": tool_match,
                    }
                )

            else:
                print("❌ Test FAILED")
                print(f"Error: {result.get('data', {}).get('error', 'Unknown error')}")
                results.append(
                    {
                        "test": test_case["name"],
                        "status": "FAILED",
                        "error": result.get("data", {}).get("error", "Unknown error"),
                    }
                )

        except Exception as e:
            print(f"❌ Test FAILED with exception: {str(e)}")
            results.append(
                {"test": test_case["name"], "status": "FAILED", "error": str(e)}
            )

    # Test agent status
    print(f"\n📊 Testing Agent Status...")
    try:
        status_result = execute_agent_call("get_agent_status", {}, tool_context)
        if status_result.get("success", False):
            tool_info = status_result.get("data", {}).get("tool_integration", {})
            print(f"✅ Agent Status: {tool_info.get('tool_count', 0)} tools available")
            print(f"Tools: {tool_info.get('available_tools', [])}")
        else:
            print("❌ Agent Status Test FAILED")
    except Exception as e:
        print(f"❌ Agent Status Test FAILED: {str(e)}")

    # Test tool usage stats
    print(f"\n📈 Testing Tool Usage Stats...")
    try:
        stats_result = execute_agent_call("get_tool_usage_stats", {}, tool_context)
        if stats_result.get("success", False):
            stats = stats_result.get("data", {})
            print(f"✅ Tool Stats: {stats.get('total_executions', 0)} total executions")
            print(f"Success Rate: {stats.get('success_rate', 0):.2%}")
        else:
            print("❌ Tool Stats Test FAILED")
    except Exception as e:
        print(f"❌ Tool Stats Test FAILED: {str(e)}")

    # Summary
    print(f"\n📋 TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for r in results if r["status"] == "PASSED")
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")

    for result in results:
        status_icon = "✅" if result["status"] == "PASSED" else "❌"
        print(f"{status_icon} {result['test']}: {result['status']}")
        if result["status"] == "PASSED" and "tools_used" in result:
            print(f"   Tools used: {result['tools_used']}")
        elif result["status"] == "FAILED":
            print(f"   Error: {result.get('error', 'Unknown')}")

    return results


def execute_agent_call(
    method: str, parameters: Dict[str, Any], tool_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute an agent call and return the result."""

    input_data = {
        "method": method,
        "parameters": parameters,
        "tool_context": tool_context,
    }

    try:
        result = subprocess.run(
            ["python", "agent.py", json.dumps(input_data)],
            capture_output=True,
            text=True,
            timeout=60,  # Increased timeout
        )

        if result.returncode == 0:
            response = json.loads(result.stdout)
            return response.get("result", response)  # Handle both formats
        else:
            return {
                "success": False,
                "data": {"error": f"Agent execution failed: {result.stderr}"},
            }

    except subprocess.TimeoutExpired:
        return {"success": False, "data": {"error": "Agent execution timed out"}}
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "data": {"error": f"Failed to parse agent response: {str(e)}"},
        }
    except Exception as e:
        return {"success": False, "data": {"error": f"Unexpected error: {str(e)}"}}


if __name__ == "__main__":
    test_tool_integration()
