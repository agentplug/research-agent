# Source Tracking Implementation Design

## Overview

This document provides detailed implementation design for source tracking functionality in the Deep Research Agent. Source tracking prevents duplicate URL scraping and manages research source metadata efficiently.

## Module Structure

```
src/research_agent/
├── source_tracker.py              # Main source tracking implementation
└── utils/
    └── url_manager.py             # URL utilities and validation
```

## Core Implementation

### 1. Source Tracker (`source_tracker.py`)

```python
"""
Source Tracking for Research Agent

Manages URL tracking, duplicate prevention, and source metadata
to avoid re-scraping already accessed sources during research.
"""

import json
import os
import hashlib
import tempfile
from typing import Set, Dict, List, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import logging

logger = logging.getLogger(__name__)


class SourceTracker:
    """
    Tracks research sources to prevent duplicate scraping and manage metadata.
    
    Features:
    - URL deduplication using hash-based tracking
    - Source metadata management
    - Temporary file-based storage
    - URL normalization and validation
    - Cleanup and maintenance utilities
    """
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize the source tracker.
        
        Args:
            temp_dir: Optional custom temp directory for storage
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.tracking_file = os.path.join(self.temp_dir, "research_sources.json")
        self.url_hashes: Set[str] = set()
        self.source_metadata: Dict[str, Dict[str, Any]] = {}
        self.session_id = self._generate_session_id()
        
        # Load existing tracking data
        self._load_tracking_data()
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID for this research session."""
        return f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
    
    def _load_tracking_data(self):
        """Load existing tracking data from file."""
        try:
            if os.path.exists(self.tracking_file):
                with open(self.tracking_file, 'r') as f:
                    data = json.load(f)
                    self.url_hashes = set(data.get('url_hashes', []))
                    self.source_metadata = data.get('source_metadata', {})
                    logger.info(f"Loaded {len(self.url_hashes)} tracked URLs")
        except Exception as e:
            logger.warning(f"Failed to load tracking data: {e}")
            self.url_hashes = set()
            self.source_metadata = {}
    
    def _save_tracking_data(self):
        """Save current tracking data to file."""
        try:
            data = {
                'url_hashes': list(self.url_hashes),
                'source_metadata': self.source_metadata,
                'last_updated': datetime.now().isoformat(),
                'session_id': self.session_id
            }
            
            # Create temp directory if it doesn't exist
            os.makedirs(os.path.dirname(self.tracking_file), exist_ok=True)
            
            with open(self.tracking_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save tracking data: {e}")
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL for consistent tracking.
        
        Args:
            url: Raw URL to normalize
            
        Returns:
            Normalized URL string
        """
        try:
            parsed = urlparse(url)
            
            # Remove common tracking parameters
            tracking_params = [
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                'fbclid', 'gclid', 'ref', 'source', 'campaign'
            ]
            
            # Rebuild URL without tracking parameters
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            if parsed.query:
                from urllib.parse import parse_qs, urlencode
                query_params = parse_qs(parsed.query)
                
                # Remove tracking parameters
                for param in tracking_params:
                    query_params.pop(param, None)
                
                if query_params:
                    normalized += "?" + urlencode(query_params, doseq=True)
            
            if parsed.fragment:
                normalized += "#" + parsed.fragment
                
            return normalized
            
        except Exception as e:
            logger.warning(f"Failed to normalize URL {url}: {e}")
            return url
    
    def _generate_url_hash(self, url: str) -> str:
        """
        Generate hash for URL tracking.
        
        Args:
            url: URL to hash
            
        Returns:
            Hash string for URL
        """
        normalized_url = self._normalize_url(url)
        return hashlib.md5(normalized_url.encode('utf-8')).hexdigest()
    
    def is_url_tracked(self, url: str) -> bool:
        """
        Check if URL has already been tracked.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is already tracked
        """
        url_hash = self._generate_url_hash(url)
        return url_hash in self.url_hashes
    
    def track_url(self, url: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Track a new URL and its metadata.
        
        Args:
            url: URL to track
            metadata: Optional metadata about the source
            
        Returns:
            True if URL was newly tracked, False if already tracked
        """
        url_hash = self._generate_url_hash(url)
        
        if url_hash in self.url_hashes:
            return False
        
        # Add to tracking
        self.url_hashes.add(url_hash)
        
        # Store metadata
        self.source_metadata[url_hash] = {
            'url': url,
            'normalized_url': self._normalize_url(url),
            'first_seen': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat(),
            'access_count': 1,
            'metadata': metadata or {}
        }
        
        # Save tracking data
        self._save_tracking_data()
        
        logger.debug(f"Tracked new URL: {url}")
        return True
    
    def update_url_access(self, url: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Update access information for an existing URL.
        
        Args:
            url: URL to update
            metadata: Optional additional metadata
        """
        url_hash = self._generate_url_hash(url)
        
        if url_hash in self.source_metadata:
            self.source_metadata[url_hash]['last_accessed'] = datetime.now().isoformat()
            self.source_metadata[url_hash]['access_count'] += 1
            
            if metadata:
                self.source_metadata[url_hash]['metadata'].update(metadata)
            
            self._save_tracking_data()
    
    def get_tracked_urls(self) -> List[Dict[str, Any]]:
        """
        Get list of all tracked URLs with metadata.
        
        Returns:
            List of tracked URL dictionaries
        """
        return list(self.source_metadata.values())
    
    def get_url_metadata(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific URL.
        
        Args:
            url: URL to get metadata for
            
        Returns:
            Metadata dictionary or None if not found
        """
        url_hash = self._generate_url_hash(url)
        return self.source_metadata.get(url_hash)
    
    def filter_new_urls(self, urls: List[str]) -> List[str]:
        """
        Filter out URLs that have already been tracked.
        
        Args:
            urls: List of URLs to filter
            
        Returns:
            List of new URLs not yet tracked
        """
        new_urls = []
        for url in urls:
            if not self.is_url_tracked(url):
                new_urls.append(url)
        return new_urls
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get statistics for current research session.
        
        Returns:
            Dictionary with session statistics
        """
        total_urls = len(self.url_hashes)
        session_urls = sum(
            1 for metadata in self.source_metadata.values()
            if metadata.get('first_seen', '').startswith(self.session_id.split('_')[0])
        )
        
        return {
            'session_id': self.session_id,
            'total_tracked_urls': total_urls,
            'session_new_urls': session_urls,
            'tracking_file': self.tracking_file,
            'last_updated': datetime.now().isoformat()
        }
    
    def cleanup_old_sources(self, days_old: int = 7):
        """
        Clean up sources older than specified days.
        
        Args:
            days_old: Remove sources older than this many days
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        removed_count = 0
        
        # Find old URLs to remove
        old_hashes = []
        for url_hash, metadata in self.source_metadata.items():
            first_seen = datetime.fromisoformat(metadata.get('first_seen', ''))
            if first_seen < cutoff_date:
                old_hashes.append(url_hash)
        
        # Remove old URLs
        for url_hash in old_hashes:
            self.url_hashes.discard(url_hash)
            del self.source_metadata[url_hash]
            removed_count += 1
        
        if removed_count > 0:
            self._save_tracking_data()
            logger.info(f"Cleaned up {removed_count} old sources")
    
    def export_tracking_data(self, filepath: str) -> bool:
        """
        Export tracking data to a file.
        
        Args:
            filepath: Path to export file
            
        Returns:
            True if export successful
        """
        try:
            data = {
                'url_hashes': list(self.url_hashes),
                'source_metadata': self.source_metadata,
                'exported_at': datetime.now().isoformat(),
                'session_id': self.session_id
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Exported tracking data to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export tracking data: {e}")
            return False
    
    def import_tracking_data(self, filepath: str) -> bool:
        """
        Import tracking data from a file.
        
        Args:
            filepath: Path to import file
            
        Returns:
            True if import successful
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Merge with existing data
            self.url_hashes.update(data.get('url_hashes', []))
            self.source_metadata.update(data.get('source_metadata', {}))
            
            self._save_tracking_data()
            logger.info(f"Imported tracking data from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import tracking data: {e}")
            return False
    
    def clear_session_data(self):
        """Clear all tracking data for current session."""
        self.url_hashes.clear()
        self.source_metadata.clear()
        self._save_tracking_data()
        logger.info("Cleared all tracking data")
    
    def __del__(self):
        """Cleanup when tracker is destroyed."""
        try:
            self._save_tracking_data()
        except Exception:
            pass  # Ignore errors during cleanup
```

### 2. URL Manager (`utils/url_manager.py`)

```python
"""
URL Management Utilities for Research Agent

Provides URL validation, normalization, and domain analysis
for source tracking and research operations.
"""

import re
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse, urljoin, urlunparse
import logging

logger = logging.getLogger(__name__)


class URLManager:
    """Utility class for URL management and validation."""
    
    # Common domains to exclude from research
    EXCLUDED_DOMAINS = {
        'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
        'youtube.com', 'tiktok.com', 'snapchat.com', 'pinterest.com',
        'reddit.com', 'quora.com', 'stackoverflow.com', 'github.com'
    }
    
    # File extensions to exclude
    EXCLUDED_EXTENSIONS = {
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.zip', '.rar', '.tar', '.gz', '.mp4', '.avi', '.mov',
        '.mp3', '.wav', '.jpg', '.jpeg', '.png', '.gif', '.svg'
    }
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Check if URL is valid and accessible.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL appears valid
        """
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    @staticmethod
    def is_research_relevant(url: str) -> bool:
        """
        Check if URL is relevant for research (not social media, etc.).
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is research-relevant
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check excluded domains
            for excluded in URLManager.EXCLUDED_DOMAINS:
                if excluded in domain:
                    return False
            
            # Check file extensions
            path = parsed.path.lower()
            for ext in URLManager.EXCLUDED_EXTENSIONS:
                if path.endswith(ext):
                    return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalize URL for consistent comparison.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        try:
            parsed = urlparse(url)
            
            # Ensure scheme
            if not parsed.scheme:
                url = 'https://' + url
                parsed = urlparse(url)
            
            # Normalize domain
            domain = parsed.netloc.lower()
            
            # Remove www prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Rebuild URL
            normalized = urlunparse((
                parsed.scheme,
                domain,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            
            return normalized
            
        except Exception as e:
            logger.warning(f"Failed to normalize URL {url}: {e}")
            return url
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """
        Extract domain from URL.
        
        Args:
            url: URL to extract domain from
            
        Returns:
            Domain string or None
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return None
    
    @staticmethod
    def is_same_domain(url1: str, url2: str) -> bool:
        """
        Check if two URLs are from the same domain.
        
        Args:
            url1: First URL
            url2: Second URL
            
        Returns:
            True if same domain
        """
        domain1 = URLManager.extract_domain(url1)
        domain2 = URLManager.extract_domain(url2)
        return domain1 and domain2 and domain1 == domain2
    
    @staticmethod
    def filter_urls(urls: List[str], 
                   min_length: int = 10,
                   max_length: int = 2000,
                   exclude_patterns: Optional[List[str]] = None) -> List[str]:
        """
        Filter URLs based on various criteria.
        
        Args:
            urls: List of URLs to filter
            min_length: Minimum URL length
            max_length: Maximum URL length
            exclude_patterns: Regex patterns to exclude
            
        Returns:
            Filtered list of URLs
        """
        filtered = []
        exclude_patterns = exclude_patterns or []
        
        for url in urls:
            # Length check
            if len(url) < min_length or len(url) > max_length:
                continue
            
            # Validity check
            if not URLManager.is_valid_url(url):
                continue
            
            # Relevance check
            if not URLManager.is_research_relevant(url):
                continue
            
            # Pattern exclusion
            excluded = False
            for pattern in exclude_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    excluded = True
                    break
            
            if not excluded:
                filtered.append(url)
        
        return filtered
    
    @staticmethod
    def get_url_priority(url: str) -> int:
        """
        Get priority score for URL (higher = more important).
        
        Args:
            url: URL to score
            
        Returns:
            Priority score (0-100)
        """
        score = 50  # Base score
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # Academic domains
            if any(academic in domain for academic in ['.edu', '.ac.', '.gov']):
                score += 30
            
            # News domains
            if any(news in domain for news in ['news', 'reuters', 'bbc', 'cnn', 'nytimes']):
                score += 20
            
            # Research-related paths
            if any(research in path for research in ['research', 'study', 'analysis', 'report']):
                score += 25
            
            # Recent content indicators
            if any(recent in path for recent in ['2024', '2023', 'latest', 'new']):
                score += 15
            
            # Avoid social media
            if any(social in domain for social in ['facebook', 'twitter', 'instagram']):
                score -= 40
            
            return max(0, min(100, score))
            
        except Exception:
            return score
```

## Integration with Research Agent

### Usage in Research Workflows

```python
# In research_agent/core.py
from .source_tracker import SourceTracker

class ResearchAgent(BaseAgent):
    def __init__(self, tool_context=None):
        super().__init__(tool_context)
        self.source_tracker = SourceTracker()
    
    def _execute_single_round(self, question, system_prompt, sources_per_round, sources_used):
        # Get tool calls from LLM
        tool_calls = self._get_tool_calls_from_llm(question)
        
        # Filter out already tracked URLs
        new_tool_calls = []
        for tool_call in tool_calls:
            if tool_call.get('tool') == 'web_search':
                urls = tool_call.get('parameters', {}).get('urls', [])
                new_urls = self.source_tracker.filter_new_urls(urls)
                
                if new_urls:
                    tool_call['parameters']['urls'] = new_urls
                    new_tool_calls.append(tool_call)
            else:
                new_tool_calls.append(tool_call)
        
        # Execute tools and track new URLs
        results = self._execute_tools(new_tool_calls)
        
        # Track new URLs
        for result in results:
            if 'url' in result:
                self.source_tracker.track_url(
                    result['url'],
                    metadata={
                        'round': len(sources_used),
                        'question': question,
                        'tool': result.get('tool', 'unknown')
                    }
                )
        
        return results
```

## Key Features

### 1. **Efficient URL Tracking**
- Hash-based deduplication for fast lookups
- URL normalization to handle variations
- Session-based tracking with cleanup

### 2. **Metadata Management**
- Rich metadata storage for each source
- Access counting and timestamps
- Custom metadata support

### 3. **Performance Optimized**
- In-memory tracking with periodic saves
- Batch operations for efficiency
- Minimal I/O operations

### 4. **Maintenance Utilities**
- Automatic cleanup of old sources
- Export/import functionality
- Session statistics and reporting

This source tracking implementation provides comprehensive URL management while maintaining performance and avoiding duplicate research efforts.
