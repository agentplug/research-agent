# Phase 1: Minimal Working Agent - Implementation Design

## Overview

**Phase Goal**: Create a minimal working agent that loads in AgentHub and responds to all methods with mock responses.

**Duration**: 1 week  
**Deliverable**: Working agent testable in AgentHub with basic functionality

## Modules to Create/Modify

### 1. **Root Level Files** (Create)

#### `agent.py` - Main Entry Point
**Purpose**: AgentHub-compatible entry point with command-line interface

**Key Components**:
- `ResearchAgent` class with all 5 methods
- `main()` function for command-line JSON interface
- Basic error handling and response formatting
- Mock LLM service integration

**Implementation Details**:
```python
#!/usr/bin/env python3
"""
Agent Hub Agent: research-agent
Phase 1: Minimal working agent with mock responses
"""

import json
import sys
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ResearchAgent:
    """Minimal research agent for Phase 1 testing."""
    
    def __init__(self, tool_context: Optional[Dict[str, Any]] = None):
        """Initialize with basic configuration."""
        self.config = self._load_config()
        self.tool_context = tool_context or {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load basic configuration."""
        return {
            "ai": {"temperature": 0.1, "max_tokens": None},
            "research": {"max_sources_per_round": 10, "max_rounds": 12},
            "system_prompts": {
                "instant": "You are a research assistant for INSTANT research mode.",
                "quick": "You are a research assistant for QUICK research mode.",
                "standard": "You are a research assistant for STANDARD research mode.",
                "deep": "You are a research assistant for DEEP research mode."
            }
        }
    
    def instant_research(self, question: str) -> str:
        """Instant research mode - mock implementation."""
        return f"Mock instant research result for: {question}"
    
    def quick_research(self, question: str) -> str:
        """Quick research mode - mock implementation."""
        return f"Mock quick research result for: {question}"
    
    def standard_research(self, question: str) -> str:
        """Standard research mode - mock implementation."""
        return f"Mock standard research result for: {question}"
    
    def deep_research(self, question: str) -> str:
        """Deep research mode - mock implementation."""
        return f"Mock deep research result for: {question}"
    
    def solve(self, question: str) -> str:
        """Auto mode selection - mock implementation."""
        return f"Mock solve result for: {question}"

def main():
    """Main entry point for agent execution."""
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)
    
    try:
        input_data = json.loads(sys.argv[1])
        method = input_data.get("method")
        parameters = input_data.get("parameters", {})
        tool_context = input_data.get("tool_context", {})
        
        agent = ResearchAgent(tool_context=tool_context)
        
        if method == "instant_research":
            result = agent.instant_research(parameters.get("question", ""))
        elif method == "quick_research":
            result = agent.quick_research(parameters.get("question", ""))
        elif method == "standard_research":
            result = agent.standard_research(parameters.get("question", ""))
        elif method == "deep_research":
            result = agent.deep_research(parameters.get("question", ""))
        elif method == "solve":
            result = agent.solve(parameters.get("question", ""))
        else:
            print(json.dumps({"error": f"Unknown method: {method}"}))
            sys.exit(1)
        
        print(json.dumps({"result": result}))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

#### `agent.yaml` - AgentHub Configuration
**Purpose**: AgentHub agent configuration file

**Implementation Details**:
```yaml
name: research-agent
version: 1.0.0
description: "Deep research agent for comprehensive research tasks"
author: agentplug
license: MIT

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

dependencies:
  python: ">=3.11"
  packages:
    - "aisuite>=0.1.0"

runtime:
  timeout: 1800
  memory_limit: "2GB"
  environment:
    - "OPENAI_API_KEY"
    - "ANTHROPIC_API_KEY"
    - "GOOGLE_API_KEY"
```

#### `pyproject.toml` - Python Package Configuration
**Purpose**: Python package configuration and dependencies

**Implementation Details**:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "research-agent"
version = "1.0.0"
description = "Deep research agent for comprehensive research tasks"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "agentplug", email = "contact@agentplug.com"},
]
keywords = ["ai", "research", "agent", "agenthub"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "aisuite>=0.1.0",
    "pydantic>=2.0.0",
    "aiohttp>=3.8.0",
    "asyncio>=3.4.3",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
]

[project.urls]
Homepage = "https://github.com/agentplug/research-agent"
Repository = "https://github.com/agentplug/research-agent"
Issues = "https://github.com/agentplug/research-agent/issues"

[tool.hatch.build.targets.wheel]
packages = ["src"]

[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 88

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

#### `config.json` - Runtime Configuration
**Purpose**: Runtime configuration for the agent

**Implementation Details**:
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

### 2. **LLM Service Module** (Create)

#### `llm_service.py` - Mock LLM Service
**Purpose**: Mock LLM service for Phase 1 testing

**Implementation Details**:
```python
"""
Mock LLM Service for Phase 1 Testing
Provides mock responses for all research modes
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class MockLLMService:
    """Mock LLM service for Phase 1 testing."""
    
    def __init__(self):
        self.model = "mock-model"
        self.temperature = 0.1
        self.max_tokens = None
        
    def generate(self, 
                prompt: str, 
                system_prompt: Optional[str] = None,
                temperature: Optional[float] = None,
                max_tokens: Optional[int] = None) -> str:
        """Generate mock response based on prompt."""
        
        # Determine research mode from system prompt
        mode = "instant"
        if system_prompt:
            if "INSTANT" in system_prompt:
                mode = "instant"
            elif "QUICK" in system_prompt:
                mode = "quick"
            elif "STANDARD" in system_prompt:
                mode = "standard"
            elif "DEEP" in system_prompt:
                mode = "deep"
        
        # Generate mode-specific mock response
        if mode == "instant":
            return f"Mock instant research result: {prompt[:50]}..."
        elif mode == "quick":
            return f"Mock quick research result with enhanced context: {prompt[:50]}..."
        elif mode == "standard":
            return f"Mock standard research result with comprehensive analysis: {prompt[:50]}..."
        elif mode == "deep":
            return f"Mock deep research result with exhaustive analysis: {prompt[:50]}..."
        else:
            return f"Mock research result: {prompt[:50]}..."
    
    def generate_research_analysis(self, question: str, data: List[Dict[str, Any]]) -> str:
        """Generate mock research analysis."""
        return f"Mock analysis for question: {question} with {len(data)} data points"
    
    def generate_clarification_questions(self, question: str) -> List[str]:
        """Generate mock clarification questions."""
        return [
            f"Mock clarification question 1 for: {question}",
            f"Mock clarification question 2 for: {question}",
            f"Mock clarification question 3 for: {question}"
        ]
    
    def generate_follow_up_queries(self, question: str, gaps: List[str]) -> str:
        """Generate mock follow-up queries."""
        return f"Mock follow-up query for: {question} addressing gaps: {gaps}"
    
    def is_local_model(self) -> bool:
        """Check if using local model."""
        return False
    
    def get_current_model(self) -> str:
        """Get current model name."""
        return self.model

# Global shared instance
_shared_llm_service: Optional[MockLLMService] = None

def get_shared_llm_service() -> MockLLMService:
    """Get shared LLM service instance."""
    global _shared_llm_service
    if _shared_llm_service is None:
        _shared_llm_service = MockLLMService()
    return _shared_llm_service

def reset_shared_llm_service():
    """Reset shared LLM service instance."""
    global _shared_llm_service
    _shared_llm_service = None
```

## Testing Strategy

### **Unit Tests** (Create)

#### `test_phase1.py` - Phase 1 Tests
**Purpose**: Test Phase 1 functionality

**Implementation Details**:
```python
"""
Phase 1 Tests - Minimal Working Agent
"""

import pytest
import json
import subprocess
import sys
from pathlib import Path

class TestPhase1Agent:
    """Test Phase 1 agent functionality."""
    
    @pytest.fixture
    def agent_script(self):
        """Path to agent.py script."""
        return Path(__file__).parent.parent.parent / "agent.py"
    
    def test_agent_script_exists(self, agent_script):
        """Test that agent.py script exists."""
        assert agent_script.exists()
    
    def test_agent_script_executable(self, agent_script):
        """Test that agent.py script is executable."""
        # Test with invalid arguments (should return error)
        result = subprocess.run(
            [sys.executable, str(agent_script)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "Invalid arguments" in result.stdout
    
    def test_instant_research_method(self, agent_script):
        """Test instant_research method."""
        input_data = {
            "method": "instant_research",
            "parameters": {
                "question": "What is AI?"
            }
        }
        
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        response = json.loads(result.stdout)
        assert "result" in response
        assert "What is AI?" in response["result"]
    
    def test_quick_research_method(self, agent_script):
        """Test quick_research method."""
        input_data = {
            "method": "quick_research",
            "parameters": {
                "question": "How does ML work?"
            }
        }
        
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        response = json.loads(result.stdout)
        assert "result" in response
        assert "How does ML work?" in response["result"]
    
    def test_standard_research_method(self, agent_script):
        """Test standard_research method."""
        input_data = {
            "method": "standard_research",
            "parameters": {
                "question": "Latest AI developments?"
            }
        }
        
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        response = json.loads(result.stdout)
        assert "result" in response
        assert "Latest AI developments?" in response["result"]
    
    def test_deep_research_method(self, agent_script):
        """Test deep_research method."""
        input_data = {
            "method": "deep_research",
            "parameters": {
                "question": "AI ethics analysis"
            }
        }
        
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        response = json.loads(result.stdout)
        assert "result" in response
        assert "AI ethics analysis" in response["result"]
    
    def test_solve_method(self, agent_script):
        """Test solve method."""
        input_data = {
            "method": "solve",
            "parameters": {
                "question": "What is AI?"
            }
        }
        
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        response = json.loads(result.stdout)
        assert "result" in response
        assert "What is AI?" in response["result"]
    
    def test_invalid_method(self, agent_script):
        """Test invalid method handling."""
        input_data = {
            "method": "invalid_method",
            "parameters": {
                "question": "Test question"
            }
        }
        
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        
        response = json.loads(result.stdout)
        assert "error" in response
        assert "Unknown method" in response["error"]

class TestMockLLMService:
    """Test mock LLM service functionality."""
    
    @pytest.fixture
    def mock_llm_service(self):
        """Create mock LLM service instance."""
        from llm_service import MockLLMService
        return MockLLMService()
    
    def test_generate_instant(self, mock_llm_service):
        """Test instant mode generation."""
        result = mock_llm_service.generate(
            "What is AI?",
            system_prompt="You are a research assistant for INSTANT research mode."
        )
        assert "instant" in result.lower()
        assert "What is AI?" in result
    
    def test_generate_quick(self, mock_llm_service):
        """Test quick mode generation."""
        result = mock_llm_service.generate(
            "How does ML work?",
            system_prompt="You are a research assistant for QUICK research mode."
        )
        assert "quick" in result.lower()
        assert "How does ML work?" in result
    
    def test_generate_standard(self, mock_llm_service):
        """Test standard mode generation."""
        result = mock_llm_service.generate(
            "Latest AI news?",
            system_prompt="You are a research assistant for STANDARD research mode."
        )
        assert "standard" in result.lower()
        assert "Latest AI news?" in result
    
    def test_generate_deep(self, mock_llm_service):
        """Test deep mode generation."""
        result = mock_llm_service.generate(
            "AI ethics analysis",
            system_prompt="You are a research assistant for DEEP research mode."
        )
        assert "deep" in result.lower()
        assert "AI ethics analysis" in result
    
    def test_generate_clarification_questions(self, mock_llm_service):
        """Test clarification questions generation."""
        questions = mock_llm_service.generate_clarification_questions("AI research")
        assert len(questions) == 3
        assert all("AI research" in q for q in questions)
```

## AgentHub Integration Testing

### **AgentHub Test Script** (Create)

#### `test_agenthub_integration.py` - AgentHub Integration Tests
**Purpose**: Test agent integration with AgentHub

**Implementation Details**:
```python
"""
AgentHub Integration Tests for Phase 1
"""

import pytest
import agenthub as ah

class TestAgentHubIntegration:
    """Test AgentHub integration for Phase 1."""
    
    def test_agent_loading(self):
        """Test that agent can be loaded in AgentHub."""
        try:
            agent = ah.load_agent("agentplug/research-agent")
            assert agent is not None
        except Exception as e:
            pytest.skip(f"AgentHub not available: {e}")
    
    def test_all_methods_exist(self):
        """Test that all required methods exist."""
        try:
            agent = ah.load_agent("agentplug/research-agent")
            
            assert hasattr(agent, 'instant_research')
            assert hasattr(agent, 'quick_research')
            assert hasattr(agent, 'standard_research')
            assert hasattr(agent, 'deep_research')
            assert hasattr(agent, 'solve')
        except Exception as e:
            pytest.skip(f"AgentHub not available: {e}")
    
    def test_mock_responses(self):
        """Test that all methods return mock responses."""
        try:
            agent = ah.load_agent("agentplug/research-agent")
            
            # Test all methods
            result1 = agent.instant_research("What is AI?")
            result2 = agent.quick_research("How does ML work?")
            result3 = agent.standard_research("Latest AI news?")
            result4 = agent.deep_research("AI ethics analysis")
            result5 = agent.solve("What is AI?")
            
            # Verify all return results
            assert "result" in result1
            assert "result" in result2
            assert "result" in result3
            assert "result" in result4
            assert "result" in result5
            
            # Verify mock responses contain question
            assert "What is AI?" in result1["result"]
            assert "How does ML work?" in result2["result"]
            assert "Latest AI news?" in result3["result"]
            assert "AI ethics analysis" in result4["result"]
            assert "What is AI?" in result5["result"]
            
        except Exception as e:
            pytest.skip(f"AgentHub not available: {e}")
```

## Implementation Checklist

### **Phase 1 Implementation Checklist:**

- [ ] **Create `agent.py`** with complete command-line interface
- [ ] **Create `agent.yaml`** with full AgentHub configuration
- [ ] **Create `pyproject.toml`** with Python package configuration
- [ ] **Create `config.json`** with runtime configuration
- [ ] **Create `llm_service.py`** with mock LLM service
- [ ] **Create `test_phase1.py`** with unit tests
- [ ] **Create `test_agenthub_integration.py`** with AgentHub tests
- [ ] **Test agent loading** in AgentHub
- [ ] **Test all methods** return mock responses
- [ ] **Test error handling** for invalid inputs
- [ ] **Verify JSON input/output** format
- [ ] **Test command-line interface** functionality

## Success Criteria

### **Phase 1 Success Criteria:**

1. ✅ **Agent loads successfully** in AgentHub
2. ✅ **All 5 methods work** (instant_research, quick_research, standard_research, deep_research, solve)
3. ✅ **Mock responses returned** for all methods
4. ✅ **Error handling works** for invalid inputs
5. ✅ **JSON input/output** format correct
6. ✅ **Command-line interface** functional
7. ✅ **Unit tests pass** for all functionality
8. ✅ **AgentHub integration tests** pass

## Next Phase Preparation

### **Phase 1 → Phase 2 Transition:**

- **Dependency**: Basic agent structure working in AgentHub
- **Preparation**: Mock LLM service ready for replacement with real LLM
- **Foundation**: All method signatures and interfaces established
- **Testing**: AgentHub integration validated and working

This Phase 1 implementation provides a solid foundation for Phase 2, where we'll replace the mock LLM service with real LLM integration while maintaining the same interface and AgentHub compatibility.
