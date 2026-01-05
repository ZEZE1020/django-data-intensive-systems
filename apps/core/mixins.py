"""
Core model mixins.

Reusable mixins for common model functionality (soft deletes, timestamps, etc.).

Usage:
    class Order(TimeStampedModel, SoftDeleteModel):
        name = models.CharField(max_length=100)
        
        class Meta:
            verbose_name = 'Order'
            verbose_name_plural = 'Orders'
            indexes = [models.Index(fields=['created_at', 'deleted'])]
"""

from django.db import models
from django.utils import timezone

from apps.core.managers import TenantAwareManager, SoftDeleteManager


class TimeStampedModel(models.Model):
    """
    Abstract model providing created_at and updated_at timestamps.

    Useful for audit trails and understanding data change history.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When this record was created',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When this record was last updated',
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]


class SoftDeleteModel(models.Model):
    """
    Abstract model providing soft-delete functionality.

    Instead of hard deleting records, marks them as deleted with a timestamp.
    Allows recovery of accidentally deleted data.

    By default, queries on this model will only return non-deleted items.
    Use .all_with_deleted() or .deleted_only() to access deleted records.
    """

    deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Whether this record is soft-deleted',
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text='When this record was soft-deleted',
    )

    objects = SoftDeleteManager() # Assign the custom manager

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['deleted', 'deleted_at']),
        ]

    def soft_delete(self):
        """Soft-delete this record."""
        self.deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted', 'deleted_at'])

    def restore(self):
        """Restore a soft-deleted record."""
        self.deleted = False
        self.deleted_at = None
        self.save(update_fields=['deleted', 'deleted_at'])


class TenantAwareModel(models.Model):
    """
    Abstract model for multi-tenancy support.

    Allows the same database to serve multiple independent tenants,
    with automatic filtering by tenant context.
    """

    tenant_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text='Tenant identifier for multi-tenancy',
    )

    objects = TenantAwareManager() # Assign the custom manager

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['tenant_id']),
        ]


class VersionedModel(models.Model):
    """
    Abstract model providing optimistic locking via version field.

    Prevents lost updates in concurrent scenarios by tracking object versions.
    Useful for Orders, Payments where concurrent modifications are possible.

    Usage:
        order = Order.objects.get(id=1)
        order.status = 'completed'
        order.save()  # Will fail if another request modified this order

    Raises:
        ConflictError: If version mismatch is detected on save
    """

    version = models.PositiveIntegerField(
        default=1,
        help_text='Version number for optimistic locking',
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Increment version on save."""
        if self.pk:
            self.version += 1
        super().save(*args, **kwargs)


class IdempotentModel(models.Model):
    """
    Abstract model providing idempotency support.

    Allows safe retries of API requests via idempotency keys,
    preventing duplicate operations.

    Usage:
        # Client sends idempotency_key with request
        payment = Payment.objects.create(
            amount=100.00,
            idempotency_key=request.headers['Idempotency-Key']
        )
        
        # Retry with same key returns existing payment, no duplicate
        payment = Payment.objects.get(idempotency_key=key)
    """

    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        null=True,
        blank=True,
        help_text='Unique key for idempotent retries',
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['idempotency_key']),
        ]
