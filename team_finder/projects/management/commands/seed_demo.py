from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from team_finder.projects.models import Project
from team_finder.users.models import Profile, Skill


class Command(BaseCommand):
    help = "Создаёт демо-данные для проверки проекта"

    def handle(self, *args, **options):
        User = get_user_model()
        users = [
            ("anna@yandex.com", "Анна", "Бель", ["Django", "Python", "REST"]),
            ("igor@yandex.com", "Игорь", "Верник", ["React", "TypeScript", "UI"]),
            ("maria@yandex.com", "Мария", "Дом", ["PostgreSQL", "Docker", "Django"]),
        ]
        created_users = []
        for email, first_name, last_name, skills in users:
            user, created = User.objects.get_or_create(
                username=email,
                defaults={"email": email, "first_name": first_name, "last_name": last_name},
            )
            if created:
                user.set_password("testpass123")
                user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.bio = f"{first_name} ищет команду для интересных pet-проектов."
            profile.github = "https://github.com/"
            profile.save()
            for skill_name in skills:
                skill, _ = Skill.objects.get_or_create(name=skill_name)
                profile.skills.add(skill)
            created_users.append(user)
        projects = [
            (
                "Трекер привычек для команд",
                (
                    "Сервис помогает небольшой команде договориться о привычках "
                    "и видеть общий прогресс."
                ),
                created_users[0],
            ),
            (
                "Каталог локальных мероприятий",
                "Приложение собирает митапы, лекции и хакатоны в одном удобном списке.",
                created_users[1],
            ),
            (
                "Планировщик учебных проектов",
                "Инструмент для распределения задач между участниками учебной команды.",
                created_users[2],
            ),
        ]
        for name, description, author in projects:
            project, _ = Project.objects.get_or_create(
                name=name,
                author=author,
                defaults={
                    "description": description,
                    "github_url": "https://github.com/",
                },
            )
            project.members.add(author)
        self.stdout.write(
            self.style.SUCCESS("Демо-данные готовы. Пароль пользователей: testpass123")
        )
