from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate, post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Category, Tag
from core.cache_utils import delete_cache_safely

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


@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, **kwargs):
    delete_cache_safely("article_categories")

@receiver([post_save, post_delete], sender=Tag)
def clear_tag_cache(sender, **kwargs):
    delete_cache_safely("article_tags")