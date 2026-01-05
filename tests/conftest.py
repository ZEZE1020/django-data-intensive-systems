"""
Global fixtures for the pytest test suite.

This file defines fixtures that are shared across multiple test files.
Pytest automatically discovers and injects these fixtures into tests.

Fixtures:
  - api_client: A DRF APIClient instance for making API requests in tests.
  - user: A standard Django user instance.
  - authenticated_client: An APIClient that is pre-authenticated with the user.

Reference: https://docs.pytest.org/en/latest/reference/fixtures.html
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Setup the Django test database.
    
    This fixture has session scope, so the database is set up once per session.
    """
    with django_db_blocker.unblock():
        # You can run management commands here if needed, e.g., for data migrations
        pass

@pytest.fixture
def api_client():
    """
    Provides a DRF APIClient instance.
    """
    return APIClient()

@pytest.fixture
def user(db) -> User:
    """
    Provides a standard Django user instance, created in the test database.
    The `db` fixture is required to enable database access.
    """
    return User.objects.create_user(
        username='testuser',
        password='testpassword',
        email='testuser@example.com'
    )

@pytest.fixture
def authenticated_client(api_client, user) -> APIClient:
    """
    Provides an APIClient that is already authenticated with a test user.
    """
    api_client.force_authenticate(user=user)
    return api_client

# TODO: Add a fixture for a superuser
# TODO: Add fixtures for model factories (e.g., a default Device)
