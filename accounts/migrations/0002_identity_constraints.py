from django.db import migrations, models
from django.db.models import Count, Q
from django.db.models.functions import Lower


def check_existing_accounts(apps, schema_editor):
    User = apps.get_model("accounts", "CustomUser")
    users = User.objects.using(schema_editor.connection.alias)
    invalid_usernames = list(users.filter(username__contains="@").values_list("pk", flat=True)[:20])

    if invalid_usernames:
        raise RuntimeError(f"Перед миграцией измените username с символом @. ID пользователей: {invalid_usernames}")

    duplicate_emails = users.annotate(normalized_email=Lower("email")).values("normalized_email").annotate(total=Count("pk")).filter(total__gt=1)

    if duplicate_emails.exists():
        raise RuntimeError("Найдены email, совпадающие без учёта регистра. Разберите эти аккаунты перед добавлением ограничения.")


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]

    operations = [
        migrations.RunPython(check_existing_accounts, reverse_code=migrations.RunPython.noop),
        migrations.AddConstraint(model_name="customuser", constraint=models.CheckConstraint(condition=~Q(username__contains="@"), name="accounts_username_without_at")),
        migrations.AddConstraint(model_name="customuser", constraint=models.UniqueConstraint(Lower("email"), name="accounts_email_ci_unique")),
    ]