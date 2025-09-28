# Research Agent Module Implementation

## Overview
The Research Agent module implements the specialized research agent that inherits from BaseAgent and provides intelligent research capabilities with dynamic tool selection and context-aware analysis.

## Files

### `__init__.py`
```python
"""
Research Agent module - Specialized research agent
"""

from .core import ResearchAgent
from .research_methods import ResearchMethods
from .tool_manager import ToolManager

__all__ = ['ResearchAgent', 'ResearchMethods', 'ToolManager']
```

### `core.py` - ResearchAgent Class
**Purpose**: Main ResearchAgent class inheriting from BaseAgent

**Key Methods**:
- `__init__(external_tools)` - Initialize research agent
- `solve(question)` - Auto mode selection and execution
- `instant_research(question)` - Instant research mode
- `quick_research(question)` - Quick research mode
- `standard_research(question)` - Standard research mode
- `deep_research(question)` - Deep research mode
- `_execute_dynamic_research(question, mode)` - Dynamic research execution
- `_select_tools_for_round(question, mode, research_data, available_tools, iteration)` - Tool selection
- `_select_tools_independently(question, mode, research_data, available_tools, analysis)` - Independent tool selection
- `_get_max_iterations_for_mode(mode)` - Get iteration limits
- `_generate_final_response(question, research_data, mode)` - Generate final response

**Features**:
- Inherits from BaseAgent
- 4 research modes (instant, quick, standard, deep)
- Dynamic tool selection
- Context-aware analysis
- Independent tool selection per round
- Progress-based research

### `research_methods.py` - Research Methods
**Purpose**: Implementation of different research modes

**Key Methods**:
- `instant_research(question)` - Single round, quick response
- `quick_research(question)` - 2 rounds, enhanced analysis
- `standard_research(question)` - 3 rounds, comprehensive coverage
- `deep_research(question)` - 5 rounds, exhaustive analysis
- `_analyze_research_progress(question, mode, research_data)` - Analyze progress
- `_evaluate_completion(question, mode, research_data)` - Evaluate completion
- `_generate_clarification_questions(question)` - Generate clarifications

**Features**:
- Mode-specific research workflows
- Progress analysis
- Completion evaluation
- Clarification generation
- Context-aware research

### `tool_manager.py` - Tool Management
**Purpose**: Tool selection, execution, and management

**Key Methods**:
- `_call_tool(tool_name, parameters)` - Execute external tool
- `_get_available_tools_info()` - Get available tools information
- `_select_tools_for_research(question, mode)` - Select tools for research
- `_generate_follow_up_queries(question, mode, selected_tools)` - Generate queries
- `_validate_tool_response(response)` - Validate tool responses
- `_format_tool_result(tool_name, result)` - Format tool results

**Features**:
- External tool integration
- Intelligent tool selection
- Follow-up query generation
- Tool response validation
- Result formatting

### `config.py` - Research Configuration
**Purpose**: Research-specific configuration management

**Key Methods**:
- `load_research_config()` - Load research configuration
- `get_mode_config(mode)` - Get mode-specific configuration
- `validate_config(config)` - Validate configuration
- `get_default_config()` - Get default configuration

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
    "instant": "You are a research assistant for INSTANT research mode...",
    "quick": "You are a research assistant for QUICK research mode...",
    "standard": "You are a research assistant for STANDARD research mode...",
    "deep": "You are a research assistant for DEEP research mode..."
  }
}
```

## Research Modes

### Instant Research
- **Rounds**: 1
- **Purpose**: Quick, direct answers
- **Tools**: 1 tool
- **Time**: < 30 seconds
- **Use Case**: Simple questions, quick facts

### Quick Research
- **Rounds**: 2
- **Purpose**: Enhanced context
- **Tools**: 1-2 tools
- **Time**: 1-2 minutes
- **Use Case**: Multi-agent systems, quick analysis

### Standard Research
- **Rounds**: 3
- **Purpose**: Comprehensive coverage
- **Tools**: 2-3 tools
- **Time**: 2-5 minutes
- **Use Case**: Direct users, thorough research

### Deep Research
- **Rounds**: 5
- **Purpose**: Exhaustive analysis
- **Tools**: Multiple tools
- **Time**: 5-15 minutes
- **Use Case**: Complex topics, detailed analysis

## Usage Example
```python
from research_agent.research_agent import ResearchAgent

# Initialize research agent
agent = ResearchAgent(external_tools=["web_search", "academic_search"])

# Use different research modes
result1 = agent.instant_research("What is AI?")
result2 = agent.quick_research("Latest AI developments")
result3 = agent.standard_research("AI impact on society")
result4 = agent.deep_research("Future of artificial intelligence")

# Auto mode selection
result = await agent.solve("What are the latest AI developments?")
```

## Dependencies
- `research_agent.base_agent` - BaseAgent framework
- `research_agent.llm_service` - LLM service
- `json` - JSON handling
- `logging` - Logging
- `asyncio` - Async operations
- `typing` - Type hints
