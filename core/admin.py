from django.contrib import admin

from .models import Profile, Project, Skill


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "github", "created_at")
    search_fields = ("user__first_name", "user__last_name", "user__email", "phone", "github")
    filter_horizontal = ("skills",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "description", "author__email")
    filter_horizontal = ("members",)


admin.site.register(Skill)
