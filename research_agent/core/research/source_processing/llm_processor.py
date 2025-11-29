"""
LLM processor for analyzing source content with language models.

This module handles the LLM-based analysis of source content to determine
relevance and extract meaningful information.
"""

import logging
from datetime import date
from typing import Any, Dict, Optional

from ....utils.utils import get_current_timestamp

logger = logging.getLogger(__name__)


class LLMProcessor:
    """Processes source content using LLM for relevance analysis."""

    def __init__(self, llm_service):
        """
        Initialize LLM processor.

        Args:
            llm_service: LLM service instance for content processing
        """
        self.llm_service = llm_service

    def process_source_with_llm(
        self,
        tool_name: str,
        content: str,
        title: str,
        url: str,
        original_query: str,
        follow_up_query: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Process content with LLM using generalized approach.

        Args:
            tool_name: Name of the tool
            content: Content to process
            title: Title of the source
            url: URL of the source
            original_query: Original research query
            follow_up_query: Current follow-up query

        Returns:
            Processed source summary or None
        """
        current_query = follow_up_query if follow_up_query else original_query
        system_prompt = self._build_analysis_prompt(
            tool_name, title, url, content, current_query
        )

        try:
            # Process this individual source
            logger.info(f"Analyzing source: {title}")
            
            source_analysis = self.llm_service.generate(
                input_data=f"Source: {title}\nContent: {content}\nQuestion: {current_query}",
                system_prompt=system_prompt,
                temperature=0.0,
            )
            
            # Check if source is relevant
            if "NOT_RELEVANT" in source_analysis.upper():
                logger.info(f"Analysis result: Source not relevant - {title}")
                logger.info(f"❌ Filtered source: {title}")
                logger.info(f"LLM reasoning: {source_analysis}")
                return None
            else:
                logger.info(f"Analysis result: Source relevant - {title}")
                logger.info(f"✅ Processed source: {title}")

            # Ensure summary is concise (max 600 characters for better context)
            summary = source_analysis.strip()
            if len(summary) > 600:
                summary = summary[:600] + "..."
            
            return {
                "source_type": tool_name,
                "title": title,
                "url": url,
                "original_content": content,
                "processed_summary": summary,
                "relevance_score": self._calculate_relevance_score(
                    summary, current_query
                ),
                "timestamp": get_current_timestamp(),
            }

        except Exception as e:
            # Log error but continue processing other sources
            return None

    def _build_analysis_prompt(
        self,
        tool_name: str,
        title: str,
        url: str,
        content: str,
        current_query: str,
    ) -> str:
        """
        Build the system prompt for LLM analysis.

        Args:
            tool_name: Name of the tool
            title: Title of the source
            url: URL of the source
            content: Content to analyze
            current_query: Current research query

        Returns:
            Formatted system prompt
        """
        today = date.today()
        current_year = today.year
        current_month = today.strftime("%B")

        return f"""You are a research assistant analyzing a single source for relevance to a research question.

CRITICAL: Today's date is {today} ({current_month} {current_year}).

TASK: Extract information from the provided source that relates to the research question.

SOURCE INFORMATION:
Tool: {tool_name}
Title: {title}
URL: {url}
Content: {content}

RESEARCH QUESTION: {current_query}

INSTRUCTIONS:
1. **BE EXTREMELY LENIENT** - Include ANY source that has even a tangential connection to the topic
2. **ONLY respond with "NOT_RELEVANT" if source is about a completely different topic** (e.g., cooking recipes when asking about physics)
3. **For ALL other sources, provide a summary (2-4 sentences, 300-500 characters)** of relevant information
4. **Include context and details** - don't be overly brief, provide enough information to be useful
5. **Include background information, related concepts, and supporting details**
6. **When in doubt, INCLUDE the source** - it's better to have extra information than miss something important

RESPONSE FORMAT:
- If relevant (99% of cases): Provide a clear summary (2-4 sentences, 300-500 characters) of the key information
- If completely unrelated (1% of cases): Respond with "NOT_RELEVANT"

CRITICAL: Default to INCLUDING sources. Only filter out sources that are truly about a completely different subject matter.

Focus on: {current_query}"""

    def _calculate_relevance_score(self, summary: str, query: str) -> float:
        """
        Calculate relevance score based on summary content.

        Args:
            summary: Processed summary
            query: Research query

        Returns:
            Relevance score between 0.0 and 1.0
        """
        if not summary or "NOT_RELEVANT" in summary.upper():
            return 0.0

        # Improved relevance scoring with more generous baseline
        query_words = set(query.lower().split())
        summary_words = set(summary.lower().split())

        # Calculate overlap
        overlap = len(query_words.intersection(summary_words))
        total_query_words = len(query_words)

        if total_query_words == 0:
            return 0.7  # Higher default score if no query words

        # More generous scoring: even 1 keyword match gives 0.5+ score
        base_score = overlap / total_query_words
        # Boost the score to be more lenient
        boosted_score = min(base_score * 1.5, 1.0)
        
        # Higher minimum relevance score - if source made it through LLM filter, it's relevant
        return max(boosted_score, 0.6)  # Minimum relevance score increased from 0.1 to 0.6
