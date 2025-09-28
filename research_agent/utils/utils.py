"""
Utils - Common utility functions for BaseAgent.

This module provides utility functions used across the BaseAgent module,
including input validation, response formatting, and helper functions.
"""

import json
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


def validate_input_data(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Validate input data against a JSON schema.

    Args:
        data: Input data to validate
        schema: JSON schema for validation

    Returns:
        True if valid, False otherwise
    """
    try:
        # Basic validation - can be enhanced with jsonschema library
        if not isinstance(data, dict):
            return False

        # Check required fields
        for field in schema.get("required", []):
            if field not in data:
                return False

        # Validate field types
        for field, value in data.items():
            if field in schema.get("properties", {}):
                field_schema = schema["properties"][field]
                if not _validate_field_type(value, field_schema):
                    return False

        return True
    except Exception:
        return False


def _validate_field_type(value: Any, field_schema: Dict[str, Any]) -> bool:
    """
    Validate a field value against its schema.

    Args:
        value: Value to validate
        field_schema: Schema for the field

    Returns:
        True if valid, False otherwise
    """
    expected_type = field_schema.get("type")

    if expected_type == "string":
        if not isinstance(value, str):
            return False

        # Check string constraints
        if "minLength" in field_schema and len(value) < field_schema["minLength"]:
            return False
        if "maxLength" in field_schema and len(value) > field_schema["maxLength"]:
            return False

        # Check pattern if specified
        if "pattern" in field_schema:
            if not re.match(field_schema["pattern"], value):
                return False

    elif expected_type == "integer":
        if not isinstance(value, int):
            return False

        # Check integer constraints
        if "minimum" in field_schema and value < field_schema["minimum"]:
            return False
        if "maximum" in field_schema and value > field_schema["maximum"]:
            return False

    elif expected_type == "boolean":
        if not isinstance(value, bool):
            return False

    elif expected_type == "array":
        if not isinstance(value, list):
            return False

        # Check array constraints
        if "minItems" in field_schema and len(value) < field_schema["minItems"]:
            return False
        if "maxItems" in field_schema and len(value) > field_schema["maxItems"]:
            return False

    elif expected_type == "object":
        if not isinstance(value, dict):
            return False

    return True


def format_response(
    success: bool,
    data: Any = None,
    message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Format a standardized response.

    Args:
        success: Whether the operation was successful
        data: Response data
        message: Response message
        metadata: Additional metadata

    Returns:
        Formatted response dictionary
    """
    response = {
        "success": success,
        "timestamp": datetime.utcnow().isoformat(),
        "response_id": str(uuid.uuid4()),
    }

    if data is not None:
        response["data"] = data

    if message is not None:
        response["message"] = message

    if metadata is not None:
        response["metadata"] = metadata

    return response


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """
    Sanitize a string for safe processing.

    Args:
        text: Text to sanitize
        max_length: Maximum length of the result

    Returns:
        Sanitized string
    """
    if not isinstance(text, str):
        text = str(text)

    # Remove control characters
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)

    # Truncate if too long
    if len(text) > max_length:
        text = text[: max_length - 3] + "..."

    return text.strip()


def generate_session_id() -> str:
    """
    Generate a unique session ID.

    Returns:
        Unique session ID string
    """
    return f"session_{int(datetime.utcnow().timestamp())}_{str(uuid.uuid4())[:8]}"


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """
    Safely parse JSON string with fallback.

    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """
    Safely serialize data to JSON string with fallback.

    Args:
        data: Data to serialize
        default: Default string if serialization fails

    Returns:
        JSON string or default string
    """
    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError):
        return default


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries, with later ones taking precedence.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def extract_key_value_pairs(
    text: str, pattern: str = r"(\w+):\s*([^\n]+)"
) -> Dict[str, str]:
    """
    Extract key-value pairs from text using regex pattern.

    Args:
        text: Text to extract from
        pattern: Regex pattern for key-value pairs

    Returns:
        Dictionary of extracted key-value pairs
    """
    matches = re.findall(pattern, text)
    return {key.strip(): value.strip() for key, value in matches}


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        url: String to check

    Returns:
        True if valid URL, False otherwise
    """
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return bool(url_pattern.match(url))


def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format.

    Returns:
        Current timestamp as ISO string
    """
    return datetime.utcnow().isoformat()


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.

    Args:
        text: Text to normalize

    Returns:
        Text with normalized whitespace
    """
    # Replace multiple whitespace with single space
    text = re.sub(r"\s+", " ", text)
    # Remove leading/trailing whitespace
    return text.strip()
