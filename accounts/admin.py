from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

if admin.site.is_registered(CustomUser):
    admin.site.unregister(CustomUser)

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_store_manager')
    list_filter = ('is_staff', 'is_superuser', 'is_store_manager')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_store_manager', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)