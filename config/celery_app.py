"""
Celery configuration and app initialization.

This module sets up Celery for asynchronous task processing.
Tasks are automatically discovered from app_label.tasks modules.

Usage:
    # In your Django code
    from config.celery_app import app
    
    # Or use the decorator
    from celery import shared_task
    
    @shared_task
    def my_task():
        pass

Reference: https://docs.celeryproject.io/en/stable/django/
"""

import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Create Celery app
app = Celery('config')

# Load configuration from Django settings
# Uses all settings with 'CELERY_' prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Aggregate sensor readings every 5 minutes
    'aggregate-sensor-readings': {
        'task': 'apps.sensors.tasks.aggregate_readings',
        'schedule': crontab(minute='*/5'),
        'options': {'queue': 'sensors'},
    },
    # Clean up old sensor data every hour
    'cleanup-sensor-data': {
        'task': 'apps.sensors.tasks.cleanup_old_readings',
        'schedule': crontab(minute=0),
        'options': {'queue': 'sensors'},
    },
    # Process pending orders every minute
    'process-pending-orders': {
        'task': 'apps.orders.tasks.process_pending_orders',
        'schedule': crontab(minute='*'),
        'options': {'queue': 'orders'},
    },
    # Retry failed payments every 5 minutes
    'retry-failed-payments': {
        'task': 'apps.orders.tasks.retry_failed_payments',
        'schedule': crontab(minute='*/5'),
        'options': {'queue': 'orders'},
    },
}

# Task routing: direct tasks to specific queues
app.conf.task_routes = {
    'apps.sensors.tasks.*': {'queue': 'sensors'},
    'apps.orders.tasks.*': {'queue': 'orders'},
    'apps.monitoring.tasks.*': {'queue': 'default'},
}

# Task time limits (hard limit: 30min, soft limit: 25min)
app.conf.task_time_limit = 30 * 60
app.conf.task_soft_time_limit = 25 * 60

# TODO: Add task error notifications (email, Sentry)
# TODO: Add task retry strategies with exponential backoff
# TODO: Add task result backend cleanup
# TODO: Configure Celery monitoring (Flower)
