#!/usr/bin/env python3
"""
Super Simple Demo - Instant Research
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_agent import ResearchAgent

# Initialize the agent with tools
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

# Simple instant research call
query = "Who is the current US president?"
print(f"🔍 Query: {query}")
print("=" * 50)

# # Call instant research
# result = agent.instant_research(query)

result = agent.standard_research(query)

# Display the final answer
if isinstance(result, dict) and "rounds" in result:
    print("\n🎯 FINAL ANSWER:")
    print("=" * 50)
    print(result)
else:
    print("\n❌ ERROR:")
    print(
        result.get("error", "Unknown error")
        if isinstance(result, dict)
        else str(result)
    )
