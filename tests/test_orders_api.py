"""API contract, negative-path, and tenant-isolation tests for orders."""

from uuid import UUID

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.orders.models import Order

User = get_user_model()


@pytest.mark.django_db
class TestOrdersAPI:
    def setup_method(self):
        self.tenant_id = UUID('33333333-3333-3333-3333-333333333333')
        self.user = User.objects.create_user(
            username='order-user', password='testpass123', tenant_id=str(self.tenant_id)
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def valid_payload(self):
        return {
            'customer_email': 'buyer@example.com',
            'customer_name': 'Test Buyer',
            'shipping_address': '1 Test Street',
            'line_items': [
                {
                    'product_name': 'Firewall license',
                    'quantity': 1,
                    'unit_price': '99.99',
                }
            ],
        }

    def test_create_order_calculates_total_and_items(self):
        response = self.client.post('/api/orders/', self.valid_payload(), format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['total_amount'] == '99.99'
        assert response.data['line_items'][0]['total_price'] == '99.99'

    def test_create_order_rejects_empty_line_items(self):
        payload = self.valid_payload()
        payload['line_items'] = []

        response = self.client.post('/api/orders/', payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Order.objects.exists()

    @pytest.mark.parametrize('email', ['', 'not-an-email'])
    def test_create_order_rejects_invalid_email(self, email):
        payload = self.valid_payload()
        payload['customer_email'] = email

        response = self.client.post('/api/orders/', payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize('quantity', [0, -1])
    def test_create_order_rejects_non_positive_quantity(self, quantity):
        payload = self.valid_payload()
        payload['line_items'][0]['quantity'] = quantity

        response = self.client.post('/api/orders/', payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthenticated_order_list_is_rejected(self):
        self.client.logout()

        response = self.client.get('/api/orders/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_tenant_cannot_read_another_tenants_order(self):
        """Validating data access policies and isolation rules."""
        order = Order.objects.create(
            order_number='ORD-OTHER-001',
            customer_email='other@example.com',
            customer_name='Other Buyer',
            shipping_address='Other Street',
            tenant_id=UUID('44444444-4444-4444-4444-444444444444'),
        )

        response = self.client.get(f'/api/orders/{order.pk}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND