"""
ResearchAgent - Deep research agent implementation.

This module provides the ResearchAgent class that inherits from BaseAgent
and implements research-specific functionality for different research modes.
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..base_agent.core import BaseAgent
from ..base_agent.context_manager import ContextType
from ..base_agent.error_handler import ErrorHandler, ErrorCategory
from ..llm_service.core import LLMService
from .workflows.workflows import WorkflowFactory, ResearchMode
from ..utils.utils import format_response, validate_input_data, sanitize_string


class ResearchAgent(BaseAgent):
    """
    Research agent for conducting deep research in multiple modes.
    
    Inherits from BaseAgent and adds research-specific capabilities.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        logger_name: Optional[str] = None
    ):
        """
        Initialize ResearchAgent.
        
        Args:
            config: Configuration dictionary
            session_id: Optional session identifier
            logger_name: Optional logger name
        """
        # Initialize base agent
        super().__init__(config, session_id, logger_name)
        
        # Initialize LLM service
        self.llm_service = LLMService(config)
        
        # Research-specific configuration
        self.research_config = self.config.get('research', {})
        self.system_prompts = self.config.get('system_prompts', {})
        self.error_messages = self.config.get('error_messages', {})
        
        # Research state
        self.current_mode = None
        self.research_history = []
        self.active_research = None
        
        # Initialize research capabilities
        self._initialize_research_capabilities()
    
    def _initialize_research_capabilities(self) -> None:
        """Initialize research-specific capabilities."""
        research_capabilities = {
            'instant_research': True,
            'quick_research': True,
            'standard_research': True,
            'deep_research': True,
            'mode_selection': True,
            'research_history': True,
            'llm_integration': True
        }
        
        # Update capabilities
        self._capabilities.update(research_capabilities)
        
        # Store in context
        self.context_manager.set_context(
            'research_capabilities',
            research_capabilities,
            ContextType.SESSION
        )
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a research request.
        
        Args:
            request: Request dictionary
            
        Returns:
            Response dictionary
        """
        try:
            method = request.get('method', '').lower()
            
            # Route to appropriate method
            if method == 'instant_research':
                return self.instant_research(request)
            elif method == 'quick_research':
                return self.quick_research(request)
            elif method == 'standard_research':
                return self.standard_research(request)
            elif method == 'deep_research':
                return self.deep_research(request)
            elif method == 'solve':
                return self.solve(request)
            else:
                return format_response(
                    success=False,
                    message=f"Unknown method: {method}",
                    data={'available_methods': self._get_available_methods()}
                )
                
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'request': request},
                "Error processing research request"
            )
    
    def instant_research(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct instant research.
        
        Args:
            request: Research request
            
        Returns:
            Research results
        """
        try:
            # Validate request
            schema = {
                'type': 'object',
                'required': ['query'],
                'properties': {
                    'query': {'type': 'string', 'minLength': 1},
                    'context': {'type': 'object'}
                }
            }
            
            if not self.validate_request(request, schema):
                return format_response(
                    success=False,
                    message="Invalid request format for instant research"
                )
            
            query = sanitize_string(request['query'])
            context = request.get('context', {})
            
            # Set current mode
            self.current_mode = 'instant'
            
            # Create workflow
            workflow = WorkflowFactory.create_workflow('instant', self.llm_service)
            
            # Execute research
            result = workflow.execute(query, context)
            
            # Store in research history
            self._add_to_research_history('instant', query, result)
            
            return result
            
        except Exception as e:
            error_msg = self.error_messages.get('instant_research', 'Error conducting instant research: {error}')
            return self.error_handler.handle_error(
                e,
                {'request': request, 'mode': 'instant'},
                error_msg.format(error=str(e))
            )
    
    def quick_research(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct quick research.
        
        Args:
            request: Research request
            
        Returns:
            Research results
        """
        try:
            # Validate request
            schema = {
                'type': 'object',
                'required': ['query'],
                'properties': {
                    'query': {'type': 'string', 'minLength': 1},
                    'context': {'type': 'object'}
                }
            }
            
            if not self.validate_request(request, schema):
                return format_response(
                    success=False,
                    message="Invalid request format for quick research"
                )
            
            query = sanitize_string(request['query'])
            context = request.get('context', {})
            
            # Set current mode
            self.current_mode = 'quick'
            
            # Create workflow
            workflow = WorkflowFactory.create_workflow('quick', self.llm_service)
            
            # Execute research
            result = workflow.execute(query, context)
            
            # Store in research history
            self._add_to_research_history('quick', query, result)
            
            return result
            
        except Exception as e:
            error_msg = self.error_messages.get('quick_research', 'Error conducting quick research: {error}')
            return self.error_handler.handle_error(
                e,
                {'request': request, 'mode': 'quick'},
                error_msg.format(error=str(e))
            )
    
    def standard_research(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct standard research.
        
        Args:
            request: Research request
            
        Returns:
            Research results
        """
        try:
            # Validate request
            schema = {
                'type': 'object',
                'required': ['query'],
                'properties': {
                    'query': {'type': 'string', 'minLength': 1},
                    'context': {'type': 'object'}
                }
            }
            
            if not self.validate_request(request, schema):
                return format_response(
                    success=False,
                    message="Invalid request format for standard research"
                )
            
            query = sanitize_string(request['query'])
            context = request.get('context', {})
            
            # Set current mode
            self.current_mode = 'standard'
            
            # Create workflow
            workflow = WorkflowFactory.create_workflow('standard', self.llm_service)
            
            # Execute research
            result = workflow.execute(query, context)
            
            # Store in research history
            self._add_to_research_history('standard', query, result)
            
            return result
            
        except Exception as e:
            error_msg = self.error_messages.get('standard_research', 'Error conducting standard research: {error}')
            return self.error_handler.handle_error(
                e,
                {'request': request, 'mode': 'standard'},
                error_msg.format(error=str(e))
            )
    
    def deep_research(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct deep research.
        
        Args:
            request: Research request
            
        Returns:
            Research results
        """
        try:
            # Validate request
            schema = {
                'type': 'object',
                'required': ['query'],
                'properties': {
                    'query': {'type': 'string', 'minLength': 1},
                    'context': {'type': 'object'}
                }
            }
            
            if not self.validate_request(request, schema):
                return format_response(
                    success=False,
                    message="Invalid request format for deep research"
                )
            
            query = sanitize_string(request['query'])
            context = request.get('context', {})
            
            # Set current mode
            self.current_mode = 'deep'
            
            # Create workflow
            workflow = WorkflowFactory.create_workflow('deep', self.llm_service)
            
            # Execute research
            result = workflow.execute(query, context)
            
            # Store in research history
            self._add_to_research_history('deep', query, result)
            
            return result
            
        except Exception as e:
            error_msg = self.error_messages.get('deep_research', 'Error conducting deep research: {error}')
            return self.error_handler.handle_error(
                e,
                {'request': request, 'mode': 'deep'},
                error_msg.format(error=str(e))
            )
    
    def solve(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solve a problem using appropriate research mode.
        
        Args:
            request: Problem-solving request
            
        Returns:
            Solution results
        """
        try:
            # Validate request
            schema = {
                'type': 'object',
                'required': ['query'],
                'properties': {
                    'query': {'type': 'string', 'minLength': 1},
                    'mode': {'type': 'string', 'enum': ['instant', 'quick', 'standard', 'deep']},
                    'context': {'type': 'object'}
                }
            }
            
            if not self.validate_request(request, schema):
                return format_response(
                    success=False,
                    message="Invalid request format for solve method"
                )
            
            query = sanitize_string(request['query'])
            mode = request.get('mode', 'standard')  # Default to standard
            context = request.get('context', {})
            
            # Route to appropriate research method
            if mode == 'instant':
                return self.instant_research({'query': query, 'context': context})
            elif mode == 'quick':
                return self.quick_research({'query': query, 'context': context})
            elif mode == 'standard':
                return self.standard_research({'query': query, 'context': context})
            elif mode == 'deep':
                return self.deep_research({'query': query, 'context': context})
            else:
                return format_response(
                    success=False,
                    message=f"Invalid research mode: {mode}"
                )
                
        except Exception as e:
            error_msg = self.error_messages.get('solve', 'Error in research: {error}')
            return self.error_handler.handle_error(
                e,
                {'request': request},
                error_msg.format(error=str(e))
            )
    
    def _add_to_research_history(self, mode: str, query: str, result: Dict[str, Any]) -> None:
        """
        Add research result to history.
        
        Args:
            mode: Research mode
            query: Research query
            result: Research result
        """
        history_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'mode': mode,
            'query': query,
            'success': result.get('success', False),
            'result_id': result.get('response_id', 'unknown')
        }
        
        self.research_history.append(history_entry)
        
        # Keep only last 50 research entries
        if len(self.research_history) > 50:
            self.research_history.pop(0)
        
        # Store in context
        self.context_manager.set_context(
            'research_history',
            self.research_history,
            ContextType.SESSION
        )
    
    def _get_available_methods(self) -> List[str]:
        """
        Get list of available research methods.
        
        Returns:
            List of available methods
        """
        return ['instant_research', 'quick_research', 'standard_research', 'deep_research', 'solve']
    
    def get_research_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get research history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of research history entries
        """
        history = self.research_history.copy()
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def get_current_mode(self) -> Optional[str]:
        """
        Get current research mode.
        
        Returns:
            Current mode or None
        """
        return self.current_mode
    
    def get_available_modes(self) -> List[str]:
        """
        Get available research modes.
        
        Returns:
            List of available modes
        """
        return WorkflowFactory.get_available_modes()
    
    def get_mode_description(self, mode: str) -> str:
        """
        Get description for a research mode.
        
        Args:
            mode: Research mode
            
        Returns:
            Mode description
        """
        return WorkflowFactory.get_mode_description(mode)
    
    def get_llm_service_status(self) -> Dict[str, Any]:
        """
        Get LLM service status.
        
        Returns:
            LLM service status
        """
        return self.llm_service.get_service_status()
    
    def test_research_capabilities(self) -> Dict[str, Any]:
        """
        Test research capabilities with sample queries.
        
        Returns:
            Test results
        """
        try:
            test_queries = {
                'instant': "What is artificial intelligence?",
                'quick': "How does machine learning work?",
                'standard': "What are the latest developments in AI research?",
                'deep': "Analyze the impact of AI on society and future implications"
            }
            
            test_results = {}
            
            for mode, query in test_queries.items():
                try:
                    workflow = WorkflowFactory.create_workflow(mode, self.llm_service)
                    result = workflow.execute(query)
                    test_results[mode] = {
                        'success': result.get('success', False),
                        'query': query,
                        'response_time': result.get('data', {}).get('workflow', {}).get('total_time', 0)
                    }
                except Exception as e:
                    test_results[mode] = {
                        'success': False,
                        'query': query,
                        'error': str(e)
                    }
            
            return format_response(
                success=True,
                data={
                    'test_results': test_results,
                    'llm_service_status': self.get_llm_service_status(),
                    'available_modes': self.get_available_modes()
                },
                message="Research capabilities test completed"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'component': 'test_capabilities'},
                "Error testing research capabilities"
            )
