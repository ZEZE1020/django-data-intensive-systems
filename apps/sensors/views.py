"""
Sensors API views.

REST API endpoints for sensor data ingestion and querying.

Endpoints:
  GET  /api/sensors/devices/
  POST /api/sensors/devices/
  GET  /api/sensors/devices/{id}/
  GET  /api/sensors/readings/
  POST /api/sensors/readings/bulk/
  GET  /api/sensors/aggregates/
"""

from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated # Import IsAuthenticated

from apps.sensors.models import Device, SensorReading, SensorAggregate
from apps.sensors.serializers import (
    DeviceSerializer,
    SensorReadingSerializer,
    SensorReadingBulkSerializer,
    SensorAggregateSerializer,
)


class DeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for sensor devices.

    Endpoints:
      GET  /api/sensors/devices/ - List all devices
      POST /api/sensors/devices/ - Create new device
      GET  /api/sensors/devices/{id}/ - Retrieve device
      PATCH /api/sensors/devices/{id}/ - Partial update
      DELETE /api/sensors/devices/{id}/ - Soft-delete device
    """

    queryset = Device.objects.active()
    serializer_class = DeviceSerializer
    filterset_fields = ['device_type', 'is_active']
    search_fields = ['name', 'device_id', 'location']
    ordering_fields = ['created_at', 'last_reading_at']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated] # Add permission class


class SensorReadingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for sensor readings.

    Endpoints:
      GET  /api/sensors/readings/ - List readings with filters
      POST /api/sensors/readings/ - Create single reading
      POST /api/sensors/readings/bulk/ - Bulk create (batch ingestion)
      GET  /api/sensors/readings/{id}/ - Retrieve reading
    """

    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
    filterset_fields = ['device', 'is_valid']
    search_fields = ['device__name', 'device__device_id']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated] # Add permission class

    def create(self, request, *args, **kwargs):
        """Create single reading and update device's last_reading_at."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Update device's last reading timestamp
        device = serializer.validated_data['device']
        device.last_reading_at = timezone.now()
        device.save(update_fields=['last_reading_at'])

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def bulk(self, request):
        """
        Bulk create sensor readings.

        Request body:
            {
                "device_id": "device-123",
                "readings": [
                    {"value": 23.5, "unit": "°C", "is_valid": true},
                    {"value": 45.2, "unit": "%", "is_valid": true},
                ]
            }
        """
        serializer = SensorReadingBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            device = Device.objects.get(device_id=serializer.validated_data['device_id'])
        except Device.DoesNotExist:
            return Response(
                {'error': f'Device {serializer.validated_data["device_id"]} not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create readings in batch
        readings = [
            SensorReading(device=device, **reading_data)
            for reading_data in serializer.validated_data['readings']
        ]
        created = SensorReading.objects.bulk_create(
            readings,
            batch_size=500,
        )

        # Update device's last reading timestamp
        device.last_reading_at = timezone.now()
        device.save(update_fields=['last_reading_at'])

        return Response(
            {
                'count': len(created),
                'message': f'{len(created)} readings created',
            },
            status=status.HTTP_201_CREATED,
        )


class SensorAggregateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for sensor aggregates.

    Populated by Celery tasks, not directly writable via API.

    Endpoints:
      GET  /api/sensors/aggregates/ - List aggregates with filters
      GET  /api/sensors/aggregates/{id}/ - Retrieve aggregate
    """

    queryset = SensorAggregate.objects.all()
    serializer_class = SensorAggregateSerializer
    filterset_fields = ['device', 'bucket']
    search_fields = ['device__name']
    ordering = ['-bucket_start']
    permission_classes = [IsAuthenticated] # Add permission class
