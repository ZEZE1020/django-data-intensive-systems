"""
Locust-based load testing script.

This script defines user behavior for load testing the application's API endpoints.
It's designed to simulate real user traffic to measure performance under load.

Usage:
    locust -f scripts/load_test.py --host http://localhost:8000

Reference: https://docs.locust.io/
"""

import sys
import os
import django
import random
import uuid
import base64
from locust import FastHttpUser, task, between, tag

# 1. Setup Django Environment to access models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.contrib.auth import get_user_model
from apps.sensors.models import Device

User = get_user_model()

class WebUser(FastHttpUser):
    """
    Simulates a web user browsing the site.
    Uses FastHttpUser for better performance (geventhttpclient).
    """
    wait_time = between(1, 3)  # 1-3 seconds between tasks
    network_timeout = 5.0
    connection_timeout = 5.0

    def on_start(self):
        """
        Setup: Create a unique user and device for this session.
        """
        try:
            # Generate unique credentials
            self.username = f"loadtest_{uuid.uuid4().hex[:8]}"
            self.password = "testpass123"
            
            # Create Django User
            self.user = User.objects.create_user(username=self.username, password=self.password)
            
            # Generate a Tenant ID (simulating multi-tenancy)
            self.tenant_id = str(uuid.uuid4())

            # Configure Headers (FastHttpUser does not support client.headers)
            auth_string = f"{self.username}:{self.password}"
            b64_auth = base64.b64encode(auth_string.encode()).decode()
            self.default_headers = {
                "Authorization": f"Basic {b64_auth}",
                "X-Tenant-ID": self.tenant_id
            }

            # Create a Device for this user to report data to
            self.device = Device.objects.create(
                device_id=str(uuid.uuid4()),
                name=f"Device-{self.username}",
                device_type=random.choice(['temperature', 'humidity']),
                location='LoadTest Lab',
                tenant_id=self.tenant_id
            )
        except Exception as e:
            print(f"Error in on_start for {getattr(self, 'username', 'unknown')}: {e}")
            self.on_stop()  # Attempt cleanup
            raise

    @tag('health')
    @task(1)
    def check_health(self):
        """
        Lightweight task to check service health.
        """
        self.client.get("/health/", headers=getattr(self, 'default_headers', {}))

    @tag('read')
    @task(3)
    def list_sensors(self):
        """
        Task to simulate a user listing sensor readings.
        """
        self.client.get("/api/sensors/", name="/api/sensors/ [list]", headers=getattr(self, 'default_headers', {}))

    @tag('write')
    @task(5)
    def create_reading(self):
        """
        High-volume task: Simulate a device pushing a new sensor reading.
        """
        payload = {
            "device": self.device.id,
            "value": round(random.uniform(20.0, 35.0), 2),
            # 'tenant_id' is handled by middleware via header or inferred from device
        }
        # Assuming /api/sensors/readings/ is the endpoint for creating readings
        self.client.post("/api/sensors/readings/", json=payload, name="/api/sensors/readings/ [create]", headers=getattr(self, 'default_headers', {}))

    def on_stop(self):
        """Cleanup user and device after test stops."""
        try:
            if hasattr(self, 'device') and self.device:
                self.device.delete()
            if hasattr(self, 'user') and self.user:
                self.user.delete()
        except Exception as e:
            print(f"Error cleaning up user {getattr(self, 'username', 'unknown')}: {e}")
