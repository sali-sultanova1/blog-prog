from django.test import SimpleTestCase
from rest_framework import serializers
from articles.models import Article
from .serializers import CommentSerializer

class CommentSerializerUnitTests(SimpleTestCase):
    def test_published_article_is_valid_for_comment(self):
        article = Article(status=Article.Status.PUBLISHED)
        serializer = CommentSerializer()

        result = serializer.validate_article(article)
        self.assertIs(result, article)

    def test_draft_article_is_invalid_for_comment(self):
        article = Article(status=Article.Status.DRAFT)
        serializer = CommentSerializer()

        with self.assertRaises(serializers.ValidationError):
            serializer.validate_article(article)