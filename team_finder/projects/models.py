from django.conf import settings
from django.db import models


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
