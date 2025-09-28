# Agent Entry Point Module - Phase 1

**Purpose**: Ensures AgentHub compatibility and command-line interface

## Overview

The Agent Entry Point module provides the interface between the research agent and AgentHub, ensuring compatibility with AgentHub's loading and execution system. It handles command-line JSON input/output and provides the necessary metadata for AgentHub integration.

## File Structure

```
agent.py              # Main agent entry point
agent.yaml            # AgentHub configuration
pyproject.toml        # Python package configuration
config.json           # Runtime configuration
```

## Implementation Details

### `agent.py` - Main Entry Point

**Purpose**: Handles command-line interface and AgentHub integration

**Key Features**:
- Command-line JSON input/output
- AgentHub method routing
- Error handling and response formatting
- Async support for solve() method

**Class Structure**:
```python
class ResearchAgent:
    def __init__(self, config: Dict[str, Any], external_tools: List[str] = None)
    def instant_research(self, question: str) -> str
    def quick_research(self, question: str) -> str
    def standard_research(self, question: str) -> str
    def deep_research(self, question: str) -> str
    async def solve(self, question: str) -> Dict[str, Any]

def main():
    # Command-line interface implementation
    # JSON input parsing
    # Method routing
    # Response formatting
    # Error handling

if __name__ == "__main__":
    main()
```

### `agent.yaml` - AgentHub Configuration

**Purpose**: Provides metadata and configuration for AgentHub

**Key Features**:
- Agent metadata (name, description, version)
- Module and class specifications
- Dependency management
- Research mode descriptions

**Configuration Structure**:
```yaml
name: research-agent
description: Deep Research Agent with dynamic tool selection
version: 1.0.0
module: agent
class: ResearchAgent
dependencies:
  - asyncio
  - json
  - typing
  - logging
research_modes:
  instant:
    description: "Quick, direct answers in under 30 seconds"
    timing: "1 round, <30 seconds"
    use_case: "Simple questions requiring immediate answers"
  quick:
    description: "Enhanced context with minimal rounds"
    timing: "2 rounds, 1-2 minutes"
    use_case: "Questions requiring some context and analysis"
  standard:
    description: "Comprehensive coverage with thorough analysis"
    timing: "3 rounds, 5-10 minutes"
    use_case: "Complex questions requiring comprehensive research"
  deep:
    description: "Exhaustive analysis with clarification questions"
    timing: "5 rounds, 15-30 minutes"
    use_case: "Complex topics requiring deep understanding"
```

### `pyproject.toml` - Package Configuration

**Purpose**: Python package configuration and dependencies

**Key Features**:
- Package metadata
- Dependency specifications
- Build configuration
- Development dependencies

**Configuration Structure**:
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "research-agent"
version = "1.0.0"
description = "Deep Research Agent with dynamic tool selection"
authors = [{name = "AgentPlug", email = "contact@agentplug.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "asyncio",
    "typing-extensions",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio",
    "black",
    "flake8",
]
```

### `config.json` - Runtime Configuration

**Purpose**: Runtime configuration and settings

**Key Features**:
- Default configuration values
- Environment-specific settings
- Runtime parameter configuration

**Configuration Structure**:
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
        "instant": "You are a research assistant for INSTANT research mode. Provide quick, accurate answers focusing on key facts.",
        "quick": "You are a research assistant for QUICK research mode. Conduct enhanced research with additional context. Provide thorough, well-structured responses.",
        "standard": "You are a research assistant for STANDARD research mode. Conduct comprehensive research with multiple rounds of analysis. Provide thorough, well-structured responses.",
        "deep": "You are a research assistant for DEEP research mode. Conduct exhaustive research with clarification and comprehensive analysis. Provide detailed, well-researched responses with full context."
    }
}
```

## Command-Line Interface

### Input Format
```json
{
    "method": "instant_research",
    "parameters": {
        "question": "What are the latest AI developments?"
    },
    "tool_context": {
        "available_tools": ["web_search", "academic_search"],
        "tool_descriptions": {
            "web_search": "Search the web for information",
            "academic_search": "Search academic papers and research"
        },
        "tool_usage_examples": {
            "web_search": "web_search(query)",
            "academic_search": "academic_search(query)"
        },
        "tool_parameters": {
            "web_search": {
                "query": {"name": "query", "type": "string", "required": true}
            },
            "academic_search": {
                "query": {"name": "query", "type": "string", "required": true}
            }
        },
        "tool_return_types": {
            "web_search": "string",
            "academic_search": "string"
        },
        "tool_namespaces": {
            "web_search": "mcp",
            "academic_search": "mcp"
        }
    }
}
```

### Output Format
```json
{
    "result": "Research results...",
    "status": "success",
    "metadata": {
        "mode": "instant",
        "rounds": 1,
        "tools_used": ["web_search"],
        "execution_time": 2.5
    }
}
```

## Dependencies

- `asyncio` - Async support
- `json` - JSON handling
- `typing` - Type hints
- `logging` - Logging functionality
- `sys` - Command-line arguments
- `argparse` - Argument parsing

## Testing

### Unit Tests
- Test command-line interface
- Test JSON parsing
- Test method routing
- Test response formatting
- Test error handling

### Integration Tests
- Test AgentHub compatibility
- Test end-to-end workflows
- Test tool context handling
- Test async method support

### AgentHub Tests
- Test agent loading
- Test method calls
- Test error handling
- Test performance

## Usage Examples

### AgentHub Loading
```python
import agenthub as ah

# Load the agent
agent = ah.load_agent("agentplug/research-agent")

# Use research methods
result = agent.instant_research("What is ChatGPT?")
result = agent.quick_research("Latest AI developments")
result = agent.standard_research("AI impact on healthcare")
result = agent.deep_research("Future of artificial intelligence")

# Auto mode selection
result = agent.solve("AI developments")
```

### Command-Line Usage
```bash
# Instant research
python agent.py '{"method": "instant_research", "parameters": {"question": "What is ChatGPT?"}}'

# Quick research
python agent.py '{"method": "quick_research", "parameters": {"question": "Latest AI developments"}}'

# Standard research
python agent.py '{"method": "standard_research", "parameters": {"question": "AI impact on healthcare"}}'

# Deep research
python agent.py '{"method": "deep_research", "parameters": {"question": "Future of artificial intelligence"}}'

# Auto mode selection
python agent.py '{"method": "solve", "parameters": {"question": "AI developments"}}'
```

## Error Handling

### Error Categories
- **Input Errors**: Invalid JSON, missing parameters
- **Method Errors**: Unknown methods, parameter validation
- **Tool Errors**: Tool calling failures
- **Runtime Errors**: Execution failures

### Error Response Format
```json
{
    "error": "Error message",
    "status": "error",
    "error_type": "InputError",
    "metadata": {
        "method": "instant_research",
        "parameters": {"question": "..."}
    }
}
```

## Performance Considerations

- Fast JSON parsing
- Efficient method routing
- Minimal overhead
- Optimized response formatting
- Memory-efficient processing

## Phase 2 Preparation

This implementation prepares for Phase 2 by:
- Establishing AgentHub compatibility
- Creating command-line interface
- Providing configuration framework
- Ensuring error handling
- Supporting async operations

Phase 2 will enhance this implementation with real LLM services while maintaining the same interface.
