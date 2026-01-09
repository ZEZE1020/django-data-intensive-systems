"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

import os

from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin interface
    path(os.getenv('DJANGO_ADMIN_URL', 'admin/'), admin.site.urls),

    # Health checks and monitoring
    path('', include('apps.monitoring.urls')),

    # App-specific URLs
    path('api/sensors/', include('apps.sensors.urls')),
    path('api/orders/', include('apps.orders.urls')),
]

# TODO: Add API documentation endpoint (requires coreapi)
# path('api/docs/', include_docs_urls(...))

# Debug toolbar in development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# TODO: Add API versioning strategy (e.g., /api/v1/, /api/v2/)
# TODO: Add pagination documentation
# TODO: Add API error response documentation
