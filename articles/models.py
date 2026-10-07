from django.db import models
from django.conf import settings

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

    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Автор", related_name='authored_articles', models.PROTECT)
    category = models.ForeignKey(Category, verbose_name="Категории", related_name='articles', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, verbose_name="Тэг", related_name='articles')

    title = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="slug")
    summary = models.TextField(verbose_name="Краткое содержание")
    content = models.TextField(verbose_name="Текст статьи")
    cover_image = models.ImageField(verbose_name="Обложка", upload_to='covers/', blank = True)
    status = models.CharField(max_length=20, choices=Status.choices, default='draft', verbose_name="Статус")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата сдачи")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата публикации")

    def __str__(self):
        return self.title