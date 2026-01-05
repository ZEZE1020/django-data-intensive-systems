"""
Sensors Django admin configuration.
"""

from django.contrib import admin

from apps.core.admin import CoreAdminMixin, SoftDeleteAdminMixin
from apps.sensors.models import Device, SensorReading, SensorAggregate


@admin.register(Device)
class DeviceAdmin(SoftDeleteAdminMixin):
    """Admin interface for Device model."""

    list_display = ['name', 'device_id', 'device_type', 'is_active', 'last_reading_at']
    list_filter = ['device_type', 'is_active', 'deleted', 'created_at']
    search_fields = ['name', 'device_id', 'location']
    readonly_fields = ['created_at', 'updated_at', 'last_reading_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('device_id', 'name', 'device_type', 'location'),
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_active', 'last_reading_at'),
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
        ('Soft Delete', {
            'fields': ('deleted', 'deleted_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(SensorReading)
class SensorReadingAdmin(CoreAdminMixin):
    """Admin interface for SensorReading model."""

    list_display = ['device', 'value', 'unit', 'is_valid', 'created_at']
    list_filter = ['device', 'is_valid', 'unit', 'created_at']
    search_fields = ['device__name', 'device__device_id']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Reading Data', {
            'fields': ('device', 'value', 'unit', 'is_valid'),
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of readings (append-only)."""
        return False


@admin.register(SensorAggregate)
class SensorAggregateAdmin(CoreAdminMixin):
    """Admin interface for SensorAggregate model."""

    list_display = ['device', 'bucket', 'bucket_start', 'avg_value', 'count']
    list_filter = ['device', 'bucket', 'bucket_start']
    search_fields = ['device__name']
    readonly_fields = ['created_at', 'device', 'bucket', 'bucket_start', 'bucket_end']
    fieldsets = (
        ('Aggregate Info', {
            'fields': ('device', 'bucket', 'bucket_start', 'bucket_end'),
        }),
        ('Statistics', {
            'fields': ('min_value', 'max_value', 'avg_value', 'count', 'valid_count'),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        """Prevent manual creation (aggregates are auto-generated)."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of aggregates."""
        return False
