from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_authors_group(sender, **kwargs):
    if sender.name != "articles":
        return

    group, _ = Group.objects.get_or_create(name="Authors")

    permissions = Permission.objects.filter(
        content_type__app_label="articles",
        content_type__model="article",
        codename__in=[
            "add_article",
            "change_article",
            "view_article",
            "delete_article",
        ],
    )

    group.permissions.set(permissions)