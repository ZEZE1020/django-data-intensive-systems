"""
Locust-based load testing script.

This script defines user behavior for load testing the application's API endpoints.
It's designed to simulate real user traffic to measure performance under load.

Usage:
    locust -f scripts/load_test.py --host http://localhost:8000

Reference: https://docs.locust.io/
"""

import random
from locust import HttpUser, task, between


class WebUser(HttpUser):
    """
    Simulates a web user browsing the site.
    """
    wait_time = between(1, 5)  # 1-5 seconds between tasks

    def on_start(self):
        """
        Called when a Locust start before any task is scheduled.
        Can be used for login or other setup.
        """
        # Example: self.client.post("/login", {"username":"foo", "password":"bar"})
        pass

    @task(1)
    def check_health(self):
        """
        Task to check the health of the service.
        """
        self.client.get("/health/")

    @task(3)
    def list_sensors(self):
        """
        Task to simulate a user listing sensor readings.
        """
        # Note: This endpoint now requires authentication.
        # Ensure 'on_start' performs a login or similar authentication step.
        self.client.get("/api/sensors/", name="/api/sensors/[list]")

    # TODO: Add tasks for creating sensor readings
    # TODO: Add tasks for creating orders
    # TODO: Add tasks for more complex user flows
