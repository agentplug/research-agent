#!/usr/bin/env python3
"""
Super Simple Demo - Research with URL Tracking

This demo shows how the research agent automatically tracks URLs from previous rounds
and includes them in exclude_urls parameter to avoid duplicate processing.
"""

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_agent import ResearchAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
query = "Why Microsoft layoff this year?"
logger.info(f"🔍 Query: {query}")
logger.info("=" * 50)

# # Call instant research
# result = agent.instant_research(query)

# Standard research will automatically:
# 1. Track URLs from each round using SourceTracker
# 2. Include them in exclude_urls for subsequent rounds to avoid duplicates
# 3. Pass exclude_urls to MCP server web_search tool
# 4. Process results with full content extraction
result = agent.standard_research(query)

# Display the final answer
if isinstance(result, dict) and "rounds" in result:
    logger.info("\n🎯 FINAL ANSWER:")
    logger.info("=" * 50)
    logger.info(result)
else:
    logger.info("\n❌ ERROR:")
    logger.info(
        result.get("error", "Unknown error")
        if isinstance(result, dict)
        else str(result)
    )
