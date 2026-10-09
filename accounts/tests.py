from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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
