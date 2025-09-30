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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
