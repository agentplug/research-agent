# LLM Service Module Implementation - Phase 2 Real LLM

## Overview
Phase 2 focuses on implementing real LLM providers and replacing mock responses with actual API calls to OpenAI, Anthropic, Google, and local models.

## Module Structure
```
src/llm_service/
├── __init__.py
├── core.py
├── providers.py
└── utils.py
```

## Files to Modify

### `src/llm_service/core.py`
- Replace MockLLMService with real CoreLLMService
- Implement real provider integration
- Add real model detection
- Implement real response generation

### `src/llm_service/providers.py`
- Implement OpenAI provider
- Implement Anthropic provider
- Implement Google provider
- Implement local model providers

## Key Features Implemented

### Real Provider Integration
- OpenAI GPT models (GPT-4, GPT-3.5-turbo)
- Anthropic Claude models (Claude-3, Claude-2)
- Google Gemini models (Gemini-Pro, Gemini-1.5)
- Local models (Ollama, LM Studio)

### Real Model Detection
- Automatic provider availability checking
- Best model selection based on capabilities
- Fallback mechanisms
- Model capability assessment

### Real Response Generation
- Actual API calls to LLM providers
- Real response parsing and processing
- Error handling and retry logic
- Rate limiting and timeout handling

## Implementation Details

### CoreLLMService Class
```python
class CoreLLMService:
    """Real LLM service with multiple provider support."""
    
    def __init__(self, model: str = None, agent_type: str = "generic"):
        """Initialize with real model and provider."""
        self.model = model or self._detect_best_model()
        self.temperature = 0.0
        self.max_tokens = None
        self.client = None
        self.agent_type = agent_type
        self._initialize_client()
    
    def _detect_best_model(self) -> str:
        """Detect best available model."""
        # Check OpenAI availability
        if self._check_openai_availability():
            return "gpt-4"
        
        # Check Anthropic availability
        if self._check_anthropic_availability():
            return "claude-3-sonnet"
        
        # Check Google availability
        if self._check_google_availability():
            return "gemini-pro"
        
        # Check local models
        if self._check_local_availability():
            return "llama2"
        
        # Fallback to mock
        return "mock-model"
    
    def _initialize_client(self):
        """Initialize the appropriate client."""
        if self.model.startswith("gpt"):
            self._init_openai_client()
        elif self.model.startswith("claude"):
            self._init_anthropic_client()
        elif self.model.startswith("gemini"):
            self._init_google_client()
        elif self.model.startswith("llama"):
            self._init_local_client()
        else:
            self._init_mock_client()
```

### Real Provider Implementations
```python
def _init_openai_client(self):
    """Initialize OpenAI client."""
    try:
        import openai
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except ImportError:
        raise ImportError("OpenAI client not installed")

def _init_anthropic_client(self):
    """Initialize Anthropic client."""
    try:
        import anthropic
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    except ImportError:
        raise ImportError("Anthropic client not installed")

def _init_google_client(self):
    """Initialize Google client."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.client = genai
    except ImportError:
        raise ImportError("Google client not installed")

def _init_local_client(self):
    """Initialize local model client."""
    try:
        import requests
        self.client = requests
        self.base_url = "http://localhost:11434"  # Ollama default
    except ImportError:
        raise ImportError("Requests not installed")
```

### Real Response Generation
```python
def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.0, **kwargs) -> str:
    """Generate real response from LLM."""
    try:
        if self.model.startswith("gpt"):
            return self._generate_openai(prompt, system_prompt, temperature, **kwargs)
        elif self.model.startswith("claude"):
            return self._generate_anthropic(prompt, system_prompt, temperature, **kwargs)
        elif self.model.startswith("gemini"):
            return self._generate_google(prompt, system_prompt, temperature, **kwargs)
        elif self.model.startswith("llama"):
            return self._generate_local(prompt, system_prompt, temperature, **kwargs)
        else:
            return self._generate_mock(prompt, system_prompt, temperature, **kwargs)
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return f"Error generating response: {str(e)}"

def _generate_openai(self, prompt: str, system_prompt: str, temperature: float, **kwargs) -> str:
    """Generate response using OpenAI."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    response = self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        temperature=temperature,
        max_tokens=self.max_tokens,
        **kwargs
    )
    
    return response.choices[0].message.content

def _generate_anthropic(self, prompt: str, system_prompt: str, temperature: float, **kwargs) -> str:
    """Generate response using Anthropic."""
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    
    response = self.client.messages.create(
        model=self.model,
        max_tokens=self.max_tokens or 1000,
        temperature=temperature,
        messages=[{"role": "user", "content": full_prompt}],
        **kwargs
    )
    
    return response.content[0].text

def _generate_google(self, prompt: str, system_prompt: str, temperature: float, **kwargs) -> str:
    """Generate response using Google."""
    model = self.client.GenerativeModel(self.model)
    
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    
    response = model.generate_content(
        full_prompt,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": self.max_tokens,
            **kwargs
        }
    )
    
    return response.text

def _generate_local(self, prompt: str, system_prompt: str, temperature: float, **kwargs) -> str:
    """Generate response using local model."""
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    
    response = self.client.post(
        f"{self.base_url}/api/generate",
        json={
            "model": self.model,
            "prompt": full_prompt,
            "temperature": temperature,
            **kwargs
        }
    )
    
    return response.json()["response"]
```

## Testing
- Provider integration tests
- Model detection tests
- Response generation tests
- Error handling tests
- Rate limiting tests

## Dependencies
- OpenAI API client
- Anthropic API client
- Google Generative AI client
- Local model clients
- Python 3.11+
- Environment variable configuration
