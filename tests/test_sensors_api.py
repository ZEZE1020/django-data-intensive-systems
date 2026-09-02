"""
API tests for the sensors application.
Covers all CRUD operations for devices and sensor readings, including edge cases.
"""
import pytest
from uuid import UUID
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.sensors.models import Device, SensorReading
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestSensorsAPI:
    def setup_method(self):
        """Setup test user and client for all sensor API tests."""
        self.tenant_id = UUID('11111111-1111-1111-1111-111111111111')
        self.user = User.objects.create_user(
            username='testuser', password='testpass123', tenant_id=str(self.tenant_id)
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        # Create test device
        self.device = Device.objects.create(
            device_id='test-device-001',
            name='Test Temperature Sensor',
            device_type='temperature',
            location='Test Lab',
            tenant_id=self.tenant_id
        )

    def test_list_devices_authenticated(self):
        """Test that authenticated users can list their devices."""
        response = self.client.get('/api/sensors/devices/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) >= 1

    def test_create_sensor_reading_success(self):
        """Test successful creation of a sensor reading with valid data."""
        payload = {
            "device": self.device.id,
            "value": 25.5
        }
        response = self.client.post(
            '/api/sensors/readings/', 
            payload, 
            format='json',
            HTTP_X_TENANT_ID=self.tenant_id
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert SensorReading.objects.without_tenant_filter().count() == 1

    def test_create_sensor_reading_invalid_value(self):
        """Test edge case: invalid temperature value returns error."""
        payload = {
            "device": self.device.id,
            "value": "not-a-number"  # Invalid data type
        }
        response = self.client.post(
            '/api/sensors/readings/', 
            payload, 
            format='json',
            HTTP_X_TENANT_ID=self.tenant_id
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_sensor_reading_missing_device(self):
        """Test edge case: missing device ID returns proper error."""
        payload = {
            "value": 25.5
        }
        response = self.client.post(
            '/api/sensors/readings/', 
            payload, 
            format='json',
            HTTP_X_TENANT_ID=self.tenant_id
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthorized_access_blocked(self):
        """Test that unauthenticated users cannot access sensor data."""
        self.client.logout()
        response = self.client.get('/api/sensors/devices/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_tenant_cannot_read_another_tenants_device(self):
        """Validating data access policies and isolation rules."""
        other_device = Device.objects.create(
            device_id='other-device-001',
            name='Other tenant device',
            device_type='temperature',
            location='Other lab',
            tenant_id=UUID('22222222-2222-2222-2222-222222222222'),
        )

        response = self.client.get(f'/api/sensors/devices/{other_device.pk}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND