"""
Core managers.

Custom QuerySet and Manager classes providing common filtering,
aggregation, and soft-delete functionality.

Usage:
    class MyModel(models.Model):
        objects = CoreManager()
        
        class Meta:
            pass
    
    # Default queryset includes soft-deleted items (use .active() to exclude)
    MyModel.objects.all()  # includes deleted=True
    MyModel.objects.active()  # only deleted=False
"""

from django.db import models
from django.utils import timezone

from apps.core.tenant_context import get_current_tenant


class CoreQuerySet(models.QuerySet):
    """Base QuerySet with common operations."""

    def active(self):
        """
        Return only non-deleted items.

        Used with SoftDeleteModel to exclude soft-deleted records.
        """
        return self.filter(deleted=False)

    def deleted(self):
        """Return only soft-deleted items."""
        return self.filter(deleted=True)

    def restore(self):
        """
        Restore soft-deleted items.

        Updates deleted=False and deleted_at=None for all matching records.
        """
        return self.update(deleted=False, deleted_at=None)

    def with_timestamps(self, created_after=None, created_before=None, 
                        updated_after=None, updated_before=None):
        """
        Filter by timestamp ranges.

        Args:
            created_after: Filter items created after this datetime
            created_before: Filter items created before this datetime
            updated_after: Filter items updated after this datetime
            updated_before: Filter items updated before this datetime

        Returns:
            Filtered QuerySet
        """
        queryset = self
        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)
        if created_before:
            queryset = queryset.filter(created_at__lte=created_before)
        if updated_after:
            queryset = queryset.filter(updated_at__gte=updated_after)
        if updated_before:
            queryset = queryset.filter(updated_at__lte=updated_before)
        return queryset

    def recent(self, days=7):
        """
        Return items created in the last N days.

        Args:
            days: Number of days to look back (default: 7)

        Returns:
            Filtered QuerySet
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=cutoff)

    def oldest_first(self):
        """Order by created_at ascending (oldest first)."""
        return self.order_by('created_at')

    def newest_first(self):
        """Order by created_at descending (newest first)."""
        return self.order_by('-created_at')


class CoreManager(models.Manager):
    """Base Manager using CoreQuerySet."""

    def get_queryset(self):
        """Return CoreQuerySet."""
        return CoreQuerySet(self.model, using=self._db)

    def active(self):
        """Return only non-deleted items."""
        return self.get_queryset().active()

    def deleted(self):
        """Return only soft-deleted items."""
        return self.get_queryset().deleted()

    def restore(self):
        """Restore all soft-deleted items."""
        return self.get_queryset().restore()

    def with_timestamps(self, **kwargs):
        """Filter by timestamp ranges."""
        return self.get_queryset().with_timestamps(**kwargs)

    def recent(self, days=7):
        """Return items created in the last N days."""
        return self.get_queryset().recent(days)

    def oldest_first(self):
        """Order by created_at ascending."""
        return self.get_queryset().oldest_first()

    def newest_first(self):
        """Order by created_at descending."""
        return self.get_queryset().newest_first()


class SoftDeleteQuerySet(CoreQuerySet):
    """
    QuerySet that provides methods for filtering soft-deleted items.
    """
    pass


class SoftDeleteManager(models.Manager):
    """
    Manager that by default only returns non-deleted items.
    """
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).active()

    def all_with_deleted(self):
        """Return all items, including soft-deleted ones."""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self):
        """Return only soft-deleted items."""
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()


class TenantAwareQuerySet(CoreQuerySet):
    """
    QuerySet that automatically filters by the current tenant_id.
    """
    pass


class TenantAwareManager(models.Manager): # Inherit from models.Manager directly
    """
    Manager that automatically filters queries by the current tenant_id
    and provides soft-deletion methods.
    """
    def get_queryset(self):
        current_tenant_id = get_current_tenant()
        if current_tenant_id:
            return TenantAwareQuerySet(self.model, using=self._db).filter(tenant_id=current_tenant_id)
        # If tenant_id is not set, we return an empty queryset to prevent data leakage.
        return TenantAwareQuerySet(self.model, using=self._db).none()

    def active(self):
        """Return only non-deleted items, with tenant filtering."""
        return self.get_queryset().active()

    def deleted(self):
        """Return only soft-deleted items, with tenant filtering."""
        return self.get_queryset().deleted()

    def restore(self):
        """Restore soft-deleted items, with tenant filtering."""
        return self.get_queryset().restore()

    def without_tenant_filter(self):
        """
        Returns a queryset that bypasses the automatic tenant filtering.
        Use with extreme caution.
        """
        return TenantAwareQuerySet(self.model, using=self._db)
