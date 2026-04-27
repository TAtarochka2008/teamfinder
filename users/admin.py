from django.contrib import admin

from .models import Profile, Skill


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "github", "created_at")
    search_fields = ("user__first_name", "user__last_name", "user__email", "phone", "github")
    filter_horizontal = ("skills",)


admin.site.register(Skill)
