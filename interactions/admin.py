from django.contrib import admin
from .models import Comment, Like, Bookmark

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "created_at", "updated_at")
    search_fields = ("user__username", "article__title", "content")
    list_filter = ("created_at",)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "created_at")
    search_fields = ("user__username", "article__title")

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "created_at")
    search_fields = ("user__username", "article__title")
