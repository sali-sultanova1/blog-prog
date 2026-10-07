from django.urls import path
from .views import create_article_view, my_articles_view, edit_my_article_view, submit_article_view, moderate_article_view, moderation_queue_view, become_author_view, delete_article_view, article_list_view, article_detail_view

urlpatterns = [
    path("create/", create_article_view, name="create_article"),
    path("mine/", my_articles_view, name="my_articles"),
    path("<int:pk>/edit/", edit_my_article_view, name="edit_article"),
    path("<int:pk>/submit/", submit_article_view, name="submit_article"),
    path("<int:pk>/moderate/", moderate_article_view, name="moderate_article"),
    path("moderation/", moderation_queue_view, name="moderation_queue"),
    path("become-author/", become_author_view, name="become_author"),
    path("<int:pk>/delete/", delete_article_view, name="delete_article"),
    path("", article_list_view, name="article_list"),

    
    path("<slug:slug>/", article_detail_view, name="article_detail"),

]