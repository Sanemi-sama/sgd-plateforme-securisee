from django.contrib import admin
from .models import ActionLog

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'description', 'ip_address')
    list_filter = ('action',)
    search_fields = ('user__username', 'description', 'ip_address')
    readonly_fields = [f.name for f in ActionLog._meta.fields]

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return request.user.is_superuser
