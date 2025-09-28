#!/usr/bin/env python3
"""
Simple Tool Integration Test

Demonstrates tool integration features of the Research Agent.
"""

import json
import subprocess


def test_web_search():
    """Test web search tool integration."""
    print("🔍 Testing Web Search Tool...")

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

    result = subprocess.run(
        ["python", "agent.py", json.dumps(input_data)], capture_output=True, text=True
    )

    if result.returncode == 0:
        response = json.loads(result.stdout)
        result_data = response.get("result", {})

        if result_data.get("success", False):
            content = result_data.get("data", {}).get("content", "")
            if "web_search" in content and "TOOL RESULTS" in content:
                print("✅ Web Search Tool Test PASSED")
                print(f"   Tool was used and results integrated")
                return True
            else:
                print("❌ Web Search Tool Test FAILED - Tool not used")
                return False
        else:
            print(
                f"❌ Web Search Tool Test FAILED - {result_data.get('data', {}).get('error', 'Unknown error')}"
            )
            return False
    else:
        print(f"❌ Web Search Tool Test FAILED - Execution error: {result.stderr}")
        return False


def test_calculation():
    """Test calculation tool integration."""
    print("\n🧮 Testing Calculation Tool...")

    input_data = {
        "method": "instant_research",
        "parameters": {"query": "Calculate 25% of 480"},
        "tool_context": {
            "available_tools": ["calculate"],
            "tool_descriptions": {"calculate": "Perform mathematical calculations"},
            "tool_usage_examples": {"calculate": ["Calculate percentages"]},
        },
    }

    result = subprocess.run(
        ["python", "agent.py", json.dumps(input_data)], capture_output=True, text=True
    )

    if result.returncode == 0:
        response = json.loads(result.stdout)
        result_data = response.get("result", {})

        if result_data.get("success", False):
            content = result_data.get("data", {}).get("content", "")
            if (
                "calculate" in content
                and "TOOL RESULTS" in content
                and "120" in content
            ):
                print("✅ Calculation Tool Test PASSED")
                print(f"   Tool was used and calculation performed correctly")
                return True
            else:
                print(
                    "❌ Calculation Tool Test FAILED - Tool not used or incorrect result"
                )
                return False
        else:
            print(
                f"❌ Calculation Tool Test FAILED - {result_data.get('data', {}).get('error', 'Unknown error')}"
            )
            return False
    else:
        print(f"❌ Calculation Tool Test FAILED - Execution error: {result.stderr}")
        return False


def test_agent_status():
    """Test agent status with tool information."""
    print("\n📊 Testing Agent Status...")

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

    result = subprocess.run(
        ["python", "agent.py", json.dumps(input_data)], capture_output=True, text=True
    )

    if result.returncode == 0:
        response = json.loads(result.stdout)
        result_data = response.get("result", {})

        if result_data.get("success", False):
            tool_info = result_data.get("data", {}).get("tool_integration", {})
            if (
                tool_info.get("has_tools", False)
                and tool_info.get("tool_count", 0) == 2
            ):
                print("✅ Agent Status Test PASSED")
                print(f"   Tools detected: {tool_info.get('available_tools', [])}")
                return True
            else:
                print("❌ Agent Status Test FAILED - Tool information not found")
                return False
        else:
            print(
                f"❌ Agent Status Test FAILED - {result_data.get('data', {}).get('error', 'Unknown error')}"
            )
            return False
    else:
        print(f"❌ Agent Status Test FAILED - Execution error: {result.stderr}")
        return False


def main():
    """Run all tool integration tests."""
    print("🧪 TOOL INTEGRATION TEST SUITE")
    print("=" * 50)

    tests = [
        ("Web Search Tool", test_web_search),
        ("Calculation Tool", test_calculation),
        ("Agent Status", test_agent_status),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} Test FAILED with exception: {str(e)}")
            results.append((test_name, False))

    # Summary
    print(f"\n📋 TEST SUMMARY")
    print("=" * 50)
    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")

    for test_name, success in results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}")

    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! Tool integration is working correctly.")
    else:
        print(
            f"\n⚠️ {total - passed} test(s) failed. Check the output above for details."
        )

    return passed == total


if __name__ == "__main__":
    main()
