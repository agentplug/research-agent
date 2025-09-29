#!/usr/bin/env python3
"""
Programmatic Tool Integration Testing

This script shows how to test tool integration programmatically.
"""

from research_agent.research_agent.core import ResearchAgent


def test_programmatic_tool_integration():
    """Test tool integration programmatically."""
    print("🔧 Programmatic Tool Integration Testing")
    print("=" * 50)

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
    print("\n🔍 Test 1: Web Search Tool")
    try:
        result = agent.instant_research("What is the latest news about AI?")
        if result.get("success", False):
            content = result.get("data", {}).get("content", "")
            if "web_search" in content and "TOOL RESULTS" in content:
                print("✅ Web search tool used successfully")
            else:
                print("❌ Web search tool not used")
        else:
            print(
                f"❌ Research failed: {result.get('data', {}).get('error', 'Unknown error')}"
            )
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

    # Test 2: Calculation Tool
    print("\n🧮 Test 2: Calculation Tool")
    try:
        result = agent.instant_research("Calculate 15% of 250")
        if result.get("success", False):
            content = result.get("data", {}).get("content", "")
            if "calculate" in content and "TOOL RESULTS" in content:
                print("✅ Calculation tool used successfully")
            else:
                print("❌ Calculation tool not used")
        else:
            print(
                f"❌ Research failed: {result.get('data', {}).get('error', 'Unknown error')}"
            )
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

    # Test 3: Agent Status
    print("\n📊 Test 3: Agent Status")
    try:
        status = agent.get_agent_status()
        if status.get("success", False):
            tool_info = status.get("data", {}).get("tool_integration", {})
            print(f"✅ Agent status retrieved")
            print(f"   Tools available: {tool_info.get('available_tools', [])}")
            print(f"   Tool count: {tool_info.get('tool_count', 0)}")
        else:
            print(
                f"❌ Status check failed: {status.get('data', {}).get('error', 'Unknown error')}"
            )
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

    # Test 4: Tool Usage Stats
    print("\n📈 Test 4: Tool Usage Stats")
    try:
        stats = agent.get_tool_usage_stats()
        print(f"✅ Tool usage stats retrieved")
        print(f"   Total executions: {stats.get('total_executions', 0)}")
        print(f"   Available tools: {stats.get('available_tools', [])}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

    print("\n🎉 Programmatic testing completed!")


if __name__ == "__main__":
    test_programmatic_tool_integration()
