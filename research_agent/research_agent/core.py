"""
ResearchAgent - Simple research agent implementation.

KISS & YAGNI: Keep only essential functionality.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..base_agent.core import BaseAgent
from ..llm_service.core import LLMService, get_shared_llm_service
from ..utils.utils import format_response, get_current_timestamp


class ResearchAgent(BaseAgent):
    """
    Simple research agent - KISS & YAGNI implementation.
    """

    def __init__(self, model: Optional[str] = None):
        """Initialize with minimal required parameters."""
        super().__init__()
        self.llm_service = get_shared_llm_service(model=model)
        self.research_history: List[Dict[str, Any]] = []

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Required abstract method implementation."""
        query = request.get("query", "")
        mode = request.get("mode", "instant")

        if mode == "instant":
            return self.instant_research(query)
        elif mode == "quick":
            return self.quick_research(query)
        elif mode == "standard":
            return self.standard_research(query)
        elif mode == "deep":
            return self.deep_research(query)
        else:
            return format_response(
                success=False,
                data={"error": f"Unknown mode: {mode}"},
                message="Invalid research mode",
            )

    def _first_round_query(self, query: str, mode: str) -> Dict[str, Any]:
        """Execute the first round of research."""
        system_prompts = {
            "instant": "Provide quick, accurate answers. Focus on key facts.",
            "quick": "Provide enhanced analysis with context and examples.",
            "standard": "Conduct comprehensive research with multiple perspectives.",
            "deep": "Conduct exhaustive research with academic-level analysis.",
        }

        temperatures = {"instant": 0.0, "quick": 0.0, "standard": 0.0, "deep": 0.0}

        content = self.llm_service.generate(
            input_data=query,
            system_prompt=system_prompts.get(
                mode, "You are a helpful research assistant."
            ),
            temperature=temperatures.get(mode, 0.0),
        )

        return {
            "round": 1,
            "query": query,
            "content": content,
            "timestamp": get_current_timestamp(),
        }

    def _follow_up_round_query(
        self, original_query: str, previous_results: List[Dict[str, Any]], mode: str
    ) -> Optional[Dict[str, Any]]:
        """Execute a follow-up round with gap analysis."""
        research_summary = "\n".join(
            [
                f"Round {r['round']}:\nTried Query: {r['query']}\nReceived Answer: {r['content']}..."
                for r in previous_results
            ]
        )

        analysis_prompt = f"""You are a research analyst conducting gap analysis. Your task is to evaluate whether the research has fully answered the original query and identify what's missing.

ORIGINAL QUERY: {original_query}

PREVIOUS RESEARCH RESULTS:
{research_summary}

ANALYSIS INSTRUCTIONS:
1. Compare the research results against the original query requirements
2. Identify specific gaps, missing information, or unanswered aspects
3. Determine if the research comprehensively addresses ALL aspects of the original query
4. If gaps exist, formulate a precise follow-up query that targets the missing information

GOAL COMPLETION CRITERIA:
- Mark goal_reached as TRUE only if the research provides complete, comprehensive answers to ALL aspects of the original query
- Consider depth, accuracy, completeness, and relevance
- Ensure no important sub-questions or aspects are left unaddressed

NEXT QUERY GUIDELINES:
- Be specific and targeted to fill identified gaps
- Avoid repeating previous queries
- Focus on missing information, not general exploration
- Make the query actionable and precise

Return your analysis as valid JSON:
{{
    "analysis": "Detailed analysis of research completeness, identifying specific gaps and strengths",
    "goal_reached": true/false,
    "reasoning": "Explanation of why goal is/isn't reached based on completeness criteria",
    "gaps_identified": ["list", "of", "specific", "gaps", "or", "missing", "information"],
    "next_query": "Precise follow-up query targeting the most critical gap, or null if goal reached"
}}"""

        analysis_response = self.llm_service.generate(
            input_data=analysis_prompt,
            system_prompt="You are a research analyst specializing in gap analysis and research completeness evaluation.",
            temperature=0.0,
            return_json=True,
        )

        try:
            analysis = json.loads(analysis_response)

            # Check if goal is reached or no next query provided
            goal_reached = analysis.get("goal_reached", False)
            next_query = analysis.get("next_query")

            if (
                goal_reached
                or not next_query
                or next_query.lower() in ["null", "none", ""]
            ):
                return None

            # Generate follow-up content with improved context
            followup_system_prompt = f"""Build upon the previous research to address specific gaps.

Identified Gaps: {analysis.get('gaps_identified', [])}

Focus on: {next_query}

Provide comprehensive information that fills the identified gaps while building upon previous findings."""

            followup_content = self.llm_service.generate(
                input_data=next_query,
                system_prompt=followup_system_prompt,
                temperature=0.0,
            )

            return {
                "round": len(previous_results) + 1,
                "query": next_query,
                "content": followup_content,
                "timestamp": get_current_timestamp(),
                "analysis": analysis.get("analysis", ""),
                "gaps_targeted": analysis.get("gaps_identified", []),
            }

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # Log the error for debugging but don't fail the research
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                f"Failed to parse analysis response: {e}. Response: {analysis_response[:200]}..."
            )
            return None

    def instant_research(self, query: str) -> Dict[str, Any]:
        """Single round quick answer."""
        try:
            start_time = datetime.now()
            first_round = self._first_round_query(query, "instant")
            execution_time = (datetime.now() - start_time).total_seconds()

            result = format_response(
                success=True,
                data={
                    "mode": "instant",
                    "query": query,
                    "content": first_round["content"],
                    "execution_time": round(execution_time, 2),
                    "research_rounds": 1,
                    "timestamp": get_current_timestamp(),
                },
                message="Instant research completed",
            )

            self.research_history.append(
                {
                    "mode": "instant",
                    "query": query,
                    "result": result,
                    "timestamp": get_current_timestamp(),
                }
            )

            return result

        except Exception as e:
            return format_response(
                success=False, data={"error": str(e)}, message="Instant research failed"
            )

    def quick_research(self, query: str) -> Dict[str, Any]:
        """2 rounds with gap analysis."""
        try:
            start_time = datetime.now()
            results = []

            # Round 1
            first_round = self._first_round_query(query, "quick")
            results.append(first_round)

            # Round 2
            follow_up = self._follow_up_round_query(query, results, "quick")
            if follow_up:
                results.append(follow_up)

            execution_time = (datetime.now() - start_time).total_seconds()

            # Combine results into JSON structure
            combined_content: Dict[str, Any] = {
                "research_summary": f"Research completed in {len(results)} rounds",
                "total_rounds": len(results),
                "rounds": [],
            }

            for result in results:
                combined_content["rounds"].append(
                    {
                        "round_number": result["round"],
                        "query": result["query"],
                        "content": result["content"],
                        "timestamp": result["timestamp"],
                    }
                )

            response = format_response(
                success=True,
                data={
                    "mode": "quick",
                    "query": query,
                    "content": combined_content,
                    "execution_time": round(execution_time, 2),
                    "research_rounds": len(results),
                    "timestamp": get_current_timestamp(),
                },
                message=f"Quick research completed ({len(results)} rounds)",
            )

            self.research_history.append(
                {
                    "mode": "quick",
                    "query": query,
                    "result": response,
                    "timestamp": get_current_timestamp(),
                }
            )

            return response

        except Exception as e:
            return format_response(
                success=False, data={"error": str(e)}, message="Quick research failed"
            )

    def standard_research(self, query: str) -> Dict[str, Any]:
        """3 rounds with comprehensive analysis."""
        try:
            start_time = datetime.now()
            results = []

            # Round 1
            first_round = self._first_round_query(query, "standard")
            results.append(first_round)

            # Rounds 2-3: Use for loop
            for _ in range(2):
                follow_up = self._follow_up_round_query(query, results, "standard")
                if follow_up:
                    results.append(follow_up)
                else:
                    break

            execution_time = (datetime.now() - start_time).total_seconds()

            # Combine results into JSON structure
            combined_content: Dict[str, Any] = {
                "research_summary": f"Comprehensive research completed in {len(results)} rounds",
                "total_rounds": len(results),
                "rounds": [],
            }

            for result in results:
                combined_content["rounds"].append(
                    {
                        "round_number": result["round"],
                        "query": result["query"],
                        "content": result["content"],
                        "timestamp": result["timestamp"],
                    }
                )

            response = format_response(
                success=True,
                data={
                    "mode": "standard",
                    "query": query,
                    "content": combined_content,
                    "execution_time": round(execution_time, 2),
                    "research_rounds": len(results),
                    "timestamp": get_current_timestamp(),
                },
                message=f"Standard research completed ({len(results)} rounds)",
            )

            self.research_history.append(
                {
                    "mode": "standard",
                    "query": query,
                    "result": response,
                    "timestamp": get_current_timestamp(),
                }
            )

            return response

        except Exception as e:
            return format_response(
                success=False,
                data={"error": str(e)},
                message="Standard research failed",
            )

    def deep_research(self, query: str) -> Dict[str, Any]:
        """4 rounds with exhaustive analysis."""
        try:
            start_time = datetime.now()
            results = []

            # Round 1
            first_round = self._first_round_query(query, "deep")
            results.append(first_round)

            # Rounds 2-4
            for _ in range(3):
                follow_up = self._follow_up_round_query(query, results, "deep")
                if follow_up:
                    results.append(follow_up)
                else:
                    break

            execution_time = (datetime.now() - start_time).total_seconds()

            # Combine results into JSON structure
            combined_content: Dict[str, Any] = {
                "research_summary": f"Exhaustive research completed in {len(results)} rounds",
                "total_rounds": len(results),
                "rounds": [],
            }

            for result in results:
                combined_content["rounds"].append(
                    {
                        "round_number": result["round"],
                        "query": result["query"],
                        "content": result["content"],
                        "timestamp": result["timestamp"],
                    }
                )

            response = format_response(
                success=True,
                data={
                    "mode": "deep",
                    "query": query,
                    "content": combined_content,
                    "execution_time": round(execution_time, 2),
                    "research_rounds": len(results),
                    "timestamp": get_current_timestamp(),
                },
                message=f"Deep research completed ({len(results)} rounds)",
            )

            self.research_history.append(
                {
                    "mode": "deep",
                    "query": query,
                    "result": response,
                    "timestamp": get_current_timestamp(),
                }
            )

            return response

        except Exception as e:
            return format_response(
                success=False, data={"error": str(e)}, message="Deep research failed"
            )
