"""
Prometheus metrics setup.

Exports application metrics for Prometheus scraping.

Usage:
    from apps.monitoring.metrics import request_duration_seconds, requests_total
    
    @request_duration_seconds.time()
    def expensive_operation():
        pass

Endpoints:
    GET /metrics/ - Prometheus metrics export

Reference: https://github.com/prometheus/client_python
"""

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

# Create registry
REGISTRY = CollectorRegistry()

# Request metrics
requests_total = Counter(
    'requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY,
)

request_duration_seconds = Histogram(
    'request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=REGISTRY,
)

# Database metrics
database_queries = Counter(
    'database_queries_total',
    'Total database queries',
    ['operation', 'table'],
    registry=REGISTRY,
)

database_duration_seconds = Histogram(
    'database_duration_seconds',
    'Database query duration in seconds',
    ['operation'],
    registry=REGISTRY,
)

# Celery metrics
celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total Celery tasks',
    ['task_name', 'status'],
    registry=REGISTRY,
)

celery_task_duration_seconds = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_name'],
    registry=REGISTRY,
)

# Business metrics
sensor_readings_total = Counter(
    'sensor_readings_total',
    'Total sensor readings ingested',
    ['device_type'],
    registry=REGISTRY,
)

orders_total = Counter(
    'orders_total',
    'Total orders created',
    ['status'],
    registry=REGISTRY,
)

payments_total = Counter(
    'payments_total',
    'Total payment transactions',
    ['method', 'status'],
    registry=REGISTRY,
)

# Custom gauges
active_devices = Gauge(
    'active_devices',
    'Number of active sensor devices',
    registry=REGISTRY,
)

pending_orders = Gauge(
    'pending_orders',
    'Number of pending orders',
    registry=REGISTRY,
)


def init_metrics():
    """Initialize metrics (register collectors, etc.)."""
    # TODO: Initialize background tasks to update gauges
    pass


# TODO: Add middleware to automatically record metrics
# TODO: Add distributed tracing metrics (span duration, errors)
# TODO: Add cache hit/miss metrics
# TODO: Add queue length metrics
