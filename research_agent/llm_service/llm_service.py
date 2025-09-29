"""
Core LLM Service - AISuite Integration

This module provides the core LLM service interface with real LLM providers
using AISuite for unified provider access.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from ..base_agent.error_handler import ErrorHandler
from ..utils.utils import format_response
from .client_manager import ClientManager
from .model_config import ModelInfo
from .model_detector import ModelDetector

logger = logging.getLogger(__name__)

# Global shared instance (AgentHub pattern)
_shared_llm_service: Optional["LLMService"] = None


class LLMService:
    """
    LLM service with AISuite integration for real provider access.

    Features:
    - AISuite integration for unified provider access
    - Automatic model detection and selection
    - Multi-provider support (Ollama, LM Studio, OpenAI, Anthropic, etc.)
    - Shared instance management
    - Research mode-specific optimization
    """

    def __init__(
        self, config: Optional[Dict[str, Any]] = None, model: Optional[str] = None
    ):
        """
        Initialize LLM service.

        Args:
            config: Configuration dictionary
            model: Specific model to use (e.g., "ollama:llama3.1:8b")
        """
        self.config = config or {}
        self.error_handler = ErrorHandler("LLMService")

        # Initialize components
        self.model_detector = ModelDetector()
        self.client_manager = ClientManager()
        self.cache: Dict[str, Any] = {}
        self._model_info: Optional[ModelInfo] = None

        # Determine model to use
        if model:
            self.model = model
            logger.info(f"🎯 Using specified model: {model}")
        else:
            self.model = self.model_detector.detect_best_model()
            logger.info(f"🎯 Auto-selected model: {self.model}")

        # Initialize client
        self.client = self.client_manager.initialize_client(self.model)

        self.service_type = "real"
        self.initialized = True

    def generate(
        self,
        input_data: Union[str, List[Dict[str, Any]]],
        system_prompt: Optional[str] = None,
        return_json: bool = False,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str:
        """
        Generate response using AISuite with research mode optimization.

        Args:
            input_data: Either a string (single prompt) or list of messages
            system_prompt: Optional system prompt to define AI behavior
            return_json: If True, request JSON response from AISuite
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
            **kwargs: Additional parameters for AISuite

        Returns:
            Generated text response from LLM
        """
        if not self.client:
            return self._fallback_response()

        try:
            # Prepare request parameters
            request_kwargs = kwargs.copy()

            # Handle JSON response format for different providers
            if return_json:
                if self.is_local_model():
                    # For local models (Ollama/LM Studio), ask for JSON in prompt
                    if isinstance(input_data, str):
                        input_data = (
                            f"{input_data}\n\nPlease respond with valid JSON only, "
                            "no additional text."
                        )
                    elif isinstance(input_data, list):
                        # Add JSON instruction to the last user message
                        if input_data and input_data[-1].get("role") == "user":
                            input_data[-1]["content"] += (
                                "\n\nPlease respond with valid JSON only, "
                                "no additional text."
                            )
                else:
                    # For cloud models, use response_format
                    request_kwargs["response_format"] = {"type": "json_object"}

            # Set temperature parameter
            request_kwargs["temperature"] = temperature

            if isinstance(input_data, str):
                # Single prompt - convert to messages format
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": input_data})

                response = self.client.chat.completions.create(
                    model=self.client_manager.get_actual_model_name(self.model),
                    messages=messages,
                    **request_kwargs,
                )

                if hasattr(response, "choices") and response.choices:
                    return str(response.choices[0].message.content)
                else:
                    logger.error(f"Invalid response format: {response}")
                    return self._fallback_response()

            elif isinstance(input_data, list):
                # Messages - organize into AISuite format
                messages = self._organize_messages_to_aisuite_format(
                    input_data, system_prompt
                )

                response = self.client.chat.completions.create(
                    model=self.client_manager.get_actual_model_name(self.model),
                    messages=messages,
                    **request_kwargs,
                )

                if hasattr(response, "choices") and response.choices:
                    return str(response.choices[0].message.content)
                else:
                    logger.error(f"Invalid response format: {response}")
                    return self._fallback_response()
            else:
                raise ValueError("input_data must be string or list")

        except Exception as e:
            logger.error(f"AISuite generation failed: {e}")
            return self._fallback_response()

    def _get_mode_settings(self, mode: str) -> Dict[str, Any]:
        """Get mode-specific settings."""
        mode_settings = {
            "instant": {"temperature": 0.1, "max_tokens": 500},
            "quick": {"temperature": 0.2, "max_tokens": 1000},
            "standard": {"temperature": 0.2, "max_tokens": 1500},
            "deep": {"temperature": 0.3, "max_tokens": 2000},
        }
        return mode_settings.get(mode, {"temperature": 0.2, "max_tokens": 1000})

    def _get_system_prompt(self, mode: str) -> str:
        """Get system prompt for research mode."""
        system_prompts = {
            "instant": "You are a research assistant for INSTANT research mode. Provide quick, accurate answers based on available data. Focus on key facts and essential information.",
            "quick": "You are a research assistant for QUICK research mode. Analyze data and provide enhanced answers with context. Include relevant details and insights.",
            "standard": "You are a research assistant for STANDARD research mode. Conduct comprehensive research with multiple rounds of analysis. Provide thorough, well-structured responses.",
            "deep": "You are a research assistant for DEEP research mode. Conduct exhaustive research with clarification and comprehensive analysis. Provide detailed, well-researched responses with full context.",
        }
        return system_prompts.get(mode, "You are a helpful research assistant.")

    def _build_user_prompt(self, query: str, mode: str) -> str:
        """Build user prompt for research mode."""
        mode_prompts = {
            "instant": f"Provide a concise, factual answer to: {query}",
            "quick": f"Provide enhanced analysis with context for: {query}",
            "standard": f"Conduct comprehensive research with multiple perspectives on: {query}",
            "deep": f"Conduct exhaustive research with academic-level analysis on: {query}",
        }
        return mode_prompts.get(mode, f"Answer: {query}")

    def _organize_messages_to_aisuite_format(
        self, messages: List[Dict[str, Any]], system_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Organize messages for AISuite format."""
        organized_messages = []

        # Add system prompt if provided
        if system_prompt:
            organized_messages.append({"role": "system", "content": system_prompt})

        # Add user messages
        for message in messages:
            if message.get("role") in ["user", "assistant", "system"]:
                organized_messages.append(message)

        return organized_messages

    def is_local_model(self) -> bool:
        """Check if the current model is a local model."""
        return self.model.startswith(("ollama:", "lmstudio:"))

    def get_current_model(self) -> str:
        """Get the current model identifier."""
        return self.model

    def _fallback_response(self) -> str:
        """Provide fallback response when LLM is unavailable."""
        return "AISuite not available"

    def _get_provider_name(self, model: str) -> str:
        """Get provider name from model identifier."""
        if ":" in model:
            return model.split(":")[0]
        return "unknown"

    def get_available_models(self) -> List[ModelInfo]:
        """Get all available models."""
        try:
            return self.model_detector.list_available_models()
        except Exception as e:
            self.error_handler.log_error(e, {"component": "get_models"})
            return []

    def get_service_status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            "status": "operational",
            "type": "real",
            "model": self.model,
            "provider": self._get_provider_name(self.model),
            "is_local": self.model_detector.is_local_model(self.model),
            "client_available": self.client is not None,
            "initialized": self.initialized,
        }

    def get_model_info(self) -> ModelInfo:
        """Get information about the current model."""
        if not self._model_info:
            self._model_info = self.model_detector.create_model_info(
                self.model, is_local=self.model_detector.is_local_model(self.model)
            )
        return self._model_info


# Shared instance management (AgentHub pattern)
def get_shared_llm_service(
    config: Optional[Dict[str, Any]] = None, model: Optional[str] = None
) -> LLMService:
    """
    Get or create a shared LLM service instance.

    This prevents duplicate model detection and reduces initialization overhead.

    Args:
        config: Configuration dictionary
        model: Specific model to use

    Returns:
        Shared LLMService instance
    """
    global _shared_llm_service

    if _shared_llm_service is None:
        logger.debug("Created shared LLMService instance")
        _shared_llm_service = LLMService(config=config, model=model)
    else:
        logger.debug("Reusing shared LLMService instance")

    return _shared_llm_service


def reset_shared_llm_service() -> None:
    """Reset the shared LLM service instance."""
    global _shared_llm_service
    _shared_llm_service = None
    logger.debug("Reset shared LLMService instance")
