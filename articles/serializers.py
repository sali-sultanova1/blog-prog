from rest_framework import serializers

from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.CharField(
        source="author.username",
        read_only=True
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "author",
            "categories",
            "tags",
            "title",
            "slug",
            "summary",
            "content",
            "cover_image",
            "status",
            "created_at",
            "updated_at",
            "submitted_at",
            "published_at",
        ]

        read_only_fields = [
            "id",
            "author",
            "status",
            "created_at",
            "updated_at",
            "submitted_at",
            "published_at",
        ]