# Phase 1: Foundation - Core Agent Infrastructure

## Overview

This phase establishes the foundational infrastructure for the Deep Research Agent, focusing on creating a working agent that can be loaded in AgentHub with basic functionality.

## Phase Goals

- ✅ Create working `agent.py` and `agent.yaml` in project root
- ✅ Implement BaseAgent class with common capabilities
- ✅ Implement ResearchAgent class inheriting from BaseAgent
- ✅ Create mock LLM service for testing
- ✅ Establish basic error handling and JSON responses
- ✅ Enable AgentHub loading and method execution

## Implementation Scope

### Core Files (Project Root)
- `agent.py` - Main entry point following AgentHub pattern
- `agent.yaml` - AgentHub configuration
- `pyproject.toml` - Python package configuration
- `config.json` - Runtime configuration
- `llm_service.py` - Mock LLM service

### Module Structure (`research_agent/`)
```
research_agent/
├── __init__.py
├── base_agent/
│   ├── __init__.py
│   ├── core.py              # BaseAgent class
│   ├── context_manager.py   # Context management
│   ├── error_handler.py     # Error handling
│   └── utils.py             # Common utilities
├── research_agent/
│   ├── __init__.py
│   ├── core.py              # ResearchAgent class
│   └── workflows/
│       ├── __init__.py
│       ├── instant.py       # Instant research workflow
│       ├── quick.py         # Quick research workflow
│       ├── standard.py      # Standard research workflow
│       └── deep.py         # Deep research workflow
└── llm_service/
    ├── __init__.py
    ├── core.py              # Mock LLM service
    └── mock_responses.py    # Mock response data
```

## Key Components

### 1. BaseAgent (`research_agent/base_agent/core.py`)
- Abstract base class with common agent capabilities
- Context management and error handling
- Tool management interface
- Universal `solve()` method interface

### 2. ResearchAgent (`research_agent/research_agent/core.py`)
- Inherits from BaseAgent
- Implements 5 research methods:
  - `instant_research()` - 1 round, 10 sources, 15-30 sec
  - `quick_research()` - 2 rounds, 20 sources, 1-2 min
  - `standard_research()` - 5 rounds, 50 sources, 8-15 min
  - `deep_research()` - 12 rounds, 120 sources, 20-30 min
  - `solve()` - Auto mode selection

### 3. Mock LLM Service (`research_agent/llm_service/core.py`)
- Returns static responses for testing
- Simulates different response qualities per mode
- No external dependencies

### 4. AgentHub Integration (`agent.py`)
- Command-line JSON interface
- Method routing and execution
- Error handling and response formatting

## Implementation Details

### Response Format Standardization

All research methods should return a consistent JSON format:

```python
{
    "result": "Research response content",
    "mode": "instant|quick|standard|deep",
    "sources": ["source1", "source2", ...],
    "status": "success|error",
    "timestamp": "2024-01-01T00:00:00Z",
    "metadata": {
        "rounds_completed": 1,
        "sources_used": 10,
        "execution_time": "15s"
    }
}
```

### Mode Selection Logic

The `solve()` method should implement simple mode selection based on question characteristics:

```python
def _select_mode(self, question: str) -> str:
    """Simple mode selection based on question characteristics"""
    question_length = len(question)
    question_lower = question.lower()

    # Deep research indicators
    if any(word in question_lower for word in ["comprehensive", "exhaustive", "detailed analysis", "thorough"]):
        return "deep"

    # Standard research indicators
    if any(word in question_lower for word in ["analysis", "research", "study", "investigation"]) or question_length > 100:
        return "standard"

    # Quick research indicators
    if any(word in question_lower for word in ["how", "what", "explain", "describe"]) or question_length > 50:
        return "quick"

    # Default to instant
    return "instant"
```

### Error Handling Strategy

Implement consistent error handling across all methods:

```python
def _handle_research_error(self, error: Exception, method: str) -> str:
    """Handle errors consistently across research methods"""
    error_message = self.config["error_messages"].get(method, "Error in research: {error}")
    return error_message.format(error=str(error))
```

### Mock Response Templates

Create realistic mock responses that demonstrate mode differences:

```python
MOCK_RESPONSES = {
    "instant": "Based on available information, {question} can be answered as follows: [Concise 1-2 sentence response with key facts]",
    "quick": "Enhanced analysis of {question}: [2-3 paragraph response with context and relevant details]",
    "standard": "Comprehensive research on {question}: [4-5 paragraph response with thorough analysis and multiple perspectives]",
    "deep": "Exhaustive research on {question}: [6+ paragraph response with academic-level analysis, clarification questions, and detailed findings]"
}
```

## Testing Strategy

### AgentHub Tests
```python
import agenthub as ah

# Load the agent
agent = ah.load_agent("agentplug/research-agent")

# Test all methods (all return mock responses)
result1 = agent.instant_research("What is AI?")
result2 = agent.quick_research("How does ML work?")
result3 = agent.standard_research("Latest AI news?")
result4 = agent.deep_research("AI ethics analysis")
result5 = agent.solve("What is artificial intelligence?")
```

### Expected Results
- All methods return JSON responses with mock data
- Different response lengths per mode
- Consistent error handling
- AgentHub loading success

## Implementation Checklist

### Project Setup
- [ ] Create project directory structure
- [ ] Initialize `pyproject.toml` with dependencies
- [ ] Create `config.json` with runtime configuration
- [ ] Set up logging configuration

### BaseAgent Implementation
- [ ] Implement `BaseAgent` abstract class
- [ ] Create `ContextManager` for state management
- [ ] Implement `ErrorHandler` for error management
- [ ] Add utility functions for common operations
- [ ] Write unit tests for BaseAgent components

### ResearchAgent Implementation
- [ ] Implement `ResearchAgent` class inheriting from BaseAgent
- [ ] Create mock workflow implementations for each mode
- [ ] Implement mode selection logic in `solve()` method
- [ ] Add research-specific error handling
- [ ] Write unit tests for ResearchAgent

### LLM Service Implementation
- [ ] Create mock LLM service with consistent API
- [ ] Implement mode-specific response templates
- [ ] Add error simulation for testing
- [ ] Create shared instance management
- [ ] Write unit tests for LLM service

### AgentHub Integration
- [ ] Implement `agent.py` with command-line interface
- [ ] Create `agent.yaml` with complete configuration
- [ ] Add method routing and execution logic
- [ ] Implement JSON response formatting
- [ ] Test AgentHub loading and method execution

### Testing and Validation
- [ ] Test all 5 research methods
- [ ] Verify mode-specific behavior differences
- [ ] Test error handling with invalid inputs
- [ ] Validate JSON response formatting
- [ ] Test AgentHub integration

## Success Criteria

- [ ] Agent loads successfully in AgentHub
- [ ] All 5 methods execute without errors
- [ ] Mock responses demonstrate mode differences
- [ ] Error handling works for invalid inputs
- [ ] JSON responses are properly formatted
- [ ] BaseAgent inheritance structure is established
- [ ] Mode selection logic works correctly
- [ ] Response format is consistent across methods

## Common Pitfalls to Avoid

### 1. Inconsistent Response Formats
- Ensure all methods return the same JSON structure
- Include all required fields (result, mode, sources, status)
- Use consistent field naming

### 2. Poor Error Handling
- Handle all possible error conditions
- Return user-friendly error messages
- Maintain consistent error response format

### 3. Mode Selection Issues
- Test mode selection with various question types
- Ensure fallback to instant mode works
- Validate mode selection logic

### 4. AgentHub Integration Problems
- Follow exact AgentHub pattern from reference agents
- Ensure proper JSON input/output handling
- Test with actual AgentHub loading

## Next Phase Dependencies

This phase provides the foundation for:
- Phase 2: Real LLM integration
- Phase 3: External tool integration
- Phase 4: Production-ready features

The BaseAgent class will be reused and extended in subsequent phases, demonstrating the OOP inheritance design.
