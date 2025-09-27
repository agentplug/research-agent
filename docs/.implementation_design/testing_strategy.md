# Testing Strategy Implementation Design

## Overview

This document provides detailed testing strategy for the Deep Research Agent implementation. It covers unit testing, integration testing, and end-to-end testing approaches to ensure reliability and maintainability.

## Testing Structure

```
tests/
├── unit/                           # Unit tests
│   ├── test_base_agent.py
│   ├── test_research_agent.py
│   ├── test_llm_service.py
│   ├── test_source_tracker.py
│   ├── test_file_manager.py
│   └── test_utils.py
├── integration/                    # Integration tests
│   ├── test_agent_integration.py
│   ├── test_tool_integration.py
│   └── test_llm_integration.py
├── e2e/                           # End-to-end tests
│   ├── test_research_workflows.py
│   ├── test_agenthub_integration.py
│   └── test_performance.py
├── fixtures/                      # Test fixtures
│   ├── sample_research_data.json
│   ├── mock_tool_responses.json
│   └── test_configs.json
└── conftest.py                    # Pytest configuration
```

## Unit Testing

### 1. Base Agent Tests (`test_base_agent.py`)

```python
"""
Unit tests for BaseAgent functionality.
"""

import pytest
from unittest.mock import Mock, patch
from src.base_agent.core import BaseAgent
from src.base_agent.context_manager import ContextManager
from src.base_agent.error_handler import ErrorHandler


class TestBaseAgent:
    """Test cases for BaseAgent class."""
    
    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLM service for testing."""
        return Mock()
    
    @pytest.fixture
    def base_agent(self, mock_llm_service):
        """Create BaseAgent instance for testing."""
        return BaseAgent(mock_llm_service)
    
    def test_initialization(self, base_agent, mock_llm_service):
        """Test BaseAgent initialization."""
        assert base_agent.llm_service == mock_llm_service
        assert isinstance(base_agent.context_manager, ContextManager)
        assert isinstance(base_agent.error_handler, ErrorHandler)
    
    def test_get_available_tools(self, base_agent):
        """Test getting available tools."""
        base_agent.external_tools = ["web_search", "academic_search"]
        tools = base_agent.get_available_tools()
        assert tools == ["web_search", "academic_search"]
    
    def test_validate_input_valid(self, base_agent):
        """Test input validation with valid data."""
        valid_input = {"question": "Test question", "mode": "instant"}
        assert base_agent.validate_input(valid_input) is True
    
    def test_validate_input_invalid(self, base_agent):
        """Test input validation with invalid data."""
        invalid_input = {"question": ""}  # Empty question
        assert base_agent.validate_input(invalid_input) is False
    
    @pytest.mark.asyncio
    async def test_handle_error(self, base_agent):
        """Test error handling."""
        error = Exception("Test error")
        result = await base_agent.handle_error(error)
        
        assert "error" in result
        assert result["error"] == "Test error"
        assert "timestamp" in result


class TestContextManager:
    """Test cases for ContextManager class."""
    
    @pytest.fixture
    def context_manager(self):
        """Create ContextManager instance for testing."""
        return ContextManager()
    
    def test_set_get_context(self, context_manager):
        """Test setting and getting context."""
        context_manager.set_context("test_key", "test_value")
        assert context_manager.get_context("test_key") == "test_value"
    
    def test_clear_context(self, context_manager):
        """Test clearing context."""
        context_manager.set_context("test_key", "test_value")
        context_manager.clear_context()
        assert context_manager.get_context("test_key") is None


class TestErrorHandler:
    """Test cases for ErrorHandler class."""
    
    @pytest.fixture
    def error_handler(self):
        """Create ErrorHandler instance for testing."""
        return ErrorHandler()
    
    def test_log_error(self, error_handler, caplog):
        """Test error logging."""
        error = Exception("Test error")
        context = {"test": "context"}
        
        error_handler.log_error(error, context)
        
        assert "Test error" in caplog.text
        assert "context" in caplog.text
```

### 2. Research Agent Tests (`test_research_agent.py`)

```python
"""
Unit tests for ResearchAgent functionality.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.research_agent.core import ResearchAgent


class TestResearchAgent:
    """Test cases for ResearchAgent class."""
    
    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLM service for testing."""
        service = Mock()
        service.generate = AsyncMock(return_value="Test response")
        return service
    
    @pytest.fixture
    def research_agent(self, mock_llm_service):
        """Create ResearchAgent instance for testing."""
        return ResearchAgent(mock_llm_service)
    
    @pytest.mark.asyncio
    async def test_instant_research(self, research_agent):
        """Test instant research mode."""
        question = "What is AI?"
        result = await research_agent.instant_research(question)
        
        assert "result" in result
        assert result["mode"] == "instant"
        assert result["rounds"] == 1
    
    @pytest.mark.asyncio
    async def test_quick_research(self, research_agent):
        """Test quick research mode."""
        question = "How does machine learning work?"
        result = await research_agent.quick_research(question)
        
        assert "result" in result
        assert result["mode"] == "quick"
        assert result["rounds"] == 2
    
    @pytest.mark.asyncio
    async def test_standard_research(self, research_agent):
        """Test standard research mode."""
        question = "What are the latest developments in AI?"
        result = await research_agent.standard_research(question)
        
        assert "result" in result
        assert result["mode"] == "standard"
        assert result["rounds"] == 5
    
    @pytest.mark.asyncio
    async def test_deep_research(self, research_agent):
        """Test deep research mode."""
        question = "Comprehensive analysis of AI ethics"
        result = await research_agent.deep_research(question)
        
        assert "result" in result
        assert result["mode"] == "deep"
        assert result["rounds"] == 12
    
    @pytest.mark.asyncio
    async def test_solve_auto_mode_selection(self, research_agent):
        """Test automatic mode selection."""
        # Test instant mode selection
        short_question = "What is AI?"
        result = await research_agent.solve(short_question)
        assert result["mode"] == "instant"
        
        # Test deep mode selection
        long_question = "Provide a comprehensive analysis of the ethical implications of artificial intelligence in healthcare, including privacy concerns, bias in algorithms, patient autonomy, and the role of regulatory frameworks in ensuring responsible AI deployment."
        result = await research_agent.solve(long_question)
        assert result["mode"] == "deep"
    
    def test_build_research_prompt(self, research_agent):
        """Test research prompt building."""
        prompt = research_agent._build_research_prompt("instant")
        assert "instant" in prompt.lower()
        assert "research" in prompt.lower()
    
    def test_process_research_response(self, research_agent):
        """Test research response processing."""
        response = '{"tool_calls": [{"tool": "web_search", "parameters": {"query": "test"}}]}'
        result = research_agent._process_research_response(response, "instant")
        
        assert result["status"] == "tool_requested"
        assert "tool_calls" in result
```

### 3. LLM Service Tests (`test_llm_service.py`)

```python
"""
Unit tests for LLM service functionality.
"""

import pytest
from unittest.mock import Mock, patch
from src.llm_service.core import CoreLLMService
from src.llm_service.model_detector import ModelDetector


class TestCoreLLMService:
    """Test cases for CoreLLMService class."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock AISuite client for testing."""
        client = Mock()
        client.chat.completions.create = Mock()
        return client
    
    @pytest.fixture
    def llm_service(self, mock_client):
        """Create CoreLLMService instance for testing."""
        with patch('src.llm_service.core.ClientManager') as mock_manager:
            mock_manager.return_value.initialize_client.return_value = mock_client
            service = CoreLLMService(model="test-model")
            service.client = mock_client
            return service
    
    def test_initialization(self, llm_service):
        """Test LLM service initialization."""
        assert llm_service.model == "test-model"
        assert llm_service.client is not None
    
    def test_generate_simple(self, llm_service, mock_client):
        """Test simple text generation."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        result = llm_service.generate("Test prompt")
        
        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once()
    
    def test_generate_with_system_prompt(self, llm_service, mock_client):
        """Test generation with system prompt."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        result = llm_service.generate(
            "Test prompt",
            system_prompt="You are a helpful assistant"
        )
        
        assert result == "Test response"
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
    
    def test_generate_research_analysis(self, llm_service):
        """Test research analysis generation."""
        question = "What is AI?"
        data = [{"title": "AI Article", "content": "AI content", "source": "test.com"}]
        
        with patch.object(llm_service, 'generate') as mock_generate:
            mock_generate.return_value = "Analysis result"
            
            result = llm_service.generate_research_analysis(question, data)
            
            assert result == "Analysis result"
            mock_generate.assert_called_once()
    
    def test_generate_clarification_questions(self, llm_service):
        """Test clarification question generation."""
        question = "Research AI ethics"
        
        with patch.object(llm_service, 'generate') as mock_generate:
            mock_generate.return_value = '["What specific aspects of AI ethics?", "What time frame?"]'
            
            result = llm_service.generate_clarification_questions(question)
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert "ethics" in result[0].lower()
    
    def test_is_local_model(self, llm_service):
        """Test local model detection."""
        llm_service.model = "ollama:gpt-oss:20b"
        assert llm_service.is_local_model() is True
        
        llm_service.model = "gpt-4"
        assert llm_service.is_local_model() is False


class TestModelDetector:
    """Test cases for ModelDetector class."""
    
    @pytest.fixture
    def model_detector(self):
        """Create ModelDetector instance for testing."""
        return ModelDetector()
    
    def test_detect_best_model(self, model_detector):
        """Test best model detection."""
        with patch.object(model_detector, '_detect_local_models') as mock_local:
            with patch.object(model_detector, '_detect_cloud_models') as mock_cloud:
                mock_local.return_value = []
                mock_cloud.return_value = [Mock(name="test-model")]
                
                result = model_detector.detect_best_model()
                
                assert result == "test-model"
    
    def test_calculate_model_score(self, model_detector):
        """Test model scoring calculation."""
        score = model_detector._calculate_model_score("gpt-oss:20b")
        assert score > 0
        
        score = model_detector._calculate_model_score("embedding-model")
        assert score < 0  # Embedding models should have negative scores
```

### 4. Source Tracker Tests (`test_source_tracker.py`)

```python
"""
Unit tests for source tracking functionality.
"""

import pytest
import tempfile
import os
from src.research_agent.source_tracker import SourceTracker


class TestSourceTracker:
    """Test cases for SourceTracker class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        return tempfile.mkdtemp()
    
    @pytest.fixture
    def source_tracker(self, temp_dir):
        """Create SourceTracker instance for testing."""
        return SourceTracker(temp_dir=temp_dir)
    
    def test_initialization(self, source_tracker):
        """Test SourceTracker initialization."""
        assert source_tracker.session_id is not None
        assert source_tracker.tracking_file is not None
        assert len(source_tracker.url_hashes) == 0
    
    def test_normalize_url(self, source_tracker):
        """Test URL normalization."""
        url = "https://example.com/page?utm_source=test&utm_campaign=test"
        normalized = source_tracker._normalize_url(url)
        assert "utm_source" not in normalized
        assert "utm_campaign" not in normalized
    
    def test_track_url(self, source_tracker):
        """Test URL tracking."""
        url = "https://example.com/test"
        metadata = {"title": "Test Page"}
        
        result = source_tracker.track_url(url, metadata)
        
        assert result is True
        assert source_tracker.is_url_tracked(url) is True
        assert len(source_tracker.url_hashes) == 1
    
    def test_track_duplicate_url(self, source_tracker):
        """Test tracking duplicate URL."""
        url = "https://example.com/test"
        
        # Track first time
        result1 = source_tracker.track_url(url)
        assert result1 is True
        
        # Track second time
        result2 = source_tracker.track_url(url)
        assert result2 is False
    
    def test_filter_new_urls(self, source_tracker):
        """Test filtering new URLs."""
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        # Track first URL
        source_tracker.track_url(urls[0])
        
        # Filter new URLs
        new_urls = source_tracker.filter_new_urls(urls)
        
        assert len(new_urls) == 2
        assert urls[0] not in new_urls
        assert urls[1] in new_urls
        assert urls[2] in new_urls
    
    def test_get_session_stats(self, source_tracker):
        """Test session statistics."""
        source_tracker.track_url("https://example.com/test")
        
        stats = source_tracker.get_session_stats()
        
        assert stats["total_tracked_urls"] == 1
        assert stats["session_new_urls"] == 1
        assert "session_id" in stats
```

## Integration Testing

### 1. Agent Integration Tests (`test_agent_integration.py`)

```python
"""
Integration tests for agent components.
"""

import pytest
from unittest.mock import Mock, patch
from src.research_agent.core import ResearchAgent
from src.llm_service.core import CoreLLMService


class TestAgentIntegration:
    """Integration tests for agent components."""
    
    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLM service for integration testing."""
        service = Mock(spec=CoreLLMService)
        service.generate = Mock(return_value="Test response")
        return service
    
    @pytest.fixture
    def research_agent(self, mock_llm_service):
        """Create ResearchAgent for integration testing."""
        return ResearchAgent(mock_llm_service)
    
    def test_research_workflow_integration(self, research_agent):
        """Test complete research workflow integration."""
        question = "What is artificial intelligence?"
        
        with patch.object(research_agent, '_execute_research_workflow') as mock_workflow:
            mock_workflow.return_value = {
                "result": "AI is a field of computer science...",
                "mode": "instant",
                "sources": ["https://example.com/ai"]
            }
            
            result = research_agent.instant_research(question)
            
            assert "result" in result
            assert result["mode"] == "instant"
            mock_workflow.assert_called_once()
    
    def test_tool_integration(self, research_agent):
        """Test tool integration with research agent."""
        tool_context = {
            "available_tools": ["web_search", "academic_search"],
            "tool_descriptions": {
                "web_search": "Search the web",
                "academic_search": "Search academic sources"
            }
        }
        
        agent = ResearchAgent(tool_context=tool_context)
        
        assert len(agent.available_tools) == 2
        assert "web_search" in agent.available_tools
        assert "academic_search" in agent.available_tools
    
    def test_llm_service_integration(self, research_agent, mock_llm_service):
        """Test LLM service integration."""
        question = "Test question"
        
        research_agent.instant_research(question)
        
        # Verify LLM service was called
        mock_llm_service.generate.assert_called()
```

## End-to-End Testing

### 1. Research Workflow Tests (`test_research_workflows.py`)

```python
"""
End-to-end tests for research workflows.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.research_agent.core import ResearchAgent


class TestResearchWorkflows:
    """End-to-end tests for research workflows."""
    
    @pytest.fixture
    def research_agent(self):
        """Create ResearchAgent for E2E testing."""
        mock_llm = Mock()
        mock_llm.generate = Mock(return_value="Test research result")
        return ResearchAgent(mock_llm)
    
    @pytest.mark.asyncio
    async def test_instant_research_workflow(self, research_agent):
        """Test complete instant research workflow."""
        question = "What is machine learning?"
        
        with patch.object(research_agent, '_execute_research_workflow') as mock_workflow:
            mock_workflow.return_value = {
                "result": "Machine learning is a subset of AI...",
                "mode": "instant",
                "sources": ["https://example.com/ml"],
                "rounds": 1
            }
            
            result = await research_agent.instant_research(question)
            
            assert result["mode"] == "instant"
            assert "result" in result
            mock_workflow.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_quick_research_workflow(self, research_agent):
        """Test complete quick research workflow."""
        question = "How does deep learning work?"
        
        with patch.object(research_agent, '_execute_research_workflow') as mock_workflow:
            mock_workflow.return_value = {
                "result": "Deep learning uses neural networks...",
                "mode": "quick",
                "sources": ["https://example.com/dl1", "https://example.com/dl2"],
                "rounds": 2
            }
            
            result = await research_agent.quick_research(question)
            
            assert result["mode"] == "quick"
            assert result["rounds"] == 2
            assert "result" in result
    
    @pytest.mark.asyncio
    async def test_standard_research_workflow(self, research_agent):
        """Test complete standard research workflow."""
        question = "What are the latest AI developments?"
        
        with patch.object(research_agent, '_execute_research_workflow') as mock_workflow:
            mock_workflow.return_value = {
                "result": "Recent AI developments include...",
                "mode": "standard",
                "sources": ["https://example.com/ai1", "https://example.com/ai2"],
                "rounds": 5
            }
            
            result = await research_agent.standard_research(question)
            
            assert result["mode"] == "standard"
            assert result["rounds"] == 5
            assert "result" in result
    
    @pytest.mark.asyncio
    async def test_deep_research_workflow(self, research_agent):
        """Test complete deep research workflow."""
        question = "Comprehensive analysis of AI ethics"
        
        with patch.object(research_agent, '_execute_research_workflow') as mock_workflow:
            mock_workflow.return_value = {
                "result": "AI ethics involves several key considerations...",
                "mode": "deep",
                "sources": ["https://example.com/ethics1", "https://example.com/ethics2"],
                "rounds": 12
            }
            
            result = await research_agent.deep_research(question)
            
            assert result["mode"] == "deep"
            assert result["rounds"] == 12
            assert "result" in result
```

### 2. AgentHub Integration Tests (`test_agenthub_integration.py`)

```python
"""
End-to-end tests for AgentHub integration.
"""

import pytest
import json
import subprocess
import sys
from pathlib import Path


class TestAgentHubIntegration:
    """Tests for AgentHub integration."""
    
    @pytest.fixture
    def agent_script(self):
        """Path to agent.py script."""
        return Path(__file__).parent.parent.parent / "agent.py"
    
    def test_agent_script_exists(self, agent_script):
        """Test that agent.py script exists."""
        assert agent_script.exists()
    
    def test_agent_script_executable(self, agent_script):
        """Test that agent.py script is executable."""
        # Test with invalid arguments (should return error)
        result = subprocess.run(
            [sys.executable, str(agent_script)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "Invalid arguments" in result.stdout
    
    def test_instant_research_method(self, agent_script):
        """Test instant_research method via command line."""
        input_data = {
            "method": "instant_research",
            "parameters": {
                "question": "What is AI?"
            }
        }
        
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        response = json.loads(result.stdout)
        assert "result" in response
    
    def test_quick_research_method(self, agent_script):
        """Test quick_research method via command line."""
        input_data = {
            "method": "quick_research",
            "parameters": {
                "question": "How does machine learning work?"
            }
        }
        
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        response = json.loads(result.stdout)
        assert "result" in response
    
    def test_standard_research_method(self, agent_script):
        """Test standard_research method via command line."""
        input_data = {
            "method": "standard_research",
            "parameters": {
                "question": "What are the latest AI developments?"
            }
        }
        
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        response = json.loads(result.stdout)
        assert "result" in response
    
    def test_deep_research_method(self, agent_script):
        """Test deep_research method via command line."""
        input_data = {
            "method": "deep_research",
            "parameters": {
                "question": "Comprehensive analysis of AI ethics"
            }
        }
        
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        response = json.loads(result.stdout)
        assert "result" in response
    
    def test_solve_method(self, agent_script):
        """Test solve method via command line."""
        input_data = {
            "method": "solve",
            "parameters": {
                "question": "What is artificial intelligence?"
            }
        }
        
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        response = json.loads(result.stdout)
        assert "result" in response
    
    def test_invalid_method(self, agent_script):
        """Test invalid method handling."""
        input_data = {
            "method": "invalid_method",
            "parameters": {
                "question": "Test question"
            }
        }
        
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        
        response = json.loads(result.stdout)
        assert "error" in response
        assert "Unknown method" in response["error"]
```

## Test Configuration

### 1. Pytest Configuration (`conftest.py`)

```python
"""
Pytest configuration for research agent tests.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock


@pytest.fixture(scope="session")
def temp_dir():
    """Create temporary directory for test session."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after tests
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    service = Mock()
    service.generate = Mock(return_value="Test response")
    service.get_current_model = Mock(return_value="test-model")
    service.is_local_model = Mock(return_value=False)
    return service


@pytest.fixture
def sample_research_data():
    """Sample research data for testing."""
    return {
        "question": "What is artificial intelligence?",
        "mode": "instant",
        "sources": [
            {
                "title": "AI Overview",
                "content": "Artificial intelligence is...",
                "url": "https://example.com/ai",
                "source": "web"
            }
        ],
        "result": "AI is a field of computer science...",
        "rounds": 1
    }


@pytest.fixture
def mock_tool_context():
    """Mock tool context for testing."""
    return {
        "available_tools": ["web_search", "academic_search"],
        "tool_descriptions": {
            "web_search": "Search the web for information",
            "academic_search": "Search academic sources"
        },
        "tool_usage_examples": {
            "web_search": "web_search(query='AI research')",
            "academic_search": "academic_search(query='machine learning')"
        },
        "tool_parameters": {
            "web_search": {
                "query": {"type": "string", "required": True}
            },
            "academic_search": {
                "query": {"type": "string", "required": True}
            }
        }
    }


# Test markers
pytest_plugins = ["pytest_asyncio"]


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
```

### 2. Test Fixtures (`fixtures/sample_research_data.json`)

```json
{
  "instant_research": {
    "question": "What is artificial intelligence?",
    "expected_mode": "instant",
    "expected_rounds": 1,
    "expected_sources": 10,
    "expected_time_seconds": 30
  },
  "quick_research": {
    "question": "How does machine learning work?",
    "expected_mode": "quick",
    "expected_rounds": 2,
    "expected_sources": 20,
    "expected_time_seconds": 120
  },
  "standard_research": {
    "question": "What are the latest AI developments?",
    "expected_mode": "standard",
    "expected_rounds": 5,
    "expected_sources": 50,
    "expected_time_seconds": 900
  },
  "deep_research": {
    "question": "Comprehensive analysis of AI ethics",
    "expected_mode": "deep",
    "expected_rounds": 12,
    "expected_sources": 120,
    "expected_time_seconds": 1800
  }
}
```

## Test Execution

### 1. Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/ -m unit

# Run integration tests only
pytest tests/integration/ -m integration

# Run E2E tests only
pytest tests/e2e/ -m e2e

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_research_agent.py

# Run with verbose output
pytest -v

# Run with parallel execution
pytest -n auto
```

### 2. Continuous Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Key Features

### 1. **Comprehensive Test Coverage**
- Unit tests for all components
- Integration tests for component interactions
- End-to-end tests for complete workflows

### 2. **Test Organization**
- Clear separation of test types
- Reusable fixtures and mocks
- Consistent test structure

### 3. **Performance Testing**
- Load testing for research workflows
- Memory usage monitoring
- Response time validation

### 4. **Quality Assurance**
- Code coverage reporting
- Continuous integration
- Automated test execution

This testing strategy provides comprehensive coverage and ensures the reliability and maintainability of the Deep Research Agent implementation.
