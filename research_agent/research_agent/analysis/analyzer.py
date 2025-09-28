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
        """Build mode-specific analysis prompt."""
        today = date.today()
        config = ModeConfig.get_mode_config(mode)

        return f"""You are a research analyst conducting {config['focus']} gap analysis. Your task is to evaluate whether the research has fully answered the original query and identify what's missing.

ORIGINAL QUERY: {original_query}

PREVIOUS RESEARCH RESULTS:
{research_summary}

Today's date: {today}

ANALYSIS INSTRUCTIONS:
1. Compare the research results against the original query requirements
2. Identify specific gaps, missing information, or unanswered aspects
3. Determine if the research provides {config['completeness_threshold']}
4. If gaps exist, formulate a {config['query_style']} follow-up query that targets the missing information

GOAL COMPLETION CRITERIA:
- Mark goal_reached as TRUE only if the research provides {config['completeness_threshold']}
- Consider depth, accuracy, completeness, and relevance
- Ensure no important sub-questions or aspects are left unaddressed
- For {mode} mode: Focus on {config['depth']}

NEXT QUERY GUIDELINES:
- Be {config['query_style']} to fill identified gaps
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
