from django.db import models
from articles.models import Article
from django.conf import settings

class Comment(models.Model):
    article = models.ForeignKey(Article, verbose_name="Статья", related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Пользователь", related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"{self.user.username}: {self.article.title}"
    

class Like(models.Model):
    article = models.ForeignKey(Article, verbose_name="Статья", related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Пользователь", related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["article", "user"], name="unique_article_like",)]

    def __str__(self):
        return f"{self.user.username}: {self.article.title}"

class Bookmark(models.Model):
    article = models.ForeignKey(Article, verbose_name="Статья", related_name='bookmarks', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Пользователь", related_name='bookmarks', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["article", "user"], name="unique_article_bookmark",)]

    def __str__(self):
        return f"{self.user.username}: {self.article.title}"



