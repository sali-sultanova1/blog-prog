from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.functions import Lower
from core.validators import validate_uploaded_image

class CustomUser(AbstractUser):
    email = models.EmailField(verbose_name="Электронная почта", unique=True)
    bio = models.TextField(verbose_name="Биография", blank = True)
    avatar = models.ImageField(verbose_name="Аватар", upload_to="avatars/", blank=True, validators=[validate_uploaded_image])

    def clean(self):
        super().clean()

        if "@" in self.username:
            raise ValidationError({"username": "Имя пользователя не должно содержать @."})

        self.email = self.email.strip().lower()

    class Meta(AbstractUser.Meta):
        abstract = False
        constraints = [
            models.CheckConstraint(condition=~Q(username__contains="@"), name="accounts_username_without_at"),
            models.UniqueConstraint(Lower("email"), name="accounts_email_ci_unique"),
        ]

class AuthorProfile(models.Model):
    user = models.OneToOneField(CustomUser, related_name="author_profile", verbose_name="Пользователь", on_delete=models.CASCADE)
    specialization = models.CharField(verbose_name="Специализация", max_length=200, blank = True)
    portfolio_url = models.URLField(verbose_name="Ссылка на портфолио", blank = True)

    def __str__(self):
        return self.user.username
    