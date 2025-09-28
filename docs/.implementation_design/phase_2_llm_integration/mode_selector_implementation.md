# Mode Selector Implementation - Phase 2

## Overview

This document details the implementation of the intelligent mode selector for Phase 2, which automatically selects the appropriate research mode based on query analysis and context.

## Current State (Phase 1)

The current implementation has basic mode selection in the `solve()` method:
- Simple keyword-based mode detection
- Fallback to 'standard' mode
- No context awareness
- No complexity analysis

## Phase 2 Enhancements

### 1. ModeSelector Class Implementation

```python
# research_agent/research_agent/mode_selector.py
import re
from typing import Dict, Any, Optional, List
from enum import Enum
from ..base_agent.error_handler import ErrorHandler
from ..utils.utils import format_response

class ResearchComplexity(Enum):
    """Research complexity levels."""
    INSTANT = "instant"
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"

class ModeSelector:
    """Intelligent mode selection based on query analysis."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.error_handler = ErrorHandler("ModeSelector")
        
        # Complexity indicators with weights
        self.complexity_indicators = {
            # High complexity (3 points)
            'comprehensive': 3,
            'exhaustive': 3,
            'detailed analysis': 3,
            'thorough investigation': 3,
            'in-depth study': 3,
            'complete analysis': 3,
            'full research': 3,
            'extensive research': 3,
            
            # Medium complexity (2 points)
            'thorough': 2,
            'analysis': 2,
            'research': 2,
            'investigation': 2,
            'study': 2,
            'examine': 2,
            'explore': 2,
            'evaluate': 2,
            'assess': 2,
            'compare': 2,
            'contrast': 2,
            'review': 2,
            
            # Low complexity (1 point)
            'explain': 1,
            'describe': 1,
            'discuss': 1,
            'outline': 1,
            'summarize': 1,
            'overview': 1,
            'introduction': 1,
            'basics': 1,
            'fundamentals': 1,
            
            # Very low complexity (0 points)
            'what is': 0,
            'define': 0,
            'meaning': 0,
            'definition': 0
        }
        
        # Explicit mode indicators
        self.explicit_indicators = {
            'instant': ['quick answer', 'immediate', 'fast', 'brief', 'short'],
            'quick': ['quick analysis', 'enhanced', 'context', 'overview'],
            'standard': ['comprehensive', 'detailed', 'thorough', 'analysis'],
            'deep': ['exhaustive', 'in-depth', 'extensive', 'complete', 'full research']
        }
        
        # Question type patterns
        self.question_patterns = {
            'what': 0,      # Definitional questions
            'how': 1,       # Process questions
            'why': 2,       # Explanatory questions
            'when': 0,      # Temporal questions
            'where': 0,     # Locational questions
            'who': 0,       # Identity questions
            'which': 1,     # Comparative questions
            'compare': 2,   # Comparative analysis
            'contrast': 2,  # Contrastive analysis
            'analyze': 3,   # Analysis requests
            'evaluate': 3,  # Evaluation requests
            'assess': 3     # Assessment requests
        }
    
    def select_mode(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Select optimal research mode based on query analysis.
        
        Args:
            query: Research query
            context: Additional context information
            
        Returns:
            Selected research mode
        """
        try:
            # Clean and normalize query
            normalized_query = self._normalize_query(query)
            
            # Check for explicit mode indicators first
            explicit_mode = self._detect_explicit_mode(normalized_query)
            if explicit_mode:
                return explicit_mode
            
            # Analyze query complexity
            complexity_score = self._analyze_complexity(normalized_query)
            
            # Analyze query length and structure
            length_score = self._analyze_length(normalized_query)
            
            # Analyze question type
            question_score = self._analyze_question_type(normalized_query)
            
            # Analyze context if provided
            context_score = self._analyze_context(context) if context else 0
            
            # Combine scores
            total_score = complexity_score + length_score + question_score + context_score
            
            # Map score to mode
            selected_mode = self._score_to_mode(total_score)
            
            # Log selection for debugging
            self.error_handler.logger.debug(
                f"Mode selection: query='{query[:50]}...', "
                f"complexity={complexity_score}, length={length_score}, "
                f"question={question_score}, context={context_score}, "
                f"total={total_score}, mode={selected_mode}"
            )
            
            return selected_mode
            
        except Exception as e:
            self.error_handler.log_error(e, {'query': query, 'context': context})
            return 'instant'  # Safe fallback
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for analysis."""
        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove punctuation at the end
        normalized = re.sub(r'[.!?]+$', '', normalized)
        
        return normalized
    
    def _detect_explicit_mode(self, query: str) -> Optional[str]:
        """Detect explicit mode indicators in query."""
        for mode, indicators in self.explicit_indicators.items():
            for indicator in indicators:
                if indicator in query:
                    return mode
        return None
    
    def _analyze_complexity(self, query: str) -> int:
        """Analyze query complexity based on keywords."""
        score = 0
        
        for indicator, weight in self.complexity_indicators.items():
            if indicator in query:
                score += weight
        
        # Cap the score to prevent extreme values
        return min(score, 8)
    
    def _analyze_length(self, query: str) -> int:
        """Analyze query length and structure."""
        word_count = len(query.split())
        char_count = len(query)
        
        # Length scoring
        if word_count >= 50 or char_count >= 300:
            return 3  # Very long queries suggest deep research
        elif word_count >= 25 or char_count >= 150:
            return 2  # Long queries suggest standard research
        elif word_count >= 10 or char_count >= 60:
            return 1  # Medium queries suggest quick research
        else:
            return 0  # Short queries suggest instant research
    
    def _analyze_question_type(self, query: str) -> int:
        """Analyze question type and complexity."""
        score = 0
        
        for pattern, weight in self.question_patterns.items():
            if pattern in query:
                score = max(score, weight)  # Take highest weight found
        
        return score
    
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
    
    def get_mode_explanation(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get detailed explanation of mode selection.
        
        Args:
            query: Research query
            context: Additional context
            
        Returns:
            Detailed explanation of mode selection
        """
        normalized_query = self._normalize_query(query)
        
        # Analyze each component
        explicit_mode = self._detect_explicit_mode(normalized_query)
        complexity_score = self._analyze_complexity(normalized_query)
        length_score = self._analyze_length(normalized_query)
        question_score = self._analyze_question_type(normalized_query)
        context_score = self._analyze_context(context) if context else 0
        
        total_score = complexity_score + length_score + question_score + context_score
        selected_mode = self._score_to_mode(total_score)
        
        return {
            'selected_mode': selected_mode,
            'explicit_mode': explicit_mode,
            'scores': {
                'complexity': complexity_score,
                'length': length_score,
                'question_type': question_score,
                'context': context_score,
                'total': total_score
            },
            'analysis': {
                'query_length': len(normalized_query.split()),
                'query_chars': len(normalized_query),
                'complexity_keywords': self._get_matched_keywords(normalized_query),
                'question_type': self._get_question_type(normalized_query),
                'context_info': context or {}
            }
        }
    
    def _get_matched_keywords(self, query: str) -> List[str]:
        """Get matched complexity keywords."""
        matched = []
        for indicator in self.complexity_indicators:
            if indicator in query:
                matched.append(indicator)
        return matched
    
    def _get_question_type(self, query: str) -> str:
        """Get detected question type."""
        for pattern in self.question_patterns:
            if pattern in query:
                return pattern
        return 'unknown'
    
    def validate_mode_selection(self, query: str, mode: str) -> bool:
        """
        Validate if the selected mode is appropriate for the query.
        
        Args:
            query: Research query
            mode: Selected mode
            
        Returns:
            True if mode is appropriate, False otherwise
        """
        explanation = self.get_mode_explanation(query)
        recommended_mode = explanation['selected_mode']
        
        # Allow some flexibility in mode selection
        mode_hierarchy = ['instant', 'quick', 'standard', 'deep']
        recommended_index = mode_hierarchy.index(recommended_mode)
        selected_index = mode_hierarchy.index(mode)
        
        # Allow selection within one level of recommendation
        return abs(selected_index - recommended_index) <= 1
    
    def get_mode_recommendations(self, query: str) -> List[Dict[str, Any]]:
        """
        Get recommendations for all modes with explanations.
        
        Args:
            query: Research query
            
        Returns:
            List of mode recommendations with scores
        """
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
    
    def _calculate_mode_suitability(self, query: str, mode: str) -> float:
        """Calculate suitability score for a specific mode."""
        explanation = self.get_mode_explanation(query)
        total_score = explanation['scores']['total']
        
        # Map total score to 0-1 suitability
        if mode == 'instant':
            return max(0, 1 - (total_score / 8))
        elif mode == 'quick':
            return max(0, 1 - abs(total_score - 2) / 6)
        elif mode == 'standard':
            return max(0, 1 - abs(total_score - 5) / 6)
        elif mode == 'deep':
            return max(0, total_score / 8)
        
        return 0.0
    
    def _get_mode_description(self, mode: str) -> str:
        """Get description for a research mode."""
        descriptions = {
            'instant': 'Quick single-round research for immediate answers',
            'quick': 'Enhanced single-round research with context',
            'standard': 'Multi-round comprehensive research',
            'deep': 'Exhaustive multi-round research with thorough analysis'
        }
        return descriptions.get(mode, 'Unknown mode')
```

### 2. Integration with ResearchAgent

#### Enhanced ResearchAgent Implementation
```python
# research_agent/research_agent/core.py (enhanced solve method)
from .mode_selector import ModeSelector

class ResearchAgent(BaseAgent):
    """Enhanced ResearchAgent with intelligent mode selection."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(config, **kwargs)
        
        # Initialize Phase 2 components
        self.mode_selector = ModeSelector(config)
        
        # Enhanced LLM service (from Phase 2)
        self.llm_service = LLMService(config)
        
        # Other Phase 2 components...
    
    def solve(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced solve method with intelligent mode selection.
        
        Args:
            request: Request dictionary with query and optional mode/context
            
        Returns:
            Research results
        """
        try:
            # Validate request
            schema = {
                'type': 'object',
                'required': ['query'],
                'properties': {
                    'query': {'type': 'string', 'minLength': 1},
                    'mode': {'type': 'string', 'enum': ['instant', 'quick', 'standard', 'deep']},
                    'context': {'type': 'object'}
                }
            }
            
            if not self.validate_request(request, schema):
                return format_response(
                    success=False,
                    message="Invalid request format for solve method"
                )
            
            query = sanitize_string(request['query'])
            explicit_mode = request.get('mode')
            context = request.get('context', {})
            
            # Use intelligent mode selection if no explicit mode
            if not explicit_mode:
                selected_mode = self.mode_selector.select_mode(query, context)
                
                # Log mode selection for debugging
                self.logger.info(f"Auto-selected mode '{selected_mode}' for query: {query[:50]}...")
            else:
                selected_mode = explicit_mode
                
                # Validate explicit mode selection
                if not self.mode_selector.validate_mode_selection(query, selected_mode):
                    self.logger.warning(
                        f"Explicit mode '{selected_mode}' may not be optimal for query: {query[:50]}..."
                    )
            
            # Route to appropriate research method
            if selected_mode == 'instant':
                return self.instant_research({'query': query, 'context': context})
            elif selected_mode == 'quick':
                return self.quick_research({'query': query, 'context': context})
            elif selected_mode == 'standard':
                return self.standard_research({'query': query, 'context': context})
            elif selected_mode == 'deep':
                return self.deep_research({'query': query, 'context': context})
            else:
                return format_response(
                    success=False,
                    message=f"Invalid research mode: {selected_mode}"
                )
                
        except Exception as e:
            error_msg = self.error_messages.get('solve', 'Error in research: {error}')
            return self.error_handler.handle_error(
                e,
                {'request': request},
                error_msg.format(error=str(e))
            )
    
    def get_mode_recommendations(self, query: str) -> Dict[str, Any]:
        """
        Get mode recommendations for a query.
        
        Args:
            query: Research query
            
        Returns:
            Mode recommendations with explanations
        """
        try:
            recommendations = self.mode_selector.get_mode_recommendations(query)
            explanation = self.mode_selector.get_mode_explanation(query)
            
            return format_response(
                success=True,
                data={
                    'query': query,
                    'recommendations': recommendations,
                    'explanation': explanation
                },
                message="Mode recommendations generated"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'query': query},
                "Error generating mode recommendations"
            )
```

### 3. Configuration Updates

#### Enhanced config.json
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
    },
    "question_type_weights": {
      "analyze": 3,
      "evaluate": 3,
      "assess": 3,
      "compare": 2,
      "contrast": 2,
      "why": 2,
      "how": 1,
      "which": 1,
      "what": 0,
      "when": 0,
      "where": 0,
      "who": 0
    }
  }
}
```

## Testing Strategy

### Unit Tests
```python
# tests/test_mode_selector.py
import unittest
from research_agent.research_agent.mode_selector import ModeSelector

class TestModeSelector(unittest.TestCase):
    """Test mode selector functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mode_selector = ModeSelector()
    
    def test_instant_mode_selection(self):
        """Test instant mode selection."""
        queries = [
            "What is AI?",
            "Define machine learning",
            "What does API mean?"
        ]
        
        for query in queries:
            mode = self.mode_selector.select_mode(query)
            self.assertEqual(mode, 'instant')
    
    def test_quick_mode_selection(self):
        """Test quick mode selection."""
        queries = [
            "How does machine learning work?",
            "Explain neural networks",
            "Describe the process of training a model"
        ]
        
        for query in queries:
            mode = self.mode_selector.select_mode(query)
            self.assertEqual(mode, 'quick')
    
    def test_standard_mode_selection(self):
        """Test standard mode selection."""
        queries = [
            "Analyze the impact of AI on society",
            "Research the latest developments in machine learning",
            "Compare different approaches to natural language processing"
        ]
        
        for query in queries:
            mode = self.mode_selector.select_mode(query)
            self.assertEqual(mode, 'standard')
    
    def test_deep_mode_selection(self):
        """Test deep mode selection."""
        queries = [
            "Conduct comprehensive analysis of AI ethics",
            "Exhaustive research on machine learning applications",
            "Detailed investigation of neural network architectures"
        ]
        
        for query in queries:
            mode = self.mode_selector.select_mode(query)
            self.assertEqual(mode, 'deep')
    
    def test_explicit_mode_detection(self):
        """Test explicit mode detection."""
        queries = [
            "Quick answer: What is AI?",
            "Comprehensive analysis of machine learning",
            "Exhaustive research on neural networks"
        ]
        
        expected_modes = ['instant', 'standard', 'deep']
        
        for query, expected_mode in zip(queries, expected_modes):
            mode = self.mode_selector.select_mode(query)
            self.assertEqual(mode, expected_mode)
    
    def test_context_analysis(self):
        """Test context analysis."""
        query = "What is machine learning?"
        
        # Test with different contexts
        contexts = [
            {'research_depth': 'deep', 'time_constraint': 'flexible'},
            {'research_depth': 'quick', 'time_constraint': 'urgent'},
            {'available_tools': ['web_search', 'document_analysis', 'data_analysis']}
        ]
        
        expected_modes = ['deep', 'quick', 'standard']
        
        for context, expected_mode in zip(contexts, expected_modes):
            mode = self.mode_selector.select_mode(query, context)
            self.assertEqual(mode, expected_mode)
    
    def test_mode_explanation(self):
        """Test mode explanation generation."""
        query = "Comprehensive analysis of AI impact on society"
        explanation = self.mode_selector.get_mode_explanation(query)
        
        self.assertIn('selected_mode', explanation)
        self.assertIn('scores', explanation)
        self.assertIn('analysis', explanation)
        self.assertEqual(explanation['selected_mode'], 'deep')
    
    def test_mode_recommendations(self):
        """Test mode recommendations."""
        query = "How does machine learning work?"
        recommendations = self.mode_selector.get_mode_recommendations(query)
        
        self.assertEqual(len(recommendations), 4)
        self.assertTrue(any(r['recommended'] for r in recommendations))
        
        # Check that quick mode is recommended
        quick_rec = next(r for r in recommendations if r['mode'] == 'quick')
        self.assertTrue(quick_rec['recommended'])
    
    def test_mode_validation(self):
        """Test mode validation."""
        query = "What is AI?"
        
        # Valid modes for simple query
        self.assertTrue(self.mode_selector.validate_mode_selection(query, 'instant'))
        self.assertTrue(self.mode_selector.validate_mode_selection(query, 'quick'))
        
        # Invalid mode for simple query
        self.assertFalse(self.mode_selector.validate_mode_selection(query, 'deep'))
```

### Integration Tests
```python
# tests/test_research_agent_mode_selection.py
import unittest
from research_agent.research_agent.core import ResearchAgent

class TestResearchAgentModeSelection(unittest.TestCase):
    """Test ResearchAgent with mode selection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = ResearchAgent()
    
    def test_solve_with_auto_mode_selection(self):
        """Test solve method with automatic mode selection."""
        request = {'query': 'What is artificial intelligence?'}
        result = self.agent.solve(request)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIn('mode', result['data'])
        
        # Should select instant mode for simple query
        self.assertEqual(result['data']['mode'], 'instant')
    
    def test_solve_with_explicit_mode(self):
        """Test solve method with explicit mode."""
        request = {
            'query': 'What is AI?',
            'mode': 'deep'
        }
        result = self.agent.solve(request)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['mode'], 'deep')
    
    def test_solve_with_context(self):
        """Test solve method with context."""
        request = {
            'query': 'What is machine learning?',
            'context': {
                'research_depth': 'deep',
                'time_constraint': 'flexible'
            }
        }
        result = self.agent.solve(request)
        
        self.assertTrue(result['success'])
        # Should select deep mode due to context
        self.assertEqual(result['data']['mode'], 'deep')
    
    def test_mode_recommendations(self):
        """Test mode recommendations."""
        query = "Comprehensive analysis of AI ethics"
        result = self.agent.get_mode_recommendations(query)
        
        self.assertTrue(result['success'])
        self.assertIn('recommendations', result['data'])
        self.assertIn('explanation', result['data'])
        
        # Should recommend deep mode
        recommendations = result['data']['recommendations']
        deep_rec = next(r for r in recommendations if r['mode'] == 'deep')
        self.assertTrue(deep_rec['recommended'])
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
- [ ] Configuration allows customization of selection criteria

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
