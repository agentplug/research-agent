# Research Agent Module - Phase 1

**Purpose**: Implements research-specific functionality inheriting from BaseAgent

## Overview

The Research Agent module implements the core research functionality, inheriting from BaseAgent and specializing it for research tasks. It implements dynamic research workflows with context-aware tool selection and progress-based decision making.

## File Structure

```
src/research_agent/
├── __init__.py              # Module initialization
├── research_agent.py        # ResearchAgent class implementation
├── research_methods.py      # Research mode implementations
└── tool_integration.py      # Tool calling and management
```

## Implementation Details

### `research_agent.py` - ResearchAgent Class

**Key Features**:
- Inherits from BaseAgent
- Implements 4 research modes (instant, quick, standard, deep)
- Dynamic tool selection based on context
- Progress-based research workflow
- Independent tool selection per round
- Follow-up query generation

**Class Structure**:
```python
class ResearchAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any], external_tools: List[str] = None)
    def instant_research(self, question: str) -> str
    def quick_research(self, question: str) -> str
    def standard_research(self, question: str) -> str
    def deep_research(self, question: str) -> str
    async def solve(self, question: str) -> Dict[str, Any]
    def _execute_dynamic_research(self, question: str, mode: str) -> str
    def _select_tools_for_round(self, question: str, mode: str, research_data: List[str], available_tools: List[str], iteration: int) -> List[str]
    def _select_tools_independently(self, question: str, mode: str, research_data: List[str], available_tools: List[str], analysis: str) -> List[str]
    def _get_max_iterations_for_mode(self, mode: str) -> int
    def _generate_final_response(self, question: str, research_data: List[str], mode: str) -> str
```

### `research_methods.py` - Research Mode Implementations

**Purpose**: Implements the specific logic for each research mode

**Research Modes**:

#### Instant Research
- **Purpose**: Quick, direct answers
- **Iterations**: 1 round
- **Focus**: Single tool, direct response
- **Use Case**: Simple questions requiring immediate answers

#### Quick Research
- **Purpose**: Enhanced context with minimal rounds
- **Iterations**: 2 rounds
- **Focus**: 1-2 tools, enhanced analysis
- **Use Case**: Questions requiring some context and analysis

#### Standard Research
- **Purpose**: Comprehensive coverage
- **Iterations**: 3 rounds
- **Focus**: 2-3 tools, thorough analysis
- **Use Case**: Complex questions requiring comprehensive research

#### Deep Research
- **Purpose**: Exhaustive analysis with clarification
- **Iterations**: 5 rounds
- **Focus**: Multiple tools, exhaustive analysis, clarification questions
- **Use Case**: Complex topics requiring deep understanding

### `tool_integration.py` - Tool Management

**Purpose**: Handles tool calling and integration with external tools

**Key Features**:
- Tool context management
- Tool calling interface
- Tool result processing
- Error handling for tool calls

**Tool Integration Methods**:
```python
def _call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str
def _get_available_tools_info(self) -> Dict[str, Any]
def _execute_tools_for_round(self, tools_to_use: List[str], follow_up_queries: List[str], question: str) -> List[str]
```

## Dynamic Research Workflow

### Two-Step Process

**Step 1: Analysis & Completion Check**
```python
# Analyze current progress and determine completion status
analysis_response = self.llm_service.generate(analysis_prompt, ...)
analysis_data = json.loads(analysis_response)
analysis = analysis_data.get("analysis", "")
is_complete = analysis_data.get("is_complete", False)
```

**Step 2: Independent Tool Selection** (only if not complete)
```python
# Independent tool selection based on current context
tool_selection_response = self.llm_service.generate(tool_selection_prompt, ...)
tool_data = json.loads(tool_selection_response)
selected_tools = tool_data.get("selected_tools", [])
follow_up_queries = tool_data.get("follow_up_queries", [])
```

### Research Flow Example

**Research Question**: "What are the latest AI developments?"

**Round 1**:
- **Analysis**: "No previous data. Need basic AI information."
- **Completion**: false
- **Tool Selection**: `web_search`
- **Query**: "latest AI developments 2024 news"
- **Result**: General AI news and developments

**Round 2**:
- **Analysis**: "Have general AI news. Missing technical details and research papers."
- **Completion**: false
- **Tool Selection**: `academic_search`, `news_search`
- **Queries**: ["AI research papers 2024 technical breakthroughs", "AI industry analysis expert opinions"]
- **Result**: Technical papers + industry analysis

**Round 3**:
- **Analysis**: "Have comprehensive coverage. Research complete."
- **Completion**: true
- **Tool Selection**: [] (no tools needed)

## Dependencies

- `base_agent` - BaseAgent class
- `llm_service` - LLM service interface
- `asyncio` - Async support
- `json` - JSON handling
- `typing` - Type hints
- `logging` - Logging functionality

## Testing

### Unit Tests
- Test each research mode
- Test dynamic research workflow
- Test tool selection logic
- Test progress analysis
- Test completion detection
- Test follow-up query generation

### Integration Tests
- Test complete research workflows
- Test tool integration
- Test error handling
- Test performance

### Test Coverage
- All research methods
- All workflow steps
- Error conditions
- Edge cases
- Tool integration

## Usage Example

```python
from research_agent import ResearchAgent

# Initialize research agent
agent = ResearchAgent(
    config={"temperature": 0.0},
    external_tools=["web_search", "academic_search", "news_search"]
)

# Instant research
result = agent.instant_research("What is ChatGPT?")

# Quick research
result = agent.quick_research("Latest AI developments")

# Standard research
result = agent.standard_research("AI impact on healthcare")

# Deep research
result = agent.deep_research("Future of artificial intelligence")

# Auto mode selection
result = await agent.solve("AI developments")
```

## Configuration

### Research Mode Configuration
```json
{
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

### Mode-Specific Iteration Limits
```python
def _get_max_iterations_for_mode(self, mode: str) -> int:
    return {
        "instant": 1,
        "quick": 2,
        "standard": 3,
        "deep": 5
    }.get(mode, 2)
```

## Error Handling

### Error Categories
- **Tool Errors**: Tool calling failures
- **LLM Errors**: LLM service failures
- **JSON Parsing Errors**: Response parsing failures
- **Research Errors**: Research workflow failures

### Error Recovery
- Graceful degradation
- Fallback mechanisms
- Error logging
- Status reporting

## Performance Considerations

- Efficient tool selection
- Minimal LLM calls per round
- Optimized research workflow
- Fast response generation
- Memory-efficient data handling

## Phase 2 Preparation

This implementation prepares for Phase 2 by:
- Establishing dynamic research workflow
- Creating context-aware tool selection
- Implementing progress-based decision making
- Providing comprehensive error handling
- Ensuring AgentHub compatibility

Phase 2 will enhance this implementation with real LLM services and advanced research capabilities.
