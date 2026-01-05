"""
Orders API views.

REST API endpoints for order management and payment processing.

Endpoints:
  GET  /api/orders/
  POST /api/orders/
  GET  /api/orders/{id}/
  PATCH /api/orders/{id}/
  GET  /api/orders/{id}/payment/
  POST /api/orders/{id}/payment/
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.orders.models import Order, OrderLineItem, Payment
from apps.orders.serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    PaymentSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for orders.

    Endpoints:
      GET  /api/orders/ - List orders
      POST /api/orders/ - Create new order
      GET  /api/orders/{id}/ - Retrieve order
      PATCH /api/orders/{id}/ - Update order status (optimistic locking)
      DELETE /api/orders/{id}/ - Soft-delete order
    """

    queryset = Order.objects.active()
    serializer_class = OrderSerializer
    filterset_fields = ['status', 'customer_email']
    search_fields = ['order_number', 'customer_name', 'customer_email']
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Use OrderCreateSerializer for create action."""
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def perform_update(self, serializer):
        """Handle optimistic locking on update."""
        try:
            serializer.save()
        except Exception as e:
            return Response(
                {'error': 'Order was modified by another request. Please refresh.'},
                status=status.HTTP_409_CONFLICT,
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order."""
        order = self.get_object()
        if order.status in ['shipped', 'delivered', 'refunded']:
            return Response(
                {'error': f'Cannot cancel order with status {order.status}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = 'cancelled'
        order.save()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['get'])
    def payment(self, request, pk=None):
        """Get payment details for this order."""
        order = self.get_object()
        try:
            payment = order.payment
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'No payment found for this order'},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Initiate payment processing for this order."""
        order = self.get_object()
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if payment already exists
        if hasattr(order, 'payment'):
            return Response(
                {'error': 'Payment already exists for this order'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create payment
        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            **serializer.validated_data,
        )

        # TODO: Trigger Celery task to process payment asynchronously
        # from apps.orders.tasks import process_payment_task
        # process_payment_task.delay(payment.id)

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
