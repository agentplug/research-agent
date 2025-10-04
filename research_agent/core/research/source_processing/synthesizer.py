"""
Synthesizer for combining multiple processed sources into comprehensive answers.

This module handles the synthesis of multiple source summaries into
a coherent, comprehensive answer to research questions.
"""

import logging
from datetime import date
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SourceSynthesizer:
    """Synthesizes processed sources into comprehensive answers."""

    def __init__(self, llm_service):
        """
        Initialize source synthesizer.

        Args:
            llm_service: LLM service instance for synthesis
        """
        self.llm_service = llm_service

    def synthesize_sources(
        self,
        processed_sources: List[Dict[str, Any]],
        original_query: str,
        follow_up_query: str = "",
    ) -> str:
        """
        Synthesize processed sources into a comprehensive answer.

        Args:
            processed_sources: List of processed source summaries
            original_query: Original research query
            follow_up_query: Current follow-up query

        Returns:
            Synthesized answer
        """
        if not processed_sources:
            return "No relevant sources found to answer the research question."

        current_query = follow_up_query if follow_up_query else original_query
        sources_text = self._prepare_source_summaries(processed_sources)
        
        # Log the summary parts being used for synthesis
        logger.info(f"Synthesizing {len(processed_sources)} source summaries")
        logger.info(f"Summary parts: {sources_text[:500]}...")
        
        synthesis_prompt = self._build_synthesis_prompt(current_query, sources_text)

        try:
            synthesis_result = self.llm_service.generate(
                input_data=f"Question: {current_query}\nSources: {sources_text}",
                system_prompt=synthesis_prompt,
                temperature=0.0,
            )

            result = synthesis_result.strip()
            logger.info(f"Synthesis result: {result[:200]}...")
            return result

        except Exception as e:
            return f"Error synthesizing sources: {str(e)}"

    def _prepare_source_summaries(self, processed_sources: List[Dict[str, Any]]) -> str:
        """
        Prepare formatted source summaries for synthesis.

        Args:
            processed_sources: List of processed source summaries

        Returns:
            Formatted source summaries text
        """
        source_summaries = []
        # Limit to top 10 sources to prevent token overflow
        max_sources = 10
        sources_to_process = processed_sources[:max_sources]
        
        if len(processed_sources) > max_sources:
            logger.info(f"Limiting synthesis to top {max_sources} sources (out of {len(processed_sources)} total)")
        
        for i, source in enumerate(sources_to_process, 1):
            source_summaries.append(
                f"Source {i} ({source['source_type']}):\n"
                f"Title: {source['title']}\n"
                f"URL: {source['url']}\n"
                f"Summary: {source['processed_summary']}\n"
            )

        return "\n".join(source_summaries)

    def _build_synthesis_prompt(self, current_query: str, sources_text: str) -> str:
        """
        Build the system prompt for source synthesis.

        Args:
            current_query: Current research query
            sources_text: Formatted source summaries

        Returns:
            Formatted synthesis prompt
        """
        today = date.today()
        current_year = today.year
        current_month = today.strftime("%B")

        return f"""You are a research assistant synthesizing multiple sources into a comprehensive answer.

CRITICAL: Today's date is {today} ({current_month} {current_year}).

TASK: Synthesize the provided sources into a comprehensive, accurate answer to the research question.

RESEARCH QUESTION: {current_query}

SOURCES TO SYNTHESIZE:
{sources_text}

INSTRUCTIONS:
1. **Synthesize information from all relevant sources**
2. **Provide a comprehensive answer that addresses the research question**
3. **Cite specific sources when making claims**
4. **Ensure accuracy and avoid contradictions**
5. **Structure the answer logically and clearly**
6. **Include specific facts, data, and insights from the sources**

RESPONSE FORMAT:
Provide a comprehensive answer that synthesizes information from the sources. Include specific citations and ensure the answer directly addresses the research question.

Focus on: {current_query}"""

    def get_synthesis_statistics(
        self, processed_sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get statistics about the processed sources.

        Args:
            processed_sources: List of processed source summaries

        Returns:
            Dictionary containing synthesis statistics
        """
        if not processed_sources:
            return {"total_sources": 0, "source_types": {}, "avg_relevance": 0.0}

        source_types = {}
        total_relevance = 0.0

        for source in processed_sources:
            source_type = source.get("source_type", "unknown")
            source_types[source_type] = source_types.get(source_type, 0) + 1
            total_relevance += source.get("relevance_score", 0.0)

        avg_relevance = (
            total_relevance / len(processed_sources) if processed_sources else 0.0
        )

        return {
            "total_sources": len(processed_sources),
            "source_types": source_types,
            "avg_relevance": avg_relevance,
            "relevance_range": {
                "min": min(
                    source.get("relevance_score", 0.0) for source in processed_sources
                ),
                "max": max(
                    source.get("relevance_score", 0.0) for source in processed_sources
                ),
            },
        }
