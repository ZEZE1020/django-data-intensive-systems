"""
Tests for monitoring health check endpoints.
Covers all health, readiness, and liveness probes to ensure they work as expected.
"""
import pytest
from django.test import Client
from django.contrib.auth import get_user_model

@pytest.mark.django_db
def test_health_endpoint_returns_200():
    """Test that general health endpoint returns healthy status when all services are up."""
    client = Client()
    response = client.get('/health/')
    
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['checks']['database'] == 'ok'
    assert data['checks']['cache'] == 'ok'

@pytest.mark.django_db
def test_readiness_endpoint_returns_200():
    """Test that readiness probe returns true when all dependencies are available."""
    client = Client()
    response = client.get('/health/ready/')
    
    assert response.status_code == 200
    assert response.json()['ready'] is True

@pytest.mark.django_db
def test_liveness_endpoint_always_returns_200():
    """Test that liveness probe always returns alive=true as long as the process is running."""
    client = Client()
    response = client.get('/health/live/')
    
    assert response.status_code == 200
    assert response.json()['alive'] is True

@pytest.mark.django_db
def test_metrics_endpoint_returns_prometheus_data():
    """Test that Prometheus metrics endpoint exports all expected metrics."""
    client = Client()
    staff_user = get_user_model().objects.create_user(
        username='metrics-staff', password='testpass123', is_staff=True
    )
    client.force_login(staff_user)
    response = client.get('/metrics/')
    
    assert response.status_code == 200
    # Check that core metrics are present
    content = response.content.decode()
    assert 'requests_total' in content
    assert 'database_queries_total' in content
    assert 'celery_tasks_total' in content