# BaseAgent Module Implementation

## Overview
The BaseAgent module provides a reusable framework for building AI agents. It includes common capabilities like LLM integration, error handling, context management, and tool management.

## Files

### `__init__.py`
```python
"""
BaseAgent module - Reusable agent framework
"""

from .core import BaseAgent
from .context_manager import ContextManager
from .error_handler import ErrorHandler
from .utils import AgentUtils

__all__ = ['BaseAgent', 'ContextManager', 'ErrorHandler', 'AgentUtils']
```

### `core.py` - BaseAgent Class
**Purpose**: Main BaseAgent class with common agent capabilities

**Key Methods**:
- `__init__(agent_type, config, external_tools)` - Initialize agent
- `solve(question)` - Universal solve method
- `add_tool(tool_name, tool_info)` - Add external tool
- `remove_tool(tool_name)` - Remove tool
- `has_tool(tool_name)` - Check if tool exists
- `get_config(key)` - Get configuration value
- `set_config(key, value)` - Set configuration value
- `get_health_status()` - Get agent health status
- `get_agent_info()` - Get agent information

**Features**:
- Generic agent type support
- Tool management system
- Configuration management
- Health monitoring
- Error handling integration

### `context_manager.py` - Context Management
**Purpose**: Manage agent context and state

**Key Methods**:
- `set_context(key, value)` - Set context value
- `get_context(key)` - Get context value
- `clear_context()` - Clear all context
- `update_context(updates)` - Update multiple context values
- `get_context_summary()` - Get context summary

**Features**:
- Context persistence
- State management
- Context validation
- Memory optimization

### `error_handler.py` - Error Handling
**Purpose**: Comprehensive error handling and logging

**Key Methods**:
- `handle_error(error, context)` - Handle errors
- `log_info(message)` - Log info messages
- `log_warning(message)` - Log warnings
- `log_error(message)` - Log errors
- `get_error_summary()` - Get error summary

**Features**:
- Error categorization
- Context-aware logging
- Error recovery
- Performance monitoring

### `utils.py` - Utility Functions
**Purpose**: Common utility functions

**Key Methods**:
- `validate_input(input_data)` - Validate input data
- `format_response(response)` - Format response
- `sanitize_data(data)` - Sanitize data
- `generate_id()` - Generate unique IDs
- `timestamp()` - Get current timestamp

**Features**:
- Input validation
- Data sanitization
- Response formatting
- ID generation
- Time utilities

## Usage Example
```python
from research_agent.base_agent import BaseAgent

# Initialize agent
agent = BaseAgent(
    agent_type="research",
    config={"temperature": 0.0},
    external_tools=["web_search", "academic_search"]
)

# Use agent
result = await agent.solve("What are the latest AI developments?")
```

## Dependencies
- `logging` - For error handling and logging
- `json` - For configuration management
- `typing` - For type hints
- `asyncio` - For async operations
