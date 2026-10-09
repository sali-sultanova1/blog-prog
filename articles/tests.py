from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import AuthorProfile
from interactions.models import Like, Bookmark, Comment
from .models import Article, ModerationRecord

User = get_user_model()

class ArticleListTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", email="author@example.com", password="testpass123")
        authors_group = Group.objects.get(name="Authors")
        self.author.groups.add(authors_group)

        self.user = User.objects.create_user(username="user", email="user@example.com", password="testpass123")
        self.staff = User.objects.create_user(username="staff", email="staff@example.com", password="testpass123", is_staff=True)

        self.published_article = Article.objects.create(author=self.author, title="Published article", slug="published-article", summary="Published summary", content="Published content", status=Article.Status.PUBLISHED, published_at=timezone.now())
        self.draft_article = Article.objects.create(author=self.author, title="Draft article", slug="draft-article", summary="Draft summary", content="Draft content", status=Article.Status.DRAFT)

    def test_article_list_shows_only_published_articles(self):
        response = self.client.get(reverse("article_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Published article")
        self.assertNotContains(response, "Draft article")

    def test_draft_article_is_not_public(self):
        response = self.client.get(reverse("article_detail", args=[self.draft_article.slug]))

        self.assertEqual(response.status_code, 404)

    def test_regular_user_cannot_create_article(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("create_article"))

        self.assertEqual(response.status_code, 403)

    def test_user_can_become_author(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("become_author"))

        self.assertRedirects(response, reverse("profile"))
        group_exists = self.user.groups.filter(name="Authors").exists()
        self.assertTrue(group_exists)
        profile_exists = AuthorProfile.objects.filter(user=self.user).exists()
        self.assertTrue(profile_exists)

    def test_author_can_submit_draft(self):
        self.client.force_login(self.author)
        response = self.client.post(reverse("submit_article", args=[self.draft_article.pk]))

        self.assertRedirects(response, reverse("my_articles"))
        self.draft_article.refresh_from_db()
        self.assertEqual(self.draft_article.status, Article.Status.SUBMITTED)
        self.assertIsNotNone(self.draft_article.submitted_at)

    def test_staff_can_publish_submitted_article(self):
        self.draft_article.status = Article.Status.SUBMITTED
        self.draft_article.submitted_at = timezone.now()
        self.draft_article.save()

        self.client.force_login(self.staff)

        data = {
            "decision": ModerationRecord.Decision.PUBLISHED,
            "comment": "Approved",
        }

        response = self.client.post(reverse("moderate_article", args=[self.draft_article.pk]), data)

        self.assertRedirects(response, reverse("moderation_queue"))
        self.draft_article.refresh_from_db()
        self.assertEqual(self.draft_article.status, Article.Status.PUBLISHED)
        self.assertIsNotNone(self.draft_article.published_at)
        moderationrecord_exists = ModerationRecord.objects.filter(article=self.draft_article, moderator=self.staff, decision=ModerationRecord.Decision.PUBLISHED).exists()
        self.assertTrue(moderationrecord_exists)

    def test_guest_cannot_view_author_profile(self):
        url = reverse("author_profile", args=[self.author.username])
        response = self.client.get(url)

        self.assertRedirects(response, f"{reverse('login')}?next={url}")


class ArticleAPITests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="api_author", email="api_author@example.com", password="testpass123")
        authors_group = Group.objects.get(name="Authors")
        self.author.groups.add(authors_group)

        self.user = User.objects.create_user(username="api_user", email="api_user@example.com", password="testpass123")

        self.published_article = Article.objects.create(author=self.author, title="API published", slug="api-published", summary="Summary", content="Content", status=Article.Status.PUBLISHED, published_at=timezone.now())
        self.draft_article = Article.objects.create(author=self.author, title="API draft", slug="api-draft", summary="Summary", content="Content", status=Article.Status.DRAFT)

    def test_api_list_contains_only_published_articles(self):
        response = self.client.get(reverse("api-article-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        titles = []
        for article in response.data["results"]:
            titles.append(article["title"])

        self.assertIn("API published", titles)
        self.assertNotIn("API draft", titles)

    def test_author_can_create_draft_via_api(self):
        self.client.force_authenticate(user=self.author)

        data = {
            "title": "Created through API",
            "slug": "created-through-api",
            "summary": "Summary",
            "content": "Content",
            "status": Article.Status.PUBLISHED,
        }

        response = self.client.post(reverse("api-article-list"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        article = Article.objects.get(slug="created-through-api")
        self.assertEqual(article.author, self.author)
        self.assertEqual(article.status, Article.Status.DRAFT)

    def test_regular_user_cannot_create_article_via_api(self):
        self.client.force_authenticate(user=self.user)

        data = {
            "title": "Forbidden article",
            "slug": "forbidden-article",
            "summary": "Summary",
            "content": "Content",
        }

        response = self.client.post(reverse("api-article-list"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Article.objects.filter(slug="forbidden-article").exists())

    def test_published_article_cannot_be_edited_via_api(self):
        self.client.force_authenticate(user=self.author)
        old_title = self.published_article.title

        data = {
            "title": "Changed title",
        }

        response = self.client.patch(reverse("api-article-detail", args=[self.published_article.pk]), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.published_article.refresh_from_db()
        self.assertEqual(self.published_article.title, old_title)

    def test_user_can_toggle_like_via_api(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("api-article-like", args=[self.published_article.pk])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["liked"])
        like_exists = Like.objects.filter(user=self.user, article=self.published_article).exists()
        self.assertTrue(like_exists)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["liked"])
        like_exists = Like.objects.filter(user=self.user, article=self.published_article).exists()
        self.assertFalse(like_exists)

    def test_author_can_edit_own_draft_via_api(self):
        self.client.force_authenticate(user=self.author)

        data = {
            "title": "Edited draft",
        }

        response = self.client.patch(reverse("api-article-detail", args=[self.draft_article.pk]), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.draft_article.refresh_from_db()
        self.assertEqual(self.draft_article.title, data["title"])

    def test_user_can_comment_on_published_article_via_api(self):
        self.client.force_authenticate(user=self.user)

        data = {
            "article": self.published_article.pk,
            "content": "Great article!",
        }

        response = self.client.post(reverse("api-comment-list"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.get(article=self.published_article, content=data["content"])
        self.assertEqual(comment.user, self.user)

    def test_guest_cannot_comment_via_api(self):
        data = {
            "article": self.published_article.pk,
            "content": "Guest comment",
        }

        response = self.client.post(reverse("api-comment-list"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        comment_exists = Comment.objects.filter(article=self.published_article, content=data["content"]).exists()
        self.assertFalse(comment_exists)

    def test_user_cannot_comment_on_draft_via_api(self):
        self.client.force_authenticate(user=self.user)

        data = {
            "article": self.draft_article.pk,
            "content": "Draft comment",
        }

        response = self.client.post(reverse("api-comment-list"), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        comment_exists = Comment.objects.filter(article=self.draft_article, content=data["content"]).exists()
        self.assertFalse(comment_exists)

    def test_user_cannot_edit_another_users_comment(self):
        comment = Comment.objects.create(article=self.published_article, user=self.user, content="Original comment")
        old_content = comment.content
        self.client.force_authenticate(user=self.author)

        data = {
            "content": "Changed comment",
        }

        response = self.client.patch(reverse("api-comment-detail", args=[comment.pk]), data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        comment.refresh_from_db()
        self.assertEqual(comment.content, old_content)

    def test_user_can_toggle_bookmark_via_api(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("api-article-bookmark", args=[self.published_article.pk])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["bookmarked"])
        bookmark_exists = Bookmark.objects.filter(user=self.user, article=self.published_article).exists()
        self.assertTrue(bookmark_exists)

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["bookmarked"])
        bookmark_exists = Bookmark.objects.filter(user=self.user, article=self.published_article).exists()
        self.assertFalse(bookmark_exists)          
