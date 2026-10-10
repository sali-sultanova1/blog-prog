from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import email_verification_token

User = get_user_model()

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


class EmailVerificationTests(TestCase):
    def test_registration_creates_inactive_user_and_sends_email(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new_user",
                "email": "new@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        user = User.objects.get(username="new_user")

        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 1)
        self.assertContains(response, "new@example.com")

    def test_inactive_user_cannot_login(self):
        User.objects.create_user(
            username="inactive_user",
            email="inactive@example.com",
            password="testpass123",
            is_active=False,
        )

        response = self.client.post(
            reverse("login"),
            {
                "username": "inactive_user",
                "password": "testpass123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_valid_verification_link_activates_user(self):
        user = User.objects.create_user(
            username="verify_user",
            email="verify@example.com",
            password="testpass123",
            is_active=False,
        )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)

        response = self.client.get(
            reverse(
                "verify_email",
                kwargs={
                    "uidb64": uid,
                    "token": token,
                },
            )
        )

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertRedirects(response, reverse("login"))