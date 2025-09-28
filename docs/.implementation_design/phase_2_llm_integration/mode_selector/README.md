# Mode Selector Module - Phase 2

## Overview

This module implements intelligent mode selection for Phase 2, automatically determining the optimal research mode based on query analysis, context, and complexity scoring.

## Module Structure

```
research_agent/research_agent/
├── mode_selector.py           # Main ModeSelector class
└── workflows/                 # Enhanced workflows (from Phase 1)
    ├── workflows.py           # Updated with mode selection integration
    ├── instant.py            # NEW: Dedicated instant workflow
    ├── quick.py              # NEW: Dedicated quick workflow
    ├── standard.py           # NEW: Dedicated standard workflow
    └── deep.py               # NEW: Dedicated deep workflow
```

## Key Components

### 1. Mode Selector (`mode_selector.py`)

Intelligent mode selection based on query analysis:

```python
class ModeSelector:
    """Intelligent mode selection based on query analysis."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Complexity indicators with weights
        self.complexity_indicators = {
            # High complexity (3 points)
            'comprehensive': 3, 'exhaustive': 3, 'detailed analysis': 3,
            'thorough investigation': 3, 'in-depth study': 3,

            # Medium complexity (2 points)
            'thorough': 2, 'analysis': 2, 'research': 2,
            'investigation': 2, 'study': 2, 'examine': 2,

            # Low complexity (1 point)
            'explain': 1, 'describe': 1, 'discuss': 1,
            'outline': 1, 'summarize': 1, 'overview': 1,

            # Very low complexity (0 points)
            'what is': 0, 'define': 0, 'meaning': 0
        }

    def select_mode(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Select optimal research mode based on query analysis."""
        # Normalize query
        normalized_query = self._normalize_query(query)

        # Check for explicit mode indicators
        explicit_mode = self._detect_explicit_mode(normalized_query)
        if explicit_mode:
            return explicit_mode

        # Analyze query complexity
        complexity_score = self._analyze_complexity(normalized_query)
        length_score = self._analyze_length(normalized_query)
        question_score = self._analyze_question_type(normalized_query)
        context_score = self._analyze_context(context) if context else 0

        # Combine scores and map to mode
        total_score = complexity_score + length_score + question_score + context_score
        return self._score_to_mode(total_score)
```

### 2. Query Analysis Methods

#### Complexity Analysis
```python
def _analyze_complexity(self, query: str) -> int:
    """Analyze query complexity based on keywords."""
    score = 0
    for indicator, weight in self.complexity_indicators.items():
        if indicator in query:
            score += weight
    return min(score, 8)  # Cap at 8
```

#### Length Analysis
```python
def _analyze_length(self, query: str) -> int:
    """Analyze query length and structure."""
    word_count = len(query.split())
    char_count = len(query)

    if word_count >= 50 or char_count >= 300:
        return 3  # Very long queries suggest deep research
    elif word_count >= 25 or char_count >= 150:
        return 2  # Long queries suggest standard research
    elif word_count >= 10 or char_count >= 60:
        return 1  # Medium queries suggest quick research
    else:
        return 0  # Short queries suggest instant research
```

#### Question Type Analysis
```python
def _analyze_question_type(self, query: str) -> int:
    """Analyze question type and complexity."""
    question_patterns = {
        'what': 0,      # Definitional questions
        'how': 1,       # Process questions
        'why': 2,       # Explanatory questions
        'when': 0,      # Temporal questions
        'where': 0,     # Locational questions
        'who': 0,       # Identity questions
        'which': 1,      # Comparative questions
        'compare': 2,   # Comparative analysis
        'contrast': 2,  # Contrastive analysis
        'analyze': 3,   # Analysis requests
        'evaluate': 3,  # Evaluation requests
        'assess': 3     # Assessment requests
    }

    score = 0
    for pattern, weight in question_patterns.items():
        if pattern in query:
            score = max(score, weight)  # Take highest weight found
    return score
```

#### Context Analysis
```python
def _analyze_context(self, context: Dict[str, Any]) -> int:
    """Analyze context information for mode selection."""
    score = 0

    # Check for research-specific context
    if context.get('research_depth') == 'deep':
        score += 3
    elif context.get('research_depth') == 'standard':
        score += 2
    elif context.get('research_depth') == 'quick':
        score += 1

    # Check for time constraints
    if context.get('time_constraint') == 'urgent':
        score -= 2  # Prefer faster modes
    elif context.get('time_constraint') == 'flexible':
        score += 1  # Allow for deeper research

    # Check for available tools
    available_tools = context.get('available_tools', [])
    if len(available_tools) >= 5:
        score += 1  # More tools enable deeper research

    return max(score, 0)  # Don't go negative
```

### 3. Mode Selection Logic

#### Score to Mode Mapping
```python
def _score_to_mode(self, total_score: int) -> str:
    """Convert total score to research mode."""
    if total_score >= 8:
        return 'deep'
    elif total_score >= 5:
        return 'standard'
    elif total_score >= 2:
        return 'quick'
    else:
        return 'instant'
```

#### Explicit Mode Detection
```python
def _detect_explicit_mode(self, query: str) -> Optional[str]:
    """Detect explicit mode indicators in query."""
    explicit_indicators = {
        'instant': ['quick answer', 'immediate', 'fast', 'brief', 'short'],
        'quick': ['quick analysis', 'enhanced', 'context', 'overview'],
        'standard': ['comprehensive', 'detailed', 'thorough', 'analysis'],
        'deep': ['exhaustive', 'in-depth', 'extensive', 'complete', 'full research']
    }

    for mode, indicators in explicit_indicators.items():
        for indicator in indicators:
            if indicator in query:
                return mode
    return None
```

### 4. Mode Validation and Recommendations

#### Mode Validation
```python
def validate_mode_selection(self, query: str, mode: str) -> bool:
    """Validate if the selected mode is appropriate for the query."""
    explanation = self.get_mode_explanation(query)
    recommended_mode = explanation['selected_mode']

    # Allow some flexibility in mode selection
    mode_hierarchy = ['instant', 'quick', 'standard', 'deep']
    recommended_index = mode_hierarchy.index(recommended_mode)
    selected_index = mode_hierarchy.index(mode)

    # Allow selection within one level of recommendation
    return abs(selected_index - recommended_index) <= 1
```

#### Mode Recommendations
```python
def get_mode_recommendations(self, query: str) -> List[Dict[str, Any]]:
    """Get recommendations for all modes with explanations."""
    explanation = self.get_mode_explanation(query)
    total_score = explanation['scores']['total']

    recommendations = []
    modes = ['instant', 'quick', 'standard', 'deep']

    for mode in modes:
        mode_score = self._score_to_mode(total_score)
        is_recommended = mode == mode_score

        recommendations.append({
            'mode': mode,
            'recommended': is_recommended,
            'suitability': self._calculate_mode_suitability(query, mode),
            'description': self._get_mode_description(mode)
        })

    return recommendations
```

## Integration with ResearchAgent

### Enhanced solve() Method
```python
class ResearchAgent(BaseAgent):
    def solve(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced solve method with intelligent mode selection."""
        query = request.get('query', '')
        explicit_mode = request.get('mode')
        context = request.get('context', {})

        # Use intelligent mode selection if no explicit mode
        if not explicit_mode:
            selected_mode = self.mode_selector.select_mode(query, context)
            logger.info(f"Auto-selected mode '{selected_mode}' for query: {query[:50]}...")
        else:
            selected_mode = explicit_mode

            # Validate explicit mode selection
            if not self.mode_selector.validate_mode_selection(query, selected_mode):
                logger.warning(f"Explicit mode '{selected_mode}' may not be optimal")

        # Route to appropriate research method
        return self._route_to_research_method(selected_mode, request)
```

## Testing Strategy

### Unit Tests
```python
class TestModeSelector(unittest.TestCase):
    def test_instant_mode_selection(self):
        """Test instant mode selection."""
        queries = ["What is AI?", "Define machine learning"]
        for query in queries:
            mode = self.mode_selector.select_mode(query)
            self.assertEqual(mode, 'instant')

    def test_deep_mode_selection(self):
        """Test deep mode selection."""
        queries = [
            "Comprehensive analysis of AI ethics",
            "Exhaustive research on machine learning applications"
        ]
        for query in queries:
            mode = self.mode_selector.select_mode(query)
            self.assertEqual(mode, 'deep')

    def test_context_analysis(self):
        """Test context analysis."""
        query = "What is machine learning?"
        contexts = [
            {'research_depth': 'deep', 'time_constraint': 'flexible'},
            {'research_depth': 'quick', 'time_constraint': 'urgent'}
        ]
        expected_modes = ['deep', 'quick']

        for context, expected_mode in zip(contexts, expected_modes):
            mode = self.mode_selector.select_mode(query, context)
            self.assertEqual(mode, expected_mode)
```

### Integration Tests
- Test with ResearchAgent.solve() method
- Test mode validation and recommendations
- Test explicit mode detection
- Test context-aware selection

## Configuration

### config.json Updates
```json
{
  "mode_selection": {
    "enabled": true,
    "fallback_mode": "instant",
    "validation_enabled": true,
    "logging_enabled": true,
    "complexity_weights": {
      "comprehensive": 3,
      "exhaustive": 3,
      "detailed analysis": 3,
      "thorough": 2,
      "analysis": 2,
      "research": 2,
      "explain": 1,
      "describe": 1,
      "what is": 0
    },
    "length_thresholds": {
      "deep": 50,
      "standard": 25,
      "quick": 10,
      "instant": 0
    }
  }
}
```

## Success Criteria

- [ ] Intelligent mode selection works for various query types
- [ ] Explicit mode selection overrides automatic selection
- [ ] Context information influences mode selection
- [ ] Mode validation prevents inappropriate mode selection
- [ ] Mode recommendations provide helpful explanations
- [ ] Integration with ResearchAgent.solve() works seamlessly
- [ ] All existing tests pass with mode selection enabled
- [ ] Mode selection logging provides useful debugging information

## Implementation Order

1. **Create ModeSelector class with basic functionality**
2. **Implement query analysis methods**
3. **Add context analysis support**
4. **Create mode validation and recommendations**
5. **Integrate with ResearchAgent**
6. **Update configuration**
7. **Write comprehensive tests**
8. **Test with various query types**
9. **Update documentation and examples**
