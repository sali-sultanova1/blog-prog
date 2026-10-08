from django.urls import path
from .views import register_view, profile_view, edit_profile_view, author_profile_view
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('register/', register_view, name="register"),
    path('login/', LoginView.as_view(template_name="login.html"), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", edit_profile_view, name="edit_profile"),
    path("authors/<str:username>/", author_profile_view, name="author_profile"),

]