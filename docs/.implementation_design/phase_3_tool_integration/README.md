# Phase 3: Tool Integration - External Tool Ecosystem

## Overview

This phase integrates external tools provided by users through AgentHub, enabling the research agent to use real search tools, document retrieval, and other external services for comprehensive research.

## Phase Goals

- ✅ Parse tool context from AgentHub external_tools parameter
- ✅ Implement tool execution and coordination
- ✅ Integrate tool results with LLM responses
- ✅ Enhance research workflows with tool calls
- ✅ Implement advanced source tracking with URL deduplication
- ✅ Add advanced temp file management and caching

## Implementation Scope

### Enhanced Module Structure
```
research_agent/
├── base_agent/              # (from Phase 1)
├── research_agent/
│   ├── core.py             # Enhanced with tool integration
│   ├── mode_selector.py    # (from Phase 2)
│   ├── source_tracker.py   # Enhanced with URL deduplication
│   ├── tool_coordinator.py # NEW: Tool execution and coordination
│   └── workflows/          # Enhanced with tool calls
├── llm_service/            # (from Phase 2)
├── tools/                  # NEW: Tool ecosystem
│   ├── __init__.py
│   ├── base.py            # Base tool interface
│   ├── web_search.py      # Web search tool
│   ├── academic_search.py # Academic search tool
│   ├── news_search.py     # News search tool
│   └── document_retrieval.py # Document retrieval tool
└── utils/
    ├── file_manager.py    # Enhanced with caching
    └── data_models.py     # Enhanced with tool data models
```

## Key Components

### 1. Tool Coordinator (`research_agent/research_agent/tool_coordinator.py`)
- **Tool Discovery**: Parses external_tools from AgentHub
- **Tool Execution**: Coordinates tool calls across research rounds
- **Result Integration**: Combines tool results with LLM responses
- **Error Handling**: Manages tool failures and retries

### 2. Tool Ecosystem (`research_agent/tools/`)
- **Base Tool Interface**: Common interface for all tools
- **Web Search Tool**: General web search capabilities
- **Academic Search Tool**: Academic paper and research search
- **News Search Tool**: News and current events search
- **Document Retrieval Tool**: Document parsing and analysis

### 3. Enhanced Source Tracker (`research_agent/research_agent/source_tracker.py`)
- **URL Deduplication**: Prevents duplicate sources across research rounds
- **Metadata Storage**: Tracks source information, timestamps, and usage
- **Session Management**: Maintains source history per session
- **Quality Scoring**: Rates sources based on relevance and reliability

### 4. Enhanced Workflows (`research_agent/research_agent/workflows/`)
- **Tool Integration**: Each workflow uses appropriate tools
- **Result Synthesis**: Combines tool results with LLM analysis
- **Gap Analysis**: Uses tool results to identify information gaps
- **Follow-up Queries**: Generates targeted tool calls for gaps

### 5. Enhanced File Manager (`research_agent/utils/file_manager.py`)
- **Caching Support**: Stores tool results for reuse
- **Data Persistence**: Maintains research data across sessions
- **Cleanup Management**: Automatic cleanup of old data
- **Performance Optimization**: Efficient storage and retrieval

## Tool Integration Patterns

### Tool Discovery
```python
# Tools are provided by users through AgentHub
agent = ah.load_agent(
    "agentplug/research-agent",
    external_tools=["web_search", "academic_search", "news_search"]
)

# ResearchAgent discovers and uses these tools
class ResearchAgent(BaseAgent):
    def __init__(self, llm_service, external_tools=None):
        super().__init__(llm_service, external_tools)
        self.tool_coordinator = ToolCoordinator(external_tools)
```

### Tool Execution Flow
1. **Tool Selection**: Choose appropriate tools based on research mode
2. **Tool Execution**: Execute tools with research-specific parameters
3. **Result Processing**: Process and standardize tool results
4. **LLM Integration**: Use tool results to enhance LLM responses
5. **Source Tracking**: Track and deduplicate sources from tools

### Mode-Specific Tool Usage

#### Instant Research
- **Primary Tools**: Web search, quick fact retrieval
- **Tool Calls**: 1-2 tool calls per round
- **Result Processing**: Basic fact extraction and summarization

#### Quick Research
- **Primary Tools**: Web search, news search
- **Tool Calls**: 2-3 tool calls per round
- **Result Processing**: Context-aware analysis and enhancement

#### Standard Research
- **Primary Tools**: Web search, academic search, news search
- **Tool Calls**: 3-5 tool calls per round
- **Result Processing**: Comprehensive analysis and gap identification

#### Deep Research
- **Primary Tools**: All available tools
- **Tool Calls**: 5-10 tool calls per round
- **Result Processing**: Exhaustive analysis and synthesis

## Testing Strategy

### AgentHub Tests
```python
import agenthub as ah

# Load agent with external tools
agent = ah.load_agent(
    "agentplug/research-agent",
    external_tools=["web_search", "academic_search", "news_search"]
)

# Test with external tools
result1 = agent.instant_research("What is AI?")
# Expected: Uses web_search tool, integrates results with LLM

result2 = agent.standard_research("Latest AI research papers")
# Expected: Uses academic_search tool, provides comprehensive analysis

result3 = agent.deep_research("AI news and developments")
# Expected: Uses multiple tools (web_search, news_search), deep analysis

# Test tool integration
assert "sources" in result1
assert len(result1["sources"]) > 0
assert "tool_results" in result1 or "external_data" in result1

# Test source tracking (no duplicate URLs)
result4 = agent.quick_research("AI developments")
result5 = agent.quick_research("AI developments")  # Same question
# Expected: Second call should avoid duplicate sources
```

### Tool Integration Tests
- Test tool discovery and registration
- Test tool execution and result processing
- Test source tracking and deduplication
- Test error handling and fallbacks
- Test performance with multiple tools

## Success Criteria

- [ ] External tools are discovered and registered correctly
- [ ] Tool execution works with real external services
- [ ] Tool results are integrated with LLM responses
- [ ] Source tracking prevents duplicate URLs
- [ ] Research workflows use appropriate tools per mode
- [ ] Error handling gracefully manages tool failures
- [ ] Performance is acceptable with multiple tools
- [ ] Caching improves performance for repeated queries

## Next Phase Dependencies

This phase provides the foundation for:
- Phase 4: Production-ready features

The tool integration and enhanced workflows will be optimized and productionized in Phase 4.
