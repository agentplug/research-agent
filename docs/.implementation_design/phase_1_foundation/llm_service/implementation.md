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

## User Testing & Expectations - Phase 1 Foundation

### ✅ What You Should Be Able to Test

#### 1. LLM Service Initialization
```python
from llm_service import CoreLLMService, get_shared_llm_service

# Test basic initialization
service = CoreLLMService(agent_type="research")
assert service.agent_type == "research"
assert service.temperature == 0.0
assert service.model in ["gpt-4", "claude-3-sonnet", "gemini-pro", "llama2", "mock-model"]
```

#### 2. Model Detection
```python
# Test model detection
service = CoreLLMService()
model = service._detect_best_model()
assert model in ["gpt-4", "claude-3-sonnet", "gemini-pro", "llama2", "mock-model"]
print(f"Detected model: {model}")
```

#### 3. Response Generation
```python
# Test basic response generation
response = service.generate("What is artificial intelligence?", "You are a helpful assistant")
assert "Mock response" in response
assert "research" in response.lower()  # Agent-type aware

# Test analysis generation
analysis = service.generate_analysis("What is AI?", ["AI is artificial intelligence"])
assert "Mock analysis" in analysis
assert "research" in analysis.lower()

# Test summary generation
summary = service.generate_summary("Long text about artificial intelligence")
assert "Mock summary" in summary
assert "research" in summary.lower()

# Test question generation
questions = service.generate_questions("What is AI?", count=3)
assert "Mock questions" in questions
assert "research" in questions.lower()
```

#### 4. Shared Instance Management
```python
# Test shared instance
service1 = get_shared_llm_service("research")
service2 = get_shared_llm_service("research")
assert service1 is service2  # Same instance

# Test agent-type awareness
research_service = get_shared_llm_service("research")
coding_service = get_shared_llm_service("coding")

research_response = research_service.generate("Test prompt")
coding_response = coding_service.generate("Test prompt")

assert "research" in research_response.lower()
assert "coding" in coding_response.lower()
```

### ✅ What You Should Expect

#### 1. Working Mock LLM Service
- **Initialization**: CoreLLMService creates successfully with different parameters
- **Model Detection**: Automatically detects best available model or falls back to mock
- **Response Generation**: All methods return appropriate mock responses
- **Agent-Type Awareness**: Responses are customized based on agent type
- **Error Handling**: Graceful handling of various error scenarios

#### 2. Model Detection
- **Provider Checking**: Checks availability of different providers
- **Best Model Selection**: Selects most capable available model
- **Fallback Mechanism**: Falls back to mock model when no providers available
- **Configuration Handling**: Handles different provider configurations

#### 3. Shared Instance Management
- **Singleton Pattern**: Same instance returned for same agent type
- **Agent-Type Awareness**: Different instances for different agent types
- **Resource Sharing**: Efficient resource utilization
- **Configuration Management**: Proper configuration handling

#### 4. Provider Support
- **Multiple Providers**: Support for OpenAI, Anthropic, Google, Local models
- **Provider Availability**: Checks if providers are available
- **Fallback Mechanisms**: Graceful fallback when providers unavailable
- **Configuration**: Proper handling of provider configurations

### ✅ Manual Testing Commands

#### Test LLM Service Directly
```python
# Create test script: test_llm_service.py
from llm_service import CoreLLMService, get_shared_llm_service

def test_llm_service():
    # Test initialization
    service = CoreLLMService(agent_type="research")
    print(f"✓ Service initialized: {service.agent_type}")
    print(f"✓ Temperature: {service.temperature}")
    print(f"✓ Model: {service.model}")
    
    # Test model detection
    model = service._detect_best_model()
    print(f"✓ Detected model: {model}")
    
    # Test response generation
    response = service.generate("What is AI?", "You are a helpful assistant")
    print(f"✓ Response: {response[:50]}...")
    
    # Test specialized methods
    analysis = service.generate_analysis("What is AI?", ["AI is artificial intelligence"])
    print(f"✓ Analysis: {analysis[:50]}...")
    
    summary = service.generate_summary("Long text about AI")
    print(f"✓ Summary: {summary[:50]}...")
    
    questions = service.generate_questions("What is AI?", count=3)
    print(f"✓ Questions: {questions[:50]}...")
    
    # Test shared instance
    service1 = get_shared_llm_service("research")
    service2 = get_shared_llm_service("research")
    print(f"✓ Shared instance: {service1 is service2}")
    
    # Test agent-type awareness
    research_service = get_shared_llm_service("research")
    coding_service = get_shared_llm_service("coding")
    
    research_response = research_service.generate("Test prompt")
    coding_response = coding_service.generate("Test prompt")
    
    print(f"✓ Research response: {research_response[:50]}...")
    print(f"✓ Coding response: {coding_response[:50]}...")

if __name__ == "__main__":
    test_llm_service()
```

#### Expected Output
```
✓ Service initialized: research
✓ Temperature: 0.0
✓ Model: mock-model
✓ Detected model: mock-model
✓ Response: Mock response for research agent: What is AI?
✓ Analysis: Mock analysis for research agent: What is AI?
✓ Summary: Mock summary for research agent: Long text about AI
✓ Questions: Mock questions for research agent: What is AI?
✓ Shared instance: True
✓ Research response: Mock response for research agent: Test prompt
✓ Coding response: Mock response for coding agent: Test prompt
```

#### Test Provider Availability
```python
# Test provider availability checking
def test_provider_availability():
    service = CoreLLMService()
    
    # Test OpenAI availability
    openai_available = service._check_openai_availability()
    print(f"OpenAI available: {openai_available}")
    
    # Test Anthropic availability
    anthropic_available = service._check_anthropic_availability()
    print(f"Anthropic available: {anthropic_available}")
    
    # Test Google availability
    google_available = service._check_google_availability()
    print(f"Google available: {google_available}")
    
    # Test local availability
    local_available = service._check_local_availability()
    print(f"Local available: {local_available}")

if __name__ == "__main__":
    test_provider_availability()
```

### ✅ Success Criteria Checklist

- [ ] CoreLLMService initializes correctly with different parameters
- [ ] Model detection works and falls back appropriately
- [ ] All response generation methods work and return mock responses
- [ ] Shared instance management functions correctly
- [ ] Agent-type aware responses work properly
- [ ] Provider availability checking works
- [ ] Error handling works for various scenarios
- [ ] All tests pass
- [ ] Module can be imported and used by other modules
- [ ] Performance is acceptable for Phase 1 requirements
- [ ] Documentation is complete and accurate

## Dependencies
- Python 3.11+
- OpenAI API client
- Anthropic API client
- Google API client
- Local model clients
- JSON handling
