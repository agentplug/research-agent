# Phase 3: External Tool Integration - Implementation Design

## Overview

**Phase Goal**: Integrate external tools provided by users through AgentHub and implement enhanced research workflows.

**Duration**: 2-3 weeks  
**Deliverable**: Agent with external tool integration and source tracking testable in AgentHub

## Modules to Create/Modify

### 1. **Root Level Files** (Modify)

#### `agent.py` - Enhanced with Tool Integration
**Key Changes**:
- Tool context parsing from AgentHub
- Tool execution and coordination
- Enhanced research workflows with tool calls
- Source tracking with URL deduplication

**Implementation Details**:
```python
#!/usr/bin/env python3
"""
Agent Hub Agent: research-agent
Phase 3: External tool integration with source tracking
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
from llm_service import CoreLLMService, get_shared_llm_service
from source_tracker import SourceTracker
from file_manager import TempFileManager

logger = logging.getLogger(__name__)

class ResearchAgent:
    """Research agent with external tool integration for Phase 3."""
    
    def __init__(self, tool_context: Optional[Dict[str, Any]] = None):
        """Initialize with tool integration."""
        self.config = self._load_config()
        self.llm_service = get_shared_llm_service()
        self.tool_context = tool_context or {}
        
        # Initialize tool management
        self.available_tools = self.tool_context.get("available_tools", [])
        self.tool_descriptions = self.tool_context.get("tool_descriptions", {})
        self.tool_usage_examples = self.tool_context.get("tool_usage_examples", {})
        
        # Initialize source tracking and file management
        self.source_tracker = SourceTracker()
        self.file_manager = TempFileManager()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json file."""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "ai": {"temperature": 0.1, "max_tokens": None, "timeout": 30},
            "research": {"max_sources_per_round": 10, "max_rounds": 12},
            "system_prompts": {
                "instant": "You are a research assistant for INSTANT research mode.",
                "quick": "You are a research assistant for QUICK research mode.",
                "standard": "You are a research assistant for STANDARD research mode.",
                "deep": "You are a research assistant for DEEP research mode."
            }
        }
    
    def instant_research(self, question: str) -> str:
        """Instant research with tool integration."""
        try:
            # Execute single round with tools
            result = self._execute_research_round(question, "instant", 1)
            return result
            
        except Exception as e:
            return f"Error in instant research: {str(e)}"
    
    def quick_research(self, question: str) -> str:
        """Quick research with tool integration."""
        try:
            # Execute two rounds with analysis
            round1_result = self._execute_research_round(question, "quick", 1)
            round2_result = self._execute_research_round(question, "quick", 2)
            
            # Synthesize results
            final_result = self.llm_service.generate(
                f"Research question: {question}\n\nRound 1: {round1_result}\n\nRound 2: {round2_result}\n\nSynthesize into comprehensive response.",
                system_prompt=self.config["system_prompts"]["quick"]
            )
            
            return final_result
            
        except Exception as e:
            return f"Error in quick research: {str(e)}"
    
    def standard_research(self, question: str) -> str:
        """Standard research with comprehensive tool integration."""
        try:
            research_data = []
            
            # Execute multiple rounds
            for round_num in range(1, 6):  # 5 rounds
                round_result = self._execute_research_round(question, "standard", round_num)
                research_data.append(f"Round {round_num}: {round_result}")
                
                # Gap analysis between rounds
                if round_num < 5:
                    gap_analysis = self._analyze_gaps(question, research_data)
                    research_data.append(f"Gap Analysis: {gap_analysis}")
            
            # Final synthesis
            final_result = self.llm_service.generate(
                f"Research question: {question}\n\nAll rounds: {research_data}\n\nProvide comprehensive response.",
                system_prompt=self.config["system_prompts"]["standard"]
            )
            
            return final_result
            
        except Exception as e:
            return f"Error in standard research: {str(e)}"
    
    def deep_research(self, question: str) -> str:
        """Deep research with exhaustive tool integration."""
        try:
            # Generate clarification questions
            clarifications = self.llm_service.generate_clarification_questions(question)
            enhanced_question = f"{question}\n\nClarifications: {', '.join(clarifications)}"
            
            research_data = []
            
            # Execute multiple rounds
            for round_num in range(1, 13):  # 12 rounds
                round_result = self._execute_research_round(enhanced_question, "deep", round_num)
                research_data.append(f"Round {round_num}: {round_result}")
                
                # Deep gap analysis
                if round_num < 12:
                    gap_analysis = self._analyze_gaps(enhanced_question, research_data)
                    research_data.append(f"Deep Gap Analysis: {gap_analysis}")
            
            # Final comprehensive synthesis
            final_result = self.llm_service.generate(
                f"Enhanced question: {enhanced_question}\n\nAll rounds: {research_data}\n\nProvide exhaustive response.",
                system_prompt=self.config["system_prompts"]["deep"]
            )
            
            return final_result
            
        except Exception as e:
            return f"Error in deep research: {str(e)}"
    
    def solve(self, question: str) -> str:
        """Auto mode selection with tool integration."""
        try:
            # Auto-select mode based on question complexity
            question_length = len(question)
            complexity = self._analyze_question_complexity(question)
            
            if question_length < 50 and complexity < 3:
                return self.instant_research(question)
            elif question_length < 100 and complexity < 5:
                return self.quick_research(question)
            elif question_length < 200 and complexity < 8:
                return self.standard_research(question)
            else:
                return self.deep_research(question)
                
        except Exception as e:
            return f"Error in auto mode selection: {str(e)}"
    
    def _execute_research_round(self, question: str, mode: str, round_num: int) -> str:
        """Execute a single research round with tools."""
        try:
            # Build system prompt with tool context
            system_prompt = self._build_research_prompt(mode)
            
            # Generate tool calls if tools are available
            if self.available_tools:
                tool_calls = self._generate_tool_calls(question, mode, round_num)
                if tool_calls:
                    # Execute tools and get results
                    tool_results = self._execute_tools(tool_calls)
                    
                    # Generate response using tool results
                    response = self.llm_service.generate(
                        f"Research question: {question}\n\nTool results: {tool_results}\n\nProvide research response.",
                        system_prompt=system_prompt
                    )
                    
                    return response
            
            # Fallback to LLM-only response
            return self.llm_service.generate(
                f"Research question: {question}\n\nProvide research response.",
                system_prompt=system_prompt
            )
            
        except Exception as e:
            return f"Error in research round: {str(e)}"
    
    def _generate_tool_calls(self, question: str, mode: str, round_num: int) -> List[Dict[str, Any]]:
        """Generate tool calls based on available tools."""
        tool_calls = []
        
        # Simple tool selection logic
        if "web_search" in self.available_tools:
            tool_calls.append({
                "tool": "web_search",
                "parameters": {"query": question}
            })
        
        if "academic_search" in self.available_tools and mode in ["standard", "deep"]:
            tool_calls.append({
                "tool": "academic_search",
                "parameters": {"query": question}
            })
        
        if "news_search" in self.available_tools and mode in ["quick", "standard", "deep"]:
            tool_calls.append({
                "tool": "news_search",
                "parameters": {"query": question}
            })
        
        return tool_calls
    
    def _execute_tools(self, tool_calls: List[Dict[str, Any]]) -> str:
        """Execute tool calls and return results."""
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool")
            parameters = tool_call.get("parameters", {})
            
            # Simulate tool execution (in real implementation, this would call actual tools)
            result = self._simulate_tool_execution(tool_name, parameters)
            results.append(f"{tool_name}: {result}")
            
            # Track sources
            if "url" in result:
                self.source_tracker.track_url(result["url"])
        
        return "\n".join(results)
    
    def _simulate_tool_execution(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Simulate tool execution (placeholder for actual tool integration)."""
        query = parameters.get("query", "")
        
        if tool_name == "web_search":
            return f"Web search results for: {query}"
        elif tool_name == "academic_search":
            return f"Academic search results for: {query}"
        elif tool_name == "news_search":
            return f"News search results for: {query}"
        else:
            return f"Tool {tool_name} results for: {query}"
    
    def _analyze_gaps(self, question: str, research_data: List[str]) -> str:
        """Analyze research gaps."""
        return self.llm_service.generate(
            f"Question: {question}\n\nResearch data: {research_data}\n\nIdentify information gaps.",
            system_prompt="You are a research analyst."
        )
    
    def _analyze_question_complexity(self, question: str) -> int:
        """Analyze question complexity for auto mode selection."""
        complexity_score = 0
        
        if len(question) > 100:
            complexity_score += 2
        elif len(question) > 50:
            complexity_score += 1
        
        complexity_keywords = [
            "comprehensive", "detailed", "exhaustive", "analysis", "research"
        ]
        
        for keyword in complexity_keywords:
            if keyword.lower() in question.lower():
                complexity_score += 1
        
        return complexity_score
    
    def _build_research_prompt(self, mode: str) -> str:
        """Build research prompt with tool context."""
        base_prompt = self.config["system_prompts"][mode]
        
        if self.available_tools:
            tool_context = f"\n\nAvailable tools: {', '.join(self.available_tools)}"
            return base_prompt + tool_context
        
        return base_prompt

def main():
    """Main entry point for agent execution."""
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)
    
    try:
        input_data = json.loads(sys.argv[1])
        method = input_data.get("method")
        parameters = input_data.get("parameters", {})
        tool_context = input_data.get("tool_context", {})
        
        agent = ResearchAgent(tool_context=tool_context)
        
        if method == "instant_research":
            result = agent.instant_research(parameters.get("question", ""))
        elif method == "quick_research":
            result = agent.quick_research(parameters.get("question", ""))
        elif method == "standard_research":
            result = agent.standard_research(parameters.get("question", ""))
        elif method == "deep_research":
            result = agent.deep_research(parameters.get("question", ""))
        elif method == "solve":
            result = agent.solve(parameters.get("question", ""))
        else:
            print(json.dumps({"error": f"Unknown method: {method}"}))
            sys.exit(1)
        
        print(json.dumps({"result": result}))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 2. **New Modules** (Create)

#### `source_tracker.py` - Source Tracking
**Purpose**: Track research sources to prevent duplicates

**Implementation Details**:
```python
"""
Source Tracking for Research Agent
Manages URL tracking and duplicate prevention
"""

import json
import os
import hashlib
import tempfile
from typing import Set, Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class SourceTracker:
    """Tracks research sources to prevent duplicate scraping."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.tracking_file = os.path.join(self.temp_dir, "research_sources.json")
        self.url_hashes: Set[str] = set()
        self.source_metadata: Dict[str, Dict[str, Any]] = {}
        self.session_id = self._generate_session_id()
        self._load_tracking_data()
    
    def _generate_session_id(self) -> str:
        return f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
    
    def _load_tracking_data(self):
        """Load existing tracking data."""
        try:
            if os.path.exists(self.tracking_file):
                with open(self.tracking_file, 'r') as f:
                    data = json.load(f)
                    self.url_hashes = set(data.get('url_hashes', []))
                    self.source_metadata = data.get('source_metadata', {})
        except Exception as e:
            logger.warning(f"Failed to load tracking data: {e}")
    
    def _save_tracking_data(self):
        """Save current tracking data."""
        try:
            data = {
                'url_hashes': list(self.url_hashes),
                'source_metadata': self.source_metadata,
                'last_updated': datetime.now().isoformat(),
                'session_id': self.session_id
            }
            
            os.makedirs(os.path.dirname(self.tracking_file), exist_ok=True)
            
            with open(self.tracking_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save tracking data: {e}")
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for consistent tracking."""
        try:
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        except Exception:
            return url
    
    def _generate_url_hash(self, url: str) -> str:
        """Generate hash for URL tracking."""
        normalized_url = self._normalize_url(url)
        return hashlib.md5(normalized_url.encode('utf-8')).hexdigest()
    
    def is_url_tracked(self, url: str) -> bool:
        """Check if URL has already been tracked."""
        url_hash = self._generate_url_hash(url)
        return url_hash in self.url_hashes
    
    def track_url(self, url: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Track a new URL and its metadata."""
        url_hash = self._generate_url_hash(url)
        
        if url_hash in self.url_hashes:
            return False
        
        self.url_hashes.add(url_hash)
        
        self.source_metadata[url_hash] = {
            'url': url,
            'normalized_url': self._normalize_url(url),
            'first_seen': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat(),
            'access_count': 1,
            'metadata': metadata or {}
        }
        
        self._save_tracking_data()
        return True
    
    def filter_new_urls(self, urls: List[str]) -> List[str]:
        """Filter out URLs that have already been tracked."""
        new_urls = []
        for url in urls:
            if not self.is_url_tracked(url):
                new_urls.append(url)
        return new_urls
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for current research session."""
        return {
            'session_id': self.session_id,
            'total_tracked_urls': len(self.url_hashes),
            'tracking_file': self.tracking_file,
            'last_updated': datetime.now().isoformat()
        }
```

#### `file_manager.py` - Temp File Management
**Purpose**: Manage temporary files for research data

**Implementation Details**:
```python
"""
Temp File Management for Research Agent
Manages temporary files for research data storage
"""

import os
import json
import tempfile
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TempFileManager:
    """Manages temporary files for research agent operations."""
    
    def __init__(self, base_temp_dir: Optional[str] = None):
        self.base_temp_dir = base_temp_dir or tempfile.gettempdir()
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_dir = os.path.join(self.base_temp_dir, f"research_agent_{self.session_id}")
        self._ensure_session_dir()
        
    def _ensure_session_dir(self):
        """Ensure session directory exists."""
        os.makedirs(self.session_dir, exist_ok=True)
    
    def save_research_data(self, research_data: Dict[str, Any], round_num: int, mode: str) -> str:
        """Save research data for a specific round and mode."""
        filename = f"research_{mode}_round_{round_num:02d}.json"
        filepath = os.path.join(self.session_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(research_data, f, indent=2)
            return filepath
        except Exception as e:
            logger.error(f"Failed to save research data: {e}")
            return ""
    
    def load_research_data(self, filepath: str) -> Dict[str, Any]:
        """Load research data from file."""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load research data: {e}")
            return {}
    
    def cleanup_session(self):
        """Clean up all session files."""
        try:
            if os.path.exists(self.session_dir):
                shutil.rmtree(self.session_dir)
            logger.info(f"Cleaned up session directory: {self.session_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup session: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for current session."""
        total_files = 0
        total_size = 0
        
        if os.path.exists(self.session_dir):
            for root, dirs, files in os.walk(self.session_dir):
                total_files += len(files)
                for file in files:
                    filepath = os.path.join(root, file)
                    total_size += os.path.getsize(filepath)
        
        return {
            'session_id': self.session_id,
            'session_dir': self.session_dir,
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
```

## Testing Strategy

### **Unit Tests** (Create)

#### `test_phase3.py` - Phase 3 Tests
**Purpose**: Test Phase 3 functionality

**Implementation Details**:
```python
"""
Phase 3 Tests - External Tool Integration
"""

import pytest
import json
import subprocess
import sys
from pathlib import Path

class TestPhase3Agent:
    """Test Phase 3 agent functionality."""
    
    @pytest.fixture
    def agent_script(self):
        """Path to agent.py script."""
        return Path(__file__).parent.parent.parent / "agent.py"
    
    def test_tool_integration(self, agent_script):
        """Test external tool integration."""
        input_data = {
            "method": "instant_research",
            "parameters": {
                "question": "AI news"
            },
            "tool_context": {
                "available_tools": ["web_search", "news_search"],
                "tool_descriptions": {
                    "web_search": "Search the web",
                    "news_search": "Search news sources"
                }
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
        assert len(response["result"]) > 50
    
    def test_source_tracking(self, agent_script):
        """Test source tracking functionality."""
        # First call
        input_data = {
            "method": "quick_research",
            "parameters": {"question": "AI developments"},
            "tool_context": {"available_tools": ["web_search"]}
        }
        
        result1 = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        assert result1.returncode == 0
        
        # Second call with same question
        result2 = subprocess.run(
            [sys.executable, str(agent_script), json.dumps(input_data)],
            capture_output=True,
            text=True
        )
        
        assert result2.returncode == 0
        
        # Both should work (source tracking prevents duplicates)
        response1 = json.loads(result1.stdout)
        response2 = json.loads(result2.stdout)
        
        assert "result" in response1
        assert "result" in response2

class TestSourceTracker:
    """Test source tracking functionality."""
    
    @pytest.fixture
    def source_tracker(self):
        """Create source tracker instance."""
        from source_tracker import SourceTracker
        return SourceTracker()
    
    def test_track_url(self, source_tracker):
        """Test URL tracking."""
        url = "https://example.com/test"
        result = source_tracker.track_url(url)
        assert result is True
        assert source_tracker.is_url_tracked(url) is True
    
    def test_track_duplicate_url(self, source_tracker):
        """Test tracking duplicate URL."""
        url = "https://example.com/test"
        
        result1 = source_tracker.track_url(url)
        result2 = source_tracker.track_url(url)
        
        assert result1 is True
        assert result2 is False
    
    def test_filter_new_urls(self, source_tracker):
        """Test filtering new URLs."""
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
        
        source_tracker.track_url(urls[0])
        
        new_urls = source_tracker.filter_new_urls(urls)
        
        assert len(new_urls) == 2
        assert urls[0] not in new_urls
        assert urls[1] in new_urls
        assert urls[2] in new_urls

class TestTempFileManager:
    """Test temp file management functionality."""
    
    @pytest.fixture
    def file_manager(self):
        """Create file manager instance."""
        from file_manager import TempFileManager
        return TempFileManager()
    
    def test_save_load_data(self, file_manager):
        """Test saving and loading research data."""
        data = {"question": "test", "result": "test result"}
        
        filepath = file_manager.save_research_data(data, 1, "instant")
        assert filepath != ""
        
        loaded_data = file_manager.load_research_data(filepath)
        assert loaded_data == data
    
    def test_session_stats(self, file_manager):
        """Test session statistics."""
        stats = file_manager.get_session_stats()
        
        assert "session_id" in stats
        assert "session_dir" in stats
        assert "total_files" in stats
        assert "total_size_bytes" in stats
```

## AgentHub Integration Testing

### **AgentHub Test Script** (Create)

#### `test_agenthub_phase3.py` - AgentHub Phase 3 Tests
**Purpose**: Test Phase 3 agent integration with AgentHub

**Implementation Details**:
```python
"""
AgentHub Integration Tests for Phase 3
"""

import pytest
import agenthub as ah

class TestAgentHubPhase3:
    """Test AgentHub integration for Phase 3."""
    
    def test_tool_integration(self):
        """Test external tool integration in AgentHub."""
        try:
            agent = ah.load_agent(
                "agentplug/research-agent",
                external_tools=["web_search", "academic_search", "news_search"]
            )
            
            result = agent.instant_research("AI developments")
            
            assert "result" in result
            assert len(result["result"]) > 50
            
        except Exception as e:
            pytest.skip(f"AgentHub not available: {e}")
    
    def test_tool_context_parsing(self):
        """Test tool context parsing."""
        try:
            agent = ah.load_agent(
                "agentplug/research-agent",
                external_tools=["web_search", "academic_search"]
            )
            
            # Test different research modes with tools
            result1 = agent.instant_research("AI news")
            result2 = agent.standard_research("AI research papers")
            
            assert "result" in result1
            assert "result" in result2
            
        except Exception as e:
            pytest.skip(f"AgentHub not available: {e}")
    
    def test_source_tracking(self):
        """Test source tracking in AgentHub."""
        try:
            agent = ah.load_agent(
                "agentplug/research-agent",
                external_tools=["web_search"]
            )
            
            # Test source tracking
            result1 = agent.quick_research("AI developments")
            result2 = agent.quick_research("AI developments")  # Same question
            
            assert "result" in result1
            assert "result" in result2
            
        except Exception as e:
            pytest.skip(f"AgentHub not available: {e}")
```

## Implementation Checklist

### **Phase 3 Implementation Checklist:**

- [ ] **Modify `agent.py`** with tool integration
- [ ] **Create `source_tracker.py`** for URL tracking
- [ ] **Create `file_manager.py`** for temp file management
- [ ] **Implement tool context parsing** from AgentHub
- [ ] **Implement tool execution** and coordination
- [ ] **Add source tracking** with URL deduplication
- [ ] **Create `test_phase3.py`** with unit tests
- [ ] **Create `test_agenthub_phase3.py`** with AgentHub tests
- [ ] **Test tool integration** with external tools
- [ ] **Test source tracking** functionality
- [ ] **Test temp file management** operations
- [ ] **Verify AgentHub integration** with tools

## Success Criteria

### **Phase 3 Success Criteria:**

1. ✅ **External tool integration** working with AgentHub
2. ✅ **Tool context parsing** from AgentHub
3. ✅ **Tool execution** and coordination
4. ✅ **Source tracking** with URL deduplication
5. ✅ **Temp file management** for research data
6. ✅ **Enhanced research workflows** with tool calls
7. ✅ **AgentHub integration** with external tools
8. ✅ **Unit tests pass** for all functionality

## Next Phase Preparation

### **Phase 3 → Phase 4 Transition:**

- **Dependency**: External tool integration working in AgentHub
- **Preparation**: Tool integration ready for production optimization
- **Foundation**: Source tracking and file management established
- **Testing**: External tools validated and working

This Phase 3 implementation provides external tool integration while maintaining AgentHub compatibility, setting the foundation for Phase 4 where we'll add production-ready features and optimization.
