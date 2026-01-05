"""
Monitoring app configuration.

Observability and monitoring module for metrics, logging, and health checks.
"""

from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    """Configuration for the monitoring app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.monitoring'
    verbose_name = 'Monitoring'

    def ready(self):
        """App initialization hook."""
        # Initialize Prometheus metrics
        # from .metrics import init_metrics
        # init_metrics()
        pass
