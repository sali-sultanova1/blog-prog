from rest_framework import serializers
from .models import Article, Category, Tag


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    category_names = serializers.SlugRelatedField(source="categories", many=True, read_only=True, slug_field="name")
    tag_names = serializers.SlugRelatedField(source="tags", many=True, read_only=True, slug_field="name")
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Article
        fields = ["id", "author", "categories", "category_names", "tags", "tag_names", "title", "slug", "summary", "content", "cover_image", "status", "likes_count", "comments_count", "created_at", "updated_at", "submitted_at", "published_at"]
        read_only_fields = ["id", "author", "status", "created_at", "updated_at", "submitted_at", "published_at"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]