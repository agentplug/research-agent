"""
Research Agent Package

A comprehensive research agent with multiple research modes, intelligent mode selection,
real LLM integration, source tracking, and temporary file management.
"""

from .research_agent.core import ResearchAgent
from .base_agent.core import BaseAgent
from .llm_service import LLMService, get_shared_llm_service
from .mode_selector import ModeSelector
from .source_tracker import SourceTracker
from .temp_file_manager import TempFileManager

__all__ = [
    # Main Agent
    'ResearchAgent',
    'BaseAgent',
    
    # LLM Service
    'LLMService',
    'get_shared_llm_service',
    
    # Phase 2 Components
    'ModeSelector',
    'SourceTracker',
    'TempFileManager',
]

__version__ = "2.0.0"
__author__ = "agentplug"
__description__ = "Deep research agent with Phase 2 LLM integration"
