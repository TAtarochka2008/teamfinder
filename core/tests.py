from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import Project, Skill


class SmokeTests(TestCase):
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
        self.skill = Skill.objects.create(name="Django")
        self.user.profile.skills.add(self.skill)

    def test_public_pages_open(self):
        urls = [
            reverse("home"),
            reverse("user_list"),
            reverse("profile_detail", args=[self.user.profile.pk]),
            reverse("project_detail", args=[self.project.pk]),
            reverse("login"),
            reverse("signup"),
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

    def test_user_list_filters_by_skill(self):
        response = self.client.get(reverse("user_list"), {"skill": self.skill.name})
        self.assertContains(response, "Олег")
        self.assertContains(response, self.skill.name)

    def test_user_email_is_unique(self):
        User = get_user_model()
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                User.objects.create_user(
                    username="second@yandex.com",
                    email="owner@yandex.com",
                    password="testpass123",
                )
