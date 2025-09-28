"""
ContextManager - Session state and context management for BaseAgent.

This module provides context management capabilities including session state,
conversation history, and metadata management.
"""

import json
import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from ..utils.utils import generate_session_id, safe_json_dumps, safe_json_loads


class ContextType(Enum):
    """Types of context data."""

    SESSION = "session"
    CONVERSATION = "conversation"
    METADATA = "metadata"
    TEMPORARY = "temporary"


@dataclass
class ContextEntry:
    """A context entry with metadata."""

    key: str
    value: Any
    context_type: ContextType
    created_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def is_expired(self) -> bool:
        """Check if the context entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "value": self.value,
            "context_type": self.context_type.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextEntry":
        """Create from dictionary."""
        return cls(
            key=data["key"],
            value=data["value"],
            context_type=ContextType(data["context_type"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"])
            if data.get("expires_at")
            else None,
            metadata=data.get("metadata", {}),
        )


class ContextManager:
    """
    Manages session state and context for BaseAgent.

    Provides thread-safe context management with expiration support.
    """

    def __init__(self, session_id: Optional[str] = None, max_context_size: int = 1000):
        """
        Initialize ContextManager.

        Args:
            session_id: Unique session identifier
            max_context_size: Maximum number of context entries
        """
        self.session_id = session_id or generate_session_id()
        self.max_context_size = max_context_size
        self._context: Dict[str, ContextEntry] = {}
        self._lock = threading.RLock()
        self._conversation_history: List[Dict[str, Any]] = []
        self._metadata: Dict[str, Any] = {
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat(),
            "access_count": 0,
        }

    def set_context(
        self,
        key: str,
        value: Any,
        context_type: ContextType = ContextType.SESSION,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Set a context value with optional expiration.

        Args:
            key: Context key
            value: Context value
            context_type: Type of context
            ttl_seconds: Time to live in seconds
            metadata: Additional metadata
        """
        with self._lock:
            # Calculate expiration time
            expires_at = None
            if ttl_seconds:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)

            # Create context entry
            entry = ContextEntry(
                key=key,
                value=value,
                context_type=context_type,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                metadata=metadata,
            )

            # Store the entry
            self._context[key] = entry

            # Clean up if we exceed max size
            if len(self._context) > self.max_context_size:
                self._cleanup_expired()
                if len(self._context) > self.max_context_size:
                    self._remove_oldest()

            # Update metadata
            self._update_access_metadata()

    def get_context(
        self, key: str, default: Any = None, context_type: Optional[ContextType] = None
    ) -> Any:
        """
        Get a context value.

        Args:
            key: Context key
            default: Default value if key not found
            context_type: Optional context type filter

        Returns:
            Context value or default
        """
        with self._lock:
            if key not in self._context:
                return default

            entry = self._context[key]

            # Check if expired
            if entry.is_expired():
                del self._context[key]
                return default

            # Check context type if specified
            if context_type and entry.context_type != context_type:
                return default

            # Update access metadata
            self._update_access_metadata()

            return entry.value

    def has_context(self, key: str, context_type: Optional[ContextType] = None) -> bool:
        """
        Check if a context key exists and is not expired.

        Args:
            key: Context key
            context_type: Optional context type filter

        Returns:
            True if context exists and is valid
        """
        with self._lock:
            if key not in self._context:
                return False

            entry = self._context[key]

            # Check if expired
            if entry.is_expired():
                del self._context[key]
                return False

            # Check context type if specified
            if context_type and entry.context_type != context_type:
                return False

            return True

    def remove_context(self, key: str) -> bool:
        """
        Remove a context entry.

        Args:
            key: Context key to remove

        Returns:
            True if removed, False if not found
        """
        with self._lock:
            if key in self._context:
                del self._context[key]
                return True
            return False

    def clear_context(self, context_type: Optional[ContextType] = None) -> int:
        """
        Clear context entries.

        Args:
            context_type: Optional context type filter

        Returns:
            Number of entries cleared
        """
        with self._lock:
            if context_type:
                keys_to_remove = [
                    key
                    for key, entry in self._context.items()
                    if entry.context_type == context_type
                ]
            else:
                keys_to_remove = list(self._context.keys())

            for key in keys_to_remove:
                del self._context[key]

            return len(keys_to_remove)

    def add_conversation_entry(
        self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add an entry to conversation history.

        Args:
            role: Role of the speaker (user, assistant, system)
            content: Content of the message
            metadata: Additional metadata
        """
        with self._lock:
            entry = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }

            self._conversation_history.append(entry)

            # Keep only last 100 conversation entries
            if len(self._conversation_history) > 100:
                self._conversation_history.pop(0)

    def get_conversation_history(
        self, limit: Optional[int] = None, role_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history.

        Args:
            limit: Maximum number of entries to return
            role_filter: Filter by role

        Returns:
            List of conversation entries
        """
        with self._lock:
            history = self._conversation_history.copy()

            # Apply role filter
            if role_filter:
                history = [entry for entry in history if entry["role"] == role_filter]

            # Apply limit
            if limit:
                history = history[-limit:]

            return history

    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set session metadata.

        Args:
            key: Metadata key
            value: Metadata value
        """
        with self._lock:
            self._metadata[key] = value
            self._update_access_metadata()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get session metadata.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        with self._lock:
            return self._metadata.get(key, default)

    def get_all_metadata(self) -> Dict[str, Any]:
        """
        Get all session metadata.

        Returns:
            Copy of all metadata
        """
        with self._lock:
            return self._metadata.copy()

    def _cleanup_expired(self) -> int:
        """
        Remove expired context entries.

        Returns:
            Number of entries removed
        """
        expired_keys = [
            key for key, entry in self._context.items() if entry.is_expired()
        ]

        for key in expired_keys:
            del self._context[key]

        return len(expired_keys)

    def _remove_oldest(self) -> None:
        """Remove the oldest context entry."""
        if not self._context:
            return

        oldest_key = min(
            self._context.keys(), key=lambda k: self._context[k].created_at
        )
        del self._context[oldest_key]

    def _update_access_metadata(self) -> None:
        """Update access metadata."""
        self._metadata["last_accessed"] = datetime.utcnow().isoformat()
        self._metadata["access_count"] = self._metadata.get("access_count", 0) + 1

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize context manager to dictionary.

        Returns:
            Dictionary representation
        """
        with self._lock:
            return {
                "session_id": self.session_id,
                "context": {
                    key: entry.to_dict()
                    for key, entry in self._context.items()
                    if not entry.is_expired()
                },
                "conversation_history": self._conversation_history.copy(),
                "metadata": self._metadata.copy(),
            }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Deserialize context manager from dictionary.

        Args:
            data: Dictionary representation
        """
        with self._lock:
            self.session_id = data.get("session_id", self.session_id)

            # Restore context
            self._context = {}
            for key, entry_data in data.get("context", {}).items():
                try:
                    entry = ContextEntry.from_dict(entry_data)
                    if not entry.is_expired():
                        self._context[key] = entry
                except (KeyError, ValueError):
                    continue

            # Restore conversation history
            self._conversation_history = data.get("conversation_history", [])

            # Restore metadata
            self._metadata.update(data.get("metadata", {}))

    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current context state.

        Returns:
            Context summary
        """
        with self._lock:
            return {
                "session_id": self.session_id,
                "context_count": len(self._context),
                "conversation_entries": len(self._conversation_history),
                "metadata_keys": list(self._metadata.keys()),
                "last_accessed": self._metadata.get("last_accessed"),
                "access_count": self._metadata.get("access_count", 0),
            }
