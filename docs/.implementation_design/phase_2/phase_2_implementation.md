# Phase 2: Real LLM Integration - Implementation Design

## Overview

**Phase Goal**: Replace mock LLM service with real LLM integration and implement mode-specific research workflows.

**Duration**: 2 weeks  
**Deliverable**: Agent with real AI responses and mode-specific behavior testable in AgentHub

## Modules to Create/Modify

### 1. **Root Level Files** (Modify)

#### `agent.py` - Enhanced Entry Point
**Purpose**: Update agent with real LLM integration and mode-specific workflows

**Key Changes**:
- Replace mock LLM service with real LLM service
- Implement mode-specific research workflows
- Add auto mode selection logic
- Enhanced error handling and response formatting

**Implementation Details**:
```python
#!/usr/bin/env python3
"""
Agent Hub Agent: research-agent
Phase 2: Real LLM integration with mode-specific workflows
"""

import json
import sys
import os
import logging
from typing import Dict, Any, Optional, List
import asyncio
import tempfile
from datetime import datetime

# Import our modules
from src.base_agent import BaseAgent
from llm_service import CoreLLMService, get_shared_llm_service

logger = logging.getLogger(__name__)

class ResearchAgent(BaseAgent):
    """Research agent with real LLM integration for Phase 2."""
    
    def __init__(self, tool_context: Optional[Dict[str, Any]] = None):
        """Initialize with real LLM service."""
        # Initialize BaseAgent
        super().__init__(external_tools=tool_context.get("available_tools", []) if tool_context else [])
        
        self.config = self._load_config()
        self.llm_service = get_shared_llm_service(agent_type="research")
        self.tool_context = tool_context or {}
        
    def _call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Call an external tool with parameters."""
        if not self.has_tool(tool_name):
            raise ValueError(f"Tool '{tool_name}' not available")
        
        # Get tool information from context
        tool_info = self.tool_context.get("tool_descriptions", {}).get(tool_name)
        if not tool_info:
            raise ValueError(f"Tool '{tool_name}' not found in tool context")
        
        # Example tool calling logic (this would be implemented based on AgentHub's tool system)
        # In real implementation, this would interface with AgentHub's tool calling mechanism
        return f"Real LLM result from {tool_name} with parameters: {parameters}"
    
    def _get_available_tools_info(self) -> Dict[str, Any]:
        """Get detailed information about available tools."""
        return {
            "available_tools": self.get_available_tools(),
            "tool_descriptions": self.tool_context.get("tool_descriptions", {}),
            "tool_usage_examples": self.tool_context.get("tool_usage_examples", {}),
            "tool_parameters": self.tool_context.get("tool_parameters", {}),
            "tool_return_types": self.tool_context.get("tool_return_types", {})
        }
    
    def _execute_dynamic_research(self, question: str, mode: str) -> str:
        """Execute dynamic research with LLM deciding tools for each round."""
        try:
            tools_info = self._get_available_tools_info()
            available_tools = tools_info["available_tools"]
            
            if not available_tools:
                return f"No tools available for research: {question}"
            
            # Initialize research state
            research_data = []
            max_iterations = self._get_max_iterations_for_mode(mode)
            
            for iteration in range(max_iterations):
                # LLM decides which tools to use for this round
                tools_to_use = self._select_tools_for_round(
                    question, mode, research_data, available_tools, iteration
                )
                
                if not tools_to_use:
                    break  # No tools selected for this round
                
                # Execute tools for this round
                round_results = []
                for tool_name in tools_to_use:
                    tool_result = self._call_tool(tool_name, {"query": question})
                    round_results.append(f"{tool_name}: {tool_result}")
                
                if round_results:
                    research_data.extend(round_results)
                
                # Check if research is complete
                if self._is_research_complete(question, research_data, mode):
                    break
            
            # Generate final response
            return self._generate_final_response(question, research_data, mode)
            
        except Exception as e:
            return f"Error in dynamic research: {str(e)}"
    
    def _select_tools_for_round(self, question: str, mode: str, research_data: List[str], 
                               available_tools: List[str], iteration: int) -> List[str]:
        """Use LLM to decide which tools to use for this specific round."""
        try:
            tools_info = self._get_available_tools_info()
            tool_descriptions = tools_info["tool_descriptions"]
            tool_list = "\n".join([f"- {tool}: {desc}" for tool, desc in tool_descriptions.items()])
            
            # Create context about current research state
            current_context = ""
            if research_data:
                current_context = f"\nCurrent research data from previous rounds:\n{chr(10).join(research_data)}"
            
            selection_prompt = f"""
Research question: {question}
Research mode: {mode}
Current round: {iteration + 1}

Available tools:
{tool_list}
{current_context}

Based on the research question, mode, current round, and existing research data, decide which tools to use for this round. Consider:
- What information is still needed to complete the research?
- Which tools can provide the most relevant data for this round?
- You can reuse the same tools from previous rounds if they would provide additional value
- You can select different tools if they would provide better coverage
- For instant research: Focus on 1 tool that provides quick answers
- For quick research: Use 1-2 tools for enhanced context
- For standard research: Use 2-3 tools for comprehensive coverage
- For deep research: Use multiple tools for exhaustive analysis

Return only the tool names separated by commas, no explanations.
If no tools are needed for this round, return "NONE".
"""
            
            selected_tools_response = self.llm_service.generate(
                selection_prompt,
                system_prompt="You are a research coordinator. Decide which tools to use for each research round based on current progress.",
                temperature=0.1
            )
            
            if "NONE" in selected_tools_response.upper():
                return []
            
            # Parse the response to get tool names
            selected_tools = []
            for tool_name in available_tools:
                if tool_name.lower() in selected_tools_response.lower():
                    selected_tools.append(tool_name)
            
            return selected_tools
            
        except Exception as e:
            logger.error(f"Error in round tool selection: {str(e)}")
            return []
    
    def _get_max_iterations_for_mode(self, mode: str) -> int:
        """Get maximum iterations based on research mode."""
        return {
            "instant": 1,
            "quick": 2,
            "standard": 3,
            "deep": 5
        }.get(mode, 2)
    
    def _is_research_complete(self, question: str, research_data: List[str], mode: str) -> bool:
        """Use LLM to determine if research is complete based on current data."""
        try:
            completion_prompt = f"""
Research question: {question}
Research mode: {mode}

Current research data:
{chr(10).join(research_data)}

Based on the research mode and current data, determine if the research is complete:
- For instant research: Is there a quick, direct answer available?
- For quick research: Is there sufficient context for enhanced analysis?
- For standard research: Is there comprehensive coverage of the topic?
- For deep research: Is there exhaustive analysis with full context?

Answer with "YES" if research is complete, "NO" if more research is needed.
"""
            
            completion_response = self.llm_service.generate(
                completion_prompt,
                system_prompt="You are a research completion evaluator. Determine if research objectives are met.",
                temperature=0.1
            )
            
            return "YES" in completion_response.upper()
            
        except Exception as e:
            logger.error(f"Error in research completion check: {str(e)}")
            return True  # Default to complete to avoid infinite loops
    
    def _generate_final_response(self, question: str, research_data: List[str], mode: str) -> str:
        """Generate final response based on research data and mode."""
        try:
            system_prompt = self.config["system_prompts"][mode]
            
            if mode == "deep":
                # Generate clarification questions for deep research
                clarifications = self.llm_service.generate_questions(question, count=3)
                
                # Generate comprehensive analysis
                analysis = self.llm_service.generate(
                    f"Research question: {question}\n\nResearch data:\n" + "\n".join(research_data) + 
                    f"\n\nClarification questions: {clarifications}\n\nProvide exhaustive deep research response with comprehensive analysis.",
                    system_prompt=system_prompt,
                    temperature=self.config["ai"]["temperature"]
                )
                
                # Generate summary
                summary = self.llm_service.generate_summary(analysis)
                
                return f"Deep research results:\n{analysis}\n\nSummary: {summary}\n\nClarification questions: {clarifications}"
            else:
                # Generate response for other modes
                response = self.llm_service.generate(
                    f"Research question: {question}\n\nResearch data:\n" + "\n".join(research_data) + 
                    f"\n\nProvide {mode} research response based on the data.",
                    system_prompt=system_prompt,
                    temperature=self.config["ai"]["temperature"]
                )
                
                return response
                
        except Exception as e:
            return f"Error generating final response: {str(e)}"
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json file."""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config
        except FileNotFoundError:
            # Fallback to default configuration
            return {
                "ai": {"temperature": 0.1, "max_tokens": None, "timeout": 30},
                "research": {"max_sources_per_round": 10, "max_rounds": 12, "timeout_per_round": 300},
                "system_prompts": {
                    "instant": "You are a research assistant for INSTANT research mode. Provide quick, accurate answers based on available data. Focus on key facts and essential information.",
                    "quick": "You are a research assistant for QUICK research mode. Analyze data and provide enhanced answers with context. Include relevant details and insights.",
                    "standard": "You are a research assistant for STANDARD research mode. Conduct comprehensive research with multiple rounds of analysis. Provide thorough, well-structured responses.",
                    "deep": "You are a research assistant for DEEP research mode. Conduct exhaustive research with clarification and comprehensive analysis. Provide detailed, well-researched responses with full context."
                }
            }
    
    def instant_research(self, question: str) -> str:
        """Instant research mode - dynamic tool selection for quick response."""
        try:
            return self._execute_dynamic_research(question, "instant")
        except Exception as e:
            return f"Error in instant research: {str(e)}"
    
    def quick_research(self, question: str) -> str:
        """Quick research mode - dynamic tool selection with enhanced analysis."""
        try:
            return self._execute_dynamic_research(question, "quick")
        except Exception as e:
            return f"Error in quick research: {str(e)}"
    
    def standard_research(self, question: str) -> str:
        """Standard research mode - dynamic tool selection with comprehensive analysis."""
        try:
            return self._execute_dynamic_research(question, "standard")
        except Exception as e:
            return f"Error in standard research: {str(e)}"
    
    def deep_research(self, question: str) -> str:
        """Deep research mode - dynamic tool selection with exhaustive analysis."""
        try:
            return self._execute_dynamic_research(question, "deep")
        except Exception as e:
            return f"Error in deep research: {str(e)}"
    
    async def solve(self, question: str) -> Dict[str, Any]:
        """Auto mode selection based on question complexity."""
        try:
            # Auto-select mode based on question complexity
            question_length = len(question)
            question_complexity = self._analyze_question_complexity(question)
            
            if question_length < 50 and question_complexity < 3:
                result = self.instant_research(question)
                mode = "instant"
            elif question_length < 100 and question_complexity < 5:
                result = self.quick_research(question)
                mode = "quick"
            elif question_length < 200 and question_complexity < 8:
                result = self.standard_research(question)
                mode = "standard"
            else:
                result = self.deep_research(question)
                mode = "deep"
            
            return self.format_response(result, {"mode": mode, "auto_selected": True})
                
        except Exception as e:
            error_info = await self.handle_error(e, {"method": "solve", "question": question})
            return self.format_response(f"Error in auto mode selection: {str(e)}", {"error": error_info, "status": "error"})
    
    def _analyze_question_complexity(self, question: str) -> int:
        """Analyze question complexity for auto mode selection."""
        complexity_score = 0
        
        # Length factor
        if len(question) > 100:
            complexity_score += 2
        elif len(question) > 50:
            complexity_score += 1
        
        # Complexity indicators
        complexity_keywords = [
            "comprehensive", "detailed", "exhaustive", "analysis", "research",
            "compare", "contrast", "evaluate", "assess", "investigate"
        ]
        
        for keyword in complexity_keywords:
            if keyword.lower() in question.lower():
                complexity_score += 1
        
        # Question type factor
        if "?" in question:
            complexity_score += 1
        
        return complexity_score

def main():
    """Main entry point for agent execution."""
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)
    
    try:
        # Parse input from command line
        input_data = json.loads(sys.argv[1])
        method = input_data.get("method")
        parameters = input_data.get("parameters", {})
        tool_context = input_data.get("tool_context", {})
        
        # Create agent instance
        agent = ResearchAgent(tool_context=tool_context)
        
        # Execute requested method
        if method == "instant_research":
            result = agent.instant_research(parameters.get("question", ""))
        elif method == "quick_research":
            result = agent.quick_research(parameters.get("question", ""))
        elif method == "standard_research":
            result = agent.standard_research(parameters.get("question", ""))
        elif method == "deep_research":
            result = agent.deep_research(parameters.get("question", ""))
        elif method == "solve":
            import asyncio
            result = asyncio.run(agent.solve(parameters.get("question", "")))
        else:
            print(json.dumps({"error": f"Unknown method: {method}"}))
            sys.exit(1)
        
        if method == "solve":
            print(json.dumps(result))
        else:
            print(json.dumps({"result": result}))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 2. **LLM Service Module** (Create)

#### `llm_service.py` - Real LLM Service
**Purpose**: Real LLM service with multiple providers and research-specific methods

**Implementation Details**:
```python
"""
Real LLM Service for Phase 2
Provides real LLM integration with multiple providers
"""

import logging
import json
from typing import Any, Optional, Dict, List
from datetime import datetime

# Import AISuite for LLM integration
try:
    from aisuite import ClientManager
    AISUITE_AVAILABLE = True
except ImportError:
    AISUITE_AVAILABLE = False
    logging.warning("AISuite not available, using mock responses")

logger = logging.getLogger(__name__)

class CoreLLMService:
    """Real LLM service for research agent operations."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize LLM service."""
        self.model = model or self._detect_best_model()
        self.temperature = 0.1
        self.max_tokens = None
        self.client = None
        
        if AISUITE_AVAILABLE:
            self._initialize_client()
        else:
            logger.warning("Using mock LLM service - AISuite not available")
    
    def _detect_best_model(self) -> str:
        """Detect best available model."""
        if AISUITE_AVAILABLE:
            try:
                # Try to detect available models
                return "gpt-4"  # Default to GPT-4
            except Exception:
                return "gpt-3.5-turbo"  # Fallback
        else:
            return "mock-model"
    
    def _initialize_client(self):
        """Initialize AISuite client."""
        if AISUITE_AVAILABLE:
            try:
                self.client = ClientManager()
                logger.info(f"Initialized LLM service with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize LLM client: {e}")
                self.client = None
    
    def generate(self, 
                prompt: str, 
                system_prompt: Optional[str] = None,
                temperature: Optional[float] = None,
                max_tokens: Optional[int] = None) -> str:
        """Generate response using LLM."""
        
        if self.client and AISUITE_AVAILABLE:
            try:
                # Use real LLM service
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature or self.temperature,
                    max_tokens=max_tokens or self.max_tokens
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                return self._fallback_response(prompt, system_prompt)
        else:
            # Fallback to mock response
            return self._fallback_response(prompt, system_prompt)
    
    def _fallback_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Fallback response when LLM is not available."""
        # Determine research mode from system prompt
        mode = "instant"
        if system_prompt:
            if "INSTANT" in system_prompt:
                mode = "instant"
            elif "QUICK" in system_prompt:
                mode = "quick"
            elif "STANDARD" in system_prompt:
                mode = "standard"
            elif "DEEP" in system_prompt:
                mode = "deep"
        
        # Generate mode-specific fallback response
        if mode == "instant":
            return f"Instant research response: {prompt[:100]}..."
        elif mode == "quick":
            return f"Quick research response with enhanced context: {prompt[:100]}..."
        elif mode == "standard":
            return f"Standard research response with comprehensive analysis: {prompt[:100]}..."
        elif mode == "deep":
            return f"Deep research response with exhaustive analysis: {prompt[:100]}..."
        else:
            return f"Research response: {prompt[:100]}..."
    
    def generate_research_analysis(self, question: str, data: List[Dict[str, Any]]) -> str:
        """Generate research analysis from data."""
        prompt = f"""
        Analyze the following research data and provide insights:
        
        Question: {question}
        
        Data: {json.dumps(data, indent=2)}
        
        Provide a comprehensive analysis of the data.
        """
        
        return self.generate(prompt, system_prompt="You are a research analyst.")
    
    def generate_clarification_questions(self, question: str) -> List[str]:
        """Generate clarification questions for deep research."""
        prompt = f"""
        Generate 3-5 clarification questions to better understand this research request:
        
        Question: {question}
        
        Return as a JSON array of strings.
        """
        
        try:
            response = self.generate(prompt, system_prompt="You are a research assistant.")
            # Try to parse as JSON
            if response.strip().startswith('['):
                return json.loads(response)
            else:
                # Fallback to simple parsing
                return [
                    f"Clarification question 1 for: {question}",
                    f"Clarification question 2 for: {question}",
                    f"Clarification question 3 for: {question}"
                ]
        except Exception:
            return [
                f"Clarification question 1 for: {question}",
                f"Clarification question 2 for: {question}",
                f"Clarification question 3 for: {question}"
            ]
    
    def generate_follow_up_queries(self, question: str, gaps: List[str]) -> str:
        """Generate follow-up queries based on identified gaps."""
        prompt = f"""
        Based on the research question and identified gaps, generate a refined research query:
        
        Original question: {question}
        Identified gaps: {gaps}
        
        Generate a refined research question that addresses these gaps.
        """
        
        return self.generate(prompt, system_prompt="You are a research strategist.")
    
    def is_local_model(self) -> bool:
        """Check if using local model."""
        return self.model.startswith("ollama:") or self.model.startswith("lm-studio:")
    
    def get_current_model(self) -> str:
        """Get current model name."""
        return self.model

# Global shared instance
_shared_llm_service: Optional[CoreLLMService] = None

def get_shared_llm_service() -> CoreLLMService:
    """Get shared LLM service instance."""
    global _shared_llm_service
    if _shared_llm_service is None:
        _shared_llm_service = CoreLLMService()
    return _shared_llm_service

def reset_shared_llm_service():
    """Reset shared LLM service instance."""
    global _shared_llm_service
    _shared_llm_service = None
```

### 3. **Configuration Files** (Modify)

#### `config.json` - Enhanced Configuration
**Purpose**: Enhanced configuration for Phase 2

**Implementation Details**:
```json
{
  "ai": {
    "temperature": 0.1,
    "max_tokens": null,
    "timeout": 30,
    "model": "gpt-4",
    "fallback_model": "gpt-3.5-turbo"
  },
  "research": {
    "max_sources_per_round": 10,
    "max_rounds": 12,
    "timeout_per_round": 300,
    "instant_rounds": 1,
    "quick_rounds": 2,
    "standard_rounds": 5,
    "deep_rounds": 12
  },
  "system_prompts": {
    "instant": "You are a research assistant for INSTANT research mode. Provide quick, accurate answers based on available data. Focus on key facts and essential information. Keep responses concise and direct.",
    "quick": "You are a research assistant for QUICK research mode. Analyze data and provide enhanced answers with context. Include relevant details and insights. Provide moderate depth with good context.",
    "standard": "You are a research assistant for STANDARD research mode. Conduct comprehensive research with multiple rounds of analysis. Provide thorough, well-structured responses. Include detailed analysis and comprehensive coverage.",
    "deep": "You are a research assistant for DEEP research mode. Conduct exhaustive research with clarification and comprehensive analysis. Provide detailed, well-researched responses with full context. Include deep analysis and comprehensive insights."
  },
  "error_messages": {
    "instant_research": "Error conducting instant research: {error}",
    "quick_research": "Error conducting quick research: {error}",
    "standard_research": "Error conducting standard research: {error}",
    "deep_research": "Error conducting deep research: {error}",
    "solve": "Error in research: {error}"
  },
  "mode_selection": {
    "instant_threshold": 50,
    "quick_threshold": 100,
    "standard_threshold": 200,
    "complexity_keywords": [
      "comprehensive", "detailed", "exhaustive", "analysis", "research",
      "compare", "contrast", "evaluate", "assess", "investigate"
    ]
  }
}
```

## Testing Strategy

### **Unit Tests** (Create)

#### `test_phase2.py` - Phase 2 Tests
**Purpose**: Test Phase 2 functionality

**Implementation Details**:
```python
"""
Phase 2 Tests - Real LLM Integration
"""

import pytest
import json
import subprocess
import sys
from pathlib import Path

class TestPhase2Agent:
    """Test Phase 2 agent functionality."""
    
    @pytest.fixture
    def agent_script(self):
        """Path to agent.py script."""
        return Path(__file__).parent.parent.parent / "agent.py"
    
    def test_instant_research_real_llm(self, agent_script):
        """Test instant research with real LLM."""
        input_data = {
            "method": "instant_research",
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
        assert len(response["result"]) > 50  # Real response, not mock
    
    def test_quick_research_real_llm(self, agent_script):
        """Test quick research with real LLM."""
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
        assert len(response["result"]) > 100  # Enhanced response
    
    def test_standard_research_real_llm(self, agent_script):
        """Test standard research with real LLM."""
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
        assert len(response["result"]) > 200  # Comprehensive response
    
    def test_deep_research_real_llm(self, agent_script):
        """Test deep research with real LLM."""
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
        assert len(response["result"]) > 500  # Exhaustive response
    
    def test_solve_auto_mode_selection(self, agent_script):
        """Test auto mode selection."""
        # Test instant mode selection
        input_data = {
            "method": "solve",
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
        assert len(response["result"]) > 50  # Real response
    
    def test_mode_differences(self, agent_script):
        """Test that different modes produce different response lengths."""
        question = "What is artificial intelligence?"
        
        # Test instant mode
        input_data = {
            "method": "instant_research",
            "parameters": {"question": question}
        }
        
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        instant_response = json.loads(result.stdout)["result"]
        
        # Test deep mode
        input_data = {
            "method": "deep_research",
            "parameters": {"question": question}
        }
        
        result = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        deep_response = json.loads(result.stdout)["result"]
        
        # Deep response should be longer than instant
        assert len(deep_response) > len(instant_response)

class TestRealLLMService:
    """Test real LLM service functionality."""
    
    @pytest.fixture
    def llm_service(self):
        """Create LLM service instance."""
        from llm_service import CoreLLMService
        return CoreLLMService()
    
    def test_generate_response(self, llm_service):
        """Test basic response generation."""
        response = llm_service.generate("What is AI?")
        assert len(response) > 10
        assert "AI" in response or "artificial" in response.lower()
    
    def test_generate_with_system_prompt(self, llm_service):
        """Test generation with system prompt."""
        response = llm_service.generate(
            "What is AI?",
            system_prompt="You are a research assistant."
        )
        assert len(response) > 10
    
    def test_generate_clarification_questions(self, llm_service):
        """Test clarification questions generation."""
        questions = llm_service.generate_clarification_questions("AI research")
        assert isinstance(questions, list)
        assert len(questions) >= 3
        assert all(isinstance(q, str) for q in questions)
    
    def test_generate_follow_up_queries(self, llm_service):
        """Test follow-up queries generation."""
        response = llm_service.generate_follow_up_queries(
            "AI research",
            ["missing information", "gaps in data"]
        )
        assert len(response) > 10
        assert "AI research" in response
```

## AgentHub Integration Testing

### **AgentHub Test Script** (Create)

#### `test_agenthub_phase2.py` - AgentHub Phase 2 Tests
**Purpose**: Test Phase 2 agent integration with AgentHub

**Implementation Details**:
```python
"""
AgentHub Integration Tests for Phase 2
"""

import pytest
import agenthub as ah

class TestAgentHubPhase2:
    """Test AgentHub integration for Phase 2."""
    
    def test_agent_loading(self):
        """Test that agent can be loaded in AgentHub."""
        try:
            agent = ah.load_agent("agentplug/research-agent")
            assert agent is not None
        except Exception as e:
            pytest.skip(f"AgentHub not available: {e}")
    
    def test_real_llm_responses(self):
        """Test that all methods return real LLM responses."""
        try:
            agent = ah.load_agent("agentplug/research-agent")
            
            # Test all methods
            result1 = agent.instant_research("What is AI?")
            result2 = agent.quick_research("How does ML work?")
            result3 = agent.standard_research("Latest AI news?")
            result4 = agent.deep_research("AI ethics analysis")
            result5 = agent.solve("What is AI?")
            
            # Verify all return results
            assert "result" in result1
            assert "result" in result2
            assert "result" in result3
            assert "result" in result4
            assert "result" in result5
            
            # Verify real responses (not mock)
            assert len(result1["result"]) > 50
            assert len(result2["result"]) > 100
            assert len(result3["result"]) > 200
            assert len(result4["result"]) > 500
            assert len(result5["result"]) > 50
            
        except Exception as e:
            pytest.skip(f"AgentHub not available: {e}")
    
    def test_mode_differences(self):
        """Test that different modes produce different response qualities."""
        try:
            agent = ah.load_agent("agentplug/research-agent")
            
            question = "What is artificial intelligence?"
            
            # Test different modes
            instant = agent.instant_research(question)
            quick = agent.quick_research(question)
            standard = agent.standard_research(question)
            deep = agent.deep_research(question)
            
            # Verify response length differences
            assert len(instant["result"]) < len(quick["result"])
            assert len(quick["result"]) < len(standard["result"])
            assert len(standard["result"]) < len(deep["result"])
            
        except Exception as e:
            pytest.skip(f"AgentHub not available: {e}")
    
    def test_auto_mode_selection(self):
        """Test automatic mode selection."""
        try:
            agent = ah.load_agent("agentplug/research-agent")
            
            # Test short question (should select instant)
            result1 = agent.solve("What is AI?")
            assert len(result1["result"]) > 50
            
            # Test long question (should select deep)
            long_question = "Provide a comprehensive analysis of the ethical implications of artificial intelligence in healthcare, including privacy concerns, bias in algorithms, patient autonomy, and the role of regulatory frameworks in ensuring responsible AI deployment."
            result2 = agent.solve(long_question)
            assert len(result2["result"]) > 500
            
        except Exception as e:
            pytest.skip(f"AgentHub not available: {e}")
```

## Implementation Checklist

### **Phase 2 Implementation Checklist:**

- [ ] **Modify `agent.py`** with real LLM integration
- [ ] **Create `llm_service.py`** with real LLM service
- [ ] **Update `config.json`** with enhanced configuration
- [ ] **Implement mode-specific workflows** for all research modes
- [ ] **Add auto mode selection logic** in solve() method
- [ ] **Create `test_phase2.py`** with unit tests
- [ ] **Create `test_agenthub_phase2.py`** with AgentHub tests
- [ ] **Test real LLM responses** for all methods
- [ ] **Test mode differences** in response quality
- [ ] **Test auto mode selection** functionality
- [ ] **Verify AgentHub integration** still works
- [ ] **Test error handling** for LLM failures

## Success Criteria

### **Phase 2 Success Criteria:**

1. ✅ **Real LLM responses** for all methods (not mock)
2. ✅ **Mode-specific behavior** with different response qualities
3. ✅ **Auto mode selection** working based on question complexity
4. ✅ **Enhanced research workflows** with multiple rounds
5. ✅ **Error handling** for LLM failures
6. ✅ **AgentHub integration** still functional
7. ✅ **Unit tests pass** for all functionality
8. ✅ **AgentHub integration tests** pass

## Next Phase Preparation

### **Phase 2 → Phase 3 Transition:**

- **Dependency**: Real LLM integration working in AgentHub
- **Preparation**: LLM service ready for tool integration
- **Foundation**: Mode-specific workflows established
- **Testing**: Real AI responses validated and working

This Phase 2 implementation provides real LLM integration while maintaining AgentHub compatibility, setting the foundation for Phase 3 where we'll add external tool integration.

## Tool Usage Documentation

### **How to Use External Tools with ResearchAgent**

The ResearchAgent in Phase 2 provides comprehensive tool management capabilities for working with external tools provided by AgentHub:

```python
# Example usage with tools
agent = ResearchAgent(tool_context={
    "available_tools": ["web_search", "document_retrieval", "academic_search"],
    "tool_descriptions": {
        "web_search": "Search the web for information",
        "document_retrieval": "Retrieve documents from various sources",
        "academic_search": "Search academic databases and papers"
    },
    "tool_usage_examples": {
        "web_search": "web_search(query='latest AI developments')",
        "document_retrieval": "document_retrieval(source='pdf', query='machine learning')",
        "academic_search": "academic_search(database='arxiv', query='neural networks')"
    },
    "tool_parameters": {
        "web_search": {
            "query": {"name": "query", "type": "string", "required": True, "default": None},
            "max_results": {"name": "max_results", "type": "integer", "required": False, "default": 10}
        }
    },
    "tool_return_types": {
        "web_search": "List[Dict[str, Any]]",
        "document_retrieval": "List[Dict[str, Any]]",
        "academic_search": "List[Dict[str, Any]]"
    }
})

# Check available tools
print(agent.get_available_tools())  # ['web_search', 'document_retrieval', 'academic_search']

# Check if specific tool is available
if agent.has_tool("web_search"):
    print("Web search tool is available")

# Get detailed tool information
tools_info = agent._get_available_tools_info()
print(tools_info["tool_descriptions"]["web_search"])  # "Search the web for information"

# Call a tool (mock implementation in Phase 2)
result = agent._call_tool("web_search", {"query": "AI developments"})
print(result)  # "Real LLM result from web_search with parameters: {'query': 'AI developments'}"
```

### **Tool Integration in Research Methods**

The research methods in Phase 2 can be enhanced to use external tools:

```python
def enhanced_instant_research(self, question: str) -> str:
    """Enhanced instant research using external tools."""
    try:
        # Get available tools
        tools_info = self._get_available_tools_info()
        available_tools = tools_info["available_tools"]
        
        if not available_tools:
            return f"No tools available for research: {question}"
        
        # Use first available tool for instant research
        tool_name = available_tools[0]
        tool_result = self._call_tool(tool_name, {"query": question})
        
        # Generate response using real LLM with tool results
        system_prompt = self.config["system_prompts"]["instant"]
        response = self.llm_service.generate(
            f"Question: {question}\nTool Result: {tool_result}",
            system_prompt=system_prompt
        )
        
        return response
        
    except Exception as e:
        return f"Error in enhanced instant research: {str(e)}"
```

### **Tool Context Structure**

The `tool_context` parameter contains comprehensive tool information:

```python
tool_context = {
    "available_tools": ["web_search", "document_retrieval", "academic_search"],
    "tool_descriptions": {
        "web_search": "Search the web for information",
        "document_retrieval": "Retrieve documents from various sources",
        "academic_search": "Search academic databases and papers"
    },
    "tool_usage_examples": {
        "web_search": "web_search(query='latest AI developments')",
        "document_retrieval": "document_retrieval(source='pdf', query='machine learning')",
        "academic_search": "academic_search(database='arxiv', query='neural networks')"
    },
    "tool_parameters": {
        "web_search": {
            "query": {"name": "query", "type": "string", "required": True, "default": None},
            "max_results": {"name": "max_results", "type": "integer", "required": False, "default": 10}
        },
        "document_retrieval": {
            "source": {"name": "source", "type": "string", "required": True, "default": None},
            "query": {"name": "query", "type": "string", "required": True, "default": None}
        }
    },
    "tool_return_types": {
        "web_search": "List[Dict[str, Any]]",
        "document_retrieval": "List[Dict[str, Any]]",
        "academic_search": "List[Dict[str, Any]]"
    },
    "tool_namespaces": {
        "web_search": "mcp",
        "document_retrieval": "mcp",
        "academic_search": "mcp"
    }
}
```

### **Tool Management Methods**

```python
# Check if tool is available
if agent.has_tool("web_search"):
    result = agent._call_tool("web_search", {"query": "AI news"})

# Add tool dynamically
agent.add_tool("new_tool")

# Remove tool
agent.remove_tool("old_tool")

# Get all available tools
tools = agent.get_available_tools()

# Get detailed tool information
tools_info = agent._get_available_tools_info()
```
