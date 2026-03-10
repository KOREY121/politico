from django.contrib import admin

from .models import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display    = ['candidate_id', 'full_name', 'party', 'election', 'constituency', 'total_votes']
    list_filter     = ['party', 'election', 'constituency']
    search_fields   = ['full_name', 'party']
    ordering        = ['full_name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Candidate Info',  {'fields': ('full_name', 'party')}),
        ('Assignment',      {'fields': ('election', 'constituency')}),
        ('Timestamps',      {'fields': ('created_at', 'updated_at')}),
    )