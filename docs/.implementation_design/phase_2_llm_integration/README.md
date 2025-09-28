# Phase 2: LLM Integration - Real AI Responses

## Overview

This phase integrates real LLM services with the research agent, replacing the mock service from Phase 1 with actual AI-generated content while maintaining the established mode-specific behavior differences and BaseAgent inheritance structure.

## Phase Goals

- ✅ Replace mock LLM service with real LLM providers (Ollama, OpenAI, Anthropic, etc.)
- ✅ Implement multi-provider LLM integration with automatic model detection
- ✅ Enhance mode-specific research workflows with real AI responses
- ✅ Add intelligent mode selection logic in `solve()` method
- ✅ Implement basic source tracking and URL deduplication
- ✅ Add temp file management for research data storage
- ✅ Enhance error handling with LLM-specific retry logic
- ✅ Maintain backward compatibility with Phase 1 interface

## Implementation Scope

### Enhanced Module Structure
```
research_agent/
├── base_agent/              # (from Phase 1 - unchanged)
│   ├── core.py              # BaseAgent abstract class
│   ├── context_manager.py   # Context management
│   └── error_handler.py     # Error handling
├── research_agent/
│   ├── core.py              # Enhanced ResearchAgent with real LLM
│   ├── mode_selector.py     # NEW: Intelligent mode selection
│   ├── source_tracker.py    # NEW: URL tracking and deduplication
│   └── workflows/           # Enhanced with real LLM calls
│       ├── workflows.py     # Updated with real LLM integration
│       ├── instant.py       # NEW: Dedicated instant workflow
│       ├── quick.py         # NEW: Dedicated quick workflow
│       ├── standard.py      # NEW: Dedicated standard workflow
│       └── deep.py          # NEW: Dedicated deep workflow
├── llm_service/
│   ├── core.py              # Enhanced with real LLM providers
│   ├── providers/           # NEW: Provider-specific implementations
│   │   ├── __init__.py
│   │   ├── ollama.py        # Ollama provider
│   │   ├── openai.py        # OpenAI provider
│   │   ├── anthropic.py     # Anthropic provider
│   │   └── base_provider.py # Base provider class
│   ├── model_detector.py    # NEW: Model detection and selection
│   ├── model_config.py      # NEW: Model configuration management
│   └── mock_service.py      # (from Phase 1 - kept for fallback)
└── utils/
    ├── utils.py             # (from Phase 1 - unchanged)
    ├── file_manager.py       # NEW: Temp file management
    └── data_models.py       # NEW: Pydantic data models
```

## Key Components

### 1. Enhanced LLM Service (`research_agent/llm_service/`)

#### CoreLLMService Enhancement
- **Multi-Provider Support**: Ollama, OpenAI, Anthropic, LM Studio
- **Automatic Model Detection**: Intelligent model selection based on query complexity
- **Provider Fallback**: Graceful fallback between providers
- **Research Optimization**: Mode-specific temperature and token settings

#### Provider Architecture
```python
class BaseProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def generate_response(self, query: str, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_available_models(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass

class OllamaProvider(BaseProvider):
    """Ollama provider implementation."""

class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation."""

class AnthropicProvider(BaseProvider):
    """Anthropic provider implementation."""
```

#### Model Detection Logic
```python
class ModelDetector:
    """Intelligent model detection and selection."""

    def select_model(self, mode: str, query: str, available_models: List[str]) -> str:
        """Select optimal model based on mode and query complexity."""

        # Mode-specific model preferences
        mode_preferences = {
            'instant': ['gpt-3.5-turbo', 'claude-3-haiku', 'llama3.1:8b'],
            'quick': ['gpt-4', 'claude-3-sonnet', 'llama3.1:70b'],
            'standard': ['gpt-4', 'claude-3-opus', 'llama3.1:70b'],
            'deep': ['gpt-4', 'claude-3-opus', 'llama3.1:70b']
        }

        # Query complexity analysis
        complexity = self._analyze_query_complexity(query)

        # Select best available model
        return self._select_best_model(mode_preferences[mode], available_models, complexity)
```

### 2. Mode Selector (`research_agent/research_agent/mode_selector.py`)

#### Intelligent Mode Selection
```python
class ModeSelector:
    """Intelligent mode selection based on question analysis."""

    def select_mode(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Select optimal research mode based on query characteristics."""

        # Analyze query complexity
        complexity_score = self._analyze_complexity(query)

        # Check for explicit mode indicators
        explicit_mode = self._detect_explicit_mode(query)
        if explicit_mode:
            return explicit_mode

        # Analyze query length and structure
        length_score = self._analyze_length(query)

        # Check for research-specific keywords
        keyword_score = self._analyze_keywords(query)

        # Combine scores to determine mode
        total_score = complexity_score + length_score + keyword_score

        if total_score >= 8:
            return 'deep'
        elif total_score >= 5:
            return 'standard'
        elif total_score >= 2:
            return 'quick'
        else:
            return 'instant'

    def _analyze_complexity(self, query: str) -> int:
        """Analyze query complexity indicators."""
        complexity_indicators = {
            'comprehensive': 3,
            'exhaustive': 3,
            'detailed analysis': 3,
            'thorough': 2,
            'analysis': 2,
            'research': 2,
            'investigation': 2,
            'study': 2,
            'explain': 1,
            'describe': 1,
            'what is': 0,
            'how': 1
        }

        query_lower = query.lower()
        score = 0

        for indicator, weight in complexity_indicators.items():
            if indicator in query_lower:
                score += weight

        return min(score, 5)  # Cap at 5
```

### 3. Source Tracker (`research_agent/research_agent/source_tracker.py`)

#### URL Deduplication and Tracking
```python
class SourceTracker:
    """Track and deduplicate sources across research rounds."""

    def __init__(self):
        self.used_sources = set()
        self.source_metadata = {}
        self.session_sources = []

    def add_source(self, url: str, metadata: Dict[str, Any]) -> bool:
        """Add source if not already used."""
        if url in self.used_sources:
            return False

        self.used_sources.add(url)
        self.source_metadata[url] = {
            'url': url,
            'added_at': datetime.utcnow().isoformat(),
            'metadata': metadata
        }
        self.session_sources.append(url)
        return True

    def get_unused_sources(self, candidate_sources: List[str]) -> List[str]:
        """Filter out already used sources."""
        return [url for url in candidate_sources if url not in self.used_sources]

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of sources used in current session."""
        return {
            'total_sources': len(self.used_sources),
            'session_sources': len(self.session_sources),
            'sources': list(self.used_sources)
        }
```

### 4. Enhanced Workflows (`research_agent/research_agent/workflows/`)

#### Mode-Specific Workflow Implementation
Each research mode gets its own dedicated workflow class:

```python
class InstantWorkflow(BaseWorkflow):
    """Instant research workflow - single LLM call."""

    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute instant research with single LLM call."""

        # Single LLM call with instant-optimized prompt
        response = self.llm_service.generate_response(
            query=query,
            mode='instant',
            temperature=0.1,  # Low temperature for factual responses
            max_tokens=500    # Limited tokens for quick responses
        )

        return self._format_response(response, rounds=1, sources=0)

class DeepWorkflow(BaseWorkflow):
    """Deep research workflow - multiple rounds with clarification."""

    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute deep research with multiple rounds and clarification."""

        # Round 1: Generate clarification questions
        clarification_response = self.llm_service.generate_response(
            query=f"Generate clarification questions for: {query}",
            mode='deep',
            temperature=0.3,
            max_tokens=1000
        )

        # Round 2-4: Research with clarifications
        research_responses = []
        for round_num in range(2, 5):
            response = self.llm_service.generate_response(
                query=f"Research round {round_num} for: {query}",
                mode='deep',
                temperature=0.2,
                max_tokens=1500
            )
            research_responses.append(response)

        # Final synthesis
        synthesis_response = self.llm_service.generate_response(
            query=f"Synthesize comprehensive analysis for: {query}",
            mode='deep',
            temperature=0.1,
            max_tokens=2000
        )

        return self._format_deep_response(
            clarification_response, research_responses, synthesis_response
        )
```

### 5. Temp File Manager (`research_agent/utils/file_manager.py`)

#### Research Data Storage
```python
class TempFileManager:
    """Manage temporary files for research data."""

    def __init__(self, base_dir: str = "/tmp/research_agent"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.session_dir = None

    def create_session(self, session_id: str) -> Path:
        """Create session-specific directory."""
        self.session_dir = self.base_dir / session_id
        self.session_dir.mkdir(exist_ok=True)
        return self.session_dir

    def save_research_data(self, data: Dict[str, Any], filename: str) -> Path:
        """Save research data to temporary file."""
        if not self.session_dir:
            raise ValueError("No active session")

        file_path = self.session_dir / filename
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

        return file_path

    def cleanup_session(self, session_id: str):
        """Clean up session files."""
        session_path = self.base_dir / session_id
        if session_path.exists():
            shutil.rmtree(session_path)
```

## Mode-Specific Enhancements

### Instant Research (1 round, 0-5 sources, 15-30 sec)
- **Single LLM Call**: Direct question → immediate answer
- **Low Temperature**: 0.1 for factual, concise responses
- **Limited Tokens**: 500 max tokens for quick responses
- **No Iteration**: Single-pass processing
- **Prompt**: "Provide a concise, factual answer to: {query}"

### Quick Research (2 rounds, 5-15 sources, 1-2 min)
- **Two LLM Calls**: Initial research + enhanced analysis
- **Medium Temperature**: 0.2 for balanced creativity/factuality
- **Moderate Tokens**: 1000 max tokens per call
- **Context Building**: Second round builds on first round results
- **Prompt**: "Provide enhanced analysis with context for: {query}"

### Standard Research (4-6 rounds, 20-50 sources, 8-15 min)
- **Multiple LLM Calls**: 4-6 rounds of research and analysis
- **Gap Analysis**: Identifies missing information between rounds
- **Follow-up Queries**: Generates targeted queries for gaps
- **Medium Temperature**: 0.2-0.3 for comprehensive analysis
- **Higher Tokens**: 1500 max tokens per call
- **Prompt**: "Conduct comprehensive research with multiple perspectives on: {query}"

### Deep Research (8-12 rounds, 50-120 sources, 20-30 min)
- **Clarification Questions**: Generates questions to refine research scope
- **Exhaustive Analysis**: Maximum rounds with deep gap analysis
- **Enhanced Context**: Incorporates clarifications into research
- **Academic-Level Synthesis**: Detailed, well-researched final response
- **Higher Temperature**: 0.3 for creative analysis
- **Maximum Tokens**: 2000 max tokens per call
- **Prompt**: "Conduct exhaustive research with academic-level analysis on: {query}"

## Implementation Details

### LLM Service Integration

#### Provider Configuration
```python
# config.json enhancement
{
  "llm": {
    "default_provider": "ollama",
    "providers": {
      "ollama": {
        "base_url": "http://localhost:11434",
        "default_model": "llama3.1:8b",
        "timeout": 60
      },
      "openai": {
        "api_key": "${OPENAI_API_KEY}",
        "default_model": "gpt-4",
        "timeout": 30
      },
      "anthropic": {
        "api_key": "${ANTHROPIC_API_KEY}",
        "default_model": "claude-3-sonnet",
        "timeout": 30
      }
    },
    "fallback_order": ["ollama", "openai", "anthropic"],
    "mode_settings": {
      "instant": {"temperature": 0.1, "max_tokens": 500},
      "quick": {"temperature": 0.2, "max_tokens": 1000},
      "standard": {"temperature": 0.2, "max_tokens": 1500},
      "deep": {"temperature": 0.3, "max_tokens": 2000}
    }
  }
}
```

#### Error Handling and Retry Logic
```python
class LLMService(LLMService):
    """Enhanced LLM service with real providers."""

    def generate_response(self, query: str, mode: str, **kwargs) -> Dict[str, Any]:
        """Generate response with retry logic and fallback."""

        providers = self.config.get('llm', {}).get('fallback_order', ['ollama'])
        last_error = None

        for provider_name in providers:
            try:
                provider = self._get_provider(provider_name)
                response = provider.generate_response(query, mode, **kwargs)
                return response
            except Exception as e:
                last_error = e
                self.error_handler.log_error(e, {
                    'provider': provider_name,
                    'query': query,
                    'mode': mode
                })
                continue

        # All providers failed, return error
        return self.error_handler.handle_error(
            last_error,
            {'query': query, 'mode': mode},
            "All LLM providers failed"
        )
```

### ResearchAgent Enhancement

#### Enhanced solve() Method
```python
class ResearchAgent(BaseAgent):
    """Enhanced ResearchAgent with real LLM integration."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(config, **kwargs)

        # Initialize Phase 2 components
        self.mode_selector = ModeSelector()
        self.source_tracker = SourceTracker()
        self.temp_file_manager = TempFileManager()

        # Enhanced LLM service
        self.llm_service = LLMService(config)  # Real LLM service

    def solve(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced solve method with intelligent mode selection."""

        query = request.get('query', '')
        explicit_mode = request.get('mode')

        # Use intelligent mode selection if no explicit mode
        if not explicit_mode:
            mode = self.mode_selector.select_mode(query, request.get('context'))
        else:
            mode = explicit_mode

        # Route to appropriate research method
        return self._route_to_research_method(mode, request)
```

## Testing Strategy

### AgentHub Tests
```python
import agenthub as ah

# Load the agent
agent = ah.load_agent("agentplug/research-agent")

# Test mode differences with real LLM
result1 = agent.instant_research("What is AI?")
# Expected: Short, direct response (1-2 sentences, ~500 tokens)

result2 = agent.quick_research("How does ML work?")
# Expected: Medium response with context (2-3 paragraphs, ~1000 tokens)

result3 = agent.standard_research("Latest AI developments?")
# Expected: Comprehensive response (4-5 paragraphs, ~1500 tokens)

result4 = agent.deep_research("AI ethics comprehensive analysis")
# Expected: Detailed response with clarification (6+ paragraphs, ~2000 tokens)

result5 = agent.solve("What is artificial intelligence?")
# Expected: Auto-selected mode based on question complexity

# Verify mode-specific behavior
assert len(result1["data"]["response"]["data"]["content"]) < len(result2["data"]["response"]["data"]["content"])
assert len(result2["data"]["response"]["data"]["content"]) < len(result3["data"]["response"]["data"]["content"])
assert len(result3["data"]["response"]["data"]["content"]) < len(result4["data"]["response"]["data"]["content"])

# Verify source tracking
assert result4["data"]["sources_used"] > result1["data"]["sources_used"]
```

### LLM Integration Tests
- Test with different LLM providers (Ollama, OpenAI, Anthropic)
- Verify model detection and selection
- Test error handling and provider fallback
- Validate response quality differences between modes
- Test source tracking and deduplication
- Verify temp file management

## Implementation Checklist

### LLM Service Enhancement
- [ ] Create BaseProvider abstract class
- [ ] Implement OllamaProvider
- [ ] Implement OpenAIProvider
- [ ] Implement AnthropicProvider
- [ ] Create ModelDetector for intelligent model selection
- [ ] Enhance CoreLLMService with multi-provider support
- [ ] Add provider fallback and retry logic
- [ ] Update configuration for LLM providers
- [ ] Write unit tests for all providers

### Mode Selection Enhancement
- [ ] Create ModeSelector class
- [ ] Implement query complexity analysis
- [ ] Add explicit mode detection
- [ ] Create mode selection scoring algorithm
- [ ] Integrate with ResearchAgent.solve() method
- [ ] Write unit tests for mode selection

### Source Tracking Implementation
- [ ] Create SourceTracker class
- [ ] Implement URL deduplication
- [ ] Add source metadata storage
- [ ] Integrate with all research workflows
- [ ] Add session source management
- [ ] Write unit tests for source tracking

### Workflow Enhancement
- [ ] Create dedicated workflow classes for each mode
- [ ] Implement real LLM integration in each workflow
- [ ] Add mode-specific prompt engineering
- [ ] Implement gap analysis for standard/deep modes
- [ ] Add clarification question generation for deep mode
- [ ] Write unit tests for all workflows

### Temp File Management
- [ ] Create TempFileManager class
- [ ] Implement session-based file organization
- [ ] Add automatic cleanup functionality
- [ ] Integrate with research workflows
- [ ] Write unit tests for file management

### Integration and Testing
- [ ] Update ResearchAgent with new components
- [ ] Test all research modes with real LLM
- [ ] Verify mode-specific behavior differences
- [ ] Test error handling and fallback mechanisms
- [ ] Validate source tracking functionality
- [ ] Test AgentHub integration
- [ ] Update examples and documentation

## Success Criteria

- [ ] Real LLM responses replace mock responses
- [ ] Mode-specific behavior differences are evident in response length and quality
- [ ] Auto mode selection works correctly for various question types
- [ ] Source tracking prevents duplicate sources across rounds
- [ ] Temp file management works properly for research data
- [ ] Error handling gracefully manages LLM failures with fallback
- [ ] Multiple LLM providers are supported (Ollama, OpenAI, Anthropic)
- [ ] Backward compatibility maintained with Phase 1 interface
- [ ] All existing tests pass with real LLM integration
- [ ] AgentHub integration works seamlessly

## Common Pitfalls to Avoid

### 1. LLM Provider Integration Issues
- Ensure proper API key management and environment variables
- Implement robust error handling for network failures
- Test with multiple providers to ensure fallback works
- Handle rate limiting and timeout scenarios

### 2. Mode Selection Problems
- Test mode selection with various question types and lengths
- Ensure fallback to instant mode works for edge cases
- Validate that explicit mode selection overrides auto-selection
- Test with ambiguous questions

### 3. Source Tracking Issues
- Ensure URL normalization for proper deduplication
- Handle malformed URLs gracefully
- Test with large numbers of sources
- Verify session isolation

### 4. Response Quality Degradation
- Monitor response quality across different providers
- Ensure mode-specific prompts are optimized
- Test with various query complexities
- Validate token limits are appropriate for each mode

## Next Phase Dependencies

This phase provides the foundation for:
- Phase 3: External tool integration (web search, document analysis)
- Phase 4: Production-ready features (caching, monitoring, scaling)

The enhanced LLM service, mode-specific workflows, and source tracking will be extended with external tool integration in Phase 3, while maintaining the established BaseAgent inheritance structure.
