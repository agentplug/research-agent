# Phase 3 Implementation Order

## Step 1: Fix AgentHub Integration

### 1.1 Update agent.py for AgentHub Compatibility

**Current Issue**: The current `agent.py` is designed for CLI usage, not AgentHub integration.

**Required Changes**:
- Remove CLI argument parsing
- Add JSON input parsing from command line
- Implement proper method routing
- Add tool context handling

**Implementation**:
```python
def main():
    """Main entry point for AgentHub integration."""
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
            result = agent.instant_research(parameters.get("query", ""))
            print(json.dumps({"result": result}))
        elif method == "quick_research":
            result = agent.quick_research(parameters.get("query", ""))
            print(json.dumps({"result": result}))
        elif method == "standard_research":
            result = agent.standard_research(parameters.get("query", ""))
            print(json.dumps({"result": result}))
        elif method == "deep_research":
            result = agent.deep_research(
                parameters.get("query", ""),
                parameters.get("user_clarification", "")
            )
            print(json.dumps({"result": result}))
        else:
            print(json.dumps({"error": f"Unknown method: {method}"}))
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
```

### 1.2 Update agent.yaml

**Required Changes**:
- Add proper method definitions
- Include tool context parameters
- Update interface specifications

**Implementation**:
```yaml
name: research-agent
version: 2.0.0
description: "Advanced research agent with tool integration and multi-round analysis"
author: "agentplug"
license: "MIT"
python_version: "3.11+"

interface:
  methods:
    instant_research:
      description: "Conduct instant research with tool integration"
      parameters:
        query:
          type: "string"
          description: "Research query"
          required: true
      returns:
        type: "object"
        description: "Research results with tool integration"

    quick_research:
      description: "Conduct quick research with enhanced analysis"
      parameters:
        query:
          type: "string"
          description: "Research query"
          required: true
      returns:
        type: "object"
        description: "Multi-round research results"

    standard_research:
      description: "Conduct comprehensive research with tool integration"
      parameters:
        query:
          type: "string"
          description: "Research query"
          required: true
      returns:
        type: "object"
        description: "Comprehensive research results"

    deep_research:
      description: "Conduct exhaustive research with clarification and tools"
      parameters:
        query:
          type: "string"
          description: "Research query"
          required: true
        user_clarification:
          type: "string"
          description: "User clarification for deep research"
          required: false
      returns:
        type: "object"
        description: "Exhaustive research results with tool integration"

tags: ["research", "analysis", "tools", "multi-round", "clarification"]
```

## Step 2: Implement BaseAgent Integration

### 2.1 Create AgentHub BaseAgent

**Location**: `research_agent/base_agent/agenthub_base.py`

**Implementation**:
```python
from typing import Dict, Any, List, Optional
import json

class AgentHubBaseAgent:
    """Base class for AgentHub agents with tool integration."""

    def __init__(self, tool_context: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.

        Args:
            tool_context: Dictionary containing tool metadata and context information
        """
        self.tool_context = tool_context or {}
        self.available_tools = self.tool_context.get("available_tools", [])
        self.tool_descriptions = self.tool_context.get("tool_descriptions", {})
        self.tool_usage_examples = self.tool_context.get("tool_usage_examples", {})
        self.tool_parameters = self.tool_context.get("tool_parameters", {})
        self.tool_return_types = self.tool_context.get("tool_return_types", {})

    def validate_tool_context(self) -> bool:
        """Validate tool context structure."""
        if not isinstance(self.tool_context, dict):
            return False

        # Check required fields
        required_fields = ["available_tools", "tool_descriptions"]
        for field in required_fields:
            if field not in self.tool_context:
                return False

        return True

    def build_tool_context_string(self) -> str:
        """Build tool context string for AI system prompt."""
        if not self.available_tools:
            return ""

        tool_descriptions = []
        for tool_name in self.available_tools:
            description = self.tool_descriptions.get(tool_name, f"Tool: {tool_name}")
            examples = self.tool_usage_examples.get(tool_name, [])

            tool_descriptions.append(f"""
Tool: {tool_name}
Description: {description}
Examples: {', '.join(examples)}
""")

        return f"""
You have access to the following tools. Use them when appropriate for the research task.

{''.join(tool_descriptions)}

To use a tool, respond with a JSON object containing:
{{
    "tool_call": {{
        "tool_name": "tool_name",
        "arguments": {{"param1": "value1", "param2": "value2"}}
    }},
    "analysis": "I will use the tool to perform this operation"
}}

IMPORTANT: Use tools when they can provide better or more current information than your training data.
"""
```

### 2.2 Update ResearchAgent to Inherit from AgentHub BaseAgent

**Location**: `research_agent/research_agent/core.py`

**Required Changes**:
- Change inheritance from `BaseAgent` to `AgentHubBaseAgent`
- Add tool context handling
- Implement tool-aware research workflows

**Implementation**:
```python
from ..base_agent.agenthub_base import AgentHubBaseAgent

class ResearchAgent(AgentHubBaseAgent):
    """Enhanced research agent with AgentHub tool integration."""

    def __init__(self, model: Optional[str] = None, config_path: Optional[str] = None,
                 tool_context: Optional[Dict[str, Any]] = None):
        """Initialize with AgentHub tool context."""
        super().__init__(tool_context)

        # Initialize existing components
        self.config_path = config_path or "config.json"
        self.config = self._load_config(self.config_path)
        self.model = model
        self.error_handler = ErrorHandler("ResearchAgent")

        self.llm_service = get_shared_llm_service(model=model)
        self.research_history: List[Dict[str, Any]] = []

        # Initialize modules with tool awareness
        self.analysis_engine = ToolAwareAnalysisEngine(self.llm_service, self.available_tools)
        self.clarification_engine = ClarificationEngine(self.llm_service)
        self.intention_generator = IntentionGenerator(self.llm_service)
        self.research_workflows = ToolAwareResearchWorkflows(
            self.llm_service,
            self.analysis_engine,
            self.clarification_engine,
            self.intention_generator,
            self.available_tools
        )
        self.helpers = ResearchHelpers()
```

## Step 3: Implement Tool-Aware Components

### 3.1 Create ToolAwareAnalysisEngine

**Location**: `research_agent/research_agent/analysis/tool_aware_analyzer.py`

**Implementation**:
```python
from .analyzer import AnalysisEngine

class ToolAwareAnalysisEngine(AnalysisEngine):
    """Analysis engine with tool integration capabilities."""

    def __init__(self, llm_service, available_tools):
        super().__init__(llm_service)
        self.available_tools = available_tools

    def build_analysis_prompt(self, original_query: str, research_summary: str, mode: str) -> str:
        """Build analysis prompt with tool context."""
        base_prompt = super().build_analysis_prompt(original_query, research_summary, mode)

        if self.available_tools:
            tool_context = self._build_tool_context_for_analysis()
            return f"{base_prompt}\n\n{tool_context}"

        return base_prompt

    def _build_tool_context_for_analysis(self) -> str:
        """Build tool context specifically for analysis."""
        if not self.available_tools:
            return ""

        return f"""
TOOL INTEGRATION CONTEXT:
You have access to these tools: {', '.join(self.available_tools)}

When analyzing research gaps, consider if any tools could help gather missing information:
- web_search: For current information, news, recent developments
- document_retrieval: For extracting information from documents
- data_analysis: For statistical analysis and calculations

If tools could help fill gaps, suggest their use in your analysis.
"""
```

### 3.2 Create ToolAwareResearchWorkflows

**Location**: `research_agent/research_agent/research/tool_aware_workflows.py`

**Implementation**:
```python
from .workflows_enhanced import ResearchWorkflows

class ToolAwareResearchWorkflows(ResearchWorkflows):
    """Research workflows with tool integration."""

    def __init__(self, llm_service, analysis_engine, clarification_engine,
                 intention_generator, available_tools):
        super().__init__(llm_service, analysis_engine, clarification_engine, intention_generator)
        self.available_tools = available_tools
        self.tool_executor = ToolExecutor(available_tools) if available_tools else None

    def execute_first_round(self, query: str, mode: str, intention_paragraph: str = "") -> Dict[str, Any]:
        """Execute first round with tool integration."""
        # Build system prompt with tool context
        system_prompt = self._build_tool_aware_system_prompt(query, mode, intention_paragraph)

        # Generate response
        content = self.llm_service.generate(
            input_data=query,
            system_prompt=system_prompt,
            temperature=0.0,
        )

        # Check for tool calls in response
        tool_calls = self._extract_tool_calls(content)

        if tool_calls and self.tool_executor:
            # Execute tools and regenerate response
            tool_results = self.tool_executor.execute_tools(tool_calls)
            enhanced_content = self._enhance_content_with_tools(content, tool_results)
            content = enhanced_content

        return {
            "round": 1,
            "query": query,
            "content": content,
            "tools_used": [call["tool_name"] for call in tool_calls] if tool_calls else [],
            "timestamp": get_current_timestamp(),
        }

    def _build_tool_aware_system_prompt(self, query: str, mode: str, intention_paragraph: str = "") -> str:
        """Build system prompt with tool context."""
        base_prompt = self._get_base_system_prompt(mode, intention_paragraph)

        if self.available_tools:
            tool_context = self._build_tool_context_string()
            return f"{base_prompt}\n\n{tool_context}"

        return base_prompt

    def _extract_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """Extract tool calls from LLM response."""
        # Implementation for parsing tool calls from JSON responses
        try:
            if "tool_call" in content:
                # Parse JSON tool calls
                import json
                # Extract and parse tool calls
                pass
        except:
            pass
        return []

    def _enhance_content_with_tools(self, original_content: str, tool_results: List[Dict[str, Any]]) -> str:
        """Enhance content with tool results."""
        # Implementation for integrating tool results into research content
        return original_content
```

## Step 4: Testing and Validation

### 4.1 Unit Tests

**Location**: `tests/unit/test_tool_integration.py`

**Test Cases**:
- Tool context validation
- Tool call extraction
- Tool execution integration
- Enhanced research workflows

### 4.2 Integration Tests

**Location**: `tests/integration/test_agenthub_integration.py`

**Test Cases**:
- AgentHub method calls
- Tool context passing
- End-to-end research with tools
- Error handling

### 4.3 AgentHub Compatibility Test

**Test Script**:
```python
# Test AgentHub integration
import json
import subprocess

def test_agenthub_integration():
    """Test AgentHub integration."""

    # Test data
    test_data = {
        "method": "instant_research",
        "parameters": {"query": "What is AI?"},
        "tool_context": {
            "available_tools": ["web_search"],
            "tool_descriptions": {"web_search": "Search the web"},
            "tool_usage_examples": {"web_search": ["Search for information"]}
        }
    }

    # Execute agent
    result = subprocess.run(
        ["python", "agent.py", json.dumps(test_data)],
        capture_output=True,
        text=True
    )

    # Validate result
    response = json.loads(result.stdout)
    assert "result" in response
    assert response["result"]["success"] == True
```

## Step 5: Documentation and Deployment

### 5.1 Update README.md

**Add sections**:
- Tool integration overview
- AgentHub usage examples
- Tool configuration guide
- API reference

### 5.2 Create Tool Integration Guide

**Location**: `docs/TOOL_INTEGRATION.md`

**Content**:
- Tool setup instructions
- Tool context configuration
- Custom tool development
- Troubleshooting guide

### 5.3 Update Examples

**Location**: `examples/tool_integration_example.py`

**Content**:
- AgentHub usage examples
- Tool integration demonstrations
- Best practices
- Performance benchmarks

This implementation order ensures a systematic approach to integrating tools while maintaining the existing research capabilities and user experience.
