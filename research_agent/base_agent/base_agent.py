"""
BaseAgent - Core agent class with common capabilities.

This module provides the BaseAgent class that serves as the foundation
for all agent implementations, including common capabilities and interfaces.
"""

import json
import logging
import socket
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

from ..utils.utils import (
    format_response,
    merge_dicts,
    safe_json_dumps,
    safe_json_loads,
    sanitize_string,
    validate_input_data,
)
from .context_manager import ContextManager, ContextType
from .error_handler import ErrorCategory, ErrorHandler


class BaseAgent(ABC):
    """
    Base agent class with common capabilities.

    Provides foundation functionality including context management,
    error handling, configuration, and standardized interfaces.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        logger_name: Optional[str] = None,
        tool_context: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize BaseAgent.

        Args:
            config: Configuration dictionary
            session_id: Optional session identifier
            logger_name: Optional logger name
            tool_context: Dictionary containing tool metadata and context information
        """
        self.config = config or {}
        self.session_id = session_id
        self.logger_name = logger_name or self.__class__.__name__

        # Tool integration
        self.tool_context = tool_context or {}
        self.available_tools = self.tool_context.get("available_tools", [])
        self.tool_descriptions = self.tool_context.get("tool_descriptions", {})
        self.tool_usage_examples = self.tool_context.get("tool_usage_examples", {})
        self.tool_parameters = self.tool_context.get("tool_parameters", {})
        self.tool_return_types = self.tool_context.get("tool_return_types", {})
        self.tool_namespaces = self.tool_context.get("tool_namespaces", {})

        # Initialize core components
        self.context_manager = ContextManager(session_id)
        self.error_handler = ErrorHandler(self.logger_name)
        self.logger = logging.getLogger(self.logger_name)

        # Initialize agent state
        self._initialized = False
        self._capabilities: Dict[str, Any] = {}
        self._tools: Dict[str, Any] = {}

        # Initialize agent
        self._initialize()

    def _initialize(self) -> None:
        """Initialize the agent with configuration and capabilities."""
        try:
            # Load configuration
            self._load_config()

            # Initialize capabilities
            self._initialize_capabilities()

            # Initialize tools
            self._initialize_tools()

            # Mark as initialized
            self._initialized = True

            self.logger.info(
                f"Agent {self.__class__.__name__} initialized successfully"
            )

        except Exception as e:
            self.error_handler.log_error(e, {"component": "initialization"})
            raise

    def _load_config(self) -> None:
        """Load and validate configuration."""
        # Set default configuration
        default_config = {
            "ai": {"temperature": 0.1, "max_tokens": None, "timeout": 30},
            "research": {
                "max_sources_per_round": 10,
                "max_rounds": 12,
                "timeout_per_round": 300,
            },
        }

        # Merge with provided config
        self.config = merge_dicts(default_config, self.config)

        # Store in context
        self.context_manager.set_context(
            "agent_config", self.config, ContextType.SESSION
        )

    def _initialize_capabilities(self) -> None:
        """Initialize agent capabilities."""
        self._capabilities = {
            "context_management": True,
            "error_handling": True,
            "configuration": True,
            "logging": True,
            "session_management": True,
        }

        # Store capabilities in context
        self.context_manager.set_context(
            "agent_capabilities", self._capabilities, ContextType.SESSION
        )

    def _initialize_tools(self) -> None:
        """Initialize available tools."""
        self._tools = {
            "get_context": self._tool_get_context,
            "set_context": self._tool_set_context,
            "clear_context": self._tool_clear_context,
            "get_metadata": self._tool_get_metadata,
            "set_metadata": self._tool_set_metadata,
        }

    def validate_request(self, request: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        Validate a request against a schema.

        Args:
            request: Request to validate
            schema: Validation schema

        Returns:
            True if valid, False otherwise
        """
        try:
            return validate_input_data(request, schema)
        except Exception as e:
            self.error_handler.log_error(e, {"component": "validation"})
            return False

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a request with error handling and logging.

        Args:
            request: Request dictionary

        Returns:
            Response dictionary
        """
        try:
            # Log request
            self.logger.info(f"Processing request: {request.get('method', 'unknown')}")

            # Add to conversation history
            self.context_manager.add_conversation_entry(
                "user", safe_json_dumps(request), {"request_type": "agent_request"}
            )

            # Process the request
            response = self.process_request(request)

            # Add response to conversation history
            self.context_manager.add_conversation_entry(
                "assistant",
                safe_json_dumps(response),
                {"response_type": "agent_response"},
            )

            return response

        except Exception as e:
            error_response = self.error_handler.handle_error(
                e, {"request": request}, f"Error processing request: {str(e)}"
            )

            # Add error to conversation history
            self.context_manager.add_conversation_entry(
                "system",
                safe_json_dumps(error_response),
                {"response_type": "error_response"},
            )

            return error_response

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities.

        Returns:
            Dictionary of capabilities
        """
        return self._capabilities.copy()

    def get_tools(self) -> Dict[str, Callable]:
        """
        Get available tools.

        Returns:
            Dictionary of tool functions
        """
        return self._tools.copy()

    def get_session_info(self) -> Dict[str, Any]:
        """
        Get session information.

        Returns:
            Session information dictionary
        """
        return {
            "session_id": self.session_id,
            "agent_type": self.__class__.__name__,
            "initialized": self._initialized,
            "capabilities": self._capabilities,
            "context_summary": self.context_manager.get_context_summary(),
            "error_statistics": self.error_handler.get_error_statistics(),
        }

    def reset_session(self) -> Dict[str, Any]:
        """
        Reset the session state.

        Returns:
            Reset confirmation response
        """
        try:
            # Clear context
            cleared_count = self.context_manager.clear_context()

            # Clear error history
            self.error_handler.clear_error_history()

            # Generate new session ID
            old_session_id = self.session_id
            self.session_id = self.context_manager.session_id

            self.logger.info(f"Session reset: {old_session_id} -> {self.session_id}")

            return format_response(
                success=True,
                message="Session reset successfully",
                data={
                    "old_session_id": old_session_id,
                    "new_session_id": self.session_id,
                    "cleared_context_entries": cleared_count,
                },
            )

        except Exception as e:
            return self.error_handler.handle_error(
                e, {"component": "session_reset"}, "Error resetting session"
            )

    # Tool implementations
    def _tool_get_context(
        self, key: str, context_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Tool: Get context value."""
        try:
            ctx_type = ContextType(context_type) if context_type else None
            value = self.context_manager.get_context(key, context_type=ctx_type)

            return format_response(
                success=True,
                data={"key": key, "value": value, "context_type": context_type},
            )
        except Exception as e:
            return self.error_handler.handle_error(e, {"tool": "get_context"})

    def _tool_set_context(
        self,
        key: str,
        value: Any,
        context_type: str = "session",
        ttl_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Tool: Set context value."""
        try:
            ctx_type = ContextType(context_type)
            self.context_manager.set_context(key, value, ctx_type, ttl_seconds)

            return format_response(
                success=True,
                message=f"Context '{key}' set successfully",
                data={"key": key, "context_type": context_type},
            )
        except Exception as e:
            return self.error_handler.handle_error(e, {"tool": "set_context"})

    def _tool_clear_context(self, context_type: Optional[str] = None) -> Dict[str, Any]:
        """Tool: Clear context."""
        try:
            ctx_type = ContextType(context_type) if context_type else None
            cleared_count = self.context_manager.clear_context(ctx_type)

            return format_response(
                success=True,
                message=f"Cleared {cleared_count} context entries",
                data={"cleared_count": cleared_count, "context_type": context_type},
            )
        except Exception as e:
            return self.error_handler.handle_error(e, {"tool": "clear_context"})

    def _tool_get_metadata(self, key: str) -> Dict[str, Any]:
        """Tool: Get metadata value."""
        try:
            value = self.context_manager.get_metadata(key)

            return format_response(success=True, data={"key": key, "value": value})
        except Exception as e:
            return self.error_handler.handle_error(e, {"tool": "get_metadata"})

    def _tool_set_metadata(self, key: str, value: Any) -> Dict[str, Any]:
        """Tool: Set metadata value."""
        try:
            self.context_manager.set_metadata(key, value)

            return format_response(
                success=True,
                message=f"Metadata '{key}' set successfully",
                data={"key": key},
            )
        except Exception as e:
            return self.error_handler.handle_error(e, {"tool": "set_metadata"})

    def validate_tool_context(self) -> bool:
        """
        Validate tool context structure.

        Returns:
            True if tool context is valid, False otherwise
        """
        if not isinstance(self.tool_context, dict):
            return False

        # Check required fields
        required_fields = ["available_tools", "tool_descriptions"]
        for field in required_fields:
            if field not in self.tool_context:
                return False

        # Check if available_tools is a list
        if not isinstance(self.tool_context["available_tools"], list):
            return False

        # Check if tool_descriptions is a dict
        if not isinstance(self.tool_context["tool_descriptions"], dict):
            return False

        return True

    def build_tool_context_string(self) -> str:
        """
        Build tool context string for AI system prompt.

        Returns:
            Formatted tool context string
        """
        if not self.available_tools:
            return ""

        tool_descriptions = []
        for tool_name in self.available_tools:
            description = self.tool_descriptions.get(tool_name, f"Tool: {tool_name}")
            examples = self.tool_usage_examples.get(tool_name, [])
            parameters = self.tool_parameters.get(tool_name, {})
            return_type = self.tool_return_types.get(tool_name, "unknown")

            tool_descriptions.append(
                f"""
Tool: {tool_name}
Description: {description}
Parameters: {json.dumps(parameters) if parameters else "None"}
Return Type: {return_type}
Examples: {', '.join(examples) if examples else "None"}
"""
            )

        return f"""
TOOL INTEGRATION CONTEXT:
You have access to the following tools. Use them when appropriate for the research task.

{''.join(tool_descriptions)}

TOOL USAGE RULES:
1. Use tools when they can provide better, more current, or more specific information
2. For web searches, use web_search tool instead of relying on training data
3. For calculations, use math tools instead of manual computation
4. For document analysis, use document_retrieval tool
5. Always format tool calls as JSON with "tool_call" structure

TOOL CALL FORMAT:
{{
    "tool_call": {{
        "tool_name": "tool_name",
        "arguments": {{"param1": "value1", "param2": "value2"}}
    }},
    "analysis": "I will use the tool to perform this operation"
}}

EXAMPLES:
- "What's the latest news about AI?" → {{"tool_call": {{"tool_name": "web_search", "arguments": {{"query": "latest AI news 2024"}}}}}}
- "Calculate 15% of 250" → {{"tool_call": {{"tool_name": "calculate", "arguments": {{"expression": "250 * 0.15"}}}}}}
- "Extract key points from this document" → {{"tool_call": {{"tool_name": "document_retrieval", "arguments": {{"file_path": "document.pdf", "extract_type": "key_points"}}}}}}

IMPORTANT: Use tools when they can provide better information than your training data. Always format responses as JSON with "tool_call" structure.
"""

    def get_tool_info(self) -> Dict[str, Any]:
        """
        Get information about available tools.

        Returns:
            Dictionary with tool information
        """
        return {
            "available_tools": self.available_tools,
            "tool_descriptions": self.tool_descriptions,
            "tool_usage_examples": self.tool_usage_examples,
            "tool_parameters": self.tool_parameters,
            "tool_return_types": self.tool_return_types,
            "tool_namespaces": self.tool_namespaces,
            "tool_count": len(self.available_tools),
            "has_tools": len(self.available_tools) > 0,
        }

    def has_tool(self, tool_name: str) -> bool:
        """
        Check if a specific tool is available.

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if tool is available, False otherwise
        """
        return tool_name in self.available_tools

    def get_tool_description(self, tool_name: str) -> str:
        """
        Get description for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool description or empty string if not found
        """
        return self.tool_descriptions.get(tool_name, "")

    def log_execution_step(self, step: str, details: str = "") -> None:
        """
        Log execution step for debugging and transparency.

        Args:
            step: Step description
            details: Additional details
        """
        logger.info(f"🔍 AGENT STEP: {step}")
        if details:
            logger.info(f"   📝 Details: {details}")

    def get_user_input_via_websocket(
        self,
        prompt: str,
        host: str = "localhost",
        port: int = 38765,
        timeout: int = 300,  # 5 minutes default timeout
        fallback_input: Optional[str] = None,
        use_stdin: bool = True,  # Default to stdin (works with AgentHub)
    ) -> str:
        """
        Get user input via stdin or WebSocket connection.

        By default uses stdin which works with AgentHub and other environments.
        Can optionally connect to a standalone WebSocket server.

        Args:
            prompt: The prompt/question to display or send
            host: WebSocket server host (default: localhost) - only for WebSocket mode
            port: WebSocket server port (default: 38765) - only for WebSocket mode
            timeout: Connection timeout in seconds (default: 300) - only for WebSocket mode
            fallback_input: Fallback value if input fails (default: None)
            use_stdin: If True, use stdin (default); if False, use WebSocket

        Returns:
            User's response from stdin, WebSocket server, or fallback_input

        Example:
            # Use stdin (works with AgentHub)
            clarification = agent.get_user_input_via_websocket(
                prompt="Please provide clarification",
                fallback_input="No clarification provided"
            )
            
            # Use WebSocket (standalone mode)
            clarification = agent.get_user_input_via_websocket(
                prompt="Please provide clarification",
                use_stdin=False,
                host="localhost",
                port=38765
            )
        """
        import sys
        
        if use_stdin:
            # Use stdin for input (works with AgentHub and terminal)
            self.logger.info("📝 Using stdin for user input")
            
            try:
                # Print the prompt to stderr (not stdout - keep stdout clean for JSON output)
                sys.stderr.write(f"\n{'='*60}\n")
                sys.stderr.write("🧠 USER INPUT REQUIRED\n")
                sys.stderr.write(f"{'='*60}\n")
                sys.stderr.write(f"{prompt}\n")
                sys.stderr.write(f"{'='*60}\n\n")
                sys.stderr.flush()
                
                # Wait for input via stdin (blocks indefinitely until user responds)
                self.logger.info("⏳ Waiting for user input via stdin...")
                user_input = input().strip()
                
                if user_input:
                    self.logger.info(f"✅ Received user input: {user_input}")
                    return user_input
                else:
                    self.logger.info("Empty input provided, using fallback")
                    return fallback_input if fallback_input else ""
                    
            except Exception as e:
                self.logger.warning(f"Could not get input via stdin: {e}")
                if fallback_input is not None:
                    self.logger.info(f"Using fallback input: {fallback_input}")
                    return fallback_input
                raise
        
        # WebSocket mode - connect to WebSocket server
        try:
            # Create socket connection
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(timeout)
            client_socket.connect((host, port))
            
            self.logger.info(f"Connected to WebSocket server at {host}:{port}")

            # Send prompt to server
            message_data = {"type": "prompt", "prompt": prompt, "session_id": self.session_id}
            client_socket.send(json.dumps(message_data).encode("utf-8"))
            self.logger.info(f"Sent prompt to server: {prompt}")

            # Wait for response from server (blocking until user responds or timeout)
            self.logger.info(f"⏳ Waiting for user response via WebSocket (timeout: {timeout}s)...")
            response_data = b""
            
            # Keep receiving until we get complete data
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk
                # Try to parse JSON - if successful, we have complete message
                try:
                    data = json.loads(response_data.decode("utf-8"))
                    break
                except json.JSONDecodeError:
                    # Incomplete JSON, keep receiving
                    continue
            
            user_input = data.get("message", data.get("response", ""))
            self.logger.info(f"✅ Received user input via WebSocket: {user_input}")

            client_socket.close()
            return user_input

        except socket.timeout:
            self.logger.warning(f"WebSocket connection timeout after {timeout}s")
            if fallback_input is not None:
                self.logger.info(f"Using fallback input: {fallback_input}")
                return fallback_input
            raise

        except Exception as e:
            self.logger.error(f"Error getting user input via WebSocket: {e}")
            if fallback_input is not None:
                self.logger.info(f"Using fallback input: {fallback_input}")
                return fallback_input
            raise

    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(session_id={self.session_id}, initialized={self._initialized})"

    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return (
            f"{self.__class__.__name__}("
            f"session_id={self.session_id}, "
            f"initialized={self._initialized}, "
            f"capabilities={len(self._capabilities)}, "
            f"tools={len(self._tools)})"
        )
