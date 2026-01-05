"""
Health check endpoints for Kubernetes / Docker probes.

Provides:
  - /health/: General health status
  - /health/ready/: Readiness probe (ready to accept traffic)
  - /health/live/: Liveness probe (process is alive)

Usage in Docker/Kubernetes:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
"""

import logging
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


def health_check(request):
    """
    General health check endpoint.

    Checks database connectivity and basic service health.
    """
    try:
        # Test database connection
        connection.ensure_connection()
        db_ok = True
    except Exception as e:
        logger.error(f'Database health check failed: {e}')
        db_ok = False

    try:
        # Test cache connectivity
        cache.set('health_check', 'ok', 10)
        cache_ok = cache.get('health_check') == 'ok'
    except Exception as e:
        logger.error(f'Cache health check failed: {e}')
        cache_ok = False

    status_code = 200 if (db_ok and cache_ok) else 503
    return JsonResponse(
        {
            'status': 'healthy' if db_ok and cache_ok else 'unhealthy',
            'checks': {
                'database': 'ok' if db_ok else 'error',
                'cache': 'ok' if cache_ok else 'error',
            },
        },
        status=status_code,
    )


def readiness_check(request):
    """
    Readiness probe for Kubernetes.

    Indicates the service is ready to accept traffic.
    Checks all dependencies (DB, cache, external services).
    """
    try:
        connection.ensure_connection()
        cache.get('readiness_check')
        # TODO: Check external service dependencies (payment gateway, etc.)
        return JsonResponse({'ready': True}, status=200)
    except Exception as e:
        logger.error(f'Readiness check failed: {e}')
        return JsonResponse({'ready': False, 'error': str(e)}, status=503)


def liveness_check(request):
    """
    Liveness probe for Kubernetes.

    Indicates the process is still alive.
    Can recover from temporary failures (DB connection resets, etc.).
    """
    # Simple check: if we can respond, we're alive
    return JsonResponse({'alive': True}, status=200)
