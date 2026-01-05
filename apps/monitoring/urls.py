"""
URLs for the monitoring app.
"""

from django.urls import path

from apps.monitoring import health_checks, views

urlpatterns = [
    path('health/', health_checks.health_check, name='health-check'),
    path('health/ready/', health_checks.readiness_check, name='readiness-check'),
    path('health/live/', health_checks.liveness_check, name='liveness-check'),
    path('metrics/', views.metrics_view, name='prometheus-metrics'),
]
