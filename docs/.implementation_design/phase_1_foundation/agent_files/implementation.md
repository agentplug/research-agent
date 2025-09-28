# Agent Files Implementation - Phase 1 Foundation

## Overview
The agent files provide the main entry point and configuration for the research agent, following AgentHub's interface requirements.

## Files to Create/Modify

### `agent.py` (Project Root)
- Main agent entry point
- Command-line interface
- JSON input/output handling
- Method routing

### `agent.yaml` (Project Root)
- Agent metadata and configuration
- Method definitions
- Parameter specifications
- Installation instructions

### `config.json` (Project Root)
- Runtime configuration
- AI parameters
- Research settings
- System prompts

### `pyproject.toml` (Project Root)
- Python package configuration
- Dependencies
- Build settings
- Metadata

## Implementation Details

### `agent.py` Structure
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
from typing import Dict, Any

# Import our modules
from research_agent import ResearchAgent
from llm_service import get_shared_llm_service

logger = logging.getLogger(__name__)

class ResearchAgentHub:
    """Research agent for AgentHub integration."""
    
    def __init__(self):
        """Initialize the research agent."""
        self.config = self._load_config()
        self.agent = ResearchAgent()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json file."""
        # Implementation details...

    def instant_research(self, question: str) -> str:
        """Instant research mode."""
        # Implementation details...

    def quick_research(self, question: str) -> str:
        """Quick research mode."""
        # Implementation details...

    def standard_research(self, question: str) -> str:
        """Standard research mode."""
        # Implementation details...

    def deep_research(self, question: str) -> str:
        """Deep research mode."""
        # Implementation details...

    async def solve(self, question: str) -> Dict[str, Any]:
        """Auto mode selection."""
        # Implementation details...

def main():
    """Main entry point for agent execution."""
    # Command-line interface implementation...

if __name__ == "__main__":
    main()
```

### `agent.yaml` Structure
```yaml
name: "research-agent"
version: "1.0.0"
description: "Intelligent research agent with multiple research modes"
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
  description: "Install uv and dependencies for the research agent"

interface:
  methods:
    instant_research:
      description: "Instant research mode - quick response using LLM-selected tools"
      parameters:
        question:
          type: "string"
          description: "Research question to investigate"
          required: true
      returns:
        type: "string"
        description: "Research results and analysis"
    
    quick_research:
      description: "Quick research mode - enhanced analysis with context-aware tool selection"
      parameters:
        question:
          type: "string"
          description: "Research question to investigate"
          required: true
      returns:
        type: "string"
        description: "Enhanced research results with analysis"
    
    standard_research:
      description: "Standard research mode - comprehensive analysis with multiple rounds"
      parameters:
        question:
          type: "string"
          description: "Research question to investigate"
          required: true
      returns:
        type: "string"
        description: "Comprehensive research results with thorough analysis"
    
    deep_research:
      description: "Deep research mode - exhaustive analysis with clarification questions"
      parameters:
        question:
          type: "string"
          description: "Research question to investigate"
          required: true
      returns:
        type: "string"
        description: "Exhaustive research results with comprehensive analysis and clarification questions"
    
    solve:
      description: "Auto mode selection based on question complexity and context"
      parameters:
        question:
          type: "string"
          description: "Research question to investigate"
          required: true
      returns:
        type: "object"
        description: "Research results with mode information and analysis"

tags: ["research", "ai-assistant", "intelligence", "analysis"]
```

### `config.json` Structure
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

### `pyproject.toml` Structure
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "research-agent"
version = "1.0.0"
description = "Intelligent research agent with multiple research modes"
authors = [{name = "agentplug", email = "contact@agentplug.com"}]
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
    "requests>=2.28.0",
    "aiohttp>=3.8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"
```

## Testing
- Command-line interface tests
- JSON input/output tests
- Method routing tests
- Configuration loading tests
- Error handling tests

## Dependencies
- ResearchAgent module
- LLM Service module
- Python 3.11+
- JSON handling
- Command-line argument parsing
