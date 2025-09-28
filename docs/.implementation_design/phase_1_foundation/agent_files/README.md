# Agent Entry Point - Phase 1 Foundation

## Overview

The agent entry point (`agent.py`) serves as the main interface between the research agent and AgentHub, following the standard AgentHub pattern for agent integration.

## File Structure

```
research-agent/
├── agent.py                    # Main entry point (AgentHub pattern)
├── agent.yaml                  # AgentHub configuration
├── pyproject.toml              # Python package configuration
├── config.json                 # Runtime configuration
└── research_agent/             # Agent modules
```

## Key Components

### 1. Agent Entry Point (`agent.py`)

**Purpose**: Main entry point following AgentHub pattern

**Key Features**:
- Command-line JSON interface
- Method routing and execution
- Error handling and response formatting
- Configuration loading
- Tool context parsing

**Implementation Structure**:
```python
#!/usr/bin/env python3
"""
Agent Hub Agent: research-agent
Conducts comprehensive research using multiple tools and sources.
"""

import json
import sys
import os
import logging
from typing import Dict, Any, Optional, List

# Import our modular LLM service
from llm_service import CoreLLMService, get_shared_llm_service

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Deep research agent for comprehensive research tasks."""
    
    def __init__(self, tool_context: Optional[Dict[str, Any]] = None):
        """Initialize the research agent."""
        self.config = self._load_config()
        self.llm_service = get_shared_llm_service()
        
        # Parse tool context from AgentHub
        self.tool_context = tool_context or {}
        self.available_tools = self.tool_context.get("available_tools", [])
        self.tool_descriptions = self.tool_context.get("tool_descriptions", {})
    
    def instant_research(self, question: str) -> str:
        """Conduct instant research (1 round, 10 sources, 15-30 sec)."""
        # Implementation details
    
    def quick_research(self, question: str) -> str:
        """Conduct quick research (2 rounds, 20 sources, 1-2 min)."""
        # Implementation details
    
    def standard_research(self, question: str) -> str:
        """Conduct standard research (2-5 rounds, 20-50 sources, 8-15 min)."""
        # Implementation details
    
    def deep_research(self, question: str) -> str:
        """Conduct deep research (5-12 rounds, 50-120 sources, 20-30 min)."""
        # Implementation details
    
    def solve(self, question: str) -> str:
        """Universal solve method with auto mode selection."""
        # Implementation details


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
        
        # Create agent instance with tool context
        agent = ResearchAgent(tool_context=tool_context)
        
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
            result = agent.solve(parameters.get("question", ""))
            print(json.dumps({"result": result}))
        else:
            print(json.dumps({"error": f"Unknown method: {method}"}))
            sys.exit(1)
            
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 2. AgentHub Configuration (`agent.yaml`)

**Purpose**: AgentHub configuration file

**Key Features**:
- Agent metadata and description
- Method definitions and parameters
- Installation instructions
- Interface specifications

**Configuration Structure**:
```yaml
name: "research-agent"
version: "1.0.0"
description: "Deep research agent with multiple research modes for comprehensive information gathering"
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
      description: "Get immediate answers to simple questions using direct tool queries and basic analysis. Executes in 15-30 seconds with 1 research round and 10 sources. Perfect for quick facts, definitions, or straightforward information needs when speed is critical."
      parameters:
        question:
          type: "string"
          description: "Research question or topic"
          required: true
      returns:
        type: "string"
        description: "Direct research results with key facts and essential information"
    
    quick_research:
      description: "Perform enhanced research with context-aware analysis across multiple rounds. Executes in 1-2 minutes with 2 research rounds and 20 sources. Analyzes initial results to improve follow-up queries and provides comprehensive answers with additional context. Ideal for moderate complexity questions requiring some depth."
      parameters:
        question:
          type: "string"
          description: "Research question or topic"
          required: true
      returns:
        type: "string"
        description: "Enhanced research results with context and detailed insights"
    
    standard_research:
      description: "Conduct comprehensive research with systematic gap analysis and iterative refinement. Executes in 8-15 minutes with 5 research rounds and 50 sources. Identifies information gaps, generates targeted follow-up queries, and synthesizes results from multiple research rounds for thorough coverage. Best for complex topics requiring detailed analysis."
      parameters:
        question:
          type: "string"
          description: "Research question or topic"
          required: true
      returns:
        type: "string"
        description: "Comprehensive research results with thorough analysis and synthesis"
    
    deep_research:
      description: "Execute exhaustive research with clarification questions and maximum depth analysis. Executes in 20-30 minutes with 12 research rounds and 120 sources. Generates clarification questions to better understand requirements, conducts extensive gap analysis, and provides academic-level comprehensive research with full context and detailed findings. Perfect for research projects requiring exhaustive analysis."
      parameters:
        question:
          type: "string"
          description: "Research question or topic"
          required: true
      returns:
        type: "string"
        description: "Exhaustive research results with comprehensive analysis and detailed findings"
    
    solve:
      description: "Automatically select the most appropriate research mode based on question complexity, context, and available time. Uses intelligent analysis to determine whether instant (15-30s), quick (1-2min), standard (8-15min), or deep (20-30min) research is needed for optimal results. Considers both research depth requirements and time constraints."
      parameters:
        question:
          type: "string"
          description: "Research question or topic"
          required: true
      returns:
        type: "string"
        description: "Research results using the most appropriate research mode"

tags: ["research", "information-gathering", "ai-assistant", "analysis"]
```

### 3. Python Package Configuration (`pyproject.toml`)

**Purpose**: Python package configuration

**Key Features**:
- Package metadata
- Dependencies
- Build configuration
- Scripts and entry points

**Configuration Structure**:
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "research-agent"
version = "1.0.0"
description = "Deep research agent for AgentHub - comprehensive information gathering with multiple research modes"
authors = [{ name = "agentplug" }]
license = { text = "MIT" }
readme = "README.md"
requires-python = ">=3.11"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
]
keywords = ["research", "information-gathering", "ai-assistant", "analysis"]

dependencies = [
    "aisuite[openai]>=0.1.7",
    "python-dotenv>=1.0.0",
    "docstring-parser>=0.17.0",
]

[project.scripts]
research-agent = "agent:main"

[project.urls]
Homepage = "https://github.com/agentplug/research-agent"
Repository = "https://github.com/agentplug/research-agent"
Issues = "https://github.com/agentplug/research-agent/issues"

[tool.setuptools.packages.find]
where = ["."]
include = ["*"]

[tool.setuptools.package-data]
"*" = ["*.yaml", "*.yml", "*.json"]
```

### 4. Runtime Configuration (`config.json`)

**Purpose**: Runtime configuration file

**Key Features**:
- LLM service configuration
- Research mode settings
- System prompts
- Error messages

**Configuration Structure**:
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
    "instant": "You are a research assistant for INSTANT research mode. Provide quick, accurate answers based on available data. Focus on key facts and essential information. Use tools efficiently to get immediate results.",
    "quick": "You are a research assistant for QUICK research mode. Analyze data and provide enhanced answers with context. Include relevant details and insights. Use tools to gather additional information for better context.",
    "standard": "You are a research assistant for STANDARD research mode. Conduct comprehensive research with multiple rounds of analysis. Provide thorough, well-structured responses. Use tools extensively to gather comprehensive information.",
    "deep": "You are a research assistant for DEEP research mode. Conduct exhaustive research with clarification and comprehensive analysis. Provide detailed, well-researched responses with full context. Use tools extensively and analyze gaps in information."
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

## Testing Strategy

### AgentHub Integration Tests
```python
import agenthub as ah

# Load the agent
agent = ah.load_agent("agentplug/research-agent")

# Test all methods (all return mock responses)
result1 = agent.instant_research("What is AI?")
result2 = agent.quick_research("How does ML work?")
result3 = agent.standard_research("Latest AI news?")
result4 = agent.deep_research("AI ethics analysis")
result5 = agent.solve("What is artificial intelligence?")

# Expected: All methods return JSON responses with mock data
# Example response:
# {
#   "result": "Mock research result for: What is AI?",
#   "mode": "instant",
#   "sources": ["mock_source_1", "mock_source_2"],
#   "status": "success"
# }
```

### Command Line Tests
```bash
# Test agent.py directly
python agent.py '{"method": "instant_research", "parameters": {"question": "What is AI?"}}'

# Expected output:
# {"result": "Mock research result for: What is AI?"}
```

## Success Criteria

- [ ] Agent loads successfully in AgentHub
- [ ] All 5 methods execute without errors
- [ ] Mock responses demonstrate mode differences
- [ ] Error handling works for invalid inputs
- [ ] JSON responses are properly formatted
- [ ] Configuration loading works correctly
- [ ] Tool context parsing works (when provided)

## Next Steps

This entry point provides the foundation for:
- Real LLM integration (Phase 2)
- External tool integration (Phase 3)
- Production-ready features (Phase 4)

The agent entry point will be enhanced with real LLM integration in Phase 2, external tool integration in Phase 3, and production-ready features in Phase 4.
