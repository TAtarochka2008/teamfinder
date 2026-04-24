from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Skill(models.Model):
    name = models.CharField("Название", max_length=80, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar_url = models.URLField("Аватар", blank=True)
    bio = models.TextField("О себе", blank=True)
    phone = models.CharField("Телефон", max_length=40, blank=True)
    github = models.URLField("GitHub", blank=True)
    skills = models.ManyToManyField(Skill, blank=True, related_name="profiles")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.user.get_full_name() or self.user.email

    @property
    def avatar(self):
        return self.avatar_url or "https://api.dicebear.com/8.x/initials/svg?seed=" + (
            self.user.get_full_name() or self.user.email
        )


class Project(models.Model):
    OPEN = "open"
    CLOSED = "closed"
    STATUS_CHOICES = [
        (OPEN, "Открыт"),
        (CLOSED, "Закрыт"),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name="Автор",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="joined_projects",
        verbose_name="Участники",
    )
    name = models.CharField("Название", max_length=120)
    description = models.TextField("Описание")
    github_url = models.URLField("Ссылка на GitHub", blank=True)
    status = models.CharField("Статус", max_length=10, choices=STATUS_CHOICES, default=OPEN)
    created_at = models.DateTimeField("Дата публикации", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name

    @property
    def short_description(self):
        if len(self.description) <= 170:
            return self.description
        return self.description[:167].rstrip() + "..."


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
