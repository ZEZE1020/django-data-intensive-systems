"""Monitoring Django admin configuration."""

from django.contrib import admin

from apps.monitoring.models import MonitoringConfig


@admin.register(MonitoringConfig)
class MonitoringConfigAdmin(admin.ModelAdmin):
    """Admin interface for MonitoringConfig."""

    list_display = ['name']
    search_fields = ['name']
