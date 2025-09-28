# Phase 2: LLM Integration - Real AI Responses

## Overview

This phase integrates real LLM services with the research agent, replacing mock responses with actual AI-generated content while maintaining mode-specific behavior differences.

## Phase Goals

- ✅ Integrate real LLM service with multiple providers (Ollama, OpenAI, etc.)
- ✅ Implement mode-specific research workflows with different response qualities
- ✅ Add auto mode selection logic in `solve()` method
- ✅ Implement basic source tracking (in-memory)
- ✅ Add temp file management for research data
- ✅ Enhance error handling and retry logic

## Implementation Scope

### Enhanced Module Structure
```
research_agent/
├── base_agent/              # (from Phase 1)
├── research_agent/
│   ├── core.py             # Enhanced with real LLM integration
│   ├── mode_selector.py    # NEW: Auto mode selection logic
│   ├── source_tracker.py   # NEW: URL tracking and duplicates
│   └── workflows/          # Enhanced with real LLM calls
├── llm_service/
│   ├── core.py             # Real LLM service implementation
│   ├── providers.py        # NEW: Provider-specific implementations
│   ├── model_config.py     # NEW: Model configuration
│   └── model_detector.py   # NEW: Model detection and selection
└── utils/
    ├── __init__.py
    ├── file_manager.py     # NEW: Temp file management
    └── data_models.py      # NEW: Pydantic data models
```

## Key Components

### 1. Enhanced LLM Service (`research_agent/llm_service/`)
- **CoreLLMService**: Multi-provider LLM integration
- **ModelDetector**: Automatic model detection and selection
- **Provider Support**: Ollama, LM Studio, OpenAI, Anthropic, etc.
- **Research Optimization**: Lower temperature defaults, specialized prompts

### 2. Mode Selector (`research_agent/research_agent/mode_selector.py`)
- **Auto Mode Selection**: Analyzes question complexity
- **Context Awareness**: Considers available tools and time constraints
- **Intelligent Routing**: Maps questions to appropriate research modes

### 3. Source Tracker (`research_agent/research_agent/source_tracker.py`)
- **URL Deduplication**: Prevents duplicate sources across rounds
- **Metadata Storage**: Tracks source information and usage
- **Session Management**: Maintains source history per session

### 4. Enhanced Workflows (`research_agent/research_agent/workflows/`)
- **Real LLM Integration**: Each workflow uses actual LLM calls
- **Mode-Specific Behavior**: Different response lengths and analysis depth
- **Error Recovery**: Graceful handling of LLM failures

### 5. Temp File Manager (`research_agent/utils/file_manager.py`)
- **Research Data Storage**: Temporary storage for research results
- **Automatic Cleanup**: Manages file lifecycle
- **Caching Support**: Stores intermediate results

## Mode-Specific Enhancements

### Instant Research (1 round, 10 sources, 15-30 sec)
- **Single LLM Call**: Direct question → immediate answer
- **Quick Analysis**: Basic fact extraction and summarization
- **No Iteration**: Single-pass processing

### Quick Research (2 rounds, 20 sources, 1-2 min)
- **Two LLM Calls**: Initial research + enhanced analysis
- **Context Building**: Second round builds on first round results
- **Basic Synthesis**: Combines results from both rounds

### Standard Research (5 rounds, 50 sources, 8-15 min)
- **Multiple LLM Calls**: 5 rounds of research and analysis
- **Gap Analysis**: Identifies missing information between rounds
- **Follow-up Queries**: Generates targeted queries for gaps
- **Comprehensive Synthesis**: Thorough analysis of all rounds

### Deep Research (12 rounds, 120 sources, 20-30 min)
- **Clarification Questions**: Generates questions to refine research scope
- **Exhaustive Analysis**: Maximum rounds with deep gap analysis
- **Enhanced Context**: Incorporates clarifications into research
- **Academic-Level Synthesis**: Detailed, well-researched final response

## Testing Strategy

### AgentHub Tests
```python
import agenthub as ah

# Load the agent
agent = ah.load_agent("agentplug/research-agent")

# Test mode differences with real LLM
result1 = agent.instant_research("What is AI?")
# Expected: Short, direct response (1-2 sentences)

result2 = agent.quick_research("How does ML work?")
# Expected: Medium response with some context (2-3 paragraphs)

result3 = agent.standard_research("Latest AI developments?")
# Expected: Comprehensive response (4-5 paragraphs)

result4 = agent.deep_research("AI ethics comprehensive analysis")
# Expected: Detailed response with clarification questions (6+ paragraphs)

result5 = agent.solve("What is artificial intelligence?")
# Expected: Auto-selected mode based on question complexity

# Verify mode-specific behavior
assert len(result1["result"]) < len(result2["result"])
assert len(result2["result"]) < len(result3["result"])
assert len(result3["result"]) < len(result4["result"])
```

### LLM Integration Tests
- Test with different LLM providers (Ollama, OpenAI, etc.)
- Verify model detection and selection
- Test error handling and fallbacks
- Validate response quality differences

## Success Criteria

- [ ] Real LLM responses replace mock responses
- [ ] Mode-specific behavior differences are evident
- [ ] Auto mode selection works correctly
- [ ] Source tracking prevents duplicates
- [ ] Temp file management works properly
- [ ] Error handling gracefully manages LLM failures
- [ ] Multiple LLM providers are supported

## Next Phase Dependencies

This phase provides the foundation for:
- Phase 3: External tool integration
- Phase 4: Production-ready features

The enhanced LLM service and mode-specific workflows will be extended with external tool integration in Phase 3.
