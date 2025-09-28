# LLM Service Implementation - Phase 2

## Overview

This document details the implementation of the enhanced LLM service for Phase 2, replacing the mock service with real LLM providers while maintaining the established interface from Phase 1.

## Current State (Phase 1)

The current LLM service implementation includes:
- `CoreLLMService` abstract base class
- `LLMService` concrete implementation using `MockLLMService`
- `MockLLMService` with realistic response patterns
- Consistent API interface for all research modes

## Phase 2 Enhancements

### 1. Provider Architecture

#### BaseProvider Abstract Class
```python
# research_agent/llm_service/providers/base_provider.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseProvider(ABC):
    """Base class for all LLM providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__.replace('Provider', '').lower()

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
        """Generate a response using this provider."""
        pass

    @abstractmethod
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models for this provider."""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to this provider."""
        pass

    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information."""
        return {
            'name': self.name,
            'config': self.config,
            'available': self.test_connection()
        }
```

#### Ollama Provider Implementation
```python
# research_agent/llm_service/providers/ollama.py
import requests
from typing import Dict, Any, List, Optional
from .base_provider import BaseProvider
from ...utils.utils import format_response

class OllamaProvider(BaseProvider):
    """Ollama provider implementation."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.default_model = config.get('default_model', 'llama3.1:8b')
        self.timeout = config.get('timeout', 60)

    def generate_response(
        self,
        query: str,
        mode: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Generate response using Ollama."""

        model = model or self.default_model
        timeout = timeout or self.timeout

        # Mode-specific prompt engineering
        prompt = self._build_prompt(query, mode)

        payload = {
            'model': model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': temperature or self._get_mode_temperature(mode),
                'num_predict': max_tokens or self._get_mode_tokens(mode)
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()

            result = response.json()
            content = result.get('response', '')

            return format_response(
                success=True,
                data={
                    'content': content,
                    'model': model,
                    'mode': mode,
                    'query': query,
                    'provider': 'ollama',
                    'metadata': {
                        'prompt_tokens': result.get('prompt_eval_count', 0),
                        'completion_tokens': result.get('eval_count', 0),
                        'total_tokens': result.get('prompt_eval_count', 0) + result.get('eval_count', 0),
                        'generation_time': result.get('total_duration', 0) / 1e9  # Convert nanoseconds to seconds
                    }
                },
                message=f"Ollama response generated for {mode} research"
            )

        except requests.exceptions.RequestException as e:
            return format_response(
                success=False,
                message=f"Ollama API error: {str(e)}",
                data={'provider': 'ollama', 'error': str(e)}
            )

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available Ollama models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()

            models_data = response.json()
            models = []

            for model_info in models_data.get('models', []):
                models.append({
                    'name': model_info['name'],
                    'size': model_info.get('size', 0),
                    'modified_at': model_info.get('modified_at'),
                    'provider': 'ollama',
                    'available': True
                })

            return models

        except requests.exceptions.RequestException:
            return []

    def test_connection(self) -> bool:
        """Test connection to Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def _build_prompt(self, query: str, mode: str) -> str:
        """Build mode-specific prompt."""
        mode_prompts = {
            'instant': f"Provide a concise, factual answer to: {query}",
            'quick': f"Provide enhanced analysis with context for: {query}",
            'standard': f"Conduct comprehensive research with multiple perspectives on: {query}",
            'deep': f"Conduct exhaustive research with academic-level analysis on: {query}"
        }
        return mode_prompts.get(mode, f"Answer: {query}")

    def _get_mode_temperature(self, mode: str) -> float:
        """Get temperature setting for mode."""
        temperatures = {
            'instant': 0.1,
            'quick': 0.2,
            'standard': 0.2,
            'deep': 0.3
        }
        return temperatures.get(mode, 0.2)

    def _get_mode_tokens(self, mode: str) -> int:
        """Get token limit for mode."""
        token_limits = {
            'instant': 500,
            'quick': 1000,
            'standard': 1500,
            'deep': 2000
        }
        return token_limits.get(mode, 1000)
```

#### OpenAI Provider Implementation
```python
# research_agent/llm_service/providers/openai.py
import openai
from typing import Dict, Any, List, Optional
from .base_provider import BaseProvider
from ...utils.utils import format_response

class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.default_model = config.get('default_model', 'gpt-4')
        self.timeout = config.get('timeout', 30)

        if self.api_key:
            openai.api_key = self.api_key

    def generate_response(
        self,
        query: str,
        mode: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Generate response using OpenAI."""

        if not self.api_key:
            return format_response(
                success=False,
                message="OpenAI API key not configured",
                data={'provider': 'openai', 'error': 'missing_api_key'}
            )

        model = model or self.default_model
        timeout = timeout or self.timeout

        # Mode-specific prompt engineering
        prompt = self._build_prompt(query, mode)

        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(mode)},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature or self._get_mode_temperature(mode),
                max_tokens=max_tokens or self._get_mode_tokens(mode),
                timeout=timeout
            )

            content = response.choices[0].message.content

            return format_response(
                success=True,
                data={
                    'content': content,
                    'model': model,
                    'mode': mode,
                    'query': query,
                    'provider': 'openai',
                    'metadata': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens,
                        'finish_reason': response.choices[0].finish_reason
                    }
                },
                message=f"OpenAI response generated for {mode} research"
            )

        except Exception as e:
            return format_response(
                success=False,
                message=f"OpenAI API error: {str(e)}",
                data={'provider': 'openai', 'error': str(e)}
            )

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available OpenAI models."""
        models = [
            {'name': 'gpt-4', 'provider': 'openai', 'available': True},
            {'name': 'gpt-4-turbo', 'provider': 'openai', 'available': True},
            {'name': 'gpt-3.5-turbo', 'provider': 'openai', 'available': True},
            {'name': 'gpt-3.5-turbo-16k', 'provider': 'openai', 'available': True}
        ]
        return models

    def test_connection(self) -> bool:
        """Test connection to OpenAI."""
        if not self.api_key:
            return False

        try:
            openai.Model.list()
            return True
        except Exception:
            return False

    def _build_prompt(self, query: str, mode: str) -> str:
        """Build mode-specific prompt."""
        mode_prompts = {
            'instant': f"Provide a concise, factual answer to: {query}",
            'quick': f"Provide enhanced analysis with context for: {query}",
            'standard': f"Conduct comprehensive research with multiple perspectives on: {query}",
            'deep': f"Conduct exhaustive research with academic-level analysis on: {query}"
        }
        return mode_prompts.get(mode, f"Answer: {query}")

    def _get_system_prompt(self, mode: str) -> str:
        """Get system prompt for mode."""
        system_prompts = {
            'instant': "You are a research assistant for INSTANT research mode. Provide quick, accurate answers based on available data. Focus on key facts and essential information.",
            'quick': "You are a research assistant for QUICK research mode. Analyze data and provide enhanced answers with context. Include relevant details and insights.",
            'standard': "You are a research assistant for STANDARD research mode. Conduct comprehensive research with multiple rounds of analysis. Provide thorough, well-structured responses.",
            'deep': "You are a research assistant for DEEP research mode. Conduct exhaustive research with clarification and comprehensive analysis. Provide detailed, well-researched responses with full context."
        }
        return system_prompts.get(mode, "You are a helpful research assistant.")

    def _get_mode_temperature(self, mode: str) -> float:
        """Get temperature setting for mode."""
        temperatures = {
            'instant': 0.1,
            'quick': 0.2,
            'standard': 0.2,
            'deep': 0.3
        }
        return temperatures.get(mode, 0.2)

    def _get_mode_tokens(self, mode: str) -> int:
        """Get token limit for mode."""
        token_limits = {
            'instant': 500,
            'quick': 1000,
            'standard': 1500,
            'deep': 2000
        }
        return token_limits.get(mode, 1000)
```

### 2. Model Detection and Selection

#### ModelDetector Implementation
```python
# research_agent/llm_service/model_detector.py
from typing import Dict, Any, List, Optional
from .providers.base_provider import BaseProvider

class ModelDetector:
    """Intelligent model detection and selection."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mode_preferences = config.get('mode_preferences', {})

    def select_model(
        self,
        mode: str,
        query: str,
        available_models: List[str],
        provider: BaseProvider
    ) -> str:
        """Select optimal model based on mode, query, and available models."""

        # Get mode-specific preferences
        preferred_models = self.mode_preferences.get(mode, [])

        # Filter to available models
        available_preferred = [m for m in preferred_models if m in available_models]

        if available_preferred:
            return available_preferred[0]

        # Fallback to first available model
        if available_models:
            return available_models[0]

        # Fallback to provider default
        return provider.default_model

    def analyze_query_complexity(self, query: str) -> int:
        """Analyze query complexity to influence model selection."""
        complexity_indicators = {
            'comprehensive': 3,
            'exhaustive': 3,
            'detailed analysis': 3,
            'thorough': 2,
            'analysis': 2,
            'research': 2,
            'investigation': 2,
            'study': 2,
            'explain': 1,
            'describe': 1,
            'what is': 0,
            'how': 1
        }

        query_lower = query.lower()
        score = 0

        for indicator, weight in complexity_indicators.items():
            if indicator in query_lower:
                score += weight

        return min(score, 5)  # Cap at 5

    def get_model_recommendations(self, mode: str) -> List[str]:
        """Get recommended models for a research mode."""
        recommendations = {
            'instant': ['gpt-3.5-turbo', 'claude-3-haiku', 'llama3.1:8b'],
            'quick': ['gpt-4', 'claude-3-sonnet', 'llama3.1:70b'],
            'standard': ['gpt-4', 'claude-3-opus', 'llama3.1:70b'],
            'deep': ['gpt-4', 'claude-3-opus', 'llama3.1:70b']
        }
        return recommendations.get(mode, ['gpt-3.5-turbo'])
```

### 3. Enhanced Core LLM Service

#### Updated LLMService Implementation
```python
# research_agent/llm_service/core.py (enhanced)
from typing import Dict, Any, Optional, List
from .providers.ollama import OllamaProvider
from .providers.openai import OpenAIProvider
from .providers.anthropic import AnthropicProvider
from .model_detector import ModelDetector
from .mock_service import MockLLMService  # Keep for fallback
from ..base_agent.error_handler import ErrorHandler
from ..utils.utils import format_response

class LLMService:
    """Enhanced LLM service with real providers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.error_handler = ErrorHandler("LLMService")

        # Initialize providers
        self.providers = {}
        self._initialize_providers()

        # Initialize model detector
        self.model_detector = ModelDetector(self.config.get('llm', {}))

        # Fallback order
        self.fallback_order = self.config.get('llm', {}).get('fallback_order', ['ollama', 'openai', 'anthropic'])

        # Keep mock service as ultimate fallback
        self.mock_service = MockLLMService(config)

        self.service_type = "real"  # Now using real providers
        self.initialized = True

    def _initialize_providers(self):
        """Initialize available providers."""
        llm_config = self.config.get('llm', {})
        providers_config = llm_config.get('providers', {})

        # Initialize Ollama provider
        if 'ollama' in providers_config:
            try:
                self.providers['ollama'] = OllamaProvider(providers_config['ollama'])
            except Exception as e:
                self.error_handler.log_error(e, {'provider': 'ollama'})

        # Initialize OpenAI provider
        if 'openai' in providers_config:
            try:
                self.providers['openai'] = OpenAIProvider(providers_config['openai'])
            except Exception as e:
                self.error_handler.log_error(e, {'provider': 'openai'})

        # Initialize Anthropic provider
        if 'anthropic' in providers_config:
            try:
                self.providers['anthropic'] = AnthropicProvider(providers_config['anthropic'])
            except Exception as e:
                self.error_handler.log_error(e, {'provider': 'anthropic'})

    def generate_response(
        self,
        query: str,
        mode: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Generate response with provider fallback."""

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

        # Try providers in fallback order
        last_error = None

        for provider_name in self.fallback_order:
            if provider_name not in self.providers:
                continue

            provider = self.providers[provider_name]

            # Test connection first
            if not provider.test_connection():
                self.error_handler.log_error(
                    Exception(f"Provider {provider_name} not available"),
                    {'provider': provider_name, 'query': query, 'mode': mode}
                )
                continue

            try:
                # Get available models for this provider
                available_models = [m['name'] for m in provider.get_available_models()]

                # Select optimal model
                selected_model = self.model_detector.select_model(
                    mode, query, available_models, provider
                )

                # Generate response
                response = provider.generate_response(
                    query=query,
                    mode=mode,
                    model=selected_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout
                )

                if response.get('success'):
                    return response
                else:
                    last_error = Exception(response.get('message', 'Provider error'))

            except Exception as e:
                last_error = e
                self.error_handler.log_error(e, {
                    'provider': provider_name,
                    'query': query,
                    'mode': mode
                })
                continue

        # All real providers failed, fallback to mock service
        self.error_handler.log_error(
            last_error or Exception("All providers failed"),
            {'query': query, 'mode': mode},
            "Falling back to mock service"
        )

        return self.mock_service.generate_response(
            query=query,
            mode=mode,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get all available models from all providers."""
        all_models = []

        for provider_name, provider in self.providers.items():
            try:
                if provider.test_connection():
                    models = provider.get_available_models()
                    all_models.extend(models)
            except Exception as e:
                self.error_handler.log_error(e, {'provider': provider_name})

        return all_models

    def get_service_status(self) -> Dict[str, Any]:
        """Get service status with provider information."""
        provider_status = {}

        for provider_name, provider in self.providers.items():
            provider_status[provider_name] = provider.get_provider_info()

        return {
            'status': 'operational',
            'type': 'real',
            'providers': provider_status,
            'fallback_order': self.fallback_order,
            'mock_fallback_available': True,
            'initialized': self.initialized
        }
```

## Configuration Updates

### Enhanced config.json
```json
{
  "ai": {
    "temperature": 0.1,
    "max_tokens": null,
    "timeout": 30
  },
  "research": {
    "max_sources_per_round": 10,
    "max_rounds": 12,
    "timeout_per_round": 300
  },
  "llm": {
    "default_provider": "ollama",
    "fallback_order": ["ollama", "openai", "anthropic"],
    "mode_preferences": {
      "instant": ["gpt-3.5-turbo", "claude-3-haiku", "llama3.1:8b"],
      "quick": ["gpt-4", "claude-3-sonnet", "llama3.1:70b"],
      "standard": ["gpt-4", "claude-3-opus", "llama3.1:70b"],
      "deep": ["gpt-4", "claude-3-opus", "llama3.1:70b"]
    },
    "providers": {
      "ollama": {
        "base_url": "http://localhost:11434",
        "default_model": "llama3.1:8b",
        "timeout": 60
      },
      "openai": {
        "api_key": "${OPENAI_API_KEY}",
        "default_model": "gpt-4",
        "timeout": 30
      },
      "anthropic": {
        "api_key": "${ANTHROPIC_API_KEY}",
        "default_model": "claude-3-sonnet",
        "timeout": 30
      }
    },
    "mode_settings": {
      "instant": {"temperature": 0.1, "max_tokens": 500},
      "quick": {"temperature": 0.2, "max_tokens": 1000},
      "standard": {"temperature": 0.2, "max_tokens": 1500},
      "deep": {"temperature": 0.3, "max_tokens": 2000}
    }
  },
  "system_prompts": {
    "instant": "You are a research assistant for INSTANT research mode. Provide quick, accurate answers based on available data. Focus on key facts and essential information.",
    "quick": "You are a research assistant for QUICK research mode. Analyze data and provide enhanced answers with context. Include relevant details and insights.",
    "standard": "You are a research assistant for STANDARD research mode. Conduct comprehensive research with multiple rounds of analysis. Provide thorough, well-structured responses.",
    "deep": "You are a research assistant for DEEP research mode. Conduct exhaustive research with clarification and comprehensive analysis. Provide detailed, well-researched responses with full context."
  },
  "error_messages": {
    "instant_research": "Error conducting instant research: {error}",
    "quick_research": "Error conducting quick research: {error}",
    "standard_research": "Error conducting standard research: {error}",
    "deep_research": "Error conducting deep research: {error}",
    "solve": "Error in research: {error}"
  }
}
```

## Testing Strategy

### Unit Tests
```python
# tests/test_llm_service_phase2.py
import unittest
from unittest.mock import Mock, patch
from research_agent.llm_service.core import LLMService
from research_agent.llm_service.providers.ollama import OllamaProvider
from research_agent.llm_service.providers.openai import OpenAIProvider

class TestLLMServicePhase2(unittest.TestCase):
    """Test enhanced LLM service with real providers."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'llm': {
                'fallback_order': ['ollama', 'openai'],
                'providers': {
                    'ollama': {
                        'base_url': 'http://localhost:11434',
                        'default_model': 'llama3.1:8b'
                    },
                    'openai': {
                        'api_key': 'test-key',
                        'default_model': 'gpt-4'
                    }
                }
            }
        }
        self.llm_service = LLMService(self.config)

    def test_provider_initialization(self):
        """Test provider initialization."""
        self.assertIn('ollama', self.llm_service.providers)
        self.assertIn('openai', self.llm_service.providers)

    @patch('requests.post')
    def test_ollama_provider(self, mock_post):
        """Test Ollama provider."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': 'Test response',
            'eval_count': 100,
            'prompt_eval_count': 50,
            'total_duration': 1000000000
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        provider = OllamaProvider(self.config['llm']['providers']['ollama'])
        result = provider.generate_response("Test query", "instant")

        self.assertTrue(result['success'])
        self.assertEqual(result['data']['content'], 'Test response')
        self.assertEqual(result['data']['provider'], 'ollama')

    @patch('openai.ChatCompletion.create')
    def test_openai_provider(self, mock_create):
        """Test OpenAI provider."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'Test response'
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 100
        mock_response.usage.total_tokens = 150
        mock_response.choices[0].finish_reason = 'stop'
        mock_create.return_value = mock_response

        provider = OpenAIProvider(self.config['llm']['providers']['openai'])
        result = provider.generate_response("Test query", "instant")

        self.assertTrue(result['success'])
        self.assertEqual(result['data']['content'], 'Test response')
        self.assertEqual(result['data']['provider'], 'openai')

    def test_fallback_mechanism(self):
        """Test provider fallback mechanism."""
        # Mock all providers to fail
        for provider in self.llm_service.providers.values():
            provider.test_connection = Mock(return_value=False)

        result = self.llm_service.generate_response("Test query", "instant")

        # Should fallback to mock service
        self.assertTrue(result['success'])
        self.assertIn('Mock response', result['data']['content'])

    def test_model_detection(self):
        """Test model detection."""
        available_models = ['gpt-4', 'gpt-3.5-turbo', 'llama3.1:8b']

        # Test instant mode
        model = self.llm_service.model_detector.select_model(
            'instant', 'What is AI?', available_models,
            self.llm_service.providers['openai']
        )
        self.assertIn(model, available_models)

        # Test deep mode
        model = self.llm_service.model_detector.select_model(
            'deep', 'Comprehensive analysis of AI', available_models,
            self.llm_service.providers['openai']
        )
        self.assertIn(model, available_models)
```

## Success Criteria

- [ ] Real LLM responses replace mock responses
- [ ] Multiple providers (Ollama, OpenAI, Anthropic) are supported
- [ ] Provider fallback mechanism works correctly
- [ ] Model detection selects appropriate models for each mode
- [ ] Error handling gracefully manages provider failures
- [ ] Backward compatibility maintained with Phase 1 interface
- [ ] All existing tests pass with real LLM integration
- [ ] Configuration supports multiple providers and fallback order
- [ ] Mode-specific prompts and settings are applied correctly

## Implementation Order

1. **Create provider base class and interfaces**
2. **Implement Ollama provider**
3. **Implement OpenAI provider**
4. **Implement Anthropic provider**
5. **Create model detector**
6. **Enhance core LLM service with multi-provider support**
7. **Update configuration**
8. **Write comprehensive tests**
9. **Test with real providers**
10. **Update documentation and examples**
