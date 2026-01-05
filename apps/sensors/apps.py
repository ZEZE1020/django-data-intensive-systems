"""
Sensors app configuration.

High-throughput sensor data ingestion module.
Handles device registration, sensor readings, and time-series aggregation.
"""

from django.apps import AppConfig


class SensorsConfig(AppConfig):
    """Configuration for the sensors app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sensors'
    verbose_name = 'Sensors'

    def ready(self):
        """App initialization hook."""
        # Import signal handlers for cleanup, aggregation
        # from . import signals  # noqa
        pass
