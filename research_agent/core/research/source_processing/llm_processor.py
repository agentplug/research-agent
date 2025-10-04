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
            logger.info(f"Analyzing source: {title[:100]}...")
            
            source_analysis = self.llm_service.generate(
                input_data=f"Source: {title}\nContent: {content}\nQuestion: {current_query}",
                system_prompt=system_prompt,
                temperature=0.0,
            )
            
            # Check if source is relevant
            if "NOT_RELEVANT" in source_analysis.upper():
                logger.info(f"Analysis result: Source not relevant - {title[:50]}...")
                return None
            else:
                logger.info(f"Analysis result: Source relevant - {title[:50]}...")

            return {
                "source_type": tool_name,
                "title": title,
                "url": url,
                "original_content": content,
                "processed_summary": source_analysis.strip(),
                "relevance_score": self._calculate_relevance_score(
                    source_analysis, current_query
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

TASK: Analyze the provided source content and extract ONLY information that is directly relevant to the research question. If the source is not relevant, respond with "NOT_RELEVANT".

SOURCE INFORMATION:
Tool: {tool_name}
Title: {title}
URL: {url}
Content: {content}

RESEARCH QUESTION: {current_query}

INSTRUCTIONS:
1. **Extract any information that could be relevant to the research question**
2. **Only respond with "NOT_RELEVANT" if the source has absolutely no connection to the question**
3. **If relevant, provide a concise summary (2-3 sentences) of the key information**
4. **Include specific facts, data, or insights that could help answer the research question**
5. **Maintain accuracy and cite the source**

RESPONSE FORMAT:
If relevant: Provide a concise summary of the relevant information from this source.
If not relevant: Respond with "NOT_RELEVANT"

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

        # Simple relevance scoring based on keyword matching
        query_words = set(query.lower().split())
        summary_words = set(summary.lower().split())

        # Calculate overlap
        overlap = len(query_words.intersection(summary_words))
        total_query_words = len(query_words)

        if total_query_words == 0:
            return 0.5  # Default score if no query words

        relevance_score = min(overlap / total_query_words, 1.0)
        return max(relevance_score, 0.1)  # Minimum relevance score
