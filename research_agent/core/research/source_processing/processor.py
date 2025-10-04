"""
Main source processor orchestrating the modular processing pipeline.

This module coordinates the different processing components to handle
tool results in a generalized, extensible way.
"""

import logging
from typing import Any, Dict, List, Optional

from .content_extractor import ContentExtractor
from .llm_processor import LLMProcessor
from .parallel_executor import ParallelExecutor
from .strategy_detector import StrategyDetector
from .synthesizer import SourceSynthesizer

logger = logging.getLogger(__name__)


class SourceProcessor:
    """Processes individual sources to extract relevant information using modular components."""

    def __init__(self, llm_service, max_workers: int = 5):
        """
        Initialize source processor with modular components.

        Args:
            llm_service: LLM service instance for content processing
            max_workers: Maximum number of parallel workers
        """
        self.llm_service = llm_service

        # Initialize modular components
        self.strategy_detector = StrategyDetector()
        self.content_extractor = ContentExtractor()
        self.llm_processor = LLMProcessor(llm_service)
        self.synthesizer = SourceSynthesizer(llm_service)
        self.parallel_executor = ParallelExecutor(max_workers)

    def process_sources(
        self,
        tool_results: List[Dict[str, Any]],
        original_query: str,
        follow_up_query: str = "",
        max_workers: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Process sources in parallel for improved performance.
        Uses generalized tool processing that can handle any tool type.

        Args:
            tool_results: Results from tool executions
            original_query: Original research query
            follow_up_query: Current follow-up query (if any)
            max_workers: Maximum number of parallel workers (overrides default)

        Returns:
            List of processed source summaries
        """
        # Use provided max_workers or default
        if max_workers is not None:
            self.parallel_executor.max_workers = max_workers

        # Collect all individual sources to process
        sources_to_process = self._prepare_sources_for_processing(
            tool_results, original_query, follow_up_query
        )

        # Process sources in parallel
        logger.info(f"Starting parallel processing of {len(sources_to_process)} sources with {self.parallel_executor.max_workers} workers")
        return self.parallel_executor.execute_parallel(
            tasks=sources_to_process,
            processor_func=self._process_single_source,
            task_name="source",
        )

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
        return self.synthesizer.synthesize_sources(
            processed_sources, original_query, follow_up_query
        )

    def _prepare_sources_for_processing(
        self,
        tool_results: List[Dict[str, Any]],
        original_query: str,
        follow_up_query: str,
    ) -> List[Dict[str, Any]]:
        """
        Prepare sources for processing by determining strategies and collecting individual sources.

        Args:
            tool_results: Results from tool executions
            original_query: Original research query
            follow_up_query: Current follow-up query

        Returns:
            List of sources ready for processing
        """
        sources_to_process = []

        for result in tool_results:
            if not result.get("success", False):
                continue

            tool_name = result.get("tool_name", "unknown")
            tool_result = result.get("result", {})

            # Determine processing strategy
            processing_strategy = self.strategy_detector.determine_processing_strategy(
                tool_name, tool_result
            )

            if self.strategy_detector.is_multi_result_strategy(processing_strategy):
                # Tools that return multiple results (like web_search)
                for individual_result in processing_strategy["results"]:
                    sources_to_process.append(
                        {
                            "tool_name": tool_name,
                            "data": individual_result,
                            "original_query": original_query,
                            "follow_up_query": follow_up_query,
                            "processing_strategy": processing_strategy,
                        }
                    )
            else:
                # Tools that return single results (like calculate, document_retrieval)
                sources_to_process.append(
                    {
                        "tool_name": tool_name,
                        "data": tool_result,
                        "original_query": original_query,
                        "follow_up_query": follow_up_query,
                        "processing_strategy": processing_strategy,
                    }
                )

        return sources_to_process

    def _process_single_source(
        self, source_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Process a single source using modular components.

        Args:
            source_data: Dictionary containing tool name, data, queries, and processing strategy

        Returns:
            Processed source summary or None
        """
        tool_name = source_data["tool_name"]
        data = source_data["data"]
        original_query = source_data["original_query"]
        follow_up_query = source_data["follow_up_query"]
        strategy = source_data["processing_strategy"]

        # Extract content using strategy-defined fields
        extracted_fields = self.content_extractor.extract_all_fields(data, strategy)

        # Skip if no meaningful content
        if not self.content_extractor.has_meaningful_content(
            extracted_fields["content"]
        ):
            return None

        # Process with LLM using generalized approach
        return self.llm_processor.process_source_with_llm(
            tool_name=tool_name,
            content=extracted_fields["content"],
            title=extracted_fields["title"],
            url=extracted_fields["url"],
            original_query=original_query,
            follow_up_query=follow_up_query,
        )

    def get_processing_statistics(
        self, tool_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get statistics about the tool results and processing.

        Args:
            tool_results: Results from tool executions

        Returns:
            Dictionary containing processing statistics
        """
        if not tool_results:
            return {"total_tools": 0, "successful_tools": 0, "tool_types": {}}

        tool_types = {}
        successful_tools = 0

        for result in tool_results:
            tool_name = result.get("tool_name", "unknown")
            tool_types[tool_name] = tool_types.get(tool_name, 0) + 1

            if result.get("success", False):
                successful_tools += 1

        return {
            "total_tools": len(tool_results),
            "successful_tools": successful_tools,
            "success_rate": successful_tools / len(tool_results)
            if tool_results
            else 0.0,
            "tool_types": tool_types,
            "max_workers": self.parallel_executor.max_workers,
        }
