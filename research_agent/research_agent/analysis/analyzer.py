"""Analysis engine for research gap analysis."""

import json
import logging
from datetime import date
from typing import Any, Dict, List, Optional

from .config import ModeConfig


class AnalysisEngine:
    """Handles analysis prompts and processing for research gaps."""

    def __init__(self, llm_service):
        """Initialize analysis engine."""
        self.llm_service = llm_service
        self.logger = logging.getLogger(__name__)

    def build_analysis_prompt(
        self, original_query: str, research_summary: str, mode: str
    ) -> str:
        """Build mode-specific analysis prompt with different analysis depths."""
        today = date.today()

        if mode == "instant":
            return self._build_instant_analysis_prompt(
                original_query, research_summary, today
            )
        elif mode == "quick":
            return self._build_quick_analysis_prompt(
                original_query, research_summary, today
            )
        elif mode == "standard":
            return self._build_standard_analysis_prompt(
                original_query, research_summary, today
            )
        elif mode == "deep":
            return self._build_deep_analysis_prompt(
                original_query, research_summary, today
            )
        else:
            return self._build_standard_analysis_prompt(
                original_query, research_summary, today
            )

    def _build_instant_analysis_prompt(
        self, original_query: str, research_summary: str, today: date
    ) -> str:
        """Build instant mode analysis prompt - minimal analysis."""
        return f"""You are conducting a quick research evaluation. Determine if the basic question is answered.

ORIGINAL QUERY: {original_query}

PREVIOUS RESEARCH RESULTS:
{research_summary}

Today's date: {today}

ANALYSIS INSTRUCTIONS:
1. Check if the main question is directly answered
2. Identify only major missing information
3. Only continue if the answer is clearly incomplete

GOAL COMPLETION CRITERIA:
- Mark goal_reached as TRUE if the main question is answered with basic facts
- Don't require comprehensive coverage or deep analysis
- Focus on direct answer to the core question

Return your analysis as valid JSON:
{{
    "analysis": "Brief assessment of whether the main question is answered",
    "goal_reached": true/false,
    "reasoning": "Simple explanation of completeness",
    "gaps_identified": ["only", "major", "missing", "information"],
    "next_query": "Simple follow-up question or null if goal reached"
}}"""

    def _build_quick_analysis_prompt(
        self, original_query: str, research_summary: str, today: date
    ) -> str:
        """Build quick mode analysis prompt - enhanced analysis."""
        return f"""You are conducting enhanced research evaluation. Assess completeness with context and examples.

ORIGINAL QUERY: {original_query}

PREVIOUS RESEARCH RESULTS:
{research_summary}

Today's date: {today}

ANALYSIS INSTRUCTIONS:
1. Evaluate if the query is answered with good context and examples
2. Check for missing important details or perspectives
3. Consider if additional context would improve understanding
4. Identify gaps that would enhance the analysis

GOAL COMPLETION CRITERIA:
- Mark goal_reached as TRUE if the answer includes context, examples, and covers main aspects
- Require good coverage but not exhaustive detail
- Consider practical implications and real-world context

NEXT QUERY GUIDELINES:
- Target specific missing context or examples
- Focus on enhancing understanding with practical details
- Be specific about what additional information is needed

Return your analysis as valid JSON:
{{
    "analysis": "Assessment of completeness with focus on context and examples",
    "goal_reached": true/false,
    "reasoning": "Explanation focusing on context and practical coverage",
    "gaps_identified": ["specific", "context", "or", "example", "gaps"],
    "next_query": "Targeted query for missing context or examples, or null if goal reached"
}}"""

    def _build_standard_analysis_prompt(
        self, original_query: str, research_summary: str, today: date
    ) -> str:
        """Build standard mode analysis prompt - comprehensive analysis."""
        return f"""You are conducting comprehensive research evaluation. Assess completeness with multiple perspectives.

ORIGINAL QUERY: {original_query}

PREVIOUS RESEARCH RESULTS:
{research_summary}

Today's date: {today}

ANALYSIS INSTRUCTIONS:
1. Evaluate completeness from multiple angles and perspectives
2. Check for missing viewpoints, counterarguments, or alternative approaches
3. Assess if all important sub-questions are addressed
4. Consider if additional depth or breadth would improve the analysis
5. Look for gaps in methodology, evidence, or reasoning

GOAL COMPLETION CRITERIA:
- Mark goal_reached as TRUE only if research covers all major aspects comprehensively
- Require multiple perspectives and thorough analysis
- Consider different viewpoints, methodologies, and evidence types
- Ensure no important sub-questions are left unaddressed

NEXT QUERY GUIDELINES:
- Target specific missing perspectives or methodologies
- Focus on gaps in comprehensive coverage
- Address specific sub-questions or alternative viewpoints
- Be precise about what additional analysis is needed

Return your analysis as valid JSON:
{{
    "analysis": "Comprehensive assessment covering multiple perspectives and thoroughness",
    "goal_reached": true/false,
    "reasoning": "Detailed explanation of completeness from multiple angles",
    "gaps_identified": ["specific", "perspectives", "methodologies", "or", "sub-questions"],
    "next_query": "Precise query targeting specific gaps in comprehensive coverage, or null if goal reached"
}}"""

    def _build_deep_analysis_prompt(
        self, original_query: str, research_summary: str, today: date
    ) -> str:
        """Build deep mode analysis prompt - exhaustive academic-level analysis."""
        return f"""You are conducting exhaustive academic-level research evaluation. Assess completeness with scholarly rigor.

ORIGINAL QUERY: {original_query}

PREVIOUS RESEARCH RESULTS:
{research_summary}

Today's date: {today}

ANALYSIS INSTRUCTIONS:
1. Conduct exhaustive evaluation with academic-level scrutiny
2. Assess theoretical frameworks, empirical evidence, and methodological rigor
3. Check for missing historical context, comparative analysis, or interdisciplinary perspectives
4. Evaluate if the research meets scholarly standards for depth and breadth
5. Consider gaps in critical analysis, theoretical grounding, or empirical validation
6. Look for missing nuances, edge cases, or complex interactions
7. Assess if the research addresses potential limitations, biases, or alternative interpretations

GOAL COMPLETION CRITERIA:
- Mark goal_reached as TRUE only if research provides exhaustive coverage with academic-level analysis
- Require scholarly depth, theoretical grounding, and comprehensive evidence
- Consider multiple theoretical frameworks, methodologies, and perspectives
- Ensure critical analysis, limitations, and alternative interpretations are addressed
- Require exhaustive coverage of all relevant aspects and sub-questions

NEXT QUERY GUIDELINES:
- Target specific gaps in academic rigor or theoretical depth
- Focus on missing scholarly perspectives or methodological approaches
- Address specific theoretical frameworks, empirical evidence, or critical analysis gaps
- Be extremely precise about what additional academic-level analysis is needed

Return your analysis as valid JSON:
{{
    "analysis": "Exhaustive academic-level assessment with scholarly rigor and theoretical depth",
    "goal_reached": true/false,
    "reasoning": "Detailed scholarly explanation of completeness with academic standards",
    "gaps_identified": ["specific", "theoretical", "methodological", "or", "scholarly", "gaps"],
    "next_query": "Highly precise query targeting specific gaps in academic-level analysis, or null if goal reached"
}}"""

    def analyze_research_gaps(
        self, original_query: str, research_summary: str, mode: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze research gaps and return analysis result."""
        analysis_prompt = self.build_analysis_prompt(
            original_query, research_summary, mode
        )
        system_prompt = ModeConfig.get_system_prompt(mode)

        analysis_response = self.llm_service.generate(
            input_data=analysis_prompt,
            system_prompt=system_prompt,
            temperature=0.0,
            return_json=True,
        )

        try:
            return json.loads(analysis_response)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self.logger.warning(
                f"Failed to parse analysis response: {e}. Response: {analysis_response[:200]}..."
            )
            return None

    def should_stop_research(self, analysis: Dict[str, Any]) -> bool:
        """Check if research should stop based on analysis results."""
        goal_reached = analysis.get("goal_reached", False)
        next_query = analysis.get("next_query")

        return (
            goal_reached or not next_query or next_query.lower() in ["null", "none", ""]
        )

    def generate_followup_content(self, analysis: Dict[str, Any], mode: str) -> str:
        """Generate follow-up content based on analysis."""
        today = date.today()
        next_query = analysis.get("next_query")
        gaps = analysis.get("gaps_identified", [])
        instruction = ModeConfig.get_followup_instruction(mode)

        followup_system_prompt = f"""Build upon the previous research to address specific gaps.

Identified Gaps: {gaps}

Today's date: {today}
Focus on: {next_query}

{instruction}
Only answer long if needed. If you can confidently answer directly and concisely, do so."""

        return self.llm_service.generate(
            input_data=next_query,
            system_prompt=followup_system_prompt,
            temperature=0.0,
        )
