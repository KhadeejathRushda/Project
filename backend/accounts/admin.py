from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # This list must match the field names in accounts/models.py
    list_display = ('username', 'email', 'role', 'is_doctor_verified', 'is_staff')
    list_filter = ('role', 'is_doctor_verified')
    
    # Allows you to edit custom fields in the admin panel
    fieldsets = UserAdmin.fieldsets + (
        ('Professional Info', {'fields': ('role', 'certificate', 'is_doctor_verified', 'assigned_doctor')}),
    )
    
    # Allows you to set custom fields when creating a user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Professional Info', {'fields': ('role', 'certificate', 'is_doctor_verified', 'assigned_doctor')}),
    )

admin.site.register(User, CustomUserAdmin)