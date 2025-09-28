"""
ResearchAgent - Simple research agent implementation.

KISS & YAGNI: Keep only essential functionality.
"""

from typing import Any, Dict, List, Optional

from ..base_agent.core import BaseAgent
from ..llm_service.core import get_shared_llm_service
from .analysis import AnalysisEngine
from .research import ResearchWorkflows
from .utils import ResearchHelpers


class ResearchAgent(BaseAgent):
    """
    Simple research agent - KISS & YAGNI implementation.
    """

    def __init__(self, model: Optional[str] = None):
        """Initialize with minimal required parameters."""
        super().__init__()
        self.llm_service = get_shared_llm_service(model=model)
        self.research_history: List[Dict[str, Any]] = []

        # Initialize modules
        self.analysis_engine = AnalysisEngine(self.llm_service)
        self.research_workflows = ResearchWorkflows(
            self.llm_service, self.analysis_engine
        )
        self.helpers = ResearchHelpers()

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Required abstract method implementation."""
        query = request.get("query", "")
        mode = request.get("mode", "instant")

        if not self.helpers.validate_mode(mode):
            from ..utils.utils import format_response

            return format_response(
                success=False,
                data={"error": f"Unknown mode: {mode}"},
                message="Invalid research mode",
            )

        if mode == "instant":
            return self.instant_research(query)
        elif mode == "quick":
            return self.quick_research(query)
        elif mode == "standard":
            return self.standard_research(query)
        elif mode == "deep":
            return self.deep_research(query)

    def instant_research(self, query: str) -> Dict[str, Any]:
        """Conduct instant research - single round quick answer."""
        result = self.research_workflows.instant_research(query)
        self._add_to_research_history("instant", query, result)
        return result

    def quick_research(self, query: str) -> Dict[str, Any]:
        """Conduct quick research - 2 rounds with gap analysis."""
        result = self.research_workflows.quick_research(query)
        self._add_to_research_history("quick", query, result)
        return result

    def standard_research(self, query: str) -> Dict[str, Any]:
        """Conduct standard research - 3 rounds with comprehensive analysis."""
        result = self.research_workflows.standard_research(query)
        self._add_to_research_history("standard", query, result)
        return result

    def deep_research(self, query: str) -> Dict[str, Any]:
        """Conduct deep research - 4 rounds with exhaustive analysis."""
        result = self.research_workflows.deep_research(query)
        self._add_to_research_history("deep", query, result)
        return result

    def get_research_history(self) -> List[Dict[str, Any]]:
        """Get research history."""
        return self.research_history.copy()

    def get_available_modes(self) -> List[str]:
        """Get available research modes."""
        return self.helpers.get_available_modes()

    def get_mode_description(self, mode: str) -> str:
        """Get description for a research mode."""
        return self.helpers.get_mode_description(mode)

    def _add_to_research_history(
        self, mode: str, query: str, result: Dict[str, Any]
    ) -> None:
        """Add entry to research history."""
        entry = self.helpers.format_research_history_entry(mode, query, result)
        self.research_history.append(entry)
