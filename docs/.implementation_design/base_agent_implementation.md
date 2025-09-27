# BaseAgent Module Implementation Design

## Overview

The BaseAgent module provides common agent capabilities that can be shared across all agent types. It serves as the foundation for specialized agents like ResearchAgent, ensuring consistent behavior and reducing code duplication.

## Module Structure

```
src/base_agent/
├── __init__.py                 # Module initialization and exports
├── core.py                     # BaseAgent class implementation
├── context_manager.py          # Context management and state handling
├── error_handler.py            # Error handling and logging
└── utils.py                    # Common utility functions
```

## Core Implementation

### 1. BaseAgent Class (`core.py`)

```python
"""
BaseAgent - Common agent capabilities for all agent types.

This module provides the foundational agent class that all specialized
agents inherit from, ensuring consistent behavior and shared functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
import asyncio
import logging
import uuid
from datetime import datetime
import json

from .context_manager import ContextManager
from .error_handler import ErrorHandler
from .utils import validate_input_data, format_response


class BaseAgent(ABC):
    """
    Base agent class with common capabilities shared across all agents.
    
    This abstract base class provides:
    - LLM service integration
    - Error handling and logging
    - Context management
    - Input validation
    - Universal solve() method interface
    - Tool management
    """
    
    def __init__(
        self, 
        llm_service: Any, 
        external_tools: Optional[List[Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            llm_service: LLM service instance for AI operations
            external_tools: List of external tools available to the agent
            config: Optional configuration dictionary
        """
        self.llm_service = llm_service
        self.external_tools = external_tools or []
        self.config = config or {}
        
        # Initialize core components
        self.context_manager = ContextManager()
        self.error_handler = ErrorHandler()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Agent metadata
        self.agent_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.session_id = None
        
        # Initialize agent
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize agent-specific setup."""
        self.logger.info(f"Initializing {self.__class__.__name__} with ID: {self.agent_id}")
        
        # Set up logging
        self._setup_logging()
        
        # Initialize tools
        self._initialize_tools()
        
        # Load configuration
        self._load_configuration()
    
    def _setup_logging(self):
        """Set up logging configuration."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _initialize_tools(self):
        """Initialize external tools."""
        for tool in self.external_tools:
            if hasattr(tool, 'initialize'):
                try:
                    tool.initialize()
                    self.logger.info(f"Initialized tool: {tool.get_name()}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize tool {tool.get_name()}: {e}")
    
    def _load_configuration(self):
        """Load agent configuration."""
        # Load from config parameter or default configuration
        self.config = {
            'timeout': 30,
            'max_retries': 3,
            'log_level': 'INFO',
            **self.config
        }
    
    @abstractmethod
    async def solve(self, question: str) -> Dict[str, Any]:
        """
        Universal solve method - to be implemented by subclasses.
        
        This is the main entry point for agent execution. Each specialized
        agent must implement this method according to its specific functionality.
        
        Args:
            question: The question or task to solve
            
        Returns:
            Dictionary containing the solution and metadata
        """
        pass
    
    async def get_available_tools(self) -> List[Dict[str, str]]:
        """
        Get list of available tools with their metadata.
        
        Returns:
            List of dictionaries containing tool information
        """
        tools = []
        for tool in self.external_tools:
            tools.append({
                'name': tool.get_name(),
                'description': tool.get_description(),
                'type': getattr(tool, 'tool_type', 'unknown')
            })
        return tools
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data according to agent requirements.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            return validate_input_data(input_data, self._get_input_schema())
        except Exception as e:
            self.logger.error(f"Input validation error: {e}")
            return False
    
    def _get_input_schema(self) -> Dict[str, Any]:
        """
        Get input validation schema for this agent.
        
        Returns:
            JSON schema for input validation
        """
        return {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 1000
                }
            },
            "required": ["question"]
        }
    
    async def handle_error(self, error: Exception, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Handle errors with appropriate logging and user-friendly responses.
        
        Args:
            error: The exception that occurred
            context: Optional context information
            
        Returns:
            Dictionary containing error information
        """
        error_id = str(uuid.uuid4())
        
        # Log the error
        self.error_handler.log_error(error, context, error_id)
        
        # Return user-friendly error response
        return {
            'error': True,
            'error_id': error_id,
            'message': self._get_user_friendly_error_message(error),
            'timestamp': datetime.utcnow().isoformat(),
            'agent_id': self.agent_id
        }
    
    def _get_user_friendly_error_message(self, error: Exception) -> str:
        """
        Convert technical error messages to user-friendly ones.
        
        Args:
            error: The exception that occurred
            
        Returns:
            User-friendly error message
        """
        error_messages = {
            'ConnectionError': 'Unable to connect to external services. Please try again later.',
            'TimeoutError': 'The request timed out. Please try again with a simpler question.',
            'ValidationError': 'Invalid input provided. Please check your request.',
            'RateLimitError': 'Too many requests. Please wait a moment before trying again.'
        }
        
        error_type = type(error).__name__
        return error_messages.get(error_type, 'An unexpected error occurred. Please try again.')
    
    async def execute_with_retry(
        self, 
        operation: callable, 
        max_retries: int = None,
        delay: float = 1.0
    ) -> Any:
        """
        Execute an operation with retry logic.
        
        Args:
            operation: The operation to execute
            max_retries: Maximum number of retries (uses config default if None)
            delay: Delay between retries in seconds
            
        Returns:
            Result of the operation
        """
        max_retries = max_retries or self.config.get('max_retries', 3)
        
        for attempt in range(max_retries + 1):
            try:
                return await operation()
            except Exception as e:
                if attempt == max_retries:
                    raise e
                
                self.logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about this agent instance.
        
        Returns:
            Dictionary containing agent metadata
        """
        return {
            'agent_id': self.agent_id,
            'agent_type': self.__class__.__name__,
            'created_at': self.created_at.isoformat(),
            'session_id': self.session_id,
            'available_tools': len(self.external_tools),
            'config': self.config
        }
    
    def set_session_id(self, session_id: str):
        """Set the current session ID."""
        self.session_id = session_id
        self.context_manager.set_context('session_id', session_id)
    
    async def cleanup(self):
        """Clean up agent resources."""
        self.logger.info(f"Cleaning up agent {self.agent_id}")
        
        # Clean up tools
        for tool in self.external_tools:
            if hasattr(tool, 'cleanup'):
                try:
                    await tool.cleanup()
                except Exception as e:
                    self.logger.error(f"Error cleaning up tool {tool.get_name()}: {e}")
        
        # Clear context
        self.context_manager.clear_context()
        
        self.logger.info(f"Agent {self.agent_id} cleanup completed")
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(id={self.agent_id})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return f"{self.__class__.__name__}(id={self.agent_id}, tools={len(self.external_tools)})"
```

### 2. Context Manager (`context_manager.py`)

```python
"""
Context Manager - Manages agent context and state.

This module provides context management capabilities for agents,
including session state, conversation history, and metadata storage.
"""

from typing import Dict, Any, Optional, List
import json
import threading
from datetime import datetime
from collections import defaultdict


class ContextManager:
    """
    Manages agent context and state across interactions.
    
    Provides thread-safe context management with support for:
    - Session state
    - Conversation history
    - Metadata storage
    - Context persistence
    """
    
    def __init__(self):
        """Initialize the context manager."""
        self._context = {}
        self._conversation_history = []
        self._metadata = defaultdict(dict)
        self._lock = threading.RLock()
        self._session_id = None
        self._created_at = datetime.utcnow()
    
    def set_context(self, key: str, value: Any, persistent: bool = False):
        """
        Set a context value.
        
        Args:
            key: Context key
            value: Context value
            persistent: Whether to persist across sessions
        """
        with self._lock:
            self._context[key] = {
                'value': value,
                'timestamp': datetime.utcnow(),
                'persistent': persistent
            }
    
    def get_context(self, key: str = None, default: Any = None) -> Any:
        """
        Get a context value.
        
        Args:
            key: Context key (if None, returns all context)
            default: Default value if key not found
            
        Returns:
            Context value or all context if key is None
        """
        with self._lock:
            if key is None:
                return dict(self._context)
            
            context_item = self._context.get(key)
            if context_item is None:
                return default
            
            return context_item['value']
    
    def has_context(self, key: str) -> bool:
        """
        Check if a context key exists.
        
        Args:
            key: Context key to check
            
        Returns:
            True if key exists, False otherwise
        """
        with self._lock:
            return key in self._context
    
    def remove_context(self, key: str):
        """
        Remove a context key.
        
        Args:
            key: Context key to remove
        """
        with self._lock:
            self._context.pop(key, None)
    
    def clear_context(self, persistent_only: bool = False):
        """
        Clear context data.
        
        Args:
            persistent_only: If True, only clear non-persistent context
        """
        with self._lock:
            if persistent_only:
                # Remove only non-persistent context
                keys_to_remove = [
                    key for key, item in self._context.items()
                    if not item.get('persistent', False)
                ]
                for key in keys_to_remove:
                    del self._context[key]
            else:
                # Clear all context
                self._context.clear()
    
    def add_to_conversation(self, role: str, content: str, metadata: Dict = None):
        """
        Add an entry to conversation history.
        
        Args:
            role: Role of the speaker (user, agent, system)
            content: Content of the message
            metadata: Optional metadata
        """
        with self._lock:
            self._conversation_history.append({
                'role': role,
                'content': content,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow()
            })
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of conversation entries
        """
        with self._lock:
            if limit is None:
                return list(self._conversation_history)
            return list(self._conversation_history[-limit:])
    
    def clear_conversation_history(self):
        """Clear conversation history."""
        with self._lock:
            self._conversation_history.clear()
    
    def set_metadata(self, category: str, key: str, value: Any):
        """
        Set metadata for a category.
        
        Args:
            category: Metadata category
            key: Metadata key
            value: Metadata value
        """
        with self._lock:
            self._metadata[category][key] = value
    
    def get_metadata(self, category: str, key: str = None, default: Any = None) -> Any:
        """
        Get metadata for a category.
        
        Args:
            category: Metadata category
            key: Metadata key (if None, returns all metadata for category)
            default: Default value if key not found
            
        Returns:
            Metadata value or all metadata for category
        """
        with self._lock:
            if key is None:
                return dict(self._metadata[category])
            return self._metadata[category].get(key, default)
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get session information.
        
        Returns:
            Dictionary containing session information
        """
        with self._lock:
            return {
                'session_id': self._session_id,
                'created_at': self._created_at.isoformat(),
                'context_keys': list(self._context.keys()),
                'conversation_length': len(self._conversation_history),
                'metadata_categories': list(self._metadata.keys())
            }
    
    def export_context(self) -> Dict[str, Any]:
        """
        Export context data for persistence.
        
        Returns:
            Dictionary containing exportable context data
        """
        with self._lock:
            return {
                'context': dict(self._context),
                'conversation_history': list(self._conversation_history),
                'metadata': dict(self._metadata),
                'session_id': self._session_id,
                'created_at': self._created_at.isoformat()
            }
    
    def import_context(self, data: Dict[str, Any]):
        """
        Import context data from persistence.
        
        Args:
            data: Context data to import
        """
        with self._lock:
            self._context = data.get('context', {})
            self._conversation_history = data.get('conversation_history', [])
            self._metadata = defaultdict(dict, data.get('metadata', {}))
            self._session_id = data.get('session_id')
            self._created_at = datetime.fromisoformat(data.get('created_at', datetime.utcnow().isoformat()))
```

### 3. Error Handler (`error_handler.py`)

```python
"""
Error Handler - Centralized error handling and logging.

This module provides comprehensive error handling capabilities for agents,
including error logging, categorization, and user-friendly error responses.
"""

import logging
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import json


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""
    VALIDATION = "validation"
    NETWORK = "network"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    RESOURCE = "resource"
    CONFIGURATION = "configuration"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL = "internal"
    UNKNOWN = "unknown"


class ErrorHandler:
    """
    Centralized error handling and logging for agents.
    
    Provides comprehensive error handling including:
    - Error logging with context
    - Error categorization and severity assessment
    - User-friendly error message generation
    - Error tracking and metrics
    """
    
    def __init__(self, log_level: str = "INFO"):
        """
        Initialize the error handler.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Error tracking
        self._error_count = 0
        self._error_categories = {}
        self._recent_errors = []
        self._max_recent_errors = 100
    
    async def handle_error(
        self, 
        error: Exception, 
        context: Optional[Dict] = None,
        error_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle an error with comprehensive logging and categorization.
        
        Args:
            error: The exception that occurred
            context: Optional context information
            error_id: Optional error ID for tracking
            
        Returns:
            Dictionary containing error information
        """
        if error_id is None:
            error_id = f"err_{int(datetime.utcnow().timestamp())}"
        
        # Categorize the error
        category = self._categorize_error(error)
        severity = self._assess_severity(error, category)
        
        # Log the error
        self.log_error(error, context, error_id, category, severity)
        
        # Track the error
        self._track_error(error_id, category, severity)
        
        # Generate user-friendly response
        user_message = self._generate_user_message(error, category, severity)
        
        return {
            'error': True,
            'error_id': error_id,
            'category': category.value,
            'severity': severity.value,
            'message': user_message,
            'timestamp': datetime.utcnow().isoformat(),
            'context': context or {}
        }
    
    def log_error(
        self, 
        error: Exception, 
        context: Optional[Dict] = None,
        error_id: Optional[str] = None,
        category: Optional[ErrorCategory] = None,
        severity: Optional[ErrorSeverity] = None
    ):
        """
        Log an error with detailed information.
        
        Args:
            error: The exception that occurred
            context: Optional context information
            error_id: Optional error ID for tracking
            category: Error category
            severity: Error severity
        """
        if category is None:
            category = self._categorize_error(error)
        if severity is None:
            severity = self._assess_severity(error, category)
        
        # Prepare log data
        log_data = {
            'error_id': error_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'category': category.value,
            'severity': severity.value,
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat(),
            'traceback': traceback.format_exc()
        }
        
        # Log based on severity
        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"Critical error: {json.dumps(log_data)}")
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(f"High severity error: {json.dumps(log_data)}")
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"Medium severity error: {json.dumps(log_data)}")
        else:
            self.logger.info(f"Low severity error: {json.dumps(log_data)}")
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """
        Categorize an error based on its type and message.
        
        Args:
            error: The exception to categorize
            
        Returns:
            Error category
        """
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Network-related errors
        if any(keyword in error_type.lower() for keyword in ['connection', 'network', 'timeout']):
            return ErrorCategory.NETWORK
        
        # Timeout errors
        if 'timeout' in error_message or 'timeout' in error_type.lower():
            return ErrorCategory.TIMEOUT
        
        # Authentication errors
        if any(keyword in error_message for keyword in ['auth', 'unauthorized', 'forbidden']):
            return ErrorCategory.AUTHENTICATION
        
        # Rate limiting errors
        if any(keyword in error_message for keyword in ['rate', 'limit', 'quota']):
            return ErrorCategory.RATE_LIMIT
        
        # Validation errors
        if any(keyword in error_type.lower() for keyword in ['validation', 'value', 'invalid']):
            return ErrorCategory.VALIDATION
        
        # Resource errors
        if any(keyword in error_message for keyword in ['resource', 'memory', 'disk']):
            return ErrorCategory.RESOURCE
        
        # Configuration errors
        if any(keyword in error_message for keyword in ['config', 'setting', 'parameter']):
            return ErrorCategory.CONFIGURATION
        
        # External service errors
        if any(keyword in error_message for keyword in ['api', 'service', 'external']):
            return ErrorCategory.EXTERNAL_SERVICE
        
        return ErrorCategory.UNKNOWN
    
    def _assess_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """
        Assess the severity of an error.
        
        Args:
            error: The exception to assess
            category: Error category
            
        Returns:
            Error severity
        """
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Critical errors
        if any(keyword in error_message for keyword in ['critical', 'fatal', 'system']):
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if category in [ErrorCategory.AUTHENTICATION, ErrorCategory.CONFIGURATION]:
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if category in [ErrorCategory.NETWORK, ErrorCategory.EXTERNAL_SERVICE, ErrorCategory.RATE_LIMIT]:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors
        if category in [ErrorCategory.VALIDATION, ErrorCategory.TIMEOUT]:
            return ErrorSeverity.LOW
        
        return ErrorSeverity.MEDIUM
    
    def _generate_user_message(self, error: Exception, category: ErrorCategory, severity: ErrorSeverity) -> str:
        """
        Generate a user-friendly error message.
        
        Args:
            error: The exception that occurred
            category: Error category
            severity: Error severity
            
        Returns:
            User-friendly error message
        """
        # Base messages by category
        category_messages = {
            ErrorCategory.VALIDATION: "There was an issue with your request. Please check your input and try again.",
            ErrorCategory.NETWORK: "Unable to connect to external services. Please check your internet connection and try again.",
            ErrorCategory.TIMEOUT: "The request timed out. Please try again with a simpler question.",
            ErrorCategory.AUTHENTICATION: "Authentication failed. Please check your credentials and try again.",
            ErrorCategory.RATE_LIMIT: "Too many requests. Please wait a moment before trying again.",
            ErrorCategory.RESOURCE: "Insufficient resources available. Please try again later.",
            ErrorCategory.CONFIGURATION: "Configuration error. Please contact support.",
            ErrorCategory.EXTERNAL_SERVICE: "External service unavailable. Please try again later.",
            ErrorCategory.INTERNAL: "An internal error occurred. Please try again.",
            ErrorCategory.UNKNOWN: "An unexpected error occurred. Please try again."
        }
        
        base_message = category_messages.get(category, category_messages[ErrorCategory.UNKNOWN])
        
        # Add severity-specific information
        if severity == ErrorSeverity.CRITICAL:
            return f"Critical Error: {base_message}"
        elif severity == ErrorSeverity.HIGH:
            return f"Error: {base_message}"
        else:
            return base_message
    
    def _track_error(self, error_id: str, category: ErrorCategory, severity: ErrorSeverity):
        """
        Track error for metrics and monitoring.
        
        Args:
            error_id: Error ID
            category: Error category
            severity: Error severity
        """
        self._error_count += 1
        
        # Track by category
        if category not in self._error_categories:
            self._error_categories[category] = 0
        self._error_categories[category] += 1
        
        # Track recent errors
        self._recent_errors.append({
            'error_id': error_id,
            'category': category.value,
            'severity': severity.value,
            'timestamp': datetime.utcnow()
        })
        
        # Keep only recent errors
        if len(self._recent_errors) > self._max_recent_errors:
            self._recent_errors = self._recent_errors[-self._max_recent_errors:]
    
    def get_error_metrics(self) -> Dict[str, Any]:
        """
        Get error metrics and statistics.
        
        Returns:
            Dictionary containing error metrics
        """
        return {
            'total_errors': self._error_count,
            'errors_by_category': {cat.value: count for cat, count in self._error_categories.items()},
            'recent_errors': self._recent_errors[-10:],  # Last 10 errors
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def clear_metrics(self):
        """Clear error metrics and tracking data."""
        self._error_count = 0
        self._error_categories.clear()
        self._recent_errors.clear()
```

### 4. Utils Module (`utils.py`)

```python
"""
Utils - Common utility functions for BaseAgent.

This module provides utility functions used across the BaseAgent module,
including input validation, response formatting, and helper functions.
"""

import json
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid


def validate_input_data(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Validate input data against a JSON schema.
    
    Args:
        data: Input data to validate
        schema: JSON schema for validation
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Basic validation - can be enhanced with jsonschema library
        if not isinstance(data, dict):
            return False
        
        # Check required fields
        required_fields = schema.get('properties', {}).keys()
        for field in schema.get('required', []):
            if field not in data:
                return False
        
        # Validate field types
        for field, value in data.items():
            if field in schema.get('properties', {}):
                field_schema = schema['properties'][field]
                if not _validate_field_type(value, field_schema):
                    return False
        
        return True
    except Exception:
        return False


def _validate_field_type(value: Any, field_schema: Dict[str, Any]) -> bool:
    """
    Validate a field value against its schema.
    
    Args:
        value: Value to validate
        field_schema: Schema for the field
        
    Returns:
        True if valid, False otherwise
    """
    expected_type = field_schema.get('type')
    
    if expected_type == 'string':
        if not isinstance(value, str):
            return False
        
        # Check string constraints
        if 'minLength' in field_schema and len(value) < field_schema['minLength']:
            return False
        if 'maxLength' in field_schema and len(value) > field_schema['maxLength']:
            return False
        
        # Check pattern if specified
        if 'pattern' in field_schema:
            if not re.match(field_schema['pattern'], value):
                return False
    
    elif expected_type == 'integer':
        if not isinstance(value, int):
            return False
        
        # Check integer constraints
        if 'minimum' in field_schema and value < field_schema['minimum']:
            return False
        if 'maximum' in field_schema and value > field_schema['maximum']:
            return False
    
    elif expected_type == 'boolean':
        if not isinstance(value, bool):
            return False
    
    elif expected_type == 'array':
        if not isinstance(value, list):
            return False
        
        # Check array constraints
        if 'minItems' in field_schema and len(value) < field_schema['minItems']:
            return False
        if 'maxItems' in field_schema and len(value) > field_schema['maxItems']:
            return False
    
    elif expected_type == 'object':
        if not isinstance(value, dict):
            return False
    
    return True


def format_response(
    success: bool,
    data: Any = None,
    message: str = None,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Format a standardized response.
    
    Args:
        success: Whether the operation was successful
        data: Response data
        message: Response message
        metadata: Additional metadata
        
    Returns:
        Formatted response dictionary
    """
    response = {
        'success': success,
        'timestamp': datetime.utcnow().isoformat(),
        'response_id': str(uuid.uuid4())
    }
    
    if data is not None:
        response['data'] = data
    
    if message is not None:
        response['message'] = message
    
    if metadata is not None:
        response['metadata'] = metadata
    
    return response


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """
    Sanitize a string for safe processing.
    
    Args:
        text: Text to sanitize
        max_length: Maximum length of the result
        
    Returns:
        Sanitized string
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length-3] + '...'
    
    return text.strip()


def generate_session_id() -> str:
    """
    Generate a unique session ID.
    
    Returns:
        Unique session ID string
    """
    return f"session_{int(datetime.utcnow().timestamp())}_{str(uuid.uuid4())[:8]}"


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """
    Safely parse JSON string with fallback.
    
    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """
    Safely serialize data to JSON string with fallback.
    
    Args:
        data: Data to serialize
        default: Default string if serialization fails
        
    Returns:
        JSON string or default string
    """
    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError):
        return default


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries, with later ones taking precedence.
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def extract_key_value_pairs(text: str, pattern: str = r'(\w+):\s*([^\n]+)') -> Dict[str, str]:
    """
    Extract key-value pairs from text using regex pattern.
    
    Args:
        text: Text to extract from
        pattern: Regex pattern for key-value pairs
        
    Returns:
        Dictionary of extracted key-value pairs
    """
    matches = re.findall(pattern, text)
    return {key.strip(): value.strip() for key, value in matches}


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.
    
    Args:
        url: String to check
        
    Returns:
        True if valid URL, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    return text.strip()
```

## Module Initialization (`__init__.py`)

```python
"""
BaseAgent Module - Common agent capabilities.

This module provides the foundational agent class and utilities
that all specialized agents inherit from.
"""

from .core import BaseAgent
from .context_manager import ContextManager
from .error_handler import ErrorHandler, ErrorSeverity, ErrorCategory
from .utils import (
    validate_input_data,
    format_response,
    sanitize_string,
    generate_session_id,
    safe_json_loads,
    safe_json_dumps
)

__version__ = "1.0.0"
__author__ = "agentplug"

__all__ = [
    "BaseAgent",
    "ContextManager", 
    "ErrorHandler",
    "ErrorSeverity",
    "ErrorCategory",
    "validate_input_data",
    "format_response",
    "sanitize_string",
    "generate_session_id",
    "safe_json_loads",
    "safe_json_dumps"
]
```

## Testing Strategy

### Unit Tests
- Test BaseAgent initialization and configuration
- Test context management operations
- Test error handling and categorization
- Test utility functions
- Test input validation

### Integration Tests
- Test BaseAgent with mock LLM service
- Test error handling with real exceptions
- Test context persistence and restoration
- Test tool integration

### Performance Tests
- Test context manager with large datasets
- Test error handler with high error rates
- Test memory usage and cleanup

This BaseAgent implementation provides a solid foundation for all agent types with comprehensive error handling, context management, and utility functions.
