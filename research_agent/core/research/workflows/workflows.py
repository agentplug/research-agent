"""
Main research workflows orchestrating the modular research pipeline.

This module coordinates the different workflow components to provide
comprehensive research capabilities with tool integration.
"""

from typing import Any, Dict, List, Optional

from .prompt_builder import PromptBuilder
from .research_executor import ResearchExecutor
from .research_modes import ResearchModes
from .response_formatter import ResponseFormatter
from .tool_analyzer import ToolAwareAnalyzer


class ResearchWorkflows:
    """Research workflows with tool integration using modular components."""

    def __init__(
        self,
        llm_service,
        analysis_engine,
        clarification_engine,
        intention_generator,
        available_tools: List[str] = None,
        tool_descriptions: Dict[str, str] = None,
    ):
        """
        Initialize research workflows with modular components.

        Args:
            llm_service: LLM service instance
            analysis_engine: Analysis engine instance
            clarification_engine: Clarification engine instance
            intention_generator: Intention generator instance
            available_tools: List of available tool names
            tool_descriptions: Dictionary of tool descriptions
        """
        self.llm_service = llm_service
        self.analysis_engine = analysis_engine
        self.clarification_engine = clarification_engine
        self.intention_generator = intention_generator
        self.available_tools = available_tools or []
        self.tool_descriptions = tool_descriptions or {}

        # Initialize modular components
        self.research_modes = ResearchModes()
        self.research_executor = ResearchExecutor(
            llm_service,
            analysis_engine,
            clarification_engine,
            intention_generator,
            available_tools,
            tool_descriptions,
        )
        self.response_formatter = ResponseFormatter()
        self.prompt_builder = PromptBuilder(available_tools, tool_descriptions)

    def instant_research(self, query: str) -> Dict[str, Any]:
        """
        Conduct instant research (1 round).

        Args:
            query: Research query

        Returns:
            Instant research result
        """
        try:
            # Execute single round
            result = self.research_executor.execute_first_round(query, "instant")

            # Format as instant response with proper structure
            return {
                "mode": "instant",
                "query": query,
                "content": result["content"],
                "timestamp": result["timestamp"],
                "rounds": [result],
            }

        except Exception as e:
            return self.response_formatter.format_error_response(str(e), "instant")

    def quick_research(self, query: str) -> Dict[str, Any]:
        """
        Conduct quick research (2 rounds).

        Args:
            query: Research query

        Returns:
            Quick research result
        """
        try:
            rounds = []

            # Execute first round
            first_round = self.research_executor.execute_first_round(query, "quick")
            rounds.append(first_round)

            # Execute follow-up round
            follow_up_round = self.research_executor.execute_followup_round(
                query, rounds, "quick"
            )
            rounds.append(follow_up_round)

            # Format response
            return self.response_formatter.format_quick_response(rounds)

        except Exception as e:
            return self.response_formatter.format_error_response(str(e), "quick")

    def standard_research(self, query: str) -> Dict[str, Any]:
        """
        Conduct standard research (3 rounds).

        Args:
            query: Research query

        Returns:
            Standard research result
        """
        try:
            rounds = []

            # Execute first round
            first_round = self.research_executor.execute_first_round(query, "standard")
            rounds.append(first_round)

            # Execute follow-up rounds
            for _ in range(2):  # 2 additional rounds
                follow_up_round = self.research_executor.execute_followup_round(
                    query, rounds, "standard"
                )
                rounds.append(follow_up_round)

            # Format response
            return self.response_formatter.format_standard_response(rounds)

        except Exception as e:
            return self.response_formatter.format_error_response(str(e), "standard")

    def deep_research(self, query: str, user_clarification: str = "") -> Dict[str, Any]:
        """
        Conduct deep research (4 rounds) with optional clarification.

        Args:
            query: Research query
            user_clarification: User clarification (if provided)

        Returns:
            Deep research result
        """
        try:
            rounds = []
            user_intention = ""

            # Handle clarification if needed
            if not user_clarification:
                # Generate clarification questions
                analysis = self.clarification_engine.analyze_query_for_clarification(query)
                clarification_questions = self.clarification_engine.format_clarification_questions(analysis)
                return self.response_formatter.format_clarification_response(
                    [clarification_questions]
                )

            # Generate intention from clarification
            clarification_context = {"query": query, "clarification": user_clarification}
            user_intention = self.intention_generator.generate_intention_paragraph(
                query, clarification_context, user_clarification
            )

            # Execute first round with intention
            first_round = self.research_executor.execute_first_round(
                query, "deep", user_intention
            )
            rounds.append(first_round)

            # Execute follow-up rounds
            for _ in range(3):  # 3 additional rounds
                follow_up_round = self.research_executor.execute_followup_round(
                    query, rounds, "deep"
                )
                rounds.append(follow_up_round)

            # Format response
            return self.response_formatter.format_deep_response(rounds)

        except Exception as e:
            return self.response_formatter.format_error_response(str(e), "deep")

    def get_tool_usage_stats(self) -> Dict[str, Any]:
        """
        Get tool usage statistics.

        Returns:
            Tool usage statistics
        """
        stats = {
            "available_tools": self.available_tools,
            "tool_descriptions": self.tool_descriptions,
            "research_modes": self.research_modes.get_mode_statistics(),
        }

        # Add executor statistics
        if hasattr(self.research_executor, "get_execution_statistics"):
            stats["executor_stats"] = self.research_executor.get_execution_statistics()

        return stats

    def validate_mode(self, mode: str) -> bool:
        """
        Validate research mode.

        Args:
            mode: Research mode name

        Returns:
            True if mode is valid
        """
        return self.research_modes.is_valid_mode(mode)

    def get_mode_info(self, mode: str) -> Dict[str, Any]:
        """
        Get information about a research mode.

        Args:
            mode: Research mode name

        Returns:
            Mode information dictionary
        """
        if not self.validate_mode(mode):
            return {"error": f"Invalid mode: {mode}"}

        return {
            "mode": mode,
            "rounds": self.research_modes.get_rounds_for_mode(mode),
            "description": self.research_modes.get_mode_description(mode),
            "analysis_depth": self.research_modes.get_analysis_depth(mode),
            "follow_up_strategy": self.research_modes.get_follow_up_strategy(mode),
            "uses_clarification": self.research_modes.should_use_clarification(mode),
        }

    def get_workflow_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive workflow statistics.

        Returns:
            Workflow statistics dictionary
        """
        return {
            "available_modes": self.research_modes.get_available_modes(),
            "mode_statistics": self.research_modes.get_mode_statistics(),
            "tool_statistics": self.get_tool_usage_stats(),
            "component_status": {
                "research_executor": hasattr(self, "research_executor"),
                "response_formatter": hasattr(self, "response_formatter"),
                "prompt_builder": hasattr(self, "prompt_builder"),
                "research_modes": hasattr(self, "research_modes"),
            },
        }
