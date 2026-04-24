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

    def test_password_change_requires_login(self):
        response = self.client.get(reverse("password_change"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

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

    def test_owner_can_edit_profile(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("profile_edit", args=[self.user.profile.pk]),
            {
                "first_name": "Олег",
                "last_name": "Новый",
                "email": "owner-new@yandex.com",
                "avatar_url": "",
                "bio": "Обновлённое описание",
                "phone": "+79990000000",
                "github": "https://github.com/",
            },
        )
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertRedirects(response, reverse("profile_detail", args=[self.user.profile.pk]))
        self.assertEqual(self.user.email, "owner-new@yandex.com")
        self.assertEqual(self.user.profile.bio, "Обновлённое описание")

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

    def test_user_list_filters_by_skill(self):
        response = self.client.get(reverse("user_list"), {"skill": self.skill.name})
        self.assertContains(response, "Олег")
        self.assertContains(response, self.skill.name)

    def test_owner_can_add_and_delete_skill_without_page_reload(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("profile_skill_add", args=[self.user.profile.pk]),
            {"name": "Docker"},
        )
        self.assertEqual(response.status_code, 200)
        skill_id = response.json()["id"]
        self.assertTrue(self.user.profile.skills.filter(name="Docker").exists())

        response = self.client.post(
            reverse("profile_skill_delete", args=[self.user.profile.pk, skill_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user.profile.skills.filter(name="Docker").exists())

    def test_skill_search_suggests_existing_and_new_skills(self):
        response = self.client.get(reverse("skill_search"), {"q": "Djan"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["name"], "Django")

        response = self.client.get(reverse("skill_search"), {"q": "FastAPI"})
        self.assertTrue(response.json()["can_create"])

    def test_user_email_is_unique(self):
        User = get_user_model()
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                User.objects.create_user(
                    username="second@yandex.com",
                    email="owner@yandex.com",
                    password="testpass123",
                )
