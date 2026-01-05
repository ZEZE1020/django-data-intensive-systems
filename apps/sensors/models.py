"""
Sensors models.

Models for high-throughput sensor data ingestion:
  - Device: Physical device that generates readings
  - SensorReading: Individual sensor measurement (high volume)
  - SensorAggregate: Time-bucketed aggregates (5min, hourly, daily)

Design patterns:
  - Time-series partitioning hints for PostgreSQL
  - Batch inserts for high-throughput ingestion
  - Aggregation for efficient querying
"""

from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.core.mixins import TimeStampedModel, SoftDeleteModel, TenantAwareModel
from apps.core.managers import TenantAwareManager


class Device(TimeStampedModel, SoftDeleteModel, TenantAwareModel):
    """
    Physical sensor device.

    A device can have multiple sensors and generate many readings over time.
    Soft-deletable for audit trails.
    """

    device_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text='Unique device identifier (MAC, serial number, etc.)',
    )
    name = models.CharField(
        max_length=255,
        help_text='Human-readable device name',
    )
    device_type = models.CharField(
        max_length=50,
        choices=[
            ('temperature', 'Temperature Sensor'),
            ('humidity', 'Humidity Sensor'),
            ('pressure', 'Pressure Sensor'),
            ('motion', 'Motion Detector'),
            ('light', 'Light Sensor'),
            ('custom', 'Custom Sensor'),
        ],
        help_text='Type of sensor device',
    )
    location = models.CharField(
        max_length=255,
        help_text='Physical location of device',
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='GPS latitude',
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text='GPS longitude',
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Whether device is actively reporting',
    )
    last_reading_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text='Timestamp of last received reading',
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional device configuration (firmware version, etc.)',
    )

    objects = TenantAwareManager()

    class Meta:
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device_type', 'is_active']),
            models.Index(fields=['deleted', 'is_active']),
            models.Index(fields=['last_reading_at']),
        ]
        # TODO: Add partitioning hint for high-volume sensors
        # PARTITION BY RANGE (YEAR(created_at))

    def __str__(self):
        return f'{self.name} ({self.device_id})'


class SensorReading(TimeStampedModel, TenantAwareModel):
    """
    Individual sensor measurement.

    Designed for high-throughput ingestion. Readings should be batched
    on insert for better performance.

    Note: No soft-delete; readings are immutable.
    """

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='readings',
        help_text='Device that generated this reading',
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text='Sensor measurement value',
    )
    unit = models.CharField(
        max_length=20,
        default='',
        blank=True,
        help_text='Unit of measurement (°C, %, hPa, etc.)',
    )
    is_valid = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Whether reading passed validation',
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional reading data (raw value, RSSI, etc.)',
    )

    objects = TenantAwareManager()

    class Meta:
        verbose_name = 'Sensor Reading'
        verbose_name_plural = 'Sensor Readings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', 'created_at']),
            models.Index(fields=['created_at', 'is_valid']),
            models.Index(fields=['is_valid']),
        ]
        # TODO: Add time-series partitioning for high-volume ingestion
        # PARTITION BY RANGE (MONTH(created_at))
        # Partition readings by month to manage table size

    def __str__(self):
        return f'{self.device.name}: {self.value}{self.unit} at {self.created_at}'


class SensorAggregate(TimeStampedModel, TenantAwareModel):
    """
    Time-bucketed sensor data aggregates.

    Pre-computed statistics for efficient querying:
      - min_value, max_value, avg_value: Descriptive statistics
      - count: Number of readings in bucket
      - valid_count: Number of valid readings

    Buckets: 5-minute, 1-hour, 1-day

    Populated by Celery tasks for batch aggregation.
    """

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='aggregates',
        help_text='Device being aggregated',
    )
    bucket = models.CharField(
        max_length=10,
        choices=[
            ('5min', '5 Minutes'),
            ('1hour', '1 Hour'),
            ('1day', '1 Day'),
        ],
        help_text='Aggregation time bucket',
    )
    bucket_start = models.DateTimeField(
        db_index=True,
        help_text='Start timestamp of this bucket',
    )
    bucket_end = models.DateTimeField(
        help_text='End timestamp of this bucket',
    )
    min_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text='Minimum value in bucket',
    )
    max_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text='Maximum value in bucket',
    )
    avg_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text='Average value in bucket',
    )
    count = models.PositiveIntegerField(
        default=0,
        help_text='Total readings in bucket',
    )
    valid_count = models.PositiveIntegerField(
        default=0,
        help_text='Valid readings in bucket',
    )

    objects = TenantAwareManager()

    class Meta:
        verbose_name = 'Sensor Aggregate'
        verbose_name_plural = 'Sensor Aggregates'
        ordering = ['-bucket_start']
        unique_together = ('device', 'bucket', 'bucket_start')
        indexes = [
            models.Index(fields=['device', 'bucket', 'bucket_start']),
            models.Index(fields=['bucket_start', 'bucket_end']),
        ]
        # TODO: Add partitioning for efficient querying
        # PARTITION BY RANGE (MONTH(bucket_start))

    def __str__(self):
        return f'{self.device.name} {self.bucket} @ {self.bucket_start}'
