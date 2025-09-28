"""
Mock LLM Service - Mock implementation for Phase 1 testing.

This module provides a mock LLM service that simulates real LLM behavior
with consistent API and realistic response patterns for testing purposes.
"""

import json
import random
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

from ..base_agent.error_handler import ErrorHandler, ErrorCategory
from ..utils.utils import format_response, sanitize_string


class MockModelType(Enum):
    """Mock model types."""
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"


class MockResponses:
    """Mock response templates for different research modes."""
    
    INSTANT_RESPONSES = [
        "Based on the available information, {query} can be answered as follows: {answer}",
        "Quick analysis shows that {query} relates to {answer}",
        "The key information about {query} is: {answer}",
        "From the data available: {query} = {answer}"
    ]
    
    QUICK_RESPONSES = [
        "Enhanced analysis of {query} reveals: {answer}. Additional context: {context}",
        "Quick research shows {query} involves {answer}. Key insights: {insights}",
        "Analysis indicates {query} is related to {answer}. Supporting evidence: {evidence}",
        "Research findings for {query}: {answer}. Important considerations: {considerations}"
    ]
    
    STANDARD_RESPONSES = [
        "Comprehensive research on {query} shows: {answer}. Detailed analysis: {analysis}. Sources: {sources}",
        "Multi-round analysis of {query} reveals: {answer}. Research methodology: {methodology}. Findings: {findings}",
        "Thorough investigation of {query} indicates: {answer}. Research process: {process}. Conclusions: {conclusions}",
        "Detailed research on {query} concludes: {answer}. Analysis framework: {framework}. Results: {results}"
    ]
    
    DEEP_RESPONSES = [
        "Exhaustive research on {query} demonstrates: {answer}. Comprehensive analysis: {analysis}. Research methodology: {methodology}. Sources consulted: {sources}. Gaps identified: {gaps}. Recommendations: {recommendations}",
        "Deep investigation of {query} reveals: {answer}. Multi-dimensional analysis: {analysis}. Research approach: {approach}. Data sources: {sources}. Limitations: {limitations}. Future research: {future}",
        "Comprehensive study of {query} shows: {answer}. Systematic analysis: {analysis}. Research design: {design}. Evidence base: {evidence}. Critical evaluation: {evaluation}. Implications: {implications}",
        "Exhaustive analysis of {query} concludes: {answer}. Holistic research: {research}. Analytical framework: {framework}. Source diversity: {sources}. Quality assessment: {quality}. Synthesis: {synthesis}"
    ]
    
    ERROR_RESPONSES = [
        "I encountered an issue while researching {query}. Error: {error}",
        "Research failed for {query} due to: {error}",
        "Unable to complete research on {query}. Problem: {error}",
        "Research error for {query}: {error}"
    ]


class MockLLMService:
    """
    Mock LLM service for Phase 1 testing.
    
    Provides consistent API with realistic response patterns and error simulation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Mock LLM Service.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.error_handler = ErrorHandler("MockLLMService")
        
        # Mock model configuration
        self.models = {
            MockModelType.GPT_4.value: {
                'max_tokens': 4096,
                'temperature_range': (0.0, 0.3),
                'response_time_range': (0.5, 2.0),
                'accuracy': 0.95
            },
            MockModelType.GPT_3_5_TURBO.value: {
                'max_tokens': 4096,
                'temperature_range': (0.0, 0.5),
                'response_time_range': (0.3, 1.5),
                'accuracy': 0.90
            },
            MockModelType.CLAUDE_3_OPUS.value: {
                'max_tokens': 4096,
                'temperature_range': (0.0, 0.2),
                'response_time_range': (0.8, 2.5),
                'accuracy': 0.96
            },
            MockModelType.CLAUDE_3_SONNET.value: {
                'max_tokens': 4096,
                'temperature_range': (0.0, 0.4),
                'response_time_range': (0.5, 1.8),
                'accuracy': 0.93
            },
            MockModelType.CLAUDE_3_HAIKU.value: {
                'max_tokens': 4096,
                'temperature_range': (0.0, 0.6),
                'response_time_range': (0.2, 1.0),
                'accuracy': 0.88
            }
        }
        
        # Response counters for consistency
        self.response_counters = {
            'instant': 0,
            'quick': 0,
            'standard': 0,
            'deep': 0
        }
        
        # Error simulation settings
        self.error_rate = self.config.get('error_rate', 0.05)  # 5% error rate
        self.timeout_rate = self.config.get('timeout_rate', 0.02)  # 2% timeout rate
    
    def generate_response(
        self,
        query: str,
        mode: str,
        model: str = MockModelType.GPT_4.value,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate a mock response for a query.
        
        Args:
            query: Research query
            mode: Research mode (instant, quick, standard, deep)
            model: Model to use
            temperature: Temperature setting
            max_tokens: Maximum tokens
            timeout: Timeout in seconds
            
        Returns:
            Response dictionary
        """
        try:
            # Simulate processing time
            processing_time = self._simulate_processing_time(model)
            
            # Check for timeout
            if timeout and processing_time > timeout:
                return self._create_timeout_response(query, mode)
            
            # Simulate errors
            if random.random() < self.error_rate:
                return self._create_error_response(query, mode)
            
            # Generate response based on mode
            response_content = self._generate_mode_response(query, mode)
            
            # Create response metadata
            response_metadata = self._create_response_metadata(
                query, mode, model, temperature, max_tokens, processing_time
            )
            
            return format_response(
                success=True,
                data={
                    'content': response_content,
                    'model': model,
                    'mode': mode,
                    'query': query,
                    'metadata': response_metadata
                },
                message=f"Mock response generated for {mode} research"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'query': query, 'mode': mode, 'model': model},
                f"Error generating mock response: {str(e)}"
            )
    
    def _simulate_processing_time(self, model: str) -> float:
        """
        Simulate realistic processing time based on model.
        
        Args:
            model: Model identifier
            
        Returns:
            Processing time in seconds
        """
        model_config = self.models.get(model, self.models[MockModelType.GPT_4.value])
        min_time, max_time = model_config['response_time_range']
        
        # Add some randomness
        base_time = random.uniform(min_time, max_time)
        
        # Add occasional longer processing times
        if random.random() < 0.1:  # 10% chance
            base_time *= random.uniform(2, 4)
        
        return round(base_time, 2)
    
    def _generate_mode_response(self, query: str, mode: str) -> str:
        """
        Generate response content based on research mode.
        
        Args:
            query: Research query
            mode: Research mode
            
        Returns:
            Generated response content
        """
        # Get response templates
        templates = getattr(MockResponses, f"{mode.upper()}_RESPONSES", MockResponses.INSTANT_RESPONSES)
        
        # Cycle through templates for consistency
        template_index = self.response_counters[mode] % len(templates)
        template = templates[template_index]
        self.response_counters[mode] += 1
        
        # Generate mock data for template
        mock_data = self._generate_mock_data(query, mode)
        
        # Format template with mock data
        try:
            return template.format(**mock_data)
        except KeyError:
            # Fallback if template formatting fails
            return f"Mock response for {mode} research on '{query}': {mock_data.get('answer', 'Analysis completed')}"
    
    def _generate_mock_data(self, query: str, mode: str) -> Dict[str, str]:
        """
        Generate mock data for response templates.
        
        Args:
            query: Research query
            mode: Research mode
            
        Returns:
            Dictionary of mock data
        """
        base_data = {
            'query': query,
            'answer': f"Mock answer for '{query}'",
            'context': "Additional context information",
            'insights': "Key insights from analysis",
            'evidence': "Supporting evidence",
            'considerations': "Important considerations",
            'analysis': "Detailed analysis",
            'sources': "Source 1, Source 2, Source 3",
            'methodology': "Research methodology used",
            'findings': "Key findings",
            'process': "Research process",
            'conclusions': "Research conclusions",
            'framework': "Analytical framework",
            'results': "Research results",
            'gaps': "Identified gaps",
            'recommendations': "Recommendations",
            'approach': "Research approach",
            'limitations': "Research limitations",
            'future': "Future research directions",
            'design': "Research design",
            'evaluation': "Critical evaluation",
            'implications': "Research implications",
            'research': "Holistic research approach",
            'quality': "Quality assessment",
            'synthesis': "Research synthesis"
        }
        
        # Add mode-specific enhancements
        if mode == 'instant':
            base_data['answer'] = f"Quick answer: {query} involves basic concepts"
        elif mode == 'quick':
            base_data['answer'] = f"Enhanced answer: {query} has multiple aspects"
            base_data['context'] = f"Context for {query}: relevant background information"
        elif mode == 'standard':
            base_data['answer'] = f"Comprehensive answer: {query} requires detailed analysis"
            base_data['analysis'] = f"Multi-dimensional analysis of {query}"
        elif mode == 'deep':
            base_data['answer'] = f"Exhaustive answer: {query} demands thorough investigation"
            base_data['analysis'] = f"Comprehensive analysis of {query}"
        
        return base_data
    
    def _create_response_metadata(
        self,
        query: str,
        mode: str,
        model: str,
        temperature: Optional[float],
        max_tokens: Optional[int],
        processing_time: float
    ) -> Dict[str, Any]:
        """
        Create response metadata.
        
        Args:
            query: Research query
            mode: Research mode
            model: Model used
            temperature: Temperature setting
            max_tokens: Maximum tokens
            processing_time: Processing time
            
        Returns:
            Metadata dictionary
        """
        model_config = self.models.get(model, {})
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'processing_time': processing_time,
            'model_config': {
                'temperature': temperature or random.uniform(*model_config.get('temperature_range', (0.0, 0.3))),
                'max_tokens': max_tokens or model_config.get('max_tokens', 4096),
                'accuracy': model_config.get('accuracy', 0.95)
            },
            'query_length': len(query),
            'mode_complexity': self._get_mode_complexity(mode),
            'response_id': f"mock_{int(datetime.utcnow().timestamp())}"
        }
    
    def _get_mode_complexity(self, mode: str) -> str:
        """
        Get complexity level for research mode.
        
        Args:
            mode: Research mode
            
        Returns:
            Complexity level
        """
        complexity_map = {
            'instant': 'low',
            'quick': 'medium',
            'standard': 'high',
            'deep': 'very_high'
        }
        return complexity_map.get(mode, 'medium')
    
    def _create_timeout_response(self, query: str, mode: str) -> Dict[str, Any]:
        """
        Create a timeout response.
        
        Args:
            query: Research query
            mode: Research mode
            
        Returns:
            Timeout response
        """
        return format_response(
            success=False,
            message=f"Request timed out for {mode} research",
            data={
                'query': query,
                'mode': mode,
                'error_type': 'timeout',
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def _create_error_response(self, query: str, mode: str) -> Dict[str, Any]:
        """
        Create an error response.
        
        Args:
            query: Research query
            mode: Research mode
            
        Returns:
            Error response
        """
        error_templates = MockResponses.ERROR_RESPONSES
        error_template = random.choice(error_templates)
        
        error_data = {
            'query': query,
            'error': random.choice([
                'Service temporarily unavailable',
                'Rate limit exceeded',
                'Invalid request format',
                'Model overloaded',
                'Network connectivity issue'
            ])
        }
        
        error_message = error_template.format(**error_data)
        
        return format_response(
            success=False,
            message=error_message,
            data={
                'query': query,
                'mode': mode,
                'error_type': 'service_error',
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available mock models.
        
        Returns:
            List of model information
        """
        models = []
        for model_name, config in self.models.items():
            models.append({
                'name': model_name,
                'max_tokens': config['max_tokens'],
                'temperature_range': config['temperature_range'],
                'response_time_range': config['response_time_range'],
                'accuracy': config['accuracy'],
                'type': 'mock'
            })
        
        return models
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get mock service status.
        
        Returns:
            Service status information
        """
        return {
            'status': 'operational',
            'type': 'mock',
            'models_available': len(self.models),
            'error_rate': self.error_rate,
            'timeout_rate': self.timeout_rate,
            'response_counters': self.response_counters.copy(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def configure_error_simulation(
        self,
        error_rate: Optional[float] = None,
        timeout_rate: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Configure error simulation parameters.
        
        Args:
            error_rate: New error rate (0.0 to 1.0)
            timeout_rate: New timeout rate (0.0 to 1.0)
            
        Returns:
            Configuration confirmation
        """
        if error_rate is not None:
            self.error_rate = max(0.0, min(1.0, error_rate))
        
        if timeout_rate is not None:
            self.timeout_rate = max(0.0, min(1.0, timeout_rate))
        
        return format_response(
            success=True,
            message="Error simulation configured",
            data={
                'error_rate': self.error_rate,
                'timeout_rate': self.timeout_rate
            }
        )
