# Phase 1: Minimal Working Agent - Implementation Design

## Overview

**Phase Goal**: Create a minimal working agent that loads in AgentHub and responds to all methods with mock responses.

**Duration**: 1 week  
**Deliverable**: Working agent testable in AgentHub with basic functionality

## Modules to Create/Modify

### 1. **BaseAgent Module** (Create)

#### `src/base_agent/` - Base Agent Foundation
**Purpose**: Common agent capabilities shared across all agent types

**Key Components**:
- `BaseAgent` abstract base class
- Context management and state handling
- Error handling and logging
- Common utility functions
- Universal `solve()` method interface

**Implementation Details**:
```python
# src/base_agent/__init__.py
"""
BaseAgent Module - Common agent capabilities
"""

from .core import BaseAgent
from .context_manager import ContextManager
from .error_handler import ErrorHandler
from .utils import validate_input_data, format_response

__all__ = [
    "BaseAgent",
    "ContextManager", 
    "ErrorHandler",
    "validate_input_data",
    "format_response"
]
```

```python
# src/base_agent/core.py
"""
BaseAgent - Common agent capabilities for all agent types
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
import uuid
from datetime import datetime

from .context_manager import ContextManager
from .error_handler import ErrorHandler
from .utils import validate_input_data, format_response

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base agent class with common capabilities shared across all agents.
    
    This abstract base class provides:
    - LLM service integration
    - Error handling and logging
    - Context management
    - Input validation
    - Universal solve() method interface
    - Tool management
    - Configuration management
    """
    
    def __init__(self, llm_service=None, external_tools: Optional[List[str]] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize base agent with common capabilities.
        
        Args:
            llm_service: LLM service instance
            external_tools: List of available external tools
            config: Optional configuration dictionary
        """
        self.llm_service = llm_service
        self.external_tools = external_tools or []
        self.config = config or {}
        self.context_manager = ContextManager()
        self.error_handler = ErrorHandler()
        self.agent_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.agent_type = self.__class__.__name__
        
        logger.info(f"BaseAgent initialized: {self.agent_type} with ID: {self.agent_id}")
    
    @abstractmethod
    async def solve(self, question: str) -> Dict[str, Any]:
        """
        Universal solve method - to be implemented by subclasses.
        
        Args:
            question: Question or task to solve
            
        Returns:
            Dictionary containing solution and metadata
        """
        pass
    
    def get_available_tools(self) -> List[str]:
        """Get list of available external tools."""
        return self.external_tools.copy()
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data using common validation rules.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if input is valid, False otherwise
        """
        return validate_input_data(input_data)
    
    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle errors with common error handling logic.
        
        Args:
            error: Exception that occurred
            context: Additional context about the error
            
        Returns:
            Dictionary containing error information
        """
        return await self.error_handler.handle_error(error, context)
    
    def set_context(self, key: str, value: Any):
        """Set context value for the agent."""
        self.context_manager.set_context(key, value)
    
    def get_context(self, key: str = None) -> Any:
        """Get context value from the agent."""
        return self.context_manager.get_context(key)
    
    def clear_context(self):
        """Clear all context data."""
        self.context_manager.clear_context()
    
    def format_response(self, result: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format response using common formatting rules.
        
        Args:
            result: Result data to format
            metadata: Additional metadata
            
        Returns:
            Formatted response dictionary
        """
        return format_response(result, metadata)
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information and status."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "created_at": self.created_at.isoformat(),
            "available_tools": self.get_available_tools(),
            "context_keys": list(self.context_manager.get_context().keys()) if self.context_manager.get_context() else [],
            "config_keys": list(self.config.keys()) if self.config else []
        }
    
    def get_available_tools(self) -> List[str]:
        """Get list of available external tools."""
        return self.external_tools.copy()
    
    def add_tool(self, tool_name: str):
        """Add a tool to available tools."""
        if tool_name not in self.external_tools:
            self.external_tools.append(tool_name)
            logger.info(f"Added tool: {tool_name}")
    
    def remove_tool(self, tool_name: str):
        """Remove a tool from available tools."""
        if tool_name in self.external_tools:
            self.external_tools.remove(tool_name)
            logger.info(f"Removed tool: {tool_name}")
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if agent has access to a specific tool."""
        return tool_name in self.external_tools
    
    def get_config(self, key: str = None, default: Any = None) -> Any:
        """Get configuration value."""
        if key is None:
            return self.config.copy()
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
        logger.debug(f"Config set: {key}")
    
    def update_config(self, config_updates: Dict[str, Any]):
        """Update multiple configuration values."""
        self.config.update(config_updates)
        logger.debug(f"Config updated with {len(config_updates)} keys")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get agent health status."""
        return {
            "status": "healthy",
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "uptime": (datetime.now() - self.created_at).total_seconds(),
            "tools_count": len(self.external_tools),
            "context_size": len(self.context_manager.get_context()),
            "config_size": len(self.config),
            "llm_service_available": self.llm_service is not None
        }
```

```python
# src/base_agent/context_manager.py
"""
Context Manager for BaseAgent
Manages agent context and state
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ContextManager:
    """Manages agent context and state."""
    
    def __init__(self):
        self.context: Dict[str, Any] = {}
        self.session_id: Optional[str] = None
    
    def set_context(self, key: str, value: Any):
        """Set context value."""
        self.context[key] = value
        logger.debug(f"Context set: {key}")
    
    def get_context(self, key: str = None) -> Any:
        """Get context value."""
        if key is None:
            return self.context.copy()
        return self.context.get(key)
    
    def clear_context(self):
        """Clear all context."""
        self.context.clear()
        logger.debug("Context cleared")
```

```python
# src/base_agent/error_handler.py
"""
Error Handler for BaseAgent
Provides common error handling and logging
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Common error handling and logging for agents."""
    
    def __init__(self):
        self.error_count = 0
        self.error_types: Dict[str, int] = {}
    
    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle error with common error handling logic.
        
        Args:
            error: Exception that occurred
            context: Additional context about the error
            
        Returns:
            Dictionary containing error information
        """
        self.error_count += 1
        error_type = type(error).__name__
        self.error_types[error_type] = self.error_types.get(error_type, 0) + 1
        
        error_info = {
            "error_type": error_type,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
            "error_count": self.error_count
        }
        
        logger.error(f"Error {self.error_count}: {error_type} - {str(error)}")
        if context:
            logger.debug(f"Error context: {context}")
        
        return error_info
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "total_errors": self.error_count,
            "error_types": self.error_types
        }
```

```python
# src/base_agent/utils.py
"""
Utility functions for BaseAgent
Common utility functions used across agents
"""

from typing import Dict, Any, Optional
import json

def validate_input_data(input_data: Dict[str, Any]) -> bool:
    """
    Validate input data using common validation rules.
    
    Args:
        input_data: Input data to validate
        
    Returns:
        True if input is valid, False otherwise
    """
    if not isinstance(input_data, dict):
        return False
    
    # Check for required fields
    if "method" not in input_data:
        return False
    
    if "parameters" not in input_data:
        return False
    
    return True

def format_response(result: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Format response using common formatting rules.
    
    Args:
        result: Result data to format
        metadata: Additional metadata
        
    Returns:
        Formatted response dictionary
    """
    response = {
        "result": result,
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }
    
    if metadata:
        response.update(metadata)
    
    return response
```

### 2. **Root Level Files** (Create)

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

# Import BaseAgent
from src.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ResearchAgent(BaseAgent):
    """Minimal research agent for Phase 1 testing."""
    
    def __init__(self, tool_context: Optional[Dict[str, Any]] = None):
        """Initialize with basic configuration."""
        # Initialize BaseAgent
        super().__init__(external_tools=tool_context.get("available_tools", []) if tool_context else [])
        
        self.config = self._load_config()
        self.tool_context = tool_context or {}
        
        # Initialize LLM service for research agent
        self.llm_service = get_shared_llm_service(agent_type="research")
        
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
    
    async def solve(self, question: str) -> Dict[str, Any]:
        """Auto mode selection - mock implementation."""
        try:
            # Simple auto mode selection based on question length
            if len(question) < 50:
                result = self.instant_research(question)
                mode = "instant"
            elif len(question) < 100:
                result = self.quick_research(question)
                mode = "quick"
            elif len(question) < 200:
                result = self.standard_research(question)
                mode = "standard"
            else:
                result = self.deep_research(question)
                mode = "deep"
            
            return self.format_response(result, {"mode": mode, "auto_selected": True})
            
        except Exception as e:
            error_info = await self.handle_error(e, {"method": "solve", "question": question})
            return self.format_response(f"Error in solve: {str(e)}", {"error": error_info, "status": "error"})

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
            import asyncio
            result = asyncio.run(agent.solve(parameters.get("question", "")))
        else:
            print(json.dumps({"error": f"Unknown method: {method}"}))
            sys.exit(1)
        
        if method == "solve":
            print(json.dumps(result))
        else:
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
    """Mock LLM service for Phase 1 testing - Generic and reusable."""
    
    def __init__(self, agent_type: str = "generic"):
        self.model = "mock-model"
        self.temperature = 0.1
        self.max_tokens = None
        self.agent_type = agent_type
        
    def generate(self, 
                prompt: str, 
                system_prompt: Optional[str] = None,
                temperature: Optional[float] = None,
                max_tokens: Optional[int] = None) -> str:
        """Generate mock response based on prompt and agent type."""
        
        # Determine mode from system prompt or agent type
        mode = "generic"
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
            return f"Mock instant response for {self.agent_type}: {prompt[:50]}..."
        elif mode == "quick":
            return f"Mock quick response for {self.agent_type}: {prompt[:50]}..."
        elif mode == "standard":
            return f"Mock standard response for {self.agent_type}: {prompt[:50]}..."
        elif mode == "deep":
            return f"Mock deep response for {self.agent_type}: {prompt[:50]}..."
        else:
            return f"Mock {self.agent_type} response: {prompt[:50]}..."
    
    def generate_analysis(self, question: str, data: List[Dict[str, Any]]) -> str:
        """Generate mock analysis from data."""
        return f"Mock analysis for {self.agent_type}: {question} with {len(data)} data points"
    
    def generate_questions(self, topic: str, count: int = 3) -> List[str]:
        """Generate mock questions for a topic."""
        return [
            f"Mock question 1 for {self.agent_type}: {topic}",
            f"Mock question 2 for {self.agent_type}: {topic}",
            f"Mock question 3 for {self.agent_type}: {topic}"
        ][:count]
    
    def generate_summary(self, content: str) -> str:
        """Generate mock summary of content."""
        return f"Mock summary for {self.agent_type}: {content[:100]}..."
    
    def is_local_model(self) -> bool:
        """Check if using local model."""
        return False
    
    def get_current_model(self) -> str:
        """Get current model name."""
        return self.model
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get LLM service information."""
        return {
            "model": self.model,
            "agent_type": self.agent_type,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "is_local": self.is_local_model()
        }

# Global shared instance
_shared_llm_service: Optional[MockLLMService] = None

def get_shared_llm_service(agent_type: str = "generic") -> MockLLMService:
    """Get shared LLM service instance."""
    global _shared_llm_service
    if _shared_llm_service is None:
        _shared_llm_service = MockLLMService(agent_type=agent_type)
    return _shared_llm_service

def reset_shared_llm_service():
    """Reset shared LLM service instance."""
    global _shared_llm_service
    _shared_llm_service = None

def create_llm_service(agent_type: str = "generic") -> MockLLMService:
    """Create a new LLM service instance."""
    return MockLLMService(agent_type=agent_type)
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

- [ ] **Create `src/base_agent/`** module with BaseAgent foundation
- [ ] **Create `src/base_agent/__init__.py`** with module exports
- [ ] **Create `src/base_agent/core.py`** with BaseAgent class
- [ ] **Create `src/base_agent/context_manager.py`** with context management
- [ ] **Create `src/base_agent/error_handler.py`** with error handling
- [ ] **Create `src/base_agent/utils.py`** with utility functions
- [ ] **Create `agent.py`** with ResearchAgent inheriting from BaseAgent
- [ ] **Create `agent.yaml`** with full AgentHub configuration
- [ ] **Create `pyproject.toml`** with Python package configuration
- [ ] **Create `config.json`** with runtime configuration
- [ ] **Create `llm_service.py`** with mock LLM service
- [ ] **Create `test_phase1.py`** with unit tests
- [ ] **Create `test_agenthub_integration.py`** with AgentHub tests
- [ ] **Test BaseAgent** functionality and inheritance
- [ ] **Test agent loading** in AgentHub
- [ ] **Test all methods** return mock responses
- [ ] **Test error handling** for invalid inputs
- [ ] **Verify JSON input/output** format
- [ ] **Test command-line interface** functionality

## Success Criteria

### **Phase 1 Success Criteria:**

1. ✅ **BaseAgent module** created and functional
2. ✅ **ResearchAgent inherits** from BaseAgent correctly
3. ✅ **Agent loads successfully** in AgentHub
4. ✅ **All 5 methods work** (instant_research, quick_research, standard_research, deep_research, solve)
5. ✅ **Mock responses returned** for all methods
6. ✅ **Error handling works** for invalid inputs
7. ✅ **JSON input/output** format correct
8. ✅ **Command-line interface** functional
9. ✅ **Unit tests pass** for all functionality
10. ✅ **AgentHub integration tests** pass

## Next Phase Preparation

### **Phase 1 → Phase 2 Transition:**

- **Dependency**: BaseAgent module and ResearchAgent inheritance working in AgentHub
- **Preparation**: Mock LLM service ready for replacement with real LLM
- **Foundation**: All method signatures and interfaces established with BaseAgent
- **Testing**: AgentHub integration validated and working

## Reusability Examples

### **Example: Creating Other Agent Types**

The BaseAgent and LLM service are designed to be reusable across different agent types:

```python
# Example: Coding Agent
from src.base_agent import BaseAgent
from llm_service import get_shared_llm_service

class CodingAgent(BaseAgent):
    """Coding agent using reusable BaseAgent and LLM service."""
    
    def __init__(self, tool_context=None):
        super().__init__(external_tools=tool_context.get("available_tools", []) if tool_context else [])
        self.llm_service = get_shared_llm_service(agent_type="coding")
    
    async def solve(self, question: str) -> Dict[str, Any]:
        """Solve coding problems."""
        try:
            result = self.llm_service.generate(f"Coding question: {question}")
            return self.format_response(result, {"agent_type": "coding"})
        except Exception as e:
            error_info = await self.handle_error(e, {"method": "solve", "question": question})
            return self.format_response(f"Error: {str(e)}", {"error": error_info, "status": "error"})
    
    def generate_code(self, requirements: str) -> str:
        """Generate code based on requirements."""
        return self.llm_service.generate(f"Generate code for: {requirements}")

# Example: Analysis Agent
class AnalysisAgent(BaseAgent):
    """Analysis agent using reusable BaseAgent and LLM service."""
    
    def __init__(self, tool_context=None):
        super().__init__(external_tools=tool_context.get("available_tools", []) if tool_context else [])
        self.llm_service = get_shared_llm_service(agent_type="analysis")
    
    async def solve(self, question: str) -> Dict[str, Any]:
        """Solve analysis problems."""
        try:
            result = self.llm_service.generate(f"Analysis question: {question}")
            return self.format_response(result, {"agent_type": "analysis"})
        except Exception as e:
            error_info = await self.handle_error(e, {"method": "solve", "question": question})
            return self.format_response(f"Error: {str(e)}", {"error": error_info, "status": "error"})
    
    def analyze_data(self, data: List[Dict[str, Any]]) -> str:
        """Analyze data using LLM service."""
        return self.llm_service.generate_analysis("Analyze this data", data)
```

### **Tool Usage Documentation**

#### **How to Use External Tools with BaseAgent**

The BaseAgent provides comprehensive tool management capabilities for working with external tools provided by AgentHub:

```python
from src.base_agent import BaseAgent
from llm_service import get_shared_llm_service

class ResearchAgent(BaseAgent):
    def __init__(self, tool_context=None):
        super().__init__(external_tools=tool_context.get("available_tools", []) if tool_context else [])
        self.tool_context = tool_context or {}
        self.llm_service = get_shared_llm_service(agent_type="research")
    
    def _call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Call an external tool with parameters."""
        if not self.has_tool(tool_name):
            raise ValueError(f"Tool '{tool_name}' not available")
        
        # Get tool information from context
        tool_info = self.tool_context.get("tool_descriptions", {}).get(tool_name)
        if not tool_info:
            raise ValueError(f"Tool '{tool_name}' not found in tool context")
        
        # Example tool calling logic (this would be implemented based on AgentHub's tool system)
        # In real implementation, this would interface with AgentHub's tool calling mechanism
        return f"Mock result from {tool_name} with parameters: {parameters}"
    
    def _execute_dynamic_research(self, question: str, mode: str) -> str:
        """Execute dynamic research with LLM deciding tools for each round."""
        try:
            tools_info = self._get_available_tools_info()
            available_tools = tools_info["available_tools"]
            
            if not available_tools:
                return f"No tools available for research: {question}"
            
            # Initialize research state
            research_data = []
            max_iterations = self._get_max_iterations_for_mode(mode)
            
            for iteration in range(max_iterations):
                # LLM decides which tools to use for this round
                tools_to_use = self._select_tools_for_round(
                    question, mode, research_data, available_tools, iteration
                )
                
                if not tools_to_use:
                    break  # No tools selected for this round
                
                # Execute tools for this round
                round_results = []
                for tool_name in tools_to_use:
                    tool_result = self._call_tool(tool_name, {"query": question})
                    round_results.append(f"{tool_name}: {tool_result}")
                
                if round_results:
                    research_data.extend(round_results)
                
                # Check if research is complete
                if self._is_research_complete(question, research_data, mode):
                    break
            
            # Generate final response
            return self._generate_final_response(question, research_data, mode)
            
        except Exception as e:
            return f"Error in dynamic research: {str(e)}"
    
    def _select_tools_for_round(self, question: str, mode: str, research_data: List[str], 
                               available_tools: List[str], iteration: int) -> List[str]:
        """Use LLM to analyze research progress and decide what to do next."""
        try:
            tools_info = self._get_available_tools_info()
            tool_descriptions = tools_info["tool_descriptions"]
            tool_list = "\n".join([f"- {tool}: {desc}" for tool, desc in tool_descriptions.items()])
            
            # Create context about current research state
            current_context = ""
            if research_data:
                current_context = f"\nResearch progress from previous rounds:\n{chr(10).join(research_data)}"
            
            # First, analyze what has been done and what's missing
            analysis_prompt = f"""
Research question: {question}
Research mode: {mode}
Current round: {iteration + 1}

Research progress from previous rounds:
{current_context if current_context else "No previous research data - this is the first round."}

Analyze the current research progress and identify:
1. What information has been gathered so far?
2. What information is still missing or incomplete?
3. What are the next steps needed to complete this research?
4. What specific gaps need to be filled?

Based on this analysis, what should be the focus for this round?
"""
            
            analysis_response = self.llm_service.generate(
                analysis_prompt,
                system_prompt="You are a research analyst. Analyze current progress and identify what needs to be done next.",
                temperature=0.1
            )
            
            # Now select tools based on the analysis
            selection_prompt = f"""
Research question: {question}
Research mode: {mode}
Current round: {iteration + 1}

Research progress analysis:
{analysis_response}

Available tools:
{tool_list}

Based on the analysis above, select the tools that would best address the identified gaps and next steps. Consider:
- Which tools can provide the missing information?
- Which tools can fill the identified gaps?
- Which tools can help with the next steps?
- You can reuse tools from previous rounds if they would provide additional value
- You can select different tools if they would provide better coverage

Return only the tool names separated by commas, no explanations.
If no tools are needed for this round, return "NONE".
"""
            
            selected_tools_response = self.llm_service.generate(
                selection_prompt,
                system_prompt="You are a research coordinator. Select tools based on research gaps and next steps.",
                temperature=0.1
            )
            
            if "NONE" in selected_tools_response.upper():
                return []
            
            # Parse the response to get tool names
            selected_tools = []
            for tool_name in available_tools:
                if tool_name.lower() in selected_tools_response.lower():
                    selected_tools.append(tool_name)
            
            return selected_tools
            
        except Exception as e:
            logger.error(f"Error in round tool selection: {str(e)}")
            return []
    
    def _get_max_iterations_for_mode(self, mode: str) -> int:
        """Get maximum iterations based on research mode."""
        return {
            "instant": 1,
            "quick": 2,
            "standard": 3,
            "deep": 5
        }.get(mode, 2)
    
    def _is_research_complete(self, question: str, research_data: List[str], mode: str) -> bool:
        """Use LLM to determine if research is complete based on current data."""
        try:
            completion_prompt = f"""
Research question: {question}
Research mode: {mode}

Current research data:
{chr(10).join(research_data)}

Based on the research mode and current data, determine if the research is complete:
- For instant research: Is there a quick, direct answer available?
- For quick research: Is there sufficient context for enhanced analysis?
- For standard research: Is there comprehensive coverage of the topic?
- For deep research: Is there exhaustive analysis with full context?

Answer with "YES" if research is complete, "NO" if more research is needed.
"""
            
            completion_response = self.llm_service.generate(
                completion_prompt,
                system_prompt="You are a research completion evaluator. Determine if research objectives are met.",
                temperature=0.1
            )
            
            return "YES" in completion_response.upper()
            
        except Exception as e:
            logger.error(f"Error in research completion check: {str(e)}")
            return True  # Default to complete to avoid infinite loops
    
    def _generate_final_response(self, question: str, research_data: List[str], mode: str) -> str:
        """Generate final response based on research data and mode."""
        try:
            if mode == "deep":
                # Generate clarification questions for deep research
                clarifications = self.llm_service.generate_questions(question, count=3)
                
                # Generate comprehensive analysis
                analysis = self.llm_service.generate_analysis(question, research_data)
                summary = self.llm_service.generate_summary(analysis)
                
                return f"Deep research results:\n" + "\n".join(research_data) + f"\n\nAnalysis: {analysis}\n\nSummary: {summary}\n\nClarification questions: {clarifications}"
            else:
                # Generate response for other modes
                analysis = self.llm_service.generate_analysis(question, research_data)
                return f"{mode.title()} research results:\n" + "\n".join(research_data) + f"\n\nAnalysis: {analysis}"
                
        except Exception as e:
            return f"Error generating final response: {str(e)}"
    
    def instant_research(self, question: str) -> str:
        """Instant research mode - dynamic tool selection for quick response."""
        try:
            return self._execute_dynamic_research(question, "instant")
        except Exception as e:
            return f"Error in instant research: {str(e)}"
    
    def quick_research(self, question: str) -> str:
        """Quick research mode - dynamic tool selection with enhanced analysis."""
        try:
            return self._execute_dynamic_research(question, "quick")
        except Exception as e:
            return f"Error in quick research: {str(e)}"
    
    def standard_research(self, question: str) -> str:
        """Standard research mode - dynamic tool selection with comprehensive analysis."""
        try:
            return self._execute_dynamic_research(question, "standard")
        except Exception as e:
            return f"Error in standard research: {str(e)}"
    
    def deep_research(self, question: str) -> str:
        """Deep research mode - dynamic tool selection with exhaustive analysis."""
        try:
            return self._execute_dynamic_research(question, "deep")
        except Exception as e:
            return f"Error in deep research: {str(e)}"
```

#### **Tool Context Structure**

The `tool_context` parameter contains comprehensive tool information:

```python
tool_context = {
    "available_tools": ["web_search", "document_retrieval", "academic_search"],
    "tool_descriptions": {
        "web_search": "Search the web for information",
        "document_retrieval": "Retrieve documents from various sources",
        "academic_search": "Search academic databases and papers"
    },
    "tool_usage_examples": {
        "web_search": "web_search(query='latest AI developments')",
        "document_retrieval": "document_retrieval(source='pdf', query='machine learning')",
        "academic_search": "academic_search(database='arxiv', query='neural networks')"
    },
    "tool_parameters": {
        "web_search": {
            "query": {"name": "query", "type": "string", "required": True, "default": None},
            "max_results": {"name": "max_results", "type": "integer", "required": False, "default": 10}
        },
        "document_retrieval": {
            "source": {"name": "source", "type": "string", "required": True, "default": None},
            "query": {"name": "query", "type": "string", "required": True, "default": None}
        }
    },
    "tool_return_types": {
        "web_search": "List[Dict[str, Any]]",
        "document_retrieval": "List[Dict[str, Any]]",
        "academic_search": "List[Dict[str, Any]]"
    },
    "tool_namespaces": {
        "web_search": "mcp",
        "document_retrieval": "mcp",
        "academic_search": "mcp"
    }
}
```

#### **Tool Management Methods**

```python
# Check if tool is available
if agent.has_tool("web_search"):
    result = agent._call_tool("web_search", {"query": "AI news"})

# Add tool dynamically
agent.add_tool("new_tool")

# Remove tool
agent.remove_tool("old_tool")

# Get all available tools
tools = agent.get_available_tools()

# Get detailed tool information
tools_info = agent._get_available_tools_info()
```

### **Key Reusability Features:**

1. **BaseAgent provides common capabilities**:
   - Error handling and logging
   - Context management
   - Tool management
   - Configuration management
   - Health status monitoring

2. **LLM service is agent-type agnostic**:
   - Generic methods (`generate`, `generate_analysis`, `generate_questions`)
   - Agent-type aware responses
   - Configurable for different use cases

3. **Consistent interface**:
   - All agents implement `solve()` method
   - Standardized error handling
   - Common response formatting

4. **Comprehensive tool integration**:
   - Dynamic tool management
   - Tool context parsing
   - Error handling for tool calls
   - Tool information retrieval

This Phase 1 implementation provides a solid foundation for Phase 2, where we'll replace the mock LLM service with real LLM integration while maintaining the same interface and AgentHub compatibility.
