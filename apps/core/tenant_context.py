"""
Multi-tenancy context management.

This module provides utilities for managing the current tenant ID within
a thread-local context, ensuring tenant isolation in multi-tenant applications.

Usage:
    from apps.core.tenant_context import set_current_tenant, get_current_tenant, tenant_context

    # Set tenant ID for the current thread/request
    set_current_tenant(request.user.tenant_id)

    # Get the current tenant ID
    current_tenant_id = get_current_tenant()

    # Use a context manager for temporary tenant context (e.g., in management commands)
    with tenant_context(some_tenant_id):
        # Operations within this block will use some_tenant_id
        ...
"""

import threading
from contextlib import contextmanager

_thread_tenant = threading.local()


def set_current_tenant(tenant_id):
    """Set the tenant ID for the current thread."""
    _thread_tenant.tenant_id = tenant_id


def get_current_tenant():
    """Get the tenant ID for the current thread, or None if not set."""
    return getattr(_thread_tenant, 'tenant_id', None)


def clear_current_tenant():
    """Clear the tenant ID for the current thread."""
    if hasattr(_thread_tenant, 'tenant_id'):
        del _thread_tenant.tenant_id


@contextmanager
def tenant_context(tenant_id):
    """
    Context manager to temporarily set and then clear the tenant ID.

    Usage:
        with tenant_context(some_tenant_id):
            # Operations within this block will use some_tenant_id
            ...
    """
    old_tenant_id = get_current_tenant()
    set_current_tenant(tenant_id)
    try:
        yield
    finally:
        set_current_tenant(old_tenant_id)
