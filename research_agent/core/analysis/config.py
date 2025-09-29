"""Mode-specific configurations for research analysis."""

from typing import Any, Dict


class ModeConfig:
    """Configuration for different research modes."""

    MODE_CONFIGS = {
        "quick": {
            "focus": "enhanced analysis",
            "depth": "moderate depth",
            "completeness_threshold": "good coverage of main aspects",
            "query_style": "targeted and specific",
        },
        "standard": {
            "focus": "comprehensive research",
            "depth": "thorough analysis",
            "completeness_threshold": "complete coverage of all aspects",
            "query_style": "precise and comprehensive",
        },
        "deep": {
            "focus": "exhaustive research",
            "depth": "academic-level analysis",
            "completeness_threshold": "exhaustive coverage with full context",
            "query_style": "detailed and exhaustive",
        },
    }

    SYSTEM_PROMPTS = {
        "instant": "You are a quick research evaluator. Focus on basic completeness and direct answers.",
        "quick": "You are a research analyst specializing in enhanced analysis with context and examples.",
        "standard": "You are a research analyst specializing in comprehensive gap analysis and multi-perspective evaluation.",
        "deep": "You are a research analyst specializing in exhaustive academic-level gap analysis and scholarly evaluation.",
    }

    FOLLOWUP_INSTRUCTIONS = {
        "instant": "Provide a quick, direct answer focusing on key facts.",
        "quick": "Provide enhanced analysis with context and examples.",
        "standard": "Conduct comprehensive research with multiple perspectives.",
        "deep": "Conduct exhaustive research with academic-level analysis.",
    }

    @classmethod
    def get_mode_config(cls, mode: str) -> Dict[str, Any]:
        """Get configuration for a specific mode."""
        return cls.MODE_CONFIGS.get(mode, cls.MODE_CONFIGS["standard"])

    @classmethod
    def get_system_prompt(cls, mode: str) -> str:
        """Get system prompt for a specific mode."""
        return cls.SYSTEM_PROMPTS.get(mode, cls.SYSTEM_PROMPTS["standard"])

    @classmethod
    def get_followup_instruction(cls, mode: str) -> str:
        """Get follow-up instruction for a specific mode."""
        return cls.FOLLOWUP_INSTRUCTIONS.get(
            mode, cls.FOLLOWUP_INSTRUCTIONS["standard"]
        )
