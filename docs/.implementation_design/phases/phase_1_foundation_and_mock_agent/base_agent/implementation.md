# BaseAgent Module - Phase 1

**Purpose**: Provides common agent capabilities that can be reused by other agents

## Overview

The BaseAgent module establishes the foundation for all agents in the system, providing common functionality that can be inherited and specialized by specific agent implementations like ResearchAgent.

## File Structure

```
src/base_agent/
├── __init__.py          # Module initialization and exports
├── core.py              # BaseAgent class with common functionality
├── context_manager.py   # Context and state management
├── error_handler.py     # Error handling and recovery
└── utils.py             # Utility functions and helpers
```

## Implementation Details

### `core.py` - BaseAgent Class

**Key Features**:
- Generic agent initialization with `agent_type` parameter
- Tool management (add, remove, has_tool)
- Configuration management (get, set, update)
- Health monitoring and status reporting
- Universal `solve()` method interface
- Error handling and logging

**Class Structure**:
```python
class BaseAgent:
    def __init__(self, agent_type: str, config: Dict[str, Any], external_tools: List[str] = None)
    def add_tool(self, tool_name: str, tool_info: Dict[str, Any])
    def remove_tool(self, tool_name: str)
    def has_tool(self, tool_name: str) -> bool
    def get_config(self, key: str) -> Any
    def set_config(self, key: str, value: Any)
    def update_config(self, updates: Dict[str, Any])
    def get_health_status(self) -> Dict[str, Any]
    def get_agent_info(self) -> Dict[str, Any]
    async def solve(self, question: str) -> Dict[str, Any]
```

### `context_manager.py` - Context Management

**Purpose**: Manages agent context, state, and tool information

**Key Features**:
- Tool context management
- Research state tracking
- Context persistence
- State validation

### `error_handler.py` - Error Handling

**Purpose**: Provides comprehensive error handling and recovery

**Key Features**:
- Error logging and reporting
- Graceful error recovery
- Error categorization
- Fallback mechanisms

### `utils.py` - Utility Functions

**Purpose**: Common utility functions and helpers

**Key Features**:
- Configuration validation
- Data formatting
- Common helper functions
- Type checking utilities

## Dependencies

- `asyncio` - Async support
- `logging` - Logging functionality
- `json` - JSON handling
- `typing` - Type hints

## Testing

### Unit Tests
- Test agent initialization
- Test tool management
- Test configuration management
- Test health monitoring
- Test error handling

### Test Coverage
- All public methods
- Error conditions
- Edge cases
- Configuration validation

## Usage Example

```python
from base_agent import BaseAgent

# Initialize base agent
agent = BaseAgent(
    agent_type="research",
    config={"temperature": 0.0},
    external_tools=["web_search", "academic_search"]
)

# Add tool
agent.add_tool("news_search", {"description": "Search news articles"})

# Check health
status = agent.get_health_status()

# Solve problem
result = await agent.solve("What are the latest AI developments?")
```

## Reusability

This module is designed to be reusable by other agent types:

### CodingAgent Example
```python
class CodingAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any], external_tools: List[str] = None):
        super().__init__("coding", config, external_tools)
        self.llm_service = get_shared_llm_service(agent_type="coding")
    
    async def solve(self, question: str) -> Dict[str, Any]:
        return await self._execute_coding_task(question)
```

### AnalysisAgent Example
```python
class AnalysisAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any], external_tools: List[str] = None):
        super().__init__("analysis", config, external_tools)
        self.llm_service = get_shared_llm_service(agent_type="analysis")
    
    async def solve(self, question: str) -> Dict[str, Any]:
        return await self._execute_analysis_task(question)
```

## Configuration

### Default Configuration
```json
{
    "ai": {
        "temperature": 0.0,
        "max_tokens": null,
        "timeout": 30
    },
    "research": {
        "max_sources_per_round": 10,
        "max_rounds": 12,
        "timeout_per_round": 300
    },
    "system_prompts": {
        "instant": "You are a research assistant for INSTANT research mode...",
        "quick": "You are a research assistant for QUICK research mode...",
        "standard": "You are a research assistant for STANDARD research mode...",
        "deep": "You are a research assistant for DEEP research mode..."
    }
}
```

## Error Handling

### Error Categories
- **Initialization Errors**: Agent setup failures
- **Tool Errors**: Tool calling failures
- **Configuration Errors**: Invalid configuration
- **Runtime Errors**: Execution failures

### Error Recovery
- Graceful degradation
- Fallback mechanisms
- Error logging
- Status reporting

## Performance Considerations

- Efficient tool management
- Minimal memory footprint
- Fast initialization
- Optimized configuration access
