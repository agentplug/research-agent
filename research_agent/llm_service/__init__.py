"""
LLM Service Module

This module provides the core LLM service functionality with AISuite integration
for unified access to multiple LLM providers.
"""

from .client_manager import ClientManager
from .llm_service import LLMService, get_shared_llm_service, reset_shared_llm_service
from .model_config import (
    IntermediateResult,
    ModelConfig,
    ModelInfo,
    ResearchData,
    SessionInfo,
    SourceInfo,
)
from .model_detector import ModelDetector

__all__ = [
    # Core LLM Service
    "LLMService",
    "get_shared_llm_service",
    "reset_shared_llm_service",
    # Components
    "ClientManager",
    "ModelDetector",
    "ModelConfig",
    # Data Classes
    "ModelInfo",
    "SourceInfo",
    "SessionInfo",
    "ResearchData",
    "IntermediateResult",
]

__version__ = "2.0.0"
__author__ = "agentplug"
__description__ = "LLM Service with AISuite integration for research agent"
