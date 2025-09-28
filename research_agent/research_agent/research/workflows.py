"""Research workflow implementations."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from ...utils.utils import format_response, get_current_timestamp
from .round_manager import RoundManager


class ResearchWorkflows:
    """Handles different research workflow implementations."""

    def __init__(self, llm_service, analysis_engine):
        """Initialize research workflows."""
        self.llm_service = llm_service
        self.analysis_engine = analysis_engine
        self.round_manager = RoundManager()

    def execute_first_round(self, query: str, mode: str) -> Dict[str, Any]:
        """Execute the first round of research."""
        today = date.today()
        system_prompts = {
            "instant": f"Today's date: {today}. Provide quick, accurate answers. Focus on key facts.",
            "quick": f"Today's date: {today}. Provide enhanced analysis with context and examples.",
            "standard": f"Today's date: {today}. Conduct comprehensive research with multiple perspectives.",
            "deep": f"Today's date: {today}. Conduct exhaustive research with academic-level analysis.",
        }

        temperatures = {"instant": 0.0, "quick": 0.0, "standard": 0.0, "deep": 0.0}

        content = self.llm_service.generate(
            input_data=query,
            system_prompt=system_prompts.get(
                mode, "You are a helpful research assistant."
            ),
            temperature=temperatures.get(mode, 0.0),
        )

        return self.round_manager.build_first_round_result(query, content)

    def execute_followup_round(
        self, original_query: str, previous_results: List[Dict[str, Any]], mode: str
    ) -> Optional[Dict[str, Any]]:
        """Execute a follow-up round with gap analysis."""
        research_summary = self.round_manager.build_research_summary(previous_results)

        analysis = self.analysis_engine.analyze_research_gaps(
            original_query, research_summary, mode
        )

        if not analysis or self.analysis_engine.should_stop_research(analysis):
            return None

        followup_content = self.analysis_engine.generate_followup_content(
            analysis, mode
        )

        return self.round_manager.build_round_result(
            analysis, followup_content, previous_results
        )

    def instant_research(self, query: str) -> Dict[str, Any]:
        """Conduct instant research - single round quick answer."""
        try:
            start_time = datetime.now()

            first_round = self.execute_first_round(query, "instant")
            execution_time = (datetime.now() - start_time).total_seconds()

            return format_response(
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

        except Exception as e:
            return format_response(
                success=False, data={"error": str(e)}, message="Instant research failed"
            )

    def quick_research(self, query: str) -> Dict[str, Any]:
        """Conduct quick research - 2 rounds with gap analysis."""
        try:
            start_time = datetime.now()
            results = []

            # Round 1
            first_round = self.execute_first_round(query, "quick")
            results.append(first_round)

            # Round 2
            follow_up = self.execute_followup_round(query, results, "quick")
            if follow_up:
                results.append(follow_up)

            execution_time = (datetime.now() - start_time).total_seconds()

            # Build response
            response = self._build_multi_round_response(
                query, "quick", results, execution_time
            )

            return response

        except Exception as e:
            return format_response(
                success=False, data={"error": str(e)}, message="Quick research failed"
            )

    def standard_research(self, query: str) -> Dict[str, Any]:
        """Conduct standard research - 3 rounds with comprehensive analysis."""
        try:
            start_time = datetime.now()
            results = []

            # Round 1
            first_round = self.execute_first_round(query, "standard")
            results.append(first_round)

            # Rounds 2-3
            for _ in range(2):
                follow_up = self.execute_followup_round(query, results, "standard")
                if follow_up:
                    results.append(follow_up)
                else:
                    break

            execution_time = (datetime.now() - start_time).total_seconds()

            # Build response
            response = self._build_multi_round_response(
                query, "standard", results, execution_time
            )

            return response

        except Exception as e:
            return format_response(
                success=False,
                data={"error": str(e)},
                message="Standard research failed",
            )

    def deep_research(self, query: str) -> Dict[str, Any]:
        """Conduct deep research - 4 rounds with exhaustive analysis."""
        try:
            start_time = datetime.now()
            results = []

            # Round 1
            first_round = self.execute_first_round(query, "deep")
            results.append(first_round)

            # Rounds 2-4
            for _ in range(3):
                follow_up = self.execute_followup_round(query, results, "deep")
                if follow_up:
                    results.append(follow_up)
                else:
                    break

            execution_time = (datetime.now() - start_time).total_seconds()

            # Build response
            response = self._build_multi_round_response(
                query, "deep", results, execution_time
            )

            return response

        except Exception as e:
            return format_response(
                success=False, data={"error": str(e)}, message="Deep research failed"
            )

    def _build_multi_round_response(
        self,
        query: str,
        mode: str,
        results: List[Dict[str, Any]],
        execution_time: float,
    ) -> Dict[str, Any]:
        """Build response for multi-round research."""
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

        return format_response(
            success=True,
            data={
                "mode": mode,
                "query": query,
                "content": combined_content,
                "execution_time": round(execution_time, 2),
                "research_rounds": len(results),
                "timestamp": get_current_timestamp(),
            },
            message=f"{mode.title()} research completed ({len(results)} rounds)",
        )
