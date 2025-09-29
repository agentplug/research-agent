#!/usr/bin/env python3
"""
Step-by-step debug script to show tool results for each round
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from research_agent import ResearchAgent

# Initialize the agent with tools
tool_context = {
    "available_tools": ["web_search"],
    "tool_descriptions": {"web_search": "Search the web for information"},
}

agent = ResearchAgent(tool_context=tool_context)

# Test with a simple query
query = "Who is the current US president?"
print(f"🔍 Query: {query}")
print("=" * 80)

# Step 1: Test first round
print(f"\n📊 STEP 1: First Round")
print("=" * 80)

first_round = agent.research_workflows.research_executor.execute_first_round(
    query, "standard"
)

print(f"✅ First round completed")
print(f"Tools used: {first_round.get('tools_used', [])}")
print(f"Tool calls: {first_round.get('tool_calls', [])}")
print(f"Tool results count: {len(first_round.get('tool_results', []))}")

# Show tool results for first round
tool_results = first_round.get("tool_results", [])
if tool_results:
    print(f"\n🔧 First Round Tool Results:")
    for i, result in enumerate(tool_results):
        print(f"  Result {i+1}:")
        print(f"    Success: {result.get('success', False)}")
        print(f"    Tool name: {result.get('tool_name', 'N/A')}")
        print(f"    Full result: {result}")

        if result.get("tool_name") == "web_search":
            tool_result_data = result.get("result", {})
            print(f"    Result data keys: {list(tool_result_data.keys())}")
            if "results" in tool_result_data:
                search_results = tool_result_data.get("results", [])
                print(f"    Search results count: {len(search_results)}")
                if search_results:
                    print(f"    First result: {search_results[0]}")
            if "error" in tool_result_data:
                print(f"    Error: {tool_result_data.get('error')}")
            if "message" in tool_result_data:
                print(f"    Message: {tool_result_data.get('message')}")

print(f"\n📝 First Round Final Content:")
print(f"{first_round.get('content', 'No content')}")

# Show URL tracking after first round
exclude_urls = (
    agent.research_workflows.research_executor.source_tracker.get_exclude_urls("urls")
)
print(f"\n🔗 URLs tracked after Round 1: {exclude_urls}")

# Step 2: Test follow-up round
print(f"\n📊 STEP 2: Follow-up Round")
print("=" * 80)

follow_up = agent.research_workflows.research_executor.execute_followup_round(
    original_query=query, previous_results=[first_round], mode="standard"
)

print(f"✅ Follow-up round completed")
print(f"Tools used: {follow_up.get('tools_used', [])}")
print(f"Tool calls: {follow_up.get('tool_calls', [])}")
print(f"Tool results count: {len(follow_up.get('tool_results', []))}")

# Show tool results for follow-up round
tool_results = follow_up.get("tool_results", [])
if tool_results:
    print(f"\n🔧 Follow-up Round Tool Results:")
    for i, result in enumerate(tool_results):
        print(f"  Result {i+1}:")
        print(f"    Success: {result.get('success', False)}")
        print(f"    Tool name: {result.get('tool_name', 'N/A')}")
        print(f"    Full result: {result}")

        if result.get("tool_name") == "web_search":
            tool_result_data = result.get("result", {})
            print(f"    Result data keys: {list(tool_result_data.keys())}")
            if "results" in tool_result_data:
                search_results = tool_result_data.get("results", [])
                print(f"    Search results count: {len(search_results)}")
                if search_results:
                    print(f"    First result: {search_results[0]}")
            if "error" in tool_result_data:
                print(f"    Error: {tool_result_data.get('error')}")
            if "message" in tool_result_data:
                print(f"    Message: {tool_result_data.get('message')}")

print(f"\n📝 Follow-up Round Final Content:")
print(f"{follow_up.get('content', 'No content')}")

# Show URL tracking after follow-up round
exclude_urls = (
    agent.research_workflows.research_executor.source_tracker.get_exclude_urls("urls")
)
print(f"\n🔗 URLs tracked after Round 2: {exclude_urls}")

# Step 3: Test full standard research (this will run 3 rounds total)
print(f"\n📊 STEP 3: Full Standard Research")
print("=" * 80)
print("ℹ️  Note: This will run 3 rounds total (1 first + 2 follow-up)")
print("ℹ️  Each round will process sources independently")
print("=" * 80)

full_result = agent.standard_research(query)

if "rounds" in full_result:
    rounds = full_result.get("rounds", [])

    print(f"✅ Full research completed")
    print(f"Total rounds: {full_result.get('total_rounds', 'N/A')}")
    print(f"Mode: {full_result.get('mode', 'N/A')}")
    print(f"Research summary: {full_result.get('research_summary', 'N/A')}")

    for i, round_data in enumerate(rounds, 1):
        print(f"\n🔍 Round {i} Summary:")
        print(f"   Query: {round_data.get('query', 'N/A')}")
        print(f"   Content preview: {round_data.get('content', 'No content')[:200]}...")
else:
    print(f"❌ Full research failed: {full_result.get('error', 'Unknown error')}")
    print(f"Full result: {full_result}")
