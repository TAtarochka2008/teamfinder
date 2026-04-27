from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE UNIQUE INDEX IF NOT EXISTS user_email_unique ON auth_user(email) WHERE email <> '';",
            reverse_sql="DROP INDEX IF EXISTS user_email_unique;",
        ),
    ]
