from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Article, ModerationRecord


@transaction.atomic
def moderate_article(*, article_id, moderator, decision, comment=""):
    if not moderator.is_active or not moderator.is_staff:
        raise PermissionDenied("У вас нет доступа к модерации.")

    article = get_object_or_404(Article.objects.select_for_update(), pk=article_id)

    if article.status != Article.Status.SUBMITTED:
        raise ValidationError("Статья уже обработана другим модератором или больше не ожидает проверки.")

    if decision not in ModerationRecord.Decision.values:
        raise ValidationError("Неизвестное решение модератора.")

    if decision == ModerationRecord.Decision.PUBLISHED:
        article.status = Article.Status.PUBLISHED
        article.published_at = timezone.now()
    else:
        article.status = Article.Status.REJECTED
        article.published_at = None

    article.save(update_fields=["status", "published_at", "updated_at"])
    ModerationRecord.objects.create(article=article, moderator=moderator, decision=decision, comment=comment)

    return article