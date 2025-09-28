"""
Research Agent - AgentHub integration entry point.

This module provides the main entry point for the research agent,
including command-line interface and AgentHub integration.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from research_agent.base_agent.error_handler import ErrorHandler
from research_agent.research_agent.core import ResearchAgent
from research_agent.utils.utils import format_response


class ResearchAgentHub:
    """
    Research Agent for AgentHub integration.

    Provides the main interface for AgentHub integration and command-line usage.
    """

    def __init__(self, config_path: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Research Agent Hub with Phase 2 integration.

        Args:
            config_path: Path to configuration file
            model: Specific LLM model to use
        """
        self.config_path = config_path or "config.json"
        self.config = self._load_config()
        self.model = model
        self.agent = None
        self.error_handler = ErrorHandler("ResearchAgentHub")

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Configuration dictionary
        """
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file) as f:
                    return json.load(f)
            else:
                # Return default configuration
                return {
                    "ai": {"temperature": 0.1, "max_tokens": None, "timeout": 30},
                    "research": {
                        "max_sources_per_round": 10,
                        "max_rounds": 12,
                        "timeout_per_round": 300,
                    },
                }
        except Exception as e:
            self.error_handler.log_error(e, {"config_path": self.config_path})
            return {}

    def initialize_agent(self) -> bool:
        """
        Initialize the research agent with Phase 2 integration.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.agent = ResearchAgent(model=self.model)
            return True
        except Exception as e:
            self.error_handler.log_error(e, {"component": "agent_initialization"})
            return False

    def instant_research(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Conduct instant research.

        Args:
            query: Research query
            context: Additional context

        Returns:
            Research results
        """
        if not self.agent:
            if not self.initialize_agent():
                return format_response(
                    success=False, message="Failed to initialize agent"
                )

        return self.agent.instant_research(query)

    def quick_research(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Conduct quick research.

        Args:
            query: Research query
            context: Additional context

        Returns:
            Research results
        """
        if not self.agent:
            if not self.initialize_agent():
                return format_response(
                    success=False, message="Failed to initialize agent"
                )

        return self.agent.quick_research(query)

    def standard_research(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Conduct standard research.

        Args:
            query: Research query
            context: Additional context

        Returns:
            Research results
        """
        if not self.agent:
            if not self.initialize_agent():
                return format_response(
                    success=False, message="Failed to initialize agent"
                )

        return self.agent.standard_research(query)

    def deep_research(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Conduct deep research.

        Args:
            query: Research query
            context: Additional context

        Returns:
            Research results
        """
        if not self.agent:
            if not self.initialize_agent():
                return format_response(
                    success=False, message="Failed to initialize agent"
                )

        return self.agent.deep_research(query)

    def solve(
        self,
        query: str,
        mode: str = "standard",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Solve a problem using appropriate research mode.

        Args:
            query: Problem query
            mode: Research mode
            context: Additional context

        Returns:
            Solution results
        """
        if not self.agent:
            return format_response(success=False, message="Agent not initialized")

        request = {
            "method": "solve",
            "query": query,
            "mode": mode,
            "context": context or {},
        }

        return self.agent.handle_request(request)

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get comprehensive agent status including Phase 2 components.

        Returns:
            Agent status information
        """
        if not self.agent:
            return format_response(success=False, message="Agent not initialized")

        try:
            # Get base session info
            session_info = self.agent.get_session_info()

            # Get Phase 2 component status
            llm_status = self.agent.get_llm_service_status()
            mode_selector_status = self.agent.get_mode_selector_status()
            source_tracker_status = self.agent.get_source_tracker_status()
            temp_file_manager_status = self.agent.get_temp_file_manager_status()

            # Enhance session info with Phase 2 data
            if session_info.get("success"):
                session_info["data"].update(
                    {
                        "current_mode": self.agent.get_current_mode(),
                        "current_round": self.agent.current_round,
                        "llm_service": llm_status,
                        "mode_selector": mode_selector_status,
                        "source_tracker": source_tracker_status,
                        "temp_file_manager": temp_file_manager_status,
                        "phase_2_features": {
                            "real_llm_integration": llm_status.get("type") == "real",
                            "intelligent_mode_selection": mode_selector_status.get(
                                "enabled", False
                            ),
                            "source_tracking": source_tracker_status.get("data", {})
                            .get("statistics", {})
                            .get("total_sources", 0)
                            >= 0,
                            "temp_file_management": temp_file_manager_status.get(
                                "data", {}
                            ).get("enabled", False),
                            "aisuite_integration": llm_status.get(
                                "client_available", False
                            ),
                        },
                    }
                )

            return session_info

        except Exception as e:
            return self.error_handler.handle_error(
                e, {"component": "get_status"}, "Error getting agent status"
            )

    def test_agent(self) -> Dict[str, Any]:
        """
        Test agent capabilities.

        Returns:
            Test results
        """
        if not self.agent:
            return format_response(success=False, message="Agent not initialized")

        return self.agent.test_research_capabilities()


def main() -> None:
    """Main entry point for command-line usage with Phase 2 integration."""
    parser = argparse.ArgumentParser(
        description="Research Agent - Deep research capabilities with Phase 2 LLM integration"
    )
    parser.add_argument(
        "--config", help="Path to configuration file", default="config.json"
    )
    parser.add_argument(
        "--model", help="Specific LLM model to use (e.g., 'ollama:llama3.1:8b')"
    )
    parser.add_argument(
        "--mode",
        choices=["instant", "quick", "standard", "deep"],
        help="Research mode",
        default="standard",
    )
    parser.add_argument("--query", help="Research query")
    parser.add_argument("--context", help="Additional context as JSON string")
    parser.add_argument("--test", action="store_true", help="Test agent capabilities")
    parser.add_argument("--status", action="store_true", help="Show agent status")
    parser.add_argument(
        "--auto-mode", action="store_true", help="Use intelligent mode selection"
    )

    args = parser.parse_args()

    # Initialize agent hub with model selection
    agent_hub = ResearchAgentHub(args.config, args.model)

    if not agent_hub.initialize_agent():
        print("Error: Failed to initialize agent")
        sys.exit(1)

    try:
        # Parse context if provided
        context = None
        if args.context:
            try:
                context = json.loads(args.context)
            except json.JSONDecodeError:
                print("Error: Invalid JSON in context argument")
                sys.exit(1)

        # Handle different commands
        if args.test:
            result = agent_hub.test_agent()
        elif args.status:
            result = agent_hub.get_agent_status()
        else:
            # Conduct research with intelligent mode selection
            if not args.query:
                print("Error: --query is required for research operations")
                sys.exit(1)

            # Use intelligent mode selection if requested
            if args.auto_mode:
                result = agent_hub.solve(args.query, context={"auto_select_mode": True})
            else:
                # Use specified mode
                if args.mode == "instant":
                    result = agent_hub.instant_research(args.query, context)
                elif args.mode == "quick":
                    result = agent_hub.quick_research(args.query, context)
                elif args.mode == "standard":
                    result = agent_hub.standard_research(args.query, context)
                elif args.mode == "deep":
                    result = agent_hub.deep_research(args.query, context)
                else:
                    result = agent_hub.solve(args.query, args.mode, context)

        # Print result
        print(json.dumps(result, indent=2))

        # Exit with appropriate code
        if result.get("success", False):
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
