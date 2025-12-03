"""Helper utility functions."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import re


def parse_error_codes(error_code_string: str) -> list[str]:
    """
    Parse comma-separated error codes into a list.

    Args:
        error_code_string: Comma-separated error codes (e.g., "30001,30002,30003")

    Returns:
        List of error code strings
    """
    if not error_code_string:
        return []

    return [code.strip() for code in error_code_string.split(",") if code.strip()]


def is_within_time_window(
    timestamp: datetime, window_minutes: int, reference_time: Optional[datetime] = None
) -> bool:
    """
    Check if a timestamp is within a time window.

    Args:
        timestamp: Timestamp to check
        window_minutes: Time window in minutes
        reference_time: Reference time (defaults to now)

    Returns:
        True if timestamp is within the window
    """
    if reference_time is None:
        reference_time = datetime.utcnow()

    window_start = reference_time - timedelta(minutes=window_minutes)
    return window_start <= timestamp <= reference_time


def sanitize_phone_number(phone: Optional[str]) -> Optional[str]:
    """
    Sanitize phone number for storage.

    Args:
        phone: Phone number string

    Returns:
        Sanitized phone number or None
    """
    if not phone:
        return None

    # Remove all non-digit characters except +
    sanitized = re.sub(r"[^\d+]", "", phone)
    return sanitized if sanitized else None


def safe_dict_get(data: Dict[Any, Any], *keys, default=None) -> Any:
    """
    Safely get nested dictionary value.

    Args:
        data: Dictionary to search
        *keys: Keys to traverse
        default: Default value if key not found

    Returns:
        Value at the nested key or default

    Example:
        safe_dict_get({"a": {"b": {"c": 1}}}, "a", "b", "c")  # Returns 1
        safe_dict_get({"a": {"b": {}}}, "a", "b", "c", default=0)  # Returns 0
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix
