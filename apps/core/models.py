"""
Core models.

The core app doesn't define concrete models; instead, it provides
abstract models and mixins used by other apps.

See apps.core.mixins for:
  - TimeStampedModel
  - SoftDeleteModel
  - TenantAwareModel
  - VersionedModel
  - IdempotentModel
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom User model to include tenant_id for multi-tenancy.
    """
    tenant_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username