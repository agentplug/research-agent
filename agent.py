#!/usr/bin/env python3
"""
Research Agent - AgentHub integration entry point.

Enhanced research agent with tool integration and multi-round analysis.
"""

import json
import logging
import sys
from typing import Any, Dict, Optional

from research_agent import ResearchAgent

# Set up logging with cleaner format
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Disable verbose HTTP request logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

# Disable verbose source processing logging
logging.getLogger("research_agent.core.research.source_processing.parallel_executor").setLevel(logging.WARNING)
logging.getLogger("research_agent.core.research.source_processing.content_extractor").setLevel(logging.WARNING)
# Keep llm_processor logging enabled to see source analysis

# Disable verbose LLM service logging
logging.getLogger("research_agent.llm_service.model_detector").setLevel(logging.WARNING)

# Disable verbose research workflow logging
logging.getLogger("research_agent.core.research.workflows.research_executor").setLevel(logging.WARNING)
logging.getLogger("research_agent.core.tools.agenthub_mcp_client").setLevel(logging.WARNING)


def main():
    """Main entry point for AgentHub integration."""
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)

    try:
        # Parse input from command line
        input_data = json.loads(sys.argv[1])
        method = input_data.get("method")
        parameters = input_data.get("parameters", {})
        tool_context = input_data.get("tool_context", {})

        # Create agent instance with tool context
        logger.info(f"Creating agent with tool_context: {tool_context}")
        agent = ResearchAgent(tool_context=tool_context)
        logger.info(f"Agent created successfully. Tool executor available: {agent.research_workflows.research_executor.tool_executor is not None}")

        # Execute requested method
        if method == "instant_research":
            result = agent.instant_research(parameters.get("query", ""))
            print(json.dumps({"result": result}))
        elif method == "quick_research":
            result = agent.quick_research(parameters.get("query", ""))
            print(json.dumps({"result": result}))
        elif method == "standard_research":
            result = agent.standard_research(parameters.get("query", ""))
            print(json.dumps({"result": result}))
        elif method == "deep_research":
            result = agent.deep_research(
                parameters.get("query", ""), parameters.get("user_clarification", "")
            )
            print(json.dumps({"result": result}))
        elif method == "get_agent_status":
            result = agent.get_agent_status()
            print(json.dumps({"result": result}))
        elif method == "get_tool_usage_stats":
            result = agent.get_tool_usage_stats()
            print(json.dumps({"result": result}))
        else:
            print(json.dumps({"error": f"Unknown method: {method}"}))
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
