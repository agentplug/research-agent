# Unit Testing Plan - Phase 1 Foundation

## Overview

This document provides a comprehensive unit testing plan for Phase 1 implementation, ensuring each component is thoroughly tested before integration.

## Testing Structure

```
tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_base_agent.py
│   ├── test_research_agent.py
│   ├── test_llm_service.py
│   ├── test_context_manager.py
│   ├── test_error_handler.py
│   └── test_utils.py
├── integration/
│   ├── __init__.py
│   ├── test_agent_integration.py
│   └── test_workflows.py
├── fixtures/
│   ├── __init__.py
│   ├── mock_responses.json
│   ├── test_config.json
│   └── sample_questions.json
└── conftest.py
```

## Unit Test Specifications

### 1. BaseAgent Tests (`test_base_agent.py`)

#### Test Initialization
```python
def test_base_agent_initialization():
    """Test BaseAgent initialization with various parameters"""
    
    # Test with minimal parameters
    agent = BaseAgent(mock_llm_service)
    assert agent.llm_service == mock_llm_service
    assert agent.external_tools == []
    assert agent.agent_id is not None
    assert agent.created_at is not None
    
    # Test with external tools
    tools = ["web_search", "academic_search"]
    agent = BaseAgent(mock_llm_service, external_tools=tools)
    assert agent.external_tools == tools
    
    # Test with configuration
    config = {"timeout": 60}
    agent = BaseAgent(mock_llm_service, config=config)
    assert agent.config["timeout"] == 60

def test_base_agent_abstract_methods():
    """Test that BaseAgent abstract methods raise NotImplementedError"""
    
    agent = BaseAgent(mock_llm_service)
    
    # Test abstract solve method
    with pytest.raises(NotImplementedError):
        agent.solve("test question")

def test_get_available_tools():
    """Test get_available_tools method"""
    
    tools = ["web_search", "academic_search"]
    agent = BaseAgent(mock_llm_service, external_tools=tools)
    
    available_tools = agent.get_available_tools()
    assert len(available_tools) == 2
    assert "web_search" in available_tools
    assert "academic_search" in available_tools

def test_validate_input():
    """Test input validation"""
    
    agent = BaseAgent(mock_llm_service)
    
    # Valid input
    valid_input = {"question": "What is AI?"}
    assert agent.validate_input(valid_input) == True
    
    # Invalid input - missing question
    invalid_input = {"topic": "AI"}
    assert agent.validate_input(invalid_input) == False
    
    # Invalid input - empty question
    empty_input = {"question": ""}
    assert agent.validate_input(empty_input) == False

def test_handle_error():
    """Test error handling"""
    
    agent = BaseAgent(mock_llm_service)
    
    # Test with different error types
    test_error = ValueError("Test error")
    error_response = agent.handle_error(test_error)
    
    assert error_response["error"] == True
    assert "error_id" in error_response
    assert "message" in error_response
    assert "timestamp" in error_response
    assert "agent_id" in error_response
```

#### Test Context Management
```python
def test_context_management():
    """Test context management functionality"""
    
    agent = BaseAgent(mock_llm_service)
    
    # Test setting context
    agent.context_manager.set_context("session_id", "test_session")
    assert agent.context_manager.get_context("session_id") == "test_session"
    
    # Test conversation history
    agent.context_manager.add_to_conversation("user", "What is AI?")
    agent.context_manager.add_to_conversation("agent", "AI is...")
    
    history = agent.context_manager.get_conversation_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "agent"
```

### 2. ResearchAgent Tests (`test_research_agent.py`)

#### Test Initialization
```python
def test_research_agent_initialization():
    """Test ResearchAgent initialization"""
    
    agent = ResearchAgent(mock_llm_service)
    assert isinstance(agent, BaseAgent)
    assert agent.llm_service == mock_llm_service
    assert hasattr(agent, 'research_engine')
    assert hasattr(agent, 'mode_selector')
    assert hasattr(agent, 'source_tracker')

def test_research_methods_exist():
    """Test that all research methods exist"""
    
    agent = ResearchAgent(mock_llm_service)
    
    assert hasattr(agent, 'instant_research')
    assert hasattr(agent, 'quick_research')
    assert hasattr(agent, 'standard_research')
    assert hasattr(agent, 'deep_research')
    assert hasattr(agent, 'solve')
```

#### Test Research Methods
```python
def test_instant_research():
    """Test instant research method"""
    
    agent = ResearchAgent(mock_llm_service)
    result = agent.instant_research("What is AI?")
    
    # Validate response format
    assert "result" in result
    assert "mode" in result
    assert "sources" in result
    assert "status" in result
    assert "timestamp" in result
    assert "metadata" in result
    
    # Validate content
    assert result["mode"] == "instant"
    assert result["status"] == "success"
    assert isinstance(result["sources"], list)
    assert len(result["result"]) > 0

def test_quick_research():
    """Test quick research method"""
    
    agent = ResearchAgent(mock_llm_service)
    result = agent.quick_research("How does ML work?")
    
    assert result["mode"] == "quick"
    assert result["status"] == "success"
    assert len(result["result"]) > 0

def test_standard_research():
    """Test standard research method"""
    
    agent = ResearchAgent(mock_llm_service)
    result = agent.standard_research("Latest AI developments")
    
    assert result["mode"] == "standard"
    assert result["status"] == "success"
    assert len(result["result"]) > 0

def test_deep_research():
    """Test deep research method"""
    
    agent = ResearchAgent(mock_llm_service)
    result = agent.deep_research("AI ethics analysis")
    
    assert result["mode"] == "deep"
    assert result["status"] == "success"
    assert len(result["result"]) > 0

def test_solve_method():
    """Test solve method with auto mode selection"""
    
    agent = ResearchAgent(mock_llm_service)
    
    # Test simple question
    result = agent.solve("What is AI?")
    assert result["status"] == "success"
    assert result["mode"] in ["instant", "quick", "standard", "deep"]
    
    # Test complex question
    result = agent.solve("Comprehensive analysis of AI ethics")
    assert result["status"] == "success"
    assert result["mode"] in ["standard", "deep"]
```

#### Test Mode Selection
```python
def test_mode_selection():
    """Test mode selection logic"""
    
    agent = ResearchAgent(mock_llm_service)
    
    # Test instant mode selection
    mode = agent._select_mode("What is AI?")
    assert mode == "instant"
    
    # Test quick mode selection
    mode = agent._select_mode("How does machine learning work?")
    assert mode == "quick"
    
    # Test standard mode selection
    mode = agent._select_mode("Latest developments in AI research")
    assert mode == "standard"
    
    # Test deep mode selection
    mode = agent._select_mode("Comprehensive analysis of AI ethics")
    assert mode == "deep"
```

#### Test Error Handling
```python
def test_research_error_handling():
    """Test error handling in research methods"""
    
    agent = ResearchAgent(mock_llm_service)
    
    # Test empty question
    result = agent.instant_research("")
    assert result["status"] == "error"
    assert "error" in result["result"].lower()
    
    # Test invalid input
    result = agent.quick_research(None)
    assert result["status"] == "error"
```

### 3. LLM Service Tests (`test_llm_service.py`)

#### Test Initialization
```python
def test_llm_service_initialization():
    """Test LLM service initialization"""
    
    service = CoreLLMService()
    assert service.mock_responses is not None
    assert hasattr(service, 'generate')
    assert hasattr(service, 'generate_research_analysis')

def test_shared_instance():
    """Test shared instance management"""
    
    service1 = get_shared_llm_service()
    service2 = get_shared_llm_service()
    
    assert service1 is service2  # Should be the same instance
```

#### Test Response Generation
```python
def test_generate_response():
    """Test response generation"""
    
    service = CoreLLMService()
    
    # Test basic generation
    response = service.generate("What is AI?")
    assert isinstance(response, str)
    assert len(response) > 0
    
    # Test with system prompt
    response = service.generate("What is AI?", system_prompt="You are a helpful assistant")
    assert isinstance(response, str)
    assert len(response) > 0

def test_mode_specific_responses():
    """Test mode-specific response generation"""
    
    service = CoreLLMService()
    
    # Test instant response
    instant_response = service.generate("What is AI?", mode="instant")
    assert len(instant_response) < 200  # Should be short
    
    # Test deep response
    deep_response = service.generate("What is AI?", mode="deep")
    assert len(deep_response) > 1000  # Should be long

def test_research_analysis():
    """Test research analysis generation"""
    
    service = CoreLLMService()
    
    data = [{"title": "Test source", "content": "Test content"}]
    analysis = service.generate_research_analysis("AI ethics", data, "comprehensive")
    
    assert isinstance(analysis, str)
    assert len(analysis) > 0
```

### 4. Context Manager Tests (`test_context_manager.py`)

#### Test Context Operations
```python
def test_context_operations():
    """Test context management operations"""
    
    manager = ContextManager()
    
    # Test setting and getting context
    manager.set_context("test_key", "test_value")
    assert manager.get_context("test_key") == "test_value"
    
    # Test context with persistence
    manager.set_context("persistent_key", "persistent_value", persistent=True)
    assert manager.get_context("persistent_key") == "persistent_value"
    
    # Test context removal
    manager.remove_context("test_key")
    assert manager.get_context("test_key") is None

def test_conversation_history():
    """Test conversation history management"""
    
    manager = ContextManager()
    
    # Add conversation entries
    manager.add_to_conversation("user", "What is AI?")
    manager.add_to_conversation("agent", "AI is artificial intelligence")
    
    # Test history retrieval
    history = manager.get_conversation_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "agent"
    
    # Test history with limit
    recent_history = manager.get_conversation_history(limit=1)
    assert len(recent_history) == 1
    assert recent_history[0]["role"] == "agent"

def test_metadata_management():
    """Test metadata management"""
    
    manager = ContextManager()
    
    # Set metadata
    manager.set_metadata("research", "sources_used", 10)
    manager.set_metadata("research", "rounds_completed", 3)
    
    # Get metadata
    sources = manager.get_metadata("research", "sources_used")
    assert sources == 10
    
    # Get all metadata for category
    research_metadata = manager.get_metadata("research")
    assert research_metadata["sources_used"] == 10
    assert research_metadata["rounds_completed"] == 3
```

### 5. Error Handler Tests (`test_error_handler.py`)

#### Test Error Categorization
```python
def test_error_categorization():
    """Test error categorization"""
    
    handler = ErrorHandler()
    
    # Test network error
    network_error = ConnectionError("Connection failed")
    category = handler._categorize_error(network_error)
    assert category == ErrorCategory.NETWORK
    
    # Test validation error
    validation_error = ValueError("Invalid input")
    category = handler._categorize_error(validation_error)
    assert category == ErrorCategory.VALIDATION
    
    # Test timeout error
    timeout_error = TimeoutError("Request timed out")
    category = handler._categorize_error(timeout_error)
    assert category == ErrorCategory.TIMEOUT

def test_error_severity():
    """Test error severity assessment"""
    
    handler = ErrorHandler()
    
    # Test critical error
    critical_error = Exception("Critical system failure")
    severity = handler._assess_severity(critical_error, ErrorCategory.INTERNAL)
    assert severity == ErrorSeverity.CRITICAL
    
    # Test low severity error
    low_error = ValueError("Invalid input")
    severity = handler._assess_severity(low_error, ErrorCategory.VALIDATION)
    assert severity == ErrorSeverity.LOW

def test_user_friendly_messages():
    """Test user-friendly error message generation"""
    
    handler = ErrorHandler()
    
    # Test network error message
    network_error = ConnectionError("Connection failed")
    message = handler._generate_user_message(network_error, ErrorCategory.NETWORK, ErrorSeverity.MEDIUM)
    assert "connect" in message.lower()
    assert "try again" in message.lower()
    
    # Test validation error message
    validation_error = ValueError("Invalid input")
    message = handler._generate_user_message(validation_error, ErrorCategory.VALIDATION, ErrorSeverity.LOW)
    assert "request" in message.lower()
    assert "check" in message.lower()
```

### 6. Utils Tests (`test_utils.py`)

#### Test Input Validation
```python
def test_validate_input_data():
    """Test input data validation"""
    
    schema = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "minLength": 1,
                "maxLength": 1000
            }
        },
        "required": ["question"]
    }
    
    # Valid data
    valid_data = {"question": "What is AI?"}
    assert validate_input_data(valid_data, schema) == True
    
    # Invalid data - missing required field
    invalid_data = {"topic": "AI"}
    assert validate_input_data(invalid_data, schema) == False
    
    # Invalid data - empty string
    empty_data = {"question": ""}
    assert validate_input_data(empty_data, schema) == False

def test_response_formatting():
    """Test response formatting"""
    
    # Test successful response
    response = format_response(True, {"result": "test"}, "Success")
    assert response["success"] == True
    assert response["data"]["result"] == "test"
    assert response["message"] == "Success"
    assert "timestamp" in response
    assert "response_id" in response
    
    # Test error response
    response = format_response(False, None, "Error occurred")
    assert response["success"] == False
    assert response["message"] == "Error occurred"
    assert "data" not in response

def test_string_utilities():
    """Test string utility functions"""
    
    # Test string sanitization
    dirty_string = "Test\x00string\x1fwith\x7fcontrol\x9fchars"
    clean_string = sanitize_string(dirty_string)
    assert "\x00" not in clean_string
    assert "\x1f" not in clean_string
    
    # Test string truncation
    long_string = "A" * 200
    truncated = truncate_text(long_string, max_length=100)
    assert len(truncated) == 100
    assert truncated.endswith("...")
    
    # Test URL validation
    assert is_valid_url("https://example.com") == True
    assert is_valid_url("http://localhost:8080") == True
    assert is_valid_url("invalid-url") == False
    assert is_valid_url("ftp://example.com") == False
```

## Integration Tests

### 1. Agent Integration Tests (`test_agent_integration.py`)

```python
def test_agent_integration():
    """Test complete agent integration"""
    
    # Test agent initialization
    agent = ResearchAgent(mock_llm_service)
    assert agent is not None
    
    # Test all methods work together
    methods = ['instant_research', 'quick_research', 'standard_research', 'deep_research', 'solve']
    for method in methods:
        result = getattr(agent, method)("Test question")
        assert result["status"] == "success"
        assert "result" in result

def test_workflow_integration():
    """Test workflow integration"""
    
    agent = ResearchAgent(mock_llm_service)
    
    # Test that workflows use correct components
    result = agent.instant_research("What is AI?")
    assert result["mode"] == "instant"
    assert result["status"] == "success"
    
    # Test mode selection integration
    result = agent.solve("What is AI?")
    assert result["status"] == "success"
    assert result["mode"] in ["instant", "quick", "standard", "deep"]
```

## Test Fixtures

### 1. Mock Responses (`mock_responses.json`)
```json
{
  "instant_responses": [
    "Based on available information, {question} can be answered as follows: [Concise 1-2 sentence response with key facts]",
    "Quick answer to {question}: [Direct response with essential information]"
  ],
  "quick_responses": [
    "Enhanced analysis of {question}: [2-3 paragraph response with context and relevant details]",
    "Comprehensive answer to {question}: [Medium-length response with insights and context]"
  ],
  "standard_responses": [
    "Thorough analysis of {question}: [4-5 paragraph response with comprehensive coverage]",
    "In-depth research on {question}: [Detailed response with multiple perspectives]"
  ],
  "deep_responses": [
    "Exhaustive research on {question}: [6+ paragraph response with academic-level analysis]",
    "Comprehensive analysis of {question}: [Detailed response with clarification questions]"
  ]
}
```

### 2. Test Configuration (`test_config.json`)
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
  "system_prompts": {
    "instant": "You are a research assistant for INSTANT research mode.",
    "quick": "You are a research assistant for QUICK research mode.",
    "standard": "You are a research assistant for STANDARD research mode.",
    "deep": "You are a research assistant for DEEP research mode."
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

### 3. Sample Questions (`sample_questions.json`)
```json
{
  "instant_questions": [
    "What is AI?",
    "What is the capital of France?",
    "How many days in a year?"
  ],
  "quick_questions": [
    "How does machine learning work?",
    "What are the benefits of renewable energy?",
    "Explain the water cycle"
  ],
  "standard_questions": [
    "Latest developments in AI research",
    "Impact of climate change on agriculture",
    "Analysis of renewable energy policies"
  ],
  "deep_questions": [
    "Comprehensive analysis of AI ethics",
    "Exhaustive study of climate change mitigation strategies",
    "Detailed investigation of renewable energy implementation challenges"
  ]
}
```

## Test Configuration (`conftest.py`)

```python
import pytest
from unittest.mock import Mock, MagicMock
from research_agent.base_agent import BaseAgent
from research_agent.research_agent import ResearchAgent
from research_agent.llm_service import CoreLLMService

@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing"""
    service = Mock(spec=CoreLLMService)
    service.generate.return_value = "Mock response"
    service.generate_research_analysis.return_value = "Mock analysis"
    return service

@pytest.fixture
def base_agent(mock_llm_service):
    """BaseAgent instance for testing"""
    return BaseAgent(mock_llm_service)

@pytest.fixture
def research_agent(mock_llm_service):
    """ResearchAgent instance for testing"""
    return ResearchAgent(mock_llm_service)

@pytest.fixture
def sample_questions():
    """Sample questions for testing"""
    return {
        "instant": "What is AI?",
        "quick": "How does ML work?",
        "standard": "Latest AI developments",
        "deep": "AI ethics analysis"
    }
```

## Running Tests

### Test Commands
```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_research_agent.py

# Run with coverage
pytest --cov=research_agent --cov-report=html

# Run with verbose output
pytest -v

# Run specific test
pytest tests/unit/test_research_agent.py::test_instant_research
```

### Test Coverage Goals
- **Unit Tests**: 90%+ coverage for all modules
- **Integration Tests**: 80%+ coverage for integration scenarios
- **Error Handling**: 100% coverage for error scenarios

## Success Criteria

### Test Results
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Test coverage meets goals
- [ ] No test warnings or errors
- [ ] Performance tests pass

### Quality Metrics
- [ ] Code follows testing best practices
- [ ] Tests are maintainable and readable
- [ ] Mock objects are properly used
- [ ] Test data is realistic and comprehensive
- [ ] Error scenarios are thoroughly tested

This comprehensive unit testing plan ensures that Phase 1 is thoroughly tested before integration and deployment.
