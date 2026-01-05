import pytest
from django.contrib.auth import get_user_model

@pytest.mark.django_db
def test_create_custom_user():
    User = get_user_model()
    user = User.objects.create_user(username='testuser', password='password123', tenant_id='test-tenant-id')
    assert user.username == 'testuser'
    assert user.tenant_id == 'test-tenant-id'
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser

@pytest.mark.django_db
def test_create_superuser():
    User = get_user_model()
    admin_user = User.objects.create_superuser(username='admin', password='adminpassword')
    assert admin_user.username == 'admin'
    assert admin_user.is_staff
    assert admin_user.is_superuser
    # Superuser should not have a tenant_id by default, or it should be handled
    # differently in a multi-tenant context. For now, we expect it to be None/blank.
    assert admin_user.tenant_id is None or admin_user.tenant_id == ''
