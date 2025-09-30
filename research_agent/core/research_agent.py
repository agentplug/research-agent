"""
ResearchAgent - Enhanced research agent with clarification system.

KISS & YAGNI: Keep only essential functionality.
Direct AgentHub interface - no unnecessary wrapper classes.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base_agent.base_agent import BaseAgent
from ..base_agent.error_handler import ErrorHandler
from ..llm_service.llm_service import get_shared_llm_service
from ..utils.helpers import ResearchHelpers
from ..utils.utils import format_response, get_current_timestamp
from .analysis.tool_aware_analyzer import ToolAwareAnalysisEngine
from .clarification import ClarificationEngine, IntentionGenerator
from .research.workflows import ResearchWorkflows

# Set up logger
logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """
    Enhanced research agent with clarification system - KISS & YAGNI implementation.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        config_path: Optional[str] = None,
        tool_context: Optional[Dict[str, Any]] = None,
    ):
        """Initialize with tool context and configuration."""
        # Initialize parent first
        super().__init__(tool_context=tool_context, logger_name="ResearchAgent")

        # Load config after parent initialization
        self.config_path = config_path or "config.json"
        self.config = self._load_config(self.config_path)

        # Initialize existing components
        self.model = model
        self.llm_service = get_shared_llm_service(model=model)
        self.research_history: List[Dict[str, Any]] = []

        # Initialize tool-aware modules
        self.analysis_engine = ToolAwareAnalysisEngine(
            self.llm_service, self.available_tools, self.tool_descriptions
        )
        self.clarification_engine = ClarificationEngine(self.llm_service)
        self.intention_generator = IntentionGenerator(self.llm_service)
        self.research_workflows = ResearchWorkflows(
            self.llm_service,
            self.analysis_engine,
            self.clarification_engine,
            self.intention_generator,
            self.available_tools,
            self.tool_descriptions,
        )
        self.helpers = ResearchHelpers()

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file."""
        # Use provided config_path or fall back to self.config_path
        path = config_path or getattr(self, "config_path", "config.json")

        try:
            config_file = Path(path)
            if config_file.exists():
                with open(config_file) as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            # Use error handler if available, otherwise just return empty config
            if hasattr(self, "error_handler"):
                self.error_handler.log_error(f"Failed to load config: {e}")
            return {}

    def instant_research(self, query: str) -> Dict[str, Any]:
        """Conduct instant research - single round quick answer."""
        result = self.research_workflows.instant_research(query)
        self._add_to_research_history("instant", query, result)
        return result

    def quick_research(self, query: str) -> Dict[str, Any]:
        """Conduct quick research - 2 rounds with gap analysis."""
        result = self.research_workflows.quick_research(query)
        self._add_to_research_history("quick", query, result)
        return result

    def standard_research(self, query: str) -> Dict[str, Any]:
        """Conduct standard research - 3 rounds with comprehensive analysis."""
        result = self.research_workflows.standard_research(query)
        self._add_to_research_history("standard", query, result)
        return result

    def deep_research(self, query: str, user_clarification: str = "") -> Dict[str, Any]:
        """
        Conduct deep research - 4 rounds with exhaustive analysis and clarification.

        If no user_clarification is provided, this method will:
        1. Generate clarification questions
        2. Ask user for input using input()
        3. Execute research with user's clarification
        """
        # If no clarification provided, get it interactively
        if not user_clarification:
            # Step 1: Get clarification questions
            result = self.research_workflows.deep_research(query, "")

            if result["data"].get("clarification_needed", False):
                # Step 2: Display questions and get user input
                logger.info("\n" + "=" * 60)
                logger.info("🧠 DEEP RESEARCH CLARIFICATION")
                logger.info("=" * 60)
                logger.info(f"Query: {query}")
                logger.info(
                    "\nTo provide the most comprehensive research, please answer these questions:"
                )
                logger.info("")

                questions = result["data"].get("clarification_questions", "")
                logger.info(questions)
                logger.info("")

                # Get user input
                user_clarification = input(
                    "Please provide your clarification (you can answer some or all questions): "
                ).strip()

                if not user_clarification:
                    user_clarification = "No specific clarifications provided. Please conduct comprehensive research."
                    logger.info(
                        "No clarification provided. Proceeding with comprehensive research..."
                    )
                else:
                    # Generate a contextual response using LLM
                    contextual_response = self._generate_contextual_response(
                        query, user_clarification
                    )
                    logger.info(f"\n{contextual_response}")

        # Execute research with clarification
        result = self.research_workflows.deep_research(query, user_clarification)
        self._add_to_research_history("deep", query, result)
        return result

    def _generate_contextual_response(self, query: str, user_clarification: str) -> str:
        """Generate a contextual response using LLM based on user clarification."""
        try:
            prompt = f"""Based on the user's research query and their clarification, generate a brief, natural response that acknowledges their input and sets expectations for the research.

Research Query: "{query}"
User Clarification: "{user_clarification}"

Generate a 1-2 sentence response that:
1. Acknowledges their specific requirements
2. Sets appropriate expectations for the research depth and focus
3. Sounds natural and professional

Examples:
- "Perfect! I'll conduct an expert-level analysis focusing on recent computer vision developments in semiconductors, tailored for academic research."
- "Excellent! I'll provide a comprehensive overview of AI developments over the past year, with particular emphasis on computer vision applications."
- "Great! I'll deliver an in-depth analysis suitable for academic research, focusing on the technical aspects you've specified."

Response:"""

            response = self.llm_service.generate(
                input_data=prompt,
                system_prompt="You are a helpful research assistant that generates natural, contextual responses to user clarifications.",
                temperature=0.3,  # Slightly creative but still focused
            )

            return response.strip()

        except Exception as e:
            # Fallback to simple response if LLM fails
            return f"Thank you! Proceeding with research based on your clarification: {user_clarification}"

    def get_research_history(self) -> List[Dict[str, Any]]:
        """Get research history."""
        return self.research_history.copy()

    def get_available_modes(self) -> List[str]:
        """Get available research modes."""
        return self.helpers.get_available_modes()

    def get_mode_description(self, mode: str) -> str:
        """Get description for a research mode."""
        return self.helpers.get_mode_description(mode)

    def _add_to_research_history(
        self, mode: str, query: str, result: Dict[str, Any]
    ) -> None:
        """Add entry to research history."""
        entry = self.helpers.format_research_history_entry(mode, query, result)
        self.research_history.append(entry)

    def get_tool_usage_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics."""
        return self.research_workflows.get_tool_usage_stats()

    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status."""
        try:
            # Get LLM service status
            llm_status = self.llm_service.get_service_status()

            # Get research history stats
            history_stats = {
                "total_researches": len(self.research_history),
                "modes_used": list({entry["mode"] for entry in self.research_history}),
                "last_research": self.research_history[-1]
                if self.research_history
                else None,
            }

            return format_response(
                success=True,
                data={
                    "agent_type": "ResearchAgent",
                    "model": self.model,
                    "config_loaded": bool(self.config),
                    "llm_service": llm_status,
                    "research_history": history_stats,
                    "available_modes": self.get_available_modes(),
                    "tool_integration": {
                        "has_tools": len(self.available_tools) > 0,
                        "available_tools": self.available_tools,
                        "tool_count": len(self.available_tools),
                        "tool_descriptions": self.tool_descriptions,
                    },
                    "timestamp": get_current_timestamp(),
                },
                message="Agent status retrieved successfully",
            )
        except Exception as e:
            return format_response(
                success=False,
                data={"error": str(e)},
                message="Failed to get agent status",
            )

    def test_agent(self) -> Dict[str, Any]:
        """Test agent capabilities."""
        try:
            test_results = {}

            # Test instant research
            instant_result = self.instant_research("What is Python?")
            test_results["instant_research"] = instant_result["success"]

            # Test quick research
            quick_result = self.quick_research("What is machine learning?")
            test_results["quick_research"] = quick_result["success"]

            # Test standard research
            standard_result = self.standard_research("What is artificial intelligence?")
            test_results["standard_research"] = standard_result["success"]

            # Test deep research (clarification)
            deep_result = self.deep_research("What are AI developments?")
            test_results["deep_research"] = deep_result["success"]
            test_results["clarification_system"] = deep_result["data"].get(
                "clarification_needed", False
            )

            # Test mode validation
            test_results["mode_validation"] = all(
                self.helpers.validate_mode(mode) for mode in self.get_available_modes()
            )

            all_tests_passed = all(test_results.values())

            return format_response(
                success=all_tests_passed,
                data={
                    "test_results": test_results,
                    "timestamp": get_current_timestamp(),
                },
                message="Agent testing completed"
                if all_tests_passed
                else "Some tests failed",
            )
        except Exception as e:
            return format_response(
                success=False,
                data={"error": str(e)},
                message="Agent testing failed",
            )
