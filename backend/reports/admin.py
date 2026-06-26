from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    # Displays the diagnostic results in the admin list view
    list_display = ('id', 'patient', 'doctor', 'result', 'confidence', 'is_verified', 'created_at')
    
    # Filter sidebar for easy navigation
    list_filter = ('is_verified', 'result', 'created_at')
    
    # Search by username to find specific patient files
    search_fields = ('patient__username', 'doctor__username', 'result')
    
    # Stops the creation date from being manually changed
    readonly_fields = ('created_at',)