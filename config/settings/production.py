"""
Django settings for production environment.

Extends base.py with production-specific overrides:
  - Debug mode disabled
  - PostgreSQL required
  - Minimal logging (only warnings/errors)
  - Strict security settings (SSL, HTTPS, secure cookies)
  - Sentry error tracking enabled
  - Prometheus metrics enabled
  - Email via SMTP
"""

import logging

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .base import *  # noqa: F401, F403

# Production: Disable debug
DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ValueError('ALLOWED_HOSTS must be set in production')

# Remove development apps
INSTALLED_APPS = [app for app in INSTALLED_APPS 
                  if app not in ['debug_toolbar', 'django_extensions']]
MIDDLEWARE = [m for m in MIDDLEWARE 
              if m not in ['debug_toolbar.middleware.DebugToolbarMiddleware']]

# Database: PostgreSQL required in production
if os.getenv('DB_ENGINE') is None or os.getenv('DB_ENGINE') == 'django.db.backends.sqlite3':
    raise ValueError('PostgreSQL required in production. Set DB_ENGINE=django.db.backends.postgresql')

# Cache: Redis required in production
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_CACHE_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'RETRY_ON_TIMEOUT': True,
        }
    }
}

# Sessions: Use Redis in production for distributed systems
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Logging: Only warnings and errors in production
LOGGING['handlers']['console']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps']['level'] = 'WARNING'
logging.getLogger('django.db.backends').setLevel(logging.WARNING)

# Security: Strict settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'style-src': ("'self'", "'unsafe-inline'"),
    'script-src': ("'self'",),
}

# HSTS: Strict Transport Security
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Clickjacking protection
X_FRAME_OPTIONS = 'DENY'

# Email: Use SMTP in production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    raise ValueError('EMAIL_HOST_USER and EMAIL_HOST_PASSWORD required in production')

# Static files: WhiteNoise serves in production
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Celery: Async task execution in production
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False

# Sentry error tracking
SENTRY_DSN = os.getenv('SENTRY_DSN', '')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=float(os.getenv('SENTRY_TRACE_SAMPLE_RATE', 0.1)),
        send_default_pii=False,
        environment=os.getenv('ENVIRONMENT', 'production'),
    )

# TODO: Configure APM (Application Performance Monitoring)
# TODO: Set up log aggregation (Datadog, ELK, etc.)
# TODO: Configure CDN for static assets
