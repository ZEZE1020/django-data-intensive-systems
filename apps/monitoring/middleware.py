"""
Request middleware for logging and tracing.

Captures request metadata, execution time, and optional distributed tracing.

Usage (automatically loaded from settings.MIDDLEWARE):
    - RequestLoggingMiddleware: Logs all HTTP requests with duration
    - RequestTracingMiddleware: Adds request tracing headers (correlation ID)
"""

import logging
import time
import uuid
from django.utils.deprecation import MiddlewareMixin
from apps.monitoring.metrics import requests_total, request_duration_seconds

logger = logging.getLogger(__name__)


class MetricsMiddleware(MiddlewareMixin):
    """
    Middleware to capture Prometheus metrics for each request.
    """
    def process_request(self, request):
        """Record request start time."""
        request.start_time = time.time()

    def process_response(self, request, response):
        """Record request metrics."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Record request duration
            request_duration_seconds.labels(
                method=request.method,
                endpoint=request.path
            ).observe(duration)

            # Record request count
            requests_total.labels(
                method=request.method,
                endpoint=request.path,
                status=response.status_code
            ).inc()

        return response



class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log HTTP requests with duration and status.

    Logs:
      - HTTP method and path
      - Response status code
      - Request duration in ms
      - User ID (if authenticated)
    """

    def process_request(self, request):
        """Record request start time."""
        request._start_time = time.time()

    def process_response(self, request, response):
        """Log request details."""
        if not hasattr(request, '_start_time'):
            return response

        duration_ms = (time.time() - request._start_time) * 1000
        user_id = request.user.id if request.user.is_authenticated else None

        log_extra = {
            'method': request.method,
            'path': request.path_info, # Log path without query parameters
            'status_code': response.status_code,
            'duration_ms': duration_ms,
            'user_id': user_id,
            'correlation_id': getattr(request, 'correlation_id', None),
            'request_id': getattr(request, 'request_id', None),
            'content_length': len(response.content) if hasattr(response, 'content') else 0,
        }

        # Add query parameters, which will be redacted by JSONFormatter if sensitive
        if request.GET:
            log_extra['query_params'] = dict(request.GET)

        logger.info(
            f'{request.method} {request.path_info}', # Log path without query parameters
            extra=log_extra,
        )

        return response


class RequestTracingMiddleware(MiddlewareMixin):
    """
    Middleware to add distributed tracing support.

    Adds/propagates request correlation ID for end-to-end tracing
    across microservices.

    Standard headers:
      - X-Request-ID: Unique request identifier
      - X-Correlation-ID: Correlation across related requests
    """

    def process_request(self, request):
        """Add/propagate correlation ID."""
        # Check if correlation ID already exists (from upstream service)
        correlation_id = request.headers.get(
            'X-Correlation-ID',
            request.headers.get('X-Request-ID', str(uuid.uuid4())),
        )

        # Store in request for access in views/tasks
        request.correlation_id = correlation_id
        request.request_id = str(uuid.uuid4())

    def process_response(self, request, response):
        """Add tracing headers to response."""
        if hasattr(request, 'correlation_id'):
            response['X-Correlation-ID'] = request.correlation_id
        if hasattr(request, 'request_id'):
            response['X-Request-ID'] = request.request_id

        return response


# TODO: Add OpenTelemetry instrumentation
# TODO: Add span creation for database queries
# TODO: Add span creation for Celery tasks
# TODO: Integrate with distributed tracing backend (Jaeger, Zipkin)
