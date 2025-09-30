#!/usr/bin/env python3
"""
Complete Workflow Example - URL Tracking with MCP Server

This example demonstrates the complete workflow:
1. Research agent tracks URLs from tool results
2. Excludes processed URLs in follow-up rounds
3. MCP server receives exclude_urls parameter
4. Results are processed with full content extraction
"""

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_agent import ResearchAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
logger.info(f"🔍 Research Query: {query}")
logger.info("=" * 60)

logger.info("\n📋 Workflow Overview:")
logger.info("1. Round 1: Search with empty exclude_urls")
logger.info("2. URLs from Round 1 are tracked in SourceTracker")
logger.info("3. Round 2: Search with exclude_urls from Round 1")
logger.info("4. URLs from Round 2 are added to tracking")
logger.info("5. Round 3: Search with exclude_urls from Rounds 1 & 2")
logger.info("6. Final synthesis of all unique results")

logger.info("\n🚀 Starting multi-round research...")
logger.info("=" * 60)

# Run standard research (3 rounds)
result = agent.standard_research(query)

# Display results
if isinstance(result, dict) and "rounds" in result:
    logger.info(f"\n✅ Research completed in {len(result['rounds'])} rounds")
    logger.info("=" * 60)

    for i, round_data in enumerate(result["rounds"], 1):
        logger.info(f"\n📊 Round {i}:")
        logger.info(f"Query: {round_data.get('query', 'N/A')}")
        logger.info(f"Content: {round_data.get('content', 'N/A')[:200]}...")

    logger.info(f"\n🎯 Final Answer:")
    logger.info("=" * 60)
    logger.info(result.get("content", "No final answer available"))

    # Show URL tracking statistics
    if hasattr(agent, "research_workflows") and hasattr(
        agent.research_workflows, "research_executor"
    ):
        stats = (
            agent.research_workflows.research_executor.source_tracker.get_statistics()
        )
        logger.info(f"\n📈 URL Tracking Statistics:")
        logger.info(f"Total URLs processed: {stats['data']['processed_urls_count']}")
        logger.info(f"Unique domains: {stats['data']['processed_domains_count']}")

else:
    logger.info("\n❌ Error:")
    logger.info(
        result.get("error", "Unknown error")
        if isinstance(result, dict)
        else str(result)
    )

logger.info("\n🎉 Complete workflow example finished!")
