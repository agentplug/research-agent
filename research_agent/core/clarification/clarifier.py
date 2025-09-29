"""
Clarification Engine for Deep Research Mode

This module handles the clarification process for deep research, analyzing the query
and generating targeted questions to understand user intent better.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from ...llm_service.llm_service import LLMService


class ClarificationEngine:
    """Handles clarification question generation for deep research."""

    def __init__(self, llm_service: LLMService):
        """Initialize clarification engine."""
        self.llm_service = llm_service
        self.logger = logging.getLogger(__name__)

    def analyze_query_for_clarification(self, query: str) -> Dict[str, Any]:
        """
        Analyze the query and generate clarification questions.

        Args:
            query: The original research query

        Returns:
            Dictionary containing clarification questions and analysis
        """
        analysis_prompt = f"""You are a research analyst conducting deep research query analysis. Your task is to analyze the given query and identify areas that need clarification to provide the most targeted and useful research.

ORIGINAL QUERY: {query}

ANALYSIS INSTRUCTIONS:
1. Identify ambiguous terms, concepts, or scope that need clarification
2. Determine the user's likely intent, audience, and use case
3. Identify potential perspectives, angles, or aspects that could be explored
4. Consider time frame, geographic scope, or domain-specific requirements
5. Think about the depth level and technical sophistication needed

CLARIFICATION QUESTION GUIDELINES:
- Ask 3-5 targeted questions maximum
- Focus on the most important aspects that would significantly impact research direction
- Make questions specific and actionable
- Avoid overly broad or obvious questions
- Consider different user personas (student, professional, researcher, etc.)
- Think about practical applications and use cases

QUESTION CATEGORIES TO CONSIDER:
- Scope and boundaries (time, geography, domain)
- Depth and technical level (beginner, intermediate, expert)
- Purpose and use case (academic, professional, personal)
- Specific aspects or perspectives to focus on
- Constraints or preferences (budget, time, resources)

Return your analysis as valid JSON:
{{
    "query_analysis": "Detailed analysis of the query, identifying key areas needing clarification",
    "user_intent_assessment": "Assessment of likely user intent, audience, and use case",
    "clarification_questions": [
        "Specific question 1 about scope or intent",
        "Specific question 2 about depth or perspective",
        "Specific question 3 about use case or application",
        "Specific question 4 about constraints or preferences",
        "Specific question 5 about specific aspects to focus on"
    ],
    "research_direction": "Suggested research direction based on analysis"
}}"""

        system_prompt = """You are an expert research analyst specializing in deep research query analysis and clarification. You excel at identifying ambiguous aspects of research queries and generating targeted clarification questions that help researchers provide more focused and useful results."""

        try:
            response = self.llm_service.generate(
                input_data=analysis_prompt,
                system_prompt=system_prompt,
                temperature=0.0,
                return_json=True,
            )

            analysis = json.loads(response)

            return {
                "success": True,
                "data": analysis,
                "message": f"Generated {len(analysis.get('clarification_questions', []))} clarification questions",
            }

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self.logger.warning(f"Failed to parse clarification analysis: {e}")
            return {
                "success": False,
                "data": {"error": str(e)},
                "message": "Failed to generate clarification questions",
            }

    def format_clarification_questions(self, analysis: Dict[str, Any]) -> str:
        """
        Format clarification questions for user presentation.

        Args:
            analysis: The analysis result from analyze_query_for_clarification

        Returns:
            Formatted string with questions for user
        """
        if not analysis.get("success", False):
            return "Unable to generate clarification questions."

        data = analysis["data"]
        questions = data.get("clarification_questions", [])

        if not questions:
            return "No clarification questions generated."

        formatted_questions = []
        for i, question in enumerate(questions, 1):
            formatted_questions.append(f"{i}. {question}")

        return "\n".join(formatted_questions)

    def get_clarification_context(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract clarification context for intention generation.

        Args:
            analysis: The analysis result from analyze_query_for_clarification

        Returns:
            Dictionary with clarification context
        """
        if not analysis.get("success", False):
            return {}

        data = analysis["data"]
        return {
            "query_analysis": data.get("query_analysis", ""),
            "user_intent_assessment": data.get("user_intent_assessment", ""),
            "research_direction": data.get("research_direction", ""),
            "clarification_questions": data.get("clarification_questions", []),
        }
