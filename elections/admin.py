from django.contrib import admin

from elections.models import Election

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display  = ['election_id', 'start_date', 'end_date', 'status']
    list_filter   = ['status']
    list_editable = ['status']
    ordering       = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Election Details', {'fields': ('start_date', 'end_date', 'status')}),
        ('Timestamps',       {'fields': ('created_at', 'updated_at')}),
    )