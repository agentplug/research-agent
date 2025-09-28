"""
Research Workflows - Multi-round LLM-powered research implementations.

This module provides comprehensive workflow implementations for each research mode
with proper multi-round research where each round builds on previous results.
"""

import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from ...base_agent.error_handler import ErrorHandler
from ...utils.utils import format_response, sanitize_string, get_current_timestamp


class ResearchMode(Enum):
    """Research modes."""
    INSTANT = "instant"
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class BaseWorkflow:
    """Base class for research workflows."""
    
    def __init__(self, mode: ResearchMode, llm_service=None):
        """
        Initialize workflow.
        
        Args:
            mode: Research mode
            llm_service: LLM service instance
        """
        self.mode = mode
        self.llm_service = llm_service
        self.error_handler = ErrorHandler(f"Workflow_{mode.value.title()}")
        self.rounds_config = {
            'instant': 1,
            'quick': 2,
            'standard': 3,
            'deep': 4
        }
    
    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the research workflow.
        
        Args:
            query: Research query
            context: Additional context
            
        Returns:
            Research results
        """
        raise NotImplementedError("Subclasses must implement execute method")
    
    def _generate_research_response(
        self, 
        query: str, 
        research_context: str, 
        temperature: float = 0.2,
        previous_results: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Generate research response using LLM.
        
        Args:
            query: Research query
            research_context: Context for the research
            temperature: Temperature setting
            previous_results: Results from previous rounds
            
        Returns:
            Generated response
        """
        if not self.llm_service:
            return f"Mock response for '{query}': {research_context}"
        
        # Build context from previous rounds
        context_text = ""
        if previous_results:
            context_text = "\n\nPrevious Research Results:\n"
            for i, result in enumerate(previous_results, 1):
                context_text += f"\nRound {i}:\n{result['content'][:500]}...\n"
        
        system_prompt = f"""You are an expert research assistant specializing in {self.mode.value} research mode.

{research_context}

Guidelines:
- Provide accurate, well-researched information
- Use clear, professional language
- Structure your response logically
- Include relevant details and context
- Be concise but comprehensive
- Focus on factual accuracy and clarity
- Build upon previous research when available
- Avoid repeating information from previous rounds{context_text}"""

        return self.llm_service.generate(
            input_data=query,
            system_prompt=system_prompt,
            temperature=temperature
        )
    
    def _analyze_gaps_and_generate_followup(
        self, 
        original_query: str, 
        current_results: List[Dict[str, Any]], 
        round_number: int
    ) -> str:
        """
        Analyze current research results and generate follow-up query.
        
        Args:
            original_query: Original research query
            current_results: Results from previous rounds
            round_number: Current round number
            
        Returns:
            Follow-up query for next round
        """
        if not self.llm_service:
            return f"Follow-up query for round {round_number + 1}"
        
        # Build summary of current results
        results_summary = ""
        for i, result in enumerate(current_results, 1):
            results_summary += f"\nRound {i}: {result['content'][:300]}...\n"
        
        gap_analysis_prompt = f"""You are a research analyst. Analyze the current research results and identify gaps or areas that need deeper exploration.

Original Query: {original_query}

Current Research Results:{results_summary}

Round {round_number + 1} Focus:
- Identify what information is missing or needs clarification
- Suggest specific aspects that need deeper analysis
- Consider different perspectives or angles not yet covered
- Think about practical applications, case studies, or examples
- Consider controversies, debates, or differing opinions
- Think about future implications or trends

Generate a specific, focused follow-up query that will help fill the identified gaps. The query should be actionable and specific, not vague.

Format: Return only the follow-up query, nothing else."""

        return self.llm_service.generate(
            input_data=gap_analysis_prompt,
            system_prompt="You are a research analyst specializing in identifying research gaps and generating focused follow-up queries.",
            temperature=0.3
        )


class InstantWorkflow(BaseWorkflow):
    """Instant research workflow - single round quick response."""
    
    def __init__(self, llm_service=None):
        super().__init__(ResearchMode.INSTANT, llm_service)
    
    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute instant research workflow (1 round).
        
        Args:
            query: Research query
            context: Additional context
            
        Returns:
            Instant research results
        """
        try:
            start_time = time.time()
            
            # Instant research context
            research_context = """INSTANT RESEARCH MODE (Round 1/1):
- Provide immediate, factual answers
- Focus on essential information only
- Use concise, direct language
- Prioritize accuracy over depth
- Answer the core question quickly
- Include key facts and definitions
- Avoid lengthy explanations"""
            
            # Generate response (single round)
            content = self._generate_research_response(
                query=query,
                research_context=research_context,
                temperature=0.1
            )
            
            execution_time = round(time.time() - start_time, 2)
            
            return format_response(
                success=True,
                data={
                    'mode': 'instant',
                    'query': query,
                    'content': content,
                    'execution_time': execution_time,
                    'research_rounds': 1,
                    'total_rounds': 1,
                    'sources_used': 0,
                    'context': context or {},
                    'timestamp': get_current_timestamp()
                },
                message="Instant research completed (1 round)"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'query': query, 'mode': 'instant'},
                "Error in instant research workflow"
            )


class QuickWorkflow(BaseWorkflow):
    """Quick research workflow - 2 rounds of enhanced research."""
    
    def __init__(self, llm_service=None):
        super().__init__(ResearchMode.QUICK, llm_service)
    
    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute quick research workflow (2 rounds).
        
        Args:
            query: Research query
            context: Additional context
            
        Returns:
            Quick research results
        """
        try:
            start_time = time.time()
            results = []
            
            # Round 1: Initial research
            research_context = """QUICK RESEARCH MODE (Round 1/2):
- Provide enhanced analysis with context
- Include relevant background information
- Explain key concepts and relationships
- Add practical examples when helpful
- Structure information logically
- Balance depth with accessibility
- Include implications and applications"""
            
            content = self._generate_research_response(
                query=query,
                research_context=research_context,
                temperature=0.2
            )
            
            results.append({
                'round': 1,
                'query': query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            # Round 2: Follow-up research
            followup_query = self._analyze_gaps_and_generate_followup(query, results, 1)
            
            research_context = """QUICK RESEARCH MODE (Round 2/2):
- Build upon the initial research
- Address specific gaps or clarifications
- Provide additional context and examples
- Focus on practical applications
- Include relevant case studies or scenarios
- Ensure comprehensive coverage of the topic"""
            
            content = self._generate_research_response(
                query=followup_query,
                research_context=research_context,
                temperature=0.2,
                previous_results=results
            )
            
            results.append({
                'round': 2,
                'query': followup_query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            execution_time = round(time.time() - start_time, 2)
            
            return format_response(
                success=True,
                data={
                    'mode': 'quick',
                    'query': query,
                    'content': self._combine_results(results),
                    'rounds': results,
                    'execution_time': execution_time,
                    'research_rounds': 2,
                    'total_rounds': 2,
                    'sources_used': 0,
                    'context': context or {},
                    'timestamp': get_current_timestamp()
                },
                message="Quick research completed (2 rounds)"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'query': query, 'mode': 'quick'},
                "Error in quick research workflow"
            )
    
    def _combine_results(self, results: List[Dict[str, Any]]) -> str:
        """Combine results from multiple rounds."""
        combined = f"# Research Results ({len(results)} rounds)\n\n"
        for result in results:
            combined += f"## Round {result['round']}: {result['query']}\n\n"
            combined += f"{result['content']}\n\n"
        return combined


class StandardWorkflow(BaseWorkflow):
    """Standard research workflow - 3 rounds of comprehensive research."""
    
    def __init__(self, llm_service=None):
        super().__init__(ResearchMode.STANDARD, llm_service)
    
    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute standard research workflow (3 rounds).
        
        Args:
            query: Research query
            context: Additional context
            
        Returns:
            Standard research results
        """
        try:
            start_time = time.time()
            results = []
            
            # Round 1: Initial comprehensive research
            research_context = """STANDARD RESEARCH MODE (Round 1/3):
- Conduct comprehensive analysis from multiple perspectives
- Examine different viewpoints and approaches
- Include historical context and evolution
- Analyze current trends and developments
- Consider practical applications and case studies
- Structure with clear sections and subsections"""
            
            content = self._generate_research_response(
                query=query,
                research_context=research_context,
                temperature=0.2
            )
            
            results.append({
                'round': 1,
                'query': query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            # Round 2: Gap analysis and follow-up
            followup_query = self._analyze_gaps_and_generate_followup(query, results, 1)
            
            research_context = """STANDARD RESEARCH MODE (Round 2/3):
- Address identified gaps from Round 1
- Provide deeper analysis of specific aspects
- Include additional case studies and examples
- Discuss challenges and limitations
- Consider different methodologies or approaches
- Analyze controversies or debates"""
            
            content = self._generate_research_response(
                query=followup_query,
                research_context=research_context,
                temperature=0.2,
                previous_results=results
            )
            
            results.append({
                'round': 2,
                'query': followup_query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            # Round 3: Final synthesis and implications
            followup_query = self._analyze_gaps_and_generate_followup(query, results, 2)
            
            research_context = """STANDARD RESEARCH MODE (Round 3/3):
- Synthesize findings from previous rounds
- Provide balanced, well-rounded coverage
- Include relevant statistics and data points
- Address potential implications and future directions
- Provide comprehensive conclusions
- Ensure all aspects are thoroughly covered"""
            
            content = self._generate_research_response(
                query=followup_query,
                research_context=research_context,
                temperature=0.2,
                previous_results=results
            )
            
            results.append({
                'round': 3,
                'query': followup_query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            execution_time = round(time.time() - start_time, 2)
            
            return format_response(
                success=True,
                data={
                    'mode': 'standard',
                    'query': query,
                    'content': self._combine_results(results),
                    'rounds': results,
                    'execution_time': execution_time,
                    'research_rounds': 3,
                    'total_rounds': 3,
                    'sources_used': 0,
                    'context': context or {},
                    'timestamp': get_current_timestamp()
                },
                message="Standard research completed (3 rounds)"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'query': query, 'mode': 'standard'},
                "Error in standard research workflow"
            )
    
    def _combine_results(self, results: List[Dict[str, Any]]) -> str:
        """Combine results from multiple rounds."""
        combined = f"# Comprehensive Research Results ({len(results)} rounds)\n\n"
        for result in results:
            combined += f"## Round {result['round']}: {result['query']}\n\n"
            combined += f"{result['content']}\n\n"
        return combined


class DeepWorkflow(BaseWorkflow):
    """Deep research workflow - 4 rounds of exhaustive academic-level research."""
    
    def __init__(self, llm_service=None):
        super().__init__(ResearchMode.DEEP, llm_service)
    
    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute deep research workflow (4 rounds).
        
        Args:
            query: Research query
            context: Additional context
            
        Returns:
            Deep research results
        """
        try:
            start_time = time.time()
            results = []
            
            # Round 1: Foundation and overview
            research_context = """DEEP RESEARCH MODE (Round 1/4):
- Provide comprehensive overview and foundation
- Include detailed historical background and evolution
- Analyze multiple theoretical frameworks and approaches
- Examine fundamental concepts and principles
- Structure with detailed sections and subsections
- Use professional academic language and terminology"""
            
            content = self._generate_research_response(
                query=query,
                research_context=research_context,
                temperature=0.3
            )
            
            results.append({
                'round': 1,
                'query': query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            # Round 2: Case studies and applications
            followup_query = self._analyze_gaps_and_generate_followup(query, results, 1)
            
            research_context = """DEEP RESEARCH MODE (Round 2/4):
- Examine detailed case studies and real-world applications
- Analyze quantitative data, statistics, and research findings
- Discuss practical implementations and methodologies
- Include cross-disciplinary perspectives
- Provide specific examples and scenarios
- Analyze trends, patterns, and correlations"""
            
            content = self._generate_research_response(
                query=followup_query,
                research_context=research_context,
                temperature=0.3,
                previous_results=results
            )
            
            results.append({
                'round': 2,
                'query': followup_query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            # Round 3: Controversies and debates
            followup_query = self._analyze_gaps_and_generate_followup(query, results, 2)
            
            research_context = """DEEP RESEARCH MODE (Round 3/4):
- Discuss controversies, debates, and differing opinions
- Analyze ethical implications and societal impact
- Examine limitations and challenges
- Consider alternative approaches and methodologies
- Analyze conflicting research findings
- Discuss unresolved questions and areas of uncertainty"""
            
            content = self._generate_research_response(
                query=followup_query,
                research_context=research_context,
                temperature=0.3,
                previous_results=results
            )
            
            results.append({
                'round': 3,
                'query': followup_query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            # Round 4: Future prospects and synthesis
            followup_query = self._analyze_gaps_and_generate_followup(query, results, 3)
            
            research_context = """DEEP RESEARCH MODE (Round 4/4):
- Discuss future prospects and emerging developments
- Provide critical analysis and evaluation
- Synthesize all findings into comprehensive conclusions
- Include recommendations and implications
- Address long-term trends and predictions
- Provide comprehensive final analysis"""
            
            content = self._generate_research_response(
                query=followup_query,
                research_context=research_context,
                temperature=0.3,
                previous_results=results
            )
            
            results.append({
                'round': 4,
                'query': followup_query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            execution_time = round(time.time() - start_time, 2)
            
            return format_response(
                success=True,
                data={
                    'mode': 'deep',
                    'query': query,
                    'content': self._combine_results(results),
                    'rounds': results,
                    'execution_time': execution_time,
                    'research_rounds': 4,
                    'total_rounds': 4,
                    'sources_used': 0,
                    'context': context or {},
                    'timestamp': get_current_timestamp()
                },
                message="Deep research completed (4 rounds)"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'query': query, 'mode': 'deep'},
                "Error in deep research workflow"
            )
    
    def _combine_results(self, results: List[Dict[str, Any]]) -> str:
        """Combine results from multiple rounds."""
        combined = f"# Exhaustive Research Results ({len(results)} rounds)\n\n"
        for result in results:
            combined += f"## Round {result['round']}: {result['query']}\n\n"
            combined += f"{result['content']}\n\n"
        return combined


class WorkflowFactory:
    """Factory for creating research workflows."""
    
    @staticmethod
    def create_workflow(mode: str, llm_service=None) -> BaseWorkflow:
        """
        Create a workflow instance for the specified mode.
        
        Args:
            mode: Research mode (instant, quick, standard, deep)
            llm_service: LLM service instance
            
        Returns:
            Workflow instance
        """
        mode_map = {
            'instant': InstantWorkflow,
            'quick': QuickWorkflow,
            'standard': StandardWorkflow,
            'deep': DeepWorkflow
        }
        
        if mode not in mode_map:
            raise ValueError(f"Invalid research mode: {mode}")
        
        return mode_map[mode](llm_service)
    
    @staticmethod
    def get_available_modes() -> List[str]:
        """Get list of available research modes."""
        return ['instant', 'quick', 'standard', 'deep']