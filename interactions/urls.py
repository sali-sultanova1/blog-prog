from django.urls import path
from .views import add_comment_view, edit_comment_view, delete_comment_view, toggle_like_view, toggle_bookmark_view, my_bookmarks_view

urlpatterns = [
    path("articles/<slug:slug>/comment/", add_comment_view, name="add_comment"),
    path("comments/<int:pk>/edit/", edit_comment_view, name="edit_comment"),
    path("comments/<int:pk>/delete/", delete_comment_view, name="delete_comment"),
    path("articles/<slug:slug>/like/", toggle_like_view, name="toggle_like"),
    path("articles/<slug:slug>/bookmark/", toggle_bookmark_view, name="toggle_bookmark"),
    path("bookmark/", my_bookmarks_view, name="my_bookmarks"),
    
]