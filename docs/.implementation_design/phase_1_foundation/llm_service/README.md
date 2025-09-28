# LLM Service Module - Phase 1 Foundation

## Overview

The LLM Service module provides a simplified LLM service for the research agent, initially using mock responses for testing and validation in Phase 1.

## Module Structure

```
research_agent/llm_service/
├── __init__.py                 # Module initialization and exports
├── core.py                     # Mock LLM service implementation
└── mock_responses.py           # Mock response data and templates
```

## Key Components

### 1. Core LLM Service (`core.py`)

**Purpose**: Mock LLM service for Phase 1 testing and validation

**Key Features**:
- Mock response generation
- Mode-specific response templates
- Error simulation for testing
- Consistent API interface

**Implementation**:
```python
class CoreLLMService:
    """Mock LLM service for Phase 1 testing"""

    def __init__(self):
        self.mock_responses = MockResponses()

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate mock response based on prompt"""
        return self.mock_responses.get_response(prompt, **kwargs)

    def generate_research_analysis(self, question: str, data: List[Dict], analysis_type: str) -> str:
        """Generate mock research analysis"""
        return self.mock_responses.get_analysis_response(question, analysis_type)
```

### 2. Mock Responses (`mock_responses.py`)

**Purpose**: Provides mock response data and templates

**Key Features**:
- Mode-specific response templates
- Research analysis templates
- Error response templates
- Configurable response lengths

**Response Templates**:
```python
class MockResponses:
    """Mock response data and templates"""

    INSTANT_RESPONSES = [
        "Based on available data, {question} can be answered as follows: [Mock instant response]",
        "Quick answer to {question}: [Mock instant response]",
        "Direct response to {question}: [Mock instant response]"
    ]

    QUICK_RESPONSES = [
        "Enhanced analysis of {question}: [Mock quick response with context]",
        "Comprehensive answer to {question}: [Mock quick response with details]",
        "Detailed response to {question}: [Mock quick response with insights]"
    ]

    STANDARD_RESPONSES = [
        "Thorough analysis of {question}: [Mock standard response with comprehensive coverage]",
        "In-depth research on {question}: [Mock standard response with multiple perspectives]",
        "Comprehensive study of {question}: [Mock standard response with detailed analysis]"
    ]

    DEEP_RESPONSES = [
        "Exhaustive research on {question}: [Mock deep response with academic-level analysis]",
        "Comprehensive analysis of {question}: [Mock deep response with clarification questions]",
        "Detailed investigation of {question}: [Mock deep response with exhaustive coverage]"
    ]
```

## Implementation Details

### Phase 1 Scope
- Mock LLM service with static responses
- Mode-specific response templates
- Basic error simulation
- Consistent API interface
- No external dependencies

### Phase 2 Enhancements
- Real LLM service integration
- Multi-provider support (Ollama, OpenAI, etc.)
- Model detection and selection
- Research-specific optimizations

### Phase 3 Enhancements
- Tool integration support
- Advanced prompt engineering
- Response caching
- Performance optimization

### Phase 4 Enhancements
- Production-ready error handling
- Advanced monitoring and metrics
- Circuit breakers and fault tolerance
- Comprehensive logging

## Response Characteristics

### Mode-Specific Differences
- **Instant**: Short, direct responses (1-2 sentences)
- **Quick**: Medium responses with context (2-3 paragraphs)
- **Standard**: Comprehensive responses (4-5 paragraphs)
- **Deep**: Detailed responses with clarifications (6+ paragraphs)

### Response Quality
- **Instant**: Basic facts and essential information
- **Quick**: Enhanced context and relevant details
- **Standard**: Comprehensive analysis with multiple perspectives
- **Deep**: Exhaustive analysis with clarification questions

### Error Simulation
- Network timeout errors
- Rate limit errors
- Invalid response errors
- Service unavailable errors

## Testing Strategy

### Unit Tests
- Test mock response generation
- Test mode-specific responses
- Test error simulation
- Test API consistency

### Integration Tests
- Test with ResearchAgent
- Test response quality differences
- Test error handling
- Test performance

### AgentHub Tests
```python
import agenthub as ah

# Load the agent
agent = ah.load_agent("agentplug/research-agent")

# Test mock responses
result1 = agent.instant_research("What is AI?")
# Expected: Short, direct mock response

result2 = agent.quick_research("How does ML work?")
# Expected: Medium mock response with context

result3 = agent.standard_research("Latest AI news?")
# Expected: Comprehensive mock response

result4 = agent.deep_research("AI ethics analysis")
# Expected: Detailed mock response with clarifications

# Verify mode differences
assert len(result1["result"]) < len(result2["result"])
assert len(result2["result"]) < len(result3["result"])
assert len(result3["result"]) < len(result4["result"])
```

## Usage Example

```python
from research_agent.llm_service import get_shared_llm_service

# Get shared mock LLM service
llm_service = get_shared_llm_service()

# Generate mock response
response = llm_service.generate("What is artificial intelligence?")

# Generate research analysis
analysis = llm_service.generate_research_analysis(
    "AI ethics",
    [{"title": "Mock source", "content": "Mock content"}],
    "comprehensive"
)
```

## Dependencies

- Python 3.11+
- typing for type hints
- logging for error handling
- No external LLM dependencies (Phase 1)

## Next Steps

This module provides the foundation for:
- Real LLM integration (Phase 2)
- Multi-provider support (Phase 2)
- Tool integration (Phase 3)
- Production-ready features (Phase 4)

The mock LLM service will be replaced with real LLM integration in Phase 2, providing actual AI responses while maintaining the same API interface.
