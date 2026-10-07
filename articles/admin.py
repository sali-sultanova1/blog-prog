from django.contrib import admin
from .models import Category, Tag, Article, ModerationRecord

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    search_fields = ('name', 'slug')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'slug', 'created_at', 'published_at')
    search_fields = ('title', 'summary', 'author__username', 'author__email')
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ('status', 'created_at', 'published_at')

@admin.register(ModerationRecord)
class ModerationRecordAdmin(admin.ModelAdmin):
    list_display = ('article', 'moderator', 'decision', 'created_at')
    search_fields = ('article__title', 'moderator__username')
    list_filter = ('decision',)
