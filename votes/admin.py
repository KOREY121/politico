from django.contrib import admin
from .models import Vote



@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display    = ['vote_id', 'voter', 'candidate', 'election', 'time']
    list_filter     = ['election', 'candidate__constituency']
    search_fields   = ['voter__full_name', 'voter__national_id', 'candidate__full_name']
    ordering        = ['-time']
    readonly_fields = ['vote_id', 'voter', 'candidate', 'election', 'time']

    # Votes should never be editable in admin
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    fieldsets = (
        ('Vote Info',  {'fields': ('vote_id', 'voter', 'candidate', 'election', 'time')}),
    )