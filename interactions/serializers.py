from rest_framework import serializers

from articles.models import Article

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "article",
            "username",
            "content",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "username",
            "created_at",
            "updated_at",
        ]

    def validate_article(self, article):
        if article.status != Article.Status.PUBLISHED:
            raise serializers.ValidationError(
                "Комментировать можно только опубликованные статьи."
            )

        return article

    def validate(self, attrs):
        if self.instance:
            new_article = attrs.get("article")

            if (
                new_article
                and new_article != self.instance.article
            ):
                raise serializers.ValidationError({
                    "article": "Нельзя перенести комментарий к другой статье."
                })

        return attrs