# LLM Service Module Implementation

## Overview
The LLM Service module provides a modular, multi-provider LLM service that supports OpenAI, Anthropic, Google, and local models. It includes auto-detection and fallback mechanisms.

## Files

### `__init__.py`
```python
"""
LLM Service module - Multi-provider LLM service
"""

from .core import LLMService, get_shared_llm_service
from .mock_service import MockLLMService
from .providers import OpenAIProvider, AnthropicProvider, GoogleProvider, LocalProvider

__all__ = [
    'LLMService', 'get_shared_llm_service', 'MockLLMService',
    'OpenAIProvider', 'AnthropicProvider', 'GoogleProvider', 'LocalProvider'
]
```

### `core.py` - LLMService Class
**Purpose**: Main LLM service with provider management

**Key Methods**:
- `__init__(model, temperature, max_tokens)` - Initialize service
- `generate(prompt, system_prompt, temperature)` - Generate text
- `generate_analysis(question, data)` - Generate analysis
- `generate_summary(text)` - Generate summary
- `generate_questions(question, count)` - Generate questions
- `_detect_best_model()` - Auto-detect best available model
- `_initialize_client()` - Initialize LLM client
- `get_service_info()` - Get service information

**Features**:
- Multi-provider support
- Auto-detection of best model
- Temperature control (0.0 for deterministic)
- Error handling and fallback
- Provider switching

### `mock_service.py` - Mock LLM Service
**Purpose**: Mock LLM service for testing and development

**Key Methods**:
- `__init__(agent_type)` - Initialize mock service
- `generate(prompt, system_prompt, temperature)` - Generate mock response
- `generate_analysis(question, data)` - Generate mock analysis
- `generate_summary(text)` - Generate mock summary
- `generate_questions(question, count)` - Generate mock questions
- `get_service_info()` - Get mock service info

**Features**:
- Deterministic mock responses
- Agent-type aware responses
- Temperature 0.0 for consistency
- All research mode support
- Testing and development use

### `providers/` - Provider Implementations

#### `__init__.py`
```python
"""
LLM Providers - Provider-specific implementations
"""

from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .google_provider import GoogleProvider
from .local_provider import LocalProvider

__all__ = ['OpenAIProvider', 'AnthropicProvider', 'GoogleProvider', 'LocalProvider']
```

#### `openai_provider.py` - OpenAI Provider
**Purpose**: OpenAI API integration

**Key Methods**:
- `generate(prompt, system_prompt, temperature)` - Generate with OpenAI
- `_validate_config()` - Validate OpenAI configuration
- `_get_available_models()` - Get available OpenAI models

#### `anthropic_provider.py` - Anthropic Provider
**Purpose**: Anthropic Claude API integration

**Key Methods**:
- `generate(prompt, system_prompt, temperature)` - Generate with Claude
- `_validate_config()` - Validate Anthropic configuration
- `_get_available_models()` - Get available Claude models

#### `google_provider.py` - Google Provider
**Purpose**: Google Gemini API integration

**Key Methods**:
- `generate(prompt, system_prompt, temperature)` - Generate with Gemini
- `_validate_config()` - Validate Google configuration
- `_get_available_models()` - Get available Gemini models

#### `local_provider.py` - Local Provider
**Purpose**: Local model integration (Ollama, LM Studio)

**Key Methods**:
- `generate(prompt, system_prompt, temperature)` - Generate with local model
- `_validate_config()` - Validate local configuration
- `_get_available_models()` - Get available local models

### `utils.py` - LLM Utilities
**Purpose**: LLM utility functions

**Key Methods**:
- `format_prompt(prompt, system_prompt)` - Format prompts
- `validate_response(response)` - Validate LLM responses
- `extract_json(response)` - Extract JSON from response
- `sanitize_prompt(prompt)` - Sanitize prompts
- `estimate_tokens(text)` - Estimate token count

## Usage Example
```python
from research_agent.llm_service import get_shared_llm_service

# Get shared LLM service
llm_service = get_shared_llm_service(agent_type="research")

# Generate response
response = llm_service.generate(
    prompt="What are the latest AI developments?",
    system_prompt="You are a research assistant.",
    temperature=0.0
)
```

## Configuration
```json
{
  "ai": {
    "temperature": 0.0,
    "max_tokens": null,
    "timeout": 30
  },
  "providers": {
    "openai": {
      "api_key": "your-openai-key",
      "model": "gpt-4"
    },
    "anthropic": {
      "api_key": "your-anthropic-key",
      "model": "claude-3-sonnet"
    }
  }
}
```

## Dependencies
- `openai` - OpenAI API client
- `anthropic` - Anthropic API client
- `google-generativeai` - Google Gemini API
- `requests` - HTTP requests for local models
- `json` - JSON handling
- `logging` - Logging
