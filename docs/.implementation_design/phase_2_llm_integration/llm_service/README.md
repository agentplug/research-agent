# LLM Service Module - Phase 2

## Overview

This module implements the enhanced LLM service for Phase 2, incorporating AgentHub's proven AISuite integration patterns while maintaining research-specific optimizations.

## Module Structure

```
research_agent/llm_service/
├── __init__.py
├── core.py                    # Enhanced LLMService with AISuite
├── client_manager.py          # AISuite client management
├── model_detector.py          # Model detection and scoring
├── model_config.py            # Model configuration and data classes
└── mock_service.py            # Mock service (from Phase 1)
```

## Key Components

### 1. Core LLM Service (`core.py`)

Enhanced LLM service with AISuite integration (AgentHub pattern):

```python
class LLMService:
    """Enhanced LLM service with AgentHub-inspired architecture."""
    
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
        """Generate response using AISuite with research mode optimization."""
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

### 2. Client Manager (`client_manager.py`)

Manages AISuite client initialization (AgentHub pattern):

```python
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
    
    def get_actual_model_name(self, model: str) -> str:
        """Get the actual model name to use with AISuite."""
        if self._is_ollama_model(model):
            return model  # Keep full format for Ollama
        elif self._is_lmstudio_model(model):
            model_name = model.replace("lmstudio:", "")
            return f"openai:{model_name}"
        else:
            return model  # Use as-is for cloud models
```

### 3. Model Detector (`model_detector.py`)

Intelligent model detection and scoring:

```python
class ModelDetector:
    """Handles model detection and scoring for optimal model selection."""
    
    def detect_best_model(self) -> str:
        """Detect the best available model across all providers."""
        # Priority: Local models (Ollama > LM Studio) > Cloud models
        local_model = self._detect_running_local_model()
        if local_model:
            return local_model
        
        cloud_model = self._detect_cloud_model()
        if cloud_model:
            return cloud_model
        
        return "fallback"
    
    def _calculate_model_score(self, model_name: str) -> int:
        """Calculate score based on size, family, and quality indicators."""
```

### 4. Model Configuration (`model_config.py`)

Configuration constants and data classes:

```python
class ModelConfig:
    """Configuration constants for model selection and scoring."""
    
    SIZE_SCORES = {
        "1b": 10, "2b": 15, "3b": 20, "4b": 35, "7b": 30, "8b": 40,
        "13b": 50, "20b": 60, "32b": 70, "70b": 80, "120b": 90,
        "latest": 40,
    }
    
    FAMILY_SCORES = {
        "gpt-oss": 50, "deepseek": 60, "qwen": 60, "gemma": 45,
        "llama": 40, "mistral": 45, "claude": 55, "gpt": 50,
    }

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

## Implementation Details

### AISuite Integration (AgentHub Pattern)

The service uses AISuite as the unified interface for all providers:

```python
# Initialize AISuite client
import aisuite as ai

# Provider-specific configuration
provider_configs = {
    "ollama": {
        "api_url": "http://localhost:11434",
        "timeout": 300,
    }
}

client = ai.Client(provider_configs=provider_configs)

# Generate response
response = client.chat.completions.create(
    model="ollama:llama3.1:8b",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.2,
    max_tokens=1000
)
```

### Model Detection Priority

1. **Local Models** (preferred for privacy and speed)
   - Ollama (highest priority)
   - LM Studio (fallback)

2. **Cloud Models** (fallback when local unavailable)
   - OpenAI, Anthropic, Google, etc.

3. **Mock Service** (ultimate fallback)

### Research Mode Optimization

Each research mode has optimized settings:

```python
MODE_SETTINGS = {
    'instant': {'temperature': 0.1, 'max_tokens': 500},
    'quick': {'temperature': 0.2, 'max_tokens': 1000},
    'standard': {'temperature': 0.2, 'max_tokens': 1500},
    'deep': {'temperature': 0.3, 'max_tokens': 2000}
}
```

### Shared Instance Management

Prevents duplicate initialization and improves performance:

```python
_shared_llm_service: Optional["LLMService"] = None

def get_shared_llm_service() -> LLMService:
    """Get or create a shared LLM service instance."""
    global _shared_llm_service
    if _shared_llm_service is None:
        _shared_llm_service = LLMService()
    return _shared_llm_service
```

## Testing Strategy

### Unit Tests
- Test model detection and scoring
- Test AISuite client initialization
- Test mode-specific response generation
- Test fallback mechanisms
- Test shared instance management

### Integration Tests
- Test with real Ollama models
- Test with real cloud providers (OpenAI, Anthropic)
- Test mode-specific behavior differences
- Test error handling and recovery
- Test model switching and fallbacks

## Configuration

### Environment Variables
```bash
# Ollama
OLLAMA_API_URL=http://localhost:11434

# LM Studio
LMSTUDIO_API_URL=http://localhost:1234/v1

# Cloud providers
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### config.json Updates
```json
{
  "llm": {
    "default_provider": "ollama",
    "fallback_order": ["ollama", "openai", "anthropic"],
    "mode_settings": {
      "instant": {"temperature": 0.1, "max_tokens": 500},
      "quick": {"temperature": 0.2, "max_tokens": 1000},
      "standard": {"temperature": 0.2, "max_tokens": 1500},
      "deep": {"temperature": 0.3, "max_tokens": 2000}
    }
  }
}
```

## Success Criteria

- [ ] AISuite integration works with multiple providers
- [ ] Model detection selects optimal models automatically
- [ ] Research mode-specific optimizations are applied
- [ ] Fallback mechanisms work correctly
- [ ] Shared instance management improves performance
- [ ] All existing Phase 1 tests pass
- [ ] New tests cover AISuite integration
- [ ] Configuration supports all providers through AISuite

## Dependencies

- `aisuite[openai]>=0.1.7` (already in pyproject.toml)
- `httpx` for HTTP requests to local providers
- Environment variables for API keys and URLs

## Next Steps

1. Implement model configuration and data classes
2. Create model detector with scoring
3. Build client manager for AISuite
4. Enhance core LLM service
5. Add shared instance management
6. Write comprehensive tests
7. Test with real providers through AISuite
