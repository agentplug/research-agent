#!/usr/bin/env python3
"""
Simple Tool Integration Testing Guide

This script provides easy ways to test tool integration.
"""

import json
import subprocess


def test_web_search():
    """Test web search tool."""
    print("🔍 Testing Web Search Tool...")

    cmd = [
        "python",
        "agent.py",
        json.dumps(
            {
                "method": "instant_research",
                "parameters": {"query": "What is the latest news about AI?"},
                "tool_context": {
                    "available_tools": ["web_search"],
                    "tool_descriptions": {
                        "web_search": "Search the web for current information"
                    },
                },
            }
        ),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            content = response.get("result", {}).get("data", {}).get("content", "")
            if "web_search" in content and "TOOL RESULTS" in content:
                print("✅ Web Search Tool Test PASSED")
                return True
            else:
                print("❌ Web Search Tool Test FAILED - Tool not used")
                return False
        else:
            print(f"❌ Web Search Tool Test FAILED - {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Web Search Tool Test FAILED - {str(e)}")
        return False


def test_calculation():
    """Test calculation tool."""
    print("\n🧮 Testing Calculation Tool...")

    cmd = [
        "python",
        "agent.py",
        json.dumps(
            {
                "method": "instant_research",
                "parameters": {"query": "Calculate 15% of 250"},
                "tool_context": {
                    "available_tools": ["calculate"],
                    "tool_descriptions": {
                        "calculate": "Perform mathematical calculations"
                    },
                },
            }
        ),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            content = response.get("result", {}).get("data", {}).get("content", "")
            if "calculate" in content and "TOOL RESULTS" in content:
                print("✅ Calculation Tool Test PASSED")
                return True
            else:
                print("❌ Calculation Tool Test FAILED - Tool not used")
                return False
        else:
            print(f"❌ Calculation Tool Test FAILED - {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Calculation Tool Test FAILED - {str(e)}")
        return False


def test_agent_status():
    """Test agent status."""
    print("\n📊 Testing Agent Status...")

    cmd = [
        "python",
        "agent.py",
        json.dumps(
            {
                "method": "get_agent_status",
                "parameters": {},
                "tool_context": {
                    "available_tools": ["web_search", "calculate"],
                    "tool_descriptions": {
                        "web_search": "Search the web for current information",
                        "calculate": "Perform mathematical calculations",
                    },
                },
            }
        ),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            tool_info = (
                response.get("result", {}).get("data", {}).get("tool_integration", {})
            )
            if tool_info.get("has_tools", False):
                print("✅ Agent Status Test PASSED")
                print(f"   Tools detected: {tool_info.get('available_tools', [])}")
                return True
            else:
                print("❌ Agent Status Test FAILED - No tool info")
                return False
        else:
            print(f"❌ Agent Status Test FAILED - {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Agent Status Test FAILED - {str(e)}")
        return False


def main():
    """Run simple tool integration tests."""
    print("🧪 SIMPLE TOOL INTEGRATION TEST")
    print("=" * 40)

    tests = [
        ("Web Search", test_web_search),
        ("Calculation", test_calculation),
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
    print("=" * 40)
    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")

    for test_name, success in results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}")

    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! Tool integration is working.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")


if __name__ == "__main__":
    main()
