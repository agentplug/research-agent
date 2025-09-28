# Temp File Management Implementation Design

## Overview

This document provides detailed implementation design for temporary file management in the Deep Research Agent. Temp files are used for storing research data, caching results, and managing intermediate processing without requiring a database.

## Module Structure

```
src/utils/
├── file_manager.py                # Main file management implementation
├── cache_manager.py               # Caching utilities
└── data_serializer.py             # Data serialization helpers
```

## Core Implementation

### 1. File Manager (`utils/file_manager.py`)

```python
"""
Temporary File Management for Research Agent

Manages temporary files for research data storage, caching,
and intermediate processing without requiring a database.
"""

import os
import json
import tempfile
import shutil
import hashlib
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from pathlib import Path
import logging
import pickle
import gzip

logger = logging.getLogger(__name__)


class TempFileManager:
    """
    Manages temporary files for research agent operations.
    
    Features:
    - Automatic temp directory management
    - File-based caching with TTL
    - Data serialization and compression
    - Cleanup and maintenance utilities
    - Session-based file organization
    """
    
    def __init__(self, 
                 base_temp_dir: Optional[str] = None,
                 session_id: Optional[str] = None,
                 max_file_size: int = 100 * 1024 * 1024,  # 100MB
                 cleanup_interval: int = 3600):  # 1 hour
        """
        Initialize the temp file manager.
        
        Args:
            base_temp_dir: Base directory for temp files
            session_id: Session identifier for file organization
            max_file_size: Maximum file size before compression
            cleanup_interval: Cleanup interval in seconds
        """
        self.base_temp_dir = base_temp_dir or tempfile.gettempdir()
        self.session_id = session_id or self._generate_session_id()
        self.max_file_size = max_file_size
        self.cleanup_interval = cleanup_interval
        
        # Create session directory
        self.session_dir = os.path.join(
            self.base_temp_dir, 
            f"research_agent_{self.session_id}"
        )
        self._ensure_session_dir()
        
        # File tracking
        self.file_registry: Dict[str, Dict[str, Any]] = {}
        self.last_cleanup = datetime.now()
        
        logger.info(f"TempFileManager initialized for session: {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
    
    def _ensure_session_dir(self):
        """Ensure session directory exists."""
        os.makedirs(self.session_dir, exist_ok=True)
    
    def _get_file_path(self, filename: str, subdir: str = "") -> str:
        """
        Get full path for a file in the session directory.
        
        Args:
            filename: Name of the file
            subdir: Optional subdirectory
            
        Returns:
            Full file path
        """
        if subdir:
            subdir_path = os.path.join(self.session_dir, subdir)
            os.makedirs(subdir_path, exist_ok=True)
            return os.path.join(subdir_path, filename)
        else:
            return os.path.join(self.session_dir, filename)
    
    def _generate_filename(self, prefix: str, extension: str = ".json") -> str:
        """
        Generate a unique filename.
        
        Args:
            prefix: Filename prefix
            extension: File extension
            
        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime("%H%M%S_%f")
        return f"{prefix}_{timestamp}{extension}"
    
    def save_data(self, 
                  data: Any, 
                  filename: Optional[str] = None,
                  subdir: str = "",
                  compress: bool = False,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Save data to a temporary file.
        
        Args:
            data: Data to save
            filename: Optional custom filename
            subdir: Optional subdirectory
            compress: Whether to compress the file
            metadata: Optional metadata about the file
            
        Returns:
            Path to saved file
        """
        try:
            # Generate filename if not provided
            if not filename:
                extension = ".json.gz" if compress else ".json"
                filename = self._generate_filename("data", extension)
            
            filepath = self._get_file_path(filename, subdir)
            
            # Serialize data
            if isinstance(data, (dict, list)):
                serialized_data = json.dumps(data, indent=2, default=str)
            else:
                # Use pickle for complex objects
                serialized_data = pickle.dumps(data)
                filepath = filepath.replace('.json', '.pkl')
            
            # Write file
            if compress:
                with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                    f.write(serialized_data)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(serialized_data)
            
            # Register file
            self._register_file(filepath, metadata or {})
            
            logger.debug(f"Saved data to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            raise
    
    def load_data(self, filepath: str) -> Any:
        """
        Load data from a temporary file.
        
        Args:
            filepath: Path to file to load
            
        Returns:
            Loaded data
        """
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
            
            # Determine if file is compressed
            is_compressed = filepath.endswith('.gz')
            is_pickle = filepath.endswith('.pkl') or filepath.endswith('.pkl.gz')
            
            # Read file
            if is_compressed:
                with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                    content = f.read()
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Deserialize data
            if is_pickle:
                data = pickle.loads(content.encode('utf-8'))
            else:
                data = json.loads(content)
            
            # Update access time
            self._update_file_access(filepath)
            
            logger.debug(f"Loaded data from: {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load data from {filepath}: {e}")
            raise
    
    def save_research_data(self, 
                          research_data: Dict[str, Any],
                          round_num: int,
                          mode: str) -> str:
        """
        Save research data for a specific round and mode.
        
        Args:
            research_data: Research data to save
            round_num: Research round number
            mode: Research mode
            
        Returns:
            Path to saved file
        """
        filename = f"research_{mode}_round_{round_num:02d}.json"
        subdir = f"rounds/{mode}"
        
        metadata = {
            'round_num': round_num,
            'mode': mode,
            'timestamp': datetime.now().isoformat(),
            'data_type': 'research_data'
        }
        
        return self.save_data(research_data, filename, subdir, metadata=metadata)
    
    def save_tool_results(self, 
                         tool_results: List[Dict[str, Any]],
                         tool_name: str,
                         round_num: int) -> str:
        """
        Save tool execution results.
        
        Args:
            tool_results: Tool execution results
            tool_name: Name of the tool
            round_num: Research round number
            
        Returns:
            Path to saved file
        """
        filename = f"tool_{tool_name}_round_{round_num:02d}.json"
        subdir = f"tools/{tool_name}"
        
        metadata = {
            'tool_name': tool_name,
            'round_num': round_num,
            'timestamp': datetime.now().isoformat(),
            'data_type': 'tool_results'
        }
        
        return self.save_data(tool_results, filename, subdir, metadata=metadata)
    
    def save_analysis_results(self, 
                            analysis: Dict[str, Any],
                            analysis_type: str,
                            round_num: int) -> str:
        """
        Save analysis results.
        
        Args:
            analysis: Analysis results
            analysis_type: Type of analysis
            round_num: Research round number
            
        Returns:
            Path to saved file
        """
        filename = f"analysis_{analysis_type}_round_{round_num:02d}.json"
        subdir = f"analysis/{analysis_type}"
        
        metadata = {
            'analysis_type': analysis_type,
            'round_num': round_num,
            'timestamp': datetime.now().isoformat(),
            'data_type': 'analysis_results'
        }
        
        return self.save_data(analysis, filename, subdir, metadata=metadata)
    
    def get_session_files(self, 
                         data_type: Optional[str] = None,
                         subdir: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of files in the session.
        
        Args:
            data_type: Filter by data type
            subdir: Filter by subdirectory
            
        Returns:
            List of file information dictionaries
        """
        files = []
        
        for filepath, metadata in self.file_registry.items():
            if data_type and metadata.get('data_type') != data_type:
                continue
            
            if subdir and not filepath.startswith(os.path.join(self.session_dir, subdir)):
                continue
            
            file_info = {
                'filepath': filepath,
                'filename': os.path.basename(filepath),
                'size': os.path.getsize(filepath) if os.path.exists(filepath) else 0,
                'created': metadata.get('created'),
                'last_accessed': metadata.get('last_accessed'),
                'metadata': metadata
            }
            files.append(file_info)
        
        return files
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up files older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        removed_count = 0
        
        for filepath, metadata in list(self.file_registry.items()):
            created_time = datetime.fromisoformat(metadata.get('created', ''))
            
            if created_time < cutoff_time:
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    del self.file_registry[filepath]
                    removed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to remove file {filepath}: {e}")
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old files")
    
    def cleanup_session(self):
        """Clean up all session files."""
        try:
            if os.path.exists(self.session_dir):
                shutil.rmtree(self.session_dir)
            self.file_registry.clear()
            logger.info(f"Cleaned up session directory: {self.session_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup session: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get statistics for current session.
        
        Returns:
            Dictionary with session statistics
        """
        total_files = len(self.file_registry)
        total_size = sum(
            os.path.getsize(filepath) for filepath in self.file_registry.keys()
            if os.path.exists(filepath)
        )
        
        data_types = {}
        for metadata in self.file_registry.values():
            data_type = metadata.get('data_type', 'unknown')
            data_types[data_type] = data_types.get(data_type, 0) + 1
        
        return {
            'session_id': self.session_id,
            'session_dir': self.session_dir,
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'data_types': data_types,
            'last_cleanup': self.last_cleanup.isoformat()
        }
    
    def _register_file(self, filepath: str, metadata: Dict[str, Any]):
        """Register a file in the file registry."""
        self.file_registry[filepath] = {
            'created': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat(),
            'access_count': 1,
            **metadata
        }
    
    def _update_file_access(self, filepath: str):
        """Update file access information."""
        if filepath in self.file_registry:
            self.file_registry[filepath]['last_accessed'] = datetime.now().isoformat()
            self.file_registry[filepath]['access_count'] += 1
    
    def __del__(self):
        """Cleanup when manager is destroyed."""
        try:
            # Only cleanup if this is the main process
            if os.getpid() == os.getppid():
                self.cleanup_session()
        except Exception:
            pass  # Ignore errors during cleanup
```

### 2. Cache Manager (`utils/cache_manager.py`)

```python
"""
Cache Management for Research Agent

Provides caching functionality for research results,
tool responses, and intermediate data to improve performance.
"""

import os
import json
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages caching for research agent operations.
    
    Features:
    - TTL-based cache expiration
    - Hash-based cache keys
    - Automatic cache cleanup
    - Cache statistics and monitoring
    """
    
    def __init__(self, 
                 cache_dir: Optional[str] = None,
                 default_ttl: int = 3600):  # 1 hour
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory for cache files
            default_ttl: Default TTL in seconds
        """
        self.cache_dir = cache_dir or os.path.join(tempfile.gettempdir(), "research_cache")
        self.default_ttl = default_ttl
        self.cache_index: Dict[str, Dict[str, Any]] = {}
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load existing cache index
        self._load_cache_index()
    
    def _load_cache_index(self):
        """Load cache index from file."""
        index_file = os.path.join(self.cache_dir, "cache_index.json")
        try:
            if os.path.exists(index_file):
                with open(index_file, 'r') as f:
                    self.cache_index = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache index: {e}")
            self.cache_index = {}
    
    def _save_cache_index(self):
        """Save cache index to file."""
        index_file = os.path.join(self.cache_dir, "cache_index.json")
        try:
            with open(index_file, 'w') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")
    
    def _generate_cache_key(self, data: Any) -> str:
        """Generate cache key for data."""
        if isinstance(data, str):
            key_data = data
        else:
            key_data = json.dumps(data, sort_keys=True)
        
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get data from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found/expired
        """
        if key not in self.cache_index:
            return None
        
        cache_info = self.cache_index[key]
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        # Check if file exists
        if not os.path.exists(cache_file):
            del self.cache_index[key]
            self._save_cache_index()
            return None
        
        # Check TTL
        created_time = datetime.fromisoformat(cache_info['created'])
        ttl_seconds = cache_info.get('ttl', self.default_ttl)
        
        if datetime.now() - created_time > timedelta(seconds=ttl_seconds):
            # Cache expired
            self.delete(key)
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Update access time
            cache_info['last_accessed'] = datetime.now().isoformat()
            cache_info['access_count'] += 1
            self._save_cache_index()
            
            return data
            
        except Exception as e:
            logger.warning(f"Failed to load cache data for key {key}: {e}")
            self.delete(key)
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        Set data in cache.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            
            # Save data
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Update index
            self.cache_index[key] = {
                'created': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 1,
                'ttl': ttl or self.default_ttl,
                'size': os.path.getsize(cache_file)
            }
            
            self._save_cache_index()
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache data for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete data from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful
        """
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            
            # Remove file
            if os.path.exists(cache_file):
                os.remove(cache_file)
            
            # Remove from index
            if key in self.cache_index:
                del self.cache_index[key]
                self._save_cache_index()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False
    
    def clear(self):
        """Clear all cache data."""
        try:
            # Remove all cache files
            for key in list(self.cache_index.keys()):
                self.delete(key)
            
            logger.info("Cleared all cache data")
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def cleanup_expired(self):
        """Clean up expired cache entries."""
        expired_keys = []
        current_time = datetime.now()
        
        for key, cache_info in self.cache_index.items():
            created_time = datetime.fromisoformat(cache_info['created'])
            ttl_seconds = cache_info.get('ttl', self.default_ttl)
            
            if current_time - created_time > timedelta(seconds=ttl_seconds):
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_entries = len(self.cache_index)
        total_size = sum(info.get('size', 0) for info in self.cache_index.values())
        
        return {
            'total_entries': total_entries,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': self.cache_dir
        }
```

### 3. Data Serializer (`utils/data_serializer.py`)

```python
"""
Data Serialization Utilities for Research Agent

Provides data serialization and deserialization
for various data types used in research operations.
"""

import json
import pickle
import gzip
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataSerializer:
    """Utility class for data serialization and deserialization."""
    
    @staticmethod
    def serialize_research_data(data: Dict[str, Any]) -> str:
        """
        Serialize research data to JSON string.
        
        Args:
            data: Research data to serialize
            
        Returns:
            JSON string
        """
        try:
            # Convert datetime objects to ISO format
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            return json.dumps(data, indent=2, default=json_serializer)
            
        except Exception as e:
            logger.error(f"Failed to serialize research data: {e}")
            raise
    
    @staticmethod
    def deserialize_research_data(json_str: str) -> Dict[str, Any]:
        """
        Deserialize research data from JSON string.
        
        Args:
            json_str: JSON string to deserialize
            
        Returns:
            Deserialized data dictionary
        """
        try:
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to deserialize research data: {e}")
            raise
    
    @staticmethod
    def serialize_tool_results(results: List[Dict[str, Any]]) -> bytes:
        """
        Serialize tool results using pickle for complex objects.
        
        Args:
            results: Tool results to serialize
            
        Returns:
            Pickled bytes
        """
        try:
            return pickle.dumps(results)
        except Exception as e:
            logger.error(f"Failed to serialize tool results: {e}")
            raise
    
    @staticmethod
    def deserialize_tool_results(pickled_data: bytes) -> List[Dict[str, Any]]:
        """
        Deserialize tool results from pickled bytes.
        
        Args:
            pickled_data: Pickled bytes to deserialize
            
        Returns:
            Deserialized tool results
        """
        try:
            return pickle.loads(pickled_data)
        except Exception as e:
            logger.error(f"Failed to deserialize tool results: {e}")
            raise
    
    @staticmethod
    def compress_data(data: str) -> bytes:
        """
        Compress data using gzip.
        
        Args:
            data: String data to compress
            
        Returns:
            Compressed bytes
        """
        try:
            return gzip.compress(data.encode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to compress data: {e}")
            raise
    
    @staticmethod
    def decompress_data(compressed_data: bytes) -> str:
        """
        Decompress data using gzip.
        
        Args:
            compressed_data: Compressed bytes to decompress
            
        Returns:
            Decompressed string
        """
        try:
            return gzip.decompress(compressed_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to decompress data: {e}")
            raise
```

## Integration with Research Agent

### Usage in Research Workflows

```python
# In research_agent/core.py
from ..utils.file_manager import TempFileManager
from ..utils.cache_manager import CacheManager

class ResearchAgent(BaseAgent):
    def __init__(self, tool_context=None):
        super().__init__(tool_context)
        self.file_manager = TempFileManager()
        self.cache_manager = CacheManager()
    
    def _execute_research_workflow(self, question, config):
        # Check cache first
        cache_key = self._generate_cache_key(question, config['mode'])
        cached_result = self.cache_manager.get(cache_key)
        
        if cached_result:
            logger.info("Using cached research result")
            return cached_result
        
        # Execute research workflow
        result = self._execute_research_rounds(question, config)
        
        # Save to cache
        self.cache_manager.set(cache_key, result, ttl=3600)
        
        # Save research data
        self.file_manager.save_research_data(result, 1, config['mode'])
        
        return result
```

## Key Features

### 1. **Efficient File Management**
- Session-based file organization
- Automatic cleanup and maintenance
- Support for compression and serialization

### 2. **Caching System**
- TTL-based cache expiration
- Hash-based cache keys
- Automatic cache cleanup

### 3. **Data Serialization**
- JSON for simple data structures
- Pickle for complex objects
- Gzip compression for large files

### 4. **Performance Optimization**
- Minimal I/O operations
- Batch file operations
- Memory-efficient data handling

This temp file management implementation provides comprehensive file handling capabilities while maintaining performance and avoiding database dependencies.
