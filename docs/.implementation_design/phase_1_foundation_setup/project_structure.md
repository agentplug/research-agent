# Project Structure

## Overview
The research agent project follows a modular structure with clear separation of concerns. The main entry points are in the project root, while specialized modules are organized in the `research_agent/` directory.

## Project Root Files

### `agent.py` - Main Agent Entry Point
**Purpose**: Main entry point for AgentHub integration

**Key Components**:
- `main()` function - Command-line interface
- `ResearchAgent` instantiation
- JSON input/output handling
- Error handling and logging
- AgentHub compatibility

**Structure**:
```python
import asyncio
import json
import sys
from research_agent.research_agent import ResearchAgent

async def main():
    # Parse command line arguments
    # Initialize ResearchAgent
    # Execute research method
    # Return JSON response

if __name__ == "__main__":
    asyncio.run(main())
```

### `agent.yaml` - AgentHub Configuration
**Purpose**: AgentHub agent configuration

**Structure**:
```yaml
module: agent
class: ResearchAgent
dependencies:
  - research_agent
description: |
  Intelligent research agent with multiple research modes:
  - Instant Research: Quick answers in <30 seconds
  - Quick Research: Enhanced analysis in 1-2 minutes  
  - Standard Research: Comprehensive coverage in 2-5 minutes
  - Deep Research: Exhaustive analysis in 5-15 minutes
  
  Features:
  - Dynamic tool selection based on research progress
  - Context-aware analysis and gap identification
  - Independent tool selection per research round
  - Multi-provider LLM support
  - Source tracking and caching
```

### `pyproject.toml` - Python Package Configuration
**Purpose**: Modern Python packaging configuration

**Structure**:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "research-agent"
version = "0.1.0"
description = "Intelligent research agent with dynamic tool selection"
authors = [{name = "AgentPlug", email = "contact@agentplug.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "openai>=1.0.0",
    "anthropic>=0.3.0",
    "google-generativeai>=0.3.0",
    "requests>=2.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "flake8>=4.0.0",
]

[tool.hatch.build.targets.wheel]
packages = ["research_agent"]
```

### `config.json` - Runtime Configuration
**Purpose**: Runtime configuration for the agent

**Structure**:
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
  },
  "providers": {
    "openai": {
      "api_key": null,
      "model": "gpt-4"
    },
    "anthropic": {
      "api_key": null,
      "model": "claude-3-sonnet"
    },
    "google": {
      "api_key": null,
      "model": "gemini-pro"
    }
  }
}
```

## Module Structure (`research_agent/`)

### `research_agent/__init__.py`
```python
"""
Research Agent Package
"""

from .research_agent import ResearchAgent
from .base_agent import BaseAgent
from .llm_service import LLMService, get_shared_llm_service

__version__ = "0.1.0"
__all__ = ['ResearchAgent', 'BaseAgent', 'LLMService', 'get_shared_llm_service']
```

### `research_agent/base_agent/`
- **Purpose**: Reusable agent framework
- **Files**: `__init__.py`, `core.py`, `context_manager.py`, `error_handler.py`, `utils.py`

### `research_agent/llm_service/`
- **Purpose**: Multi-provider LLM service
- **Files**: `__init__.py`, `core.py`, `mock_service.py`, `utils.py`
- **Submodules**: `providers/` (OpenAI, Anthropic, Google, Local)

### `research_agent/research_agent/`
- **Purpose**: Specialized research agent
- **Files**: `__init__.py`, `core.py`, `research_methods.py`, `tool_manager.py`, `config.py`

## Directory Structure
```
research-agent/
├── agent.py                 # Main entry point
├── agent.yaml              # AgentHub configuration
├── pyproject.toml          # Python package config
├── config.json             # Runtime configuration
├── README.md               # Project documentation
├── .gitignore              # Git ignore rules
└── research_agent/         # Main package
    ├── __init__.py
    ├── base_agent/         # BaseAgent framework
    │   ├── __init__.py
    │   ├── core.py
    │   ├── context_manager.py
    │   ├── error_handler.py
    │   └── utils.py
    ├── llm_service/        # LLM service
    │   ├── __init__.py
    │   ├── core.py
    │   ├── mock_service.py
    │   ├── utils.py
    │   └── providers/      # Provider implementations
    │       ├── __init__.py
    │       ├── openai_provider.py
    │       ├── anthropic_provider.py
    │       ├── google_provider.py
    │       └── local_provider.py
    └── research_agent/     # Research agent
        ├── __init__.py
        ├── core.py
        ├── research_methods.py
        ├── tool_manager.py
        └── config.py
```

## Installation and Usage

### Installation
```bash
# Install dependencies
pip install -e .

# Or with uv (recommended)
uv pip install -e .
```

### Usage
```python
import agenthub as ah

# Load agent
agent = ah.load_agent("agentplug/research-agent", 
                     external_tools=["web_search", "academic_search"])

# Use different research modes
result = agent.instant_research("What is AI?")
result = agent.quick_research("Latest AI developments")
result = agent.standard_research("AI impact on society")
result = agent.deep_research("Future of artificial intelligence")

# Auto mode selection
result = await agent.solve("What are the latest AI developments?")
```

### Command Line Usage
```bash
# Run agent directly
python agent.py '{"method": "instant_research", "parameters": {"question": "What is AI?"}}'
```
