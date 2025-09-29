"""
Content extractor for extracting fields from tool results using strategy-defined mappings.

This module handles the extraction of content, title, URL, and other fields
from tool results based on the processing strategy.
"""

from typing import Any, Dict


class ContentExtractor:
    """Extracts content fields from tool results using strategy-defined mappings."""

    @staticmethod
    def extract_content(data: Dict[str, Any], strategy: Dict[str, Any]) -> str:
        """
        Extract content from data using strategy-defined field.

        Args:
            data: Source data to extract from
            strategy: Processing strategy dictionary

        Returns:
            Extracted content string
        """
        content_field = strategy["content_field"]
        snippet_field = strategy["snippet_field"]

        content = data.get(content_field, "")
        snippet = data.get(snippet_field, "")

        # Use snippet if content is empty
        if not content or content == "No content":
            content = snippet

        return content

    @staticmethod
    def extract_title(data: Dict[str, Any], strategy: Dict[str, Any]) -> str:
        """
        Extract title from data using strategy-defined field.

        Args:
            data: Source data to extract from
            strategy: Processing strategy dictionary

        Returns:
            Extracted title string
        """
        title_field = strategy["title_field"]
        return data.get(title_field, f"{strategy.get('type', 'unknown')} result")

    @staticmethod
    def extract_url(data: Dict[str, Any], strategy: Dict[str, Any]) -> str:
        """
        Extract URL from data using strategy-defined field.

        Args:
            data: Source data to extract from
            strategy: Processing strategy dictionary

        Returns:
            Extracted URL string
        """
        url_field = strategy["url_field"]
        return data.get(url_field, "No URL")

    @staticmethod
    def extract_all_fields(
        data: Dict[str, Any], strategy: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Extract all relevant fields from data using strategy.

        Args:
            data: Source data to extract from
            strategy: Processing strategy dictionary

        Returns:
            Dictionary containing extracted fields
        """
        return {
            "content": ContentExtractor.extract_content(data, strategy),
            "title": ContentExtractor.extract_title(data, strategy),
            "url": ContentExtractor.extract_url(data, strategy),
        }

    @staticmethod
    def has_meaningful_content(content: str, min_length: int = 5) -> bool:
        """
        Check if content has meaningful length.

        Args:
            content: Content to check
            min_length: Minimum required length

        Returns:
            True if content is meaningful, False otherwise
        """
        return content and len(content.strip()) >= min_length
