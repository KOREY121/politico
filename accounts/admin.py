from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Voter


@admin.register(Voter)
class VoterAdmin(UserAdmin):
    model           = Voter
    list_display    = ['voter_id', 'national_id', 'full_name', 'email', 'status', 'is_staff', 'date_joined']
    list_filter     = ['status', 'is_staff', 'is_superuser']
    search_fields   = ['national_id', 'full_name', 'email']
    list_editable   = ['status']
    ordering        = ['-date_joined']

    fieldsets = (
        ('Personal Info',   {'fields': ('national_id', 'full_name', 'email', 'dob', 'password')}),
        ('Permissions',     {'fields': ('status', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('date_joined',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('national_id', 'full_name', 'email', 'dob', 'password1', 'password2', 'status', 'is_staff', 'is_superuser'),
        }),
    )

    readonly_fields = ['date_joined']