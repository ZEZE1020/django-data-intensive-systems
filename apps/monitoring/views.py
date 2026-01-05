"""
Views for the monitoring app.
"""

from prometheus_client import generate_latest
from django.http import HttpResponse

from apps.monitoring.metrics import REGISTRY


def metrics_view(request):
    """
    Expose Prometheus metrics.
    """
    return HttpResponse(generate_latest(REGISTRY), content_type='text/plain; version=0.0.4')
