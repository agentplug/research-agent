# ResearchAgent Module Implementation - Phase 2 Real LLM

## Overview
Phase 2 focuses on implementing real LLM integration and mode-specific research workflows, replacing mock responses with actual LLM calls.

## Module Structure
```
src/research_agent/
├── __init__.py
├── core.py
├── research_methods.py
└── utils.py
```

## Files to Modify

### `src/research_agent/core.py`
- Update ResearchAgent to use real LLM service
- Implement real LLM-based tool selection
- Add real analysis and completion evaluation
- Implement real follow-up query generation

### `src/research_agent/research_methods.py`
- Replace mock responses with real LLM calls
- Implement real research workflow execution
- Add real tool selection logic
- Implement real query generation

## Key Features Implemented

### Real LLM Integration
- Replace MockLLMService with CoreLLMService
- Real LLM-based analysis and decision making
- Actual tool selection based on LLM analysis
- Real follow-up query generation

### Enhanced Research Methods
- `instant_research()` - Real LLM responses
- `quick_research()` - Real LLM analysis
- `standard_research()` - Real comprehensive analysis
- `deep_research()` - Real clarification questions and analysis

### Real Dynamic Research Process
- `_execute_dynamic_research()` - Real LLM-based execution
- `_select_tools_for_round()` - Real analysis and completion check
- `_select_tools_independently()` - Real context-aware tool selection
- `_generate_final_response()` - Real LLM-based response generation

### Real Tool Selection Logic
- LLM-based progress analysis
- Real completion evaluation
- Context-aware tool selection
- Real follow-up query generation

## Implementation Details

### Real LLM Service Integration
```python
def __init__(self, external_tools: List[str] = None):
    super().__init__(agent_type="research", external_tools=external_tools)
    self.llm_service = get_shared_llm_service(agent_type="research")
```

### Real Analysis and Completion Check
```python
def _select_tools_for_round(self, question: str, mode: str, research_data: List[str], 
                           available_tools: List[str], iteration: int) -> List[str]:
    # Real LLM analysis
    analysis_response = self.llm_service.generate(
        analysis_prompt,
        system_prompt="You are a research analyst...",
        temperature=0.0
    )
    
    # Parse real analysis
    analysis_data = json.loads(analysis_response)
    analysis = analysis_data.get("analysis", "")
    is_complete = analysis_data.get("is_complete", False)
    
    # Real completion check
    if is_complete:
        return []
    
    # Real independent tool selection
    return self._select_tools_independently(question, mode, research_data, available_tools, analysis)
```

### Real Independent Tool Selection
```python
def _select_tools_independently(self, question: str, mode: str, research_data: List[str], 
                              available_tools: List[str], analysis: str) -> List[str]:
    # Real LLM-based tool selection
    tool_selection_response = self.llm_service.generate(
        tool_selection_prompt,
        system_prompt="You are a research coordinator...",
        temperature=0.0
    )
    
    # Parse real tool selection
    tool_data = json.loads(tool_selection_response)
    selected_tools = tool_data.get("selected_tools", [])
    follow_up_queries = tool_data.get("follow_up_queries", [])
    
    return selected_tools
```

### Real Response Generation
```python
def _generate_final_response(self, question: str, research_data: List[str], mode: str) -> str:
    system_prompt = self.config["system_prompts"][mode]
    
    if mode == "deep":
        # Real clarification questions
        clarifications = self.llm_service.generate_questions(question, count=3)
        
        # Real comprehensive analysis
        analysis = self.llm_service.generate(
            f"Research question: {question}\n\nResearch data:\n" + "\n".join(research_data) + 
            f"\n\nClarification questions: {clarifications}\n\nProvide exhaustive deep research response...",
            system_prompt=system_prompt,
            temperature=self.config["ai"]["temperature"]
        )
        
        # Real summary generation
        summary = self.llm_service.generate_summary(analysis)
        
        return f"Deep research results:\n{analysis}\n\nSummary: {summary}\n\nClarification questions: {clarifications}"
    else:
        # Real response generation
        response = self.llm_service.generate(
            f"Research question: {question}\n\nResearch data:\n" + "\n".join(research_data) + 
            f"\n\nProvide {mode} research response based on the data.",
            system_prompt=system_prompt,
            temperature=self.config["ai"]["temperature"]
        )
        
        return response
```

## Testing
- Real LLM integration tests
- Tool selection tests with real LLM
- Research workflow tests
- Error handling tests
- Performance tests

## Dependencies
- CoreLLMService (real LLM service)
- OpenAI/Anthropic/Google API clients
- BaseAgent module
- Python 3.11+
- Async/await support
