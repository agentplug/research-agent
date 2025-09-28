"""
Core LLM Service - AISuite Integration

This module provides the core LLM service interface with real LLM providers
using AISuite for unified provider access.
"""

import logging
from typing import Dict, Any, Optional, List

from .client_manager import ClientManager
from .model_detector import ModelDetector
from .model_config import ModelInfo
from ..base_agent.error_handler import ErrorHandler
from ..utils.utils import format_response

logger = logging.getLogger(__name__)

# Global shared instance (AgentHub pattern)
_shared_llm_service: Optional["LLMService"] = None


class LLMService:
    """
    LLM service with AISuite integration for real provider access.
    
    Features:
    - AISuite integration for unified provider access
    - Automatic model detection and selection
    - Multi-provider support (Ollama, LM Studio, OpenAI, Anthropic, etc.)
    - Shared instance management
    - Research mode-specific optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, model: Optional[str] = None):
        """
        Initialize LLM service.
        
        Args:
            config: Configuration dictionary
            model: Specific model to use (e.g., "ollama:llama3.1:8b")
        """
        self.config = config or {}
        self.error_handler = ErrorHandler("LLMService")
        
        # Initialize components
        self.model_detector = ModelDetector()
        self.client_manager = ClientManager()
        self.cache: Dict[str, Any] = {}
        self._model_info: Optional[ModelInfo] = None
        
        # Determine model to use
        if model:
            self.model = model
            logger.info(f"🎯 Using specified model: {model}")
        else:
            self.model = self.model_detector.detect_best_model()
            logger.info(f"🎯 Auto-selected model: {self.model}")
        
        # Initialize client
        self.client = self.client_manager.initialize_client(self.model)
        
        self.service_type = "real"
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
        Generate response using AISuite with research mode optimization.
        
        Args:
            query: Research query
            mode: Research mode (instant, quick, standard, deep)
            model: Model to use (overrides default)
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
            
            # Use specified model or current model
            active_model = model or self.model
            
            # Get mode-specific settings
            mode_settings = self._get_mode_settings(mode)
            temperature = temperature or mode_settings['temperature']
            max_tokens = max_tokens or mode_settings['max_tokens']
            
            # Build mode-specific prompt
            system_prompt = self._get_system_prompt(mode)
            user_prompt = self._build_user_prompt(query, mode)
            
            # Generate response using AISuite
            if self.client:
                try:
                    response = self.client.chat.completions.create(
                        model=self.client_manager.get_actual_model_name(active_model),
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens,
                        timeout=timeout or 30
                    )
                    
                    if hasattr(response, "choices") and response.choices:
                        content = str(response.choices[0].message.content)
                        
                        return format_response(
                            success=True,
                            data={
                                'content': content,
                                'model': active_model,
                                'mode': mode,
                                'query': query,
                                'provider': self._get_provider_name(active_model),
                                'metadata': {
                                    'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                                    'completion_tokens': getattr(response.usage, 'completion_tokens', 0),
                                    'total_tokens': getattr(response.usage, 'total_tokens', 0),
                                    'finish_reason': getattr(response.choices[0], 'finish_reason', 'unknown')
                                }
                            },
                            message=f"Real LLM response generated for {mode} research"
                        )
                    else:
                        logger.error(f"Invalid response format: {response}")
                        return format_response(
                            success=False,
                            message="Invalid response format from LLM provider"
                        )
                        
                except Exception as e:
                    logger.error(f"AISuite generation failed: {e}")
                    return format_response(
                        success=False,
                        message=f"LLM generation failed: {str(e)}"
                    )
            else:
                logger.error("No AISuite client available")
                return format_response(
                    success=False,
                    message="No LLM client available"
                )
                
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'query': query, 'mode': mode, 'model': model},
                f"Error generating LLM response: {str(e)}"
            )
    
    def _get_mode_settings(self, mode: str) -> Dict[str, Any]:
        """Get mode-specific settings."""
        mode_settings = {
            'instant': {'temperature': 0.1, 'max_tokens': 500},
            'quick': {'temperature': 0.2, 'max_tokens': 1000},
            'standard': {'temperature': 0.2, 'max_tokens': 1500},
            'deep': {'temperature': 0.3, 'max_tokens': 2000}
        }
        return mode_settings.get(mode, {'temperature': 0.2, 'max_tokens': 1000})
    
    def _get_system_prompt(self, mode: str) -> str:
        """Get system prompt for research mode."""
        system_prompts = {
            'instant': "You are a research assistant for INSTANT research mode. Provide quick, accurate answers based on available data. Focus on key facts and essential information.",
            'quick': "You are a research assistant for QUICK research mode. Analyze data and provide enhanced answers with context. Include relevant details and insights.",
            'standard': "You are a research assistant for STANDARD research mode. Conduct comprehensive research with multiple rounds of analysis. Provide thorough, well-structured responses.",
            'deep': "You are a research assistant for DEEP research mode. Conduct exhaustive research with clarification and comprehensive analysis. Provide detailed, well-researched responses with full context."
        }
        return system_prompts.get(mode, "You are a helpful research assistant.")
    
    def _build_user_prompt(self, query: str, mode: str) -> str:
        """Build user prompt for research mode."""
        mode_prompts = {
            'instant': f"Provide a concise, factual answer to: {query}",
            'quick': f"Provide enhanced analysis with context for: {query}",
            'standard': f"Conduct comprehensive research with multiple perspectives on: {query}",
            'deep': f"Conduct exhaustive research with academic-level analysis on: {query}"
        }
        return mode_prompts.get(mode, f"Answer: {query}")
    
    def _get_provider_name(self, model: str) -> str:
        """Get provider name from model identifier."""
        if ":" in model:
            return model.split(":")[0]
        return "unknown"
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get all available models."""
        try:
            return self.model_detector.list_available_models()
        except Exception as e:
            self.error_handler.log_error(e, {'component': 'get_models'})
            return []
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            'status': 'operational',
            'type': 'real',
            'model': self.model,
            'provider': self._get_provider_name(self.model),
            'is_local': self.model_detector.is_local_model(self.model),
            'client_available': self.client is not None,
            'initialized': self.initialized
        }
    
    def get_model_info(self) -> ModelInfo:
        """Get information about the current model."""
        if not self._model_info:
            self._model_info = self.model_detector.create_model_info(
                self.model, 
                is_local=self.model_detector.is_local_model(self.model)
            )
        return self._model_info


# Shared instance management (AgentHub pattern)
def get_shared_llm_service(
    config: Optional[Dict[str, Any]] = None,
    model: Optional[str] = None
) -> LLMService:
    """
    Get or create a shared LLM service instance.
    
    This prevents duplicate model detection and reduces initialization overhead.
    
    Args:
        config: Configuration dictionary
        model: Specific model to use
        
    Returns:
        Shared LLMService instance
    """
    global _shared_llm_service
    
    if _shared_llm_service is None:
        logger.debug("Created shared LLMService instance")
        _shared_llm_service = LLMService(config=config, model=model)
    else:
        logger.debug("Reusing shared LLMService instance")
    
    return _shared_llm_service


def reset_shared_llm_service() -> None:
    """Reset the shared LLM service instance."""
    global _shared_llm_service
    _shared_llm_service = None
    logger.debug("Reset shared LLMService instance")
