from django.urls import path
from .views import create_article_view, my_articles_view, edit_my_article_view, submit_article_view

urlpatterns = [
    path("create/", create_article_view, name="create_article"),
    path("mine/", my_articles_view, name="my_articles"),
    path("<int:pk>/edit/", edit_my_article_view, name="edit_article"),
    path("<int:pk>/submit/", submit_article_view, name="submit_article"),

]