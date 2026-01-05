"""
Sensors DRF serializers.

Serializers for sensor API endpoints with validation and nested relationships.
"""

from rest_framework import serializers

from apps.sensors.models import Device, SensorReading, SensorAggregate


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for Device model."""

    last_reading_age = serializers.SerializerMethodField(
        read_only=True,
        help_text='Time since last reading in seconds',
    )

    class Meta:
        model = Device
        fields = [
            'id',
            'device_id',
            'name',
            'device_type',
            'location',
            'latitude',
            'longitude',
            'is_active',
            'last_reading_at',
            'last_reading_age',
            'metadata',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_reading_at']

    def get_last_reading_age(self, obj):
        """Calculate time since last reading."""
        if obj.last_reading_at is None:
            return None
        from django.utils import timezone
        delta = timezone.now() - obj.last_reading_at
        return int(delta.total_seconds())


class SensorReadingSerializer(serializers.ModelSerializer):
    """Serializer for SensorReading model."""

    device_name = serializers.CharField(
        source='device.name',
        read_only=True,
        help_text='Human-readable device name',
    )

    class Meta:
        model = SensorReading
        fields = [
            'id',
            'device',
            'device_name',
            'value',
            'unit',
            'is_valid',
            'metadata',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_value(self, value):
        """Validate sensor value is numeric."""
        if value is None:
            raise serializers.ValidationError('Sensor value cannot be null.')
        return value


class SensorReadingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating SensorReading instances, primarily for bulk ingestion.
    Excludes the 'device' field as it's handled by the bulk serializer.
    """
    class Meta:
        model = SensorReading
        fields = [
            'value',
            'unit',
            'is_valid',
            'metadata',
        ]

    def validate_value(self, value):
        """Validate sensor value is numeric."""
        if value is None:
            raise serializers.ValidationError('Sensor value cannot be null.')
        return value


class SensorReadingBulkSerializer(serializers.Serializer):
    """Serializer for bulk sensor reading ingestion."""

    device_id = serializers.CharField(
        max_length=100,
        help_text='Device identifier',
    )
    readings = serializers.ListField(
        child=SensorReadingCreateSerializer(), # Use the dedicated create serializer
        help_text='List of readings: [{"value": 23.5, "unit": "°C", ...}, ...]',
    )

    def validate_readings(self, readings):
        """Validate readings list is not empty."""
        if not readings:
            raise serializers.ValidationError('Must provide at least one reading.')
        if len(readings) > 1000:
            raise serializers.ValidationError('Cannot submit more than 1000 readings at once.')
        return readings


class SensorAggregateSerializer(serializers.ModelSerializer):
    """Serializer for SensorAggregate model."""

    device_name = serializers.CharField(
        source='device.name',
        read_only=True,
    )
    bucket_display = serializers.CharField(
        source='get_bucket_display',
        read_only=True,
    )

    class Meta:
        model = SensorAggregate
        fields = [
            'id',
            'device',
            'device_name',
            'bucket',
            'bucket_display',
            'bucket_start',
            'bucket_end',
            'min_value',
            'max_value',
            'avg_value',
            'count',
            'valid_count',
            'created_at',
        ]
        read_only_fields = fields
