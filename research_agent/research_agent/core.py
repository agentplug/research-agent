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
from ..llm_service.core import LLMService, get_shared_llm_service
from ..mode_selector.core import ModeSelector
from ..source_tracker.core import SourceTracker
from ..temp_file_manager.core import TempFileManager
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
        logger_name: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize ResearchAgent with Phase 2 components.
        
        Args:
            config: Configuration dictionary
            session_id: Optional session identifier
            logger_name: Optional logger name
            model: Specific LLM model to use
        """
        # Initialize base agent
        super().__init__(config, session_id, logger_name)
        
        # Initialize Phase 2 components
        self.llm_service = get_shared_llm_service(config, model)
        self.mode_selector = ModeSelector(config)
        self.source_tracker = SourceTracker(config)
        self.temp_file_manager = TempFileManager(config)
        
        # Initialize temp file session
        self.temp_file_manager.initialize_session(self.session_id)
        
        # Research-specific configuration
        self.research_config = self.config.get('research', {})
        self.system_prompts = self.config.get('system_prompts', {})
        self.error_messages = self.config.get('error_messages', {})
        
        # Research state
        self.current_mode = None
        self.research_history = []
        self.active_research = None
        self.current_round = 0
        
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
            'llm_integration': True,
            'real_llm_providers': True,
            'intelligent_mode_selection': True,
            'source_tracking': True,
            'temp_file_management': True,
            'aisuite_integration': True,
            'model_detection': True,
            'url_deduplication': True,
            'reliability_scoring': True
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
        Solve a problem using intelligent mode selection.
        
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
                    'context': {'type': 'object'},
                    'auto_select_mode': {'type': 'boolean'}
                }
            }
            
            if not self.validate_request(request, schema):
                return format_response(
                    success=False,
                    message="Invalid request format for solve method"
                )
            
            query = sanitize_string(request['query'])
            context = request.get('context', {})
            auto_select_mode = request.get('auto_select_mode', True)
            
            # Intelligent mode selection if enabled
            if auto_select_mode:
                mode_selection = self.mode_selector.select_mode(query, context)
                if mode_selection['success']:
                    selected_mode = mode_selection['data']['selected_mode']
                    context['mode_selection'] = mode_selection['data']
                else:
                    selected_mode = request.get('mode', 'standard')  # Fallback
            else:
                selected_mode = request.get('mode', 'standard')
            
            # Store research data
            self.temp_file_manager.store_research_data(
                data={
                    'query': query,
                    'selected_mode': selected_mode,
                    'context': context,
                    'timestamp': datetime.utcnow().isoformat()
                },
                filename=f'research_query_{self.current_round}.json',
                data_type='research_data'
            )
            
            # Increment round counter
            self.current_round += 1
            
            # Route to appropriate research method
            if selected_mode == 'instant':
                return self.instant_research({'query': query, 'context': context})
            elif selected_mode == 'quick':
                return self.quick_research({'query': query, 'context': context})
            elif selected_mode == 'standard':
                return self.standard_research({'query': query, 'context': context})
            elif selected_mode == 'deep':
                return self.deep_research({'query': query, 'context': context})
            else:
                return format_response(
                    success=False,
                    message=f"Invalid research mode: {selected_mode}"
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
    
    def get_mode_selector_status(self) -> Dict[str, Any]:
        """Get mode selector status and configuration."""
        return {
            'enabled': self.mode_selector.enabled,
            'fallback_mode': self.mode_selector.fallback_mode,
            'validation_enabled': self.mode_selector.validation_enabled,
            'available_modes': self.mode_selector.modes
        }
    
    def get_source_tracker_status(self) -> Dict[str, Any]:
        """Get source tracker status and statistics."""
        return self.source_tracker.get_statistics()
    
    def get_temp_file_manager_status(self) -> Dict[str, Any]:
        """Get temp file manager status and statistics."""
        return self.temp_file_manager.get_statistics()
    
    def select_research_mode(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Select optimal research mode for a query.
        
        Args:
            query: Research query
            context: Additional context
            
        Returns:
            Mode selection result
        """
        return self.mode_selector.select_mode(query, context)
    
    def add_research_source(
        self,
        url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        source_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a research source to tracking.
        
        Args:
            url: Source URL
            title: Source title
            description: Source description
            source_type: Type of source
            metadata: Additional metadata
            
        Returns:
            Source addition result
        """
        return self.source_tracker.add_source(
            url=url,
            title=title,
            description=description,
            source_type=source_type,
            round_number=self.current_round,
            metadata=metadata
        )
    
    def get_research_sources(self, round_number: Optional[int] = None) -> Dict[str, Any]:
        """
        Get research sources.
        
        Args:
            round_number: Specific round number (optional)
            
        Returns:
            Sources data
        """
        if round_number is not None:
            return self.source_tracker.get_sources_for_round(round_number)
        else:
            return self.source_tracker.get_all_sources()
    
    def test_research_capabilities(self) -> Dict[str, Any]:
        """
        Test research capabilities with sample queries including Phase 2 components.
        
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
            
            # Test mode selection
            mode_selection_test = {}
            for mode, query in test_queries.items():
                try:
                    selection_result = self.mode_selector.select_mode(query)
                    mode_selection_test[mode] = {
                        'success': selection_result.get('success', False),
                        'selected_mode': selection_result.get('data', {}).get('selected_mode'),
                        'complexity_score': selection_result.get('data', {}).get('metadata', {}).get('complexity_score')
                    }
                except Exception as e:
                    mode_selection_test[mode] = {
                        'success': False,
                        'error': str(e)
                    }
            
            # Test research workflows
            for mode, query in test_queries.items():
                try:
                    workflow = WorkflowFactory.create_workflow(mode, self.llm_service)
                    result = workflow.execute(query)
                    test_results[mode] = {
                        'success': result.get('success', False),
                        'query': query,
                        'response_time': result.get('data', {}).get('workflow', {}).get('total_time', 0),
                        'model_used': result.get('data', {}).get('model'),
                        'provider': result.get('data', {}).get('provider')
                    }
                except Exception as e:
                    test_results[mode] = {
                        'success': False,
                        'query': query,
                        'error': str(e)
                    }
            
            # Test source tracking
            source_test = self.add_research_source(
                url="https://example.com/test-source",
                title="Test Source",
                description="Test source for capability testing",
                source_type="web"
            )
            
            return format_response(
                success=True,
                data={
                    'test_results': test_results,
                    'mode_selection_test': mode_selection_test,
                    'source_tracking_test': source_test,
                    'llm_service_status': self.get_llm_service_status(),
                    'mode_selector_status': self.get_mode_selector_status(),
                    'source_tracker_status': self.get_source_tracker_status(),
                    'temp_file_manager_status': self.get_temp_file_manager_status(),
                    'available_modes': self.get_available_modes(),
                    'phase_2_features': {
                        'real_llm_integration': True,
                        'intelligent_mode_selection': True,
                        'source_tracking': True,
                        'temp_file_management': True,
                        'aisuite_integration': True
                    }
                },
                message="Phase 2 research capabilities test completed"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'component': 'test_capabilities'},
                "Error testing research capabilities"
            )
