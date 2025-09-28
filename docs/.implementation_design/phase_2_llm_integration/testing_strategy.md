# Phase 2 Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for Phase 2: LLM Integration, ensuring all components work correctly with real LLM providers while maintaining Phase 1 functionality.

## Testing Structure

### 1. Unit Testing

#### LLM Service Module Tests
```python
# tests/test_llm_service_phase2.py
class TestLLMServicePhase2(unittest.TestCase):
    """Test enhanced LLM service with real providers."""

    def setUp(self):
        self.config = {
            'llm': {
                'fallback_order': ['ollama', 'openai'],
                'providers': {
                    'ollama': {'base_url': 'http://localhost:11434'},
                    'openai': {'api_key': 'test-key'}
                }
            }
        }
        self.llm_service = LLMService(self.config)

    def test_model_detection(self):
        """Test model detection and selection."""
        model = self.llm_service.model_detector.detect_best_model()
        self.assertIsInstance(model, str)
        self.assertTrue(model.startswith(('ollama:', 'openai:', 'fallback')))

    def test_client_initialization(self):
        """Test client initialization."""
        self.assertIsNotNone(self.llm_service.client_manager)
        self.assertIsNotNone(self.llm_service.model_detector)

    def test_mode_specific_generation(self):
        """Test mode-specific response generation."""
        query = "What is artificial intelligence?"

        for mode in ['instant', 'quick', 'standard', 'deep']:
            response = self.llm_service.generate_response(query, mode)
            self.assertTrue(response['success'])
            self.assertEqual(response['data']['mode'], mode)

    def test_fallback_mechanism(self):
        """Test fallback to mock service."""
        # Mock all providers to fail
        for provider in self.llm_service.providers.values():
            provider.test_connection = Mock(return_value=False)

        response = self.llm_service.generate_response("Test query", "instant")
        self.assertTrue(response['success'])
        self.assertIn('Mock response', response['data']['content'])

    def test_shared_instance_management(self):
        """Test shared instance management."""
        service1 = get_shared_llm_service()
        service2 = get_shared_llm_service()
        self.assertIs(service1, service2)

        reset_shared_llm_service()
        service3 = get_shared_llm_service()
        self.assertIsNot(service1, service3)
```

#### Mode Selector Tests
```python
# tests/test_mode_selector.py
class TestModeSelector(unittest.TestCase):
    """Test mode selector functionality."""

    def setUp(self):
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

    def test_deep_mode_selection(self):
        """Test deep mode selection."""
        queries = [
            "Comprehensive analysis of AI ethics",
            "Exhaustive research on machine learning applications",
            "Detailed investigation of neural network architectures"
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

    def test_mode_validation(self):
        """Test mode validation."""
        query = "What is AI?"

        # Valid modes for simple query
        self.assertTrue(self.mode_selector.validate_mode_selection(query, 'instant'))
        self.assertTrue(self.mode_selector.validate_mode_selection(query, 'quick'))

        # Invalid mode for simple query
        self.assertFalse(self.mode_selector.validate_mode_selection(query, 'deep'))
```

#### Source Tracker Tests
```python
# tests/test_source_tracker.py
class TestSourceTracker(unittest.TestCase):
    """Test source tracker functionality."""

    def setUp(self):
        self.tracker = SourceTracker()

    def test_source_deduplication(self):
        """Test source deduplication."""
        url1 = "https://example.com/article"
        url2 = "https://www.example.com/article/"

        # Add first source
        self.assertTrue(self.tracker.add_source(url1, {}))

        # Try to add duplicate (normalized)
        self.assertFalse(self.tracker.add_source(url2, {}))

        # Check only one source is tracked
        self.assertEqual(len(self.tracker.used_sources), 1)

    def test_round_tracking(self):
        """Test round-based source tracking."""
        # Round 1
        self.tracker.start_new_round()
        self.tracker.add_source("https://source1.com", {})

        # Round 2
        self.tracker.start_new_round()
        self.tracker.add_source("https://source2.com", {})

        # Check round tracking
        self.assertEqual(self.tracker.current_round, 2)
        self.assertEqual(len(self.tracker.round_sources[1]), 1)
        self.assertEqual(len(self.tracker.round_sources[2]), 1)

    def test_url_normalization(self):
        """Test URL normalization."""
        normalizer = URLNormalizer()

        url1 = "https://www.example.com/path/"
        url2 = "https://example.com/path"

        normalized1 = normalizer.normalize_url(url1)
        normalized2 = normalizer.normalize_url(url2)

        self.assertEqual(normalized1, normalized2)
```

#### Temp File Manager Tests
```python
# tests/test_temp_file_manager.py
class TestTempFileManager(unittest.TestCase):
    """Test temp file manager functionality."""

    def setUp(self):
        self.temp_dir = Path("/tmp/test_research_agent")
        self.manager = TempFileManager(str(self.temp_dir))

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_session_creation(self):
        """Test session creation and directory structure."""
        session_id = "test_session_123"
        session_path = self.manager.create_session(session_id)

        self.assertTrue(session_path.exists())
        self.assertTrue((session_path / "research_data").exists())
        self.assertTrue((session_path / "intermediate_results").exists())
        self.assertTrue((session_path / "cache").exists())
        self.assertTrue((session_path / "logs").exists())

    def test_data_saving_and_loading(self):
        """Test saving and loading research data."""
        session_id = "test_session_456"
        self.manager.create_session(session_id)

        test_data = {
            'query': 'What is AI?',
            'response': 'AI is artificial intelligence',
            'sources': ['https://example.com']
        }

        # Save data
        file_path = self.manager.save_research_data(test_data, "test_data.json")
        self.assertTrue(file_path.exists())

        # Load data
        loaded_data = self.manager.load_research_data("test_data.json")
        self.assertEqual(loaded_data, test_data)

    def test_cache_functionality(self):
        """Test cache functionality."""
        session_id = "test_session_789"
        self.manager.create_session(session_id)

        cache = ResearchCache(self.manager.session_dir / "cache")

        # Cache a result
        test_result = {'response': 'Test response'}
        cache.cache_result("Test query", "instant", test_result)

        # Retrieve cached result
        cached_result = cache.get_cached_result("Test query", "instant")
        self.assertIsNotNone(cached_result)
        self.assertEqual(cached_result['result'], test_result)
```

### 2. Integration Testing

#### ResearchAgent Integration Tests
```python
# tests/test_research_agent_integration.py
class TestResearchAgentIntegration(unittest.TestCase):
    """Test ResearchAgent with Phase 2 components."""

    def setUp(self):
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

#### Workflow Integration Tests
```python
# tests/test_workflow_integration.py
class TestWorkflowIntegration(unittest.TestCase):
    """Test workflow integration with Phase 2 components."""

    def setUp(self):
        self.llm_service = LLMService()
        self.source_tracker = SourceTracker()
        self.temp_file_manager = TempFileManager()
        self.temp_file_manager.create_session("test_session")

    def test_instant_workflow_with_source_tracking(self):
        """Test instant workflow with source tracking."""
        workflow = InstantWorkflow(self.llm_service, self.source_tracker)

        result = workflow.execute("What is AI?")

        self.assertTrue(result['success'])
        self.assertEqual(result['data']['mode'], 'instant')
        self.assertGreaterEqual(result['data']['sources_used'], 0)

    def test_deep_workflow_with_file_management(self):
        """Test deep workflow with file management."""
        workflow = DeepWorkflow(
            self.llm_service,
            self.source_tracker,
            self.temp_file_manager
        )

        result = workflow.execute("Comprehensive analysis of AI ethics")

        self.assertTrue(result['success'])
        self.assertEqual(result['data']['mode'], 'deep')
        self.assertGreater(result['data']['research_rounds'], 1)

        # Check that files were created
        session_info = self.temp_file_manager.get_session_info("test_session")
        self.assertIsNotNone(session_info)
        self.assertGreater(session_info['file_counts']['research_data'], 0)
```

### 3. End-to-End Testing

#### Complete Research Flow Tests
```python
# tests/test_end_to_end.py
class TestEndToEnd(unittest.TestCase):
    """Test complete research flow with Phase 2 components."""

    def test_complete_research_flow(self):
        """Test complete research flow from query to result."""
        agent = ResearchAgent()

        # Test all research modes
        modes = ['instant', 'quick', 'standard', 'deep']

        for mode in modes:
            request = {
                'query': f'What is artificial intelligence? (mode: {mode})',
                'mode': mode
            }

            result = agent.solve(request)

            self.assertTrue(result['success'])
            self.assertEqual(result['data']['mode'], mode)
            self.assertIn('content', result['data']['response']['data'])
            self.assertGreaterEqual(result['data']['research_rounds'], 1)

    def test_mode_selection_accuracy(self):
        """Test mode selection accuracy with various queries."""
        agent = ResearchAgent()

        test_cases = [
            ("What is AI?", "instant"),
            ("How does machine learning work?", "quick"),
            ("Analyze the impact of AI on society", "standard"),
            ("Comprehensive analysis of AI ethics", "deep")
        ]

        for query, expected_mode in test_cases:
            request = {'query': query}
            result = agent.solve(request)

            self.assertTrue(result['success'])
            # Allow some flexibility in mode selection
            selected_mode = result['data']['mode']
            mode_hierarchy = ['instant', 'quick', 'standard', 'deep']
            expected_index = mode_hierarchy.index(expected_mode)
            selected_index = mode_hierarchy.index(selected_mode)

            # Allow selection within one level
            self.assertLessEqual(abs(selected_index - expected_index), 1)
```

### 4. Performance Testing

#### Response Time Tests
```python
# tests/test_performance.py
class TestPerformance(unittest.TestCase):
    """Test performance characteristics."""

    def test_response_times(self):
        """Test response times for different modes."""
        agent = ResearchAgent()

        query = "What is artificial intelligence?"
        modes = ['instant', 'quick', 'standard', 'deep']

        for mode in modes:
            start_time = time.time()

            request = {'query': query, 'mode': mode}
            result = agent.solve(request)

            end_time = time.time()
            response_time = end_time - start_time

            self.assertTrue(result['success'])

            # Check response time is reasonable
            if mode == 'instant':
                self.assertLess(response_time, 30)  # 30 seconds max
            elif mode == 'quick':
                self.assertLess(response_time, 120)  # 2 minutes max
            elif mode == 'standard':
                self.assertLess(response_time, 900)  # 15 minutes max
            elif mode == 'deep':
                self.assertLess(response_time, 1800)  # 30 minutes max

    def test_memory_usage(self):
        """Test memory usage during research."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        agent = ResearchAgent()

        # Perform multiple research operations
        for i in range(10):
            request = {'query': f'Test query {i}', 'mode': 'instant'}
            result = agent.solve(request)
            self.assertTrue(result['success'])

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Check memory increase is reasonable (less than 100MB)
        self.assertLess(memory_increase, 100 * 1024 * 1024)
```

### 5. Error Handling Tests

#### Error Recovery Tests
```python
# tests/test_error_handling.py
class TestErrorHandling(unittest.TestCase):
    """Test error handling and recovery."""

    def test_llm_service_failure_recovery(self):
        """Test recovery from LLM service failures."""
        # Mock LLM service to fail
        with patch('research_agent.llm_service.core.LLMService.generate_response') as mock_generate:
            mock_generate.side_effect = Exception("LLM service failed")

            agent = ResearchAgent()
            request = {'query': 'Test query'}
            result = agent.solve(request)

            # Should fallback to mock service
            self.assertTrue(result['success'])
            self.assertIn('Mock response', result['data']['response']['data']['content'])

    def test_invalid_query_handling(self):
        """Test handling of invalid queries."""
        agent = ResearchAgent()

        invalid_requests = [
            {'query': ''},  # Empty query
            {'query': None},  # None query
            {'mode': 'invalid_mode'},  # Invalid mode
        ]

        for request in invalid_requests:
            result = agent.solve(request)
            self.assertFalse(result['success'])
            self.assertIn('error', result)

    def test_file_management_error_recovery(self):
        """Test recovery from file management errors."""
        # Mock file operations to fail
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError("Permission denied")

            temp_manager = TempFileManager("/invalid/path")

            # Should handle error gracefully
            with self.assertRaises(OSError):
                temp_manager.create_session("test_session")
```

## Test Configuration

### Test Environment Setup
```python
# tests/conftest.py
import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def mock_llm_service():
    """Create mock LLM service for tests."""
    from research_agent.llm_service.mock_service import MockLLMService
    return MockLLMService()

@pytest.fixture
def test_config():
    """Create test configuration."""
    return {
        'llm': {
            'fallback_order': ['ollama', 'openai'],
            'providers': {
                'ollama': {'base_url': 'http://localhost:11434'},
                'openai': {'api_key': 'test-key'}
            }
        }
    }
```

### Test Data
```python
# tests/test_data.py
TEST_QUERIES = {
    'instant': [
        "What is AI?",
        "Define machine learning",
        "What does API mean?"
    ],
    'quick': [
        "How does machine learning work?",
        "Explain neural networks",
        "Describe the process of training a model"
    ],
    'standard': [
        "Analyze the impact of AI on society",
        "Research the latest developments in machine learning",
        "Compare different approaches to natural language processing"
    ],
    'deep': [
        "Comprehensive analysis of AI ethics",
        "Exhaustive research on machine learning applications",
        "Detailed investigation of neural network architectures"
    ]
}

TEST_SOURCES = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://scholar.google.com/scholar?q=artificial+intelligence",
    "https://arxiv.org/abs/2101.00001",
    "https://github.com/tensorflow/tensorflow",
    "https://stackoverflow.com/questions/tagged/artificial-intelligence"
]
```

## Test Execution

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test modules
python -m pytest tests/test_llm_service_phase2.py
python -m pytest tests/test_mode_selector.py
python -m pytest tests/test_source_tracker.py
python -m pytest tests/test_temp_file_manager.py

# Run with coverage
python -m pytest --cov=research_agent tests/

# Run performance tests
python -m pytest tests/test_performance.py -v

# Run integration tests
python -m pytest tests/test_integration.py -v
```

### Continuous Integration
```yaml
# .github/workflows/test.yml
name: Phase 2 Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        python -m pytest tests/ --cov=research_agent --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## Success Criteria

### Test Coverage
- [ ] Unit test coverage > 80%
- [ ] Integration test coverage > 70%
- [ ] All critical paths tested
- [ ] Error conditions covered

### Functional Testing
- [ ] All Phase 1 functionality preserved
- [ ] Real LLM integration works
- [ ] Mode selection accuracy > 80%
- [ ] Source tracking prevents duplicates
- [ ] File management works correctly

### Performance Testing
- [ ] Response times within limits
- [ ] Memory usage optimized
- [ ] File cleanup prevents issues
- [ ] Cache improves performance

### Error Handling
- [ ] Graceful failure recovery
- [ ] Fallback mechanisms work
- [ ] Error messages are helpful
- [ ] System remains stable

This comprehensive testing strategy ensures Phase 2 implementation is robust, reliable, and maintains the quality established in Phase 1.
