"""Enhanced research workflow implementations with clarification system."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from ...utils.utils import format_response, get_current_timestamp
from .round_manager import RoundManager


class ResearchWorkflows:
    """Handles different research workflow implementations with clarification support."""

    def __init__(
        self,
        llm_service,
        analysis_engine,
        clarification_engine=None,
        intention_generator=None,
    ):
        """Initialize research workflows."""
        self.llm_service = llm_service
        self.analysis_engine = analysis_engine
        self.clarification_engine = clarification_engine
        self.intention_generator = intention_generator
        self.round_manager = RoundManager()

    def execute_first_round(
        self, query: str, mode: str, intention_paragraph: str = ""
    ) -> Dict[str, Any]:
        """Execute the first round of research."""
        today = date.today()
        system_prompts = {
            "instant": f"Today's date: {today}. Provide quick, accurate answers. Focus on key facts.",
            "quick": f"Today's date: {today}. Provide enhanced analysis with context and examples.",
            "standard": f"Today's date: {today}. Conduct comprehensive research with multiple perspectives.",
            "deep": f"Today's date: {today}. Conduct exhaustive research with academic-level analysis.",
        }

        temperatures = {"instant": 0.0, "quick": 0.0, "standard": 0.0, "deep": 0.0}

        # Add intention paragraph to deep research prompts
        system_prompt = system_prompts.get(
            mode, "You are a helpful research assistant."
        )
        if mode == "deep" and intention_paragraph:
            system_prompt = f"{system_prompt}\n\n{intention_paragraph}\n\nEnsure all research aligns with this intention and addresses the specific focus areas mentioned."

        content = self.llm_service.generate(
            input_data=query,
            system_prompt=system_prompt,
            temperature=temperatures.get(mode, 0.0),
        )

        return self.round_manager.build_first_round_result(query, content)

    def execute_followup_round(
        self,
        original_query: str,
        previous_results: List[Dict[str, Any]],
        mode: str,
        intention_paragraph: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Execute a follow-up round with gap analysis."""
        research_summary = self.round_manager.build_research_summary(previous_results)

        analysis = self.analysis_engine.analyze_research_gaps(
            original_query, research_summary, mode
        )

        if not analysis or self.analysis_engine.should_stop_research(analysis):
            return None

        # Add intention paragraph to follow-up prompts for deep research
        followup_content = self.analysis_engine.generate_followup_content(
            analysis, mode
        )

        if mode == "deep" and intention_paragraph:
            # Enhance follow-up content with intention alignment
            enhanced_prompt = f"""Build upon the previous research to address specific gaps while maintaining alignment with the research intention.

{intention_paragraph}

Identified Gaps: {analysis.get("gaps_identified", [])}
Next Query: {analysis.get("next_query", "")}

Ensure the response:
1. Addresses the identified gaps
2. Maintains alignment with the research intention
3. Focuses on the key areas specified in the intention
4. Provides academic-level analysis as requested

Today's date: {date.today()}
Focus on: {analysis.get("next_query", "")}

Conduct exhaustive research with academic-level analysis.
Only answer long if needed. If you can confidently answer directly and concisely, do so."""

            followup_content = self.llm_service.generate(
                input_data=analysis.get("next_query", ""),
                system_prompt=enhanced_prompt,
                temperature=0.0,
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

    def deep_research(self, query: str, user_clarification: str = "") -> Dict[str, Any]:
        """Conduct deep research - 4 rounds with exhaustive analysis and clarification."""
        try:
            start_time = datetime.now()
            results = []
            intention_paragraph = ""

            # Step 1: Generate clarification questions (if not already provided)
            if not user_clarification and self.clarification_engine:
                clarification_analysis = (
                    self.clarification_engine.analyze_query_for_clarification(query)
                )

                if clarification_analysis.get("success", False):
                    clarification_questions = (
                        self.clarification_engine.format_clarification_questions(
                            clarification_analysis
                        )
                    )
                    clarification_context = (
                        self.clarification_engine.get_clarification_context(
                            clarification_analysis
                        )
                    )

                    # Return clarification questions to user
                    return format_response(
                        success=True,
                        data={
                            "mode": "deep",
                            "query": query,
                            "clarification_needed": True,
                            "clarification_questions": clarification_questions,
                            "clarification_context": clarification_context,
                            "timestamp": get_current_timestamp(),
                            "next_step": "Please provide your clarification and call deep_research again with the same query and your clarification as the second parameter.",
                        },
                        message="Clarification required for deep research. Please provide your answers to the questions above.",
                    )
                else:
                    # Fallback if clarification fails
                    user_clarification = "No specific clarifications provided. Please conduct comprehensive research."

            # Step 2: Generate intention paragraph (if clarification provided)
            if user_clarification and self.intention_generator:
                clarification_context = {
                    "query_analysis": "",
                    "user_intent_assessment": "",
                    "research_direction": "",
                    "clarification_questions": [],
                }
                intention_result = (
                    self.intention_generator.generate_intention_paragraph(
                        query, clarification_context, user_clarification
                    )
                )

                if intention_result.get("success", False):
                    intention_paragraph = (
                        self.intention_generator.format_intention_for_prompt(
                            intention_result
                        )
                    )

            # Step 3: Execute research rounds with intention alignment
            # Round 1
            first_round = self.execute_first_round(query, "deep", intention_paragraph)
            results.append(first_round)

            # Rounds 2-4
            for _ in range(3):
                follow_up = self.execute_followup_round(
                    query, results, "deep", intention_paragraph
                )
                if follow_up:
                    results.append(follow_up)
                else:
                    break

            execution_time = (datetime.now() - start_time).total_seconds()

            # Build response
            response = self._build_multi_round_response(
                query, "deep", results, execution_time
            )

            # Add intention paragraph to response
            if intention_paragraph:
                response["data"]["intention_paragraph"] = intention_paragraph

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
