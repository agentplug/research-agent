"""
BaseAgent - Core agent class with common capabilities.

This module provides the BaseAgent class that serves as the foundation
for all agent implementations, including common capabilities and interfaces.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Union, Callable
from abc import ABC, abstractmethod
from datetime import datetime

from .context_manager import ContextManager, ContextType
from .error_handler import ErrorHandler, ErrorCategory
from ..utils.utils import (
    validate_input_data, format_response, sanitize_string,
    safe_json_loads, safe_json_dumps, merge_dicts
)


class BaseAgent(ABC):
    """
    Base agent class with common capabilities.
    
    Provides foundation functionality including context management,
    error handling, configuration, and standardized interfaces.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        logger_name: Optional[str] = None
    ):
        """
        Initialize BaseAgent.
        
        Args:
            config: Configuration dictionary
            session_id: Optional session identifier
            logger_name: Optional logger name
        """
        self.config = config or {}
        self.session_id = session_id
        self.logger_name = logger_name or self.__class__.__name__
        
        # Initialize core components
        self.context_manager = ContextManager(session_id)
        self.error_handler = ErrorHandler(self.logger_name)
        self.logger = logging.getLogger(self.logger_name)
        
        # Initialize agent state
        self._initialized = False
        self._capabilities = {}
        self._tools = {}
        
        # Initialize agent
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the agent with configuration and capabilities."""
        try:
            # Load configuration
            self._load_config()
            
            # Initialize capabilities
            self._initialize_capabilities()
            
            # Initialize tools
            self._initialize_tools()
            
            # Mark as initialized
            self._initialized = True
            
            self.logger.info(f"Agent {self.__class__.__name__} initialized successfully")
            
        except Exception as e:
            self.error_handler.log_error(e, {'component': 'initialization'})
            raise
    
    def _load_config(self) -> None:
        """Load and validate configuration."""
        # Set default configuration
        default_config = {
            'ai': {
                'temperature': 0.1,
                'max_tokens': None,
                'timeout': 30
            },
            'research': {
                'max_sources_per_round': 10,
                'max_rounds': 12,
                'timeout_per_round': 300
            }
        }
        
        # Merge with provided config
        self.config = merge_dicts(default_config, self.config)
        
        # Store in context
        self.context_manager.set_context(
            'agent_config',
            self.config,
            ContextType.SESSION
        )
    
    def _initialize_capabilities(self) -> None:
        """Initialize agent capabilities."""
        self._capabilities = {
            'context_management': True,
            'error_handling': True,
            'configuration': True,
            'logging': True,
            'session_management': True
        }
        
        # Store capabilities in context
        self.context_manager.set_context(
            'agent_capabilities',
            self._capabilities,
            ContextType.SESSION
        )
    
    def _initialize_tools(self) -> None:
        """Initialize available tools."""
        self._tools = {
            'get_context': self._tool_get_context,
            'set_context': self._tool_set_context,
            'clear_context': self._tool_clear_context,
            'get_metadata': self._tool_get_metadata,
            'set_metadata': self._tool_set_metadata
        }
    
    @abstractmethod
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request (to be implemented by subclasses).
        
        Args:
            request: Request dictionary
            
        Returns:
            Response dictionary
        """
        pass
    
    def validate_request(self, request: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        Validate a request against a schema.
        
        Args:
            request: Request to validate
            schema: Validation schema
            
        Returns:
            True if valid, False otherwise
        """
        try:
            return validate_input_data(request, schema)
        except Exception as e:
            self.error_handler.log_error(e, {'component': 'validation'})
            return False
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a request with error handling and logging.
        
        Args:
            request: Request dictionary
            
        Returns:
            Response dictionary
        """
        try:
            # Log request
            self.logger.info(f"Processing request: {request.get('method', 'unknown')}")
            
            # Add to conversation history
            self.context_manager.add_conversation_entry(
                'user',
                safe_json_dumps(request),
                {'request_type': 'agent_request'}
            )
            
            # Process the request
            response = self.process_request(request)
            
            # Add response to conversation history
            self.context_manager.add_conversation_entry(
                'assistant',
                safe_json_dumps(response),
                {'response_type': 'agent_response'}
            )
            
            return response
            
        except Exception as e:
            error_response = self.error_handler.handle_error(
                e,
                {'request': request},
                f"Error processing request: {str(e)}"
            )
            
            # Add error to conversation history
            self.context_manager.add_conversation_entry(
                'system',
                safe_json_dumps(error_response),
                {'response_type': 'error_response'}
            )
            
            return error_response
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities.
        
        Returns:
            Dictionary of capabilities
        """
        return self._capabilities.copy()
    
    def get_tools(self) -> Dict[str, Callable]:
        """
        Get available tools.
        
        Returns:
            Dictionary of tool functions
        """
        return self._tools.copy()
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get session information.
        
        Returns:
            Session information dictionary
        """
        return {
            'session_id': self.session_id,
            'agent_type': self.__class__.__name__,
            'initialized': self._initialized,
            'capabilities': self._capabilities,
            'context_summary': self.context_manager.get_context_summary(),
            'error_statistics': self.error_handler.get_error_statistics()
        }
    
    def reset_session(self) -> Dict[str, Any]:
        """
        Reset the session state.
        
        Returns:
            Reset confirmation response
        """
        try:
            # Clear context
            cleared_count = self.context_manager.clear_context()
            
            # Clear error history
            self.error_handler.clear_error_history()
            
            # Generate new session ID
            old_session_id = self.session_id
            self.session_id = self.context_manager.session_id
            
            self.logger.info(f"Session reset: {old_session_id} -> {self.session_id}")
            
            return format_response(
                success=True,
                message="Session reset successfully",
                data={
                    'old_session_id': old_session_id,
                    'new_session_id': self.session_id,
                    'cleared_context_entries': cleared_count
                }
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'component': 'session_reset'},
                "Error resetting session"
            )
    
    # Tool implementations
    def _tool_get_context(self, key: str, context_type: Optional[str] = None) -> Dict[str, Any]:
        """Tool: Get context value."""
        try:
            ctx_type = ContextType(context_type) if context_type else None
            value = self.context_manager.get_context(key, context_type=ctx_type)
            
            return format_response(
                success=True,
                data={'key': key, 'value': value, 'context_type': context_type}
            )
        except Exception as e:
            return self.error_handler.handle_error(e, {'tool': 'get_context'})
    
    def _tool_set_context(self, key: str, value: Any, context_type: str = 'session', ttl_seconds: Optional[int] = None) -> Dict[str, Any]:
        """Tool: Set context value."""
        try:
            ctx_type = ContextType(context_type)
            self.context_manager.set_context(key, value, ctx_type, ttl_seconds)
            
            return format_response(
                success=True,
                message=f"Context '{key}' set successfully",
                data={'key': key, 'context_type': context_type}
            )
        except Exception as e:
            return self.error_handler.handle_error(e, {'tool': 'set_context'})
    
    def _tool_clear_context(self, context_type: Optional[str] = None) -> Dict[str, Any]:
        """Tool: Clear context."""
        try:
            ctx_type = ContextType(context_type) if context_type else None
            cleared_count = self.context_manager.clear_context(ctx_type)
            
            return format_response(
                success=True,
                message=f"Cleared {cleared_count} context entries",
                data={'cleared_count': cleared_count, 'context_type': context_type}
            )
        except Exception as e:
            return self.error_handler.handle_error(e, {'tool': 'clear_context'})
    
    def _tool_get_metadata(self, key: str) -> Dict[str, Any]:
        """Tool: Get metadata value."""
        try:
            value = self.context_manager.get_metadata(key)
            
            return format_response(
                success=True,
                data={'key': key, 'value': value}
            )
        except Exception as e:
            return self.error_handler.handle_error(e, {'tool': 'get_metadata'})
    
    def _tool_set_metadata(self, key: str, value: Any) -> Dict[str, Any]:
        """Tool: Set metadata value."""
        try:
            self.context_manager.set_metadata(key, value)
            
            return format_response(
                success=True,
                message=f"Metadata '{key}' set successfully",
                data={'key': key}
            )
        except Exception as e:
            return self.error_handler.handle_error(e, {'tool': 'set_metadata'})
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(session_id={self.session_id}, initialized={self._initialized})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return (
            f"{self.__class__.__name__}("
            f"session_id={self.session_id}, "
            f"initialized={self._initialized}, "
            f"capabilities={len(self._capabilities)}, "
            f"tools={len(self._tools)})"
        )
