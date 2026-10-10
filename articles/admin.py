from django.contrib import admin
from .models import Category, Tag, Article, ModerationRecord
from django.urls import reverse
from django.utils.html import format_html

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
    list_display = ("title", "author", "status", "created_at", "published_at", "moderation_link")
    search_fields = ("title", "summary", "author__username", "author__email")
    list_filter = ("status", "created_at", "published_at")
    list_select_related = ("author",)

    def get_readonly_fields(self, request, obj=None):
        fields = ("status", "created_at", "updated_at", "submitted_at", "published_at", "moderation_link")

        if obj is not None:
            fields += ("author",)

        if obj and obj.status in (Article.Status.SUBMITTED, Article.Status.PUBLISHED):
            fields += ("title", "slug", "summary", "content", "cover_image", "categories", "tags")

        return fields

    def get_prepopulated_fields(self, request, obj=None):
        if obj and obj.status in (Article.Status.SUBMITTED, Article.Status.PUBLISHED):
            return {}

        return {"slug": ("title",)}

    @admin.display(description="Модерация")
    def moderation_link(self, obj):
        if obj is None or obj.status != Article.Status.SUBMITTED:
            return "—"

        return format_html('<a href="{}">Проверить статью</a>', reverse("moderate_article", args=[obj.pk]))

@admin.register(ModerationRecord)
class ModerationRecordAdmin(admin.ModelAdmin):
    list_display = ("article", "moderator", "decision", "created_at")
    list_filter = ("decision",)
    search_fields = ("article__title", "moderator__username")
    list_select_related = ("article", "moderator")
    readonly_fields = ("article", "moderator", "decision", "comment", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False