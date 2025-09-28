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
        round_number: int,
        max_rounds: int
    ) -> Dict[str, Any]:
        """
        Analyze current research results and determine next action.
        
        Args:
            original_query: Original research query
            current_results: Results from previous rounds
            round_number: Current round number
            max_rounds: Maximum rounds for this research mode
            
        Returns:
            Dictionary with analysis results and next action
        """
        if not self.llm_service:
            return {
                "goal_reached": False,
                "next_query": f"Follow-up query for round {round_number + 1}",
                "reasoning": "Mock analysis"
            }
        
        # Build comprehensive summary of all research so far
        research_summary = f"Original Query: {original_query}\n\n"
        research_summary += f"Research Progress ({round_number}/{max_rounds} rounds completed):\n\n"
        
        for i, result in enumerate(current_results, 1):
            research_summary += f"Round {i} Query: {result['query']}\n"
            research_summary += f"Round {i} Answer: {result['content'][:400]}...\n\n"
        
        gap_analysis_prompt = f"""You are a research analyst. Analyze the current research progress and determine the next action.

{research_summary}

Your task:
1. Assess if the original query has been comprehensively answered
2. If not, identify specific gaps that need to be filled
3. Generate the next focused query to address those gaps
4. Consider if more rounds are needed or if the goal is reached

Return your analysis as JSON in this exact format:
{{
    "goal_reached": true/false,
    "reasoning": "Explanation of your assessment",
    "gaps_identified": ["gap1", "gap2", "gap3"],
    "next_query": "Specific focused query for next round",
    "confidence": 0.0-1.0
}}

Guidelines:
- goal_reached: true only if the original query is comprehensively answered
- reasoning: Explain why the goal is/isn't reached
- gaps_identified: List specific missing information
- next_query: Generate a focused, actionable query
- confidence: Your confidence in the assessment (0.0-1.0)
- If goal_reached is true, next_query can be empty
- If round_number >= max_rounds, goal_reached should be true"""

        try:
            response = self.llm_service.generate(
                input_data=gap_analysis_prompt,
                system_prompt="You are a research analyst specializing in comprehensive research assessment and gap analysis.",
                temperature=0.3,
                return_json=True
            )
            
            # Parse JSON response
            import json
            analysis = json.loads(response)
            
            # Validate required fields
            required_fields = ["goal_reached", "reasoning", "gaps_identified", "next_query", "confidence"]
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field: {field}")
            
            return analysis
            
        except Exception as e:
            # Fallback if JSON parsing fails
            return {
                "goal_reached": round_number >= max_rounds,
                "reasoning": f"Analysis failed: {str(e)}",
                "gaps_identified": ["Analysis error occurred"],
                "next_query": f"Continue research for round {round_number + 1}" if round_number < max_rounds else "",
                "confidence": 0.5
            }


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
        Execute quick research workflow (up to 2 rounds).
        
        Args:
            query: Research query
            context: Additional context
            
        Returns:
            Quick research results
        """
        try:
            start_time = time.time()
            results = []
            max_rounds = 2
            current_round = 1
            
            # Round 1: Initial research
            research_context = f"""QUICK RESEARCH MODE (Round {current_round}/{max_rounds}):
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
                'round': current_round,
                'query': query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            # Multi-round loop: analyze gaps and continue if needed
            while current_round < max_rounds:
                # Analyze gaps and determine next action
                analysis = self._analyze_gaps_and_generate_followup(
                    original_query=query,
                    current_results=results,
                    round_number=current_round,
                    max_rounds=max_rounds
                )
                
                # Check if goal is reached
                if analysis.get("goal_reached", False):
                    break
                
                # Generate next query
                next_query = analysis.get("next_query", "")
                if not next_query:
                    break
                
                current_round += 1
                
                # Generate response for next round
                research_context = f"""QUICK RESEARCH MODE (Round {current_round}/{max_rounds}):
- Build upon previous research
- Address specific gaps: {', '.join(analysis.get('gaps_identified', []))}
- Focus on: {analysis.get('reasoning', '')}
- Provide additional context and examples
- Ensure comprehensive coverage of the topic"""
                
                content = self._generate_research_response(
                    query=next_query,
                    research_context=research_context,
                    temperature=0.2,
                    previous_results=results
                )
                
                results.append({
                    'round': current_round,
                    'query': next_query,
                    'content': content,
                    'analysis': analysis,
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
                    'research_rounds': len(results),
                    'total_rounds': max_rounds,
                    'sources_used': 0,
                    'context': context or {},
                    'timestamp': get_current_timestamp()
                },
                message=f"Quick research completed ({len(results)} rounds)"
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
        Execute standard research workflow (up to 3 rounds).
        
        Args:
            query: Research query
            context: Additional context
            
        Returns:
            Standard research results
        """
        try:
            start_time = time.time()
            results = []
            max_rounds = 3
            current_round = 1
            
            # Round 1: Initial comprehensive research
            research_context = f"""STANDARD RESEARCH MODE (Round {current_round}/{max_rounds}):
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
                'round': current_round,
                'query': query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            # Multi-round loop: analyze gaps and continue if needed
            while current_round < max_rounds:
                # Analyze gaps and determine next action
                analysis = self._analyze_gaps_and_generate_followup(
                    original_query=query,
                    current_results=results,
                    round_number=current_round,
                    max_rounds=max_rounds
                )
                
                # Check if goal is reached
                if analysis.get("goal_reached", False):
                    break
                
                # Generate next query
                next_query = analysis.get("next_query", "")
                if not next_query:
                    break
                
                current_round += 1
                
                # Generate response for next round
                research_context = f"""STANDARD RESEARCH MODE (Round {current_round}/{max_rounds}):
- Build upon previous research
- Address specific gaps: {', '.join(analysis.get('gaps_identified', []))}
- Focus on: {analysis.get('reasoning', '')}
- Provide deeper analysis of specific aspects
- Include additional case studies and examples
- Discuss challenges and limitations
- Consider different methodologies or approaches
- Analyze controversies or debates"""
                
                content = self._generate_research_response(
                    query=next_query,
                    research_context=research_context,
                    temperature=0.2,
                    previous_results=results
                )
                
                results.append({
                    'round': current_round,
                    'query': next_query,
                    'content': content,
                    'analysis': analysis,
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
                    'research_rounds': len(results),
                    'total_rounds': max_rounds,
                    'sources_used': 0,
                    'context': context or {},
                    'timestamp': get_current_timestamp()
                },
                message=f"Standard research completed ({len(results)} rounds)"
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
        Execute deep research workflow (up to 4 rounds).
        
        Args:
            query: Research query
            context: Additional context
            
        Returns:
            Deep research results
        """
        try:
            start_time = time.time()
            results = []
            max_rounds = 4
            current_round = 1
            
            # Round 1: Foundation and overview
            research_context = f"""DEEP RESEARCH MODE (Round {current_round}/{max_rounds}):
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
                'round': current_round,
                'query': query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            # Multi-round loop: analyze gaps and continue if needed
            while current_round < max_rounds:
                # Analyze gaps and determine next action
                analysis = self._analyze_gaps_and_generate_followup(
                    original_query=query,
                    current_results=results,
                    round_number=current_round,
                    max_rounds=max_rounds
                )
                
                # Check if goal is reached
                if analysis.get("goal_reached", False):
                    break
                
                # Generate next query
                next_query = analysis.get("next_query", "")
                if not next_query:
                    break
                
                current_round += 1
                
                # Generate response for next round
                research_context = f"""DEEP RESEARCH MODE (Round {current_round}/{max_rounds}):
- Build upon previous research
- Address specific gaps: {', '.join(analysis.get('gaps_identified', []))}
- Focus on: {analysis.get('reasoning', '')}
- Provide exhaustive, academic-level analysis
- Include detailed case studies and real-world applications
- Analyze quantitative data, statistics, and research findings
- Discuss controversies, debates, and differing opinions
- Consider ethical implications and societal impact
- Examine limitations and challenges
- Provide critical analysis and evaluation
- Include cross-disciplinary perspectives"""
                
                content = self._generate_research_response(
                    query=next_query,
                    research_context=research_context,
                    temperature=0.3,
                    previous_results=results
                )
                
                results.append({
                    'round': current_round,
                    'query': next_query,
                    'content': content,
                    'analysis': analysis,
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
                    'research_rounds': len(results),
                    'total_rounds': max_rounds,
                    'sources_used': 0,
                    'context': context or {},
                    'timestamp': get_current_timestamp()
                },
                message=f"Deep research completed ({len(results)} rounds)"
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