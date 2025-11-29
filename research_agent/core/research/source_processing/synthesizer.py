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
        logger.info(f"Summary parts: {sources_text}")
        
        synthesis_prompt = self._build_synthesis_prompt(current_query, sources_text)

        try:
            synthesis_result = self.llm_service.generate(
                input_data=f"Question: {current_query}\nSources: {sources_text}",
                system_prompt=synthesis_prompt,
                temperature=0.0,
            )

            result = synthesis_result.strip()
            logger.info(f"Synthesis result: {result}")
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
        # Limit to top 20 sources (increased from 10 for more comprehensive answers)
        max_sources = 20
        sources_to_process = processed_sources[:max_sources]
        
        logger.info(f"Preparing {len(sources_to_process)} sources for synthesis")
        if len(processed_sources) > max_sources:
            logger.info(f"Limiting synthesis to top {max_sources} sources (out of {len(processed_sources)} total)")
        
        for i, source in enumerate(sources_to_process, 1):
            logger.info(f"Adding source {i}: {source['title']}")
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

        return f"""You are an expert research assistant providing a comprehensive, well-written answer to a user's question.

CRITICAL: Today's date is {today} ({current_month} {current_year}).

USER'S QUESTION: {current_query}

SOURCES AVAILABLE:
{sources_text}

YOUR TASK:
Write a comprehensive, flowing, and professional answer that DIRECTLY addresses the user's question. Your answer should read naturally, like an expert explaining the topic to someone seeking clear information.

WRITING STYLE REQUIREMENTS:
1. **Start by DIRECTLY answering the user's question** - don't begin with "According to sources..." or "Based on research..."
2. **Write in a smooth, natural, conversational style** - as if you're an expert sharing knowledge
3. **Organize information logically** - use clear sections/paragraphs if the topic has multiple aspects
4. **Build a narrative flow** - connect ideas smoothly, don't just list facts
5. **Be comprehensive yet accessible** - include all important details but explain them clearly
6. **Directly address what the user asked** - keep their original question as the focus throughout

CONTENT REQUIREMENTS:
1. **USE ALL PROVIDED SOURCES** - synthesize information from every source provided
2. **Include specific details**: facts, numbers, dates, names, procedures, requirements, etc.
3. **Provide context and explanation** - don't just state facts, help the user understand them
4. **Cover multiple perspectives** - if sources offer different viewpoints, present them all fairly
5. **Be accurate and precise** - ensure all information is correctly represented
6. **Highlight key takeaways** - make sure the most important information stands out

CITATION FORMAT (CRITICAL):
- **EVERY factual claim MUST include a citation as an inline markdown link**
- Format: "Information from the source [Source Title](URL) shows that..."
- Place citations naturally within the text immediately after the information
- **DO NOT** use footnotes, reference numbers, or separate bibliography
- **DO NOT** use plain URLs - always use markdown link format: [text](URL)
- Every source in the list above should be cited at least once if it contains relevant information

RESPONSE STRUCTURE:
1. **Opening**: Directly answer the core question in the first 1-2 sentences
2. **Body**: Provide comprehensive details organized logically (use sections if helpful)
3. **Closing**: Summarize key points or provide actionable next steps if relevant

EXAMPLE OF GOOD WRITING STYLE:
❌ BAD: "According to Source 1 (URL), visa requirements exist. Source 2 (URL) says processing time is 30 days."
✅ GOOD: "To visit Japan, travelers need a valid passport and may require a visa depending on their nationality [Japan Immigration Guidelines](URL). The typical processing time is 30 days, though expedited options are available for urgent travel [Embassy Processing Times](URL)."

Remember: Your answer should feel like it's coming from a knowledgeable expert, not a list of source summaries. Write naturally, comprehensively, and keep the user's original question as your North Star.

USER'S QUESTION TO ANSWER: {current_query}"""

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
