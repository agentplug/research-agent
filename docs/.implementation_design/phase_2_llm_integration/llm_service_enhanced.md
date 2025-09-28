# Enhanced LLM Service Implementation - Phase 2 (AgentHub-Inspired)

## Overview

This document details the enhanced LLM service implementation for Phase 2, incorporating proven patterns from AgentHub's LLM service architecture while maintaining compatibility with our research agent's specific needs.

## Key Learnings from AgentHub

### 1. **AISuite Integration Pattern**
- AgentHub uses AISuite as a unified interface for multiple providers
- Single client initialization with provider-specific configurations
- Automatic model detection and fallback mechanisms
- Shared instance management to avoid duplicate initialization

### 2. **Model Detection and Scoring**
- Intelligent model scoring based on size, family, and quality indicators
- Priority: Local models (Ollama > LM Studio) > Cloud models
- Comprehensive model configuration with scoring weights
- Automatic URL detection for local providers

### 3. **Client Management Architecture**
- Centralized client manager for different providers
- Provider-specific initialization logic
- Environment variable support for configuration
- Graceful fallback handling

### 4. **Decision Making Integration**
- LLM-powered decision making for intelligent selections
- Structured data extraction capabilities
- JSON response handling with fallback parsing
- Confidence scoring and reasoning

## Enhanced Implementation Strategy

### 1. **AISuite Integration**
Instead of implementing individual providers, use AISuite as the unified interface:

```python
# research_agent/llm_service/core.py (enhanced)
import aisuite as ai
from .client_manager import ClientManager
from .model_detector import ModelDetector

class LLMService:
    """Enhanced LLM service with AISuite integration."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, model: Optional[str] = None):
        self.model_detector = ModelDetector()
        self.client_manager = ClientManager()

        # Determine model to use
        if model:
            self.model = model
        else:
            self.model = self.model_detector.detect_best_model()

        # Initialize AISuite client
        self.client = self.client_manager.initialize_client(self.model)

    def generate_response(self, query: str, mode: str, **kwargs) -> Dict[str, Any]:
        """Generate response using AISuite."""
        if not self.client:
            return self._fallback_to_mock(query, mode)

        try:
            # Build mode-specific prompt
            system_prompt = self._get_system_prompt(mode)
            user_prompt = self._build_user_prompt(query, mode)

            # Generate using AISuite
            response = self.client.chat.completions.create(
                model=self.client_manager.get_actual_model_name(self.model),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self._get_mode_temperature(mode),
                max_tokens=self._get_mode_tokens(mode)
            )

            return self._format_response(response, mode, query)

        except Exception as e:
            logger.error(f"AISuite generation failed: {e}")
            return self._fallback_to_mock(query, mode)
```

### 2. **Client Manager (AgentHub Pattern)**
```python
# research_agent/llm_service/client_manager.py
class ClientManager:
    """Manages AISuite client initialization for different providers."""

    def initialize_client(self, model: str) -> Optional[Any]:
        """Initialize AISuite client for the given model."""
        try:
            import aisuite as ai
        except ImportError:
            logger.warning("AISuite not available, using fallback")
            return None

        if self._is_ollama_model(model):
            return self._initialize_ollama_client(model, ai)
        elif self._is_lmstudio_model(model):
            return self._initialize_lmstudio_client(model, ai)
        else:
            return self._initialize_cloud_client(model, ai)

    def _initialize_ollama_client(self, model: str, ai: Any) -> Optional[Any]:
        """Initialize AISuite client for Ollama."""
        try:
            ollama_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
            provider_configs = {
                "ollama": {
                    "api_url": ollama_url,
                    "timeout": 300,
                }
            }
            return ai.Client(provider_configs=provider_configs)
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            return None
```

### 3. **Model Detector (AgentHub Pattern)**
```python
# research_agent/llm_service/model_detector.py
class ModelDetector:
    """Handles model detection and scoring for optimal model selection."""

    def detect_best_model(self) -> str:
        """Detect the best available model across all providers."""
        # Try local models first (Ollama preferred over LM Studio)
        local_model = self._detect_running_local_model()
        if local_model:
            return local_model

        # Fallback to cloud models
        cloud_model = self._detect_cloud_model()
        if cloud_model:
            return cloud_model

        # Final fallback
        return "fallback"

    def _detect_running_local_model(self) -> Optional[str]:
        """Detect running local models."""
        # Try Ollama first
        ollama_model = self._detect_ollama_model()
        if ollama_model:
            return ollama_model

        # Fallback to LM Studio
        lmstudio_model = self._detect_lmstudio_model()
        if lmstudio_model:
            return lmstudio_model

        return None

    def _detect_ollama_model(self) -> Optional[str]:
        """Detect available Ollama models."""
        url = self._detect_ollama_url()

        if not self._check_ollama_available(url):
            return None

        available_models = self._get_ollama_models(url)
        if not available_models:
            return None

        best_model = self._select_best_ollama_model(available_models)
        if best_model:
            return f"ollama:{best_model}"

        return None

    def _calculate_model_score(self, model_name: str) -> int:
        """Calculate a score for a model based on various factors."""
        score = 0

        # Size scoring
        for size, points in ModelConfig.SIZE_SCORES.items():
            if size in model_name.lower():
                score += points
                break

        # Family scoring
        for family, points in ModelConfig.FAMILY_SCORES.items():
            if family in model_name.lower():
                score += points
                break

        # Quality indicators
        for indicator, points in ModelConfig.QUALITY_INDICATORS.items():
            if indicator in model_name.lower():
                score += points

        return score
```

### 4. **Model Configuration (AgentHub Pattern)**
```python
# research_agent/llm_service/model_config.py
class ModelConfig:
    """Configuration constants for model selection and scoring."""

    # Model size scoring (larger models get higher scores)
    SIZE_SCORES = {
        "1b": 10, "2b": 15, "3b": 20, "4b": 35, "7b": 30, "8b": 40,
        "13b": 50, "20b": 60, "32b": 70, "70b": 80, "120b": 90,
        "latest": 40,
    }

    # Model family scoring (quality indicators)
    FAMILY_SCORES = {
        "gpt-oss": 50, "deepseek": 60, "qwen": 60, "gemma": 45,
        "llama": 40, "mistral": 45, "claude": 55, "gpt": 50,
    }

    # Quality indicators that boost scores
    QUALITY_INDICATORS = {
        "reasoning": 10, "thinking": 5, "instruct": 5, "chat": 3,
        "latest": 5, "stable": 3,
    }

    # Default URLs for local providers
    OLLAMA_URLS = [
        "http://localhost:11434",
        "http://127.0.0.1:11434",
        "http://0.0.0.0:11434",
    ]

    LMSTUDIO_URLS = [
        "http://localhost:1234/v1",
        "http://127.0.0.1:1234/v1",
        "http://0.0.0.0:1234/v1",
    ]

@dataclass
class ModelInfo:
    """Data class for model information."""
    name: str
    provider: str
    size: str | None
    family: str | None
    score: int
    is_local: bool
    is_available: bool
    url: str | None = None
```

### 5. **Shared Instance Management (AgentHub Pattern)**
```python
# research_agent/llm_service/core.py
# Global shared instance
_shared_llm_service: Optional["LLMService"] = None

def get_shared_llm_service(
    config: Optional[Dict[str, Any]] = None,
    model: Optional[str] = None
) -> LLMService:
    """Get or create a shared LLM service instance."""
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
```

## Key Benefits of AgentHub-Inspired Design

### 1. **Proven Architecture**
- Uses AISuite for unified provider access
- Automatic model detection with intelligent scoring
- Shared instance management for efficiency
- Comprehensive fallback mechanisms

### 2. **Research-Specific Optimizations**
- Mode-specific prompts and settings
- Research-optimized temperature and token limits
- Context-aware model selection
- Enhanced error handling for research workflows

### 3. **Maintainability**
- Clear separation of concerns
- Modular design with focused responsibilities
- Comprehensive logging and debugging
- Easy to extend with new providers

### 4. **Performance**
- Shared instance management
- Intelligent model caching
- Efficient client initialization
- Graceful fallback to mock service

## Implementation Order

1. **Create model configuration and data classes**
2. **Implement model detector with scoring**
3. **Create client manager for AISuite integration**
4. **Enhance core LLM service with AISuite**
5. **Add shared instance management**
6. **Update configuration for AISuite**
7. **Write comprehensive tests**
8. **Test with real providers**

## Dependencies

- `aisuite[openai]>=0.1.7` (already in pyproject.toml)
- `httpx` for HTTP requests to local providers
- Environment variables for API keys and URLs

This enhanced design incorporates the best practices from AgentHub while maintaining compatibility with our research agent's specific needs and Phase 1 implementation.
