"""
Orders DRF serializers.

Serializers for order API endpoints with nested relationships.
"""

from rest_framework import serializers

from apps.orders.models import Order, OrderLineItem, Payment


class OrderLineItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderLineItem model."""

    class Meta:
        model = OrderLineItem
        fields = [
            'id',
            'product_name',
            'product_sku',
            'quantity',
            'unit_price',
            'total_price',
            'metadata',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'total_price']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""

    class Meta:
        model = Payment
        fields = [
            'id',
            'amount',
            'currency',
            'status',
            'payment_method',
            'transaction_id',
            'attempt_count',
            'idempotency_key',
            'authorized_at',
            'captured_at',
            'failed_at',
            'refunded_at',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'attempt_count',
            'authorized_at',
            'captured_at',
            'failed_at',
            'refunded_at',
            'created_at',
        ]


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model with nested line items and payment."""

    line_items = OrderLineItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'customer_email',
            'customer_name',
            'status',
            'subtotal',
            'tax_amount',
            'shipping_cost',
            'discount_amount',
            'total_amount',
            'shipping_address',
            'billing_address',
            'notes',
            'metadata',
            'line_items',
            'payment',
            'version',
            'fulfilled_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'order_number',
            'version',
            'created_at',
            'updated_at',
        ]

    def validate_total_amount(self, value):
        """Validate total_amount is positive."""
        if value < 0:
            raise serializers.ValidationError('Total amount cannot be negative.')
        return value


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders with inline line items."""

    customer_email = serializers.EmailField()
    customer_name = serializers.CharField(max_length=255)
    shipping_address = serializers.CharField()
    billing_address = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False)
    line_items = OrderLineItemSerializer(many=True)

    def validate_line_items(self, items):
        """Validate line items are not empty."""
        if not items:
            raise serializers.ValidationError('Order must have at least one line item.')
        return items

    def create(self, validated_data):
        """Create order with line items."""
        line_items_data = validated_data.pop('line_items')

        # Generate order number
        from apps.core.utils import generate_reference_code
        order_number = 'ORD-' + generate_reference_code(length=12)

        # Calculate totals
        subtotal = sum(
            item['unit_price'] * item['quantity']
            for item in line_items_data
        )

        order = Order.objects.create(
            order_number=order_number,
            subtotal=subtotal,
            total_amount=subtotal,  # Will be updated with tax/shipping
            **validated_data,
        )

        # Create line items
        for item_data in line_items_data:
            OrderLineItem.objects.create(order=order, **item_data)

        return order
