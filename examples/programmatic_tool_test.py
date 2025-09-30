#!/usr/bin/env python3
"""
Programmatic Tool Integration Testing

This script shows how to test tool integration programmatically.
"""

import logging
from research_agent import ResearchAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_programmatic_tool_integration():
    """Test tool integration programmatically."""
    logger.info("🔧 Programmatic Tool Integration Testing")
    logger.info("=" * 50)

    # Initialize agent with tool context
    tool_context = {
        "available_tools": ["web_search", "calculate"],
        "tool_descriptions": {
            "web_search": "Search the web for current information",
            "calculate": "Perform mathematical calculations",
        },
        "tool_usage_examples": {
            "web_search": ["Search for latest AI news"],
            "calculate": ["Calculate percentages"],
        },
    }

    agent = ResearchAgent(tool_context=tool_context)

    # Test 1: Web Search Tool
    logger.info("\n🔍 Test 1: Web Search Tool")
    try:
        result = agent.instant_research("What is the latest news about AI?")
        if result.get("success", False):
            content = result.get("data", {}).get("content", "")
            if "web_search" in content and "TOOL RESULTS" in content:
                logger.info("✅ Web search tool used successfully")
            else:
                logger.info("❌ Web search tool not used")
        else:
            logger.info(
                f"❌ Research failed: {result.get('data', {}).get('error', 'Unknown error')}"
            )
    except Exception as e:
        logger.info(f"❌ Exception: {str(e)}")

    # Test 2: Calculation Tool
    logger.info("\n🧮 Test 2: Calculation Tool")
    try:
        result = agent.instant_research("Calculate 15% of 250")
        if result.get("success", False):
            content = result.get("data", {}).get("content", "")
            if "calculate" in content and "TOOL RESULTS" in content:
                logger.info("✅ Calculation tool used successfully")
            else:
                logger.info("❌ Calculation tool not used")
        else:
            logger.info(
                f"❌ Research failed: {result.get('data', {}).get('error', 'Unknown error')}"
            )
    except Exception as e:
        logger.info(f"❌ Exception: {str(e)}")

    # Test 3: Agent Status
    logger.info("\n📊 Test 3: Agent Status")
    try:
        status = agent.get_agent_status()
        if status.get("success", False):
            tool_info = status.get("data", {}).get("tool_integration", {})
            logger.info(f"✅ Agent status retrieved")
            logger.info(f"   Tools available: {tool_info.get('available_tools', [])}")
            logger.info(f"   Tool count: {tool_info.get('tool_count', 0)}")
        else:
            logger.info(
                f"❌ Status check failed: {status.get('data', {}).get('error', 'Unknown error')}"
            )
    except Exception as e:
        logger.info(f"❌ Exception: {str(e)}")

    # Test 4: Tool Usage Stats
    logger.info("\n📈 Test 4: Tool Usage Stats")
    try:
        stats = agent.get_tool_usage_stats()
        logger.info(f"✅ Tool usage stats retrieved")
        logger.info(f"   Total executions: {stats.get('total_executions', 0)}")
        logger.info(f"   Available tools: {stats.get('available_tools', [])}")
    except Exception as e:
        logger.info(f"❌ Exception: {str(e)}")

    logger.info("\n🎉 Programmatic testing completed!")


if __name__ == "__main__":
    test_programmatic_tool_integration()
