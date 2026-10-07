from django.urls import path
from .views import register_view, profile_view
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('register/', register_view, name="register"),
    path('login/', LoginView.as_view(template_name="login.html"), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path("profile/", profile_view, name="profile")
]