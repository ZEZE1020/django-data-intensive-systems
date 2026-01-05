"""
Orders app configuration.

E-commerce order management module.
Handles order creation, line items, payment processing, and fulfillment.
"""

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Configuration for the orders app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
    verbose_name = 'Orders'

    def ready(self):
        """App initialization hook."""
        # Import signal handlers for order status changes, payments
        # from . import signals  # noqa
        pass
