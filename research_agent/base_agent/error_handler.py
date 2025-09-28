"""
ErrorHandler - Centralized error handling for BaseAgent.

This module provides comprehensive error handling capabilities including
error categorization, logging, and standardized error responses.
"""

import logging
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from ..utils.utils import format_response


class ErrorCategory(Enum):
    """Error categories for classification."""
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    TIMEOUT = "timeout"
    PERMISSION = "permission"
    RESOURCE = "resource"
    INTERNAL = "internal"
    EXTERNAL = "external"
    UNKNOWN = "unknown"


class ErrorHandler:
    """
    Centralized error handler for BaseAgent.
    
    Provides error categorization, logging, and standardized error responses.
    """
    
    def __init__(self, logger_name: str = "BaseAgent"):
        """
        Initialize ErrorHandler.
        
        Args:
            logger_name: Name for the logger
        """
        self.logger = logging.getLogger(logger_name)
        self.error_counts = {}
        self.error_history = []
    
    def categorize_error(self, error: Exception) -> ErrorCategory:
        """
        Categorize an error based on its type and message.
        
        Args:
            error: Exception to categorize
            
        Returns:
            Error category
        """
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Validation errors
        if any(keyword in error_message for keyword in ['validation', 'invalid', 'required', 'missing']):
            return ErrorCategory.VALIDATION
        
        # Configuration errors
        if any(keyword in error_message for keyword in ['config', 'setting', 'parameter']):
            return ErrorCategory.CONFIGURATION
        
        # Network errors
        if any(keyword in error_message for keyword in ['network', 'connection', 'timeout', 'unreachable']):
            return ErrorCategory.NETWORK
        
        # Permission errors
        if any(keyword in error_message for keyword in ['permission', 'unauthorized', 'forbidden', 'access denied']):
            return ErrorCategory.PERMISSION
        
        # Resource errors
        if any(keyword in error_message for keyword in ['resource', 'not found', 'unavailable', 'out of']):
            return ErrorCategory.RESOURCE
        
        # Timeout errors
        if 'timeout' in error_message or error_type in ['TimeoutError', 'asyncio.TimeoutError']:
            return ErrorCategory.TIMEOUT
        
        # External service errors
        if any(keyword in error_message for keyword in ['api', 'service', 'external', 'third-party']):
            return ErrorCategory.EXTERNAL
        
        # Internal errors (default for most exceptions)
        return ErrorCategory.INTERNAL
    
    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        level: int = logging.ERROR
    ) -> str:
        """
        Log an error with context and categorization.
        
        Args:
            error: Exception to log
            context: Additional context information
            level: Logging level
            
        Returns:
            Error ID for tracking
        """
        error_id = f"err_{int(datetime.utcnow().timestamp())}"
        category = self.categorize_error(error)
        
        # Update error counts
        category_key = category.value
        self.error_counts[category_key] = self.error_counts.get(category_key, 0) + 1
        
        # Create error record
        error_record = {
            'error_id': error_id,
            'timestamp': datetime.utcnow().isoformat(),
            'category': category.value,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        
        # Add to history (keep last 100 errors)
        self.error_history.append(error_record)
        if len(self.error_history) > 100:
            self.error_history.pop(0)
        
        # Log the error
        log_message = f"[{error_id}] {category.value.upper()}: {type(error).__name__}: {str(error)}"
        if context:
            log_message += f" | Context: {context}"
        
        self.logger.log(level, log_message)
        
        # Log traceback at DEBUG level
        self.logger.debug(f"[{error_id}] Traceback:\n{traceback.format_exc()}")
        
        return error_id
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle an error and return a standardized error response.
        
        Args:
            error: Exception to handle
            context: Additional context information
            user_message: User-friendly error message
            
        Returns:
            Standardized error response
        """
        error_id = self.log_error(error, context)
        category = self.categorize_error(error)
        
        # Generate user-friendly message if not provided
        if not user_message:
            user_message = self._generate_user_message(error, category)
        
        return format_response(
            success=False,
            message=user_message,
            metadata={
                'error_id': error_id,
                'error_category': category.value,
                'error_type': type(error).__name__,
                'context': context or {}
            }
        )
    
    def _generate_user_message(self, error: Exception, category: ErrorCategory) -> str:
        """
        Generate a user-friendly error message based on category.
        
        Args:
            error: Exception that occurred
            category: Error category
            
        Returns:
            User-friendly error message
        """
        base_messages = {
            ErrorCategory.VALIDATION: "Invalid input provided. Please check your request and try again.",
            ErrorCategory.CONFIGURATION: "Configuration error occurred. Please check your settings.",
            ErrorCategory.NETWORK: "Network error occurred. Please check your connection and try again.",
            ErrorCategory.TIMEOUT: "Request timed out. Please try again with a shorter request.",
            ErrorCategory.PERMISSION: "Permission denied. Please check your access rights.",
            ErrorCategory.RESOURCE: "Resource not available. Please try again later.",
            ErrorCategory.INTERNAL: "An internal error occurred. Please try again.",
            ErrorCategory.EXTERNAL: "External service error. Please try again later.",
            ErrorCategory.UNKNOWN: "An unexpected error occurred. Please try again."
        }
        
        return base_messages.get(category, base_messages[ErrorCategory.UNKNOWN])
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics and recent error history.
        
        Returns:
            Dictionary with error statistics
        """
        return {
            'error_counts': self.error_counts.copy(),
            'total_errors': sum(self.error_counts.values()),
            'recent_errors': self.error_history[-10:],  # Last 10 errors
            'categories': list(self.error_counts.keys())
        }
    
    def clear_error_history(self):
        """Clear error history and reset counts."""
        self.error_counts.clear()
        self.error_history.clear()
        self.logger.info("Error history cleared")
    
    def get_errors_by_category(self, category: ErrorCategory) -> List[Dict[str, Any]]:
        """
        Get all errors of a specific category.
        
        Args:
            category: Error category to filter by
            
        Returns:
            List of error records for the category
        """
        return [
            error for error in self.error_history
            if error['category'] == category.value
        ]
    
    def is_error_frequent(self, category: ErrorCategory, threshold: int = 5) -> bool:
        """
        Check if errors of a specific category are occurring frequently.
        
        Args:
            category: Error category to check
            threshold: Number of errors to consider frequent
            
        Returns:
            True if errors are frequent, False otherwise
        """
        return self.error_counts.get(category.value, 0) >= threshold
