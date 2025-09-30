#!/usr/bin/env python3
"""
Step-by-step debug script to show tool results for each round
"""

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from research_agent import ResearchAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the agent with tools
tool_context = {
    "available_tools": ["web_search"],
    "tool_descriptions": {"web_search": "Search the web for information"},
}

agent = ResearchAgent(tool_context=tool_context)

# Test with a simple query
query = "Who is the current US president?"
logger.info(f"🔍 Query: {query}")
logger.info("=" * 80)

# Step 1: Test first round
logger.info(f"\n📊 STEP 1: First Round")
logger.info("=" * 80)

first_round = agent.research_workflows.research_executor.execute_first_round(
    query, "standard"
)

logger.info(f"✅ First round completed")
logger.info(f"Tools used: {first_round.get('tools_used', [])}")
logger.info(f"Tool calls: {first_round.get('tool_calls', [])}")
logger.info(f"Tool results count: {len(first_round.get('tool_results', []))}")

# Show tool results for first round
tool_results = first_round.get("tool_results", [])
if tool_results:
    logger.info(f"\n🔧 First Round Tool Results:")
    for i, result in enumerate(tool_results):
        logger.info(f"  Result {i+1}:")
        logger.info(f"    Success: {result.get('success', False)}")
        logger.info(f"    Tool name: {result.get('tool_name', 'N/A')}")
        logger.info(f"    Full result: {result}")

        if result.get("tool_name") == "web_search":
            tool_result_data = result.get("result", {})
            logger.info(f"    Result data keys: {list(tool_result_data.keys())}")
            if "results" in tool_result_data:
                search_results = tool_result_data.get("results", [])
                logger.info(f"    Search results count: {len(search_results)}")
                if search_results:
                    logger.info(f"    First result: {search_results[0]}")
            if "error" in tool_result_data:
                logger.info(f"    Error: {tool_result_data.get('error')}")
            if "message" in tool_result_data:
                logger.info(f"    Message: {tool_result_data.get('message')}")

logger.info(f"\n📝 First Round Final Content:")
logger.info(f"{first_round.get('content', 'No content')}")

# Show URL tracking after first round
exclude_urls = (
    agent.research_workflows.research_executor.source_tracker.get_exclude_urls("urls")
)
logger.info(f"\n🔗 URLs tracked after Round 1: {exclude_urls}")

# Step 2: Test follow-up round
logger.info(f"\n📊 STEP 2: Follow-up Round")
logger.info("=" * 80)

follow_up = agent.research_workflows.research_executor.execute_followup_round(
    original_query=query, previous_results=[first_round], mode="standard"
)

logger.info(f"✅ Follow-up round completed")
logger.info(f"Tools used: {follow_up.get('tools_used', [])}")
logger.info(f"Tool calls: {follow_up.get('tool_calls', [])}")
logger.info(f"Tool results count: {len(follow_up.get('tool_results', []))}")

# Show tool results for follow-up round
tool_results = follow_up.get("tool_results", [])
if tool_results:
    logger.info(f"\n🔧 Follow-up Round Tool Results:")
    for i, result in enumerate(tool_results):
        logger.info(f"  Result {i+1}:")
        logger.info(f"    Success: {result.get('success', False)}")
        logger.info(f"    Tool name: {result.get('tool_name', 'N/A')}")
        logger.info(f"    Full result: {result}")

        if result.get("tool_name") == "web_search":
            tool_result_data = result.get("result", {})
            logger.info(f"    Result data keys: {list(tool_result_data.keys())}")
            if "results" in tool_result_data:
                search_results = tool_result_data.get("results", [])
                logger.info(f"    Search results count: {len(search_results)}")
                if search_results:
                    logger.info(f"    First result: {search_results[0]}")
            if "error" in tool_result_data:
                logger.info(f"    Error: {tool_result_data.get('error')}")
            if "message" in tool_result_data:
                logger.info(f"    Message: {tool_result_data.get('message')}")

logger.info(f"\n📝 Follow-up Round Final Content:")
logger.info(f"{follow_up.get('content', 'No content')}")

# Show URL tracking after follow-up round
exclude_urls = (
    agent.research_workflows.research_executor.source_tracker.get_exclude_urls("urls")
)
logger.info(f"\n🔗 URLs tracked after Round 2: {exclude_urls}")

# Step 3: Test full standard research (this will run 3 rounds total)
logger.info(f"\n📊 STEP 3: Full Standard Research")
logger.info("=" * 80)
logger.info("ℹ️  Note: This will run 3 rounds total (1 first + 2 follow-up)")
logger.info("ℹ️  Each round will process sources independently")
logger.info("=" * 80)

full_result = agent.standard_research(query)

if "rounds" in full_result:
    rounds = full_result.get("rounds", [])

    logger.info(f"✅ Full research completed")
    logger.info(f"Total rounds: {full_result.get('total_rounds', 'N/A')}")
    logger.info(f"Mode: {full_result.get('mode', 'N/A')}")
    logger.info(f"Research summary: {full_result.get('research_summary', 'N/A')}")

    for i, round_data in enumerate(rounds, 1):
        logger.info(f"\n🔍 Round {i} Summary:")
        logger.info(f"   Query: {round_data.get('query', 'N/A')}")
        logger.info(f"   Content preview: {round_data.get('content', 'No content')[:200]}...")
else:
    logger.info(f"❌ Full research failed: {full_result.get('error', 'Unknown error')}")
    logger.info(f"Full result: {full_result}")
