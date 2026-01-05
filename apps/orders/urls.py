"""
Orders URL configuration.

URL routing for orders API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.orders.views import OrderViewSet

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')

app_name = 'orders'

urlpatterns = [
    path('', include(router.urls)),
]
