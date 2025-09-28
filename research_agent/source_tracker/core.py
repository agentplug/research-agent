"""
Source Tracker for Research Agent

This module handles URL normalization, deduplication, and metadata management
for research sources across different rounds and sessions.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from datetime import datetime

from ..base_agent.error_handler import ErrorHandler
from ..utils.utils import format_response, get_current_timestamp

logger = logging.getLogger(__name__)


class SourceTracker:
    """
    Source tracker for managing research sources with deduplication.
    
    Features:
    - URL normalization and deduplication
    - Metadata management and reliability scoring
    - Round-based source organization
    - Session-based source tracking
    - Integration with research workflows
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize source tracker.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.error_handler = ErrorHandler("SourceTracker")
        
        # Load configuration
        self.source_config = self.config.get('source_tracking', {})
        self.enabled = self.source_config.get('enabled', True)
        self.max_sources_per_round = self.source_config.get('max_sources_per_round', {})
        self.reliability_threshold = self.source_config.get('reliability_threshold', 0.5)
        self.domain_reliability = self.source_config.get('domain_reliability', {})
        self.normalization_config = self.source_config.get('url_normalization', {})
        
        # Source storage
        self.sources: Dict[str, Dict[str, Any]] = {}  # normalized_url -> source_info
        self.round_sources: Dict[int, List[str]] = {}  # round -> list of normalized_urls
        self.session_sources: List[str] = []  # all sources in current session
        
        # Statistics
        self.stats = {
            'total_sources': 0,
            'duplicates_filtered': 0,
            'reliability_filtered': 0,
            'rounds_completed': 0
        }
    
    def add_source(
        self,
        url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        source_type: Optional[str] = None,
        round_number: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a source to the tracker with deduplication.
        
        Args:
            url: Source URL
            title: Source title
            description: Source description
            source_type: Type of source (web, document, api, etc.)
            round_number: Research round number
            metadata: Additional metadata
            
        Returns:
            Result of adding the source
        """
        try:
            if not self.enabled:
                return format_response(
                    success=True,
                    data={'added': False, 'reason': 'Source tracking disabled'},
                    message="Source tracking is disabled"
                )
            
            if not url or not isinstance(url, str):
                return format_response(
                    success=False,
                    message="Invalid URL provided"
                )
            
            # Normalize URL
            normalized_url = self._normalize_url(url)
            if not normalized_url:
                return format_response(
                    success=False,
                    message="Failed to normalize URL"
                )
            
            # Check for duplicates
            if normalized_url in self.sources:
                self.stats['duplicates_filtered'] += 1
                return format_response(
                    success=True,
                    data={
                        'added': False,
                        'reason': 'duplicate',
                        'normalized_url': normalized_url,
                        'existing_source': self.sources[normalized_url]
                    },
                    message="Source already exists (duplicate filtered)"
                )
            
            # Calculate reliability score
            reliability_score = self._calculate_reliability_score(normalized_url, title, description)
            
            # Check reliability threshold
            if reliability_score < self.reliability_threshold:
                self.stats['reliability_filtered'] += 1
                return format_response(
                    success=True,
                    data={
                        'added': False,
                        'reason': 'low_reliability',
                        'reliability_score': reliability_score,
                        'threshold': self.reliability_threshold
                    },
                    message="Source filtered due to low reliability"
                )
            
            # Create source info
            source_info = {
                'url': url,
                'normalized_url': normalized_url,
                'title': title,
                'description': description,
                'source_type': source_type or 'web',
                'domain': self._extract_domain(normalized_url),
                'reliability_score': reliability_score,
                'added_at': get_current_timestamp(),
                'round': round_number,
                'metadata': metadata or {}
            }
            
            # Add to storage
            self.sources[normalized_url] = source_info
            self.session_sources.append(normalized_url)
            
            # Add to round if specified
            if round_number is not None:
                if round_number not in self.round_sources:
                    self.round_sources[round_number] = []
                self.round_sources[round_number].append(normalized_url)
            
            # Update statistics
            self.stats['total_sources'] += 1
            
            logger.info(f"📚 Added source: {normalized_url} (reliability: {reliability_score:.2f})")
            
            return format_response(
                success=True,
                data={
                    'added': True,
                    'source_info': source_info,
                    'normalized_url': normalized_url
                },
                message="Source added successfully"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'url': url, 'title': title, 'round_number': round_number},
                f"Error adding source: {str(e)}"
            )
    
    def add_sources_batch(
        self,
        sources: List[Dict[str, Any]],
        round_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Add multiple sources in batch.
        
        Args:
            sources: List of source dictionaries
            round_number: Research round number
            
        Returns:
            Batch addition result
        """
        try:
            results = {
                'added': [],
                'filtered': [],
                'errors': []
            }
            
            for source in sources:
                result = self.add_source(
                    url=source.get('url'),
                    title=source.get('title'),
                    description=source.get('description'),
                    source_type=source.get('source_type'),
                    round_number=round_number,
                    metadata=source.get('metadata')
                )
                
                if result['success']:
                    if result['data']['added']:
                        results['added'].append(result['data']['source_info'])
                    else:
                        results['filtered'].append({
                            'url': source.get('url'),
                            'reason': result['data']['reason']
                        })
                else:
                    results['errors'].append({
                        'url': source.get('url'),
                        'error': result['message']
                    })
            
            return format_response(
                success=True,
                data=results,
                message=f"Batch processing completed: {len(results['added'])} added, {len(results['filtered'])} filtered, {len(results['errors'])} errors"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'sources_count': len(sources), 'round_number': round_number},
                f"Error in batch source addition: {str(e)}"
            )
    
    def get_sources_for_round(self, round_number: int) -> Dict[str, Any]:
        """
        Get all sources for a specific round.
        
        Args:
            round_number: Research round number
            
        Returns:
            Sources for the round
        """
        try:
            if round_number not in self.round_sources:
                return format_response(
                    success=True,
                    data={'sources': [], 'count': 0},
                    message=f"No sources found for round {round_number}"
                )
            
            round_urls = self.round_sources[round_number]
            sources = [self.sources[url] for url in round_urls if url in self.sources]
            
            return format_response(
                success=True,
                data={
                    'sources': sources,
                    'count': len(sources),
                    'round_number': round_number
                },
                message=f"Retrieved {len(sources)} sources for round {round_number}"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'round_number': round_number},
                f"Error getting sources for round: {str(e)}"
            )
    
    def get_all_sources(self) -> Dict[str, Any]:
        """Get all sources in the current session."""
        try:
            sources = list(self.sources.values())
            
            return format_response(
                success=True,
                data={
                    'sources': sources,
                    'count': len(sources),
                    'statistics': self.stats
                },
                message=f"Retrieved {len(sources)} total sources"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {},
                f"Error getting all sources: {str(e)}"
            )
    
    def get_sources_by_domain(self, domain: str) -> Dict[str, Any]:
        """
        Get all sources from a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Sources from the domain
        """
        try:
            domain_sources = [
                source for source in self.sources.values()
                if source['domain'] == domain
            ]
            
            return format_response(
                success=True,
                data={
                    'sources': domain_sources,
                    'count': len(domain_sources),
                    'domain': domain
                },
                message=f"Retrieved {len(domain_sources)} sources from {domain}"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'domain': domain},
                f"Error getting sources by domain: {str(e)}"
            )
    
    def get_high_reliability_sources(self, min_score: Optional[float] = None) -> Dict[str, Any]:
        """
        Get sources with high reliability scores.
        
        Args:
            min_score: Minimum reliability score (default: threshold)
            
        Returns:
            High reliability sources
        """
        try:
            threshold = min_score or self.reliability_threshold
            
            high_reliability_sources = [
                source for source in self.sources.values()
                if source['reliability_score'] >= threshold
            ]
            
            # Sort by reliability score (highest first)
            high_reliability_sources.sort(
                key=lambda x: x['reliability_score'], reverse=True
            )
            
            return format_response(
                success=True,
                data={
                    'sources': high_reliability_sources,
                    'count': len(high_reliability_sources),
                    'min_score': threshold
                },
                message=f"Retrieved {len(high_reliability_sources)} high reliability sources"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {'min_score': min_score},
                f"Error getting high reliability sources: {str(e)}"
            )
    
    def _normalize_url(self, url: str) -> Optional[str]:
        """
        Normalize URL for deduplication.
        
        Args:
            url: Original URL
            
        Returns:
            Normalized URL or None if invalid
        """
        try:
            # Parse URL
            parsed = urlparse(url)
            
            # Remove www if configured
            if self.normalization_config.get('remove_www', True):
                if parsed.netloc.startswith('www.'):
                    parsed = parsed._replace(netloc=parsed.netloc[4:])
            
            # Remove trailing slash if configured
            if self.normalization_config.get('remove_trailing_slash', True):
                if parsed.path.endswith('/') and len(parsed.path) > 1:
                    parsed = parsed._replace(path=parsed.path[:-1])
            
            # Sort query parameters if configured
            if self.normalization_config.get('sort_query_params', True):
                if parsed.query:
                    query_params = parse_qs(parsed.query)
                    sorted_params = sorted(query_params.items())
                    sorted_query = urlencode(sorted_params, doseq=True)
                    parsed = parsed._replace(query=sorted_query)
            
            # Reconstruct URL
            normalized = urlunparse(parsed)
            
            # Basic validation
            if not normalized.startswith(('http://', 'https://')):
                return None
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing URL {url}: {e}")
            return None
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return "unknown"
    
    def _calculate_reliability_score(
        self, url: str, title: Optional[str], description: Optional[str]
    ) -> float:
        """
        Calculate reliability score for a source.
        
        Args:
            url: Source URL
            title: Source title
            description: Source description
            
        Returns:
            Reliability score (0.0-1.0)
        """
        score = 0.5  # Base score
        
        # Domain-based scoring
        domain = self._extract_domain(url)
        if domain in self.domain_reliability:
            score = self.domain_reliability[domain]
        
        # Title quality scoring
        if title:
            title_lower = title.lower()
            
            # Positive indicators
            if any(word in title_lower for word in ['study', 'research', 'analysis', 'report']):
                score += 0.1
            
            # Negative indicators
            if any(word in title_lower for word in ['advertisement', 'sponsored', 'promo']):
                score -= 0.2
        
        # Description quality scoring
        if description:
            desc_lower = description.lower()
            
            # Positive indicators
            if any(word in desc_lower for word in ['peer-reviewed', 'academic', 'scholarly']):
                score += 0.15
            
            # Length indicator (longer descriptions often more reliable)
            if len(description) > 100:
                score += 0.05
        
        # URL structure scoring
        if '/wiki/' in url.lower():
            score += 0.1  # Wikipedia
        elif '/arxiv.org/' in url.lower():
            score += 0.15  # ArXiv
        elif '/scholar.' in url.lower():
            score += 0.2  # Google Scholar
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, score))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get source tracking statistics."""
        try:
            # Calculate additional statistics
            domain_counts = {}
            reliability_distribution = {'high': 0, 'medium': 0, 'low': 0}
            
            for source in self.sources.values():
                # Domain counts
                domain = source['domain']
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
                
                # Reliability distribution
                score = source['reliability_score']
                if score >= 0.8:
                    reliability_distribution['high'] += 1
                elif score >= 0.5:
                    reliability_distribution['medium'] += 1
                else:
                    reliability_distribution['low'] += 1
            
            return format_response(
                success=True,
                data={
                    'statistics': self.stats,
                    'domain_counts': domain_counts,
                    'reliability_distribution': reliability_distribution,
                    'total_unique_sources': len(self.sources),
                    'rounds_with_sources': len(self.round_sources)
                },
                message="Source tracking statistics retrieved"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {},
                f"Error getting statistics: {str(e)}"
            )
    
    def clear_session(self) -> Dict[str, Any]:
        """Clear all sources for the current session."""
        try:
            sources_count = len(self.sources)
            
            self.sources.clear()
            self.round_sources.clear()
            self.session_sources.clear()
            
            # Reset statistics
            self.stats = {
                'total_sources': 0,
                'duplicates_filtered': 0,
                'reliability_filtered': 0,
                'rounds_completed': 0
            }
            
            logger.info(f"🧹 Cleared {sources_count} sources from session")
            
            return format_response(
                success=True,
                data={'cleared_count': sources_count},
                message=f"Cleared {sources_count} sources from session"
            )
            
        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {},
                f"Error clearing session: {str(e)}"
            )
