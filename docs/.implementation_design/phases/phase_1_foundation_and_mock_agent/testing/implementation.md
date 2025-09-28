# Testing Module - Phase 1

**Purpose**: Comprehensive testing for all modules

## Overview

The Testing module provides comprehensive testing coverage for all components of the research agent, including unit tests, integration tests, and AgentHub compatibility tests. It ensures reliability, correctness, and performance of the agent implementation.

## File Structure

```
tests/
├── test_base_agent.py      # BaseAgent unit tests
├── test_llm_service.py     # LLM service tests
├── test_research_agent.py  # Research agent tests
├── test_agent_entry.py     # Entry point tests
├── test_integration.py     # Integration tests
├── conftest.py            # Test configuration and fixtures
└── test_utils.py          # Test utilities and helpers
```

## Implementation Details

### `test_base_agent.py` - BaseAgent Tests

**Purpose**: Unit tests for BaseAgent functionality

**Test Coverage**:
- Agent initialization
- Tool management (add, remove, has_tool)
- Configuration management (get, set, update)
- Health monitoring
- Error handling
- Reusability

**Test Examples**:
```python
def test_agent_initialization():
    agent = BaseAgent("research", {"temperature": 0.0})
    assert agent.agent_type == "research"
    assert agent.get_config("temperature") == 0.0

def test_tool_management():
    agent = BaseAgent("research", {})
    agent.add_tool("web_search", {"description": "Search web"})
    assert agent.has_tool("web_search") == True
    agent.remove_tool("web_search")
    assert agent.has_tool("web_search") == False

def test_configuration_management():
    agent = BaseAgent("research", {"temp": 0.0})
    agent.set_config("temp", 0.1)
    assert agent.get_config("temp") == 0.1
    agent.update_config({"temp": 0.2, "new_key": "value"})
    assert agent.get_config("temp") == 0.2
    assert agent.get_config("new_key") == "value"
```

### `test_llm_service.py` - LLM Service Tests

**Purpose**: Tests for LLM service functionality

**Test Coverage**:
- Mock response generation
- Agent-type awareness
- Configuration handling
- Error simulation
- Shared instance management

**Test Examples**:
```python
def test_mock_response_generation():
    llm_service = MockLLMService("research")
    response = llm_service.generate("Test prompt")
    assert isinstance(response, str)
    assert len(response) > 0

def test_agent_type_awareness():
    research_llm = MockLLMService("research")
    coding_llm = MockLLMService("coding")
    assert research_llm.agent_type == "research"
    assert coding_llm.agent_type == "coding"

def test_shared_instance_management():
    llm1 = get_shared_llm_service("research")
    llm2 = get_shared_llm_service("research")
    assert llm1 is llm2  # Same instance
```

### `test_research_agent.py` - Research Agent Tests

**Purpose**: Tests for research agent functionality

**Test Coverage**:
- All research modes (instant, quick, standard, deep)
- Dynamic research workflow
- Tool selection logic
- Progress analysis
- Completion detection
- Follow-up query generation

**Test Examples**:
```python
def test_instant_research():
    agent = ResearchAgent({}, ["web_search"])
    result = agent.instant_research("What is ChatGPT?")
    assert isinstance(result, str)
    assert len(result) > 0

def test_dynamic_research_workflow():
    agent = ResearchAgent({}, ["web_search", "academic_search"])
    result = agent._execute_dynamic_research("AI developments", "quick")
    assert isinstance(result, str)
    assert len(result) > 0

def test_tool_selection():
    agent = ResearchAgent({}, ["web_search", "academic_search"])
    tools = agent._select_tools_for_round(
        "AI question", "quick", [], ["web_search", "academic_search"], 0
    )
    assert isinstance(tools, list)
    assert len(tools) > 0

def test_progress_analysis():
    agent = ResearchAgent({}, ["web_search"])
    analysis = agent._select_tools_for_round(
        "AI question", "quick", ["web_search: AI news"], ["web_search"], 1
    )
    assert isinstance(analysis, list)
```

### `test_agent_entry.py` - Entry Point Tests

**Purpose**: Tests for agent entry point and AgentHub compatibility

**Test Coverage**:
- Command-line interface
- JSON parsing
- Method routing
- Response formatting
- Error handling
- AgentHub compatibility

**Test Examples**:
```python
def test_command_line_interface():
    # Test JSON input parsing
    input_data = {
        "method": "instant_research",
        "parameters": {"question": "What is ChatGPT?"}
    }
    result = main_with_input(json.dumps(input_data))
    assert result["status"] == "success"
    assert "result" in result

def test_method_routing():
    # Test all research methods
    methods = ["instant_research", "quick_research", "standard_research", "deep_research"]
    for method in methods:
        input_data = {
            "method": method,
            "parameters": {"question": "Test question"}
        }
        result = main_with_input(json.dumps(input_data))
        assert result["status"] == "success"

def test_error_handling():
    # Test invalid input
    result = main_with_input("invalid json")
    assert result["status"] == "error"
    assert "error" in result
```

### `test_integration.py` - Integration Tests

**Purpose**: End-to-end integration tests

**Test Coverage**:
- Complete research workflows
- Module interactions
- Tool integration
- Error handling
- Performance

**Test Examples**:
```python
def test_complete_research_workflow():
    agent = ResearchAgent({}, ["web_search", "academic_search"])
    result = agent.standard_research("AI developments")
    assert isinstance(result, str)
    assert len(result) > 0

def test_tool_integration():
    agent = ResearchAgent({}, ["web_search"])
    result = agent._call_tool("web_search", {"query": "test"})
    assert isinstance(result, str)
    assert len(result) > 0

def test_error_recovery():
    agent = ResearchAgent({}, [])
    result = agent.instant_research("test question")
    assert isinstance(result, str)
    assert "error" in result.lower() or len(result) > 0
```

## Test Configuration

### `conftest.py` - Test Fixtures

**Purpose**: Shared test fixtures and configuration

**Fixtures**:
```python
@pytest.fixture
def base_agent():
    return BaseAgent("test", {"temperature": 0.0})

@pytest.fixture
def llm_service():
    return MockLLMService("test")

@pytest.fixture
def research_agent():
    return ResearchAgent({}, ["web_search", "academic_search"])

@pytest.fixture
def tool_context():
    return {
        "available_tools": ["web_search", "academic_search"],
        "tool_descriptions": {
            "web_search": "Search web",
            "academic_search": "Search academic papers"
        }
    }
```

### `test_utils.py` - Test Utilities

**Purpose**: Test utilities and helpers

**Utilities**:
```python
def create_mock_tool_response(tool_name: str, query: str) -> str:
    return f"Mock result from {tool_name} for query: {query}"

def assert_valid_json_response(response: str) -> bool:
    try:
        json.loads(response)
        return True
    except json.JSONDecodeError:
        return False

def measure_execution_time(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time
```

## Dependencies

- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-mock` - Mocking support
- `pytest-cov` - Coverage reporting
- `asyncio` - Async support
- `json` - JSON handling
- `time` - Performance measurement

## Test Execution

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_base_agent.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run async tests
pytest -v tests/test_research_agent.py

# Run integration tests
pytest tests/test_integration.py
```

### Test Categories
```bash
# Unit tests
pytest -m "unit"

# Integration tests
pytest -m "integration"

# AgentHub tests
pytest -m "agenthub"

# Performance tests
pytest -m "performance"
```

## Coverage Requirements

### Minimum Coverage
- **Unit Tests**: 90% coverage
- **Integration Tests**: 80% coverage
- **Critical Paths**: 100% coverage

### Coverage Areas
- All public methods
- Error handling paths
- Edge cases
- Configuration validation
- Tool integration

## Performance Testing

### Benchmarks
- Agent initialization time
- Research method execution time
- Tool calling performance
- Memory usage
- Response time

### Performance Targets
- Agent initialization: < 1 second
- Instant research: < 30 seconds
- Quick research: < 2 minutes
- Standard research: < 10 minutes
- Deep research: < 30 minutes

## Continuous Integration

### CI Pipeline
1. **Code Quality**: Linting, formatting
2. **Unit Tests**: All unit tests pass
3. **Integration Tests**: All integration tests pass
4. **Coverage**: Coverage requirements met
5. **Performance**: Performance benchmarks met
6. **AgentHub**: AgentHub compatibility confirmed

### Test Reports
- Test results
- Coverage reports
- Performance benchmarks
- Error analysis
- Quality metrics

## Phase 2 Preparation

This testing framework prepares for Phase 2 by:
- Establishing comprehensive test coverage
- Creating reusable test utilities
- Ensuring quality standards
- Providing performance benchmarks
- Supporting continuous integration

Phase 2 will extend this testing framework with real LLM service tests and advanced feature testing.
