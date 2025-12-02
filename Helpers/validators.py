"""Input validation functions for user inputs and configuration."""

import re
from pathlib import Path
from typing import Tuple


def validate_username(username: str) -> str:
    """
    Validate livelib username format.

    Args:
        username: Username to validate

    Returns:
        Validated and stripped username

    Raises:
        ValueError: If username is empty or has invalid format
    """
    if not username or not username.strip():
        raise ValueError("Username cannot be empty")

    # Strip whitespace before validation
    username = username.strip()

    # Username should be alphanumeric, dash, underscore
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise ValueError(f"Invalid username format: {username}")

    return username


def validate_file_path(filepath: str, must_exist: bool = False) -> str:
    """
    Validate file path for security.

    Args:
        filepath: Path to validate
        must_exist: Whether file must already exist

    Returns:
        Validated absolute path as string

    Raises:
        ValueError: If path attempts traversal outside current directory
        FileNotFoundError: If must_exist=True and file doesn't exist
    """
    path = Path(filepath).resolve()

    # Prevent path traversal - ensure path is within or equal to current directory
    cwd = Path.cwd().resolve()
    try:
        path.relative_to(cwd)
    except ValueError:
        raise ValueError(f"File path must be within current directory: {filepath}")

    if must_exist and not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    return str(path)


def validate_delay(min_delay: int, max_delay: int) -> Tuple[int, int]:
    """
    Validate delay range.

    Args:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds

    Returns:
        Tuple of (min_delay, max_delay)

    Raises:
        ValueError: If delays are negative or min > max
    """
    if min_delay < 0 or max_delay < 0:
        raise ValueError("Delays must be non-negative")

    if min_delay > max_delay:
        raise ValueError(f"min_delay ({min_delay}) cannot exceed max_delay ({max_delay})")

    return min_delay, max_delay


def validate_file_extension(filepath: str, allowed_extensions: list) -> str:
    """
    Validate file extension.

    Args:
        filepath: File path to check
        allowed_extensions: List of allowed extensions (without dot)

    Returns:
        File extension (without dot)

    Raises:
        ValueError: If extension is not allowed
    """
    ext = Path(filepath).suffix[1:]  # Remove leading dot
    if ext not in allowed_extensions:
        raise ValueError(f"Unsupported file extension: {ext}. Allowed: {', '.join(allowed_extensions)}")
    return ext


def validate_driver_type(driver: str, supported_drivers: list) -> str:
    """
    Validate driver type.

    Args:
        driver: Driver type to validate
        supported_drivers: List of supported driver types

    Returns:
        Validated driver type

    Raises:
        ValueError: If driver type is not supported
    """
    if driver not in supported_drivers:
        raise ValueError(f"Unsupported driver: {driver}. Supported: {', '.join(supported_drivers)}")
    return driver
