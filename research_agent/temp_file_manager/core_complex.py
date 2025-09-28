"""
Temporary File Manager for Research Agent

This module handles session-based file organization, research data storage,
cache management, and automatic cleanup for research sessions.
"""

import json
import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base_agent.error_handler import ErrorHandler
from ..utils.utils import (
    format_response,
    get_current_timestamp,
    safe_json_dumps,
    safe_json_loads,
)

logger = logging.getLogger(__name__)


class TempFileManager:
    """
    Temporary file manager for research session data.

    Features:
    - Session-based file organization
    - Research data storage and retrieval
    - Cache management functionality
    - Automatic cleanup mechanisms
    - Integration with research workflows
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize temp file manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.error_handler = ErrorHandler("TempFileManager")

        # Load configuration
        self.temp_config = self.config.get("temp_file_management", {})
        self.enabled = self.temp_config.get("enabled", True)
        # Use tempfile.gettempdir() for secure temp directory
        import tempfile

        default_temp_dir = Path(tempfile.gettempdir()) / "research_agent"
        self.base_directory = Path(
            self.temp_config.get("base_directory", str(default_temp_dir))
        )
        self.auto_cleanup = self.temp_config.get("auto_cleanup", True)
        self.max_session_age_hours = self.temp_config.get("max_session_age_hours", 24)
        self.max_cache_age_hours = self.temp_config.get("max_cache_age_hours", 48)
        self.max_file_size_mb = self.temp_config.get("max_file_size_mb", 100)

        # Directory organization
        self.organization = self.temp_config.get(
            "organization",
            {
                "research_data": "research_data/",
                "intermediate_results": "intermediate_results/",
                "cache": "cache/",
                "logs": "logs/",
            },
        )

        # Current session
        self.current_session_id: Optional[str] = None
        self.session_path: Optional[Path] = None

        # Statistics
        self.stats = {
            "sessions_created": 0,
            "files_stored": 0,
            "files_retrieved": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cleanup_operations": 0,
        }

    def initialize_session(self, session_id: str) -> Dict[str, Any]:
        """
        Initialize a new research session.

        Args:
            session_id: Unique session identifier

        Returns:
            Session initialization result
        """
        try:
            if not self.enabled:
                return format_response(
                    success=True,
                    data={
                        "initialized": False,
                        "reason": "Temp file management disabled",
                    },
                    message="Temp file management is disabled",
                )

            if not session_id or not isinstance(session_id, str):
                return format_response(
                    success=False, message="Invalid session ID provided"
                )

            # Create session directory
            self.current_session_id = session_id
            self.session_path = self.base_directory / session_id

            # Create all subdirectories
            for dir_name, dir_path in self.organization.items():
                full_path = self.session_path / dir_path
                full_path.mkdir(parents=True, exist_ok=True)

            # Create session info file
            session_info = {
                "session_id": session_id,
                "created_at": get_current_timestamp(),
                "modified_at": get_current_timestamp(),
                "file_counts": {dir_name: 0 for dir_name in self.organization.keys()},
                "total_size_bytes": 0,
                "path": str(self.session_path),
            }

            self._save_session_info(session_info)

            # Update statistics
            self.stats["sessions_created"] += 1

            logger.info(f"📁 Initialized session: {session_id}")

            return format_response(
                success=True,
                data={
                    "initialized": True,
                    "session_id": session_id,
                    "session_path": str(self.session_path),
                    "session_info": session_info,
                },
                message=f"Session {session_id} initialized successfully",
            )

        except Exception as e:
            return self.error_handler.handle_error(
                e, {"session_id": session_id}, f"Error initializing session: {str(e)}"
            )

    def store_research_data(
        self,
        data: Any,
        filename: str,
        data_type: str = "research_data",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Store research data in the current session.

        Args:
            data: Data to store
            filename: Filename for the data
            data_type: Type of data (research_data, intermediate_results, cache, logs)
            metadata: Additional metadata

        Returns:
            Storage result
        """
        try:
            if not self.enabled or not self.current_session_id:
                return format_response(
                    success=False,
                    message="Session not initialized or temp file management disabled",
                )

            if data_type not in self.organization:
                return format_response(
                    success=False, message=f"Invalid data type: {data_type}"
                )

            # Prepare file path
            file_path = self.session_path / self.organization[data_type] / filename

            # Check file size limit
            if isinstance(data, str):
                data_size_mb = len(data.encode("utf-8")) / (1024 * 1024)
            elif isinstance(data, (dict, list)):
                data_size_mb = len(safe_json_dumps(data).encode("utf-8")) / (
                    1024 * 1024
                )
            else:
                data_size_mb = 0  # Unknown size

            if data_size_mb > self.max_file_size_mb:
                return format_response(
                    success=False,
                    message=f"Data too large: {data_size_mb:.2f}MB > {self.max_file_size_mb}MB",
                )

            # Store data based on type
            if isinstance(data, (dict, list)):
                # JSON data
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif isinstance(data, str):
                # Text data
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(data)
            else:
                # Binary data (convert to string representation)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(str(data))

            # Update session info
            self._update_session_info(data_type, filename, data_size_mb, metadata)

            # Update statistics
            self.stats["files_stored"] += 1

            logger.info(f"💾 Stored {data_type}: {filename}")

            return format_response(
                success=True,
                data={
                    "stored": True,
                    "file_path": str(file_path),
                    "data_type": data_type,
                    "size_mb": data_size_mb,
                    "metadata": metadata,
                },
                message=f"Data stored successfully: {filename}",
            )

        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {"filename": filename, "data_type": data_type},
                f"Error storing research data: {str(e)}",
            )

    def retrieve_research_data(
        self, filename: str, data_type: str = "research_data"
    ) -> Dict[str, Any]:
        """
        Retrieve research data from the current session.

        Args:
            filename: Filename to retrieve
            data_type: Type of data

        Returns:
            Retrieved data
        """
        try:
            if not self.enabled or not self.current_session_id:
                return format_response(
                    success=False,
                    message="Session not initialized or temp file management disabled",
                )

            if data_type not in self.organization:
                return format_response(
                    success=False, message=f"Invalid data type: {data_type}"
                )

            # Prepare file path
            file_path = self.session_path / self.organization[data_type] / filename

            if not file_path.exists():
                return format_response(
                    success=False, message=f"File not found: {filename}"
                )

            # Read data based on file extension
            if filename.endswith(".json"):
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
            else:
                with open(file_path, encoding="utf-8") as f:
                    data = f.read()

            # Update statistics
            self.stats["files_retrieved"] += 1

            logger.info(f"📖 Retrieved {data_type}: {filename}")

            return format_response(
                success=True,
                data={
                    "retrieved": True,
                    "data": data,
                    "file_path": str(file_path),
                    "data_type": data_type,
                },
                message=f"Data retrieved successfully: {filename}",
            )

        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {"filename": filename, "data_type": data_type},
                f"Error retrieving research data: {str(e)}",
            )

    def cache_data(
        self, key: str, data: Any, ttl_hours: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Cache data with TTL support.

        Args:
            key: Cache key
            data: Data to cache
            ttl_hours: Time to live in hours

        Returns:
            Cache result
        """
        try:
            if not self.enabled or not self.current_session_id:
                return format_response(
                    success=False,
                    message="Session not initialized or temp file management disabled",
                )

            # Prepare cache data
            cache_data = {
                "data": data,
                "cached_at": get_current_timestamp(),
                "ttl_hours": ttl_hours or self.max_cache_age_hours,
                "key": key,
            }

            # Store in cache
            filename = f"cache_{key}.json"
            result = self.store_research_data(
                data=cache_data,
                filename=filename,
                data_type="cache",
                metadata={"cache_key": key, "ttl_hours": ttl_hours},
            )

            if result["success"]:
                self.stats["cache_hits"] += 1

            return result

        except Exception as e:
            return self.error_handler.handle_error(
                e, {"key": key, "ttl_hours": ttl_hours}, f"Error caching data: {str(e)}"
            )

    def get_cached_data(self, key: str) -> Dict[str, Any]:
        """
        Retrieve cached data if not expired.

        Args:
            key: Cache key

        Returns:
            Cached data or None if expired/not found
        """
        try:
            if not self.enabled or not self.current_session_id:
                return format_response(
                    success=False,
                    message="Session not initialized or temp file management disabled",
                )

            filename = f"cache_{key}.json"
            result = self.retrieve_research_data(filename, "cache")

            if not result["success"]:
                self.stats["cache_misses"] += 1
                return format_response(
                    success=True,
                    data={"cached_data": None, "reason": "not_found"},
                    message="Cache miss: data not found",
                )

            cache_data = result["data"]
            cached_at = datetime.fromisoformat(cache_data["cached_at"])
            ttl_hours = cache_data["ttl_hours"]

            # Check if expired
            if datetime.now() - cached_at > timedelta(hours=ttl_hours):
                self.stats["cache_misses"] += 1
                return format_response(
                    success=True,
                    data={"cached_data": None, "reason": "expired"},
                    message="Cache miss: data expired",
                )

            self.stats["cache_hits"] += 1

            return format_response(
                success=True,
                data={
                    "cached_data": cache_data["data"],
                    "cached_at": cache_data["cached_at"],
                    "ttl_hours": ttl_hours,
                },
                message="Cache hit: data retrieved successfully",
            )

        except Exception as e:
            return self.error_handler.handle_error(
                e, {"key": key}, f"Error getting cached data: {str(e)}"
            )

    def list_session_files(self, data_type: Optional[str] = None) -> Dict[str, Any]:
        """
        List files in the current session.

        Args:
            data_type: Specific data type to list (optional)

        Returns:
            List of files
        """
        try:
            if not self.enabled or not self.current_session_id:
                return format_response(
                    success=False,
                    message="Session not initialized or temp file management disabled",
                )

            files = {}

            if data_type:
                if data_type not in self.organization:
                    return format_response(
                        success=False, message=f"Invalid data type: {data_type}"
                    )

                dir_path = self.session_path / self.organization[data_type]
                if dir_path.exists():
                    files[data_type] = [
                        {
                            "name": f.name,
                            "size_bytes": f.stat().st_size,
                            "modified_at": datetime.fromtimestamp(
                                f.stat().st_mtime
                            ).isoformat(),
                        }
                        for f in dir_path.iterdir()
                        if f.is_file()
                    ]
            else:
                # List all data types
                for dir_name, dir_path in self.organization.items():
                    full_path = self.session_path / dir_path
                    if full_path.exists():
                        files[dir_name] = [
                            {
                                "name": f.name,
                                "size_bytes": f.stat().st_size,
                                "modified_at": datetime.fromtimestamp(
                                    f.stat().st_mtime
                                ).isoformat(),
                            }
                            for f in full_path.iterdir()
                            if f.is_file()
                        ]

            return format_response(
                success=True,
                data={"files": files},
                message="Session files listed successfully",
            )

        except Exception as e:
            return self.error_handler.handle_error(
                e, {"data_type": data_type}, f"Error listing session files: {str(e)}"
            )

    def cleanup_session(self) -> Dict[str, Any]:
        """
        Clean up the current session.

        Returns:
            Cleanup result
        """
        try:
            if not self.enabled or not self.current_session_id:
                return format_response(
                    success=True,
                    data={"cleaned": False, "reason": "Session not initialized"},
                    message="No session to clean up",
                )

            if not self.session_path or not self.session_path.exists():
                return format_response(
                    success=True,
                    data={"cleaned": False, "reason": "Session path not found"},
                    message="Session path not found",
                )

            # Calculate session size before cleanup
            session_size = sum(
                f.stat().st_size for f in self.session_path.rglob("*") if f.is_file()
            )

            # Remove session directory
            shutil.rmtree(self.session_path)

            # Update statistics
            self.stats["cleanup_operations"] += 1

            logger.info(
                f"🧹 Cleaned up session: {self.current_session_id} ({session_size} bytes)"
            )

            # Reset current session
            self.current_session_id = None
            self.session_path = None

            return format_response(
                success=True,
                data={
                    "cleaned": True,
                    "session_id": self.current_session_id,
                    "size_bytes": session_size,
                },
                message=f"Session cleaned up successfully",
            )

        except Exception as e:
            return self.error_handler.handle_error(
                e,
                {"session_id": self.current_session_id},
                f"Error cleaning up session: {str(e)}",
            )

    def cleanup_old_sessions(self) -> Dict[str, Any]:
        """
        Clean up old sessions based on age.

        Returns:
            Cleanup result
        """
        try:
            if not self.enabled or not self.auto_cleanup:
                return format_response(
                    success=True,
                    data={"cleaned": False, "reason": "Auto cleanup disabled"},
                    message="Auto cleanup is disabled",
                )

            if not self.base_directory.exists():
                return format_response(
                    success=True,
                    data={"cleaned": False, "reason": "Base directory not found"},
                    message="Base directory not found",
                )

            cleaned_sessions = []
            total_size_freed = 0

            # Check all session directories
            for session_dir in self.base_directory.iterdir():
                if not session_dir.is_dir():
                    continue

                # Check session age
                session_info_path = session_dir / "session_info.json"
                if session_info_path.exists():
                    try:
                        with open(session_info_path) as f:
                            session_info = json.load(f)

                        created_at = datetime.fromisoformat(session_info["created_at"])
                        age_hours = (datetime.now() - created_at).total_seconds() / 3600

                        if age_hours > self.max_session_age_hours:
                            # Calculate size before cleanup
                            session_size = sum(
                                f.stat().st_size
                                for f in session_dir.rglob("*")
                                if f.is_file()
                            )

                            # Remove old session
                            shutil.rmtree(session_dir)

                            cleaned_sessions.append(
                                {
                                    "session_id": session_info["session_id"],
                                    "age_hours": age_hours,
                                    "size_bytes": session_size,
                                }
                            )

                            total_size_freed += session_size

                    except Exception as e:
                        logger.warning(
                            f"Error processing session {session_dir.name}: {e}"
                        )
                        continue

            # Update statistics
            self.stats["cleanup_operations"] += len(cleaned_sessions)

            logger.info(
                f"🧹 Cleaned up {len(cleaned_sessions)} old sessions ({total_size_freed} bytes)"
            )

            return format_response(
                success=True,
                data={
                    "cleaned_sessions": cleaned_sessions,
                    "count": len(cleaned_sessions),
                    "total_size_freed": total_size_freed,
                },
                message=f"Cleaned up {len(cleaned_sessions)} old sessions",
            )

        except Exception as e:
            return self.error_handler.handle_error(
                e, {}, f"Error cleaning up old sessions: {str(e)}"
            )

    def _save_session_info(self, session_info: Dict[str, Any]) -> None:
        """Save session info to file."""
        if not self.session_path:
            return
        try:
            info_path = self.session_path / "session_info.json"
            with open(info_path, "w") as f:
                json.dump(session_info, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving session info: {e}")

    def _update_session_info(
        self,
        data_type: str,
        filename: str,
        size_mb: float,
        metadata: Optional[Dict[str, Any]],
    ) -> None:
        """Update session info after storing data."""
        if not self.session_path:
            return
        try:
            info_path = self.session_path / "session_info.json"
            if info_path.exists():
                with open(info_path) as f:
                    session_info = json.load(f)

                # Update file count
                session_info["file_counts"][data_type] += 1
                session_info["total_size_bytes"] += int(size_mb * 1024 * 1024)
                session_info["modified_at"] = get_current_timestamp()

                # Save updated info
                with open(info_path, "w") as f:
                    json.dump(session_info, f, indent=2)

        except Exception as e:
            logger.error(f"Error updating session info: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get temp file manager statistics."""
        try:
            return format_response(
                success=True,
                data={
                    "statistics": self.stats,
                    "current_session_id": self.current_session_id,
                    "session_path": str(self.session_path)
                    if self.session_path
                    else None,
                    "base_directory": str(self.base_directory),
                    "enabled": self.enabled,
                    "auto_cleanup": self.auto_cleanup,
                },
                message="Temp file manager statistics retrieved",
            )

        except Exception as e:
            return self.error_handler.handle_error(
                e, {}, f"Error getting statistics: {str(e)}"
            )
