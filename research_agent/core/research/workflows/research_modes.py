"""
Research modes for different types of research workflows.

This module defines the different research modes (instant, quick, standard, deep)
and their specific configurations and behaviors.
"""

from typing import Any, Dict, List


class ResearchModes:
    """Defines different research modes and their configurations."""

    MODES = {
        "instant": {
            "rounds": 1,
            "description": "Quick, single-round research for immediate answers",
            "analysis_depth": "basic",
            "follow_up_strategy": "minimal",
        },
        "quick": {
            "rounds": 2,
            "description": "Two-round research with verification",
            "analysis_depth": "moderate",
            "follow_up_strategy": "targeted",
        },
        "standard": {
            "rounds": 3,
            "description": "Three-round comprehensive research",
            "analysis_depth": "thorough",
            "follow_up_strategy": "comprehensive",
        },
        "deep": {
            "rounds": 4,
            "description": "Four-round exhaustive research with clarification",
            "analysis_depth": "exhaustive",
            "follow_up_strategy": "exhaustive",
        },
    }

    @classmethod
    def get_mode_config(cls, mode: str) -> Dict[str, Any]:
        """
        Get configuration for a specific research mode.

        Args:
            mode: Research mode name

        Returns:
            Mode configuration dictionary
        """
        return cls.MODES.get(mode, cls.MODES["standard"])

    @classmethod
    def get_rounds_for_mode(cls, mode: str) -> int:
        """
        Get number of rounds for a specific mode.

        Args:
            mode: Research mode name

        Returns:
            Number of rounds
        """
        return cls.get_mode_config(mode)["rounds"]

    @classmethod
    def is_valid_mode(cls, mode: str) -> bool:
        """
        Check if a mode is valid.

        Args:
            mode: Research mode name

        Returns:
            True if mode is valid, False otherwise
        """
        return mode in cls.MODES

    @classmethod
    def get_available_modes(cls) -> List[str]:
        """
        Get list of available research modes.

        Returns:
            List of available mode names
        """
        return list(cls.MODES.keys())

    @classmethod
    def get_mode_description(cls, mode: str) -> str:
        """
        Get description for a specific mode.

        Args:
            mode: Research mode name

        Returns:
            Mode description
        """
        return cls.get_mode_config(mode)["description"]

    @classmethod
    def get_analysis_depth(cls, mode: str) -> str:
        """
        Get analysis depth for a specific mode.

        Args:
            mode: Research mode name

        Returns:
            Analysis depth level
        """
        return cls.get_mode_config(mode)["analysis_depth"]

    @classmethod
    def get_follow_up_strategy(cls, mode: str) -> str:
        """
        Get follow-up strategy for a specific mode.

        Args:
            mode: Research mode name

        Returns:
            Follow-up strategy
        """
        return cls.get_mode_config(mode)["follow_up_strategy"]

    @classmethod
    def should_use_clarification(cls, mode: str) -> bool:
        """
        Check if a mode should use clarification.

        Args:
            mode: Research mode name

        Returns:
            True if clarification should be used
        """
        return mode == "deep"

    @classmethod
    def get_mode_statistics(cls) -> Dict[str, Any]:
        """
        Get statistics about research modes.

        Returns:
            Dictionary containing mode statistics
        """
        return {
            "total_modes": len(cls.MODES),
            "available_modes": cls.get_available_modes(),
            "mode_configurations": cls.MODES,
            "round_ranges": {
                "min_rounds": min(config["rounds"] for config in cls.MODES.values()),
                "max_rounds": max(config["rounds"] for config in cls.MODES.values()),
            },
        }
