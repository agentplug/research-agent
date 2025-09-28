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
                f"Round {r['round']}: {r['query']}\n{r['content']}..."
                for r in previous_results
            ]
        )

        analysis_prompt = f"""Analyze research results and identify gaps.

Original Query: {original_query}
Previous Research:
{research_summary}

IMPORTANT: Only mark goal_reached as true if the research COMPLETELY answers the original query with no gaps or missing information.

Return JSON: {{"analysis": "analysis of the research results", "goal_reached": True/False, "next_query": "specific follow-up query"}}"""

        analysis_response = self.llm_service.generate(
            input_data=analysis_prompt,
            system_prompt="You are a research analyst specializing in gap analysis.",
            temperature=0.0,
            return_json=True,
        )

        try:
            analysis = json.loads(analysis_response)
            if analysis.get("goal_reached", False) or not analysis.get("next_query"):
                return None

            followup_content = self.llm_service.generate(
                input_data=analysis["next_query"],
                system_prompt="Build upon previous research and address specific gaps.",
                temperature=0.0,
            )

            return {
                "round": len(previous_results) + 1,
                "query": analysis["next_query"],
                "content": followup_content,
                "timestamp": get_current_timestamp(),
            }

        except Exception:
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
