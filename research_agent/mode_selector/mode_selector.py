"""
Intelligent Mode Selector for Research Agent

This module handles automatic mode selection based on query analysis,
complexity scoring, and context-aware decision making.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from ..base_agent.error_handler import ErrorHandler
from ..utils.utils import format_response

logger = logging.getLogger(__name__)


class ModeSelector:
    """
    Intelligent mode selector that analyzes queries and selects optimal research mode.

    Features:
    - Query complexity analysis
    - Context-aware mode selection
    - Explicit mode detection
    - Validation and recommendations
    - Integration with ResearchAgent.solve() method
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize mode selector.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.error_handler = ErrorHandler("ModeSelector")

        # Load configuration
        self.mode_config = self.config.get("mode_selection", {})
        self.enabled = self.mode_config.get("enabled", True)
        self.fallback_mode = self.mode_config.get("fallback_mode", "instant")
        self.validation_enabled = self.mode_config.get("validation_enabled", True)
        self.logging_enabled = self.mode_config.get("logging_enabled", True)

        # Complexity weights and thresholds
        self.complexity_weights = self.mode_config.get("complexity_weights", {})
        self.length_thresholds = self.mode_config.get("length_thresholds", {})

        # Mode definitions
        self.modes = ["instant", "quick", "standard", "deep"]

        # Query patterns for mode detection
        self.mode_patterns = {
            "instant": [
                r"\b(what is|who is|when is|where is|how much|how many)\b",
                r"\b(define|definition|meaning)\b",
                r"\b(quick|fast|simple|basic)\b",
                r"^\w+\?$",  # Single word questions
            ],
            "quick": [
                r"\b(explain|describe|tell me about)\b",
                r"\b(overview|summary|brief)\b",
                r"\b(compare|difference|vs|versus)\b",
                r"\b(pros and cons|advantages|disadvantages)\b",
            ],
            "standard": [
                r"\b(analyze|analysis|research|investigate)\b",
                r"\b(comprehensive|detailed|thorough)\b",
                r"\b(how does|how to|how can)\b",
                r"\b(step by step|process|procedure)\b",
            ],
            "deep": [
                r"\b(exhaustive|comprehensive|detailed analysis)\b",
                r"\b(academic|scholarly|research paper)\b",
                r"\b(complete|full|extensive)\b",
                r"\b(deep dive|in-depth|thorough investigation)\b",
            ],
        }

    def select_mode(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Select the optimal research mode for a query.

        Args:
            query: Research query
            context: Additional context information

        Returns:
            Mode selection result with recommendations
        """
        try:
            if not self.enabled:
                return self._create_result(
                    self.fallback_mode, "Mode selection disabled"
                )

            if not query or not isinstance(query, str):
                return self._create_result(self.fallback_mode, "Invalid query provided")

            # Analyze query complexity
            complexity_score = self._analyze_complexity(query)

            # Detect explicit mode requests
            explicit_mode = self._detect_explicit_mode(query)

            # Analyze query patterns
            pattern_mode = self._analyze_patterns(query)

            # Consider context if provided
            context_mode = self._analyze_context(context) if context else None

            # Make final decision
            selected_mode = self._make_decision(
                query, complexity_score, explicit_mode, pattern_mode, context_mode
            )

            # Validate selection
            if self.validation_enabled:
                validation_result = self._validate_mode(selected_mode, query)
                if not validation_result["valid"]:
                    selected_mode = validation_result["recommended_mode"]

            # Create result
            result = self._create_result(
                selected_mode,
                f"Selected {selected_mode} mode based on analysis",
                {
                    "complexity_score": complexity_score,
                    "explicit_mode": explicit_mode,
                    "pattern_mode": pattern_mode,
                    "context_mode": context_mode,
                    "query_length": len(query),
                    "analysis_details": {
                        "complexity_factors": self._get_complexity_factors(query),
                        "pattern_matches": self._get_pattern_matches(query),
                        "decision_factors": self._get_decision_factors(
                            complexity_score, explicit_mode, pattern_mode, context_mode
                        ),
                    },
                },
            )

            if self.logging_enabled:
                logger.info(
                    f"🎯 Mode selected: {selected_mode} for query: '{query}'"
                )

            return result

        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {"query": query, "context": context},
                f"Error in mode selection: {str(e)}",
            )

    def _analyze_complexity(self, query: str) -> int:
        """
        Analyze query complexity and return a score.

        Args:
            query: Research query

        Returns:
            Complexity score (0-100)
        """
        score = 0

        # Base score from query length
        query_length = len(query.split())
        if query_length <= 5:
            score += 10
        elif query_length <= 15:
            score += 20
        elif query_length <= 30:
            score += 40
        else:
            score += 60

        # Add complexity weights
        query_lower = query.lower()
        for keyword, weight in self.complexity_weights.items():
            if keyword in query_lower:
                score += weight * 10

        # Add points for question complexity
        question_count = query.count("?")
        score += question_count * 5

        # Add points for conjunction words (indicates complex queries)
        conjunctions = ["and", "or", "but", "however", "although", "while"]
        for conj in conjunctions:
            if conj in query_lower:
                score += 5

        # Add points for comparison words
        comparisons = ["compare", "versus", "vs", "difference", "similarity"]
        for comp in comparisons:
            if comp in query_lower:
                score += 10

        # Cap the score
        return min(score, 100)

    def _detect_explicit_mode(self, query: str) -> Optional[str]:
        """
        Detect explicit mode requests in the query.

        Args:
            query: Research query

        Returns:
            Explicitly requested mode or None
        """
        query_lower = query.lower()

        explicit_requests = {
            "instant": ["quick answer", "fast", "instant", "immediate"],
            "quick": ["quick research", "brief", "overview", "summary"],
            "standard": ["standard research", "normal", "regular"],
            "deep": ["deep research", "comprehensive", "thorough", "exhaustive"],
        }

        for mode, keywords in explicit_requests.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return mode

        return None

    def _analyze_patterns(self, query: str) -> Optional[str]:
        """
        Analyze query patterns to suggest mode.

        Args:
            query: Research query

        Returns:
            Suggested mode based on patterns
        """
        query_lower = query.lower()

        # Check patterns for each mode
        for mode, patterns in self.mode_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return mode

        return None

    def _analyze_context(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Analyze context to suggest mode.

        Args:
            context: Context information

        Returns:
            Suggested mode based on context
        """
        if not context:
            return None

        # Check for previous research mode
        previous_mode = context.get("previous_mode")
        if previous_mode:
            # Suggest deeper mode for follow-up questions
            if previous_mode == "instant":
                return "quick"
            elif previous_mode == "quick":
                return "standard"
            elif previous_mode == "standard":
                return "deep"

        # Check for research depth preference
        depth_preference = context.get("depth_preference")
        if depth_preference and isinstance(depth_preference, str):
            return str(depth_preference)

        # Check for time constraints
        time_constraint = context.get("time_constraint")
        if time_constraint == "urgent":
            return "instant"
        elif time_constraint == "limited":
            return "quick"

        return None

    def _make_decision(
        self,
        query: str,
        complexity_score: int,
        explicit_mode: Optional[str],
        pattern_mode: Optional[str],
        context_mode: Optional[str],
    ) -> str:
        """
        Make final mode decision based on all factors.

        Args:
            query: Research query
            complexity_score: Complexity score
            explicit_mode: Explicitly requested mode
            pattern_mode: Mode suggested by patterns
            context_mode: Mode suggested by context

        Returns:
            Selected mode
        """
        # Priority 1: Explicit mode request
        if explicit_mode:
            return explicit_mode

        # Priority 2: Context-based suggestion
        if context_mode:
            return context_mode

        # Priority 3: Pattern-based suggestion
        if pattern_mode:
            return pattern_mode

        # Priority 4: Complexity-based decision
        if complexity_score >= 70:
            return "deep"
        elif complexity_score >= 50:
            return "standard"
        elif complexity_score >= 25:
            return "quick"
        else:
            return "instant"

    def _validate_mode(self, mode: str, query: str) -> Dict[str, Any]:
        """
        Validate the selected mode against query characteristics.

        Args:
            mode: Selected mode
            query: Research query

        Returns:
            Validation result
        """
        query_length = len(query.split())

        # Check if mode is appropriate for query length
        thresholds = self.length_thresholds

        if mode == "instant" and query_length > thresholds.get("instant", 10):
            return {
                "valid": False,
                "recommended_mode": "quick",
                "reason": "Query too long for instant mode",
            }

        if mode == "quick" and query_length > thresholds.get("quick", 25):
            return {
                "valid": False,
                "recommended_mode": "standard",
                "reason": "Query too long for quick mode",
            }

        if mode == "standard" and query_length > thresholds.get("standard", 50):
            return {
                "valid": False,
                "recommended_mode": "deep",
                "reason": "Query too long for standard mode",
            }

        return {"valid": True, "recommended_mode": mode}

    def _create_result(
        self, mode: str, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a standardized result dictionary."""
        return format_response(
            success=True,
            data={
                "selected_mode": mode,
                "message": message,
                "metadata": metadata or {},
            },
            message=message,
        )

    def _get_complexity_factors(self, query: str) -> List[str]:
        """Get list of complexity factors found in query."""
        factors = []
        query_lower = query.lower()

        for keyword in self.complexity_weights.keys():
            if keyword in query_lower:
                factors.append(keyword)

        return factors

    def _get_pattern_matches(self, query: str) -> Dict[str, List[str]]:
        """Get pattern matches for each mode."""
        matches = {}
        query_lower = query.lower()

        for mode, patterns in self.mode_patterns.items():
            mode_matches = []
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    mode_matches.append(pattern)
            if mode_matches:
                matches[mode] = mode_matches

        return matches

    def _get_decision_factors(
        self,
        complexity_score: int,
        explicit_mode: Optional[str],
        pattern_mode: Optional[str],
        context_mode: Optional[str],
    ) -> List[str]:
        """Get list of factors that influenced the decision."""
        factors = []

        if explicit_mode:
            factors.append(f"explicit_request: {explicit_mode}")

        if context_mode:
            factors.append(f"context_suggestion: {context_mode}")

        if pattern_mode:
            factors.append(f"pattern_match: {pattern_mode}")

        factors.append(f"complexity_score: {complexity_score}")

        return factors

    def get_mode_recommendations(self, query: str) -> Dict[str, Any]:
        """
        Get recommendations for all modes for a query.

        Args:
            query: Research query

        Returns:
            Recommendations for all modes
        """
        try:
            recommendations = {}

            for mode in self.modes:
                # Simulate mode selection for each mode
                complexity_score = self._analyze_complexity(query)
                pattern_mode = self._analyze_patterns(query)

                # Calculate suitability score
                suitability = self._calculate_mode_suitability(
                    mode, complexity_score, pattern_mode
                )

                recommendations[mode] = {
                    "suitability_score": suitability,
                    "recommended": suitability >= 70,
                    "reason": self._get_mode_reason(
                        mode, complexity_score, pattern_mode
                    ),
                }

            return format_response(
                success=True,
                data={"recommendations": recommendations},
                message="Mode recommendations generated",
            )

        except Exception as e:
            return self.error_handler.handle_error(
                e, {"query": query}, f"Error generating mode recommendations: {str(e)}"
            )

    def _calculate_mode_suitability(
        self, mode: str, complexity_score: int, pattern_mode: Optional[str]
    ) -> int:
        """Calculate suitability score for a mode."""
        score = 0

        # Base score from complexity
        if mode == "instant" and complexity_score <= 25:
            score += 80
        elif mode == "quick" and 25 < complexity_score <= 50:
            score += 80
        elif mode == "standard" and 50 < complexity_score <= 75:
            score += 80
        elif mode == "deep" and complexity_score > 75:
            score += 80

        # Pattern match bonus
        if pattern_mode == mode:
            score += 20

        return min(score, 100)

    def _get_mode_reason(
        self, mode: str, complexity_score: int, pattern_mode: Optional[str]
    ) -> str:
        """Get reason for mode recommendation."""
        reasons = {
            "instant": f"Simple query (complexity: {complexity_score})",
            "quick": f"Moderate complexity (complexity: {complexity_score})",
            "standard": f"Complex query (complexity: {complexity_score})",
            "deep": f"Very complex query (complexity: {complexity_score})",
        }

        reason = reasons.get(mode, "Unknown mode")

        if pattern_mode == mode:
            reason += f" + pattern match"

        return reason
