#!/usr/bin/env python3
"""
Complete Workflow Example - URL Tracking with MCP Server

This example demonstrates the complete workflow:
1. Research agent tracks URLs from tool results
2. Excludes processed URLs in follow-up rounds
3. MCP server receives exclude_urls parameter
4. Results are processed with full content extraction
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_agent import ResearchAgent

# Initialize the agent with tools configured for MCP server
tool_context = {
    "available_tools": ["web_search"],
    "tool_descriptions": {
        "web_search": "Search the web for a query with AI-powered query rewriting for better results"
    },
    "tool_usage_examples": {
        "web_search": [
            "Search for current information about topics",
            "Find recent news and updates",
        ]
    },
    "tool_parameters": {
        "web_search": {
            "query": {"type": "string", "description": "Search query"},
            "exclude_urls": {
                "type": "array",
                "description": "URLs to exclude from results",
                "default": [],
            },
        }
    },
    "tool_return_types": {"web_search": "object"},
    "tool_namespaces": {"web_search": "mcp"},
}

agent = ResearchAgent(tool_context=tool_context)

# Example query
query = "What are the latest developments in AI research?"
print(f"🔍 Research Query: {query}")
print("=" * 60)

print("\n📋 Workflow Overview:")
print("1. Round 1: Search with empty exclude_urls")
print("2. URLs from Round 1 are tracked in SourceTracker")
print("3. Round 2: Search with exclude_urls from Round 1")
print("4. URLs from Round 2 are added to tracking")
print("5. Round 3: Search with exclude_urls from Rounds 1 & 2")
print("6. Final synthesis of all unique results")

print("\n🚀 Starting multi-round research...")
print("=" * 60)

# Run standard research (3 rounds)
result = agent.standard_research(query)

# Display results
if isinstance(result, dict) and "rounds" in result:
    print(f"\n✅ Research completed in {len(result['rounds'])} rounds")
    print("=" * 60)

    for i, round_data in enumerate(result["rounds"], 1):
        print(f"\n📊 Round {i}:")
        print(f"Query: {round_data.get('query', 'N/A')}")
        print(f"Content: {round_data.get('content', 'N/A')[:200]}...")

    print(f"\n🎯 Final Answer:")
    print("=" * 60)
    print(result.get("content", "No final answer available"))

    # Show URL tracking statistics
    if hasattr(agent, "research_workflows") and hasattr(
        agent.research_workflows, "research_executor"
    ):
        stats = (
            agent.research_workflows.research_executor.source_tracker.get_statistics()
        )
        print(f"\n📈 URL Tracking Statistics:")
        print(f"Total URLs processed: {stats['data']['processed_urls_count']}")
        print(f"Unique domains: {stats['data']['processed_domains_count']}")

else:
    print("\n❌ Error:")
    print(
        result.get("error", "Unknown error")
        if isinstance(result, dict)
        else str(result)
    )

print("\n🎉 Complete workflow example finished!")
