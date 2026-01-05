"""
Sensors URL configuration.

URL routing for sensors API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.sensors.views import (
    DeviceViewSet,
    SensorReadingViewSet,
    SensorAggregateViewSet,
)

router = DefaultRouter()
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'readings', SensorReadingViewSet, basename='reading')
router.register(r'aggregates', SensorAggregateViewSet, basename='aggregate')

app_name = 'sensors'

urlpatterns = [
    path('', include(router.urls)),
]
