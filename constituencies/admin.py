from django.contrib import admin
from .models import Constituency


@admin.register(Constituency)
class ConstituencyAdmin(admin.ModelAdmin):
    list_display    = ['constituency_id', 'name', 'region', 'total_candidates', 'created_at']
    list_filter     = ['region']
    search_fields   = ['name', 'region']
    ordering        = ['name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Constituency Info', {'fields': ('name', 'region')}),
        ('Timestamps',        {'fields': ('created_at', 'updated_at')}),
    )