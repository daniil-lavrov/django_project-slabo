from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
        # The forms to add and change user instances are forms which get inherited from (BaseUserAdmin)
        fieldsets = (
            (None, {'fields': ('email', 'password')}),
            ('Personal info', {'fields': ('first_name', 'last_name', 'city', 'nick')}),
            ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
            ('Important dates', {'fields': ('last_login',)}),
        )
        add_fieldsets = (
            (None, {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2'),
            }),
        )
        list_display = ('email', 'first_name', 'last_name', 'nick')
        search_fields = ('email', 'first_name', 'last_name', 'nick')
        ordering = ('email',)

admin.site.register(User, UserAdmin)
