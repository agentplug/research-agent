"""
ResearchAgent - Simple research agent implementation.

This module provides the ResearchAgent class with clean, simple research methods.
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
from ..utils.utils import format_response, validate_input_data, sanitize_string, get_current_timestamp


class ResearchAgent(BaseAgent):
    """
    Simple research agent for conducting research in multiple modes.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        logger_name: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize ResearchAgent.
        
        Args:
            config: Configuration dictionary
            session_id: Optional session identifier
            logger_name: Optional logger name
            model: Specific LLM model to use
        """
        # Initialize base agent
        super().__init__(config, session_id, logger_name)
        
        # Initialize LLM service
        self.llm_service = get_shared_llm_service(config, model)
        
        # Initialize Phase 2 components
        self.mode_selector = ModeSelector(config)
        self.source_tracker = SourceTracker(config)
        self.temp_file_manager = TempFileManager(config)
        
        # Initialize research capabilities
        self._initialize_research_capabilities()
        
        self.current_mode = None
        self.research_history = []
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
    
    def instant_research(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Conduct instant research - single round quick answer.
        
        Args:
            query: Research query
            context: Additional context
            
        Returns:
            Research results
        """
        try:
            start_time = datetime.now()
            self.current_mode = 'instant'
            
            # Generate direct answer
            system_prompt = "You are a research assistant for INSTANT research mode. Provide quick, accurate answers based on available data. Focus on key facts and essential information."
            
            content = self.llm_service.generate(
                input_data=query,
                system_prompt=system_prompt,
                temperature=0.1
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = format_response(
                success=True,
                data={
                    'mode': 'instant',
                    'query': query,
                    'content': content,
                    'execution_time': round(execution_time, 2),
                    'research_rounds': 1,
                    'total_rounds': 1,
                    'sources_used': 0,
                    'context': context or {},
                    'timestamp': get_current_timestamp()
                },
                message="Instant research completed"
            )
            
            # Store in research history
            self.research_history.append({
                'mode': 'instant',
                'query': query,
                'result': result,
                'timestamp': get_current_timestamp()
            })
            
            return result
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'query': query, 'mode': 'instant'},
                f"Error conducting instant research: {str(e)}"
            )
    
    def quick_research(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Conduct quick research - 2 rounds with gap analysis.
        
        Args:
            query: Research query
            context: Additional context
            
        Returns:
            Research results
        """
        try:
            start_time = datetime.now()
            self.current_mode = 'quick'
            results = []
            
            # Round 1: Initial research
            system_prompt = "You are a research assistant for QUICK research mode. Provide enhanced analysis with context. Include relevant background information, explain key concepts and relationships, add practical examples when helpful."
            
            content = self.llm_service.generate(
                input_data=query,
                system_prompt=system_prompt,
                temperature=0.2
            )
            
            results.append({
                'round': 1,
                'query': query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            # Round 2: Gap analysis and follow-up
            analysis_prompt = f"""You are a research analyst. Analyze the research results and identify gaps.

Original Query: {query}
Round 1 Answer: {content[:400]}...

Identify what information is missing and generate a focused follow-up query. Return JSON:
{{"goal_reached": true/false, "next_query": "specific follow-up query"}}"""

            analysis_response = self.llm_service.generate(
                input_data=analysis_prompt,
                system_prompt="You are a research analyst specializing in gap analysis.",
                temperature=0.3,
                return_json=True
            )
            
            try:
                analysis = json.loads(analysis_response)
                if not analysis.get("goal_reached", False) and analysis.get("next_query"):
                    # Round 2: Follow-up research
                    followup_system_prompt = "You are a research assistant for QUICK research mode. Build upon previous research and address specific gaps. Focus on practical applications and ensure comprehensive coverage."
                    
                    followup_content = self.llm_service.generate(
                        input_data=analysis["next_query"],
                        system_prompt=followup_system_prompt,
                        temperature=0.2
                    )
                    
                    results.append({
                        'round': 2,
                        'query': analysis["next_query"],
                        'content': followup_content,
                        'timestamp': get_current_timestamp()
                    })
            except:
                # If JSON parsing fails, skip round 2
                pass
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Combine results
            combined_content = f"# Research Results ({len(results)} rounds)\n\n"
            for result in results:
                combined_content += f"## Round {result['round']}: {result['query']}\n\n"
                combined_content += f"{result['content']}\n\n"
            
            response = format_response(
                success=True,
                data={
                    'mode': 'quick',
                    'query': query,
                    'content': combined_content,
                    'rounds': results,
                    'execution_time': round(execution_time, 2),
                    'research_rounds': len(results),
                    'total_rounds': 2,
                    'sources_used': 0,
                    'context': context or {},
                    'timestamp': get_current_timestamp()
                },
                message=f"Quick research completed ({len(results)} rounds)"
            )
            
            # Store in research history
            self.research_history.append({
                'mode': 'quick',
                'query': query,
                'result': response,
                'timestamp': get_current_timestamp()
            })
            
            return response
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'query': query, 'mode': 'quick'},
                f"Error conducting quick research: {str(e)}"
            )
    
    def standard_research(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Conduct standard research - 3 rounds with comprehensive analysis.
        
        Args:
            query: Research query
            context: Additional context
            
        Returns:
            Research results
        """
        try:
            start_time = datetime.now()
            self.current_mode = 'standard'
            results = []
            
            # Round 1: Initial comprehensive research
            system_prompt = "You are a research assistant for STANDARD research mode. Conduct comprehensive analysis from multiple perspectives. Examine different viewpoints, include historical context, analyze current trends, and consider practical applications."
            
            content = self.llm_service.generate(
                input_data=query,
                system_prompt=system_prompt,
                temperature=0.2
            )
            
            results.append({
                'round': 1,
                'query': query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            # Multi-round loop for rounds 2-3
            for round_num in range(2, 4):
                research_summary = "\n".join([f"Round {r['round']}: {r['query']}\n{r['content'][:300]}..." for r in results])
                analysis_prompt = f"""You are a research analyst. Analyze the research progress and determine next action.

Original Query: {query}
Research Progress ({len(results)}/3 rounds completed):

{research_summary}

Return JSON:
{{"goal_reached": true/false, "next_query": "specific follow-up query", "reasoning": "explanation"}}"""

                analysis_response = self.llm_service.generate(
                    input_data=analysis_prompt,
                    system_prompt="You are a research analyst specializing in comprehensive research assessment.",
                    temperature=0.3,
                    return_json=True
                )
                
                try:
                    analysis = json.loads(analysis_response)
                    if analysis.get("goal_reached", False) or not analysis.get("next_query"):
                        break
                    
                    # Generate follow-up research
                    followup_system_prompt = f"You are a research assistant for STANDARD research mode. Build upon previous research and address specific gaps. Focus on: {analysis.get('reasoning', '')}. Provide deeper analysis and comprehensive coverage."
                    
                    followup_content = self.llm_service.generate(
                        input_data=analysis["next_query"],
                        system_prompt=followup_system_prompt,
                        temperature=0.2
                    )
                    
                    results.append({
                        'round': round_num,
                        'query': analysis["next_query"],
                        'content': followup_content,
                        'timestamp': get_current_timestamp()
                    })
                except:
                    break
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Combine results
            combined_content = f"# Comprehensive Research Results ({len(results)} rounds)\n\n"
            for result in results:
                combined_content += f"## Round {result['round']}: {result['query']}\n\n"
                combined_content += f"{result['content']}\n\n"
            
            response = format_response(
                success=True,
                data={
                    'mode': 'standard',
                    'query': query,
                    'content': combined_content,
                    'rounds': results,
                    'execution_time': round(execution_time, 2),
                    'research_rounds': len(results),
                    'total_rounds': 3,
                    'sources_used': 0,
                    'context': context or {},
                    'timestamp': get_current_timestamp()
                },
                message=f"Standard research completed ({len(results)} rounds)"
            )
            
            # Store in research history
            self.research_history.append({
                'mode': 'standard',
                'query': query,
                'result': response,
                'timestamp': get_current_timestamp()
            })
            
            return response
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'query': query, 'mode': 'standard'},
                f"Error conducting standard research: {str(e)}"
            )
    
    def deep_research(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Conduct deep research - 4 rounds with exhaustive analysis.
        
        Args:
            query: Research query
            context: Additional context
            
        Returns:
            Research results
        """
        try:
            start_time = datetime.now()
            self.current_mode = 'deep'
            results = []
            
            # Round 1: Foundation and overview
            system_prompt = "You are a research assistant for DEEP research mode. Provide comprehensive overview and foundation. Include detailed historical background, analyze multiple theoretical frameworks, examine fundamental concepts, and use professional academic language."
            
            content = self.llm_service.generate(
                input_data=query,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            results.append({
                'round': 1,
                'query': query,
                'content': content,
                'timestamp': get_current_timestamp()
            })
            
            # Multi-round loop for rounds 2-4
            for round_num in range(2, 5):
                research_summary = "\n".join([f"Round {r['round']}: {r['query']}\n{r['content'][:300]}..." for r in results])
                analysis_prompt = f"""You are a research analyst. Analyze the research progress and determine next action.

Original Query: {query}
Research Progress ({len(results)}/4 rounds completed):

{research_summary}

Return JSON:
{{"goal_reached": true/false, "next_query": "specific follow-up query", "reasoning": "explanation"}}"""

                analysis_response = self.llm_service.generate(
                    input_data=analysis_prompt,
                    system_prompt="You are a research analyst specializing in exhaustive research assessment.",
                    temperature=0.3,
                    return_json=True
                )
                
                try:
                    analysis = json.loads(analysis_response)
                    if analysis.get("goal_reached", False) or not analysis.get("next_query"):
                        break
                    
                    # Generate follow-up research
                    followup_system_prompt = f"You are a research assistant for DEEP research mode. Build upon previous research and address specific gaps. Focus on: {analysis.get('reasoning', '')}. Provide exhaustive, academic-level analysis with detailed case studies, controversies, debates, and critical evaluation."
                    
                    followup_content = self.llm_service.generate(
                        input_data=analysis["next_query"],
                        system_prompt=followup_system_prompt,
                        temperature=0.3
                    )
                    
                    results.append({
                        'round': round_num,
                        'query': analysis["next_query"],
                        'content': followup_content,
                        'timestamp': get_current_timestamp()
                    })
                except:
                    break
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Combine results
            combined_content = f"# Exhaustive Research Results ({len(results)} rounds)\n\n"
            for result in results:
                combined_content += f"## Round {result['round']}: {result['query']}\n\n"
                combined_content += f"{result['content']}\n\n"
            
            response = format_response(
                success=True,
                data={
                    'mode': 'deep',
                    'query': query,
                    'content': combined_content,
                    'rounds': results,
                    'execution_time': round(execution_time, 2),
                    'research_rounds': len(results),
                    'total_rounds': 4,
                    'sources_used': 0,
                    'context': context or {},
                    'timestamp': get_current_timestamp()
                },
                message=f"Deep research completed ({len(results)} rounds)"
            )
            
            # Store in research history
            self.research_history.append({
                'mode': 'deep',
                'query': query,
                'result': response,
                'timestamp': get_current_timestamp()
            })
            
            return response
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'query': query, 'mode': 'deep'},
                f"Error conducting deep research: {str(e)}"
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
        return ['instant', 'quick', 'standard', 'deep']
    
    def get_mode_description(self, mode: str) -> str:
        """
        Get description for a research mode.
        
        Args:
            mode: Research mode
            
        Returns:
            Mode description
        """
        descriptions = {
            'instant': 'Single round quick answer',
            'quick': '2 rounds with gap analysis',
            'standard': '3 rounds comprehensive analysis',
            'deep': '4 rounds exhaustive analysis'
        }
        return descriptions.get(mode, 'Unknown mode')
    
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
            
            # Test research methods
            for mode, query in test_queries.items():
                try:
                    if mode == 'instant':
                        result = self.instant_research(query)
                    elif mode == 'quick':
                        result = self.quick_research(query)
                    elif mode == 'standard':
                        result = self.standard_research(query)
                    elif mode == 'deep':
                        result = self.deep_research(query)
                    else:
                        continue
                        
                    test_results[mode] = {
                        'success': result.get('success', False),
                        'query': query,
                        'response_time': result.get('data', {}).get('execution_time', 0),
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
