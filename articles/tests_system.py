from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Article, ModerationRecord

User = get_user_model()

class ArticleWorkflowSystemTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="workflow_user", email="workflow@example.com", password="testpass123")
        self.staff = User.objects.create_user(username="workflow_staff", email="staff@example.com", password="testpass123", is_staff=True)

    def test_article_full_workflow(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("become_author"))
        self.assertRedirects(response, reverse("profile"))

        data = {
            "title": "System test article",
            "slug": "system-test-article",
            "summary": "System test summary",
            "content": "System test content",
        }

        response = self.client.post(reverse("create_article"), data)
        self.assertRedirects(response, reverse("my_articles"))

        article = Article.objects.get(slug="system-test-article")
        self.assertEqual(article.author, self.user)
        self.assertEqual(article.status, Article.Status.DRAFT)

        response = self.client.post(reverse("submit_article", args=[article.pk]))
        self.assertRedirects(response, reverse("my_articles"))

        article.refresh_from_db()
        self.assertEqual(article.status, Article.Status.SUBMITTED)
        self.assertIsNotNone(article.submitted_at)

        self.client.force_login(self.staff)

        data = {
            "decision": ModerationRecord.Decision.PUBLISHED,
            "comment": "Approved",
        }

        response = self.client.post(reverse("moderate_article", args=[article.pk]), data)
        self.assertRedirects(response, reverse("moderation_queue"))

        article.refresh_from_db()
        self.assertEqual(article.status, Article.Status.PUBLISHED)
        self.assertIsNotNone(article.published_at)

        self.client.logout()

        response = self.client.get(reverse("article_detail", args=[article.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "System test article")