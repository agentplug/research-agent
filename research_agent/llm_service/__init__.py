"""
LLM Service Module

This module provides the core LLM service functionality with AISuite integration
for unified access to multiple LLM providers.
"""

from .core import LLMService, get_shared_llm_service, reset_shared_llm_service
from .client_manager import ClientManager
from .model_detector import ModelDetector
from .model_config import ModelConfig, ModelInfo, SourceInfo, SessionInfo, ResearchData, IntermediateResult

__all__ = [
    # Core LLM Service
    'LLMService',
    'get_shared_llm_service',
    'reset_shared_llm_service',
    
    # Components
    'ClientManager',
    'ModelDetector',
    'ModelConfig',
    
    # Data Classes
    'ModelInfo',
    'SourceInfo',
    'SessionInfo',
    'ResearchData',
    'IntermediateResult',
]

__version__ = "2.0.0"
__author__ = "agentplug"
__description__ = "LLM Service with AISuite integration for research agent"
