import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('github_url', models.URLField(blank=True, verbose_name='Ссылка на GitHub')),
                ('status', models.CharField(choices=[('open', 'Открыт'), ('closed', 'Закрыт')], default='open', max_length=10, verbose_name='Статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('members', models.ManyToManyField(blank=True, related_name='joined_projects', to=settings.AUTH_USER_MODEL, verbose_name='Участники')),
            ],
            options={
                'verbose_name': 'Проект',
                'verbose_name_plural': 'Проекты',
                'ordering': ['-created_at'],
            },
        ),
    ]
