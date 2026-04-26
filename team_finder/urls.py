from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from team_finder.core import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("accounts/signup/", views.signup, name="signup"),
    path("accounts/login/", views.EmailLoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "accounts/password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form.html",
            success_url="/accounts/password_change/done/",
        ),
        name="password_change",
    ),
    path(
        "accounts/password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path("users/list/", views.user_list, name="user_list"),
    path("users/<int:pk>/", views.profile_detail, name="profile_detail"),
    path("users/<int:pk>/edit/", views.profile_edit, name="profile_edit"),
    path("projects/list/", views.home, name="project_list"),
    path("projects/create-project/", views.project_create, name="project_create"),
    path("projects/<int:pk>/", views.project_detail, name="project_detail"),
    path("projects/<int:pk>/edit/", views.project_edit, name="project_edit"),
    path("projects/<int:pk>/join/", views.project_join, name="project_join"),
    path("projects/<int:pk>/finish/", views.project_finish, name="project_finish"),
    path("skills/search/", views.skill_search, name="skill_search"),
    path(
        "users/<int:pk>/skills/add/",
        views.profile_skill_add,
        name="profile_skill_add",
    ),
    path(
        "users/<int:pk>/skills/<int:skill_id>/delete/",
        views.profile_skill_delete,
        name="profile_skill_delete",
    ),
]
