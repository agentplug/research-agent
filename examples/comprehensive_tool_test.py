#!/usr/bin/env python3
"""
Comprehensive Tool Integration Testing Suite

This script provides various ways to test the tool integration functionality.
"""

import json
import logging
import subprocess
import sys
from typing import Any, Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_web_search_tool():
    """Test web search tool integration."""
    logger.info("🔍 Testing Web Search Tool...")

    input_data = {
        "method": "instant_research",
        "parameters": {
            "query": "What is the latest news about AI developments in 2024?"
        },
        "tool_context": {
            "available_tools": ["web_search"],
            "tool_descriptions": {
                "web_search": "Search the web for current information"
            },
            "tool_usage_examples": {"web_search": ["Search for latest AI news"]},
        },
    }

    result = execute_agent_call(input_data)

    if result.get("success", False):
        content = result.get("data", {}).get("content", "")
        if "web_search" in content and "TOOL RESULTS" in content:
            logger.info("✅ Web Search Tool Test PASSED")
            logger.info(f"   Tool was used and results integrated")
            return True
        else:
            logger.info("❌ Web Search Tool Test FAILED - Tool not used")
            return False
    else:
        logger.info(
            f"❌ Web Search Tool Test FAILED - {result.get('data', {}).get('error', 'Unknown error')}"
        )
        return False


def test_calculation_tool():
    """Test calculation tool integration."""
    logger.info("\n🧮 Testing Calculation Tool...")

    input_data = {
        "method": "instant_research",
        "parameters": {"query": "Calculate 25% of 480 and add 15% tax"},
        "tool_context": {
            "available_tools": ["calculate"],
            "tool_descriptions": {"calculate": "Perform mathematical calculations"},
            "tool_usage_examples": {"calculate": ["Calculate percentages"]},
        },
    }

    result = execute_agent_call(input_data)

    if result.get("success", False):
        content = result.get("data", {}).get("content", "")
        if "calculate" in content and "TOOL RESULTS" in content and "120" in content:
            logger.info("✅ Calculation Tool Test PASSED")
            logger.info(f"   Tool was used and calculation performed correctly")
            return True
        else:
            logger.info("❌ Calculation Tool Test FAILED - Tool not used or incorrect result")
            return False
    else:
        logger.info(
            f"❌ Calculation Tool Test FAILED - {result.get('data', {}).get('error', 'Unknown error')}"
        )
        return False


def test_multiple_tools():
    """Test multiple tools in one research."""
    logger.info("\n🔧 Testing Multiple Tools...")

    input_data = {
        "method": "quick_research",
        "parameters": {
            "query": "What are the latest AI developments and calculate the market growth rate?"
        },
        "tool_context": {
            "available_tools": ["web_search", "calculate"],
            "tool_descriptions": {
                "web_search": "Search the web for current information",
                "calculate": "Perform mathematical calculations",
            },
            "tool_usage_examples": {
                "web_search": ["Search for latest AI news"],
                "calculate": ["Calculate percentages"],
            },
        },
    }

    result = execute_agent_call(input_data)

    if result.get("success", False):
        content = result.get("data", {}).get("content", "")
        tools_used = []
        if "web_search" in content:
            tools_used.append("web_search")
        if "calculate" in content:
            tools_used.append("calculate")

        if len(tools_used) >= 1:
            logger.info("✅ Multiple Tools Test PASSED")
            logger.info(f"   Tools used: {tools_used}")
            return True
        else:
            logger.info("❌ Multiple Tools Test FAILED - No tools used")
            return False
    else:
        logger.info(
            f"❌ Multiple Tools Test FAILED - {result.get('data', {}).get('error', 'Unknown error')}"
        )
        return False


def test_deep_research_with_tools():
    """Test deep research with tool integration."""
    logger.info("\n🧠 Testing Deep Research with Tools...")

    input_data = {
        "method": "deep_research",
        "parameters": {
            "query": "Analyze AI market trends",
            "user_clarification": "Focus on 2024 data, include calculations",
        },
        "tool_context": {
            "available_tools": ["web_search", "calculate"],
            "tool_descriptions": {
                "web_search": "Search the web for current information",
                "calculate": "Perform mathematical calculations",
            },
            "tool_usage_examples": {
                "web_search": ["Search for latest AI news"],
                "calculate": ["Calculate percentages"],
            },
        },
    }

    result = execute_agent_call(input_data)

    if result.get("success", False):
        content = result.get("data", {}).get("content", "")
        if isinstance(content, dict):
            rounds = content.get("rounds", [])
            tools_used_in_rounds = []
            for round_data in rounds:
                round_tools = round_data.get("tools_used", [])
                tools_used_in_rounds.extend(round_tools)

            if tools_used_in_rounds:
                logger.info("✅ Deep Research with Tools Test PASSED")
                logger.info(f"   Tools used across rounds: {list(set(tools_used_in_rounds))}")
                return True
            else:
                logger.info("❌ Deep Research with Tools Test FAILED - No tools used")
                return False
        else:
            logger.info("❌ Deep Research with Tools Test FAILED - Unexpected content format")
            return False
    else:
        logger.info(
            f"❌ Deep Research with Tools Test FAILED - {result.get('data', {}).get('error', 'Unknown error')}"
        )
        return False


def test_agent_status():
    """Test agent status with tool information."""
    logger.info("\n📊 Testing Agent Status...")

    input_data = {
        "method": "get_agent_status",
        "parameters": {},
        "tool_context": {
            "available_tools": ["web_search", "calculate"],
            "tool_descriptions": {
                "web_search": "Search the web for current information",
                "calculate": "Perform mathematical calculations",
            },
            "tool_usage_examples": {
                "web_search": ["Search for latest AI news"],
                "calculate": ["Calculate percentages"],
            },
        },
    }

    result = execute_agent_call(input_data)

    if result.get("success", False):
        tool_info = result.get("data", {}).get("tool_integration", {})
        if tool_info.get("has_tools", False) and tool_info.get("tool_count", 0) == 2:
            logger.info("✅ Agent Status Test PASSED")
            logger.info(f"   Tools detected: {tool_info.get('available_tools', [])}")
            return True
        else:
            logger.info("❌ Agent Status Test FAILED - Tool information not found")
            return False
    else:
        logger.info(
            f"❌ Agent Status Test FAILED - {result.get('data', {}).get('error', 'Unknown error')}"
        )
        return False


def test_tool_usage_stats():
    """Test tool usage statistics."""
    logger.info("\n📈 Testing Tool Usage Stats...")

    input_data = {
        "method": "get_tool_usage_stats",
        "parameters": {},
        "tool_context": {
            "available_tools": ["web_search", "calculate"],
            "tool_descriptions": {
                "web_search": "Search the web for current information",
                "calculate": "Perform mathematical calculations",
            },
            "tool_usage_examples": {
                "web_search": ["Search for latest AI news"],
                "calculate": ["Calculate percentages"],
            },
        },
    }

    result = execute_agent_call(input_data)

    if result.get("success", False):
        stats = result.get("data", {})
        if stats.get("has_tools", False) and stats.get("tool_count", 0) == 2:
            logger.info("✅ Tool Usage Stats Test PASSED")
            logger.info(f"   Available tools: {stats.get('available_tools', [])}")
            logger.info(f"   Total executions: {stats.get('total_executions', 0)}")
            return True
        else:
            logger.info("❌ Tool Usage Stats Test FAILED - Stats not found")
            return False
    else:
        logger.info(
            f"❌ Tool Usage Stats Test FAILED - {result.get('data', {}).get('error', 'Unknown error')}"
        )
        return False


def execute_agent_call(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an agent call and return the result."""
    try:
        result = subprocess.run(
            ["python", "agent.py", json.dumps(input_data)],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            response = json.loads(result.stdout)
            return response.get("result", response)
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


def main():
    """Run comprehensive tool integration tests."""
    logger.info("🧪 COMPREHENSIVE TOOL INTEGRATION TEST SUITE")
    logger.info("=" * 60)

    tests = [
        ("Web Search Tool", test_web_search_tool),
        ("Calculation Tool", test_calculation_tool),
        ("Multiple Tools", test_multiple_tools),
        ("Deep Research with Tools", test_deep_research_with_tools),
        ("Agent Status", test_agent_status),
        ("Tool Usage Stats", test_tool_usage_stats),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            logger.info(f"❌ {test_name} Test FAILED with exception: {str(e)}")
            results.append((test_name, False))

    # Summary
    logger.info(f"\n📋 TEST SUMMARY")
    logger.info("=" * 60)
    passed = sum(1 for _, success in results if success)
    total = len(results)

    logger.info(f"Tests Passed: {passed}/{total}")

    for test_name, success in results:
        status_icon = "✅" if success else "❌"
        logger.info(f"{status_icon} {test_name}")

    if passed == total:
        logger.info(f"\n🎉 ALL TESTS PASSED! Tool integration is working perfectly.")
    else:
        logger.info(
            f"\n⚠️ {total - passed} test(s) failed. Check the output above for details."
        )

    return passed == total


if __name__ == "__main__":
    main()
