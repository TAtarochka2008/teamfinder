from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "description", "author__email")
    filter_horizontal = ("members",)
