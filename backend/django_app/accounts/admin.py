from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ConsentLog, UserActivity


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'get_location', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_active', 'data_consent')
    search_fields = ('username', 'email')
    
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type', 'country', 'mauritius_location')}),
        ('DPA 2017 Compliance', {
            'fields': ('data_consent', 'marketing_consent', 'cookie_consent', 
                      'consent_date', 'account_deletion_requested')
        }),
    )
    
    def get_location(self, obj):
        return obj.get_location()
    get_location.short_description = 'Location'


admin.site.register(ConsentLog)
admin.site.register(UserActivity)