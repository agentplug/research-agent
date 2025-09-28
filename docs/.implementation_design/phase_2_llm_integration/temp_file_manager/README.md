# Temp File Manager Module - Phase 2

## Overview

This module implements temporary file management for Phase 2, providing organized storage for research data, intermediate results, and automatic cleanup functionality.

## Module Structure

```
research_agent/utils/
├── file_manager.py            # Main TempFileManager class
├── data_models.py             # Data models for file management
└── utils.py                   # Enhanced utilities (from Phase 1)
```

## Key Components

### 1. Temp File Manager (`file_manager.py`)

Main temporary file management class:

```python
import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class TempFileManager:
    """Manage temporary files for research data."""

    def __init__(self, base_dir: str = "/tmp/research_agent"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self.session_dir = None
        self.file_registry = {}  # Track created files

    def create_session(self, session_id: str) -> Path:
        """Create session-specific directory."""
        self.session_dir = self.base_dir / session_id
        self.session_dir.mkdir(exist_ok=True)

        # Create subdirectories for organization
        (self.session_dir / "research_data").mkdir(exist_ok=True)
        (self.session_dir / "intermediate_results").mkdir(exist_ok=True)
        (self.session_dir / "cache").mkdir(exist_ok=True)
        (self.session_dir / "logs").mkdir(exist_ok=True)

        return self.session_dir

    def save_research_data(self, data: Dict[str, Any], filename: str) -> Path:
        """Save research data to temporary file."""
        if not self.session_dir:
            raise ValueError("No active session")

        file_path = self.session_dir / "research_data" / filename

        # Add metadata
        enhanced_data = {
            'data': data,
            'metadata': {
                'created_at': datetime.utcnow().isoformat(),
                'session_id': self.session_dir.name,
                'file_type': 'research_data',
                'size_bytes': len(json.dumps(data))
            }
        }

        with open(file_path, 'w') as f:
            json.dump(enhanced_data, f, indent=2)

        # Register file
        self.file_registry[str(file_path)] = {
            'path': str(file_path),
            'type': 'research_data',
            'created_at': datetime.utcnow().isoformat(),
            'size_bytes': file_path.stat().st_size
        }

        return file_path

    def save_intermediate_result(self, result: Any, filename: str) -> Path:
        """Save intermediate research result."""
        if not self.session_dir:
            raise ValueError("No active session")

        file_path = self.session_dir / "intermediate_results" / filename

        # Handle different data types
        if isinstance(result, dict):
            with open(file_path, 'w') as f:
                json.dump(result, f, indent=2)
        elif isinstance(result, str):
            with open(file_path, 'w') as f:
                f.write(result)
        else:
            # Serialize other types
            with open(file_path, 'w') as f:
                json.dump(str(result), f)

        # Register file
        self.file_registry[str(file_path)] = {
            'path': str(file_path),
            'type': 'intermediate_result',
            'created_at': datetime.utcnow().isoformat(),
            'size_bytes': file_path.stat().st_size
        }

        return file_path

    def load_research_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load research data from temporary file."""
        if not self.session_dir:
            return None

        file_path = self.session_dir / "research_data" / filename

        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data.get('data')
        except Exception:
            return None

    def cleanup_session(self, session_id: str):
        """Clean up session files."""
        session_path = self.base_dir / session_id
        if session_path.exists():
            shutil.rmtree(session_path)

        # Remove from registry
        files_to_remove = [
            path for path in self.file_registry.keys()
            if session_id in path
        ]
        for path in files_to_remove:
            del self.file_registry[path]

    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up sessions older than specified hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

        for session_dir in self.base_dir.iterdir():
            if session_dir.is_dir():
                # Check if session is old
                session_time = datetime.fromtimestamp(session_dir.stat().st_mtime)
                if session_time < cutoff_time:
                    shutil.rmtree(session_dir)

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session."""
        session_path = self.base_dir / session_id

        if not session_path.exists():
            return None

        # Count files by type
        file_counts = {
            'research_data': len(list((session_path / "research_data").glob("*"))),
            'intermediate_results': len(list((session_path / "intermediate_results").glob("*"))),
            'cache': len(list((session_path / "cache").glob("*"))),
            'logs': len(list((session_path / "logs").glob("*")))
        }

        # Calculate total size
        total_size = sum(
            f.stat().st_size
            for f in session_path.rglob("*")
            if f.is_file()
        )

        return {
            'session_id': session_id,
            'created_at': datetime.fromtimestamp(session_path.stat().st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(session_path.stat().st_mtime).isoformat(),
            'file_counts': file_counts,
            'total_size_bytes': total_size,
            'path': str(session_path)
        }
```

### 2. Data Models (`data_models.py`)

Data classes for file management:

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime

@dataclass
class FileInfo:
    """Information about a temporary file."""
    path: str
    file_type: str
    created_at: str
    size_bytes: int
    session_id: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SessionInfo:
    """Information about a research session."""
    session_id: str
    created_at: str
    modified_at: str
    file_counts: Dict[str, int]
    total_size_bytes: int
    path: str
    status: str = "active"  # active, completed, error

@dataclass
class ResearchData:
    """Structured research data."""
    query: str
    mode: str
    response: str
    sources: List[str]
    metadata: Dict[str, Any]
    created_at: str
    session_id: str

@dataclass
class IntermediateResult:
    """Intermediate research result."""
    round_number: int
    query: str
    result: Any
    sources_used: List[str]
    metadata: Dict[str, Any]
    created_at: str
```

### 3. Cache Management

#### Research Cache
```python
class ResearchCache:
    """Cache for research results to avoid duplicate work."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_index = {}  # query -> cache_file mapping

    def get_cache_key(self, query: str, mode: str) -> str:
        """Generate cache key for query and mode."""
        import hashlib
        key_string = f"{query}:{mode}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def get_cached_result(self, query: str, mode: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available."""
        cache_key = self.get_cache_key(query, mode)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return None

        return None

    def cache_result(self, query: str, mode: str, result: Dict[str, Any]):
        """Cache research result."""
        cache_key = self.get_cache_key(query, mode)
        cache_file = self.cache_dir / f"{cache_key}.json"

        cache_data = {
            'query': query,
            'mode': mode,
            'result': result,
            'cached_at': datetime.utcnow().isoformat(),
            'cache_key': cache_key
        }

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)

        self.cache_index[f"{query}:{mode}"] = str(cache_file)

    def cleanup_cache(self, max_age_hours: int = 48):
        """Clean up old cache files."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

        for cache_file in self.cache_dir.glob("*.json"):
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if file_time < cutoff_time:
                cache_file.unlink()
```

### 4. Integration with Research Workflows

#### Enhanced Workflow Integration
```python
class BaseWorkflow:
    """Base workflow with file management integration."""

    def __init__(self, llm_service, temp_file_manager: TempFileManager):
        self.llm_service = llm_service
        self.temp_file_manager = temp_file_manager
        self.cache = ResearchCache(self.temp_file_manager.session_dir / "cache")

    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute workflow with file management."""
        # Check cache first
        cached_result = self.cache.get_cached_result(query, self.mode)
        if cached_result:
            return cached_result['result']

        # Execute research
        result = self._execute_research(query, context)

        # Save intermediate results
        self._save_intermediate_results(query, result)

        # Cache result
        self.cache.cache_result(query, self.mode, result)

        return result

    def _save_intermediate_results(self, query: str, result: Dict[str, Any]):
        """Save intermediate results to files."""
        # Save research data
        research_data = {
            'query': query,
            'mode': self.mode,
            'response': result.get('data', {}).get('content', ''),
            'sources': result.get('data', {}).get('sources', []),
            'metadata': result.get('data', {}).get('metadata', {})
        }

        filename = f"research_{self.mode}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        self.temp_file_manager.save_research_data(research_data, filename)
```

## Testing Strategy

### Unit Tests
```python
class TestTempFileManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path("/tmp/test_research_agent")
        self.manager = TempFileManager(str(self.temp_dir))

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_session_creation(self):
        """Test session creation and directory structure."""
        session_id = "test_session_123"
        session_path = self.manager.create_session(session_id)

        self.assertTrue(session_path.exists())
        self.assertTrue((session_path / "research_data").exists())
        self.assertTrue((session_path / "intermediate_results").exists())
        self.assertTrue((session_path / "cache").exists())
        self.assertTrue((session_path / "logs").exists())

    def test_data_saving_and_loading(self):
        """Test saving and loading research data."""
        session_id = "test_session_456"
        self.manager.create_session(session_id)

        test_data = {
            'query': 'What is AI?',
            'response': 'AI is artificial intelligence',
            'sources': ['https://example.com']
        }

        # Save data
        file_path = self.manager.save_research_data(test_data, "test_data.json")
        self.assertTrue(file_path.exists())

        # Load data
        loaded_data = self.manager.load_research_data("test_data.json")
        self.assertEqual(loaded_data, test_data)

    def test_session_cleanup(self):
        """Test session cleanup."""
        session_id = "test_session_789"
        self.manager.create_session(session_id)

        # Add some data
        self.manager.save_research_data({'test': 'data'}, "test.json")

        # Cleanup
        self.manager.cleanup_session(session_id)

        # Verify cleanup
        session_path = self.temp_dir / session_id
        self.assertFalse(session_path.exists())

    def test_old_session_cleanup(self):
        """Test cleanup of old sessions."""
        # Create old session (mock old timestamp)
        old_session = self.temp_dir / "old_session"
        old_session.mkdir(exist_ok=True)

        # Mock old timestamp
        old_time = datetime.utcnow().timestamp() - (25 * 3600)  # 25 hours ago
        os.utime(old_session, (old_time, old_time))

        # Cleanup old sessions
        self.manager.cleanup_old_sessions(max_age_hours=24)

        # Verify old session is removed
        self.assertFalse(old_session.exists())
```

### Integration Tests
- Test with research workflows
- Test cache functionality
- Test file organization and cleanup
- Test error handling and recovery

## Configuration

### config.json Updates
```json
{
  "temp_file_management": {
    "enabled": true,
    "base_directory": "/tmp/research_agent",
    "auto_cleanup": true,
    "max_session_age_hours": 24,
    "max_cache_age_hours": 48,
    "max_file_size_mb": 100,
    "organization": {
      "research_data": "research_data/",
      "intermediate_results": "intermediate_results/",
      "cache": "cache/",
      "logs": "logs/"
    }
  }
}
```

## Success Criteria

- [ ] Session-based file organization works correctly
- [ ] Research data is saved and loaded properly
- [ ] Intermediate results are tracked and managed
- [ ] Cache functionality improves performance
- [ ] Automatic cleanup removes old files
- [ ] Integration with research workflows works seamlessly
- [ ] File metadata provides useful information
- [ ] Error handling manages file operations gracefully

## Implementation Order

1. **Create TempFileManager class with basic functionality**
2. **Implement data models and file organization**
3. **Add cache management functionality**
4. **Integrate with research workflows**
5. **Update configuration**
6. **Write comprehensive tests**
7. **Test with various file types and sizes**
8. **Update documentation and examples**
