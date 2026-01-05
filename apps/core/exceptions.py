"""
Core exceptions.

Custom exceptions for the application. Provides semantic error handling
across all layers (models, views, tasks).

Usage:
    from apps.core.exceptions import ValidationError, RateLimitExceeded
    
    try:
        process_order()
    except RateLimitExceeded as e:
        return Response({'error': str(e)}, status=429)
"""


class BaseAppException(Exception):
    """Base exception for all application-specific exceptions."""

    def __init__(self, message: str, code: str = None, details: dict = None):
        """
        Initialize exception.

        Args:
            message: Human-readable error message
            code: Error code for API responses (e.g., 'INVALID_ORDER')
            details: Additional context dictionary
        """
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAppException):
    """Raised when data validation fails."""

    pass


class RateLimitExceeded(BaseAppException):
    """Raised when rate limit is exceeded."""

    pass


class ResourceNotFound(BaseAppException):
    """Raised when a requested resource is not found."""

    pass


class ConflictError(BaseAppException):
    """Raised on conflict (e.g., concurrent modification)."""

    pass


class ProcessingError(BaseAppException):
    """Raised when background processing fails."""

    pass


class PaymentError(BaseAppException):
    """Raised when payment processing fails."""

    pass


class DataIntegrityError(BaseAppException):
    """Raised when data integrity constraints are violated."""

    pass


class TenantError(BaseAppException):
    """Raised when tenant/multi-tenancy issues occur."""

    pass
