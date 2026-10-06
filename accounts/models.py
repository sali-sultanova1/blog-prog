from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(verbose_name="Электронная почта", unique=True)
    bio = models.TextField(verbose_name="Биография", blank = True)
    avatar = models.ImageField(verbose_name="Аватар", upload_to='avatars/', blank = True)

class AuthorProfile(models.Model):
    user = models.OneToOneField(CustomUser, related_name="author_profile", verbose_name="Пользователь", on_delete=models.CASCADE)
    specialization = models.CharField(verbose_name="Специализация", max_length=200, blank = True)
    portfolio_url = models.URLField(verbose_name="Ссылка на портфолио", blank = True)