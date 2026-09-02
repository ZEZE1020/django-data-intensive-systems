"""Settings used by the automated test suite."""

from .development import *  # noqa: F401, F403

DEBUG = False
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
}
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []