"""
Orders models.

E-commerce order management:
  - Order: Main order entity (contains line items, totals, status)
  - OrderLineItem: Individual product in order (quantity, price snapshot)
  - Payment: Payment transactions (status, method, retries)

Design patterns:
  - Optimistic locking (version field) for concurrent order updates
  - Price snapshots in OrderLineItem (decoupled from product pricing)
  - Payment retry logic with status tracking
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.mixins import TimeStampedModel, SoftDeleteModel, VersionedModel, IdempotentModel, TenantAwareModel
from apps.core.managers import TenantAwareManager, CoreManager


class Order(TimeStampedModel, SoftDeleteModel, VersionedModel, TenantAwareModel):
    """
    E-commerce order.

    Main entity for order management. Uses optimistic locking (version field)
    to prevent lost updates when processing concurrent requests.
    """

    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    order_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text='Unique order number (e.g., ORD-20250105-001)',
    )
    customer_email = models.EmailField(
        help_text='Customer email address',
    )
    customer_name = models.CharField(
        max_length=255,
        help_text='Customer name',
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text='Current order status',
    )
    # Price snapshot at order time
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Sum of line items before tax and shipping',
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Tax amount',
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Shipping cost',
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Discount or coupon amount',
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Final total: subtotal + tax + shipping - discount',
    )
    # Delivery information
    shipping_address = models.TextField(
        help_text='Full shipping address',
    )
    billing_address = models.TextField(
        blank=True,
        help_text='Billing address (if different from shipping)',
    )
    # Metadata
    notes = models.TextField(
        blank=True,
        help_text='Internal notes or customer comments',
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional order data (source, campaign, etc.)',
    )
    # Fulfillment
    fulfilled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text='When order was fulfilled',
    )

    objects = TenantAwareManager()

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['customer_email', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['fulfilled_at']),
        ]

    def __str__(self):
        return f'{self.order_number} - {self.customer_name}'

    def calculate_total(self):
        """Recalculate total from components."""
        self.total_amount = (
            self.subtotal
            + self.tax_amount
            + self.shipping_cost
            - self.discount_amount
        )


class OrderLineItem(TimeStampedModel, TenantAwareModel):
    """
    Individual line item in an order.

    Stores product quantity and price snapshot at order time.
    Decoupled from Product model to preserve historical pricing.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='line_items',
        help_text='Parent order',
    )
    product_name = models.CharField(
        max_length=255,
        help_text='Product name (snapshot from order time)',
    )
    product_sku = models.CharField(
        max_length=100,
        blank=True,
        help_text='Product SKU',
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Quantity ordered',
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Price per unit at order time',
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='quantity × unit_price',
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional item data (attributes, options, etc.)',
    )

    class Meta:
        verbose_name = 'Order Line Item'
        verbose_name_plural = 'Order Line Items'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return f'{self.product_name} (x{self.quantity}) in {self.order.order_number}'

    def save(self, *args, **kwargs):
        """Auto-calculate total_price on save."""
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Payment(TimeStampedModel, IdempotentModel, TenantAwareModel):
    """
    Payment transaction.

    Tracks payment attempts, status, method, and retry logic.
    Idempotent (via idempotency_key) to prevent duplicate charges.
    """

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('stripe', 'Stripe'),
        ('other', 'Other'),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment',
        help_text='Associated order',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Payment amount',
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text='Currency code (ISO 4217)',
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text='Current payment status',
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        help_text='Payment method used',
    )
    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        help_text='Payment processor transaction ID',
    )
    # Retry logic
    attempt_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of payment attempts',
    )
    last_error = models.TextField(
        blank=True,
        help_text='Error message from last failed attempt',
    )
    # Timestamps
    authorized_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When payment was authorized',
    )
    captured_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When payment was captured (charged)',
    )
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When payment failed',
    )
    refunded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When payment was refunded',
    )

    def can_retry(self, max_attempts=3):
        """Check if payment can be retried."""
        return self.status == 'failed' and self.attempt_count < max_attempts