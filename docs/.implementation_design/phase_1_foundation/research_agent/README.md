# ResearchAgent Module - Phase 1 Foundation

## Overview

The ResearchAgent module implements the specialized research functionality, inheriting from BaseAgent and providing four distinct research modes with progressive complexity.

## Module Structure

```
research_agent/research_agent/
├── __init__.py                 # Module initialization and exports
├── core.py                     # ResearchAgent class implementation
└── workflows/                  # Mode-specific workflow implementations
    ├── __init__.py
    ├── instant.py              # Instant research workflow
    ├── quick.py                # Quick research workflow
    ├── standard.py             # Standard research workflow
    └── deep.py                 # Deep research workflow
```

## Key Components

### 1. ResearchAgent Class (`core.py`)

**Purpose**: Specialized research agent inheriting from BaseAgent

**Key Features**:
- Four research modes with different complexity levels
- Auto mode selection in solve() method
- Research workflow orchestration
- Mode-specific behavior differences

**Research Modes**:
```python
class ResearchAgent(BaseAgent):
    """Research agent specialized for research tasks"""

    async def instant_research(self, question: str) -> Dict[str, Any]:
        """Instant research: 1 round, 10 sources, 15-30 sec"""

    async def quick_research(self, question: str) -> Dict[str, Any:
        """Quick research: 2 rounds, 20 sources, 1-2 min"""

    async def standard_research(self, question: str) -> Dict[str, Any]:
        """Standard research: 5 rounds, 50 sources, 8-15 min"""

    async def deep_research(self, question: str) -> Dict[str, Any]:
        """Deep research: 12 rounds, 120 sources, 20-30 min"""

    async def solve(self, question: str) -> Dict[str, Any]:
        """Auto mode selection for research"""
```

### 2. Research Workflows (`workflows/`)

**Purpose**: Mode-specific workflow implementations

#### Instant Workflow (`instant.py`)
- **Single Round**: Direct question → immediate answer
- **Quick Analysis**: Basic fact extraction and summarization
- **No Iteration**: Single-pass processing
- **Use Case**: Quick facts, simple questions, time-sensitive queries

#### Quick Workflow (`quick.py`)
- **Two Rounds**: Initial research + enhanced analysis
- **Context Building**: Second round builds on first round results
- **Basic Synthesis**: Combines results from both rounds
- **Use Case**: Moderate complexity, need for context, multi-agent systems

#### Standard Workflow (`standard.py`)
- **Multiple Rounds**: 5 rounds of research and analysis
- **Gap Analysis**: Identifies missing information between rounds
- **Follow-up Queries**: Generates targeted queries for gaps
- **Comprehensive Synthesis**: Thorough analysis of all rounds
- **Use Case**: Complex topics, thorough research, detailed analysis

#### Deep Workflow (`deep.py`)
- **Clarification Questions**: Generates questions to refine research scope
- **Exhaustive Analysis**: Maximum rounds with deep gap analysis
- **Enhanced Context**: Incorporates clarifications into research
- **Academic-Level Synthesis**: Detailed, well-researched final response
- **Use Case**: Complex research projects, exhaustive analysis, academic-level research

## Implementation Details

### Phase 1 Scope
- Basic ResearchAgent class with all 5 methods
- Mock workflow implementations
- Simple mode selection logic
- Basic error handling
- Mock LLM service integration

### Phase 2 Enhancements
- Real LLM service integration
- Enhanced mode selection with ML
- Source tracking integration
- Temp file management

### Phase 3 Enhancements
- External tool integration
- Advanced gap analysis
- Tool coordination
- Enhanced source tracking

### Phase 4 Enhancements
- Performance optimization
- Advanced monitoring
- Production-ready error handling
- Comprehensive testing

## Mode-Specific Behavior

### Response Quality Differences
- **Instant**: Short, direct responses (1-2 sentences)
- **Quick**: Medium responses with context (2-3 paragraphs)
- **Standard**: Comprehensive responses (4-5 paragraphs)
- **Deep**: Detailed responses with clarifications (6+ paragraphs)

### Research Depth
- **Instant**: Surface-level information
- **Quick**: Basic analysis with context
- **Standard**: Comprehensive analysis with gap identification
- **Deep**: Exhaustive analysis with clarification questions

### Time and Resource Usage
- **Instant**: 15-30 seconds, 1 round, 10 sources
- **Quick**: 1-2 minutes, 2 rounds, 20 sources
- **Standard**: 8-15 minutes, 5 rounds, 50 sources
- **Deep**: 20-30 minutes, 12 rounds, 120 sources

## Testing Strategy

### Unit Tests
- Test ResearchAgent initialization
- Test each research mode
- Test mode selection logic
- Test workflow implementations

### Integration Tests
- Test complete research workflows
- Test mode-specific behavior differences
- Test error handling across modes
- Test LLM service integration

### AgentHub Tests
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

## Usage Example

```python
from research_agent.research_agent import ResearchAgent
from research_agent.llm_service import get_shared_llm_service

# Initialize research agent
llm_service = get_shared_llm_service()
agent = ResearchAgent(llm_service)

# Use specific research modes
result = agent.instant_research("What is artificial intelligence?")
result = agent.quick_research("How does machine learning work?")
result = agent.standard_research("Latest developments in AI research")
result = agent.deep_research("Comprehensive analysis of AI ethics")

# Use auto mode selection
result = agent.solve("What is artificial intelligence?")
```

## Dependencies

- BaseAgent module
- LLM service module
- asyncio for async operations
- typing for type hints
- logging for error handling

## Next Steps

This module provides the foundation for:
- Real LLM integration (Phase 2)
- External tool integration (Phase 3)
- Production-ready features (Phase 4)

The ResearchAgent class will be enhanced with real LLM integration in Phase 2, external tool integration in Phase 3, and production-ready features in Phase 4.
