from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("projects/list/", views.home, name="project_list"),
    path("projects/create-project/", views.project_create, name="project_create"),
    path("projects/<int:pk>/", views.project_detail, name="project_detail"),
    path("projects/<int:pk>/edit/", views.project_edit, name="project_edit"),
    path("projects/<int:pk>/join/", views.project_join, name="project_join"),
    path("projects/<int:pk>/finish/", views.project_finish, name="project_finish"),
]
