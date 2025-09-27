# LLM Service Implementation Design

## Overview

This document provides detailed implementation design for the LLM service module, based on the AgentHub LLM service pattern but simplified for the research agent's specific needs.

## Module Structure

```
src/llm_service/
├── __init__.py                 # Module initialization and exports
├── core.py                     # CoreLLMService implementation
├── client_manager.py           # AISuite client management
├── model_config.py             # Model configuration and constants
└── model_detector.py           # Model detection and selection
```

## Core Implementation

### 1. Core LLM Service (`core.py`)

```python
"""
LLM Service for Research Agent

A simplified LLM service based on AgentHub's pattern, providing:
- Automatic model detection and selection
- Multi-provider support (cloud + local)
- Standardized API for research operations
- Intelligent model scoring and fallbacks
- Comprehensive logging and debugging

Usage:
    from src.llm_service import get_shared_llm_service

    # Use shared instance (recommended)
    service = get_shared_llm_service()

    # Generate responses
    response = service.generate("Research question")
"""

import logging
from typing import Any, Optional, Dict, List
from datetime import datetime

from .client_manager import ClientManager
from .model_config import ModelInfo, ModelConfig
from .model_detector import ModelDetector

logger = logging.getLogger(__name__)

# Global shared instance
_shared_llm_service: Optional["CoreLLMService"] = None


class CoreLLMService:
    """
    LLM service for research agent operations.
    
    Features:
    - Automatic model detection and selection
    - Multi-provider support (Ollama, LM Studio, cloud providers)
    - Intelligent model scoring and fallbacks
    - Shared instance management
    - Research-specific optimizations
    """
    
    def __init__(self, model: Optional[str] = None, auto_detect: bool = True):
        """
        Initialize the LLM service.
        
        Args:
            model: Specific model to use (e.g., "ollama:gpt-oss:20b")
            auto_detect: Whether to auto-detect the best model if none specified
        """
        self.model_detector = ModelDetector()
        self.client_manager = ClientManager()
        self.cache: Dict[str, Any] = {}
        self._model_info: Optional[ModelInfo] = None
        
        # Determine model to use
        if model:
            self.model = model
            logger.info(f"🎯 Using specified model: {model}")
        elif auto_detect:
            self.model = self.model_detector.detect_best_model()
            logger.info(f"🎯 Selected model: {self.model}")
        else:
            self.model = "fallback"
            logger.info("🎯 Using fallback model")
        
        # Initialize client
        self.client = self.client_manager.initialize_client(self.model)
    
    def generate(
        self,
        input_data: str | List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        return_json: bool = False,
        temperature: float = 0.1,  # Lower temperature for research tasks
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate text using the LLM service.
        
        Args:
            input_data: Either a string (single prompt) or list of messages
            system_prompt: Optional system prompt to define AI behavior
            return_json: If True, request JSON response from LLM
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional parameters for the LLM
            
        Returns:
            Generated text response from LLM
        """
        if not self.client:
            return self._fallback_response()
        
        try:
            # Prepare request parameters
            request_kwargs = kwargs.copy()
            
            # Set research-optimized defaults
            request_kwargs["temperature"] = temperature
            if max_tokens:
                request_kwargs["max_tokens"] = max_tokens
            
            # Handle JSON response format for different providers
            if return_json:
                if self.is_local_model():
                    # For local models, ask for JSON in prompt
                    if isinstance(input_data, str):
                        input_data = (
                            f"{input_data}\n\nPlease respond with valid JSON only, "
                            "no additional text."
                        )
                    elif isinstance(input_data, list):
                        # Add JSON instruction to the last user message
                        if input_data and input_data[-1].get("role") == "user":
                            input_data[-1]["content"] += (
                                "\n\nPlease respond with valid JSON only, "
                                "no additional text."
                            )
                else:
                    # For cloud models, use response_format
                    request_kwargs["response_format"] = {"type": "json_object"}
            
            # Prepare messages
            if isinstance(input_data, str):
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": input_data})
            elif isinstance(input_data, list):
                messages = self._organize_messages(input_data, system_prompt)
            else:
                raise ValueError("input_data must be string or list")
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.client_manager.get_actual_model_name(self.model),
                messages=messages,
                **request_kwargs,
            )
            
            if hasattr(response, "choices") and response.choices:
                return str(response.choices[0].message.content)
            else:
                logger.error(f"Invalid response format: {response}")
                return self._fallback_response()
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._fallback_response()
    
    def generate_research_analysis(
        self, 
        question: str, 
        data: List[Dict[str, Any]], 
        analysis_type: str = "comprehensive"
    ) -> str:
        """
        Generate research analysis using specialized prompts.
        
        Args:
            question: Research question
            data: Retrieved data to analyze
            analysis_type: Type of analysis (comprehensive, gap_analysis, synthesis)
            
        Returns:
            Analysis result
        """
        system_prompts = {
            "comprehensive": self._get_comprehensive_analysis_prompt(),
            "gap_analysis": self._get_gap_analysis_prompt(),
            "synthesis": self._get_synthesis_prompt()
        }
        
        system_prompt = system_prompts.get(analysis_type, system_prompts["comprehensive"])
        
        # Format data for analysis
        formatted_data = self._format_data_for_analysis(data)
        
        prompt = f"""
Research Question: {question}

Data to Analyze:
{formatted_data}

Please provide a detailed analysis based on the above data.
"""
        
        return self.generate(prompt, system_prompt=system_prompt, temperature=0.1)
    
    def generate_clarification_questions(
        self, 
        question: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Generate clarification questions for deep research mode.
        
        Args:
            question: Original research question
            context: Optional context information
            
        Returns:
            List of clarification questions
        """
        system_prompt = self._get_clarification_prompt()
        
        context_str = ""
        if context:
            context_str = f"\nContext: {context}"
        
        prompt = f"""
Research Question: {question}{context_str}

Generate 3-5 clarification questions to better understand the research requirements.
Return as a JSON array of strings.
"""
        
        response = self.generate(prompt, system_prompt=system_prompt, return_json=True)
        
        try:
            import json
            questions = json.loads(response)
            if isinstance(questions, list):
                return questions
            else:
                return [questions]
        except (json.JSONDecodeError, TypeError):
            # Fallback: extract questions from text
            return self._extract_questions_from_text(response)
    
    def generate_follow_up_queries(
        self, 
        question: str, 
        gaps: List[str], 
        current_data: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate follow-up search queries based on identified gaps.
        
        Args:
            question: Original research question
            gaps: List of identified information gaps
            current_data: Currently available data
            
        Returns:
            List of follow-up search queries
        """
        system_prompt = self._get_follow_up_prompt()
        
        gaps_str = "\n".join(f"- {gap}" for gap in gaps)
        data_summary = self._summarize_data(current_data)
        
        prompt = f"""
Original Question: {question}

Current Data Summary:
{data_summary}

Identified Gaps:
{gaps_str}

Generate 3-5 specific search queries to address these gaps.
Return as a JSON array of strings.
"""
        
        response = self.generate(prompt, system_prompt=system_prompt, return_json=True)
        
        try:
            import json
            queries = json.loads(response)
            if isinstance(queries, list):
                return queries
            else:
                return [queries]
        except (json.JSONDecodeError, TypeError):
            # Fallback: extract queries from text
            return self._extract_queries_from_text(response)
    
    def _organize_messages(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Organize messages for LLM format."""
        organized_messages = []
        
        # Add system prompt if provided
        if system_prompt:
            organized_messages.append({"role": "system", "content": system_prompt})
        
        # Add user messages
        for message in messages:
            if message.get("role") in ["user", "assistant", "system"]:
                organized_messages.append(message)
        
        return organized_messages
    
    def _format_data_for_analysis(self, data: List[Dict[str, Any]]) -> str:
        """Format data for analysis prompts."""
        formatted_items = []
        for i, item in enumerate(data[:10], 1):  # Limit to first 10 items
            title = item.get('title', 'Untitled')
            content = item.get('content', '')[:500]  # Truncate content
            source = item.get('source', 'Unknown')
            
            formatted_items.append(f"""
{i}. {title}
   Source: {source}
   Content: {content}
""")
        
        return "\n".join(formatted_items)
    
    def _summarize_data(self, data: List[Dict[str, Any]]) -> str:
        """Create a summary of the data for context."""
        if not data:
            return "No data available"
        
        sources = set(item.get('source', 'Unknown') for item in data)
        total_items = len(data)
        
        return f"Total items: {total_items}, Sources: {', '.join(sources)}"
    
    def _extract_questions_from_text(self, text: str) -> List[str]:
        """Extract questions from text response."""
        import re
        questions = re.findall(r'\d+\.\s*(.+?\?)', text)
        return [q.strip() for q in questions if q.strip()]
    
    def _extract_queries_from_text(self, text: str) -> List[str]:
        """Extract search queries from text response."""
        import re
        queries = re.findall(r'\d+\.\s*(.+?)(?:\n|$)', text)
        return [q.strip() for q in queries if q.strip()]
    
    def _get_comprehensive_analysis_prompt(self) -> str:
        """Get system prompt for comprehensive analysis."""
        return """You are a research analyst. Analyze the provided data and provide:
1. Key findings and insights
2. Data quality assessment
3. Information gaps identified
4. Recommendations for further research
5. Overall assessment of research completeness

Be thorough, objective, and specific in your analysis."""
    
    def _get_gap_analysis_prompt(self) -> str:
        """Get system prompt for gap analysis."""
        return """You are a research analyst specializing in gap analysis. Identify:
1. Missing information that would be valuable
2. Areas where data is insufficient
3. Contradictions or inconsistencies
4. Specific questions that need answers
5. Sources that should be consulted

Be specific about what information is missing and why it's important."""
    
    def _get_synthesis_prompt(self) -> str:
        """Get system prompt for synthesis."""
        return """You are a research synthesizer. Combine information from multiple sources to:
1. Identify patterns and trends
2. Resolve contradictions
3. Create a coherent narrative
4. Highlight key insights
5. Provide a comprehensive answer

Focus on creating a unified understanding from diverse sources."""
    
    def _get_clarification_prompt(self) -> str:
        """Get system prompt for clarification questions."""
        return """You are a research assistant. Generate clarification questions to better understand research requirements. Focus on:
1. Scope and depth of research needed
2. Specific domains or fields of interest
3. Timeline and recency requirements
4. Perspective or viewpoint needed
5. Any specific constraints or preferences

Make questions specific and actionable."""
    
    def _get_follow_up_prompt(self) -> str:
        """Get system prompt for follow-up queries."""
        return """You are a research strategist. Generate specific search queries to address identified information gaps. Consider:
1. Different search terms and synonyms
2. Various source types (academic, news, web)
3. Different time periods or perspectives
4. Specific domains or fields
5. Related topics that might provide insights

Make queries specific, targeted, and likely to yield relevant results."""
    
    def get_model_info(self) -> ModelInfo:
        """Get information about the current model."""
        if not self._model_info:
            self._model_info = self._create_model_info()
        return self._model_info
    
    def _create_model_info(self) -> ModelInfo:
        """Create ModelInfo object for the current model."""
        return self.model_detector.create_model_info(
            self.model, is_local=self.is_local_model()
        )
    
    def get_current_model(self) -> str:
        """Get the current model identifier."""
        return self.model
    
    def is_local_model(self) -> bool:
        """Check if the current model is a local model."""
        return self.model.startswith(("ollama:", "lmstudio:"))
    
    def _fallback_response(self) -> str:
        """Provide fallback response when LLM is unavailable."""
        return "LLM service not available. Please check your configuration."
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the LLM service."""
        return {
            'model': self.model,
            'is_local': self.is_local_model(),
            'model_info': self.get_model_info().__dict__ if self._model_info else None,
            'cache_size': len(self.cache),
            'timestamp': datetime.utcnow().isoformat()
        }


# =============================================================================
# SHARED INSTANCE MANAGEMENT
# =============================================================================


def get_shared_llm_service(
    model: Optional[str] = None, 
    auto_detect: bool = True
) -> CoreLLMService:
    """
    Get or create a shared LLM service instance.
    
    This prevents duplicate model detection and reduces initialization overhead.
    
    Args:
        model: Specific model to use
        auto_detect: Whether to auto-detect model
        
    Returns:
        Shared CoreLLMService instance
    """
    global _shared_llm_service
    
    if _shared_llm_service is None:
        logger.debug("Created shared CoreLLMService instance")
        _shared_llm_service = CoreLLMService(model=model, auto_detect=auto_detect)
    else:
        logger.debug("Reusing shared CoreLLMService instance")
    
    return _shared_llm_service


def reset_shared_llm_service() -> None:
    """Reset the shared LLM service instance."""
    global _shared_llm_service
    _shared_llm_service = None
    logger.debug("Reset shared CoreLLMService instance")
```

### 2. Client Manager (`client_manager.py`)

```python
"""
AISuite Client Management for Research Agent LLM Service

This module handles the initialization and configuration of AISuite clients
for different LLM providers (cloud and local).
"""

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ClientManager:
    """Manages AISuite client initialization for different providers."""
    
    def __init__(self) -> None:
        """Initialize the client manager."""
        pass
    
    def initialize_client(self, model: str) -> Optional[Any]:
        """
        Initialize AISuite client for the given model.
        
        Args:
            model: Model identifier (e.g., "ollama:gpt-oss:20b")
            
        Returns:
            Initialized AISuite client or None if failed
        """
        try:
            import aisuite as ai  # type: ignore[import-untyped]
        except ImportError:
            logger.warning("AISuite not available, using fallback")
            return None
        
        if self._is_ollama_model(model):
            return self._initialize_ollama_client(model, ai)
        elif self._is_lmstudio_model(model):
            return self._initialize_lmstudio_client(model, ai)
        else:
            return self._initialize_cloud_client(model, ai)
    
    def _is_ollama_model(self, model: str) -> bool:
        """Check if model is an Ollama model."""
        return model.startswith("ollama:")
    
    def _is_lmstudio_model(self, model: str) -> bool:
        """Check if model is an LM Studio model."""
        return model.startswith("lmstudio:")
    
    def _initialize_ollama_client(self, model: str, ai: Any) -> Optional[Any]:
        """Initialize AISuite client for Ollama."""
        try:
            # Extract Ollama URL
            ollama_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
            
            # Configure provider configs for Ollama
            provider_configs = {
                "ollama": {
                    "api_url": ollama_url,
                    "timeout": 300,
                }
            }
            
            return ai.Client(provider_configs=provider_configs)
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            return None
    
    def _initialize_lmstudio_client(self, model: str, ai: Any) -> Optional[Any]:
        """Initialize AISuite client for LM Studio."""
        try:
            # Extract LM Studio URL
            lmstudio_url = os.getenv("LMSTUDIO_API_URL", "http://localhost:1234/v1")
            
            # Use OpenAI provider with custom base URL for LM Studio
            provider_configs = {
                "openai": {
                    "base_url": lmstudio_url,
                    "api_key": "lm-studio",  # LM Studio doesn't require real API key
                }
            }
            
            return ai.Client(provider_configs=provider_configs)
        except Exception as e:
            logger.error(f"Failed to initialize LM Studio client: {e}")
            return None
    
    def _initialize_cloud_client(self, model: str, ai: Any) -> Optional[Any]:
        """Initialize AISuite client for cloud providers."""
        try:
            # For cloud models, use standard initialization
            return ai.Client()
        except Exception as e:
            logger.error(f"Failed to initialize cloud client: {e}")
            return None
    
    def get_actual_model_name(self, model: str) -> str:
        """
        Get the actual model name to use with AISuite.
        
        Args:
            model: Model identifier (e.g., "ollama:gpt-oss:20b")
            
        Returns:
            Actual model name for AISuite (e.g., "gpt-oss:20b")
        """
        if self._is_ollama_model(model):
            # For Ollama, keep the full format
            return model
        elif self._is_lmstudio_model(model):
            # For LM Studio, strip the prefix and use OpenAI format
            model_name = model.replace("lmstudio:", "")
            return f"openai:{model_name}"
        else:
            # For cloud models, use as-is
            return model
```

### 3. Model Configuration (`model_config.py`)

```python
"""
Model Configuration for Research Agent LLM Service

This module contains configuration constants and data classes for model selection,
scoring, and management across different LLM providers.
"""

from dataclasses import dataclass
from typing import Any, Optional


class ModelConfig:
    """Configuration constants for model selection and scoring."""
    
    # Preferred models for research tasks (prioritize reasoning and analysis)
    PREFERRED_MODELS = [
        "gpt-oss:120b",      # OpenAI open-weight (highest priority)
        "gpt-oss:20b",       # OpenAI open-weight
        "deepseek-r1:70b",   # DeepSeek reasoning models
        "deepseek-r1:32b",   # DeepSeek reasoning models
        "qwen3:latest",      # Qwen models
        "qwen:latest",       # Qwen models
        "gemma:latest",      # General purpose models
        "llama3:latest",     # General purpose models
    ]
    
    # Cloud model providers and their models
    CLOUD_MODELS = {
        "openai": ["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
        "google": ["gemini-1.5-pro", "gemini-1.5-flash"],
        "deepseek": ["deepseek-chat", "deepseek-coder"],
        "groq": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant"],
        "mistral": ["mistral-large-latest", "mistral-small-latest"],
        "cohere": ["command-r-plus", "command-r"],
    }
    
    # Model size scoring (larger models get higher scores for research)
    SIZE_SCORES = {
        "1b": 5,
        "2b": 10,
        "3b": 15,
        "4b": 20,
        "7b": 25,
        "8b": 30,
        "13b": 40,
        "20b": 50,
        "32b": 60,
        "70b": 70,
        "120b": 80,
        "latest": 30,  # Default for "latest" models
    }
    
    # Model family scoring (research-optimized)
    FAMILY_SCORES = {
        "gpt-oss": 60,      # OpenAI open-weight models
        "deepseek": 70,     # DeepSeek reasoning models (excellent for research)
        "qwen": 65,         # Qwen models (good for research)
        "gemma": 50,        # General purpose
        "llama": 45,        # General purpose
        "mistral": 50,      # General purpose
        "claude": 60,       # Anthropic models
        "gpt": 55,          # OpenAI models
    }
    
    # Quality indicators that boost scores for research
    RESEARCH_QUALITY_INDICATORS = {
        "reasoning": 15,    # Reasoning models are excellent for research
        "thinking": 10,     # Thinking models
        "instruct": 5,      # Instruction-tuned models
        "chat": 3,          # Chat models
        "latest": 5,        # Latest versions
        "stable": 3,        # Stable versions
        "research": 10,     # Research-specific models
        "analysis": 8,      # Analysis-focused models
    }
    
    # Poor model indicators that reduce scores
    POOR_INDICATORS = {
        "embedding": -50,   # Embedding models are not for generation
        "instruct": -5,     # Some instruct models are outdated
        "old": -10,         # Old models
        "deprecated": -20,  # Deprecated models
        "tiny": -15,        # Very small models
        "test": -20,        # Test models
    }
    
    # Default URLs for local providers
    OLLAMA_URLS = [
        "http://localhost:11434",
        "http://127.0.0.1:11434",
        "http://0.0.0.0:11434",
    ]
    
    LMSTUDIO_URLS = [
        "http://localhost:1234/v1",
        "http://127.0.0.1:1234/v1",
        "http://0.0.0.0:1234/v1",
    ]
    
    # Research-specific model preferences
    RESEARCH_OPTIMIZED_MODELS = [
        "deepseek-r1:70b",  # Excellent for reasoning and analysis
        "deepseek-r1:32b",  # Good reasoning capabilities
        "gpt-oss:120b",     # Large open-weight model
        "gpt-oss:20b",      # Good open-weight model
        "qwen3:latest",     # Good for research tasks
    ]


@dataclass
class ModelInfo:
    """Data class for model information."""
    
    name: str
    provider: str
    size: Optional[str]
    family: Optional[str]
    score: int
    is_local: bool
    is_available: bool
    url: Optional[str] = None
    parameters: Optional[dict[str, Any]] = None
    research_score: Optional[int] = None  # Research-specific score
```

### 4. Model Detector (`model_detector.py`)

```python
"""
Model Detection and Selection for Research Agent LLM Service

This module handles automatic detection and selection of the best available
LLM model for research tasks.
"""

import logging
import os
from typing import List, Optional
import requests

from .model_config import ModelConfig, ModelInfo

logger = logging.getLogger(__name__)


class ModelDetector:
    """Detects and selects the best available LLM model for research tasks."""
    
    def __init__(self):
        """Initialize the model detector."""
        self.config = ModelConfig()
    
    def detect_best_model(self) -> str:
        """
        Detect the best available model for research tasks.
        
        Returns:
            Best available model identifier
        """
        # Check local models first (faster and more reliable)
        local_models = self._detect_local_models()
        if local_models:
            best_local = self._select_best_model(local_models)
            if best_local:
                logger.info(f"Selected local model: {best_local}")
                return best_local
        
        # Check cloud models
        cloud_models = self._detect_cloud_models()
        if cloud_models:
            best_cloud = self._select_best_model(cloud_models)
            if best_cloud:
                logger.info(f"Selected cloud model: {best_cloud}")
                return best_cloud
        
        # Fallback
        logger.warning("No suitable model found, using fallback")
        return "fallback"
    
    def _detect_local_models(self) -> List[ModelInfo]:
        """Detect available local models."""
        models = []
        
        # Check Ollama
        ollama_models = self._check_ollama_models()
        models.extend(ollama_models)
        
        # Check LM Studio
        lmstudio_models = self._check_lmstudio_models()
        models.extend(lmstudio_models)
        
        return models
    
    def _detect_cloud_models(self) -> List[ModelInfo]:
        """Detect available cloud models."""
        models = []
        
        # Check each cloud provider
        for provider, model_list in self.config.CLOUD_MODELS.items():
            for model in model_list:
                if self._check_cloud_model_availability(provider, model):
                    model_info = self._create_cloud_model_info(provider, model)
                    models.append(model_info)
        
        return models
    
    def _check_ollama_models(self) -> List[ModelInfo]:
        """Check available Ollama models."""
        models = []
        
        for url in self.config.OLLAMA_URLS:
            try:
                response = requests.get(f"{url}/api/tags", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    for model_data in data.get("models", []):
                        model_name = model_data.get("name", "")
                        if model_name:
                            model_info = self._create_ollama_model_info(model_name, url)
                            models.append(model_info)
                    break  # Use first available Ollama instance
            except Exception as e:
                logger.debug(f"Ollama check failed for {url}: {e}")
                continue
        
        return models
    
    def _check_lmstudio_models(self) -> List[ModelInfo]:
        """Check available LM Studio models."""
        models = []
        
        for url in self.config.LMSTUDIO_URLS:
            try:
                response = requests.get(f"{url}/v1/models", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    for model_data in data.get("data", []):
                        model_name = model_data.get("id", "")
                        if model_name:
                            model_info = self._create_lmstudio_model_info(model_name, url)
                            models.append(model_info)
                    break  # Use first available LM Studio instance
            except Exception as e:
                logger.debug(f"LM Studio check failed for {url}: {e}")
                continue
        
        return models
    
    def _check_cloud_model_availability(self, provider: str, model: str) -> bool:
        """Check if a cloud model is available."""
        # This is a simplified check - in practice, you'd check API keys and quotas
        api_key = os.getenv(f"{provider.upper()}_API_KEY")
        return api_key is not None
    
    def _create_ollama_model_info(self, model_name: str, url: str) -> ModelInfo:
        """Create ModelInfo for an Ollama model."""
        score = self._calculate_model_score(f"ollama:{model_name}")
        return ModelInfo(
            name=f"ollama:{model_name}",
            provider="ollama",
            size=self._extract_model_size(model_name),
            family=self._extract_model_family(model_name),
            score=score,
            is_local=True,
            is_available=True,
            url=url,
            research_score=self._calculate_research_score(f"ollama:{model_name}")
        )
    
    def _create_lmstudio_model_info(self, model_name: str, url: str) -> ModelInfo:
        """Create ModelInfo for an LM Studio model."""
        score = self._calculate_model_score(f"lmstudio:{model_name}")
        return ModelInfo(
            name=f"lmstudio:{model_name}",
            provider="lmstudio",
            size=self._extract_model_size(model_name),
            family=self._extract_model_family(model_name),
            score=score,
            is_local=True,
            is_available=True,
            url=url,
            research_score=self._calculate_research_score(f"lmstudio:{model_name}")
        )
    
    def _create_cloud_model_info(self, provider: str, model: str) -> ModelInfo:
        """Create ModelInfo for a cloud model."""
        score = self._calculate_model_score(model)
        return ModelInfo(
            name=model,
            provider=provider,
            size=self._extract_model_size(model),
            family=self._extract_model_family(model),
            score=score,
            is_local=False,
            is_available=True,
            research_score=self._calculate_research_score(model)
        )
    
    def _select_best_model(self, models: List[ModelInfo]) -> Optional[str]:
        """Select the best model from a list of available models."""
        if not models:
            return None
        
        # Sort by research score (if available) or regular score
        models.sort(key=lambda m: (m.research_score or m.score, m.score), reverse=True)
        
        return models[0].name
    
    def _calculate_model_score(self, model: str) -> int:
        """Calculate a score for a model based on various factors."""
        score = 0
        
        # Base score from size
        size = self._extract_model_size(model)
        if size:
            score += self.config.SIZE_SCORES.get(size, 0)
        
        # Family score
        family = self._extract_model_family(model)
        if family:
            score += self.config.FAMILY_SCORES.get(family, 0)
        
        # Quality indicators
        for indicator, points in self.config.RESEARCH_QUALITY_INDICATORS.items():
            if indicator in model.lower():
                score += points
        
        # Poor indicators
        for indicator, points in self.config.POOR_INDICATORS.items():
            if indicator in model.lower():
                score += points
        
        return max(score, 0)  # Ensure non-negative score
    
    def _calculate_research_score(self, model: str) -> int:
        """Calculate a research-specific score for a model."""
        base_score = self._calculate_model_score(model)
        
        # Boost for research-optimized models
        if any(research_model in model for research_model in self.config.RESEARCH_OPTIMIZED_MODELS):
            base_score += 20
        
        # Boost for reasoning models
        if "reasoning" in model.lower() or "r1" in model.lower():
            base_score += 15
        
        return base_score
    
    def _extract_model_size(self, model: str) -> Optional[str]:
        """Extract model size from model name."""
        import re
        
        # Look for size patterns like "7b", "13b", "70b", etc.
        size_match = re.search(r'(\d+)(b|billion)', model.lower())
        if size_match:
            return f"{size_match.group(1)}b"
        
        return None
    
    def _extract_model_family(self, model: str) -> Optional[str]:
        """Extract model family from model name."""
        model_lower = model.lower()
        
        # Check for known families
        for family in self.config.FAMILY_SCORES.keys():
            if family in model_lower:
                return family
        
        return None
    
    def create_model_info(self, model: str, is_local: bool = False) -> ModelInfo:
        """Create ModelInfo object for a given model."""
        score = self._calculate_model_score(model)
        research_score = self._calculate_research_score(model)
        
        return ModelInfo(
            name=model,
            provider=self._extract_provider(model),
            size=self._extract_model_size(model),
            family=self._extract_model_family(model),
            score=score,
            is_local=is_local,
            is_available=True,
            research_score=research_score
        )
    
    def _extract_provider(self, model: str) -> str:
        """Extract provider from model name."""
        if model.startswith("ollama:"):
            return "ollama"
        elif model.startswith("lmstudio:"):
            return "lmstudio"
        else:
            # Check cloud providers
            for provider in self.config.CLOUD_MODELS.keys():
                if provider in model.lower():
                    return provider
            return "unknown"
```

### 5. Module Initialization (`__init__.py`)

```python
"""
LLM Service Module for Research Agent

This module provides a unified interface for LLM operations in the research agent.
It uses AISuite to support multiple LLM providers with a consistent API.
"""

from .core import CoreLLMService, get_shared_llm_service, reset_shared_llm_service
from .client_manager import ClientManager
from .model_config import ModelConfig, ModelInfo
from .model_detector import ModelDetector

__version__ = "1.0.0"
__author__ = "agentplug"

__all__ = [
    "CoreLLMService",
    "ClientManager",
    "ModelConfig",
    "ModelDetector",
    "ModelInfo",
    "get_shared_llm_service",
    "reset_shared_llm_service",
]
```

## Key Features

### 1. Research-Optimized Design
- **Lower temperature defaults** (0.1) for more consistent research results
- **Research-specific prompts** for analysis, gap identification, and synthesis
- **Specialized methods** for research tasks like clarification questions and follow-up queries

### 2. Simplified Architecture
- **Removed unnecessary complexity** from AgentHub's version
- **Focused on research use cases** rather than general agent operations
- **Streamlined model detection** with research-specific scoring

### 3. External Tool Integration
- **No built-in tools** - users provide external tools through AgentHub
- **Focus on LLM operations** only
- **Clean separation** between LLM service and tool ecosystem

### 4. Shared Instance Management
- **Prevents duplicate initialization** across research operations
- **Efficient resource usage** for multiple research rounds
- **Consistent model selection** throughout research session

This LLM service implementation provides a solid foundation for the research agent's AI operations while maintaining simplicity and focus on research-specific needs.
