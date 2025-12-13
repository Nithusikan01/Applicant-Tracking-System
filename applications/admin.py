from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'job', 'match_score', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'job']
    search_fields = ['name', 'email', 'resume_text']
    readonly_fields = ['resume_text', 'match_score', 'created_at']
