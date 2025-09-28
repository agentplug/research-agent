"""
Source Tracker Module

This module provides URL normalization, deduplication, and metadata management
for research sources across different rounds and sessions.
"""

from .core import SourceTracker

__all__ = [
    'SourceTracker',
]

__version__ = "2.0.0"
__author__ = "agentplug"
__description__ = "Source tracking with URL deduplication for research agent"
