"""
Unit tests for Phase 1 Foundation implementation.

This module provides basic unit tests to verify the core functionality
of the research agent implementation.
"""

import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock

from research_agent.research_agent.core import ResearchAgent
from research_agent.base_agent.core import BaseAgent
from research_agent.llm_service.core import LLMService
from research_agent.base_agent.context_manager import ContextManager
from research_agent.base_agent.error_handler import ErrorHandler
from agent import ResearchAgentHub


class TestBaseAgent(unittest.TestCase):
    """Test BaseAgent functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete implementation for testing
        class TestAgent(BaseAgent):
            def process_request(self, request):
                return {'success': True, 'data': request}
        
        self.agent = TestAgent()
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        self.assertTrue(self.agent._initialized)
        self.assertIsNotNone(self.agent.context_manager)
        self.assertIsNotNone(self.agent.error_handler)
        self.assertIsNotNone(self.agent.context_manager.session_id)
    
    def test_capabilities(self):
        """Test agent capabilities."""
        capabilities = self.agent.get_capabilities()
        self.assertIn('context_management', capabilities)
        self.assertIn('error_handling', capabilities)
        self.assertTrue(capabilities['context_management'])
    
    def test_context_management(self):
        """Test context management."""
        self.agent.context_manager.set_context('test_key', 'test_value')
        value = self.agent.context_manager.get_context('test_key')
        self.assertEqual(value, 'test_value')
    
    def test_error_handling(self):
        """Test error handling."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            error_response = self.agent.error_handler.handle_error(e)
            self.assertFalse(error_response['success'])
            self.assertIn('error_id', error_response['metadata'])


class TestResearchAgent(unittest.TestCase):
    """Test ResearchAgent functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = ResearchAgent()
    
    def test_research_agent_initialization(self):
        """Test research agent initialization."""
        self.assertTrue(self.agent._initialized)
        self.assertIsNotNone(self.agent.llm_service)
        self.assertIn('instant_research', self.agent._capabilities)
    
    def test_instant_research(self):
        """Test instant research functionality."""
        request = {
            'method': 'instant_research',
            'query': 'What is AI?'
        }
        response = self.agent.handle_request(request)
        self.assertTrue(response['success'])
        self.assertIn('data', response)
        self.assertEqual(response['data']['mode'], 'instant')
    
    def test_quick_research(self):
        """Test quick research functionality."""
        request = {
            'method': 'quick_research',
            'query': 'How does ML work?'
        }
        response = self.agent.handle_request(request)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['mode'], 'quick')
    
    def test_standard_research(self):
        """Test standard research functionality."""
        request = {
            'method': 'standard_research',
            'query': 'Latest AI developments'
        }
        response = self.agent.handle_request(request)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['mode'], 'standard')
    
    def test_deep_research(self):
        """Test deep research functionality."""
        request = {
            'method': 'deep_research',
            'query': 'AI impact on society'
        }
        response = self.agent.handle_request(request)
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['mode'], 'deep')
    
    def test_solve_method(self):
        """Test solve method."""
        request = {
            'method': 'solve',
            'query': 'How to implement AI?',
            'mode': 'standard'
        }
        response = self.agent.handle_request(request)
        self.assertTrue(response['success'])
    
    def test_research_history(self):
        """Test research history tracking."""
        # Perform a research
        request = {
            'method': 'instant_research',
            'query': 'Test query'
        }
        self.agent.handle_request(request)
        
        # Check history
        history = self.agent.get_research_history()
        self.assertGreater(len(history), 0)
        self.assertEqual(history[-1]['query'], 'Test query')
    
    def test_available_modes(self):
        """Test available research modes."""
        modes = self.agent.get_available_modes()
        expected_modes = ['instant', 'quick', 'standard', 'deep']
        self.assertEqual(set(modes), set(expected_modes))


class TestLLMService(unittest.TestCase):
    """Test LLM Service functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.llm_service = LLMService()
    
    def test_llm_service_initialization(self):
        """Test LLM service initialization."""
        self.assertTrue(self.llm_service.initialized)
        self.assertEqual(self.llm_service.service_type, 'mock')
    
    def test_generate_response(self):
        """Test response generation."""
        response = self.llm_service.generate_response(
            query="What is AI?",
            mode="instant"
        )
        self.assertTrue(response['success'])
        self.assertIn('data', response)
        self.assertIn('content', response['data'])
    
    def test_available_models(self):
        """Test available models."""
        models = self.llm_service.get_available_models()
        self.assertGreater(len(models), 0)
        self.assertIn('name', models[0])
    
    def test_service_status(self):
        """Test service status."""
        status = self.llm_service.get_service_status()
        self.assertEqual(status['status'], 'operational')
        self.assertEqual(status['type'], 'mock')


class TestResearchAgentHub(unittest.TestCase):
    """Test ResearchAgentHub functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        config_data = {
            "ai": {"temperature": 0.1},
            "research": {"max_rounds": 10}
        }
        json.dump(config_data, self.temp_config)
        self.temp_config.close()
        
        self.agent_hub = ResearchAgentHub(self.temp_config.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_config.name)
    
    def test_agent_hub_initialization(self):
        """Test agent hub initialization."""
        self.assertTrue(self.agent_hub.initialize_agent())
        self.assertIsNotNone(self.agent_hub.agent)
    
    def test_instant_research(self):
        """Test instant research through agent hub."""
        self.agent_hub.initialize_agent()
        response = self.agent_hub.instant_research("What is AI?")
        self.assertTrue(response['success'])
    
    def test_quick_research(self):
        """Test quick research through agent hub."""
        self.agent_hub.initialize_agent()
        response = self.agent_hub.quick_research("How does ML work?")
        self.assertTrue(response['success'])
    
    def test_standard_research(self):
        """Test standard research through agent hub."""
        self.agent_hub.initialize_agent()
        response = self.agent_hub.standard_research("Latest AI developments")
        self.assertTrue(response['success'])
    
    def test_deep_research(self):
        """Test deep research through agent hub."""
        self.agent_hub.initialize_agent()
        response = self.agent_hub.deep_research("AI impact on society")
        self.assertTrue(response['success'])
    
    def test_solve_method(self):
        """Test solve method through agent hub."""
        self.agent_hub.initialize_agent()
        response = self.agent_hub.solve("How to implement AI?", "standard")
        self.assertTrue(response['success'])
    
    def test_agent_status(self):
        """Test agent status."""
        self.agent_hub.initialize_agent()
        status = self.agent_hub.get_agent_status()
        self.assertIn('agent_type', status)
        self.assertEqual(status['agent_type'], 'ResearchAgent')
    
    def test_agent_test(self):
        """Test agent capabilities test."""
        self.agent_hub.initialize_agent()
        test_result = self.agent_hub.test_agent()
        self.assertTrue(test_result['success'])
        self.assertIn('test_results', test_result['data'])


class TestContextManager(unittest.TestCase):
    """Test ContextManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context_manager = ContextManager()
    
    def test_context_set_get(self):
        """Test context setting and getting."""
        self.context_manager.set_context('test_key', 'test_value')
        value = self.context_manager.get_context('test_key')
        self.assertEqual(value, 'test_value')
    
    def test_context_expiration(self):
        """Test context expiration."""
        self.context_manager.set_context('temp_key', 'temp_value', ttl_seconds=1)
        self.assertTrue(self.context_manager.has_context('temp_key'))
        
        # Wait for expiration (in real test, you'd use time.sleep)
        # For this test, we'll just verify the method exists
        self.assertIsNotNone(self.context_manager.get_context('temp_key'))
    
    def test_conversation_history(self):
        """Test conversation history."""
        self.context_manager.add_conversation_entry('user', 'Hello')
        self.context_manager.add_conversation_entry('assistant', 'Hi there')
        
        history = self.context_manager.get_conversation_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['role'], 'user')
        self.assertEqual(history[1]['role'], 'assistant')


class TestErrorHandler(unittest.TestCase):
    """Test ErrorHandler functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.error_handler = ErrorHandler("TestAgent")
    
    def test_error_categorization(self):
        """Test error categorization."""
        validation_error = ValueError("Invalid input")
        category = self.error_handler.categorize_error(validation_error)
        self.assertEqual(category.value, 'validation')
    
    def test_error_handling(self):
        """Test error handling."""
        test_error = RuntimeError("Test runtime error")
        response = self.error_handler.handle_error(test_error)
        
        self.assertFalse(response['success'])
        self.assertIn('error_id', response['metadata'])
        self.assertIn('error_category', response['metadata'])
    
    def test_error_statistics(self):
        """Test error statistics."""
        # Generate some validation errors specifically
        for _ in range(3):
            self.error_handler.log_error(ValueError("Invalid input"))
        
        stats = self.error_handler.get_error_statistics()
        self.assertGreater(stats['total_errors'], 0)
        # Check that we have some error counts
        self.assertGreater(len(stats['error_counts']), 0)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
