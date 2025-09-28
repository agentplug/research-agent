# BaseAgent Module Implementation - Phase 1 Foundation

## Overview
The BaseAgent module provides the foundational capabilities for all agents in the system. It implements common functionality that can be reused across different agent types.

## Module Structure
```
src/base_agent/
├── __init__.py
├── core.py
├── context_manager.py
├── error_handler.py
└── utils.py
```

## Files to Create/Modify

### `src/base_agent/__init__.py`
- Export main BaseAgent class
- Export utility functions
- Module initialization

### `src/base_agent/core.py`
- BaseAgent class implementation
- Common agent capabilities
- Tool management
- Configuration management
- Health monitoring

### `src/base_agent/context_manager.py`
- Context management utilities
- Session state handling
- Memory management

### `src/base_agent/error_handler.py`
- Error handling utilities
- Exception management
- Error logging

### `src/base_agent/utils.py`
- Utility functions
- Helper methods
- Common operations

## Key Features Implemented

### BaseAgent Class
- Generic agent initialization
- Tool management (add_tool, remove_tool, has_tool)
- Configuration management (get_config, set_config, update_config)
- Health monitoring (get_health_status, get_agent_info)
- Universal solve() method
- Error handling

### Tool Management
- External tool integration
- Tool context handling
- Tool calling interface
- Tool information management

### Configuration Management
- Runtime configuration loading
- Default configuration fallback
- Configuration validation
- Dynamic configuration updates

### Health Monitoring
- Agent status tracking
- Health check functionality
- Performance monitoring
- Error tracking

## Implementation Details

### BaseAgent.__init__(self, agent_type: str, config: Dict[str, Any], external_tools: List[str] = None)
- Initialize agent with type and configuration
- Set up logging
- Initialize tools
- Load configuration

### Tool Management Methods
- `add_tool(tool_name: str, tool_info: Dict[str, Any])`
- `remove_tool(tool_name: str)`
- `has_tool(tool_name: str) -> bool`
- `_call_tool(tool_name: str, parameters: Dict[str, Any]) -> str`
- `_get_available_tools_info() -> Dict[str, Any]`

### Configuration Methods
- `get_config(key: str) -> Any`
- `set_config(key: str, value: Any)`
- `update_config(config: Dict[str, Any])`

### Health Monitoring Methods
- `get_health_status() -> Dict[str, Any]`
- `get_agent_info() -> Dict[str, Any]`

## Testing
- Unit tests for all methods
- Integration tests with mock tools
- Error handling tests
- Configuration tests

## User Testing & Expectations - Phase 1 Foundation

### ✅ What You Should Be Able to Test

#### 1. BaseAgent Initialization
```python
from base_agent import BaseAgent

# Test basic initialization
agent = BaseAgent(agent_type="research", config={"ai": {"temperature": 0.0}})
assert agent.agent_type == "research"
assert agent.get_config("ai")["temperature"] == 0.0

# Test with external tools
agent = BaseAgent(agent_type="research", config={}, external_tools=["web_search", "academic_search"])
assert agent.has_tool("web_search") == True
assert agent.has_tool("academic_search") == True
```

#### 2. Tool Management
```python
# Test tool addition
agent.add_tool("news_search", {"description": "Search news articles"})
assert agent.has_tool("news_search") == True

# Test tool calling
result = agent._call_tool("web_search", {"query": "artificial intelligence"})
assert "Mock result from web_search" in result

# Test tool removal
agent.remove_tool("news_search")
assert agent.has_tool("news_search") == False
```

#### 3. Configuration Management
```python
# Test configuration retrieval
agent.set_config("new_setting", "test_value")
assert agent.get_config("new_setting") == "test_value"

# Test configuration update
agent.update_config({"batch_size": 10, "timeout": 30})
assert agent.get_config("batch_size") == 10
assert agent.get_config("timeout") == 30
```

#### 4. Health Monitoring
```python
# Test health status
health = agent.get_health_status()
assert health["status"] == "healthy"
assert "timestamp" in health
assert "uptime" in health

# Test agent info
info = agent.get_agent_info()
assert info["agent_type"] == "research"
assert "config_keys" in info
assert "tools_count" in info
```

### ✅ What You Should Expect

#### 1. Working BaseAgent Module
- **Initialization**: BaseAgent creates successfully with different configurations
- **Tool Management**: Tools can be added, removed, and called
- **Configuration**: Settings can be loaded, updated, and retrieved
- **Health Monitoring**: Status and information are accurate and useful
- **Error Handling**: Graceful handling of invalid inputs and errors

#### 2. Reusable Foundation
- **Inheritance**: Other agent types can inherit from BaseAgent
- **Common Functionality**: All common agent capabilities are available
- **Tool Integration**: External tools work seamlessly
- **Configuration**: Runtime configuration updates work properly

#### 3. AgentHub Compatibility
- **Interface**: BaseAgent provides foundation for AgentHub integration
- **Tool Context**: External tool context is handled correctly
- **Configuration**: Runtime configuration management supports AgentHub needs

### ✅ Manual Testing Commands

#### Test BaseAgent Directly
```python
# Create test script: test_base_agent.py
from base_agent import BaseAgent

def test_base_agent():
    # Test initialization
    agent = BaseAgent(agent_type="test", config={"test": "value"})
    print(f"✓ Agent initialized: {agent.agent_type}")
    
    # Test tool management
    agent.add_tool("test_tool", {"description": "Test tool"})
    print(f"✓ Tool added: {agent.has_tool('test_tool')}")
    
    result = agent._call_tool("test_tool", {"param": "value"})
    print(f"✓ Tool called: {result[:50]}...")
    
    # Test configuration
    agent.set_config("new_key", "new_value")
    print(f"✓ Config set: {agent.get_config('new_key')}")
    
    # Test health
    health = agent.get_health_status()
    print(f"✓ Health status: {health['status']}")
    
    info = agent.get_agent_info()
    print(f"✓ Agent info: {info['agent_type']}")

if __name__ == "__main__":
    test_base_agent()
```

#### Expected Output
```
✓ Agent initialized: test
✓ Tool added: True
✓ Tool called: Mock result from test_tool with parameters: {'param': 'value'}
✓ Config set: new_value
✓ Health status: healthy
✓ Agent info: test
```

### ✅ Success Criteria Checklist

- [ ] BaseAgent initializes correctly with different configurations
- [ ] Tool management methods work as expected (add, remove, has, call)
- [ ] Configuration can be loaded, updated, and retrieved
- [ ] Health monitoring provides accurate status and information
- [ ] Error handling works for various scenarios
- [ ] All unit tests pass
- [ ] Module can be imported and used by other modules
- [ ] Documentation is complete and accurate
- [ ] Performance is acceptable for Phase 1 requirements

## Dependencies
- Python 3.11+
- Standard library modules
- Logging framework
- JSON handling
