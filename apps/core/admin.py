"""
Core Django admin configuration.

Admin interface customizations for core models.
"""

from django.contrib import admin


class CoreAdminMixin(admin.ModelAdmin):
    """Base admin mixin with common configurations."""

    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50
    search_fields = ('id',)

    def get_fieldsets(self, request, obj=None):
        """Add timestamps fieldset to all admin views."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            # Add timestamps fieldset for existing objects
            return list(fieldsets) + [
                ('Timestamps', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',),
                }),
            ]
        return fieldsets

    def get_list_display(self, request):
        """Add created_at to list display."""
        list_display = list(super().get_list_display(request))
        if 'created_at' not in list_display:
            list_display.append('created_at')
        return list_display

    def get_list_filter(self, request):
        """Add created_at to list filters."""
        list_filter = list(super().get_list_filter(request))
        if 'created_at' not in list_filter:
            list_filter.append('created_at')
        return list_filter


class SoftDeleteAdminMixin(CoreAdminMixin):
    """Admin mixin for soft-delete models."""

    def get_list_display(self, request):
        """Add deleted status to list display."""
        list_display = super().get_list_display(request)
        return list_display + ['deleted']

    def get_list_filter(self, request):
        """Add deleted filter."""
        list_filter = super().get_list_filter(request)
        return list_filter + ['deleted']

    def get_queryset(self, request):
        """Include deleted items in admin by default."""
        return super().get_queryset(request)

    actions = ['action_restore_deleted', 'action_permanently_delete']

    def action_restore_deleted(self, request, queryset):
        """Admin action to restore deleted items."""
        count = queryset.filter(deleted=True).restore()
        self.message_user(
            request,
            f'{count} items restored.',
        )

    action_restore_deleted.short_description = 'Restore selected items'

    def action_permanently_delete(self, request, queryset):
        """Admin action to permanently delete items."""
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f'{count} items permanently deleted.',
        )

    action_permanently_delete.short_description = 'Permanently delete selected items'
