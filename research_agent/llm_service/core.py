"""
Core LLM Service - Interface for LLM interactions.

This module provides the core LLM service interface that will be implemented
with real LLM providers in Phase 2, but uses mock service for Phase 1.
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from .mock_service import MockLLMService
from ..base_agent.error_handler import ErrorHandler
from ..utils.utils import format_response


class CoreLLMService(ABC):
    """
    Abstract base class for LLM service implementations.
    
    Defines the interface that all LLM service implementations must follow.
    """
    
    @abstractmethod
    def generate_response(
        self,
        query: str,
        mode: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate a response for a query.
        
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
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models.
        
        Returns:
            List of model information
        """
        pass
    
    @abstractmethod
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get service status.
        
        Returns:
            Service status information
        """
        pass


class LLMService(CoreLLMService):
    """
    LLM Service implementation using mock service for Phase 1.
    
    This will be replaced with real LLM implementations in Phase 2.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize LLM Service.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.error_handler = ErrorHandler("LLMService")
        
        # Initialize mock service for Phase 1
        self.mock_service = MockLLMService(config)
        
        # Service metadata
        self.service_type = "mock"  # Will be "real" in Phase 2
        self.initialized = True
    
    def generate_response(
        self,
        query: str,
        mode: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using the mock service.
        
        Args:
            query: Research query
            mode: Research mode
            model: Model to use
            temperature: Temperature setting
            max_tokens: Maximum tokens
            timeout: Timeout in seconds
            
        Returns:
            Response dictionary
        """
        try:
            # Validate inputs
            if not query or not isinstance(query, str):
                return format_response(
                    success=False,
                    message="Invalid query provided"
                )
            
            if mode not in ['instant', 'quick', 'standard', 'deep']:
                return format_response(
                    success=False,
                    message=f"Invalid mode '{mode}'. Must be one of: instant, quick, standard, deep"
                )
            
            # Use mock service for Phase 1
            return self.mock_service.generate_response(
                query=query,
                mode=mode,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'query': query, 'mode': mode, 'model': model},
                f"Error generating LLM response: {str(e)}"
            )
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from mock service.
        
        Returns:
            List of model information
        """
        try:
            return self.mock_service.get_available_models()
        except Exception as e:
            self.error_handler.log_error(e, {'component': 'get_models'})
            return []
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get service status from mock service.
        
        Returns:
            Service status information
        """
        try:
            status = self.mock_service.get_service_status()
            status['service_type'] = self.service_type
            status['initialized'] = self.initialized
            return status
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'component': 'get_status'},
                "Error getting service status"
            )
    
    def configure_service(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure the LLM service.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configuration confirmation
        """
        try:
            # Update configuration
            self.config.update(config)
            
            # Configure mock service if needed
            if 'error_rate' in config or 'timeout_rate' in config:
                self.mock_service.configure_error_simulation(
                    error_rate=config.get('error_rate'),
                    timeout_rate=config.get('timeout_rate')
                )
            
            return format_response(
                success=True,
                message="LLM service configured successfully",
                data={'config': self.config}
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'config': config},
                "Error configuring LLM service"
            )
    
    def test_service(self) -> Dict[str, Any]:
        """
        Test the LLM service with a simple query.
        
        Returns:
            Test result
        """
        try:
            test_query = "What is artificial intelligence?"
            test_response = self.generate_response(
                query=test_query,
                mode="instant",
                model="gpt-4"
            )
            
            return format_response(
                success=True,
                message="LLM service test completed",
                data={
                    'test_query': test_query,
                    'test_response': test_response,
                    'service_status': self.get_service_status()
                }
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'component': 'test_service'},
                "Error testing LLM service"
            )
