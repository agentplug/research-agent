# LLM Service Module Implementation - Phase 1 Foundation

## Overview
The LLM Service module provides a reusable LLM service that can be used by any agent type. It supports multiple providers and auto-detects the best available model.

## Module Structure
```
src/llm_service/
├── __init__.py
├── core.py
├── providers.py
└── utils.py
```

## Files to Create/Modify

### `src/llm_service/__init__.py`
- Export CoreLLMService class
- Export get_shared_llm_service function
- Module initialization

### `src/llm_service/core.py`
- CoreLLMService class implementation
- LLM service core functionality
- Model detection and initialization
- Response generation

### `src/llm_service/providers.py`
- Provider implementations
- OpenAI integration
- Anthropic integration
- Google integration
- Local model support

### `src/llm_service/utils.py`
- Utility functions
- Model detection
- Configuration helpers
- Error handling

## Key Features Implemented

### CoreLLMService Class
- Multi-provider support
- Auto model detection
- Shared instance management
- Agent-type aware responses

### Provider Support
- OpenAI (GPT models)
- Anthropic (Claude models)
- Google (Gemini models)
- Local models (Ollama, LM Studio)

### Model Detection
- Automatic best model selection
- Fallback mechanisms
- Provider availability checking
- Model capability assessment

### Shared Instance Management
- Singleton pattern for efficiency
- Agent-type aware responses
- Configuration management
- Resource optimization

## Implementation Details

### CoreLLMService.__init__(self, model: str = None, agent_type: str = "generic")
- Initialize with model and agent type
- Set up provider
- Configure temperature and parameters
- Initialize client

### Model Detection
- `_detect_best_model() -> str`
- Check provider availability
- Select best available model
- Fallback to mock model

### Response Generation
- `generate(prompt: str, system_prompt: str = None, temperature: float = 0.0, **kwargs) -> str`
- `generate_analysis(question: str, data: List[str]) -> str`
- `generate_summary(text: str) -> str`
- `generate_questions(question: str, count: int = 3) -> str`

### Shared Instance Management
- `get_shared_llm_service(agent_type: str = "generic") -> CoreLLMService`
- Singleton pattern implementation
- Agent-type aware responses
- Resource sharing

## Testing
- Unit tests for all methods
- Provider integration tests
- Model detection tests
- Shared instance tests
- Error handling tests

## Dependencies
- Python 3.11+
- OpenAI API client
- Anthropic API client
- Google API client
- Local model clients
- JSON handling
