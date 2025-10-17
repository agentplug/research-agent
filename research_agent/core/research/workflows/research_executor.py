"""
Research executor for handling the core research workflow logic.

This module handles the execution of research rounds, including first round
and follow-up rounds with tool integration.
"""

import logging
from typing import Any, Dict, List, Optional

from ....utils.utils import get_current_timestamp
from ...tools.tool_executor import ToolExecutor
from .prompt_builder import PromptBuilder
from .research_modes import ResearchModes
from .tool_analyzer import ToolAwareAnalyzer

# Set up logger
logger = logging.getLogger(__name__)


class ResearchExecutor:
    """Executes research workflows with tool integration."""

    def __init__(
        self,
        llm_service,
        analysis_engine,
        clarification_engine,
        intention_generator,
        available_tools: List[str] = None,
        tool_descriptions: Dict[str, str] = None,
    ):
        """
        Initialize research executor.

        Args:
            llm_service: LLM service instance
            analysis_engine: Analysis engine instance
            clarification_engine: Clarification engine instance
            intention_generator: Intention generator instance
            available_tools: List of available tool names
            tool_descriptions: Dictionary of tool descriptions
        """
        self.llm_service = llm_service
        self.analysis_engine = analysis_engine
        self.clarification_engine = clarification_engine
        self.intention_generator = intention_generator
        self.available_tools = available_tools or []
        self.tool_descriptions = tool_descriptions or {}
        self.logger = logger

        # Initialize components
        self.tool_executor = (
            ToolExecutor(available_tools, tool_descriptions)
            if available_tools
            else None
        )
        self.prompt_builder = PromptBuilder(available_tools, tool_descriptions)
        self.research_modes = ResearchModes()

        # Initialize tool analyzer with source processor
        from ....source_tracker.source_tracker import SourceTracker
        from ..source_processing import SourceProcessor

        source_processor = SourceProcessor(llm_service)
        self.tool_analyzer = ToolAwareAnalyzer(llm_service, source_processor)

        # Initialize source tracker for URL deduplication
        self.source_tracker = SourceTracker()
        
        # Store user intention and interpretation for use across all rounds
        self.user_intention = ""
        self.clarification_interpretation = ""

    def execute_first_round(
        self,
        query: str,
        mode: str,
        user_intention: str = "",
    ) -> Dict[str, Any]:
        """
        Execute the first round of research.

        Args:
            query: Research query
            mode: Research mode
            user_intention: User intention paragraph (for deep research)

        Returns:
            First round result
        """
        # Build enhanced query with current year for "current" queries
        enhanced_query = self._enhance_query_with_context(query)

        # Build system prompt with exclude URLs
        exclude_urls = self.source_tracker.get_exclude_urls("urls")
        system_prompt = self.prompt_builder.build_tool_aware_system_prompt(
            mode, enhanced_query, exclude_urls
        )

        # Store and add user intention if provided
        if user_intention:
            self.user_intention = user_intention
            system_prompt += f"\n\nUSER INTENTION: {user_intention}"
            
            # Add interpretation as additional context if available
            if self.clarification_interpretation:
                system_prompt += f"\n\nCLARIFICATION INTERPRETATION: {self.clarification_interpretation}"

        # Build input with context
        input_with_context = f"""
Research Query: {enhanced_query}
Mode: {mode}
Available Tools: {', '.join(self.available_tools)}

Please conduct research using the available tools and provide a comprehensive answer.
"""

        try:
            # Generate response with tool calls
            response = self.llm_service.generate(
                input_data=input_with_context,
                system_prompt=system_prompt,
                temperature=0.0,
                return_json=True,
            )

            # Execute tool calls if present
            tool_results = self._extract_and_execute_tools(response)

            # Enhance content with tool results
            if tool_results:
                enhanced_content = self.tool_analyzer.enhance_content_with_tools(
                    tool_results, query
                )
            else:
                enhanced_content = response

            result = {
                "round_number": 1,
                "query": query,
                "content": enhanced_content,
                "timestamp": get_current_timestamp(),
            }
            
            # Log round completion separator
            logger.info("=" * 100)
            logger.info(f"✅ Round 1 completed")
            logger.info("=" * 100)
            
            return result

        except Exception as e:
            return {
                "round_number": 1,
                "query": query,
                "content": f"Error in first round: {str(e)}",
                "timestamp": get_current_timestamp(),
            }

    def execute_followup_round(
        self,
        original_query: str,
        previous_results: List[Dict[str, Any]],
        mode: str,
    ) -> Dict[str, Any]:
        """
        Execute a follow-up round of research.

        Args:
            original_query: Original research query
            previous_results: Results from previous rounds
            mode: Research mode

        Returns:
            Follow-up round result
        """
        # Calculate round number
        round_num = len(previous_results) + 1

        # Build analysis prompt
        analysis_prompt = self.prompt_builder.build_tool_aware_analysis_prompt(mode)
        
        # Add user intention and interpretation to analysis prompt if available
        if self.user_intention:
            analysis_prompt += f"\n\nUSER INTENTION: {self.user_intention}"
            
            if self.clarification_interpretation:
                analysis_prompt += f"\n\nCLARIFICATION INTERPRETATION: {self.clarification_interpretation}"

        # Build research summary
        research_summary = self.prompt_builder.build_research_summary(previous_results)

        # Analyze gaps and generate follow-up query
        analysis_input = f"""
Original Query: {original_query}
Previous Research Results:
{research_summary}

Analyze the research progress and identify gaps. Generate a follow-up query to address missing information.
"""

        try:
            # Generate follow-up query
            follow_up_response = self.llm_service.generate(
                input_data=analysis_input,
                system_prompt=analysis_prompt,
                temperature=0.0,
                return_json=True,
            )
            
            # Parse the JSON response to extract the follow-up query
            import json
            try:
                follow_up_data = json.loads(follow_up_response)
                follow_up_query = follow_up_data.get("follow_up_query", follow_up_response)
            except json.JSONDecodeError:
                # If JSON parsing fails, use the raw response
                follow_up_query = follow_up_response

            # Build system prompt for follow-up research with exclude URLs
            exclude_urls = self.source_tracker.get_exclude_urls("urls")
            system_prompt = self.prompt_builder.build_tool_aware_system_prompt(
                mode, follow_up_query, exclude_urls
            )

            # Add user intention to follow-up rounds if available
            if self.user_intention:
                system_prompt += f"\n\nUSER INTENTION: {self.user_intention}"
                
                # Add interpretation as additional context if available
                if self.clarification_interpretation:
                    system_prompt += f"\n\nCLARIFICATION INTERPRETATION: {self.clarification_interpretation}"

            # Build input with context
            input_with_context = f"""
Follow-up Query: {follow_up_query}
Original Query: {original_query}
Previous Results: {research_summary}
Mode: {mode}
Available Tools: {', '.join(self.available_tools)}

Please conduct follow-up research using the available tools to address the identified gaps.
"""

            # Generate response with tool calls
            response = self.llm_service.generate(
                input_data=input_with_context,
                system_prompt=system_prompt,
                temperature=0.0,
                return_json=True,
            )

            # Execute tool calls if present
            tool_results = self._extract_and_execute_tools(response)

            # Enhance content with tool results
            if tool_results:
                enhanced_content = self.tool_analyzer.enhance_content_with_tools(
                    tool_results, original_query, follow_up_query
                )
            else:
                enhanced_content = response

            result = {
                "round_number": round_num,
                "query": follow_up_query,
                "content": enhanced_content,
                "timestamp": get_current_timestamp(),
            }
            
            # Log round completion separator
            logger.info("=" * 100)
            logger.info(f"✅ Round {round_num} completed")
            logger.info("=" * 100)
            
            return result

        except Exception as e:
            return {
                "round_number": round_num,
                "query": f"Error generating follow-up query: {str(e)}",
                "content": f"Error in follow-up round: {str(e)}",
                "timestamp": get_current_timestamp(),
            }

    def _enhance_query_with_context(self, query: str) -> str:
        """
        Enhance query with temporal context for "current" queries.

        Args:
            query: Original query

        Returns:
            Enhanced query with context
        """
        from datetime import date

        today = date.today()
        current_year = today.year

        # Add current year context for "current" queries
        if "current" in query.lower():
            enhanced_query = f"{query} (as of {current_year})"
        else:
            enhanced_query = query

        return enhanced_query

    def _extract_and_execute_tools(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract and execute tool calls from LLM response.

        Args:
            response: LLM response containing potential tool calls

        Returns:
            List of tool execution results
        """
        if not self.tool_executor:
            self.logger.warning("No tool executor available")
            return []

        try:
            # Extract tool calls from response
            tool_calls = self.tool_executor.extract_tool_calls(response)
            self.logger.info(f"Extracted {len(tool_calls)} tool calls from response")

            if not tool_calls:
                self.logger.info("No tool calls found in response")
                return []

            # Execute tool calls
            tool_results = []
            for i, tool_call in enumerate(tool_calls):
                self.logger.info(f"Executing tool call {i+1}: {tool_call}")
                result = self.tool_executor.execute_tool(tool_call)
                self.logger.info(f"Tool execution result {i+1}: success={result.get('success', False)}")
                tool_results.append(result)

            # Track URLs from tool results for future exclusion
            self._extract_and_track_urls(tool_results)

            return tool_results

        except Exception as e:
            # Log error but continue
            self.logger.error(f"Error in _extract_and_execute_tools: {str(e)}")
            return []

    def _extract_and_track_urls(self, tool_results: List[Dict[str, Any]]) -> None:
        """
        Extract URLs from tool results and track them for future exclusion.

        Args:
            tool_results: List of tool execution results
        """
        urls_to_track = []

        for result in tool_results:
            if not result.get("success", False):
                continue

            tool_result = result.get("result", {})

            # Extract URLs from different tool result formats
            if isinstance(tool_result, dict):
                # Web search results format
                if "results" in tool_result and isinstance(
                    tool_result["results"], list
                ):
                    for item in tool_result["results"]:
                        if isinstance(item, dict) and "url" in item:
                            urls_to_track.append(item["url"])

                # Single result format
                elif "url" in tool_result:
                    urls_to_track.append(tool_result["url"])

        # Track URLs for future exclusion
        if urls_to_track:
            self.source_tracker.add_processed_urls(urls_to_track)

    def get_execution_statistics(self) -> Dict[str, Any]:
        """
        Get execution statistics.

        Returns:
            Dictionary containing execution statistics
        """
        stats = {
            "available_tools": self.available_tools,
            "tool_descriptions_count": len(self.tool_descriptions),
            "research_modes": self.research_modes.get_available_modes(),
        }

        if self.tool_executor:
            stats["tool_executor_stats"] = self.tool_executor.get_execution_stats()

        return stats
