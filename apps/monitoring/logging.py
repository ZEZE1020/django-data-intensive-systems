"""
JSON logging configuration.

Structured logging with JSON output for better log aggregation and analysis.

Usage:
    import logging
    logger = logging.getLogger(__name__)
    logger.info('User logged in', extra={'user_id': 123, 'ip': '192.168.1.1'})

Output:
    {"timestamp": "...", "level": "INFO", "name": "apps.auth", "user_id": 123, ...}

Reference: https://docs.python.org/3/library/logging.html
"""

import json
import logging
import traceback
from datetime import datetime


SENSITIVE_KEYS = (
    'password', 'token', 'secret', 'api_key', 'authorization', 'credential',
    'access_token', 'refresh_token', 'private_key',
    # Common request data keys that might contain sensitive info
    'email', 'username', 'first_name', 'last_name', 'address', 'phone',
    'query_params', 'request_data',
)


def redact_sensitive_data(data):
    """Recursively redact sensitive data from dictionaries and lists."""
    if isinstance(data, dict):
        return {
            key: redact_sensitive_data(value)
            for key, value in data.items()
            if key not in SENSITIVE_KEYS
        }
    elif isinstance(data, list):
        return [redact_sensitive_data(item) for item in data]
    return data


class JSONFormatter(logging.Formatter):
    """
    Custom logging formatter that outputs structured JSON.

    Includes timestamp, level, logger name, message, and any extra fields.
    Sensitive data is redacted before logging.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: LogRecord to format

        Returns:
            JSON string
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info),
            }

        # Add extra fields (e.g., user_id, request_id, etc.)
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in [
                    'name', 'msg', 'args', 'created', 'filename', 'funcName',
                    'levelname', 'levelno', 'lineno', 'module', 'msecs',
                    'message', 'pathname', 'process', 'processName',
                    'relativeCreated', 'thread', 'threadName', 'exc_info',
                    'exc_text', 'stack_info', 'tenant_id', # Added tenant_id to non-sensitive keys
                ] and not key.startswith('_'): # Exclude internal _ keys
                    log_data[key] = value

        # Redact sensitive data
        log_data = redact_sensitive_data(log_data)

        return json.dumps(log_data)


# Logger configuration helper
def configure_json_logging(logger_name: str = None) -> logging.Logger:
    """
    Configure a logger with JSON output.

    Args:
        logger_name: Logger name (default: root)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(logger_name)
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    return logger


# TODO: Add correlation ID tracking
# TODO: Add request context (user, IP, path)
# TODO: Add performance metrics (duration, memory)
# TODO: Integrate with log aggregation (ELK, Datadog, etc.)
