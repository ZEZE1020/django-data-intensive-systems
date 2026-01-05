"""
Orders Django admin configuration.
"""

from django.contrib import admin

from apps.core.admin import CoreAdminMixin, SoftDeleteAdminMixin
from apps.orders.models import Order, OrderLineItem, Payment


class OrderLineItemInline(admin.TabularInline):
    """Inline admin for OrderLineItem."""

    model = OrderLineItem
    extra = 0
    readonly_fields = ['created_at', 'total_price']
    fields = ['product_name', 'product_sku', 'quantity', 'unit_price', 'total_price']


class PaymentInline(admin.StackedInline):
    """Inline admin for Payment."""

    model = Payment
    extra = 0
    readonly_fields = [
        'created_at',
        'attempt_count',
        'authorized_at',
        'captured_at',
        'failed_at',
        'refunded_at',
    ]
    fields = [
        'amount',
        'currency',
        'status',
        'payment_method',
        'transaction_id',
        'attempt_count',
        'idempotency_key',
    ]


@admin.register(Order)
class OrderAdmin(SoftDeleteAdminMixin):
    """Admin interface for Order model."""

    list_display = ['order_number', 'customer_name', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'deleted', 'created_at', 'fulfilled_at']
    search_fields = ['order_number', 'customer_name', 'customer_email']
    readonly_fields = ['created_at', 'updated_at', 'order_number', 'version']
    inlines = [OrderLineItemInline, PaymentInline]
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'status', 'version'),
        }),
        ('Customer', {
            'fields': ('customer_name', 'customer_email'),
        }),
        ('Totals', {
            'fields': ('subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount'),
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'billing_address', 'fulfilled_at'),
        }),
        ('Notes & Metadata', {
            'fields': ('notes', 'metadata'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
        ('Soft Delete', {
            'fields': ('deleted', 'deleted_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(OrderLineItem)
class OrderLineItemAdmin(CoreAdminMixin):
    """Admin interface for OrderLineItem model."""

    list_display = ['order', 'product_name', 'quantity', 'unit_price', 'total_price']
    list_filter = ['order', 'created_at']
    search_fields = ['product_name', 'product_sku', 'order__order_number']
    readonly_fields = ['created_at', 'total_price']
    fieldsets = (
        ('Item Info', {
            'fields': ('order', 'product_name', 'product_sku'),
        }),
        ('Pricing', {
            'fields': ('quantity', 'unit_price', 'total_price'),
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )


@admin.register(Payment)
class PaymentAdmin(CoreAdminMixin):
    """Admin interface for Payment model."""

    list_display = ['order', 'amount', 'status', 'payment_method', 'attempt_count']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order__order_number', 'transaction_id', 'idempotency_key']
    readonly_fields = [
        'created_at',
        'attempt_count',
        'authorized_at',
        'captured_at',
        'failed_at',
        'refunded_at',
    ]
    fieldsets = (
        ('Payment Info', {
            'fields': ('order', 'amount', 'currency', 'status', 'payment_method'),
        }),
        ('Transaction', {
            'fields': ('transaction_id', 'idempotency_key', 'attempt_count', 'last_error'),
        }),
        ('Timestamps', {
            'fields': (
                'authorized_at',
                'captured_at',
                'failed_at',
                'refunded_at',
                'created_at',
            ),
            'classes': ('collapse',),
        }),
    )
