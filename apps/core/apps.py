"""
Core app configuration.

This app provides reusable base models, managers, and utilities used
across the entire project.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the core app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core'

    def ready(self):
        """App initialization hook."""
        # Import signal handlers if needed
        # from . import signals  # noqa
        pass
