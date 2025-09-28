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

## User Testing & Expectations - Phase 2 Real LLM

### ✅ What You Should Be Able to Test

#### 1. Real LLM Integration
```python
from research_agent import ResearchAgent

# Test with real LLM service
agent = ResearchAgent(external_tools=["web_search", "academic_search"])
assert agent.llm_service.model != "mock-model"  # Should use real model
assert agent.agent_type == "research"
```

#### 2. Real Research Methods
```python
# Test instant research with real LLM
result = agent.instant_research("What is artificial intelligence?")
assert "Mock result" not in result  # Should not contain mock responses
assert len(result) > 100  # Should be substantial real response
assert "artificial intelligence" in result.lower() or "AI" in result

# Test quick research with real LLM
result = agent.quick_research("What is machine learning?")
assert "Mock result" not in result
assert "Analysis:" in result or "analysis" in result.lower()
assert len(result) > 200  # Should be more comprehensive

# Test standard research with real LLM
result = agent.standard_research("What is deep learning?")
assert "Mock result" not in result
assert len(result) > 300  # Should be comprehensive

# Test deep research with real LLM
result = agent.deep_research("What is neural networks?")
assert "Mock result" not in result
assert "Clarification questions:" in result or "questions" in result.lower()
assert len(result) > 500  # Should be exhaustive
```

#### 3. Real Tool Selection
```python
# Test real tool selection
tools = agent._select_tools_for_round("What is AI?", "instant", [], ["web_search", "academic_search"], 0)
assert len(tools) > 0
assert tools[0] in ["web_search", "academic_search"]

# Test independent tool selection
analysis = "Need more information about AI applications"
tools = agent._select_tools_independently("What is AI?", "standard", [], ["web_search", "academic_search"], analysis)
assert len(tools) > 0
```

#### 4. Real Analysis and Completion
```python
# Test real analysis
research_data = ["web_search: AI is artificial intelligence", "academic_search: AI research papers"]
analysis_response = agent.llm_service.generate(
    "Analyze this research data: " + "\n".join(research_data),
    "You are a research analyst"
)
assert "Mock" not in analysis_response
assert len(analysis_response) > 50
```

### ✅ What You Should Expect

#### 1. Real LLM Responses
- **No Mock Responses**: All responses should be from real LLM providers
- **Substantial Content**: Responses should be meaningful and substantial
- **Context Awareness**: LLM should understand the research context
- **Quality Analysis**: Analysis should be insightful and relevant
- **Proper Completion**: Completion evaluation should be accurate

#### 2. Real Tool Selection
- **Intelligent Selection**: Tools selected based on real analysis
- **Context Awareness**: Selection considers current research progress
- **Gap Identification**: Identifies real information gaps
- **Follow-Up Queries**: Generates specific, targeted queries

#### 3. Real Research Workflow
- **Dynamic Execution**: Research adapts based on real progress
- **Multi-Round Process**: Multiple rounds with real analysis
- **Tool Effectiveness**: Tools selected based on effectiveness
- **Completion Logic**: Real completion evaluation

#### 4. Provider Integration
- **Multiple Providers**: Works with OpenAI, Anthropic, Google, Local models
- **Model Detection**: Automatically selects best available model
- **Error Handling**: Graceful handling of provider errors
- **Rate Limiting**: Proper handling of API rate limits

### ✅ Manual Testing Commands

#### Test Real Research Methods
```bash
# Test instant research with real LLM
python agent.py '{"method": "instant_research", "parameters": {"question": "What is artificial intelligence?"}}'

# Test quick research with real LLM
python agent.py '{"method": "quick_research", "parameters": {"question": "What is machine learning?"}}'

# Test standard research with real LLM
python agent.py '{"method": "standard_research", "parameters": {"question": "What is deep learning?"}}'

# Test deep research with real LLM
python agent.py '{"method": "deep_research", "parameters": {"question": "What is neural networks?"}}'

# Test solve method with real LLM
python agent.py '{"method": "solve", "parameters": {"question": "What is AI?"}}'
```

#### Expected Output Format
```json
{
  "result": "Artificial intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving..."
}
```

#### Test Real LLM Service
```python
# Create test script: test_real_llm.py
from llm_service import CoreLLMService, get_shared_llm_service

def test_real_llm():
    # Test real LLM service
    service = CoreLLMService(agent_type="research")
    print(f"✓ Service model: {service.model}")
    
    # Test real response generation
    response = service.generate("What is artificial intelligence?", "You are a helpful assistant")
    print(f"✓ Real response: {response[:100]}...")
    
    # Test real analysis
    analysis = service.generate_analysis("What is AI?", ["AI is artificial intelligence"])
    print(f"✓ Real analysis: {analysis[:100]}...")
    
    # Test real summary
    summary = service.generate_summary("Long text about artificial intelligence")
    print(f"✓ Real summary: {summary[:100]}...")
    
    # Test real questions
    questions = service.generate_questions("What is AI?", count=3)
    print(f"✓ Real questions: {questions[:100]}...")

if __name__ == "__main__":
    test_real_llm()
```

#### Expected Output
```
✓ Service model: gpt-4
✓ Real response: Artificial intelligence (AI) refers to the simulation of human intelligence in machines...
✓ Real analysis: Based on the provided information about AI, I can analyze that artificial intelligence...
✓ Real summary: This text discusses artificial intelligence, covering its definition, applications...
✓ Real questions: 1. What are the main applications of artificial intelligence? 2. How does AI differ from traditional programming? 3. What are the ethical considerations in AI development?
```

### ✅ Success Criteria Checklist

- [ ] Real LLM service integration works correctly
- [ ] All research methods return real LLM responses (no mock responses)
- [ ] Tool selection uses real LLM analysis
- [ ] Progress analysis and completion evaluation work with real LLM
- [ ] Follow-up query generation works with real LLM
- [ ] Multiple LLM providers work (OpenAI, Anthropic, Google, Local)
- [ ] Model detection and fallback mechanisms work
- [ ] Error handling works for provider failures
- [ ] Rate limiting and timeout handling work
- [ ] All tests pass with real LLM integration
- [ ] Performance is acceptable with real LLM calls
- [ ] AgentHub interface works with real LLM

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