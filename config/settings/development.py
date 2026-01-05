"""
Django settings for development environment.

Extends base.py with development-specific overrides:
  - Debug mode enabled
  - SQLite database (unless overridden via .env)
  - Verbose logging
  - Development tools (debug toolbar, extensions)
  - No SSL/HTTPS requirements
  - Email console backend
"""

import logging
from .base import *  # noqa: F401, F403

# Development: enable debug mode
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')

# Development middleware additions
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# Internal IPs for debug toolbar
INTERNAL_IPS = ['127.0.0.1', '::1', 'localhost']

# Database: Use SQLite by default in development (unless .env specifies PostgreSQL)
if os.getenv('DB_ENGINE') is None:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

# Cache: Use in-memory cache in development for faster iteration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'django-dev-cache',
    }
}

# Sessions: Use database backend in development for easier debugging
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Logging: More verbose in development
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'
logging.getLogger('django.db.backends').setLevel(logging.DEBUG)

# Security: Disable in development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Email: Use console backend (prints to stdout)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files: Collect in development
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Celery: Use eager task execution in development for synchronous testing
CELERY_TASK_ALWAYS_EAGER = os.getenv('CELERY_TASK_ALWAYS_EAGER', 'True') == 'True'
CELERY_TASK_EAGER_PROPAGATES = True

# Sentry: Disabled in development
SENTRY_DSN = ''

# TODO: Add Sentry initialization when needed
# import sentry_sdk
# sentry_sdk.init(dsn='') if SENTRY_DSN else None
