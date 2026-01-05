"""
Core utilities.

Shared utility functions for formatting, validation, and common operations.

Usage:
    from apps.core.utils import format_decimal, validate_email, parse_phone
"""

import json
import logging
import re
from decimal import Decimal
from typing import Any, Optional

logger = logging.getLogger(__name__)


def format_decimal(value: Decimal, places: int = 2) -> str:
    """
    Format a Decimal value with specified decimal places.

    Args:
        value: Decimal value to format
        places: Number of decimal places (default: 2)

    Returns:
        Formatted decimal string (e.g., '19.99')
    """
    if value is None:
        return '0.00'
    return f'{value:.{places}f}'


def parse_decimal(value: str) -> Optional[Decimal]:
    """
    Parse a string into a Decimal value.

    Args:
        value: String value to parse

    Returns:
        Decimal value or None if invalid
    """
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return None


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.lower()))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (basic).

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    # Allow various formats: +1-234-567-8900, (234) 567-8900, 2345678900
    pattern = r'^(\+\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
    return bool(re.match(pattern, phone.replace(' ', '')))


def safe_json_serialize(obj: Any) -> str:
    """
    Safely serialize an object to JSON.

    Handles common edge cases like Decimal, datetime, UUID.

    Args:
        obj: Object to serialize

    Returns:
        JSON string
    """
    from decimal import Decimal
    from datetime import datetime
    from uuid import UUID

    def default_handler(o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, UUID):
            return str(o)
        raise TypeError(f'Object of type {type(o)} is not JSON serializable')

    return json.dumps(obj, default=default_handler)


def parse_json_safe(data: str, default: Any = None) -> Any:
    """
    Safely parse JSON data.

    Args:
        data: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Parsed object or default value
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError, ValueError):
        logger.warning(f'Failed to parse JSON: {data}')
        return default


def truncate_string(value: str, length: int, suffix: str = '...') -> str:
    """
    Truncate a string to a maximum length with suffix.

    Args:
        value: String to truncate
        length: Maximum length
        suffix: Suffix to append if truncated (default: '...')

    Returns:
        Truncated string
    """
    if value and len(value) > length:
        return value[:length - len(suffix)] + suffix
    return value


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes into human-readable format (KB, MB, GB, etc.).

    Args:
        bytes_value: Number of bytes

    Returns:
        Formatted string (e.g., '1.5 MB')
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024:
            return f'{bytes_value:.1f} {unit}'
        bytes_value /= 1024
    return f'{bytes_value:.1f} PB'


def format_duration(seconds: int) -> str:
    """
    Format seconds into human-readable duration.

    Args:
        seconds: Number of seconds

    Returns:
        Formatted string (e.g., '1h 30m 45s')
    """
    intervals = [
        ('week', 604800),
        ('day', 86400),
        ('hour', 3600),
        ('minute', 60),
        ('second', 1),
    ]

    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            result.append(f'{value}{name[0]}')
            seconds %= count

    return ' '.join(result) or '0s'


def generate_reference_code(prefix: str = '', length: int = 8) -> str:
    """
    Generate a unique reference code.

    Args:
        prefix: Prefix for the code (e.g., 'ORD-' for orders)
        length: Length of random portion

    Returns:
        Generated reference code (e.g., 'ORD-A1B2C3D4')
    """
    import secrets
    import string

    chars = string.ascii_uppercase + string.digits
    random_part = ''.join(secrets.choice(chars) for _ in range(length))
    return f'{prefix}{random_part}' if prefix else random_part


# TODO: Add rate limiting utilities
# TODO: Add caching decorators
# TODO: Add retry logic
