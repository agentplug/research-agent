"""
Temporary File Manager for Research Agent

KISS & YAGNI: Keep only essential functionality.
Currently unused in research workflows - minimal implementation.
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional


class TempFileManager:
    """
    Simple temporary file manager - KISS & YAGNI implementation.

    Only handles basic file operations when needed.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize temp file manager with minimal configuration."""
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)

        # Simple directory setup
        self.base_directory = Path(tempfile.gettempdir()) / "research_agent"
        self.current_session_id: Optional[str] = None
        self.session_path: Optional[Path] = None

        # Simple statistics
        self.stats = {
            "sessions_created": 0,
            "files_stored": 0,
            "files_retrieved": 0,
        }

    def initialize_session(self, session_id: str) -> Dict[str, Any]:
        """
        Initialize a new session.

        Args:
            session_id: Unique session identifier

        Returns:
            Success response
        """
        if not self.enabled:
            return {"success": True, "message": "Temp file management disabled"}

        try:
            self.current_session_id = session_id
            self.session_path = self.base_directory / session_id
            self.session_path.mkdir(parents=True, exist_ok=True)

            self.stats["sessions_created"] += 1

            return {
                "success": True,
                "data": {
                    "session_id": session_id,
                    "session_path": str(self.session_path),
                },
                "message": f"Session {session_id} initialized successfully",
            }
        except Exception as e:
            return {
                "success": False,
                "data": {"error": str(e)},
                "message": f"Failed to initialize session {session_id}",
            }

    def store_research_data(
        self,
        data: Dict[str, Any],
        filename: str,
        data_type: str = "research_data",
    ) -> Dict[str, Any]:
        """
        Store research data to a file.

        Args:
            data: Data to store
            filename: Name of the file
            data_type: Type of data (for organization)

        Returns:
            Success response
        """
        if not self.enabled:
            return {"success": True, "message": "Temp file management disabled"}

        if not self.session_path:
            return {
                "success": False,
                "data": {"error": "No active session"},
                "message": "Must initialize session first",
            }

        try:
            # Create subdirectory for data type
            data_dir = self.session_path / data_type
            data_dir.mkdir(exist_ok=True)

            file_path = data_dir / filename

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            self.stats["files_stored"] += 1

            return {
                "success": True,
                "data": {
                    "file_path": str(file_path),
                    "file_size": file_path.stat().st_size,
                },
                "message": f"Data stored to {filename}",
            }
        except Exception as e:
            return {
                "success": False,
                "data": {"error": str(e)},
                "message": f"Failed to store data to {filename}",
            }

    def retrieve_research_data(
        self, filename: str, data_type: str = "research_data"
    ) -> Dict[str, Any]:
        """
        Retrieve research data from a file.

        Args:
            filename: Name of the file
            data_type: Type of data

        Returns:
            Success response with data
        """
        if not self.enabled:
            return {"success": True, "message": "Temp file management disabled"}

        if not self.session_path:
            return {
                "success": False,
                "data": {"error": "No active session"},
                "message": "Must initialize session first",
            }

        try:
            file_path = self.session_path / data_type / filename

            if not file_path.exists():
                return {
                    "success": False,
                    "data": {"error": "File not found"},
                    "message": f"File {filename} not found",
                }

            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            self.stats["files_retrieved"] += 1

            return {
                "success": True,
                "data": data,
                "message": f"Data retrieved from {filename}",
            }
        except Exception as e:
            return {
                "success": False,
                "data": {"error": str(e)},
                "message": f"Failed to retrieve data from {filename}",
            }

    def list_session_files(self, data_type: Optional[str] = None) -> Dict[str, Any]:
        """
        List files in the current session.

        Args:
            data_type: Optional data type filter

        Returns:
            Success response with file list
        """
        if not self.enabled:
            return {"success": True, "message": "Temp file management disabled"}

        if not self.session_path:
            return {
                "success": False,
                "data": {"error": "No active session"},
                "message": "Must initialize session first",
            }

        try:
            files = []

            if data_type:
                data_dir = self.session_path / data_type
                if data_dir.exists():
                    for file_path in data_dir.iterdir():
                        if file_path.is_file():
                            files.append(
                                {
                                    "name": file_path.name,
                                    "path": str(file_path),
                                    "size": file_path.stat().st_size,
                                    "type": data_type,
                                }
                            )
            else:
                # List all files in session
                for item in self.session_path.rglob("*"):
                    if item.is_file():
                        relative_path = item.relative_to(self.session_path)
                        files.append(
                            {
                                "name": item.name,
                                "path": str(item),
                                "size": item.stat().st_size,
                                "type": str(relative_path.parent),
                            }
                        )

            return {
                "success": True,
                "data": {
                    "files": files,
                    "count": len(files),
                    "session_id": self.current_session_id,
                },
                "message": f"Found {len(files)} files",
            }
        except Exception as e:
            return {
                "success": False,
                "data": {"error": str(e)},
                "message": "Failed to list session files",
            }

    def cleanup_session(self) -> Dict[str, Any]:
        """
        Clean up the current session.

        Returns:
            Success response
        """
        if not self.enabled:
            return {"success": True, "message": "Temp file management disabled"}

        if not self.session_path:
            return {
                "success": True,
                "message": "No active session to clean up",
            }

        try:
            import shutil

            if self.session_path.exists():
                shutil.rmtree(self.session_path)

            self.current_session_id = None
            self.session_path = None

            return {
                "success": True,
                "data": {"cleaned_session": True},
                "message": "Session cleaned up successfully",
            }
        except Exception as e:
            return {
                "success": False,
                "data": {"error": str(e)},
                "message": "Failed to clean up session",
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Get basic statistics."""
        return {
            "success": True,
            "data": {
                "sessions_created": self.stats["sessions_created"],
                "files_stored": self.stats["files_stored"],
                "files_retrieved": self.stats["files_retrieved"],
                "current_session": self.current_session_id,
                "base_directory": str(self.base_directory),
            },
            "message": "Statistics retrieved successfully",
        }
