from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Project


class ProjectTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="owner@yandex.com",
            email="owner@yandex.com",
            password="testpass123",
            first_name="Олег",
            last_name="Автор",
        )
        self.project = Project.objects.create(
            author=self.user,
            name="Тестовый проект",
            description="Описание тестового проекта",
            github_url="https://github.com/",
        )
        self.project.members.add(self.user)

    def test_project_pages_open(self):
        urls = [
            reverse("home"),
            reverse("project_list"),
            reverse("project_detail", args=[self.project.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_login_required_for_project_create(self):
        response = self.client.get(reverse("project_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_authenticated_user_can_create_project(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("project_create"),
            {
                "name": "Новый проект",
                "description": "Описание нового проекта",
                "github_url": "https://github.com/",
                "status": Project.OPEN,
            },
        )
        project = Project.objects.get(name="Новый проект")
        self.assertRedirects(response, reverse("project_detail", args=[project.pk]))
        self.assertEqual(project.author, self.user)
        self.assertTrue(project.members.filter(pk=self.user.pk).exists())

    def test_owner_can_edit_and_finish_project(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("project_edit", args=[self.project.pk]),
            {
                "name": "Изменённый проект",
                "description": "Новое описание проекта",
                "github_url": "https://github.com/",
                "status": Project.OPEN,
            },
        )
        self.project.refresh_from_db()
        self.assertRedirects(response, reverse("project_detail", args=[self.project.pk]))
        self.assertEqual(self.project.name, "Изменённый проект")

        response = self.client.post(reverse("project_finish", args=[self.project.pk]))
        self.project.refresh_from_db()
        self.assertRedirects(response, reverse("project_detail", args=[self.project.pk]))
        self.assertEqual(self.project.status, Project.CLOSED)

    def test_authenticated_user_can_join_project(self):
        User = get_user_model()
        member = User.objects.create_user(
            username="member@yandex.com",
            email="member@yandex.com",
            password="testpass123",
        )
        self.client.force_login(member)
        response = self.client.post(reverse("project_join", args=[self.project.pk]))
        self.assertRedirects(response, reverse("project_detail", args=[self.project.pk]))
        self.assertTrue(self.project.members.filter(pk=member.pk).exists())
