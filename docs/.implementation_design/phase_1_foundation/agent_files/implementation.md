# Agent Files Implementation

## Files to Create/Modify

### agent.py (Project Root)
```python
#!/usr/bin/env python3
"""
Agent Hub Agent: research-agent
Conducts intelligent research using multiple tools and LLM analysis.
"""

import json
import sys
import os
import logging
import asyncio
from typing import Dict, Any

# Import our modular components
from research_agent.research_agent import ResearchAgent

logger = logging.getLogger(__name__)

def main():
    """Main entry point for agent execution."""
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)
    
    try:
        # Parse input from command line
        input_data = json.loads(sys.argv[1])
        method = input_data.get("method")
        parameters = input_data.get("parameters", {})
        tool_context = input_data.get("tool_context", {})
        
        # Create agent instance with external tools
        external_tools = tool_context.get("available_tools", [])
        agent = ResearchAgent(external_tools=external_tools)
        
        # Set tool context for the agent
        agent.tool_context = tool_context
        
        # Execute requested method
        if method == "instant_research":
            result = agent.instant_research(parameters.get("question", ""))
            print(json.dumps({"result": result}))
        elif method == "quick_research":
            result = agent.quick_research(parameters.get("question", ""))
            print(json.dumps({"result": result}))
        elif method == "standard_research":
            result = agent.standard_research(parameters.get("question", ""))
            print(json.dumps({"result": result}))
        elif method == "deep_research":
            result = agent.deep_research(parameters.get("question", ""))
            print(json.dumps({"result": result}))
        elif method == "solve":
            # Handle async solve method
            result = asyncio.run(agent.solve(parameters.get("question", "")))
            print(json.dumps(result))
        else:
            print(json.dumps({"error": f"Unknown method: {method}"}))
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### agent.yaml (Project Root)
```yaml
name: "research-agent"
version: "1.0.0"
description: "Intelligent research agent with dynamic tool selection and multi-mode research capabilities"
author: "agentplug"
license: "MIT"
python_version: "3.11+"

installation:
  commands:
    - "python -m ensurepip --upgrade"
    - "python -m pip install --upgrade pip"
    - "pip install uv"
    - "uv venv .venv"
    - "uv pip install -e ."
    - "uv sync"
  description: "Install uv (via pip or curl fallback), then install the research agent and its dependencies using uv"

interface:
  methods:
    instant_research:
      description: "Instant research mode - Quick, direct answers in under 30 seconds using 1 round of research"
      parameters:
        question:
          type: "string"
          description: "Research question to investigate"
          required: true
      returns:
        type: "string"
        description: "Quick research results with direct answers"
    
    quick_research:
      description: "Quick research mode - Enhanced analysis with context in 1-2 minutes using 2 rounds of research"
      parameters:
        question:
          type: "string"
          description: "Research question to investigate"
          required: true
      returns:
        type: "string"
        description: "Enhanced research results with additional context"
    
    standard_research:
      description: "Standard research mode - Comprehensive coverage in 5-15 minutes using 3 rounds of research"
      parameters:
        question:
          type: "string"
          description: "Research question to investigate"
          required: true
      returns:
        type: "string"
        description: "Comprehensive research results with thorough analysis"
    
    deep_research:
      description: "Deep research mode - Exhaustive analysis with clarification in 15-30 minutes using 5 rounds of research"
      parameters:
        question:
          type: "string"
          description: "Research question to investigate"
          required: true
      returns:
        type: "string"
        description: "Exhaustive research results with comprehensive analysis and clarification questions"
    
    solve:
      description: "Auto mode selection - Automatically selects the best research mode based on question complexity"
      parameters:
        question:
          type: "string"
          description: "Research question to investigate"
          required: true
      returns:
        type: "object"
        description: "Research results with selected mode information"
        properties:
          mode:
            type: "string"
            description: "Selected research mode"
          result:
            type: "string"
            description: "Research results"
          status:
            type: "string"
            description: "Execution status"

tags: ["research", "ai-assistant", "multi-tool", "intelligent-analysis"]
```

### config.json (Project Root)
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
    "quick": "You are a research assistant for QUICK research mode. Provide enhanced analysis with additional context.",
    "standard": "You are a research assistant for STANDARD research mode. Conduct comprehensive research with multiple rounds of analysis. Provide thorough, well-structured responses.",
    "deep": "You are a research assistant for DEEP research mode. Conduct exhaustive research with clarification and comprehensive analysis. Provide detailed, well-researched responses with full context."
  }
}
```

### pyproject.toml (Project Root)
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "research-agent"
version = "1.0.0"
description = "Intelligent research agent with dynamic tool selection"
authors = [
    {name = "agentplug", email = "contact@agentplug.com"}
]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.11"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "openai>=1.0.0",
    "anthropic>=0.7.0",
    "google-generativeai>=0.3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]

[project.urls]
Homepage = "https://github.com/agentplug/research-agent"
Repository = "https://github.com/agentplug/research-agent"
Issues = "https://github.com/agentplug/research-agent/issues"

[tool.setuptools.packages.find]
where = ["."]
include = ["research_agent*"]

[tool.setuptools.package-data]
research_agent = ["py.typed"]

[tool.black]
line-length = 88
target-version = ['py311']

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### research_agent/__init__.py (Project Root)
```python
"""Research Agent - Intelligent research with dynamic tool selection."""

from .research_agent import ResearchAgent
from .base_agent import BaseAgent
from .llm_service import CoreLLMService, get_shared_llm_service

__version__ = "1.0.0"
__all__ = ['ResearchAgent', 'BaseAgent', 'CoreLLMService', 'get_shared_llm_service']
```

## Project Structure
```
research-agent/
├── agent.py                    # Main agent entry point
├── agent.yaml                  # Agent configuration
├── config.json                 # Runtime configuration
├── pyproject.toml             # Python packaging
├── README.md                  # Project documentation
├── research_agent/            # Main module
│   ├── __init__.py
│   ├── base_agent/            # BaseAgent module
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── context_manager.py
│   │   ├── error_handler.py
│   │   └── utils.py
│   ├── research_agent/        # ResearchAgent module
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── research_methods.py
│   │   └── tool_integration.py
│   └── llm_service/           # LLM service module
│       ├── __init__.py
│       ├── core.py
│       ├── providers.py
│       └── mock_service.py
└── tests/                     # Test files
    ├── test_base_agent.py
    ├── test_research_agent.py
    └── test_llm_service.py
```

## Testing Commands
```bash
# Test via AgentHub
ah.load_agent("agentplug/research-agent")

# Test individual methods
python agent.py '{"method": "instant_research", "parameters": {"question": "What is AI?"}}'
python agent.py '{"method": "quick_research", "parameters": {"question": "Latest AI developments"}}'
python agent.py '{"method": "standard_research", "parameters": {"question": "AI impact on society"}}'
python agent.py '{"method": "deep_research", "parameters": {"question": "Future of AI"}}'
python agent.py '{"method": "solve", "parameters": {"question": "What is machine learning?"}}'
```
