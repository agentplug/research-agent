"""
Source Tracker for Research Agent

KISS & YAGNI: Keep only essential functionality.
Currently unused in research workflows - minimal implementation.
"""

from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


class SourceTracker:
    """
    Simple source tracker - KISS & YAGNI implementation.

    Only tracks basic source information when needed.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize source tracker with minimal configuration."""
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)

        # Simple storage
        self.sources: List[Dict[str, Any]] = []
        self.session_sources: List[str] = []

    def add_source(
        self,
        url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        round_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Add a source to the tracker.

        Args:
            url: Source URL
            title: Optional title
            description: Optional description
            round_number: Optional round number

        Returns:
            Success response
        """
        if not self.enabled:
            return {"success": True, "message": "Source tracking disabled"}

        if not url or not self._is_valid_url(url):
            return {"success": False, "message": "Invalid URL"}

        # Simple deduplication by URL
        if url in self.session_sources:
            return {"success": True, "message": "Source already tracked"}

        source_info = {
            "url": url,
            "title": title or "",
            "description": description or "",
            "round_number": round_number,
            "domain": self._extract_domain(url),
        }

        self.sources.append(source_info)
        self.session_sources.append(url)

        return {"success": True, "message": "Source added successfully"}

    def get_all_sources(self) -> Dict[str, Any]:
        """Get all tracked sources."""
        return {
            "success": True,
            "data": {
                "sources": self.sources,
                "total_count": len(self.sources),
            },
            "message": f"Retrieved {len(self.sources)} sources",
        }

    def get_sources_for_round(self, round_number: int) -> Dict[str, Any]:
        """Get sources for a specific round."""
        round_sources = [
            source
            for source in self.sources
            if source.get("round_number") == round_number
        ]

        return {
            "success": True,
            "data": {
                "sources": round_sources,
                "round_number": round_number,
                "count": len(round_sources),
            },
            "message": f"Retrieved {len(round_sources)} sources for round {round_number}",
        }

    def clear_session(self) -> Dict[str, Any]:
        """Clear all sources for current session."""
        count = len(self.sources)
        self.sources.clear()
        self.session_sources.clear()

        return {
            "success": True,
            "data": {"cleared_count": count},
            "message": f"Cleared {count} sources from session",
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get basic statistics."""
        domains = {}
        for source in self.sources:
            domain = source.get("domain", "unknown")
            domains[domain] = domains.get(domain, 0) + 1

        return {
            "success": True,
            "data": {
                "total_sources": len(self.sources),
                "unique_domains": len(domains),
                "domain_distribution": domains,
            },
            "message": "Statistics retrieved successfully",
        }

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            return urlparse(url).netloc
        except Exception:
            return "unknown"
