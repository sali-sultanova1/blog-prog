import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import close_old_connections
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from accounts.models import AuthorProfile
from interactions.models import Bookmark, Like
from .forms import ModerationForm
from .models import Article, ModerationRecord, Tag
from .services import moderate_article, unpublish_article


User = get_user_model()


class RemainingFeaturesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username="feature_author", email="feature_author@example.com", password="TestStrong123!")
        cls.other = User.objects.create_user(username="feature_other", email="feature_other@example.com", password="TestStrong123!")
        cls.reader = User.objects.create_user(username="feature_reader", email="feature_reader@example.com", password="TestStrong123!")
        cls.staff = User.objects.create_user(username="feature_staff", email="feature_staff@example.com", password="TestStrong123!", is_staff=True)
        group = Group.objects.get(name="Authors")
        cls.author.groups.add(group)
        cls.other.groups.add(group)

    def setUp(self):
        self.api = APIClient()
        self.published = Article.objects.create(author=self.author, title="Published", slug="published", summary="Summary", content="AB", status=Article.Status.PUBLISHED, published_at=timezone.now())
        self.draft = Article.objects.create(author=self.author, title="Draft", slug="draft", summary="Summary", content="SECRET", status=Article.Status.DRAFT)
        self.foreign = Article.objects.create(author=self.other, title="Other", slug="other", summary="Summary", content="Other", status=Article.Status.PUBLISHED, published_at=timezone.now())

    def test_author_filter(self):
        response = self.api.get("/api/articles/", {"author": self.author.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id"] for row in response.data["results"]], [self.published.pk])

    def test_public_status_filter_cannot_expose_drafts(self):
        response = self.api.get("/api/articles/", {"status": "draft"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_mine_requires_login_and_never_exposes_other_author(self):
        self.assertEqual(self.api.get("/api/articles/mine/").status_code, 401)
        self.api.force_authenticate(self.author)
        response = self.api.get("/api/articles/mine/", {"status": "draft"})
        self.assertEqual([row["id"] for row in response.data["results"]], [self.draft.pk])
        response = self.api.get("/api/articles/mine/", {"author": self.other.pk})
        self.assertEqual(response.data["count"], 0)

    def test_bad_status_is_validation_error(self):
        self.assertEqual(self.api.get("/api/articles/", {"status": "unknown"}).status_code, 400)

    def test_updated_at_sort(self):
        Article.objects.filter(pk=self.published.pk).update(updated_at=timezone.now() - timedelta(days=1))
        response = self.api.get("/api/articles/", {"ordering": "updated_at"})
        self.assertEqual([row["id"] for row in response.data["results"]], [self.published.pk, self.foreign.pk])

    def test_owner_unpublishes_and_data_is_hidden(self):
        Bookmark.objects.create(user=self.reader, article=self.published)
        self.api.force_authenticate(self.author)
        response = self.api.post(reverse("api-article-unpublish", args=[self.published.pk]))
        self.assertEqual(response.status_code, 200)
        self.published.refresh_from_db()
        self.assertEqual(self.published.status, Article.Status.DRAFT)
        self.assertIsNone(self.published.published_at)
        self.assertTrue(ModerationRecord.objects.filter(article=self.published, moderator=self.author, decision="unpublished").exists())
        self.api.force_authenticate(None)
        self.assertEqual(self.api.get(reverse("api-article-detail", args=[self.published.pk])).status_code, 404)
        self.client.force_login(self.reader)
        response = self.client.get(reverse("my_bookmarks"))
        self.assertEqual(len(response.context["bookmarks"]), 0)

    def test_foreign_author_cannot_unpublish(self):
        self.api.force_authenticate(self.other)
        self.assertEqual(self.api.post(reverse("api-article-unpublish", args=[self.published.pk])).status_code, 404)
        self.published.refresh_from_db()
        self.assertEqual(self.published.status, Article.Status.PUBLISHED)

    def test_reader_cannot_unpublish(self):
        self.api.force_authenticate(self.reader)
        self.assertEqual(self.api.post(reverse("api-article-unpublish", args=[self.published.pk])).status_code, 403)

    def test_staff_can_unpublish_and_repeat_returns_conflict(self):
        self.api.force_authenticate(self.staff)
        url = reverse("api-article-unpublish", args=[self.published.pk])
        self.assertEqual(self.api.post(url).status_code, 200)
        self.assertEqual(self.api.post(url).status_code, 409)
        self.assertEqual(ModerationRecord.objects.filter(article=self.published).count(), 1)

    def test_web_unpublish_is_post_only_and_can_be_resubmitted(self):
        self.client.force_login(self.author)
        url = reverse("unpublish_article", args=[self.published.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertRedirects(self.client.post(url), reverse("my_articles"))
        self.assertEqual(self.client.post(reverse("submit_article", args=[self.published.pk])).status_code, 302)
        moderate_article(article_id=self.published.pk, moderator=self.staff, decision="published")
        self.published.refresh_from_db()
        self.assertEqual(self.published.status, Article.Status.PUBLISHED)

    def test_unpublish_not_valid_moderation_form_decision(self):
        self.assertFalse(ModerationForm(data={"decision": "unpublished"}).is_valid())

        with self.assertRaises(ValidationError):
            self.draft.status = Article.Status.SUBMITTED
            self.draft.save()
            moderate_article(article_id=self.draft.pk, moderator=self.staff, decision="unpublished")

    def test_statistics_count_average_and_tags_only_published(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("author_statistics"))
        second = Article.objects.create(author=self.author, title="Second", slug="second", summary="S", content="ABCDEF", status=Article.Status.PUBLISHED)
        first_tag = Tag.objects.create(name="One", slug="one")
        second_tag = Tag.objects.create(name="Two", slug="two")
        hidden_tag = Tag.objects.create(name="SECRET_TAG", slug="secret-tag")
        self.published.tags.add(first_tag, second_tag)
        second.tags.add(first_tag)
        self.draft.tags.add(hidden_tag)
        Like.objects.create(article=self.published, user=self.reader)
        Like.objects.create(article=self.published, user=self.other)
        response = self.client.get(reverse("author_statistics"))
        self.assertEqual(response.status_code, 200)
        row = next(user for user in response.context["authors"] if user.pk == self.author.pk)
        self.assertEqual(row.published_count, 2)
        self.assertEqual(row.average_length, 4)
        self.assertCountEqual(row.used_tags, ["One", "Two"])
        self.assertNotContains(response, "SECRET_TAG")
        self.assertContains(response, "One")
        self.client.force_login(self.reader)
        response = self.client.get(reverse("author_profile", args=[self.author.username]))
        self.assertEqual(response.context["stats"]["average_length"], 4)
        self.assertCountEqual([tag.name for tag in response.context["used_tags"]], ["One", "Two"])

    def test_author_without_publications_is_in_statistics(self):
        Article.objects.filter(author=self.other).delete()
        self.client.force_login(self.staff)
        response = self.client.get(reverse("author_statistics"))
        self.assertEqual(response.status_code, 200)
        row = next(user for user in response.context["authors"] if user.pk == self.other.pk)
        self.assertEqual(row.published_count, 0)
        self.assertIsNone(row.average_length)
        self.assertEqual(row.used_tags, [])
        
    def test_author_can_edit_own_profile(self):
        self.client.force_login(self.author)
        response = self.client.post(reverse("edit_profile"), {"first_name": "New", "author-specialization": "Django", "author-portfolio_url": "https://example.com/work"})
        self.assertRedirects(response, reverse("profile"))
        profile = AuthorProfile.objects.get(user=self.author)
        self.assertEqual(profile.specialization, "Django")
        self.assertEqual(profile.portfolio_url, "https://example.com/work")

    def test_invalid_portfolio_does_not_partially_save_user(self):
        self.client.force_login(self.author)
        response = self.client.post(reverse("edit_profile"), {"first_name": "MustNotSave", "author-portfolio_url": "javascript:alert(1)"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("portfolio_url", response.context["author_form"].errors)
        self.author.refresh_from_db()
        self.assertEqual(self.author.first_name, "")
        self.assertFalse(AuthorProfile.objects.filter(user=self.author).exists())

    def test_reader_cannot_create_author_profile_by_extra_fields(self):
        self.client.force_login(self.reader)
        response = self.client.post(reverse("edit_profile"), {"first_name": "Reader", "author-specialization": "Injected", "author-portfolio_url": "https://example.com"})
        self.assertRedirects(response, reverse("profile"))
        self.assertFalse(AuthorProfile.objects.filter(user=self.reader).exists())


class UnpublishConcurrencyTests(TransactionTestCase):
    def test_two_requests_create_one_history_record(self):
        staff = User.objects.create_user(username="concurrent_staff", email="concurrent_staff@example.com", is_staff=True)
        article = Article.objects.create(author=staff, title="T", slug="concurrent", summary="S", content="C", status=Article.Status.PUBLISHED, published_at=timezone.now())
        barrier = threading.Barrier(2)

        def worker(_):
            close_old_connections()

            try:
                barrier.wait(timeout=10)
                unpublish_article(article_id=article.pk, actor=staff)
                return "saved"
            except ValidationError:
                return "conflict"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(worker, [1, 2]))

        self.assertCountEqual(results, ["saved", "conflict"])
        self.assertEqual(ModerationRecord.objects.filter(article=article).count(), 1)