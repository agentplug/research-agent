# Source Tracker Module - Phase 2

## Overview

This module implements source tracking and URL deduplication for Phase 2, preventing duplicate sources across research rounds and maintaining source metadata for comprehensive research tracking.

## Module Structure

```
research_agent/research_agent/
├── source_tracker.py          # Main SourceTracker class
└── workflows/                 # Enhanced workflows with source tracking
    ├── workflows.py           # Updated with source tracking integration
    ├── instant.py            # Source tracking for instant research
    ├── quick.py              # Source tracking for quick research
    ├── standard.py           # Source tracking for standard research
    └── deep.py               # Source tracking for deep research
```

## Key Components

### 1. Source Tracker (`source_tracker.py`)

Main source tracking and deduplication class:

```python
class SourceTracker:
    """Track and deduplicate sources across research rounds."""

    def __init__(self):
        self.used_sources = set()
        self.source_metadata = {}
        self.session_sources = []
        self.round_sources = {}  # Sources per round
        self.current_round = 0

    def add_source(self, url: str, metadata: Dict[str, Any]) -> bool:
        """Add source if not already used."""
        if url in self.used_sources:
            return False

        self.used_sources.add(url)
        self.source_metadata[url] = {
            'url': url,
            'added_at': datetime.utcnow().isoformat(),
            'round': self.current_round,
            'metadata': metadata
        }
        self.session_sources.append(url)

        # Track sources per round
        if self.current_round not in self.round_sources:
            self.round_sources[self.current_round] = []
        self.round_sources[self.current_round].append(url)

        return True

    def get_unused_sources(self, candidate_sources: List[str]) -> List[str]:
        """Filter out already used sources."""
        return [url for url in candidate_sources if url not in self.used_sources]

    def start_new_round(self):
        """Start a new research round."""
        self.current_round += 1

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of sources used in current session."""
        return {
            'total_sources': len(self.used_sources),
            'session_sources': len(self.session_sources),
            'rounds_completed': self.current_round,
            'sources_per_round': {
                round_num: len(sources)
                for round_num, sources in self.round_sources.items()
            },
            'sources': list(self.used_sources)
        }
```

### 2. Source Metadata Management

#### Source Information Structure
```python
@dataclass
class SourceInfo:
    """Data class for source information."""
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None
    source_type: Optional[str] = None  # 'web', 'document', 'api', etc.
    reliability_score: Optional[float] = None
    added_at: Optional[str] = None
    round: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class SourceMetadataManager:
    """Manages source metadata and reliability scoring."""

    def __init__(self):
        self.domain_reliability = {
            'wikipedia.org': 0.9,
            'scholar.google.com': 0.95,
            'arxiv.org': 0.9,
            'pubmed.ncbi.nlm.nih.gov': 0.95,
            'ieee.org': 0.9,
            'acm.org': 0.9,
            'nature.com': 0.95,
            'science.org': 0.95,
            'github.com': 0.8,
            'stackoverflow.com': 0.7,
            'reddit.com': 0.5,
            'twitter.com': 0.4,
        }

    def extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return "unknown"

    def calculate_reliability_score(self, url: str) -> float:
        """Calculate reliability score for a source."""
        domain = self.extract_domain(url)
        base_score = self.domain_reliability.get(domain, 0.6)

        # Adjust based on URL patterns
        if 'pdf' in url.lower():
            base_score += 0.1  # PDFs are often more reliable
        if 'blog' in url.lower():
            base_score -= 0.1  # Blogs are less reliable
        if 'news' in url.lower():
            base_score += 0.05  # News sources are moderately reliable

        return max(0.0, min(1.0, base_score))  # Clamp between 0 and 1
```

### 3. URL Normalization and Deduplication

#### URL Normalization
```python
class URLNormalizer:
    """Normalize URLs for consistent deduplication."""

    def normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication."""
        try:
            from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

            # Parse URL
            parsed = urlparse(url)

            # Normalize scheme and netloc
            scheme = parsed.scheme.lower()
            netloc = parsed.netloc.lower()

            # Remove www. prefix
            if netloc.startswith('www.'):
                netloc = netloc[4:]

            # Normalize path
            path = parsed.path
            if path.endswith('/'):
                path = path[:-1]

            # Sort query parameters
            query_params = parse_qs(parsed.query)
            sorted_params = sorted(query_params.items())
            query = urlencode(sorted_params, doseq=True)

            # Reconstruct URL
            normalized = urlunparse((scheme, netloc, path, parsed.params, query, ''))
            return normalized

        except Exception:
            return url.lower().strip()

    def is_duplicate(self, url1: str, url2: str) -> bool:
        """Check if two URLs are duplicates."""
        return self.normalize_url(url1) == self.normalize_url(url2)
```

### 4. Integration with Research Workflows

#### Enhanced Workflow Integration
```python
class BaseWorkflow:
    """Base workflow with source tracking integration."""

    def __init__(self, llm_service, source_tracker: SourceTracker):
        self.llm_service = llm_service
        self.source_tracker = source_tracker
        self.metadata_manager = SourceMetadataManager()
        self.url_normalizer = URLNormalizer()

    def _process_sources(self, sources: List[str]) -> List[str]:
        """Process and deduplicate sources."""
        # Normalize URLs
        normalized_sources = [self.url_normalizer.normalize_url(url) for url in sources]

        # Filter out duplicates
        unique_sources = self.source_tracker.get_unused_sources(normalized_sources)

        # Add new sources with metadata
        added_sources = []
        for url in unique_sources:
            metadata = {
                'reliability_score': self.metadata_manager.calculate_reliability_score(url),
                'domain': self.metadata_manager.extract_domain(url),
                'source_type': self._detect_source_type(url)
            }

            if self.source_tracker.add_source(url, metadata):
                added_sources.append(url)

        return added_sources

    def _detect_source_type(self, url: str) -> str:
        """Detect source type from URL."""
        url_lower = url.lower()

        if 'pdf' in url_lower:
            return 'document'
        elif 'api' in url_lower or 'json' in url_lower:
            return 'api'
        elif any(domain in url_lower for domain in ['wikipedia', 'scholar', 'arxiv']):
            return 'academic'
        elif any(domain in url_lower for domain in ['github', 'gitlab', 'bitbucket']):
            return 'code'
        else:
            return 'web'
```

#### Mode-Specific Source Tracking

##### Instant Research
```python
class InstantWorkflow(BaseWorkflow):
    """Instant research workflow with minimal source tracking."""

    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute instant research with basic source tracking."""
        self.source_tracker.start_new_round()

        # Generate response (minimal sources for instant mode)
        response = self.llm_service.generate_response(query, 'instant')

        # Track minimal sources
        sources = self._extract_sources_from_response(response)
        processed_sources = self._process_sources(sources[:5])  # Limit to 5 sources

        return self._format_response(response, rounds=1, sources=len(processed_sources))
```

##### Deep Research
```python
class DeepWorkflow(BaseWorkflow):
    """Deep research workflow with comprehensive source tracking."""

    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute deep research with comprehensive source tracking."""
        all_sources = []

        # Round 1: Generate clarification questions
        self.source_tracker.start_new_round()
        clarification_response = self.llm_service.generate_response(
            f"Generate clarification questions for: {query}", 'deep'
        )

        # Round 2-4: Research with clarifications
        for round_num in range(2, 5):
            self.source_tracker.start_new_round()
            response = self.llm_service.generate_response(
                f"Research round {round_num} for: {query}", 'deep'
            )

            # Track sources for this round
            sources = self._extract_sources_from_response(response)
            processed_sources = self._process_sources(sources)
            all_sources.extend(processed_sources)

        # Final synthesis
        self.source_tracker.start_new_round()
        synthesis_response = self.llm_service.generate_response(
            f"Synthesize comprehensive analysis for: {query}", 'deep'
        )

        return self._format_deep_response(
            clarification_response, synthesis_response, all_sources
        )
```

## Testing Strategy

### Unit Tests
```python
class TestSourceTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = SourceTracker()

    def test_source_deduplication(self):
        """Test source deduplication."""
        url1 = "https://example.com/article"
        url2 = "https://www.example.com/article/"

        # Add first source
        self.assertTrue(self.tracker.add_source(url1, {}))

        # Try to add duplicate (normalized)
        self.assertFalse(self.tracker.add_source(url2, {}))

        # Check only one source is tracked
        self.assertEqual(len(self.tracker.used_sources), 1)

    def test_round_tracking(self):
        """Test round-based source tracking."""
        # Round 1
        self.tracker.start_new_round()
        self.tracker.add_source("https://source1.com", {})

        # Round 2
        self.tracker.start_new_round()
        self.tracker.add_source("https://source2.com", {})

        # Check round tracking
        self.assertEqual(self.tracker.current_round, 2)
        self.assertEqual(len(self.tracker.round_sources[1]), 1)
        self.assertEqual(len(self.tracker.round_sources[2]), 1)

    def test_session_summary(self):
        """Test session summary generation."""
        self.tracker.start_new_round()
        self.tracker.add_source("https://source1.com", {})

        self.tracker.start_new_round()
        self.tracker.add_source("https://source2.com", {})

        summary = self.tracker.get_session_summary()
        self.assertEqual(summary['total_sources'], 2)
        self.assertEqual(summary['rounds_completed'], 2)
        self.assertEqual(summary['sources_per_round'][1], 1)
        self.assertEqual(summary['sources_per_round'][2], 1)
```

### Integration Tests
- Test with research workflows
- Test source extraction from LLM responses
- Test metadata management and reliability scoring
- Test URL normalization and deduplication

## Configuration

### config.json Updates
```json
{
  "source_tracking": {
    "enabled": true,
    "max_sources_per_round": {
      "instant": 5,
      "quick": 10,
      "standard": 25,
      "deep": 50
    },
    "reliability_threshold": 0.5,
    "domain_reliability": {
      "wikipedia.org": 0.9,
      "scholar.google.com": 0.95,
      "arxiv.org": 0.9,
      "github.com": 0.8,
      "stackoverflow.com": 0.7
    },
    "url_normalization": {
      "remove_www": true,
      "sort_query_params": true,
      "remove_trailing_slash": true
    }
  }
}
```

## Success Criteria

- [ ] Source deduplication prevents duplicate sources across rounds
- [ ] URL normalization works correctly for various URL formats
- [ ] Round-based source tracking maintains proper organization
- [ ] Metadata management provides useful source information
- [ ] Reliability scoring helps prioritize sources
- [ ] Integration with research workflows works seamlessly
- [ ] Session summaries provide comprehensive source statistics
- [ ] All existing tests pass with source tracking enabled

## Implementation Order

1. **Create SourceTracker class with basic functionality**
2. **Implement URL normalization and deduplication**
3. **Add metadata management and reliability scoring**
4. **Integrate with research workflows**
5. **Update configuration**
6. **Write comprehensive tests**
7. **Test with various source types**
8. **Update documentation and examples**
