"""
Core Django middleware.
"""

from apps.core.tenant_context import set_current_tenant, clear_current_tenant


class TenantContextMiddleware:
    """
    Middleware to set the current tenant ID in the request context.

    Assumes the authenticated user (request.user) has a 'tenant_id' attribute.
    If no user is authenticated or tenant_id is not found, the tenant context
    will not be set, and tenant-aware models will return empty querysets.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Assuming request.user has a tenant_id attribute
            # This needs to be adjusted based on the actual User model structure
            if hasattr(request.user, 'tenant_id'):
                set_current_tenant(request.user.tenant_id)
            else:
                # Optionally log a warning if an authenticated user lacks tenant_id
                pass
        
        response = self.get_response(request)
        
        # Clear the tenant context after the request to prevent data leakage
        # across subsequent requests in the same thread (e.g., in test environments).
        clear_current_tenant()
        
        return response
