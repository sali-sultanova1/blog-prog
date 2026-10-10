from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core import mail
from urllib.parse import urlparse
from django.core.cache import cache

User = get_user_model()

@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "login-tests"}})
class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="login_user",
            email="login@example.com",
            password="testpass123",
        )

    def test_login_with_username(self):
        response = self.client.post(reverse("login"), {"username": "login_user", "password": "testpass123"})
        self.assertRedirects(response, reverse("profile"))

    def test_login_with_email(self):
        response = self.client.post(reverse("login"), {"username": "login@example.com", "password": "testpass123"})
        self.assertRedirects(response, reverse("profile"))

@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "registration-tests"}})
class EmailVerificationTests(TestCase):
    def test_registration_does_not_create_user_before_verification(self):
        response = self.client.post(reverse("register"), {"username": "new_user", "email": "new@example.com", "password1": "StrongPass123!", "password2": "StrongPass123!"})

        self.assertFalse(User.objects.filter(username="new_user").exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertContains(response, "new@example.com")
        self.assertIn("30 минут", mail.outbox[0].body)

    def test_valid_verification_link_creates_user(self):
        self.client.post(reverse("register"), {"username": "verify_user", "email": "verify@example.com", "password1": "StrongPass123!", "password2": "StrongPass123!"})

        verification_url = next(line for line in mail.outbox[0].body.splitlines() if line.startswith("http"))
        response = self.client.get(urlparse(verification_url).path)
        user = User.objects.get(username="verify_user")

        self.assertEqual(user.email, "verify@example.com")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertRedirects(response, reverse("login"))

    def test_expired_verification_link_does_not_create_user(self):
        self.client.post(reverse("register"), {"username": "expired_user", "email": "expired@example.com", "password1": "StrongPass123!", "password2": "StrongPass123!"})

        verification_url = next(line for line in mail.outbox[0].body.splitlines() if line.startswith("http"))
        token = urlparse(verification_url).path.rstrip("/").split("/")[-1]
        cache.delete(f"pending_registration:{token}")
        response = self.client.get(urlparse(verification_url).path)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username="expired_user").exists())

class AuthorStatisticsAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create_user(
            username="statistics_reader",
            email="statistics-reader@example.com",
            password="TestPassword123!",
        )

        cls.staff = User.objects.create_user(
            username="statistics_staff",
            email="statistics-staff@example.com",
            password="TestPassword123!",
            is_staff=True,
        )

    def test_guest_is_redirected_to_login(self):
        response = self.client.get(reverse("author_statistics"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            urlparse(response.url).path,
            reverse("login"),
        )

    def test_regular_user_cannot_open_statistics(self):
        self.client.force_login(self.reader)

        response = self.client.get(reverse("author_statistics"))

        self.assertEqual(response.status_code, 403)

    def test_staff_can_open_statistics(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("author_statistics"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Статистика редакции")