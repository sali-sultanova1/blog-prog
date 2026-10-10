from django.db import models
from django.conf import settings
from core.validators import validate_uploaded_image

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Имя")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="slug")

    def __str__(self):
        return self.name
    

class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        SUBMITTED = "submitted", "На модерации"
        PUBLISHED = "published", "Опубликовано"
        REJECTED = "rejected", "Отклонено"

    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Автор", related_name='authored_articles', on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, verbose_name="Категории", related_name='articles', blank=True)
    tags = models.ManyToManyField(Tag, verbose_name="Теги", related_name='articles', blank=True)

    title = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="slug")
    summary = models.TextField(verbose_name="Краткое содержание")
    content = models.TextField(verbose_name="Текст статьи")
    cover_image = models.ImageField(verbose_name="Обложка", upload_to="articles/covers/", blank=True, validators=[validate_uploaded_image])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name="Статус")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата сдачи")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата публикации")

    def __str__(self):
        return self.title


class ModerationRecord(models.Model):
    class Decision(models.TextChoices):
        PUBLISHED = "published", "Опубликовано"
        REJECTED = "rejected", "Отклонено"
        UNPUBLISHED = "unpublished", "Снято с публикации"

    article = models.ForeignKey(Article, verbose_name="Статья", related_name='moderation_records', on_delete=models.CASCADE)
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Инициатор решения", related_name="moderation_records", on_delete=models.SET_NULL, null=True)
    decision = models.CharField(max_length=20, choices=Decision.choices, verbose_name="Решение")
    comment = models.TextField(verbose_name="Комментарий", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.article.title} — {self.get_decision_display()}"
    