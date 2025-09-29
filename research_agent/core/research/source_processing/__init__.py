"""
Source processing package for handling tool results in a modular way.

This package provides a generalized approach to processing tool results without
hardcoding specific tool names, making it extensible for any future tools.

Modules:
- processor: Main orchestrator for source processing
- strategy_detector: Determines processing strategy based on tool result structure
- content_extractor: Extracts fields from tool results using strategy mappings
- llm_processor: Handles LLM-based analysis of source content
- synthesizer: Combines multiple processed sources into comprehensive answers
- parallel_executor: Manages concurrent processing of multiple sources
"""

from .content_extractor import ContentExtractor
from .llm_processor import LLMProcessor
from .parallel_executor import ParallelExecutor
from .processor import SourceProcessor
from .strategy_detector import StrategyDetector
from .synthesizer import SourceSynthesizer

__all__ = [
    "SourceProcessor",
    "StrategyDetector",
    "ContentExtractor",
    "LLMProcessor",
    "SourceSynthesizer",
    "ParallelExecutor",
]
