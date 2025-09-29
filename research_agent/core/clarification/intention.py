"""
Intention Generator for Deep Research Mode

This module generates a comprehensive intention paragraph based on the original query
and user clarifications, which is then used in all subsequent LLM calls.
"""

import json
import logging
from typing import Any, Dict, Optional

from ...llm_service.llm_service import LLMService


class IntentionGenerator:
    """Generates user intention paragraph for deep research alignment."""

    def __init__(self, llm_service: LLMService):
        """Initialize intention generator."""
        self.llm_service = llm_service
        self.logger = logging.getLogger(__name__)

    def generate_intention_paragraph(
        self,
        original_query: str,
        clarification_context: Dict[str, Any],
        user_response: str,
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive intention paragraph based on query and clarifications.

        Args:
            original_query: The original research query
            clarification_context: Context from clarification analysis
            user_response: User's response to clarification questions

        Returns:
            Dictionary containing the intention paragraph
        """
        intention_prompt = f"""You are a research analyst creating a comprehensive intention paragraph for deep research. Your task is to synthesize the original query, clarification context, and user response into a clear, actionable intention statement.

ORIGINAL QUERY: {original_query}

CLARIFICATION CONTEXT:
Query Analysis: {clarification_context.get('query_analysis', '')}
User Intent Assessment: {clarification_context.get('user_intent_assessment', '')}
Research Direction: {clarification_context.get('research_direction', '')}
Clarification Questions Asked: {clarification_context.get('clarification_questions', [])}

USER RESPONSE: {user_response}

INTENTION PARAGRAPH REQUIREMENTS:
1. Create a comprehensive paragraph (2-4 sentences) that captures the user's true intent
2. Include specific details about scope, depth, perspective, and use case
3. Incorporate any preferences, constraints, or specific aspects mentioned
4. Make it actionable and specific enough to guide research direction
5. Ensure it reflects both the original query and user clarifications
6. Use clear, professional language suitable for research guidance

INTENTION PARAGRAPH STRUCTURE:
- Start with the core research objective
- Add specific scope, depth, and perspective details
- Include use case, audience, or application context
- Mention any constraints, preferences, or specific focus areas
- End with the desired outcome or research goal

Return your result as valid JSON:
{{
    "intention_paragraph": "Comprehensive paragraph capturing user's research intent and preferences",
    "key_focus_areas": ["area1", "area2", "area3"],
    "research_constraints": ["constraint1", "constraint2"],
    "target_audience": "Description of target audience or use case",
    "success_criteria": "What would constitute successful research completion"
}}"""

        system_prompt = """You are an expert research analyst specializing in synthesizing complex research requirements into clear, actionable intention statements. You excel at understanding user needs and creating comprehensive research guidance that ensures alignment between user intent and research execution."""

        try:
            response = self.llm_service.generate(
                input_data=intention_prompt,
                system_prompt=system_prompt,
                temperature=0.0,
                return_json=True,
            )

            intention_data = json.loads(response)

            return {
                "success": True,
                "data": intention_data,
                "message": "Intention paragraph generated successfully",
            }

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            self.logger.warning(f"Failed to parse intention generation: {e}")
            return {
                "success": False,
                "data": {"error": str(e)},
                "message": "Failed to generate intention paragraph",
            }

    def format_intention_for_prompt(self, intention_data: Dict[str, Any]) -> str:
        """
        Format intention data for inclusion in LLM prompts.

        Args:
            intention_data: The intention data from generate_intention_paragraph

        Returns:
            Formatted string for LLM prompts
        """
        if not intention_data.get("success", False):
            return ""

        data = intention_data["data"]
        intention_paragraph = data.get("intention_paragraph", "")
        key_focus_areas = data.get("key_focus_areas", [])
        target_audience = data.get("target_audience", "")

        formatted_intention = f"RESEARCH INTENTION: {intention_paragraph}"

        if key_focus_areas:
            focus_areas = ", ".join(key_focus_areas)
            formatted_intention += f"\nKEY FOCUS AREAS: {focus_areas}"

        if target_audience:
            formatted_intention += f"\nTARGET AUDIENCE: {target_audience}"

        return formatted_intention

    def get_research_guidance(self, intention_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract research guidance from intention data.

        Args:
            intention_data: The intention data from generate_intention_paragraph

        Returns:
            Dictionary with research guidance
        """
        if not intention_data.get("success", False):
            return {}

        data = intention_data["data"]
        return {
            "intention_paragraph": data.get("intention_paragraph", ""),
            "key_focus_areas": data.get("key_focus_areas", []),
            "research_constraints": data.get("research_constraints", []),
            "target_audience": data.get("target_audience", ""),
            "success_criteria": data.get("success_criteria", ""),
        }
